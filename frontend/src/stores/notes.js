import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useNotesStore = defineStore('notes', () => {
  const folders = ref([])
  const notes = ref([])
  const trashNotes = ref([])
  const activeNoteId = ref(null)
  const activeNote = ref(null)
  const activeFolderId = ref('all') // 'all' | 'tasks' | 'trash' | 'uncategorized' | folderId
  const isLoading = ref(false)
  const saveStatus = ref('saved') // 'saved' | 'saving' | 'error'
  let saveTimeout = null

  // Modals & Panels State
  const isMasterTasksOpen = ref(false)
  const isHistoryOpen = ref(false)
  const isTemplatesOpen = ref(false)
  const noteHistory = ref([])
  const allMasterTasks = ref([])
  const allMasterTargets = ref([])

  // Computed
  const currentFolderNotes = computed(() => {
    if (activeFolderId.value === 'all') return notes.value
    if (activeFolderId.value === 'trash') return trashNotes.value
    if (activeFolderId.value === 'uncategorized') {
      return notes.value.filter(n => !n.folder_id)
    }
    if (activeFolderId.value === 'tasks') {
      return notes.value.filter(n => n.content && n.content.includes('```tasks'))
    }
    return notes.value.filter(n => n.folder_id === activeFolderId.value)
  })

  const pinnedNotes = computed(() => {
    return notes.value.filter(n => n.is_pinned && !n.is_deleted)
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

  async function fetchTrashNotes() {
    try {
      const res = await fetch('/api/notes/trash')
      if (res.ok) {
        trashNotes.value = await res.json()
      }
    } catch (e) {
      console.error('Failed to fetch trash notes:', e)
    }
  }

  async function selectNote(id) {
    activeNoteId.value = id
    const match = notes.value.find(n => n.id === id) || trashNotes.value.find(n => n.id === id)
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
        folder_id: folderId && folderId !== 'all' && folderId !== 'tasks' && folderId !== 'trash' && folderId !== 'uncategorized' ? folderId : null
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
        await fetchFolders()
        return newNote
      }
    } catch (e) {
      console.error('Failed to create note:', e)
    }
  }

  async function createChecklistNote(folderId = null, title = 'Project Task Checklist') {
    const defaultTasks = [
      {
        id: `task-${Date.now()}-1`,
        title: "Define core deliverables and milestones",
        done: false,
        status: "In Progress",
        priority: "Urgent",
        due_date: new Date().toISOString().slice(0, 10)
      },
      {
        id: `task-${Date.now()}-2`,
        title: "Review checklist with stakeholders",
        done: false,
        status: "To Do",
        priority: "High",
        due_date: ""
      },
      {
        id: `task-${Date.now()}-3`,
        title: "Final sign-off and retrospective",
        done: false,
        status: "To Do",
        priority: "Normal",
        due_date: ""
      }
    ]
    const content = `# ${title}\n\nTrack progress, deadlines, and deliverables below:\n\n\`\`\`tasks\n${JSON.stringify(defaultTasks, null, 2)}\n\`\`\``
    return await createNote(folderId, title, content)
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

  // Soft delete (moves to trash)
  async function deleteNote(id) {
    try {
      const res = await fetch(`/api/notes/${id}`, { method: 'DELETE' })
      if (res.ok || res.status === 204) {
        const deleted = notes.value.find(n => n.id === id)
        if (deleted) {
          trashNotes.value.unshift({ ...deleted, is_deleted: true })
        }
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

  // Restore note from trash
  async function restoreNote(id) {
    try {
      const res = await fetch(`/api/notes/${id}/restore`, { method: 'POST' })
      if (res.ok) {
        const restored = await res.json()
        trashNotes.value = trashNotes.value.filter(n => n.id !== id)
        notes.value.unshift(restored)
        activeNoteId.value = restored.id
        activeNote.value = { ...restored }
        await fetchFolders()
      }
    } catch (e) {
      console.error('Failed to restore note:', e)
    }
  }

  // Permanent purge
  async function permanentDeleteNote(id) {
    try {
      const res = await fetch(`/api/notes/${id}/permanent`, { method: 'DELETE' })
      if (res.ok || res.status === 204) {
        trashNotes.value = trashNotes.value.filter(n => n.id !== id)
        if (activeNoteId.value === id) {
          activeNoteId.value = trashNotes.value.length ? trashNotes.value[0].id : null
          activeNote.value = trashNotes.value.length ? { ...trashNotes.value[0] } : null
        }
      }
    } catch (e) {
      console.error('Failed to purge note:', e)
    }
  }

  // Empty trash
  async function emptyTrash() {
    try {
      const res = await fetch('/api/notes/empty-trash', { method: 'POST' })
      if (res.ok) {
        trashNotes.value = []
        if (activeFolderId.value === 'trash') {
          activeNote.value = null
          activeNoteId.value = null
        }
      }
    } catch (e) {
      console.error('Failed to empty trash:', e)
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

  // History / Time Machine API
  async function fetchHistory(noteId) {
    try {
      const res = await fetch(`/api/notes/${noteId}/history`)
      if (res.ok) {
        noteHistory.value = await res.json()
      }
    } catch (e) {
      console.error('Failed to fetch history:', e)
    }
  }

  async function restoreHistory(noteId, historyId) {
    try {
      const res = await fetch(`/api/notes/${noteId}/restore-history/${historyId}`, { method: 'POST' })
      if (res.ok) {
        const restored = await res.json()
        activeNote.value = { ...restored }
        const idx = notes.value.findIndex(n => n.id === noteId)
        if (idx !== -1) notes.value[idx] = { ...restored }
        isHistoryOpen.value = false
      }
    } catch (e) {
      console.error('Failed to restore history snapshot:', e)
    }
  }

  // Master Tasks & Targets Aggregator API
  async function fetchAllTasks() {
    try {
      const [resTasks, resTargets] = await Promise.all([
        fetch('/api/notes/tasks/all'),
        fetch('/api/notes/targets/all')
      ])
      if (resTasks.ok) {
        allMasterTasks.value = await resTasks.json()
      }
      if (resTargets.ok) {
        allMasterTargets.value = await resTargets.json()
      }
    } catch (e) {
      console.error('Failed to fetch all tasks and targets:', e)
    }
  }

  return {
    folders,
    notes,
    trashNotes,
    activeNoteId,
    activeNote,
    activeFolderId,
    isLoading,
    saveStatus,
    currentFolderNotes,
    pinnedNotes,
    isMasterTasksOpen,
    isHistoryOpen,
    isTemplatesOpen,
    noteHistory,
    allMasterTasks,
    allMasterTargets,
    fetchFolders,
    createFolder,
    updateFolder,
    deleteFolder,
    fetchNotes,
    fetchTrashNotes,
    selectNote,
    createNote,
    createChecklistNote,
    queueSaveNote,
    saveNote,
    deleteNote,
    restoreNote,
    permanentDeleteNote,
    emptyTrash,
    togglePin,
    fetchHistory,
    restoreHistory,
    fetchAllTasks
  }
})
