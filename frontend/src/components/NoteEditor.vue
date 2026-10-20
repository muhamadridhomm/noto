<template>
  <div class="flex-1 flex flex-col h-full bg-white overflow-hidden">
    <!-- Empty State -->
    <div v-if="!notesStore.activeNote" class="flex-1 flex flex-col items-center justify-center p-8 text-center bg-stone-50/50">
      <div class="w-14 h-14 rounded-2xl bg-stone-100 flex items-center justify-center text-stone-400 mb-4 shadow-sm">
        <FileText class="w-7 h-7" />
      </div>
      <h3 class="text-base font-semibold text-stone-800 mb-1">Select or create a note</h3>
      <p class="text-xs text-stone-500 max-w-sm mb-6 leading-relaxed">
        Choose a note from the list, start a fresh one, or ask Noto AI to draft something for you.
      </p>
      <div class="flex items-center gap-3">
        <button
          @click="notesStore.createNote()"
          class="flex items-center gap-2 px-3.5 py-2 bg-stone-900 hover:bg-stone-800 text-white rounded-lg text-xs font-medium transition shadow-sm"
        >
          <Plus class="w-3.5 h-3.5" />
          <span>New Note</span>
        </button>
        <button
          @click="aiStore.openDrawer('new_note')"
          class="flex items-center gap-2 px-3.5 py-2 bg-brand-50 hover:bg-brand-100 text-brand-700 border border-brand-200 rounded-lg text-xs font-medium transition"
        >
          <Sparkles class="w-3.5 h-3.5 text-brand-600" />
          <span>Ask AI to Draft</span>
        </button>
      </div>
    </div>

    <!-- Active Note View -->
    <div v-else class="flex-1 flex flex-col h-full overflow-hidden">
      <!-- Editor Top Toolbar -->
      <div class="h-12 border-b border-stone-200/80 px-6 flex items-center justify-between shrink-0 bg-white">
        <!-- Folder Destination Selector & Save Status -->
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1.5 text-xs text-stone-500">
            <Folder class="w-3.5 h-3.5 text-stone-400" />
            <select
              v-model="notesStore.activeNote.folder_id"
              @change="onFolderChange"
              class="bg-transparent border-none text-xs text-stone-700 font-medium focus:outline-none cursor-pointer hover:text-stone-900"
            >
              <option :value="null">Unfiled</option>
              <option v-for="f in notesStore.folders" :key="f.id" :value="f.id">
                {{ f.name }}
              </option>
            </select>
          </div>

          <span class="text-stone-300">|</span>

          <!-- Auto-save Status Indicator -->
          <div class="flex items-center gap-1 text-[11px] text-stone-400 font-mono">
            <span
              class="w-1.5 h-1.5 rounded-full"
              :class="{
                'bg-emerald-500': notesStore.saveStatus === 'saved',
                'bg-amber-400 animate-pulse': notesStore.saveStatus === 'saving',
                'bg-rose-500': notesStore.saveStatus === 'error'
              }"
            ></span>
            <span>
              {{ notesStore.saveStatus === 'saving' ? 'Saving...' : notesStore.saveStatus === 'error' ? 'Failed to save' : 'Saved' }}
            </span>
          </div>
        </div>

        <!-- Right Action Controls -->
        <div class="flex items-center gap-2">
          <!-- AI Tidy Action Button -->
          <button
            @click="handleAITidy"
            title="Ask AI to improve, tidy, or reformat this note"
            class="flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium text-brand-700 bg-brand-50 hover:bg-brand-100 border border-brand-200/80 rounded-md transition"
          >
            <Sparkles class="w-3.5 h-3.5 text-brand-600" />
            <span>Tidy Note with AI</span>
          </button>

          <!-- View Mode Toggle -->
          <div class="flex items-center bg-stone-100 p-0.5 rounded-md text-xs text-stone-600">
            <button
              @click="viewMode = 'edit'"
              :class="['px-2 py-0.5 rounded transition', viewMode === 'edit' ? 'bg-white shadow-xs font-medium text-stone-900' : 'hover:text-stone-900']"
            >
              Write
            </button>
            <button
              @click="viewMode = 'split'"
              :class="['px-2 py-0.5 rounded transition', viewMode === 'split' ? 'bg-white shadow-xs font-medium text-stone-900' : 'hover:text-stone-900']"
            >
              Split
            </button>
            <button
              @click="viewMode = 'preview'"
              :class="['px-2 py-0.5 rounded transition', viewMode === 'preview' ? 'bg-white shadow-xs font-medium text-stone-900' : 'hover:text-stone-900']"
            >
              Preview
            </button>
          </div>

          <!-- Pin Button -->
          <button
            @click="notesStore.togglePin(notesStore.activeNote.id)"
            title="Toggle pin"
            class="p-1 rounded-md text-stone-400 hover:text-stone-700 hover:bg-stone-100 transition"
          >
            <Pin class="w-4 h-4" :class="{ 'fill-amber-500 text-amber-500': notesStore.activeNote.is_pinned }" />
          </button>
        </div>
      </div>

      <!-- Note Title Header -->
      <div class="px-8 pt-6 pb-2 shrink-0">
        <input
          v-model="notesStore.activeNote.title"
          @input="onContentChange"
          type="text"
          placeholder="Untitled Note"
          class="w-full text-2xl font-bold text-stone-900 placeholder-stone-300 border-none bg-transparent focus:outline-none focus:ring-0 tracking-tight"
        />
      </div>

      <!-- Editor Content Workspace -->
      <div class="flex-1 flex overflow-hidden px-8 pb-4">
        <!-- Markdown Raw Editor -->
        <div
          v-show="viewMode === 'edit' || viewMode === 'split'"
          class="flex-1 flex flex-col h-full"
          :class="{ 'pr-4 border-r border-stone-200/60': viewMode === 'split' }"
        >
          <textarea
            v-model="notesStore.activeNote.content"
            @input="onContentChange"
            @keydown.tab.prevent="insertTab"
            placeholder="Write your note here... (Markdown supported, or press Ctrl+J for AI assistant)"
            class="w-full h-full resize-none font-mono text-xs sm:text-sm text-stone-800 leading-relaxed bg-transparent border-none focus:outline-none focus:ring-0 placeholder-stone-300"
          ></textarea>
        </div>

        <!-- Rendered Markdown Preview -->
        <div
          v-show="viewMode === 'preview' || viewMode === 'split'"
          class="flex-1 h-full overflow-y-auto markdown-body"
          :class="{ 'pl-4': viewMode === 'split' }"
          v-html="renderedMarkdown"
        ></div>
      </div>

      <!-- Bottom Stats Bar -->
      <div class="h-7 border-t border-stone-100 px-8 flex items-center justify-between text-[11px] text-stone-400 font-mono shrink-0">
        <div class="flex items-center gap-4">
          <span>{{ wordCount }} words</span>
          <span>{{ charCount }} characters</span>
        </div>
        <div>
          <span>Markdown Enabled</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useNotesStore } from '../stores/notes'
