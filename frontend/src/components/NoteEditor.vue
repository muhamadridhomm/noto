<template>
  <div class="flex-1 flex flex-col h-full bg-white overflow-hidden">
    <!-- Empty State -->
    <div v-if="!notesStore.activeNote" class="flex-1 flex flex-col items-center justify-center p-8 text-center bg-stone-50/50">
      <div class="w-14 h-14 rounded-2xl bg-stone-100 flex items-center justify-center text-stone-400 mb-4 shadow-sm">
        <FileText class="w-7 h-7" />
      </div>
      <h3 class="text-base font-semibold text-stone-800 mb-1">Select or create a note</h3>
      <p class="text-xs text-stone-500 max-w-sm mb-6 leading-relaxed">
        Choose a note from the list, start a fresh one, or pick a template to get started.
      </p>
      <div class="flex items-center gap-3">
        <button
          @click="notesStore.createNote()"
          class="flex items-center gap-1.5 px-3.5 py-2 bg-stone-900 hover:bg-stone-800 text-white rounded-lg text-xs font-medium transition shadow-sm"
        >
          <Plus class="w-3.5 h-3.5" />
          <span>New Note</span>
        </button>
        <button
          @click="notesStore.isTemplatesOpen = true"
          class="flex items-center gap-1.5 px-3.5 py-2 bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-200 rounded-lg text-xs font-medium transition"
        >
          <LayoutTemplate class="w-3.5 h-3.5 text-amber-600" />
          <span>Use Template</span>
        </button>
        <button
          @click="aiStore.openDrawer('new_note')"
          class="flex items-center gap-1.5 px-3.5 py-2 bg-brand-50 hover:bg-brand-100 text-brand-700 border border-brand-200 rounded-lg text-xs font-medium transition"
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
          <!-- Checklist Visibility & Actions Group -->
          <div v-if="hasTasks" class="flex items-center bg-stone-100 p-0.5 rounded-md text-xs">
            <button
              @click="isChecklistVisible = !isChecklistVisible"
              class="flex items-center gap-1.5 px-2 py-0.5 rounded transition font-medium"
              :class="isChecklistVisible ? 'bg-emerald-50 text-emerald-800 shadow-2xs' : 'text-stone-500 hover:text-stone-900'"
              :title="isChecklistVisible ? 'Hide checklist panel (Focus mode)' : 'Show checklist panel'"
            >
              <CheckSquare class="w-3.5 h-3.5 text-emerald-600" />
              <span>Tasks ({{ completedTasksCount }}/{{ parsedTasks.length }})</span>
              <Eye v-if="isChecklistVisible" class="w-3 h-3 text-emerald-700 ml-0.5" />
              <EyeOff v-else class="w-3 h-3 text-stone-400 ml-0.5" />
            </button>

            <button
              v-if="isChecklistVisible"
              @click="toggleDockPosition"
              class="px-2 py-0.5 rounded transition text-stone-600 hover:text-stone-900 flex items-center gap-1 border-l border-stone-200/80 ml-0.5"
              :title="checklistDock === 'sidebar' ? 'Dock inline inside note' : 'Dock to right sidebar (Free up note space)'"
            >
              <Columns class="w-3.5 h-3.5 text-stone-500" />
              <span class="text-[11px]">{{ checklistDock === 'sidebar' ? 'Sidebar' : 'Inline' }}</span>
            </button>
          </div>

          <!-- If note has no checklist yet: Insert Checklist Button -->
          <button
            v-else
            @click="insertOrToggleChecklist"
            class="flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-md border border-stone-200 bg-stone-50 hover:bg-stone-100 text-stone-700 transition"
            title="Add interactive ClickUp checklist to this note (or type /task)"
          >
            <CheckSquare class="w-3.5 h-3.5 text-emerald-600" />
            <span>+ Checklist</span>
          </button>

          <!-- Combined Master Timeline Shortcut Button -->
          <button
            @click="openMasterTimeline"
            class="flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium text-brand-700 bg-brand-50 hover:bg-brand-100 border border-brand-200/80 rounded-md transition shadow-2xs"
            title="Buka Master Timeline & Roadmap (Semua Catatan)"
          >
            <CalendarDays class="w-3.5 h-3.5 text-brand-600" />
            <span class="hidden sm:inline">Timeline Hub</span>
          </button>

          <!-- AI: Extract Action Items to Tasks -->
          <button
            @click="handleExtractTasks"
            title="AI extracts action items from this note into ClickUp checklist"
            class="flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200/80 rounded-md transition"
          >
            <Wand2 class="w-3.5 h-3.5 text-emerald-600" />
            <span class="hidden sm:inline">Extract Tasks</span>
          </button>

          <!-- AI Tidy Action Button -->
          <button
            @click="handleAITidy"
            title="Ask AI to improve, tidy, or reformat this note"
            class="flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium text-brand-700 bg-brand-50 hover:bg-brand-100 border border-brand-200/80 rounded-md transition"
          >
            <Sparkles class="w-3.5 h-3.5 text-brand-600" />
            <span class="hidden sm:inline">Tidy</span>
          </button>

          <!-- Templates Gallery Button -->
          <button
            @click="notesStore.isTemplatesOpen = true"
            title="Template Gallery"
            class="p-1.5 rounded-md text-stone-500 hover:text-stone-800 hover:bg-stone-100 transition"
          >
            <LayoutTemplate class="w-4 h-4" />
          </button>

          <!-- Version History (Time Machine) Button -->
          <button
            @click="openHistoryModal"
            title="Version History & Snapshots"
            class="p-1.5 rounded-md text-stone-500 hover:text-stone-800 hover:bg-stone-100 transition"
          >
            <History class="w-4 h-4" />
          </button>

          <!-- Export to Markdown Button -->
          <button
            @click="downloadNoteMarkdown"
            title="Download as clean Markdown file (.md)"
            class="p-1.5 rounded-md text-stone-500 hover:text-stone-800 hover:bg-stone-100 transition"
          >
            <Download class="w-4 h-4" />
          </button>

          <!-- View Mode Toggle (Write / Split / Preview) -->
          <div class="flex items-center bg-stone-100 p-0.5 rounded-md text-xs text-stone-600">
            <button
              @click="viewMode = 'edit'"
              :class="['px-2.5 py-0.5 rounded transition', viewMode === 'edit' ? 'bg-white shadow-xs font-medium text-stone-900' : 'hover:text-stone-900']"
            >
              Write
            </button>
            <button
              @click="viewMode = 'split'"
              :class="['px-2.5 py-0.5 rounded transition', viewMode === 'split' ? 'bg-white shadow-xs font-medium text-stone-900' : 'hover:text-stone-900']"
            >
              Split
            </button>
            <button
              @click="viewMode = 'preview'"
              :class="['px-2.5 py-0.5 rounded transition', viewMode === 'preview' ? 'bg-white shadow-xs font-medium text-stone-900' : 'hover:text-stone-900']"
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

      <!-- Main Editor Workspace (with optional Resizable Right Sidebar for Checklist) -->
      <div class="flex-1 flex overflow-hidden relative">
        <!-- Notion-Style Slash Command Menu Floating Component -->
        <SlashMenu
          :is-open="isSlashOpen"
          :query="slashQuery"
          :position="slashPos"
          @close="isSlashOpen = false"
          @select="onSlashCommandSelect"
        />

        <!-- LEFT: Note Canvas Area -->
        <div class="flex-1 flex flex-col h-full overflow-hidden">
          <!-- Note Title Header -->
          <div class="px-8 pt-6 pb-2 shrink-0">
            <input
              v-model="notesStore.activeNote.title"
              @input="onTitleChange"
              type="text"
              placeholder="Untitled Note"
              class="w-full text-2xl font-bold text-stone-900 placeholder-stone-300 border-none bg-transparent focus:outline-none focus:ring-0 tracking-tight"
            />
          </div>

          <!-- Note Content Canvas -->
          <div class="flex-1 flex overflow-hidden px-8 pb-4">
            <!-- Mode 1: Write Mode -->
            <div
              v-show="viewMode === 'edit'"
              class="flex-1 h-full overflow-y-auto pr-2"
            >
              <!-- Case A: Checklist is docked to SIDEBAR, or HIDDEN, or note has no tasks -->
              <div
                v-if="checklistDock === 'sidebar' || !hasTasks || !isChecklistVisible"
                class="min-h-full flex flex-col pb-16"
              >
                <textarea
                  ref="cleanTextareaRef"
                  v-model="editorCleanText"
                  @input="e => { onCleanTextChange(); handleTextareaInput(e); adjustTextareaHeight(e.target) }"
                  @keydown.tab.prevent="insertTab"
                  placeholder="Type notes here... (Type '/' for slash commands like /task, /callout, /template)"
                  class="w-full min-h-[350px] resize-none overflow-hidden font-mono text-xs sm:text-sm text-stone-800 leading-relaxed bg-transparent border-none focus:outline-none focus:ring-0 placeholder-stone-300 block"
                ></textarea>
              </div>

              <!-- Case B: Checklist is docked INLINE in document flow -->
              <div v-else class="flex flex-col min-h-full pb-16">
                <!-- Text Before Checklist (Auto-expands smoothly with NO internal scrollbar) -->
                <textarea
                  ref="beforeTextareaRef"
                  v-model="splitData.before"
                  @input="e => { onSplitTextChange(); handleTextareaInput(e); adjustTextareaHeight(e.target) }"
                  @keydown.tab.prevent="insertTab"
                  placeholder="Notes, background, or context before tasks... (Type '/' for commands)"
                  class="w-full min-h-[44px] resize-none overflow-hidden font-mono text-xs sm:text-sm text-stone-800 leading-relaxed bg-transparent border-none focus:outline-none focus:ring-0 placeholder-stone-300 mb-2 block"
                ></textarea>

                <!-- Embedded Interactive ClickUp Checklist Table (natural document flow, like an embedded Word table) -->
                <div class="my-2 transition-all duration-200">
                  <ChecklistTable
                    :model-value="parsedTasks"
                    :initial-targets="parsedTargets"
                    :initial-groups="parsedGroups"
                    :dock-mode="'inline'"
                    :minimized="isChecklistMinimized"
                    removable
                    @toggle-minimize="isChecklistMinimized = !isChecklistMinimized"
                    @toggle-dock="setDockMode('sidebar')"
                    @remove="removeChecklist"
                    @change="onTasksChange"
                  />
                </div>

                <!-- Text After Checklist (Auto-expands smoothly with NO internal scrollbar) -->
                <textarea
                  ref="afterTextareaRef"
                  v-model="splitData.after"
                  @input="e => { onSplitTextChange(); handleTextareaInput(e); adjustTextareaHeight(e.target) }"
                  @keydown.tab.prevent="insertTab"
                  placeholder="Additional notes, decisions, or follow-ups after tasks... (Type '/' for commands)"
                  class="w-full min-h-[140px] resize-none overflow-hidden font-mono text-xs sm:text-sm text-stone-800 leading-relaxed bg-transparent border-none focus:outline-none focus:ring-0 placeholder-stone-300 mt-2 block"
                ></textarea>
              </div>
            </div>

            <!-- Mode 2: Split Mode (Raw markdown on left, rendered on right) -->
            <div
              v-show="viewMode === 'split'"
              class="flex-1 flex h-full overflow-hidden"
            >
              <!-- Raw Editor -->
              <div class="flex-1 flex flex-col h-full pr-4 border-r border-stone-200/60">
                <textarea
                  v-model="notesStore.activeNote.content"
                  @input="e => { onRawContentChange(); handleTextareaInput(e) }"
                  @keydown.tab.prevent="insertTab"
                  placeholder="Write note markdown..."
                  class="w-full h-full resize-none font-mono text-xs sm:text-sm text-stone-800 leading-relaxed bg-transparent border-none focus:outline-none focus:ring-0 placeholder-stone-300"
                ></textarea>
              </div>

              <!-- Rendered Preview -->
              <div class="flex-1 h-full overflow-y-auto pl-4">
                <div v-if="renderedMarkdownBefore" class="markdown-body" v-html="renderedMarkdownBefore"></div>
                <div v-if="hasTasks && checklistDock === 'inline'" class="my-3">
                  <ChecklistTable
                    :model-value="parsedTasks"
                    :initial-targets="parsedTargets"
                    :initial-groups="parsedGroups"
                    :dock-mode="'inline'"
                    :minimized="isChecklistMinimized"
                    @toggle-minimize="isChecklistMinimized = !isChecklistMinimized"
                    @toggle-dock="setDockMode('sidebar')"
                    @change="onTasksChange"
                  />
                </div>
                <div v-if="renderedMarkdownAfter" class="markdown-body" v-html="renderedMarkdownAfter"></div>
              </div>
            </div>

            <!-- Mode 3: Preview Mode -->
            <div
              v-show="viewMode === 'preview'"
              class="flex-1 h-full overflow-y-auto"
            >
              <div v-if="renderedMarkdownBefore" class="markdown-body" v-html="renderedMarkdownBefore"></div>
              <div v-if="hasTasks && checklistDock === 'inline'" class="my-4">
                <ChecklistTable
                  :model-value="parsedTasks"
                  :initial-targets="parsedTargets"
                  :initial-groups="parsedGroups"
                  :dock-mode="'inline'"
                  :minimized="isChecklistMinimized"
                  @toggle-minimize="isChecklistMinimized = !isChecklistMinimized"
                  @toggle-dock="setDockMode('sidebar')"
                  @change="onTasksChange"
                />
              </div>
              <div v-if="renderedMarkdownAfter" class="markdown-body" v-html="renderedMarkdownAfter"></div>
            </div>
          </div>

          <!-- Bottom Stats Bar -->
          <div class="h-7 border-t border-stone-100 px-8 flex items-center justify-between text-[11px] text-stone-400 font-mono shrink-0">
            <div class="flex items-center gap-4">
              <span>{{ wordCount }} words</span>
              <span>{{ charCount }} characters</span>
              <span v-if="hasTasks" class="text-emerald-700 font-medium flex items-center gap-1">
                <CheckSquare class="w-3.5 h-3.5" />
                <span>{{ completedTasksCount }}/{{ parsedTasks.length }} Tasks ({{ checklistDock }})</span>
              </span>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-[10px] text-stone-400 bg-stone-100 px-2 py-0.5 rounded">
                Type '/' for quick menu
              </span>
              <span>Markdown + ClickUp Tasks</span>
            </div>
          </div>
        </div>

        <!-- RESIZABLE DRAG HANDLE DIVIDER (When docked to sidebar & visible) -->
        <div
          v-if="hasTasks && checklistDock === 'sidebar' && isChecklistVisible"
          @mousedown="startResize"
          class="w-1.5 hover:w-2 bg-stone-200/80 hover:bg-brand-500 cursor-col-resize transition-all select-none shrink-0 relative flex items-center justify-center z-10"
          :class="{ 'bg-brand-500 w-2': isResizing }"
          title="Drag left/right to resize tasks panel"
        >
          <div class="w-0.5 h-8 bg-stone-400 rounded-full"></div>
        </div>

        <!-- RIGHT: Dedicated Checklist Sidebar Panel (When docked to sidebar & visible) -->
        <aside
          v-if="hasTasks && checklistDock === 'sidebar' && isChecklistVisible"
          :style="{ width: `${sidebarWidth}px` }"
          class="h-full bg-stone-50/70 border-l border-stone-200/80 flex flex-col overflow-hidden shrink-0 shadow-xs"
        >
          <!-- Sidebar Header: Actions to dock inline, minimize, or hide -->
          <div class="px-4 py-3 border-b border-stone-200/80 bg-white flex items-center justify-between shrink-0">
            <div class="flex items-center gap-2">
              <div class="p-1 rounded-md bg-brand-100 text-brand-700">
                <CheckSquare class="w-4 h-4" />
              </div>
              <div>
                <h3 class="text-xs font-bold text-stone-800 uppercase tracking-wider">Tasks & Checklist</h3>
                <p class="text-[10px] text-stone-500">{{ completedTasksCount }} of {{ parsedTasks.length }} completed</p>
              </div>
            </div>

            <div class="flex items-center gap-1">
              <button
                @click="setDockMode('inline')"
                title="Dock checklist inline inside note"
                class="p-1 text-stone-400 hover:text-stone-800 hover:bg-stone-100 rounded-md transition"
              >
                <ChevronDown class="w-4 h-4" />
              </button>

              <button
                @click="isChecklistVisible = false"
                title="Hide checklist panel (Click Tasks in toolbar to reopen)"
                class="p-1 text-stone-400 hover:text-stone-800 hover:bg-stone-100 rounded-md transition"
              >
                <EyeOff class="w-4 h-4" />
              </button>
            </div>
          </div>

          <!-- Sidebar Checklist Table Body -->
          <div class="flex-1 overflow-y-auto p-3">
            <ChecklistTable
              :model-value="parsedTasks"
              :initial-targets="parsedTargets"
              :initial-groups="parsedGroups"
              :dock-mode="'sidebar'"
              :minimized="isChecklistMinimized"
              removable
              @toggle-minimize="isChecklistMinimized = !isChecklistMinimized"
              @toggle-dock="setDockMode('inline')"
              @remove="removeChecklist"
              @change="onTasksChange"
            />
          </div>
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useNotesStore } from '../stores/notes'
import { useAIStore } from '../stores/ai'
import { marked } from 'marked'
import ChecklistTable from './ChecklistTable.vue'
import SlashMenu from './SlashMenu.vue'
import {
  FileText, Plus, Sparkles, Folder, Pin, CheckSquare, Eye, EyeOff, Columns,
  ChevronDown, LayoutTemplate, History, Download, Wand2, CalendarDays
} from 'lucide-vue-next'

