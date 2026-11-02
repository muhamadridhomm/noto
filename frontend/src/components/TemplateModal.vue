<template>
  <div
    v-if="notesStore.isTemplatesOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-stone-900/40 backdrop-blur-xs select-none"
    @click.self="notesStore.isTemplatesOpen = false"
  >
    <div class="w-full max-w-2xl bg-white rounded-xl shadow-2xl overflow-hidden border border-stone-200 animate-in fade-in zoom-in-95 duration-150">
      <!-- Modal Header -->
      <div class="px-6 py-4 border-b border-stone-100 flex items-center justify-between bg-stone-50/70">
        <div class="flex items-center gap-2.5">
          <div class="p-1.5 rounded-lg bg-amber-100 text-amber-800">
            <LayoutTemplate class="w-4 h-4" />
          </div>
          <div>
            <h3 class="text-sm font-bold text-stone-900">Template Gallery</h3>
            <p class="text-[11px] text-stone-500">Kickstart your notes with pre-built ClickUp trackers & structures</p>
          </div>
        </div>

        <button
          @click="notesStore.isTemplatesOpen = false"
          class="text-stone-400 hover:text-stone-700 p-1 rounded-md hover:bg-stone-200/60 transition"
        >
          <X class="w-4 h-4" />
        </button>
      </div>

      <!-- Templates Grid -->
      <div class="p-6 grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-[70vh] overflow-y-auto">
        <div
          v-for="tpl in templates"
          :key="tpl.id"
          @click="applyTemplate(tpl)"
          class="p-4 rounded-xl border border-stone-200 hover:border-amber-400 hover:bg-amber-50/30 transition cursor-pointer group flex flex-col justify-between"
        >
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="text-xl">{{ tpl.emoji }}</span>
              <span class="text-[10px] font-mono font-medium px-2 py-0.5 rounded-full bg-stone-100 text-stone-600 group-hover:bg-amber-100 group-hover:text-amber-800 transition">
                {{ tpl.category }}
              </span>
            </div>
            <h4 class="text-xs font-bold text-stone-900 group-hover:text-amber-900 transition">
              {{ tpl.title }}
            </h4>
            <p class="text-[11px] text-stone-500 mt-1 leading-relaxed">
              {{ tpl.description }}
            </p>
          </div>

          <div class="mt-4 pt-2 border-t border-stone-100 flex items-center justify-between text-[11px] font-medium text-amber-700">
            <span>Apply Template</span>
            <span>→</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useNotesStore } from '../stores/notes'
import { LayoutTemplate, X } from 'lucide-vue-next'

const notesStore = useNotesStore()

const templates = [
  {
    id: 'sprint',
    emoji: '🚀',
    category: 'Productivity',
    title: 'Sprint Planning & Tasks',
    description: 'Sprint goals, deliverables breakdown, and pre-built ClickUp task board with priorities.',
    content: `# Sprint Planning — Cycle 1

### Sprint Goals
- Deliver MVP features on time
- Validate user feedback and iterate
- Achieve 100% test pass rate

\`\`\`tasks
[
  {
    "id": "sp-1",
    "title": "Finalize feature scope and architecture",
    "done": true,
    "status": "Done",
    "priority": "Urgent",
    "due_date": ""
  },
  {
    "id": "sp-2",
    "title": "Implement core frontend & backend endpoints",
    "done": false,
    "status": "In Progress",
    "priority": "High",
    "due_date": ""
  },
  {
    "id": "sp-3",
    "title": "Run end-to-end QA validation",
    "done": false,
    "status": "To Do",
    "priority": "Normal",
    "due_date": ""
  }
]
\`\`\`

### Retrospective & Notes
`
  },
  {
    id: 'meeting',
    emoji: '🤝',
    category: 'Collaboration',
    title: 'Meeting Minutes & Decisions',
    description: 'Attendees, agenda, discussion notes, and actionable task checklist with due dates.',
    content: `# Meeting Minutes — Product Sync

**Date**: ${new Date().toLocaleDateString()}
**Attendees**: Team

### Agenda
1. Review roadmap progress
2. Discuss blockers & dependencies
3. Align on next week's deliverables

### Discussion & Key Decisions
- Agreed on local-first architecture for maximum speed and privacy.
- Decided to adopt ClickUp status pills and priority flags.

### Action Items
\`\`\`tasks
[
  {
    "id": "mtg-1",
    "title": "Draft revised specifications document",
    "done": false,
    "status": "In Progress",
    "priority": "High",
    "due_date": ""
  },
  {
    "id": "mtg-2",
    "title": "Sync with engineering on API contracts",
    "done": false,
    "status": "To Do",
    "priority": "Normal",
    "due_date": ""
  }
]
\`\`\`
`
  },
  {
    id: 'standup',
    emoji: '☀️',
    category: 'Daily',
    title: 'Daily Standup & Priorities',
    description: 'Yesterday accomplishments, today priorities, blockers, and quick checklist.',
    content: `# Daily Standup — ${new Date().toLocaleDateString()}

### Yesterday's Accomplishments
- Completed initial prototype
- Fixed responsiveness layout issues

### Today's Focus
\`\`\`tasks
[
  {
    "id": "std-1",
    "title": "Refine Kanban board and slash command menu",
    "done": false,
    "status": "In Progress",
    "priority": "Urgent",
    "due_date": ""
  },
  {
    "id": "std-2",
    "title": "Review test coverage and edge cases",
    "done": false,
    "status": "To Do",
    "priority": "Normal",
    "due_date": ""
  }
]
\`\`\`

### Blockers
- None at this moment.
`
  },
  {
    id: 'bug_triage',
    emoji: '🐛',
    category: 'Engineering',
    title: 'Bug Triage & QA Report',
    description: 'Steps to reproduce, expected vs actual behavior, severity rating, and fix verification.',
    content: `# Bug Triage & QA Report

**Severity**: High
**Environment**: Linux Pop!_OS / Chrome

### Steps to Reproduce
1. Open application from desktop
2. Trigger action item
3. Observe behavior

### Expected vs Actual
- **Expected**: Smooth render without delay
- **Actual**: Screen flicker

### Resolution Checklist
\`\`\`tasks
[
  {
    "id": "bug-1",
    "title": "Isolate root cause in component lifecycle",
    "done": false,
    "status": "In Progress",
    "priority": "Urgent",
    "due_date": ""
  },
  {
    "id": "bug-2",
    "title": "Apply fix and verify across browsers",
    "done": false,
    "status": "To Do",
    "priority": "High",
    "due_date": ""
  }
]
\`\`\`
`
  }
]

async function applyTemplate(tpl) {
  if (notesStore.activeNote) {
    if (confirm('Apply this template to the current note? (Existing content will be replaced)')) {
      notesStore.activeNote.title = tpl.title
      notesStore.activeNote.content = tpl.content
      await notesStore.saveNote()
      notesStore.isTemplatesOpen = false
    }
  } else {
    await notesStore.createNote(null, tpl.title, tpl.content)
    notesStore.isTemplatesOpen = false
  }
}
</script>
