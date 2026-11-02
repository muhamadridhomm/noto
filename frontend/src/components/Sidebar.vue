<template>
  <aside class="w-64 bg-stone-100/90 border-r border-stone-200/80 flex flex-col h-full select-none">
    <!-- Workspace Brand Header -->
    <div class="p-3.5 border-b border-stone-200/70 flex items-center justify-between bg-stone-50/50">
      <div class="flex items-center gap-2.5">
        <!-- Modern SVG Emblem -->
        <div class="w-8 h-8 rounded-xl shadow-xs overflow-hidden shrink-0 flex items-center justify-center bg-gradient-to-br from-indigo-600 to-brand-600 p-0.5">
          <img src="/noto-logo.svg" alt="Noto Logo" class="w-full h-full object-contain rounded-[10px]" />
        </div>
        <div class="flex flex-col">
          <div class="flex items-center gap-1.5">
            <span class="font-bold text-stone-900 tracking-tight text-sm font-sans">Noto</span>
            <span class="text-[9px] font-mono px-1.5 py-0.2 rounded-full bg-brand-50 text-brand-700 border border-brand-200 font-semibold">
              AI
            </span>
          </div>
          <span class="text-[10px] text-stone-400 font-medium tracking-tight">Notes & Roadmap Hub</span>
        </div>
      </div>
      <button
        @click="aiStore.isSettingsOpen = true"
        title="Settings"
        class="text-stone-400 hover:text-stone-700 p-1.5 rounded-lg hover:bg-stone-200/60 transition"
      >
        <Settings class="w-4 h-4" />
      </button>
    </div>

    <!-- Quick Action Buttons -->
    <div class="p-3 space-y-1.5">
      <button
        @click="handleNewNote"
        class="w-full flex items-center justify-center gap-2 py-2 px-3 bg-stone-900 hover:bg-stone-800 text-white rounded-lg text-sm font-medium shadow-sm transition active:scale-[0.99]"
      >
        <Plus class="w-4 h-4" />
        <span>New Note</span>
      </button>

      <div class="grid grid-cols-2 gap-1.5">
        <button
          @click="openMasterTasks"
          class="flex items-center justify-center gap-1.5 py-1.5 px-2 bg-white hover:bg-stone-50 border border-stone-200 rounded-md text-xs font-medium text-stone-700 transition shadow-2xs"
          title="Combined Master Timeline & Tasks Hub"
        >
          <CalendarDays class="w-3.5 h-3.5 text-brand-600" />
          <span>Timeline Hub</span>
        </button>

        <button
          @click="notesStore.isTemplatesOpen = true"
          class="flex items-center justify-center gap-1.5 py-1.5 px-2 bg-white hover:bg-stone-50 border border-stone-200 rounded-md text-xs font-medium text-stone-700 transition shadow-2xs"
          title="Open template gallery"
        >
          <LayoutTemplate class="w-3.5 h-3.5 text-amber-600" />
          <span>Templates</span>
        </button>
      </div>

      <button
        @click="aiStore.openDrawer('new_note')"
        class="w-full flex items-center justify-center gap-2 py-2 px-3 bg-gradient-to-r from-brand-50 to-indigo-50 hover:from-brand-100 hover:to-indigo-100 text-brand-700 border border-brand-200/80 rounded-lg text-sm font-medium transition active:scale-[0.99]"
      >
        <Sparkles class="w-4 h-4 text-brand-600" />
        <span>Ask AI Assistant</span>
        <span class="ml-auto text-[10px] font-mono text-brand-500 bg-white/80 px-1.5 py-0.5 rounded border border-brand-200">Ctrl+J</span>
      </button>

      <button
        @click="aiStore.isSearchOpen = true"
        class="w-full flex items-center gap-2 py-1.5 px-2.5 text-stone-600 hover:text-stone-900 hover:bg-stone-200/60 rounded-md text-sm transition"
      >
        <Search class="w-4 h-4 text-stone-400" />
        <span>Quick Search</span>
        <span class="ml-auto text-[10px] font-mono text-stone-400 bg-stone-200/70 px-1.5 py-0.5 rounded">Ctrl+K</span>
      </button>
    </div>

    <!-- Navigation Views -->
    <div class="px-2 py-1 space-y-0.5">
      <button
        @click="selectFolder('all')"
        :class="[
          'w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md text-sm transition text-left',
          notesStore.activeFolderId === 'all'
            ? 'bg-stone-200/80 text-stone-900 font-medium'
            : 'text-stone-600 hover:bg-stone-200/50 hover:text-stone-800'
        ]"
      >
        <Files class="w-4 h-4 text-stone-500" />
        <span class="flex-1 truncate">All Notes</span>
        <span class="text-xs text-stone-400 font-mono">{{ notesStore.notes.length }}</span>
      </button>

      <button
        @click="selectFolder('tasks')"
        :class="[
          'w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md text-sm transition text-left',
          notesStore.activeFolderId === 'tasks'
            ? 'bg-emerald-50 text-emerald-900 font-semibold border border-emerald-200/60'
            : 'text-stone-600 hover:bg-stone-200/50 hover:text-stone-800'
        ]"
      >
        <CheckSquare class="w-4 h-4 text-emerald-600" />
        <span class="flex-1 truncate">Tasks & Checklists</span>
        <span class="text-xs text-emerald-700 font-mono">
          {{ notesStore.notes.filter(n => n.content && n.content.includes('```tasks')).length }}
        </span>
      </button>

      <button
        @click="selectFolder('uncategorized')"
        :class="[
          'w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md text-sm transition text-left',
          notesStore.activeFolderId === 'uncategorized'
            ? 'bg-stone-200/80 text-stone-900 font-medium'
            : 'text-stone-600 hover:bg-stone-200/50 hover:text-stone-800'
        ]"
      >
        <FileText class="w-4 h-4 text-stone-400" />
        <span class="flex-1 truncate">Unfiled Notes</span>
        <span class="text-xs text-stone-400 font-mono">
          {{ notesStore.notes.filter(n => !n.folder_id).length }}
        </span>
      </button>

      <!-- Trash / Recycle Bin Navigation Item -->
      <button
        @click="selectFolder('trash')"
        :class="[
          'w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md text-sm transition text-left',
          notesStore.activeFolderId === 'trash'
            ? 'bg-rose-50 text-rose-900 font-medium border border-rose-200/60'
            : 'text-stone-500 hover:bg-stone-200/50 hover:text-stone-800'
        ]"
      >
        <Trash2 class="w-4 h-4 text-stone-400" />
        <span class="flex-1 truncate">Trash</span>
        <span class="text-xs text-stone-400 font-mono">
          {{ notesStore.trashNotes.length }}
        </span>
      </button>
    </div>

    <!-- Folders / Collections Section -->
    <div class="flex-1 overflow-y-auto px-2 py-3">
      <div class="flex items-center justify-between px-2 mb-1.5">
        <span class="text-[11px] font-semibold uppercase tracking-wider text-stone-400">Folders</span>
        <button
          @click="isCreatingFolder = true"
          title="New Folder"
          class="text-stone-400 hover:text-stone-700 p-0.5 rounded hover:bg-stone-200 transition"
        >
          <Plus class="w-3.5 h-3.5" />
        </button>
      </div>

      <!-- Inline Folder Creation Input -->
      <div v-if="isCreatingFolder" class="px-2 py-1 mb-1">
        <input
          v-model="newFolderName"
          @keydown.enter="submitCreateFolder"
          @keydown.esc="isCreatingFolder = false"
          ref="newFolderInput"
          type="text"
          placeholder="Folder name..."
          class="w-full text-xs px-2 py-1.5 bg-white border border-stone-300 rounded focus:outline-none focus:ring-1 focus:ring-brand-500"
        />
      </div>

      <!-- Folder Items -->
      <div class="space-y-0.5">
        <div
          v-for="folder in notesStore.folders"
          :key="folder.id"
          class="group flex items-center justify-between rounded-md px-2.5 py-1.5 text-sm transition cursor-pointer"
          :class="[
            notesStore.activeFolderId === folder.id
              ? 'bg-stone-200/80 text-stone-900 font-medium'
              : 'text-stone-600 hover:bg-stone-200/50 hover:text-stone-800'
          ]"
          @click="selectFolder(folder.id)"
        >
          <div class="flex items-center gap-2 truncate flex-1 mr-1">
            <Folder class="w-4 h-4 text-amber-500 shrink-0" />
            <span class="truncate">{{ folder.name }}</span>
          </div>

          <div class="flex items-center gap-1">
            <span class="text-xs text-stone-400 font-mono group-hover:hidden">
              {{ folder.note_count }}
            </span>
            <button
              @click.stop="confirmDeleteFolder(folder)"
              title="Delete folder"
              class="hidden group-hover:inline-flex text-stone-400 hover:text-rose-600 p-0.5 rounded transition"
            >
              <Trash2 class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Status / Active Provider Indicator -->
    <div class="p-2.5 border-t border-stone-200/80 bg-stone-100 text-xs text-stone-500 flex items-center justify-between">
      <div class="flex items-center gap-1.5 truncate">
        <span class="w-2 h-2 rounded-full" :class="providerStatusColor"></span>
        <span class="truncate capitalize">{{ aiStore.activeProvider }} AI active</span>
      </div>
      <button
        @click="aiStore.isSettingsOpen = true"
        class="text-stone-400 hover:text-stone-700 underline text-[11px]"
      >
        Configure
      </button>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useNotesStore } from '../stores/notes'