const notesStore = useNotesStore()
const aiStore = useAIStore()
const viewMode = ref('edit')

function openMasterTimeline() {
  notesStore.fetchAllTasks()
  notesStore.isMasterTasksOpen = true
}

const TASKS_REGEX = /```tasks\s*([\s\S]*?)\s*```/

// Dock, Minimize, and Resizing State
const checklistDock = ref(localStorage.getItem('noto_checklist_dock') || 'sidebar')
const isChecklistVisible = ref(true)
const isChecklistMinimized = ref(false)
const sidebarWidth = ref(Number(localStorage.getItem('noto_checklist_sidebar_width')) || 380)
const isResizing = ref(false)

// Template Refs for Auto-Growing Textareas (single page Word/Notion flow)
const beforeTextareaRef = ref(null)
const afterTextareaRef = ref(null)
const cleanTextareaRef = ref(null)

// Auto-adjust height to prevent internal scrollbars and squeezing
function adjustTextareaHeight(el) {
  if (!el) return
  el.style.height = 'auto'
  el.style.height = `${Math.max(el.scrollHeight, 40)}px`
}

function autoResizeAll() {
  nextTick(() => {
    if (beforeTextareaRef.value) adjustTextareaHeight(beforeTextareaRef.value)
    if (afterTextareaRef.value) adjustTextareaHeight(afterTextareaRef.value)
    if (cleanTextareaRef.value) adjustTextareaHeight(cleanTextareaRef.value)
    requestAnimationFrame(() => {
      if (beforeTextareaRef.value) adjustTextareaHeight(beforeTextareaRef.value)
      if (afterTextareaRef.value) adjustTextareaHeight(afterTextareaRef.value)
      if (cleanTextareaRef.value) adjustTextareaHeight(cleanTextareaRef.value)
    })
  })
}

