<template>
  <!-- Slide-out Drawer Overlay & Container -->
  <div
    v-if="aiStore.isDrawerOpen"
    class="fixed inset-0 z-40 flex justify-end bg-stone-900/20 backdrop-blur-xs transition-opacity"
    @click.self="aiStore.closeDrawer"
  >
    <div class="w-full max-w-md bg-white h-full shadow-2xl flex flex-col border-l border-stone-200 select-none animate-in slide-in-from-right duration-200">
      <!-- Drawer Header -->
      <div class="p-4 border-b border-stone-200/80 flex items-center justify-between bg-stone-50/70">
        <div class="flex items-center gap-2">
          <div class="p-1.5 rounded-lg bg-brand-100 text-brand-700">
            <Sparkles class="w-4 h-4" />
          </div>
          <div>
            <h3 class="text-sm font-semibold text-stone-800">Noto AI Assistant</h3>
            <p class="text-[11px] text-stone-500">Draft or improve notes with human review</p>
          </div>
        </div>

        <button
          @click="aiStore.closeDrawer"
          class="text-stone-400 hover:text-stone-700 p-1 rounded-md hover:bg-stone-200/60 transition"
        >
          <X class="w-4 h-4" />
        </button>
      </div>

      <!-- Drawer Body -->
      <div class="flex-1 overflow-y-auto p-4 space-y-4">
        <!-- Mode Tabs -->
        <div>
          <label class="block text-[11px] font-semibold text-stone-400 uppercase tracking-wider mb-1.5">Action Mode</label>
          <div class="grid grid-cols-2 gap-1.5 p-1 bg-stone-100 rounded-lg text-xs font-medium text-stone-600">
            <button
              @click="aiStore.mode = 'new_note'"
              :class="[
                'py-1.5 px-2 rounded-md transition text-center flex items-center justify-center gap-1.5',
                aiStore.mode === 'new_note' ? 'bg-white text-stone-900 shadow-xs font-semibold' : 'hover:text-stone-900'
              ]"
            >
              <FilePlus class="w-3.5 h-3.5 text-brand-600" />
              <span>Draft New Note</span>
            </button>
            <button
              @click="aiStore.openDrawer('tidy_note')"
              :class="[
                'py-1.5 px-2 rounded-md transition text-center flex items-center justify-center gap-1.5',
                aiStore.mode === 'tidy_note' ? 'bg-white text-stone-900 shadow-xs font-semibold' : 'hover:text-stone-900'
              ]"
            >
              <Wand2 class="w-3.5 h-3.5 text-indigo-600" />
              <span>Tidy Active Note</span>
            </button>
          </div>
        </div>

        <!-- Tone Options -->
        <div>
          <label class="block text-[11px] font-semibold text-stone-400 uppercase tracking-wider mb-1.5">Tone & Style</label>
          <div class="flex flex-wrap gap-1.5">
            <button
              v-for="t in ['balanced', 'concise', 'professional', 'bulleted']"
              :key="t"
              @click="aiStore.tone = t"
              :class="[
                'text-xs px-2.5 py-1 rounded-full border transition capitalize',
                aiStore.tone === t 
                  ? 'bg-brand-50 border-brand-300 text-brand-700 font-medium' 
                  : 'bg-white border-stone-200 text-stone-600 hover:border-stone-300'
              ]"
            >
              {{ t }}
            </button>
          </div>
        </div>

        <!-- AI Provider Picker -->
        <div>
          <div class="flex items-center justify-between mb-1.5">
            <label class="block text-[11px] font-semibold text-stone-400 uppercase tracking-wider">AI Engine</label>
            <button
              @click="aiStore.isSettingsOpen = true"
              class="text-[11px] text-brand-600 hover:underline"
            >
              Settings
            </button>
          </div>
          <div class="flex gap-2">
            <button
              @click="aiStore.activeProvider = 'gemini'"
              :class="[
                'flex-1 flex items-center justify-center gap-1.5 py-1.5 px-2 rounded-lg border text-xs transition',
                aiStore.activeProvider === 'gemini'
                  ? 'bg-brand-50 border-brand-400 text-brand-800 font-medium'
                  : 'border-stone-200 text-stone-600 hover:bg-stone-50'
              ]"
            >
              <span class="w-2 h-2 rounded-full" :class="aiStore.aiStatus.gemini_configured ? 'bg-emerald-500' : 'bg-amber-400'"></span>
              <span>Gemini Cloud</span>
            </button>

            <button
              @click="aiStore.activeProvider = 'ollama'"
              :class="[
                'flex-1 flex items-center justify-center gap-1.5 py-1.5 px-2 rounded-lg border text-xs transition',
                aiStore.activeProvider === 'ollama'
                  ? 'bg-brand-50 border-brand-400 text-brand-800 font-medium'
                  : 'border-stone-200 text-stone-600 hover:bg-stone-50'
              ]"
            >
              <span class="w-2 h-2 rounded-full" :class="aiStore.aiStatus.ollama_available ? 'bg-emerald-500' : 'bg-stone-300'"></span>
              <span>Ollama Offline</span>
            </button>
          </div>
        </div>

        <!-- Context Preview (if in tidy mode) -->
        <div v-if="aiStore.mode === 'tidy_note' && aiStore.originalText" class="p-2.5 rounded-lg bg-stone-50 border border-stone-200 text-xs">
          <div class="flex items-center justify-between text-stone-500 mb-1">
            <span class="font-medium text-[11px] uppercase">Working with text from:</span>
            <span class="truncate max-w-[150px] font-mono">{{ notesStore.activeNote?.title || 'Current Note' }}</span>
          </div>
          <p class="text-stone-600 line-clamp-3 italic text-[11px] leading-relaxed">
            "{{ aiStore.originalText.slice(0, 160) }}..."
          </p>
        </div>

        <!-- Prompt Textarea -->
        <div>
          <label class="block text-[11px] font-semibold text-stone-400 uppercase tracking-wider mb-1.5">
            {{ aiStore.mode === 'new_note' ? 'What note do you want to create?' : 'How should AI improve it?' }}
          </label>
          <textarea
            v-model="aiStore.prompt"
            rows="4"
            @keydown.ctrl.enter="handleGenerate"
            placeholder="e.g. Draft a meeting note with Sarah covering Q3 targets, or Clean up grammar and format as bulleted checklist..."
            class="w-full text-xs p-3 bg-white border border-stone-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-brand-500 leading-relaxed placeholder-stone-400 resize-none"
          ></textarea>
        </div>

        <!-- Quick Idea Chips -->
        <div>
          <label class="block text-[11px] font-semibold text-stone-400 uppercase tracking-wider mb-1.5">Suggestions</label>
          <div class="flex flex-wrap gap-1">
            <button
              v-for="chip in currentSuggestions"
              :key="chip"
              @click="aiStore.prompt = chip"
              class="text-[11px] px-2 py-1 bg-stone-100 hover:bg-stone-200/80 text-stone-700 rounded-md transition text-left"
            >
              {{ chip }}
            </button>
          </div>
        </div>

        <!-- Error banner if any -->
        <div v-if="aiStore.generationError" class="p-2.5 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-700">
          {{ aiStore.generationError }}
        </div>
      </div>

      <!-- Drawer Footer Action -->
      <div class="p-4 border-t border-stone-200/80 bg-stone-50/70">
        <button
          @click="handleGenerate"
          :disabled="aiStore.isGenerating || !aiStore.prompt.trim()"
          class="w-full py-2.5 px-4 bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white rounded-lg text-xs font-semibold flex items-center justify-center gap-2 shadow-sm transition active:scale-[0.99]"
        >
          <Loader2 v-if="aiStore.isGenerating" class="w-4 h-4 animate-spin" />
          <Sparkles v-else class="w-4 h-4" />
          <span>{{ aiStore.isGenerating ? 'Drafting Note...' : 'Generate Draft' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAIStore } from '../stores/ai'
import { useNotesStore } from '../stores/notes'
import {
  Sparkles, X, FilePlus, Wand2, Loader2
} from 'lucide-vue-next'

const aiStore = useAIStore()
const notesStore = useNotesStore()

const currentSuggestions = computed(() => {
  if (aiStore.mode === 'tidy_note') {
    return [
      'Clean up formatting & fix spelling',
      'Format action items as checkboxes',
      'Turn into a concise executive summary',
      'Organize with clear headers and bullet points'
    ]
  }
  return [
    'Meeting notes with team on product launch',
    'Weekly project sprint priorities & tasks',
    'Brainstorming ideas for website redesign',
    'Research summary of modern web frameworks'
  ]
})

function handleGenerate() {
  aiStore.generateDraft()
}
</script>
