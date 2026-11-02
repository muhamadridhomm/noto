<template>
  <div
    v-if="isOpen"
    class="fixed z-50 w-72 bg-white rounded-xl shadow-2xl border border-stone-200 overflow-hidden text-xs select-none animate-in fade-in zoom-in-95 duration-100"
    :style="{ top: `${position.top}px`, left: `${position.left}px` }"
  >
    <!-- Search / Filter header -->
    <div class="px-3 py-2 bg-stone-50 border-b border-stone-100 flex items-center justify-between text-stone-400">
      <span class="font-bold uppercase tracking-wider text-[10px]">Insert Block</span>
      <span class="text-[10px] font-mono">↑↓ to navigate • ↵ to insert</span>
    </div>

    <!-- Commands List -->
    <div class="max-h-64 overflow-y-auto p-1.5 space-y-0.5">
      <div v-if="filteredCommands.length === 0" class="py-4 text-center text-stone-400">
        No matching commands
      </div>

      <button
        v-for="(cmd, idx) in filteredCommands"
        :key="cmd.id"
        @click="executeCommand(cmd)"
        @mouseenter="selectedIndex = idx"
        class="w-full px-2.5 py-1.5 rounded-lg flex items-center gap-2.5 text-left transition"
        :class="selectedIndex === idx ? 'bg-amber-50 text-amber-950 font-semibold' : 'text-stone-700 hover:bg-stone-100'"
      >
        <div
          class="p-1 rounded-md shrink-0"
          :class="selectedIndex === idx ? 'bg-amber-200 text-amber-900' : 'bg-stone-100 text-stone-600'"
        >
          <component :is="cmd.icon" class="w-3.5 h-3.5" />
        </div>
        <div class="flex-1 truncate">
          <div class="text-xs">{{ cmd.title }}</div>
          <div class="text-[10px] font-normal text-stone-400 truncate">{{ cmd.desc }}</div>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import {
  CheckSquare, Lightbulb, Heading1, Heading2, Heading3, Sparkles,
  LayoutTemplate, Code, List, Quote, Wand2
} from 'lucide-vue-next'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  query: {
    type: String,
    default: ''
  },
  position: {
    type: Object,
    default: () => ({ top: 120, left: 100 })
  }
})

const emit = defineEmits(['close', 'select'])

const selectedIndex = ref(0)

const commands = [
  {
    id: 'checklist',
    title: 'Tasks & Checklist',
    desc: 'Interactive ClickUp table & Kanban board',
    icon: CheckSquare,
    keywords: 'task checklist clickup todo table kanban'
  },
  {
    id: 'callout',
    title: 'Callout Box',
    desc: 'Highlighted note or key takeaway box',
    icon: Lightbulb,
    keywords: 'callout box tip warning note info highlight'
  },
  {
    id: 'extract_tasks',
    title: 'AI: Extract Action Items',
    desc: 'Extract tasks from meeting discussion',
    icon: Wand2,
    keywords: 'extract ai action items meeting tasks'
  },
  {
    id: 'ai_copilot',
    title: 'Ask Noto AI',
    desc: 'Draft or improve note with AI',
    icon: Sparkles,
    keywords: 'ai assistant gemini ollama prompt'
  },
  {
    id: 'template',
    title: 'Use Template',
    desc: 'Insert meeting, sprint, or standup template',
    icon: LayoutTemplate,
    keywords: 'template meeting sprint standup bug'
  },
  {
    id: 'h1',
    title: 'Heading 1',
    desc: 'Large section title',
    icon: Heading1,
    keywords: 'h1 header heading title large'
  },
  {
    id: 'h2',
    title: 'Heading 2',
    desc: 'Medium section subtitle',
    icon: Heading2,
    keywords: 'h2 header subtitle medium'
  },
  {
    id: 'h3',
    title: 'Heading 3',
    desc: 'Small detail header',
    icon: Heading3,
    keywords: 'h3 header small'
  },
  {
    id: 'code',
    title: 'Code Block',
    desc: 'Syntax highlighted code block',
    icon: Code,
    keywords: 'code block snippet javascript python'
  },
  {
    id: 'list',
    title: 'Bulleted List',
    desc: 'Standard bulleted item list',
    icon: List,
    keywords: 'list bullet points'
  },
  {
    id: 'quote',
    title: 'Quote',
    desc: 'Blockquote styling',
    icon: Quote,
    keywords: 'quote blockquote'
  }
]

const filteredCommands = computed(() => {
  if (!props.query) return commands
  const q = props.query.toLowerCase().replace('/', '')
  return commands.filter(c =>
    c.title.toLowerCase().includes(q) ||
    c.desc.toLowerCase().includes(q) ||
    c.keywords.includes(q)
  )
})

watch(() => filteredCommands.value.length, () => {
  selectedIndex.value = 0
})

function executeCommand(cmd) {
  emit('select', cmd)
  emit('close')
}

function handleKeydown(e) {
  if (!props.isOpen) return

  if (e.key === 'ArrowDown') {
    e.preventDefault()
    if (filteredCommands.value.length > 0) {
      selectedIndex.value = (selectedIndex.value + 1) % filteredCommands.value.length
    }
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    if (filteredCommands.value.length > 0) {
      selectedIndex.value = (selectedIndex.value - 1 + filteredCommands.value.length) % filteredCommands.value.length
    }
  } else if (e.key === 'Enter') {
    e.preventDefault()
    if (filteredCommands.value[selectedIndex.value]) {
      executeCommand(filteredCommands.value[selectedIndex.value])
    }
  } else if (e.key === 'Escape') {
    e.preventDefault()
    emit('close')
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>
