<template>
  <div class="w-72 bg-white/70 border-r border-stone-200/80 flex flex-col h-full select-none">
    <!-- List Header -->
    <div class="p-3 border-b border-stone-200/70 flex items-center justify-between">
      <div>
        <h2 class="text-xs font-semibold text-stone-700 uppercase tracking-wider">
          {{ activeFolderName }}
        </h2>
        <span class="text-[11px] text-stone-400">
          {{ filteredNotes.length }} note{{ filteredNotes.length === 1 ? '' : 's' }}
        </span>
      </div>
      <button
        @click="handleNewNote"
        title="New Note in this view"
        class="text-stone-500 hover:text-stone-800 p-1 rounded-md hover:bg-stone-100 transition"
      >
        <Plus class="w-4 h-4" />
      </button>
    </div>

    <!-- Mini Filter Input -->
    <div class="p-2 border-b border-stone-100">
      <div class="relative">
        <Search class="w-3.5 h-3.5 text-stone-400 absolute left-2.5 top-2.5" />
        <input
          v-model="filterQuery"
          type="text"
          placeholder="Filter notes..."
          class="w-full text-xs pl-8 pr-2 py-1.5 bg-stone-100/70 border border-stone-200 rounded-md focus:outline-none focus:ring-1 focus:ring-brand-500 placeholder-stone-400"
        />
      </div>
    </div>

    <!-- Notes Scroll Area -->
    <div class="flex-1 overflow-y-auto divide-y divide-stone-100">
      <div v-if="filteredNotes.length === 0" class="p-6 text-center text-xs text-stone-400">
        No notes found here. Click <span class="font-medium text-stone-600">+</span> to write one!
      </div>

      <div
        v-for="note in filteredNotes"
        :key="note.id"
        @click="notesStore.selectNote(note.id)"
        class="group p-3 cursor-pointer transition text-left relative"
        :class="[
          notesStore.activeNoteId === note.id
            ? 'bg-brand-50/60 border-l-2 border-brand-600'
            : 'hover:bg-stone-50/90'
        ]"
      >
        <div class="flex items-start justify-between gap-1 mb-1">
          <h3
            class="text-sm font-medium truncate flex-1"
            :class="notesStore.activeNoteId === note.id ? 'text-brand-900 font-semibold' : 'text-stone-800'"
          >
            {{ note.title || 'Untitled Note' }}
          </h3>
          <div class="flex items-center gap-1 shrink-0">
            <button
              @click.stop="notesStore.togglePin(note.id)"
              :title="note.is_pinned ? 'Unpin note' : 'Pin note'"
              class="p-0.5 rounded transition"
              :class="note.is_pinned ? 'text-amber-500' : 'text-stone-300 opacity-0 group-hover:opacity-100 hover:text-stone-600'"
            >
              <Pin class="w-3.5 h-3.5" :class="{ 'fill-amber-500': note.is_pinned }" />
            </button>
            <button
              @click.stop="confirmDelete(note)"
              title="Delete note"
              class="p-0.5 text-stone-300 opacity-0 group-hover:opacity-100 hover:text-rose-600 transition"
            >
              <Trash2 class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        <p class="text-xs text-stone-500 line-clamp-2 leading-relaxed">
          {{ note.content ? note.content.slice(0, 120) : 'No content yet...' }}
        </p>

        <div class="mt-2 flex items-center justify-between text-[11px] text-stone-400 font-mono">
          <span>{{ formatDate(note.updated_at) }}</span>
          <span v-if="getFolderName(note.folder_id)" class="text-[10px] bg-stone-100 px-1.5 py-0.5 rounded text-stone-600 font-sans">
            {{ getFolderName(note.folder_id) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useNotesStore } from '../stores/notes'
import { Plus, Search, Pin, Trash2 } from 'lucide-vue-next'

const notesStore = useNotesStore()
const filterQuery = ref('')

const activeFolderName = computed(() => {
  if (notesStore.activeFolderId === 'all') return 'All Notes'
  if (notesStore.activeFolderId === 'uncategorized') return 'Unfiled Notes'
  const folder = notesStore.folders.find(f => f.id === notesStore.activeFolderId)
  return folder ? folder.name : 'Notes'
})

const filteredNotes = computed(() => {
  let list = notesStore.currentFolderNotes
  if (filterQuery.value.trim()) {
    const q = filterQuery.value.toLowerCase()
    list = list.filter(n => 
      (n.title && n.title.toLowerCase().includes(q)) ||
      (n.content && n.content.toLowerCase().includes(q))
    )
  }
  return list
})

function getFolderName(folderId) {
  if (!folderId) return null
  const f = notesStore.folders.find(x => x.id === folderId)
  return f ? f.name : null
}

function handleNewNote() {
  const folderId = notesStore.activeFolderId !== 'all' && notesStore.activeFolderId !== 'uncategorized'
    ? notesStore.activeFolderId
    : null
  notesStore.createNote(folderId)
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

async function confirmDelete(note) {
  if (confirm(`Delete "${note.title || 'Untitled Note'}"?`)) {
    await notesStore.deleteNote(note.id)
  }
}
</script>
