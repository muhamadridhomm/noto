<template>
  <div
    v-if="notesStore.isHistoryOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-stone-900/40 backdrop-blur-xs select-none"
    @click.self="notesStore.isHistoryOpen = false"
  >
    <div class="w-full max-w-4xl bg-white rounded-xl shadow-2xl h-[80vh] flex flex-col overflow-hidden border border-stone-200 animate-in fade-in zoom-in-95 duration-150">
      <!-- Modal Header -->
      <div class="px-6 py-4 border-b border-stone-200 bg-stone-50/80 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="p-2 rounded-lg bg-indigo-100 text-indigo-700">
            <History class="w-5 h-5" />
          </div>
          <div>
            <h3 class="text-sm font-bold text-stone-900 flex items-center gap-2">
              <span>Version History (Time Machine)</span>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
                Safe Snapshots
              </span>
            </h3>
            <p class="text-xs text-stone-500">
              Browse previous snapshots of "{{ notesStore.activeNote?.title }}" and restore if needed
            </p>
          </div>
        </div>

        <button
          @click="notesStore.isHistoryOpen = false"
          class="text-stone-400 hover:text-stone-700 p-1.5 rounded-md hover:bg-stone-200/60 transition"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Main History Workspace -->
      <div class="flex-1 flex overflow-hidden">
        <!-- Revisions List (Left) -->
        <div class="w-72 border-r border-stone-200 bg-stone-50/50 flex flex-col shrink-0">
          <div class="px-4 py-2.5 border-b border-stone-200/70 text-[11px] font-bold uppercase tracking-wider text-stone-400">
            Snapshots ({{ notesStore.noteHistory.length }})
          </div>

          <div class="flex-1 overflow-y-auto divide-y divide-stone-200/60">
            <div v-if="notesStore.noteHistory.length === 0" class="p-6 text-center text-xs text-stone-400">
              No previous revisions saved yet. Snapshots are recorded automatically as you make significant edits.
            </div>

            <div
              v-for="h in notesStore.noteHistory"
              :key="h.id"
              @click="selectedHistory = h"
              class="p-3.5 cursor-pointer transition text-xs"
              :class="selectedHistory?.id === h.id ? 'bg-indigo-50/70 border-l-4 border-indigo-600 font-semibold text-indigo-950' : 'hover:bg-stone-100 text-stone-700'"
            >
              <div class="flex items-center gap-1.5 text-stone-500 text-[10px] mb-1">
                <Clock class="w-3 h-3 text-stone-400" />
                <span>{{ new Date(h.created_at).toLocaleString() }}</span>
              </div>
              <div class="truncate text-stone-800">{{ h.title || 'Untitled Note' }}</div>
              <div class="text-[10px] text-stone-400 mt-1 font-mono">
                {{ h.content.length }} characters
              </div>
            </div>
          </div>
        </div>

        <!-- Snapshot Preview (Right) -->
        <div class="flex-1 flex flex-col bg-white overflow-hidden">
          <div v-if="selectedHistory" class="flex-1 flex flex-col h-full overflow-hidden">
            <!-- Header action bar -->
            <div class="px-6 py-3 border-b border-stone-100 flex items-center justify-between bg-stone-50/30 shrink-0">
              <div class="text-xs text-stone-600">
                <span>Previewing snapshot from </span>
                <span class="font-bold text-stone-900">{{ new Date(selectedHistory.created_at).toLocaleString() }}</span>
              </div>

              <button
                @click="restoreSelected"
                class="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-sm transition"
              >
                <RotateCcw class="w-3.5 h-3.5" />
                <span>Restore this Version</span>
              </button>
            </div>

            <!-- Content preview -->
            <div class="flex-1 overflow-y-auto p-6">
              <h2 class="text-xl font-bold text-stone-900 mb-4">{{ selectedHistory.title }}</h2>
              <div class="font-mono text-xs text-stone-800 whitespace-pre-wrap leading-relaxed bg-stone-50 p-4 rounded-lg border border-stone-200">
                {{ selectedHistory.content }}
              </div>
            </div>
          </div>

          <!-- Empty selection state -->
          <div v-else class="flex-1 flex items-center justify-center p-8 text-center text-xs text-stone-400">
            Select a snapshot on the left to preview its content.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useNotesStore } from '../stores/notes'
import { History, X, Clock, RotateCcw } from 'lucide-vue-next'

const notesStore = useNotesStore()
const selectedHistory = ref(null)

watch(() => notesStore.noteHistory, (list) => {
  if (list && list.length > 0) {
    selectedHistory.value = list[0]
  } else {
    selectedHistory.value = null
  }
}, { immediate: true })

async function restoreSelected() {
  if (!selectedHistory.value || !notesStore.activeNote) return
  if (confirm(`Restore note to snapshot from ${new Date(selectedHistory.value.created_at).toLocaleString()}?`)) {
    await notesStore.restoreHistory(notesStore.activeNote.id, selectedHistory.value.id)
  }
}
</script>
