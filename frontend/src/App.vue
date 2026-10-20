<template>
  <div class="flex h-screen w-screen overflow-hidden bg-white text-stone-900 font-sans">
    <!-- Left Workspace Navigation -->
    <Sidebar />

    <!-- Middle Notes List -->
    <NoteList />

    <!-- Right Main Editor Workspace -->
    <NoteEditor />

    <!-- AI Copilot Slide-out Drawer -->
    <AIDrawer />

    <!-- Staging & Human Review Modal -->
    <StagingModal />

    <!-- Global Quick Search (Ctrl+K) -->
    <SearchModal />

    <!-- Settings & AI Config Modal -->
    <SettingsModal />
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useNotesStore } from './stores/notes'
import { useAIStore } from './stores/ai'

import Sidebar from './components/Sidebar.vue'
import NoteList from './components/NoteList.vue'
import NoteEditor from './components/NoteEditor.vue'
import AIDrawer from './components/AIDrawer.vue'
import StagingModal from './components/StagingModal.vue'
import SearchModal from './components/SearchModal.vue'
import SettingsModal from './components/SettingsModal.vue'

const notesStore = useNotesStore()
const aiStore = useAIStore()

function handleGlobalKeydown(e) {
  // Ctrl+J or Cmd+J: Open AI Drawer
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'j') {
    e.preventDefault()
    if (aiStore.isDrawerOpen) {
      aiStore.closeDrawer()
    } else {
      aiStore.openDrawer('new_note')
    }
  }

  // Ctrl+K or Cmd+K: Open Search
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault()
    aiStore.isSearchOpen = !aiStore.isSearchOpen
  }

  // Ctrl+S or Cmd+S: Force immediate save
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
    e.preventDefault()
    if (notesStore.activeNote) {
      notesStore.saveNote()
    }
  }
}

onMounted(async () => {
  window.addEventListener('keydown', handleGlobalKeydown)
  
  await notesStore.fetchFolders()
  await notesStore.fetchNotes()
  await aiStore.fetchAIStatus()

  // Select initial note if available
  if (notesStore.notes.length > 0 && !notesStore.activeNoteId) {
    await notesStore.selectNote(notesStore.notes[0].id)
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
})
</script>
