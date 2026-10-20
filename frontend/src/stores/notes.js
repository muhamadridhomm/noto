import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useNotesStore = defineStore('notes', () => {
  const folders = ref([])
  const notes = ref([])
  const activeNoteId = ref(null)
  const activeNote = ref(null)
  const activeFolderId = ref('all') // 'all' | 'uncategorized' | folderId
  const isLoading = ref(false)
  const saveStatus = ref('saved') // 'saved' | 'saving' | 'error'
  let saveTimeout = null

  // Computed
  const currentFolderNotes = computed(() => {
    if (activeFolderId.value === 'all') return notes.value
    if (activeFolderId.value === 'uncategorized') {
      return notes.value.filter(n => !n.folder_id)
    }
    return notes.value.filter(n => n.folder_id === activeFolderId.value)
  })

  const pinnedNotes = computed(() => {
    return notes.value.filter(n => n.is_pinned)
  })

  // Folders API
  async function fetchFolders() {
    try {
      const res = await fetch('/api/folders')
      if (res.ok) {
        folders.value = await res.json()
      }
    } catch (e) {
      console.error('Failed to fetch folders:', e)
    }
  }

  async function createFolder(name, icon = 'folder') {
    try {
      const res = await fetch('/api/folders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, icon })
      })
      if (res.ok) {
        const newFolder = await res.json()
        folders.value.push(newFolder)
        return newFolder
      }
    } catch (e) {
      console.error('Failed to create folder:', e)
    }
  }

  async function updateFolder(id, updates) {
    try {
      const res = await fetch(`/api/folders/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      })
      if (res.ok) {
        const updated = await res.json()
        const idx = folders.value.findIndex(f => f.id === id)
        if (idx !== -1) folders.value[idx] = updated
        return updated
      }
    } catch (e) {
      console.error('Failed to update folder:', e)
    }
  }

  async function deleteFolder(id) {
    try {
      const res = await fetch(`/api/folders/${id}`, { method: 'DELETE' })
      if (res.ok || res.status === 204) {
        folders.value = folders.value.filter(f => f.id !== id)
        if (activeFolderId.value === id) {
          activeFolderId.value = 'all'
        }
        await fetchNotes()
      }
    } catch (e) {
      console.error('Failed to delete folder:', e)
    }
  }

  // Notes API
  async function fetchNotes(folderId = null) {
    isLoading.value = true
    try {
      let url = '/api/notes'
      if (folderId && folderId !== 'all') {
        url += `?folder_id=${encodeURIComponent(folderId)}`
      }
      const res = await fetch(url)
      if (res.ok) {
        notes.value = await res.json()
        if (activeNoteId.value) {
          const match = notes.value.find(n => n.id === activeNoteId.value)
          if (match) {
            activeNote.value = { ...match }
          }
        }
      }
    } catch (e) {
      console.error('Failed to fetch notes:', e)
    } finally {
      isLoading.value = false
    }
  }

  async function selectNote(id) {
    activeNoteId.value = id
    const match = notes.value.find(n => n.id === id)
    if (match) {
      activeNote.value = { ...match }
    } else {
      try {
        const res = await fetch(`/api/notes/${id}`)
        if (res.ok) {
          activeNote.value = await res.json()
        }
      } catch (e) {
        console.error('Failed to fetch note:', e)
      }
    }
  }

  async function createNote(folderId = null, title = 'Untitled Note', content = '') {
    try {
      const payload = {
        title: title || 'Untitled Note',
        content: content || '',
        folder_id: folderId && folderId !== 'all' && folderId !== 'uncategorized' ? folderId : null
      }
      const res = await fetch('/api/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      if (res.ok) {
        const newNote = await res.json()
        notes.value.unshift(newNote)
        activeNoteId.value = newNote.id
        activeNote.value = { ...newNote }
        await fetchFolders() // Refresh note counts
        return newNote
      }
    } catch (e) {
      console.error('Failed to create note:', e)
    }
  }

  function queueSaveNote(updates) {
    saveStatus.value = 'saving'
    if (saveTimeout) clearTimeout(saveTimeout)
    saveTimeout = setTimeout(async () => {
      await saveNote(updates)
    }, 400)
  }

  async function saveNote(updates = {}) {
    if (!activeNote.value) return
    try {
      const payload = {
        title: activeNote.value.title,
        content: activeNote.value.content,
        folder_id: activeNote.value.folder_id,
        is_pinned: activeNote.value.is_pinned,
        ...updates
      }
      const res = await fetch(`/api/notes/${activeNote.value.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      if (res.ok) {
        const updated = await res.json()
        saveStatus.value = 'saved'
        const idx = notes.value.findIndex(n => n.id === updated.id)
        if (idx !== -1) {
          notes.value[idx] = { ...updated }
        }
        activeNote.value = { ...updated }
      } else {
        saveStatus.value = 'error'
      }
    } catch (e) {
      saveStatus.value = 'error'
      console.error('Failed to save note:', e)
    }
  }

  async function deleteNote(id) {
    try {
      const res = await fetch(`/api/notes/${id}`, { method: 'DELETE' })
      if (res.ok || res.status === 204) {
        notes.value = notes.value.filter(n => n.id !== id)
        if (activeNoteId.value === id) {
          activeNoteId.value = notes.value.length ? notes.value[0].id : null
          activeNote.value = notes.value.length ? { ...notes.value[0] } : null
        }
        await fetchFolders()
      }
    } catch (e) {
      console.error('Failed to delete note:', e)
    }
  }

  async function togglePin(id) {
    const target = notes.value.find(n => n.id === id)
    if (!target) return
    const newPinned = !target.is_pinned
    target.is_pinned = newPinned
    if (activeNote.value && activeNote.value.id === id) {
      activeNote.value.is_pinned = newPinned
    }
    await fetch(`/api/notes/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_pinned: newPinned })
    })
  }

  return {
    folders,
    notes,
    activeNoteId,
    activeNote,
    activeFolderId,
    isLoading,
    saveStatus,
    currentFolderNotes,
    pinnedNotes,
    fetchFolders,
    createFolder,
    updateFolder,
    deleteFolder,
    fetchNotes,
    selectNote,
    createNote,
    queueSaveNote,
    saveNote,
    deleteNote,
    togglePin
  }
})