import { useAIStore } from '../stores/ai'
import { marked } from 'marked'
import {
  FileText, Plus, Sparkles, Folder, Pin
} from 'lucide-vue-next'

const notesStore = useNotesStore()
const aiStore = useAIStore()
const viewMode = ref('edit') // 'edit' | 'split' | 'preview'

const wordCount = computed(() => {
  if (!notesStore.activeNote || !notesStore.activeNote.content) return 0
  return notesStore.activeNote.content.trim().split(/\s+/).filter(Boolean).length
})

const charCount = computed(() => {
  if (!notesStore.activeNote || !notesStore.activeNote.content) return 0
  return notesStore.activeNote.content.length
})

const renderedMarkdown = computed(() => {
  if (!notesStore.activeNote || !notesStore.activeNote.content) {
    return '<p class="text-stone-300 italic">Empty note preview...</p>'
  }
  try {
    return marked.parse(notesStore.activeNote.content)
  } catch (e) {
    return `<pre>${notesStore.activeNote.content}</pre>`
  }
})

function onContentChange() {
  notesStore.queueSaveNote()
}

function onFolderChange() {
  notesStore.saveNote({ folder_id: notesStore.activeNote.folder_id })
}

function handleAITidy() {
  if (!notesStore.activeNote) return
  aiStore.openDrawer('tidy_note', notesStore.activeNote.content)
}

function insertTab(e) {
  const textarea = e.target
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const value = textarea.value
  textarea.value = value.substring(0, start) + '  ' + value.substring(end)
  textarea.selectionStart = textarea.selectionEnd = start + 2
  notesStore.activeNote.content = textarea.value
  notesStore.queueSaveNote()
}
</script>
