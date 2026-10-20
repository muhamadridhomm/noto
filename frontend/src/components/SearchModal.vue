<template>
  <div
    v-if="aiStore.isSearchOpen"
    class="fixed inset-0 z-50 flex items-start justify-center pt-24 p-4 bg-stone-900/30 backdrop-blur-xs select-none"
    @click.self="closeSearch"
  >
    <div class="w-full max-w-xl bg-white rounded-xl shadow-2xl overflow-hidden border border-stone-200 animate-in fade-in zoom-in-95 duration-100 flex flex-col max-h-[70vh]">
      <!-- Search Input Bar -->
      <div class="p-3 border-b border-stone-200 flex items-center gap-2.5">
        <Search class="w-4 h-4 text-stone-400 shrink-0 ml-1" />
        <input
          v-model="query"
          ref="searchInput"
          @input="onSearchInput"
          @keydown.down.prevent="navigateResults(1)"
          @keydown.up.prevent="navigateResults(-1)"
          @keydown.enter.prevent="selectHighlighted"
          @keydown.esc="closeSearch"
          type="text"
          placeholder="Search notes by title or content (SQLite FTS5)..."
          class="w-full text-sm text-stone-900 placeholder-stone-400 border-none bg-transparent focus:outline-none focus:ring-0"
        />
        <span class="text-[10px] font-mono text-stone-400 bg-stone-100 px-1.5 py-0.5 rounded border border-stone-200 shrink-0">
          ESC
        </span>
      </div>

      <!-- Search Results Area -->
      <div class="flex-1 overflow-y-auto divide-y divide-stone-100 p-1">
        <div v-if="isSearching" class="p-6 text-center text-xs text-stone-400 flex items-center justify-center gap-2">
          <Loader2 class="w-4 h-4 animate-spin text-brand-600" />
          <span>Searching local database...</span>
        </div>

        <div v-else-if="query && results.length === 0" class="p-8 text-center text-xs text-stone-400">
          No matching notes found for "<span class="font-medium text-stone-600">{{ query }}</span>"
        </div>

        <div v-else-if="!query" class="p-6 text-center text-xs text-stone-400">
          Type to search across all your local notes instantly.
        </div>

        <div
          v-for="(item, idx) in results"
          :key="item.id"
          @click="selectResult(item)"
          class="p-3 rounded-lg cursor-pointer transition text-left"
          :class="highlightedIndex === idx ? 'bg-brand-50/70 text-brand-900' : 'hover:bg-stone-50 text-stone-800'"
        >
          <div class="flex items-center justify-between mb-1">
            <h4 class="text-sm font-semibold truncate">{{ item.title || 'Untitled Note' }}</h4>
            <span class="text-[10px] font-mono bg-stone-100 text-stone-600 px-1.5 py-0.5 rounded">
              📁 {{ item.folder_name }}
            </span>
          </div>

          <div
            v-if="item.snippet"
            class="text-xs text-stone-500 line-clamp-2 leading-relaxed"
            v-html="item.snippet"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { useAIStore } from '../stores/ai'
import { useNotesStore } from '../stores/notes'
import { Search, Loader2 } from 'lucide-vue-next'

const aiStore = useAIStore()
const notesStore = useNotesStore()

const query = ref('')
const results = ref([])
const isSearching = ref(false)
const highlightedIndex = ref(0)
const searchInput = ref(null)
let debounceTimeout = null

watch(() => aiStore.isSearchOpen, (open) => {
  if (open) {
    query.value = ''
    results.value = []
    highlightedIndex.value = 0
    nextTick(() => {
      if (searchInput.value) searchInput.value.focus()
    })
  }
})

function closeSearch() {
  aiStore.isSearchOpen = false
}

function onSearchInput() {
  highlightedIndex.value = 0
  if (debounceTimeout) clearTimeout(debounceTimeout)
  if (!query.value.trim()) {
    results.value = []
    return
  }

  debounceTimeout = setTimeout(async () => {
    isSearching.value = true
    try {
      const res = await fetch(`/api/search?q=${encodeURIComponent(query.value.trim())}`)
      if (res.ok) {
        results.value = await res.json()
      }
    } catch (e) {
      console.error('Search error:', e)
    } finally {
      isSearching.value = false
    }
  }, 200)
}

function navigateResults(delta) {
  if (results.value.length === 0) return
  highlightedIndex.value = (highlightedIndex.value + delta + results.value.length) % results.value.length
}

function selectHighlighted() {
  if (results.value.length > 0 && results.value[highlightedIndex.value]) {
    selectResult(results.value[highlightedIndex.value])
  }
}

async function selectResult(item) {
  await notesStore.selectNote(item.id)
  closeSearch()
}
</script>