// Slash Command Menu State
const isSlashOpen = ref(false)
const slashQuery = ref('')
const slashPos = ref({ top: 120, left: 120 })
let activeTextareaRef = null

const splitData = ref({ before: '', after: '' })
const editorCleanText = ref('')

watch(() => notesStore.activeNote?.content, (content) => {
  parseContentSplit(content || '')
  syncCleanText(content || '')
  autoResizeAll()
}, { immediate: true })

watch(() => notesStore.activeNote?.id, () => {
  autoResizeAll()
})

watch(checklistDock, () => {
  autoResizeAll()
})

watch(viewMode, (mode) => {
  if (mode === 'edit') {
    autoResizeAll()
  }
})

onMounted(() => {
  autoResizeAll()
})

function syncCleanText(content) {
  editorCleanText.value = content.replace(TASKS_REGEX, '').trim()
}

function parseContentSplit(content) {
  const match = content.match(TASKS_REGEX)
  if (match) {
    const idx = content.indexOf(match[0])
    splitData.value.before = content.slice(0, idx)
    splitData.value.after = content.slice(idx + match[0].length)
  } else {
    splitData.value.before = content
    splitData.value.after = ''
  }
}

const parsedData = computed(() => {
  const content = notesStore.activeNote?.content || ''
  const match = content.match(TASKS_REGEX)
  if (match) {
    try {
      const data = JSON.parse(match[1])
      if (Array.isArray(data)) {
        return { tasks: data, targets: [], groups: [] }
      } else if (typeof data === 'object' && data !== null) {
        return {
          tasks: Array.isArray(data.tasks) ? data.tasks : [],
          targets: Array.isArray(data.targets) ? data.targets : [],
          groups: Array.isArray(data.groups) ? data.groups : []
        }
      }
    } catch (e) {
      console.warn('Failed to parse tasks JSON', e)
    }
  }
  return { tasks: [], targets: [], groups: [] }
})

