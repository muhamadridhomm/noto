<template>
  <div
    v-if="aiStore.isSettingsOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-stone-900/30 backdrop-blur-xs select-none"
    @click.self="aiStore.isSettingsOpen = false"
  >
    <div class="w-full max-w-lg bg-white rounded-xl shadow-2xl overflow-hidden border border-stone-200 animate-in fade-in zoom-in-95 duration-100 flex flex-col">
      <!-- Modal Header -->
      <div class="px-6 py-4 border-b border-stone-200 flex items-center justify-between bg-stone-50/60">
        <div class="flex items-center gap-2">
          <Settings class="w-5 h-5 text-stone-600" />
          <h3 class="text-sm font-semibold text-stone-800">Noto Settings</h3>
        </div>
        <button
          @click="aiStore.isSettingsOpen = false"
          class="text-stone-400 hover:text-stone-700 p-1 rounded-md hover:bg-stone-200/60 transition"
        >
          <X class="w-4 h-4" />
        </button>
      </div>

      <!-- Settings Content -->
      <div class="p-6 space-y-5 text-xs text-stone-700">
        <!-- AI Provider Section -->
        <div>
          <h4 class="text-[11px] font-semibold text-stone-400 uppercase tracking-wider mb-2">AI Provider Configuration</h4>
          <div class="space-y-3 bg-stone-50 p-4 rounded-lg border border-stone-200">
            <!-- Active Provider Toggle -->
            <div>
              <label class="block font-medium text-stone-700 mb-1">Active Engine</label>
              <div class="flex gap-2">
                <button
                  @click="aiStore.activeProvider = 'gemini'"
                  :class="[
                    'flex-1 py-1.5 px-3 rounded-md border text-center transition font-medium',
                    aiStore.activeProvider === 'gemini'
                      ? 'bg-brand-50 border-brand-400 text-brand-800 shadow-2xs'
                      : 'bg-white border-stone-200 text-stone-600 hover:bg-stone-100'
                  ]"
                >
                  Google Gemini (Cloud)
                </button>
                <button
                  @click="aiStore.activeProvider = 'ollama'"
                  :class="[
                    'flex-1 py-1.5 px-3 rounded-md border text-center transition font-medium',
                    aiStore.activeProvider === 'ollama'
                      ? 'bg-brand-50 border-brand-400 text-brand-800 shadow-2xs'
                      : 'bg-white border-stone-200 text-stone-600 hover:bg-stone-100'
                  ]"
                >
                  Ollama (Local Offline)
                </button>
              </div>
            </div>

            <!-- Gemini Status -->
            <div class="border-t border-stone-200/70 pt-2.5 space-y-1">
              <div class="flex items-center justify-between">
                <span class="font-medium text-stone-700">Gemini API Status:</span>
                <span
                  class="px-2 py-0.5 rounded-full text-[10px] font-mono font-medium"
                  :class="aiStore.aiStatus.gemini_configured ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'"
                >
                  {{ aiStore.aiStatus.gemini_configured ? 'Key Configured' : 'Missing Key in .env' }}
                </span>
              </div>
              <p class="text-[11px] text-stone-500">
                Model: <code class="bg-stone-200 px-1 py-0.5 rounded font-mono">{{ aiStore.aiStatus.gemini_model }}</code>
              </p>
              <p v-if="!aiStore.aiStatus.gemini_configured" class="text-[11px] text-stone-500 italic">
                To enable Gemini, add your <code class="font-mono">GEMINI_API_KEY</code> to <code class="font-mono">backend/.env</code>.
              </p>
            </div>

            <!-- Ollama Status -->
            <div class="border-t border-stone-200/70 pt-2.5 space-y-1">
              <div class="flex items-center justify-between">
                <span class="font-medium text-stone-700">Local Ollama Status:</span>
                <span
                  class="px-2 py-0.5 rounded-full text-[10px] font-mono font-medium"
                  :class="aiStore.aiStatus.ollama_available ? 'bg-emerald-100 text-emerald-800' : 'bg-stone-200 text-stone-600'"
                >
                  {{ aiStore.aiStatus.ollama_available ? 'Connected' : 'Offline / Unreachable' }}
                </span>
              </div>
              <p class="text-[11px] text-stone-500">
                URL: <code class="bg-stone-200 px-1 py-0.5 rounded font-mono">{{ aiStore.aiStatus.ollama_url }}</code>
              </p>
              <p class="text-[11px] text-stone-500">
                Model: <code class="bg-stone-200 px-1 py-0.5 rounded font-mono">{{ aiStore.aiStatus.ollama_model }}</code>
              </p>
              <button
                @click="aiStore.fetchAIStatus"
                class="mt-1 text-[11px] text-brand-600 hover:underline flex items-center gap-1"
              >
                <span>Check connection</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Export Data Section -->
        <div>
          <h4 class="text-[11px] font-semibold text-stone-400 uppercase tracking-wider mb-2">Data & Privacy</h4>
          <p class="text-stone-500 mb-3 leading-relaxed">
            All notes, folders, and search indexes are stored locally in <code class="font-mono bg-stone-100 px-1 py-0.5 rounded">data/noto.db</code>. No note contents are ever shared or analyzed without your direct prompt.
          </p>
          <button
            @click="exportMarkdownBundle"
            class="flex items-center gap-2 px-3 py-2 bg-stone-100 hover:bg-stone-200 text-stone-800 rounded-md font-medium transition"
          >
            <Download class="w-4 h-4 text-stone-600" />
            <span>Export Notes as JSON Backup</span>
          </button>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="px-6 py-3 border-t border-stone-200 bg-stone-50 flex justify-end">
        <button
          @click="aiStore.isSettingsOpen = false"
          class="px-4 py-1.5 bg-stone-900 hover:bg-stone-800 text-white rounded-md text-xs font-medium transition"
        >
          Close
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAIStore } from '../stores/ai'
import { useNotesStore } from '../stores/notes'
import { Settings, X, Download } from 'lucide-vue-next'

const aiStore = useAIStore()
const notesStore = useNotesStore()

function exportMarkdownBundle() {
  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(notesStore.notes, null, 2))
  const downloadAnchor = document.createElement('a')
  downloadAnchor.setAttribute("href", dataStr)
  downloadAnchor.setAttribute("download", `noto_backup_${new Date().toISOString().slice(0, 10)}.json`)
  document.body.appendChild(downloadAnchor)
  downloadAnchor.click()
  downloadAnchor.remove()
}
</script>