import { useAIStore } from '../stores/ai'
import {
  Plus, Sparkles, Search, Files, FileText, Folder, Trash2, Settings, CheckSquare, LayoutTemplate, CalendarDays
} from 'lucide-vue-next'

const notesStore = useNotesStore()
const aiStore = useAIStore()

const isCreatingFolder = ref(false)
const newFolderName = ref('')
const newFolderInput = ref(null)

onMounted(() => {
  notesStore.fetchTrashNotes()
})

const providerStatusColor = computed(() => {
  if (aiStore.activeProvider === 'gemini') {
    return aiStore.aiStatus.gemini_configured ? 'bg-emerald-500' : 'bg-amber-400'
  }
  return aiStore.aiStatus.ollama_available ? 'bg-emerald-500' : 'bg-stone-300'
})

function selectFolder(id) {
  notesStore.activeFolderId = id
  if (id === 'trash') {
    notesStore.fetchTrashNotes()
  } else {
    notesStore.fetchNotes(id)
  }
}

function openMasterTasks() {
  notesStore.fetchAllTasks()
  notesStore.isMasterTasksOpen = true
}

function handleNewNote() {
  const targetFolder = notesStore.activeFolderId !== 'all' && notesStore.activeFolderId !== 'uncategorized' && notesStore.activeFolderId !== 'tasks' && notesStore.activeFolderId !== 'trash'
    ? notesStore.activeFolderId
    : null
  notesStore.createNote(targetFolder)
}

async function submitCreateFolder() {
  if (!newFolderName.value.trim()) {
    isCreatingFolder.value = false
    return
  }
  await notesStore.createFolder(newFolderName.value.trim())
  newFolderName.value = ''
  isCreatingFolder.value = false
}

async function confirmDeleteFolder(folder) {
  if (confirm(`Delete folder "${folder.name}"? Notes inside will be kept in unfiled notes.`)) {
    await notesStore.deleteFolder(folder.id)
  }
}
</script>
