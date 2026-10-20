<template>
  <div
    v-if="aiStore.isStagingOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-stone-900/40 backdrop-blur-xs select-none"
  >
    <div class="w-full max-w-4xl bg-white rounded-xl shadow-2xl flex flex-col h-[85vh] overflow-hidden border border-stone-200 animate-in fade-in zoom-in-95 duration-150">
      <!-- Modal Header -->
      <div class="px-6 py-4 border-b border-stone-200/80 bg-stone-50/70 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="p-2 rounded-lg bg-emerald-100 text-emerald-700">
            <CheckCircle2 class="w-5 h-5" />
          </div>
          <div>
            <h3 class="text-sm font-semibold text-stone-900 flex items-center gap-2">
              <span>Review AI Draft</span>
              <span class="text-[10px] font-mono font-normal uppercase px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                Staged & Safe
              </span>
            </h3>
            <p class="text-xs text-stone-500">
              Inspect the draft below. Edit anything before saving, choose where it goes, or discard it.
            </p>
          </div>
        </div>

        <button
          @click="aiStore.discardDraft"
          title="Discard and close"
          class="text-stone-400 hover:text-stone-700 p-1.5 rounded-md hover:bg-stone-200/60 transition"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Review Sub-toolbar: View Modes & Editable Title -->
      <div class="px-6 py-3 border-b border-stone-100 bg-white flex flex-wrap items-center justify-between gap-3">
        <!-- Draft Title Field -->
        <div class="flex items-center gap-2 flex-1 min-w-[240px]">
          <span class="text-xs font-semibold text-stone-400 uppercase tracking-wider shrink-0">Title:</span>
          <input
            v-model="aiStore.draftTitle"
            type="text"
            placeholder="Draft Note Title..."
            class="w-full text-sm font-semibold text-stone-900 border border-stone-200 rounded-md px-2.5 py-1 focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
        </div>

        <!-- View Tabs -->
        <div class="flex items-center bg-stone-100 p-0.5 rounded-lg text-xs font-medium text-stone-600">
          <button
            @click="activeTab = 'preview'"
            :class="['px-3 py-1 rounded-md transition', activeTab === 'preview' ? 'bg-white shadow-xs text-stone-900 font-semibold' : 'hover:text-stone-900']"
          >
            Formatted Preview
          </button>
          <button
            @click="activeTab = 'edit'"
            :class="['px-3 py-1 rounded-md transition', activeTab === 'edit' ? 'bg-white shadow-xs text-stone-900 font-semibold' : 'hover:text-stone-900']"
          >
            Direct Edit
          </button>
          <button
            v-if="aiStore.mode === 'tidy_note' && aiStore.originalText"
            @click="activeTab = 'diff'"
            :class="['px-3 py-1 rounded-md transition', activeTab === 'diff' ? 'bg-white shadow-xs text-stone-900 font-semibold' : 'hover:text-stone-900']"
          >
            Side-by-Side Diff
          </button>
        </div>
      </div>

      <!-- Main Staged Content Body -->
      <div class="flex-1 overflow-y-auto p-6 bg-stone-50/30">
        <!-- Tab 1: Formatted Markdown Preview -->
        <div
          v-if="activeTab === 'preview'"
          class="bg-white p-6 rounded-lg border border-stone-200/80 shadow-xs markdown-body min-h-full"
          v-html="renderedDraft"
        ></div>

        <!-- Tab 2: Direct Edit Textarea -->
        <div v-else-if="activeTab === 'edit'" class="h-full flex flex-col">
          <textarea
            v-model="aiStore.draftText"
            placeholder="Edit draft markdown directly..."
            class="flex-1 w-full p-4 bg-white border border-stone-200 rounded-lg text-xs sm:text-sm font-mono leading-relaxed focus:outline-none focus:ring-1 focus:ring-brand-500 resize-none shadow-xs"
          ></textarea>
        </div>

        <!-- Tab 3: Side-by-Side Diff -->
        <div v-else-if="activeTab === 'diff'" class="grid grid-cols-2 gap-4 h-full">
          <div class="bg-white p-4 rounded-lg border border-stone-200 flex flex-col overflow-hidden">
            <h4 class="text-xs font-semibold text-stone-500 uppercase tracking-wider mb-2 pb-1 border-b border-stone-100 flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-rose-400"></span>
              Original Note Text
            </h4>
            <div class="flex-1 overflow-y-auto font-mono text-xs text-stone-700 whitespace-pre-wrap leading-relaxed">
              {{ aiStore.originalText }}
            </div>
          </div>

          <div class="bg-white p-4 rounded-lg border border-brand-200 flex flex-col overflow-hidden">
            <h4 class="text-xs font-semibold text-brand-700 uppercase tracking-wider mb-2 pb-1 border-b border-brand-100 flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
              AI Proposed Version
            </h4>
            <div class="flex-1 overflow-y-auto font-mono text-xs text-stone-900 whitespace-pre-wrap leading-relaxed">
              {{ aiStore.draftText }}
            </div>
          </div>
        </div>
      </div>

      <!-- Destination Picker & Bottom Action Bar -->
      <div class="px-6 py-4 border-t border-stone-200/80 bg-stone-50 flex flex-wrap items-center justify-between gap-4">
        <!-- Destination Picker -->
        <div class="flex items-center gap-3">
          <label class="text-xs font-semibold text-stone-600 flex items-center gap-1.5">
            <Folder class="w-4 h-4 text-amber-500" />
            <span>Save to Destination:</span>
          </label>

          <!-- For tidy mode, option to overwrite active note or save as new page -->
          <select
            v-if="aiStore.mode === 'tidy_note'"
            v-model="tidyDestination"
            class="text-xs bg-white border border-stone-300 rounded-md px-2.5 py-1.5 font-medium text-stone-800 focus:outline-none focus:ring-1 focus:ring-brand-500 shadow-2xs"
          >
            <option value="replace_active">Apply to Active Note ({{ notesStore.activeNote?.title || 'Current' }})</option>
            <option value="new_note">Save as a New Separate Note</option>
          </select>

          <!-- Folder Picker if saving as new note -->
          <select
            v-if="aiStore.mode === 'new_note' || tidyDestination === 'new_note'"
            v-model="selectedFolderId"
            class="text-xs bg-white border border-stone-300 rounded-md px-2.5 py-1.5 font-medium text-stone-800 focus:outline-none focus:ring-1 focus:ring-brand-500 shadow-2xs"
          >
            <option :value="null">Unfiled Notes</option>
            <option v-for="f in notesStore.folders" :key="f.id" :value="f.id">
              📁 {{ f.name }}
            </option>
          </select>
        </div>

        <!-- Approval & Discard Buttons -->
        <div class="flex items-center gap-3">
          <button
            @click="handleDiscard"
            class="px-4 py-2 text-xs font-medium text-stone-600 hover:text-rose-600 hover:bg-stone-200/60 rounded-lg transition"
          >
            Discard Draft
          </button>

          <button
            @click="handleApprove"
            class="flex items-center gap-2 px-5 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-semibold shadow-sm transition active:scale-[0.99]"
          >
            <Check class="w-4 h-4" />
            <span>Approve & Save Note</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAIStore } from '../stores/ai'
import { useNotesStore } from '../stores/notes'
import { marked } from 'marked'
import { CheckCircle2, X, Folder, Check } from 'lucide-vue-next'

const aiStore = useAIStore()
const notesStore = useNotesStore()

const activeTab = ref('preview') // 'preview' | 'edit' | 'diff'
const selectedFolderId = ref(notesStore.activeFolderId !== 'all' && notesStore.activeFolderId !== 'uncategorized' ? notesStore.activeFolderId : null)
const tidyDestination = ref('replace_active')

const renderedDraft = computed(() => {
  if (!aiStore.draftText) {
    return '<p class="text-stone-300 italic">No draft content...</p>'
  }
  try {
    return marked.parse(aiStore.draftText)
  } catch (e) {
    return `<pre>${aiStore.draftText}</pre>`
  }
})

function handleDiscard() {
  aiStore.discardDraft()
}

async function handleApprove() {
  if (aiStore.mode === 'tidy_note' && tidyDestination.value === 'replace_active') {
    await aiStore.approveAndSave()
  } else {
    await notesStore.createNote(
      selectedFolderId.value,
      aiStore.draftTitle || 'AI Note',
      aiStore.draftText
    )
    aiStore.discardDraft()
  }
}
</script>