const parsedTasks = computed(() => parsedData.value.tasks)
const parsedTargets = computed(() => parsedData.value.targets)
const parsedGroups = computed(() => parsedData.value.groups)

const hasTasks = computed(() => {
  return TASKS_REGEX.test(notesStore.activeNote?.content || '')
})

const completedTasksCount = computed(() => {
  return parsedTasks.value.filter(t => t.done).length
})

const wordCount = computed(() => {
  if (!notesStore.activeNote || !notesStore.activeNote.content) return 0
  return notesStore.activeNote.content.trim().split(/\s+/).filter(Boolean).length
})

const charCount = computed(() => {
  if (!notesStore.activeNote || !notesStore.activeNote.content) return 0
  return notesStore.activeNote.content.length
})

const renderedMarkdownBefore = computed(() => {
  if (checklistDock.value === 'sidebar') {
    const text = editorCleanText.value.trim()
    if (!text) return ''
    try {
      return marked.parse(text)
    } catch (e) {
      return `<pre>${text}</pre>`
    }
  }

  const before = splitData.value.before.trim()
  if (!before) return ''
  try {
    return marked.parse(before)
  } catch (e) {
    return `<pre>${before}</pre>`
  }
})

const renderedMarkdownAfter = computed(() => {
  if (checklistDock.value === 'sidebar') return ''
  const after = splitData.value.after.trim()
  if (!after) return ''
  try {
    return marked.parse(after)
  } catch (e) {
    return `<pre>${after}</pre>`
  }
})

