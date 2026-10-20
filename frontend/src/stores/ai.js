import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useNotesStore } from './notes'

export const useAIStore = defineStore('ai', () => {
  const isDrawerOpen = ref(false)
  const isStagingOpen = ref(false)
  const isSettingsOpen = ref(false)
  const isSearchOpen = ref(false)

  const mode = ref('new_note') // 'new_note' | 'tidy_note' | 'custom'
  const tone = ref('balanced') // 'balanced' | 'concise' | 'professional' | 'bulleted'
  const prompt = ref('')
  const isGenerating = ref(false)
  const generationError = ref('')

  // Staged draft state
  const draftText = ref('')
  const draftTitle = ref('')
  const originalText = ref('')
  const targetFolderId = ref('all')
  const activeProvider = ref('gemini') // 'gemini' | 'ollama'

  const aiStatus = ref({
    default_provider: 'gemini',
    gemini_configured: false,
    gemini_model: 'gemini-2.5-flash',
    ollama_url: 'http://localhost:11434',
    ollama_model: 'llama3.2',
    ollama_available: false
  })

  async function fetchAIStatus() {
    try {
      const res = await fetch('/api/ai/status')
      if (res.ok) {
        aiStatus.value = await res.json()
        activeProvider.value = aiStatus.value.default_provider || 'gemini'
      }
    } catch (e) {
      console.error('Failed to fetch AI status:', e)
    }
  }

  function openDrawer(newMode = 'new_note', contextContent = '') {
    mode.value = newMode
    if (newMode === 'tidy_note') {
      const notesStore = useNotesStore()
      originalText.value = contextContent || (notesStore.activeNote ? notesStore.activeNote.content : '')
      prompt.value = prompt.value || 'Clean up formatting, fix typos, and organize with clear headers.'
    } else {
      originalText.value = ''
    }
    isDrawerOpen.value = true
  }

  function closeDrawer() {
    isDrawerOpen.value = false
  }

  async function generateDraft() {
    if (!prompt.value.trim()) return

    isGenerating.value = true
    generationError.value = ''
    draftText.value = ''

    try {
      const payload = {
        prompt: prompt.value,
        context_content: originalText.value,
        mode: mode.value,
        tone: tone.value,
        provider: activeProvider.value
      }

      const res = await fetch('/api/ai/draft', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      if (!res.ok) {
        throw new Error(`Server returned status ${res.status}`)
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buffer = ''

      while (true) {
        const { value, done } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n\n')
        buffer = lines.pop() // keep incomplete chunk

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const dataStr = line.slice(6).trim()
          if (dataStr === '[DONE]') break
          try {
            const parsed = JSON.parse(dataStr)
            if (parsed.text) {
              draftText.value += parsed.text
            }
          } catch (e) {
            console.error('SSE JSON parse error', e)
          }
        }
      }

      // Extract title from draft if available (first # header)
      extractTitleFromDraft()

      // Automatically open staging review modal once streaming finishes or is substantial
      isStagingOpen.value = true
      isDrawerOpen.value = false
    } catch (e) {
      generationError.value = `Failed to generate draft: ${e.message}`
      console.error(e)
    } finally {
      isGenerating.value = false
    }
  }

  function extractTitleFromDraft() {
    const lines = draftText.value.split('\n')
    for (const l of lines) {
      const match = l.match(/^#\s+(.+)$/)
      if (match) {
        draftTitle.value = match[1].trim()
        return
      }
    }
    // Fallback title from prompt
    draftTitle.value = prompt.value.slice(0, 40).trim() || 'AI Generated Note'
  }

  async function approveAndSave(destinationFolderId = null) {
    const notesStore = useNotesStore()
    
    if (mode.value === 'tidy_note' && notesStore.activeNote) {
      // User approved updating the existing note
      notesStore.activeNote.content = draftText.value
      if (draftTitle.value && notesStore.activeNote.title === 'Untitled Note') {
        notesStore.activeNote.title = draftTitle.value
      }
      await notesStore.saveNote()
    } else {
      // User approved creating a new note in selected destination folder
      await notesStore.createNote(
        destinationFolderId || targetFolderId.value,
        draftTitle.value || 'AI Generated Note',
        draftText.value
      )
    }

    // Clean up staging
    discardDraft()
  }

  function discardDraft() {
    draftText.value = ''
    draftTitle.value = ''
    originalText.value = ''
    generationError.value = ''
    isStagingOpen.value = false
  }

  return {
    isDrawerOpen,
    isStagingOpen,
    isSettingsOpen,
    isSearchOpen,
    mode,
    tone,
    prompt,
    isGenerating,
    generationError,
    draftText,
    draftTitle,
    originalText,
    targetFolderId,
    activeProvider,
    aiStatus,
    fetchAIStatus,
    openDrawer,
    closeDrawer,
    generateDraft,
    approveAndSave,
    discardDraft
  }
})