function setDockMode(mode) {
  checklistDock.value = mode
  localStorage.setItem('noto_checklist_dock', mode)
}

function toggleDockPosition() {
  const next = checklistDock.value === 'sidebar' ? 'inline' : 'sidebar'
  setDockMode(next)
}

function onTitleChange() {
  notesStore.queueSaveNote()
}

function onCleanTextChange() {
  if (!notesStore.activeNote) return
  if (hasTasks.value) {
    const jsonStr = JSON.stringify(parsedTasks.value, null, 2)
    const taskBlock = `\`\`\`tasks\n${jsonStr}\n\`\`\``
    notesStore.activeNote.content = editorCleanText.value.trim()
      ? `${editorCleanText.value.trim()}\n\n${taskBlock}\n`
      : `${taskBlock}\n`
  } else {
    notesStore.activeNote.content = editorCleanText.value
  }
  parseContentSplit(notesStore.activeNote.content)
  notesStore.queueSaveNote()
}

function onSplitTextChange() {
  if (!notesStore.activeNote) return
  if (hasTasks.value) {
    const jsonStr = JSON.stringify(parsedTasks.value, null, 2)
    const taskBlock = `\`\`\`tasks\n${jsonStr}\n\`\`\``
    notesStore.activeNote.content = `${splitData.value.before}${taskBlock}${splitData.value.after}`
  } else {
    notesStore.activeNote.content = splitData.value.before
  }
  syncCleanText(notesStore.activeNote.content)
  notesStore.queueSaveNote()
}

function onRawContentChange() {
  parseContentSplit(notesStore.activeNote?.content || '')
  syncCleanText(notesStore.activeNote?.content || '')
  notesStore.queueSaveNote()
}

function onFolderChange() {
  notesStore.saveNote({ folder_id: notesStore.activeNote.folder_id })
}

function handleAITidy() {
  if (!notesStore.activeNote) return
  aiStore.openDrawer('tidy_note', notesStore.activeNote.content)
}

function handleExtractTasks() {
  if (!notesStore.activeNote) return
  aiStore.openDrawer('extract_tasks', notesStore.activeNote.content)
}

function openHistoryModal() {
  if (!notesStore.activeNote) return
  notesStore.fetchHistory(notesStore.activeNote.id)
  notesStore.isHistoryOpen = true
}

function downloadNoteMarkdown() {
  if (!notesStore.activeNote) return
  const blob = new Blob([notesStore.activeNote.content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${(notesStore.activeNote.title || 'untitled').replace(/[^a-z0-9_-]/gi, '_').toLowerCase()}.md`
  a.click()
  URL.revokeObjectURL(a)
}

function onTasksChange(payload) {
  if (!notesStore.activeNote) return
  let jsonStr = ''
  if (Array.isArray(payload)) {
    if (parsedTargets.value.length > 0 || parsedGroups.value.length > 0) {
      jsonStr = JSON.stringify({
        tasks: payload,
        targets: parsedTargets.value,
        groups: parsedGroups.value
      }, null, 2)
    } else {
      jsonStr = JSON.stringify(payload, null, 2)
    }
  } else if (typeof payload === 'object' && payload !== null) {
    jsonStr = JSON.stringify({
      tasks: payload.tasks || [],
      targets: payload.targets || [],
      groups: payload.groups || []
    }, null, 2)
  }

  const taskBlock = `\`\`\`tasks\n${jsonStr}\n\`\`\``

  if (checklistDock.value === 'sidebar') {
    const clean = editorCleanText.value.trim()
    notesStore.activeNote.content = clean ? `${clean}\n\n${taskBlock}\n` : `${taskBlock}\n`
  } else {
    notesStore.activeNote.content = `${splitData.value.before}${taskBlock}${splitData.value.after}`
  }
  notesStore.queueSaveNote()
}

function insertOrToggleChecklist() {
  if (!notesStore.activeNote) return
  if (hasTasks.value) {
    isChecklistVisible.value = true
    return
  }

  const defaultTasks = [
    {
      id: `task-${Date.now()}-1`,
      title: "Review project milestones & deliverables",
      done: false,
      status: "In Progress",
      priority: "High",
      due_date: new Date().toISOString().slice(0, 10)
    },
    {
      id: `task-${Date.now()}-2`,
      title: "Coordinate action items with team",
      done: false,
      status: "To Do",
      priority: "Normal",
      due_date: ""
    }
  ]
  const jsonStr = JSON.stringify(defaultTasks, null, 2)
  const taskBlock = `\n\n\`\`\`tasks\n${jsonStr}\n\`\`\`\n\n`
  const current = (notesStore.activeNote.content || '').trim()
  notesStore.activeNote.content = current ? `${current}${taskBlock}` : taskBlock.trim()
  parseContentSplit(notesStore.activeNote.content)
  syncCleanText(notesStore.activeNote.content)
  isChecklistVisible.value = true
  notesStore.queueSaveNote()
}

function removeChecklist() {
  if (!notesStore.activeNote) return
  notesStore.activeNote.content = editorCleanText.value.trim()
  parseContentSplit(notesStore.activeNote.content)
  syncCleanText(notesStore.activeNote.content)
  notesStore.queueSaveNote()
}

function insertTab(e) {
  const textarea = e.target
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const value = textarea.value
  textarea.value = value.substring(0, start) + '  ' + value.substring(end)
  textarea.selectionStart = textarea.selectionEnd = start + 2
  e.target.dispatchEvent(new Event('input'))
}

// SLASH COMMAND HANDLERS
function handleTextareaInput(e) {
  const textarea = e.target
  activeTextareaRef = textarea
  const val = textarea.value
  const caret = textarea.selectionStart

  const textBeforeCaret = val.slice(0, caret)
  const lastSlashIndex = textBeforeCaret.lastIndexOf('/')

  if (lastSlashIndex !== -1 && caret - lastSlashIndex <= 15) {
    const query = textBeforeCaret.slice(lastSlashIndex + 1)
    if (!/\s/.test(query)) {
      slashQuery.value = query
      isSlashOpen.value = true

      const rect = textarea.getBoundingClientRect()
      slashPos.value = {
        top: Math.min(rect.top + 70, window.innerHeight - 300),
        left: Math.min(rect.left + 30, window.innerWidth - 320)
      }
      return
    }
  }
  isSlashOpen.value = false
}

function onSlashCommandSelect(cmd) {
  isSlashOpen.value = false
  if (!activeTextareaRef) return

  const textarea = activeTextareaRef
  const val = textarea.value
  const caret = textarea.selectionStart
  const textBeforeCaret = val.slice(0, caret)
  const lastSlashIndex = textBeforeCaret.lastIndexOf('/')

  let replacement = ''
  if (cmd.id === 'checklist') {
    insertOrToggleChecklist()
    const before = val.slice(0, lastSlashIndex)
    const after = val.slice(caret)
    textarea.value = before + after
    textarea.dispatchEvent(new Event('input'))
    return
  } else if (cmd.id === 'extract_tasks') {
    handleExtractTasks()
    const before = val.slice(0, lastSlashIndex)
    const after = val.slice(caret)
    textarea.value = before + after
    textarea.dispatchEvent(new Event('input'))
    return
  } else if (cmd.id === 'template') {
    notesStore.isTemplatesOpen = true
    const before = val.slice(0, lastSlashIndex)
    const after = val.slice(caret)
    textarea.value = before + after
    textarea.dispatchEvent(new Event('input'))
    return
  } else if (cmd.id === 'ai_copilot') {
    aiStore.openDrawer('tidy_note', notesStore.activeNote?.content)
    const before = val.slice(0, lastSlashIndex)
    const after = val.slice(caret)
    textarea.value = before + after
    textarea.dispatchEvent(new Event('input'))
    return
  } else if (cmd.id === 'callout') {
    replacement = '\n> **Key Takeaway:** \n> Highlight important insight here...\n\n'
  } else if (cmd.id === 'h1') {
    replacement = '\n# Heading 1\n'
  } else if (cmd.id === 'h2') {
    replacement = '\n## Heading 2\n'
  } else if (cmd.id === 'h3') {
    replacement = '\n### Heading 3\n'
  } else if (cmd.id === 'code') {
    replacement = '\n```javascript\n// code here\n```\n'
  } else if (cmd.id === 'list') {
    replacement = '\n- Item 1\n- Item 2\n- Item 3\n'
  } else if (cmd.id === 'quote') {
    replacement = '\n> "Quote..."\n'
  }

  const before = val.slice(0, lastSlashIndex)
  const after = val.slice(caret)
  textarea.value = before + replacement + after
  textarea.selectionStart = textarea.selectionEnd = before.length + replacement.length
  textarea.dispatchEvent(new Event('input'))
  adjustTextareaHeight(textarea)
  textarea.focus()
}

// DRAGGABLE RESIZE DIVIDER IMPLEMENTATION
function startResize(e) {
  e.preventDefault()
  isResizing.value = true
  document.addEventListener('mousemove', onResizing)
  document.addEventListener('mouseup', stopResize)
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
}

function onResizing(e) {
  if (!isResizing.value) return
  const newWidth = window.innerWidth - e.clientX
  const maxAllowed = Math.min(window.innerWidth * 0.65, 750)
  sidebarWidth.value = Math.max(280, Math.min(newWidth, maxAllowed))
}

function stopResize() {
  if (!isResizing.value) return
  isResizing.value = false
  document.removeEventListener('mousemove', onResizing)
  document.removeEventListener('mouseup', stopResize)
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
  localStorage.setItem('noto_checklist_sidebar_width', String(sidebarWidth.value))
}

onBeforeUnmount(() => {
  stopResize()
})
</script>
