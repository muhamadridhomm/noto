<template>
  <!-- MINIMIZED VIEW: Compact, sleek status bar (takes only ~38px height) -->
  <div
    v-if="minimized"
    class="my-3 rounded-lg border border-stone-200 bg-stone-50/90 hover:bg-stone-100/80 px-4 py-2 flex items-center justify-between gap-3 shadow-2xs transition select-none cursor-pointer group"
    @click="$emit('toggleMinimize')"
    title="Click to expand checklist table"
  >
    <div class="flex items-center gap-2.5 min-w-0">
      <div class="p-1 rounded-md bg-brand-100 text-brand-700 shrink-0">
        <CheckSquare class="w-3.5 h-3.5" />
      </div>
      <div class="flex items-center gap-2 truncate text-xs">
        <span class="font-bold text-stone-800">Checklist & Tasks</span>
        <span class="text-stone-300">•</span>
        <span class="text-stone-600 font-medium">
          {{ completedCount }} of {{ tasks.length }} done ({{ progressPercent }}%)
        </span>
        <span v-if="allGroups.length > 0" class="text-stone-300 hidden sm:inline">•</span>
        <span v-if="allGroups.length > 0" class="text-stone-500 text-[11px] hidden sm:inline">
          {{ allGroups.length }} Groups
        </span>
      </div>
    </div>

    <!-- Mini Progress Bar & Quick Actions -->
    <div class="flex items-center gap-2 shrink-0" @click.stop>
      <div class="w-16 bg-stone-200 h-1.5 rounded-full overflow-hidden hidden sm:block">
        <div
          class="h-full rounded-full transition-all duration-300"
          :class="progressPercent === 100 ? 'bg-emerald-500' : 'bg-brand-500'"
          :style="{ width: `${progressPercent}%` }"
        ></div>
      </div>

      <!-- Dock Toggle Button -->
      <button
        v-if="canDock"
        @click="$emit('toggleDock')"
        :title="dockMode === 'inline' ? 'Dock to right sidebar' : 'Embed inline into document'"
        class="text-stone-400 hover:text-stone-700 p-1 rounded hover:bg-stone-200/70 transition"
      >
        <Columns v-if="dockMode === 'inline'" class="w-3.5 h-3.5" />
        <ChevronDown v-else class="w-3.5 h-3.5" />
      </button>

      <!-- Expand Button -->
      <button
        @click="$emit('toggleMinimize')"
        title="Expand checklist"
        class="text-stone-500 hover:text-stone-900 p-1 rounded hover:bg-stone-200/70 transition flex items-center gap-1 text-[11px] font-medium"
      >
        <Maximize2 class="w-3 h-3" />
        <span class="hidden sm:inline">Expand</span>
      </button>

      <!-- Remove Button -->
      <button
        v-if="removable"
        @click="$emit('remove')"
        title="Remove checklist from note"
        class="text-stone-400 hover:text-rose-600 p-1 rounded hover:bg-stone-200/70 transition"
      >
        <X class="w-3.5 h-3.5" />
      </button>
    </div>
  </div>

  <!-- EXPANDED VIEW: Full Interactive Table, Kanban Board, or Timeline -->
  <div
    v-else
    class="my-4 rounded-xl border border-stone-200 bg-white shadow-xs overflow-hidden select-none"
    :class="dockMode === 'sidebar' ? 'border-stone-200/80 shadow-none' : ''"
  >
    <!-- Header with Progress Bar & View Actions -->
    <div class="px-4 py-3 bg-stone-50/80 border-b border-stone-200/80 flex flex-wrap items-center justify-between gap-2.5">
      <div class="flex items-center gap-2.5">
        <div class="p-1.5 rounded-lg bg-brand-100 text-brand-700 shrink-0">
          <CheckSquare class="w-4 h-4" />
        </div>
        <div>
          <h3 class="text-xs font-bold text-stone-800 uppercase tracking-wider flex items-center gap-1.5">
            <span>Checklist & Roadmap</span>
            <span class="text-[9px] font-mono font-normal px-1.5 py-0.2 rounded-full bg-brand-50 text-brand-700 border border-brand-200">
              TM Forum / ClickUp
            </span>
          </h3>
          <div class="flex items-center gap-1.5 mt-0.5 text-[11px] text-stone-500">
            <span>{{ completedCount }} of {{ tasks.length }} done</span>
            <span class="text-stone-300">•</span>
            <span class="font-semibold text-stone-700">{{ progressPercent }}%</span>
            <span v-if="allGroups.length > 0" class="text-stone-300">•</span>
            <span v-if="allGroups.length > 0" class="text-stone-600 font-medium">
              {{ allGroups.length }} Groups
            </span>
          </div>
        </div>
      </div>

      <!-- Action Controls: Table vs Kanban vs Timeline, Grouping, Filters, Docking, Minimize, Close -->
      <div class="flex items-center gap-1.5 flex-wrap">
        <!-- View Mode Switcher: Table vs Kanban vs Timeline -->
        <div class="flex bg-stone-200/80 p-0.5 rounded-lg text-xs font-medium text-stone-600 mr-1">
          <button
            @click="checklistView = 'table'"
            :class="['px-2.5 py-0.5 rounded-md transition text-[11px] flex items-center gap-1', checklistView === 'table' ? 'bg-white text-stone-900 shadow-2xs font-semibold' : 'hover:text-stone-900']"
            title="List / Table view"
          >
            <List class="w-3 h-3" />
            <span>Table</span>
          </button>
          <button
            @click="checklistView = 'kanban'"
            :class="['px-2.5 py-0.5 rounded-md transition text-[11px] flex items-center gap-1', checklistView === 'kanban' ? 'bg-white text-stone-900 shadow-2xs font-semibold' : 'hover:text-stone-900']"
            title="Kanban Board view"
          >
            <Kanban class="w-3 h-3" />
            <span>Kanban</span>
          </button>
          <button
            @click="checklistView = 'timeline'"
            :class="['px-2.5 py-0.5 rounded-md transition text-[11px] flex items-center gap-1', checklistView === 'timeline' ? 'bg-white text-stone-900 shadow-2xs font-semibold' : 'hover:text-stone-900']"
            title="Timeline & Gantt Roadmap view"
          >
            <CalendarDays class="w-3 h-3" />
            <span>Timeline</span>
          </button>
        </div>

        <!-- Grouping Controls (Toggle Grouping & New Group) -->
        <div class="flex items-center gap-1 bg-stone-200/70 p-0.5 rounded-lg text-xs font-medium text-stone-600">
          <button
            @click="isGrouped = !isGrouped"
            :class="['px-2 py-0.5 rounded-md transition text-[11px] flex items-center gap-1', isGrouped ? 'bg-white text-stone-900 shadow-2xs font-semibold' : 'hover:text-stone-900']"
            :title="isGrouped ? 'Grouping is Active (organized by topic/phase)' : 'Click to enable Grouping'"
          >
            <Layers class="w-3 h-3 text-brand-600" />
            <span>{{ isGrouped ? 'Grouped' : 'Flat' }}</span>
          </button>
          <button
            @click="promptAddGroup"
            class="px-2 py-0.5 rounded-md transition text-[11px] text-stone-600 hover:text-stone-900 hover:bg-white flex items-center gap-0.5"
            title="Create a new Group or Swimlane"
          >
            <Plus class="w-3 h-3" />
            <span class="hidden sm:inline">Group</span>
          </button>
        </div>

        <!-- Filter by Group Selector (Optional) -->
        <div v-if="allGroups.length > 0" class="relative hidden sm:block">
          <select
            v-model="selectedGroupFilter"
            class="text-[11px] font-medium bg-stone-100 hover:bg-stone-200 border border-stone-200 rounded-lg px-2 py-1 text-stone-700 cursor-pointer focus:outline-none"
          >
            <option value="all">All Groups ({{ allGroups.length }})</option>
            <option v-for="g in allGroups" :key="g" :value="g">
              {{ g }}
            </option>
          </select>
        </div>

        <!-- Quick Filter Tabs (All / Active / Completed) -->
        <div class="flex bg-stone-200/70 p-0.5 rounded-lg text-xs font-medium text-stone-600">
          <button
            @click="filterStatus = 'all'"
            :class="['px-2 py-0.5 rounded-md transition text-[11px]', filterStatus === 'all' ? 'bg-white text-stone-900 shadow-2xs font-semibold' : 'hover:text-stone-900']"
          >
            All ({{ tasks.length }})
          </button>
          <button
            @click="filterStatus = 'active'"
            :class="['px-2 py-0.5 rounded-md transition text-[11px]', filterStatus === 'active' ? 'bg-white text-stone-900 shadow-2xs font-semibold' : 'hover:text-stone-900']"
          >
            Active ({{ tasks.length - completedCount }})
          </button>
          <button
            @click="filterStatus = 'completed'"
            :class="['px-2 py-0.5 rounded-md transition text-[11px]', filterStatus === 'completed' ? 'bg-white text-stone-900 shadow-2xs font-semibold' : 'hover:text-stone-900']"
          >
            Done
          </button>
        </div>

        <!-- Dock Position Toggle Button -->
        <button
          v-if="canDock"
          @click="$emit('toggleDock')"
          :title="dockMode === 'inline' ? 'Move to right sidebar' : 'Embed inline in document'"
          class="text-stone-400 hover:text-stone-700 p-1 rounded-md hover:bg-stone-200/70 transition"
        >
          <Columns v-if="dockMode === 'inline'" class="w-3.5 h-3.5" />
          <ChevronDown v-else class="w-3.5 h-3.5" />
        </button>

        <!-- Minimize Button -->
        <button
          @click="$emit('toggleMinimize')"
          title="Minimize checklist to save screen space"
          class="text-stone-400 hover:text-stone-700 p-1 rounded-md hover:bg-stone-200/70 transition"
        >
          <Minimize2 class="w-3.5 h-3.5" />
        </button>

        <!-- Remove Button -->
        <button
          v-if="removable"
          @click="$emit('remove')"
          title="Remove checklist from note"
          class="text-stone-400 hover:text-rose-600 p-1 rounded-md hover:bg-stone-200/70 transition"
        >
          <X class="w-3.5 h-3.5" />
        </button>
      </div>
    </div>

    <!-- Overall Progress Bar Line -->
    <div class="w-full bg-stone-100 h-1.5 overflow-hidden">
      <div
        class="h-full transition-all duration-300 rounded-r"
        :class="progressPercent === 100 ? 'bg-emerald-500' : 'bg-gradient-to-r from-brand-500 to-indigo-500'"
        :style="{ width: `${progressPercent}%` }"
      ></div>
    </div>

    <!-- ============================================================= -->
    <!-- VIEW 1: KANBAN BOARD VIEW                                    -->
    <!-- ============================================================= -->
    <div v-if="checklistView === 'kanban'" class="p-3 bg-stone-100/50 overflow-x-auto">
      <div class="flex gap-3 min-w-[750px] pb-2">
        <div
          v-for="col in kanbanColumns"
          :key="col.status"
          class="flex-1 min-w-[210px] bg-stone-50/90 rounded-lg border border-stone-200/80 flex flex-col"
          :class="dockMode === 'sidebar' ? 'max-h-[500px]' : ''"
        >
          <!-- Column Header -->
          <div class="px-3 py-2 border-b border-stone-200/70 flex items-center justify-between">
            <div class="flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full" :class="col.dotClass"></span>
              <span class="text-xs font-bold text-stone-700">{{ col.title }}</span>
            </div>
            <span class="text-[10px] font-mono font-medium px-1.5 py-0.2 rounded-full bg-stone-200/70 text-stone-600">
              {{ getTasksByStatus(col.status).length }}
            </span>
          </div>

          <!-- Column Cards List -->
          <div
            class="flex-1 p-2 space-y-2"
            :class="dockMode === 'sidebar' ? 'overflow-y-auto' : ''"
          >
            <div
              v-for="task in getTasksByStatus(col.status)"
              :key="task.id"
              class="group bg-white p-2.5 rounded-lg border border-stone-200/90 shadow-2xs hover:shadow-xs transition space-y-2"
            >
              <!-- Card Top: Checkbox & Editable Title -->
              <div class="flex items-start gap-2">
                <button
                  @click="toggleTaskDone(task)"
                  type="button"
                  class="w-4 h-4 mt-0.5 rounded border flex items-center justify-center transition shrink-0"
                  :class="task.done ? 'bg-emerald-600 border-emerald-600 text-white' : 'border-stone-300 hover:border-brand-500 bg-white'"
                >
                  <Check v-if="task.done" class="w-3 h-3 stroke-[3]" />
                </button>

                <input
                  v-model="task.title"
                  @input="emitChange"
                  type="text"
                  placeholder="Task title..."
                  class="flex-1 bg-transparent border-none p-0 text-xs focus:outline-none focus:ring-0 leading-snug"
                  :class="task.done ? 'line-through text-stone-400' : 'text-stone-800 font-medium'"
                />

                <button
                  @click="openTaskNoteModal(task)"
                  :title="task.notes ? 'Buka Catatan Teknis (Sudah Terisi)' : 'Sisipkan Catatan / Spek (Buka Jendela Baru)'"
                  class="p-0.5 rounded transition shrink-0 cursor-pointer"
                  :class="task.notes ? 'text-brand-600 bg-brand-50' : 'text-stone-300 opacity-0 group-hover:opacity-100 hover:text-stone-600'"
                >
                  <FileText class="w-3 h-3" />
                </button>

                <button
                  @click="removeTask(task.id)"
                  title="Delete card"
                  class="text-stone-300 opacity-0 group-hover:opacity-100 hover:text-rose-600 p-0.5 rounded transition shrink-0"
                >
                  <Trash2 class="w-3 h-3" />
                </button>
              </div>

              <!-- Note Snippet in Kanban -->
              <div
                v-if="task.notes"
                @click="openTaskNoteModal(task)"
                class="text-[9px] text-stone-500 font-mono mt-0.5 truncate bg-stone-50 border border-stone-200/80 rounded px-1.5 py-0.5 cursor-pointer hover:text-brand-700 flex items-center gap-1"
                title="Buka Catatan Teknis di Jendela Baru"
              >
                <StickyNote class="w-2.5 h-2.5 text-brand-600 shrink-0" />
                <span class="truncate">{{ task.notes.replace(/\n/g, ' ') }}</span>
              </div>

              <!-- Card Group Pill (If assigned) -->
              <div v-if="task.group" class="flex items-center gap-1">
                <span class="px-1.5 py-0.5 rounded bg-brand-50 text-brand-700 border border-brand-200 text-[9px] font-medium truncate max-w-full">
                  {{ task.group }}
                </span>
              </div>

              <!-- Card Bottom: Priority, Due Date & Quick Move Dropdown -->
              <div class="flex items-center justify-between text-[10px] pt-1 border-t border-stone-100">
                <div class="flex items-center gap-1">
                  <!-- Priority badge -->
                  <span
                    class="px-1.5 py-0.5 rounded text-[9px] font-medium border"
                    :class="getPriorityClass(task.priority)"
                  >
                    {{ task.priority }}
                  </span>

                  <!-- Due date -->
                  <span
                    v-if="task.due_date"
                    class="font-mono text-[9px]"
                    :class="isOverdue(task.due_date, task.done) ? 'text-rose-600 font-semibold' : 'text-stone-400'"
                  >
                    {{ task.due_date }}
                  </span>
                </div>

                <!-- Move to status selector -->
                <select
                  :value="task.status"
                  @change="onKanbanStatusChange(task, $event.target.value)"
                  class="text-[9px] font-medium bg-stone-100 hover:bg-stone-200 border-none rounded px-1.5 py-0.5 text-stone-600 focus:outline-none cursor-pointer"
                >
                  <option value="To Do">Move: To Do</option>
                  <option value="In Progress">Move: In Progress</option>
                  <option value="In Review">Move: In Review</option>
                  <option value="Done">Move: Done</option>
                  <option value="Blocked">Move: Blocked</option>
                </select>
              </div>
            </div>

            <!-- Empty column placeholder -->
            <div
              v-if="getTasksByStatus(col.status).length === 0"
              class="py-6 text-center text-[11px] text-stone-400 italic"
            >
              Empty
            </div>
          </div>

          <!-- Quick Add Card to Column -->
          <div class="p-2 border-t border-stone-200/60 bg-stone-100/50">
            <button
              @click="addKanbanTask(col.status)"
              class="w-full py-1 text-[11px] text-stone-500 hover:text-stone-900 hover:bg-stone-200/80 rounded transition flex items-center justify-center gap-1"
            >
              <Plus class="w-3 h-3" />
              <span>Add Card</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================================= -->
    <!-- VIEW 2: TIMELINE / GANTT ROADMAP VIEW                        -->
    <!-- ============================================================= -->
    <div v-else-if="checklistView === 'timeline'" class="p-4 bg-stone-50/50 overflow-x-auto">
      <div class="min-w-[750px] space-y-4">
        <!-- DYNAMIC & CRUD-ABLE TARGET MILESTONES BANNER -->
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-xs font-bold text-stone-700 uppercase tracking-wider flex items-center gap-1.5">
                <Target class="w-3.5 h-3.5 text-brand-600" />
                <span>Target Milestones & Phase Goals</span>
              </span>
              <span class="text-[10px] font-mono px-1.5 py-0.2 rounded-full bg-stone-200 text-stone-600 font-semibold">
                {{ targets.length }} Goals
              </span>
            </div>

            <button
              @click="openAddTargetModal"
              class="text-xs text-brand-600 hover:text-brand-800 font-semibold flex items-center gap-1 hover:underline cursor-pointer"
            >
              <Plus class="w-3 h-3" />
              <span>+ Add Target Goal</span>
            </button>
          </div>

          <!-- Target Cards Grid -->
          <div v-if="targets.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            <div
              v-for="tgt in targets"
              :key="tgt.id"
              class="p-3 bg-white border border-stone-200/90 hover:border-brand-300 rounded-xl flex flex-col justify-between shadow-2xs transition group"
            >
              <div>
                <div class="flex items-start justify-between gap-2">
                  <div class="flex items-center gap-1.5 min-w-0">
                    <div class="p-1 rounded-md bg-brand-100 text-brand-700 shrink-0">
                      <CalendarDays class="w-3.5 h-3.5" />
                    </div>
                    <span class="text-xs font-bold text-stone-900 truncate" :title="tgt.title">{{ tgt.title }}</span>
                  </div>

                  <!-- Quick Action Buttons: Edit & Delete -->
                  <div class="flex items-center gap-1 opacity-80 group-hover:opacity-100 transition shrink-0">
                    <button
                      @click="openEditTargetModal(tgt)"
                      title="Edit target goal"
                      class="p-1 text-stone-400 hover:text-brand-600 hover:bg-stone-100 rounded transition"
                    >
                      <Pencil class="w-3 h-3" />
                    </button>
                    <button
                      @click="deleteTarget(tgt.id)"
                      title="Delete target goal"
                      class="p-1 text-stone-400 hover:text-rose-600 hover:bg-stone-100 rounded transition"
                    >
                      <Trash2 class="w-3 h-3" />
                    </button>
                  </div>
                </div>

                <div class="flex items-center gap-2 mt-1.5 flex-wrap">
                  <span v-if="tgt.badge" class="text-[9px] font-mono px-1.5 py-0.2 rounded bg-indigo-100 text-indigo-800 font-bold">
                    {{ tgt.badge }}
                  </span>
                  <span v-if="tgt.date" class="text-[10px] font-mono text-stone-500 flex items-center gap-1">
                    <Clock class="w-3 h-3 text-stone-400" />
                    <span>{{ tgt.date }}</span>
                  </span>
                </div>

                <p v-if="tgt.description" class="text-[11px] text-stone-600 mt-1 leading-snug line-clamp-3">
                  {{ tgt.description }}
                </p>
              </div>
            </div>
          </div>

          <!-- Empty State for Targets -->
          <div
            v-else
            @click="openAddTargetModal"
            class="p-3 border border-dashed border-stone-200 hover:border-brand-400 bg-stone-50/70 hover:bg-stone-100/60 rounded-xl text-center cursor-pointer transition flex items-center justify-center gap-2 text-xs text-stone-500 font-medium"
          >
            <Plus class="w-3.5 h-3.5 text-brand-600" />
            <span>Belum ada Target Goal untuk catatan ini. Klik untuk menambah Target Milestone pertama (misal: Target Sprint, Deadline Integrasi, dsb).</span>
          </div>
        </div>

        <!-- Timeline Mode Controls: Swimlanes by Group vs Chronological List -->
        <div class="flex items-center justify-between pb-1 border-b border-stone-200/70 text-xs">
          <div class="flex items-center gap-2">
            <span class="font-semibold text-stone-700">Timeline Mode:</span>
            <div class="flex bg-stone-200/80 p-0.5 rounded-lg font-medium text-stone-600">
              <button
                @click="timelineMode = 'swimlane'"
                :class="['px-2 py-0.5 rounded transition text-[11px]', timelineMode === 'swimlane' ? 'bg-white text-stone-900 shadow-2xs font-semibold' : 'hover:text-stone-900']"
              >
                Group Swimlanes
              </button>
              <button
                @click="timelineMode = 'chronological'"
                :class="['px-2 py-0.5 rounded transition text-[11px]', timelineMode === 'chronological' ? 'bg-white text-stone-900 shadow-2xs font-semibold' : 'hover:text-stone-900']"
              >
                Chronological Schedule
              </button>
            </div>
          </div>

          <!-- Add Actions on Timeline -->
          <div class="flex items-center gap-2">
            <button
              v-if="timelineMode === 'swimlane'"
              @click="promptAddGroup"
              class="px-2.5 py-1 bg-white hover:bg-stone-100 border border-stone-300 text-stone-700 rounded-lg text-xs font-semibold transition flex items-center gap-1 shadow-2xs"
            >
              <FolderPlus class="w-3.5 h-3.5 text-brand-600" />
              <span>+ New Swimlane</span>
            </button>

            <button
              @click="addTimelineTask"
              class="px-2.5 py-1 bg-stone-900 hover:bg-stone-800 text-white rounded-lg text-xs font-medium transition flex items-center gap-1 shadow-2xs"
            >
              <Plus class="w-3.5 h-3.5" />
              <span>Add Task</span>
            </button>
          </div>
        </div>

        <!-- TIMELINE CASE A: GROUP SWIMLANES -->
        <div v-if="timelineMode === 'swimlane'" class="space-y-4">
          <div
            v-for="grp in displayGroups"
            :key="grp"
            class="bg-white rounded-xl border border-stone-200 shadow-2xs overflow-hidden"
          >
            <!-- Swimlane Header -->
            <div class="px-4 py-2.5 bg-stone-100/70 border-b border-stone-200/80 flex items-center justify-between">
              <div class="flex items-center gap-2 min-w-0">
                <span class="w-2.5 h-2.5 rounded-full bg-brand-600 shrink-0"></span>
                <span class="text-xs font-bold text-stone-800 tracking-tight truncate">{{ grp }}</span>
                <span class="text-[10px] font-mono px-2 py-0.2 rounded-full bg-stone-200 text-stone-600 font-semibold shrink-0">
                  {{ getTasksInGroup(grp).length }} tasks
                </span>

                <!-- Rename Swimlane -->
                <button
                  @click="promptRenameGroup(grp)"
                  title="Rename swimlane"
                  class="p-1 text-stone-400 hover:text-stone-800 hover:bg-stone-200 rounded transition"
                >
                  <Pencil class="w-3 h-3" />
                </button>

                <!-- Delete Swimlane -->
                <button
                  @click="promptDeleteGroup(grp)"
                  title="Delete swimlane (tasks will become ungrouped)"
                  class="p-1 text-stone-400 hover:text-rose-600 hover:bg-stone-200 rounded transition"
                >
                  <Trash2 class="w-3 h-3" />
                </button>
              </div>

              <button
                @click="addTaskToGroup(grp)"
                class="text-[11px] text-brand-700 hover:underline flex items-center gap-1 font-semibold shrink-0"
              >
                <Plus class="w-3 h-3" />
                <span>Add Task to {{ grp }}</span>
              </button>
            </div>

            <!-- Swimlane Task Timeline Rows -->
            <div class="p-3 space-y-2">
              <div v-if="getTasksInGroup(grp).length === 0" class="py-4 text-center text-xs text-stone-400 italic">
                No tasks assigned to this group yet.
              </div>

              <div
                v-for="task in getSortedTasksInGroup(grp)"
                :key="task.id"
                class="p-2.5 rounded-lg border border-stone-200/80 hover:border-stone-300 hover:bg-stone-50/60 transition flex items-center justify-between gap-3 text-xs"
                :class="{ 'bg-stone-50/40 opacity-75': task.done }"
              >
                <!-- Left: Checkbox + Title + Note Snippet -->
                <div class="flex items-start gap-2.5 min-w-0 flex-1">
                  <button
                    @click="toggleTaskDone(task)"
                    type="button"
                    class="w-4 h-4 mt-0.5 rounded border flex items-center justify-center transition shrink-0"
                    :class="task.done ? 'bg-emerald-600 border-emerald-600 text-white' : 'border-stone-300 hover:border-brand-500 bg-white'"
                  >
                    <Check v-if="task.done" class="w-3 h-3 stroke-[3]" />
                  </button>

                  <div class="flex-1 min-w-0">
                    <input
                      v-model="task.title"
                      @input="emitChange"
                      type="text"
                      class="w-full bg-transparent border-none p-0 text-xs focus:outline-none focus:ring-0 leading-relaxed font-medium"
                      :class="task.done ? 'line-through text-stone-400' : 'text-stone-800'"
                    />
                    <div
                      v-if="task.notes"
                      @click="openTaskNoteModal(task)"
                      class="text-[10px] text-stone-500 font-mono mt-0.5 truncate max-w-xl flex items-center gap-1.5 cursor-pointer hover:text-brand-700"
                      title="Klik untuk membuka catatan teknis di jendela baru"
                    >
                      <StickyNote class="w-3 h-3 text-brand-600 shrink-0" />
                      <span class="text-stone-700 font-medium shrink-0">Catatan:</span>
                      <span class="truncate">{{ task.notes.replace(/\n/g, ' ') }}</span>
                    </div>
                  </div>
                </div>

                <!-- Right: Status, Priority, Due Date Picker & Relative Distance Badge -->
                <div class="flex items-center gap-2 shrink-0">
                  <!-- Note button -->
                  <button
                    @click="openTaskNoteModal(task)"
                    :title="task.notes ? 'Buka Catatan Teknis (Sudah Terisi)' : 'Sisipkan Catatan / Spek (Buka Jendela Baru)'"
                    class="px-1.5 py-0.5 rounded transition flex items-center gap-1 text-[10px] cursor-pointer"
                    :class="task.notes ? 'bg-brand-50 text-brand-700 border border-brand-200 font-semibold' : 'text-stone-400 hover:text-stone-700 hover:bg-stone-100 border border-transparent'"
                  >
                    <FileText class="w-3.5 h-3.5" :class="task.notes ? 'text-brand-600' : 'text-stone-400'" />
                    <span v-if="task.notes" class="hidden sm:inline">Note</span>
                  </button>
                  <!-- Status Pill -->
                  <span
                    class="text-[10px] font-medium px-2 py-0.5 rounded-full border"
                    :class="getStatusBadgeClass(task.status)"
                  >
                    {{ task.status }}
                  </span>

                  <!-- Priority Flag -->
                  <span
                    class="text-[10px] font-medium px-1.5 py-0.5 rounded border"
                    :class="getPriorityClass(task.priority)"
                  >
                    {{ task.priority }}
                  </span>

                  <!-- Relative Date Badge -->
                  <span
                    class="text-[10px] px-2 py-0.5 rounded-md border font-mono"
                    :class="getRelativeDateBadge(task.due_date, task.done).class"
                  >
                    {{ getRelativeDateBadge(task.due_date, task.done).text }}
                  </span>

                  <!-- Date Input -->
                  <input
                    v-model="task.due_date"
                    @change="emitChange"
                    type="date"
                    title="Change deadline"
                    class="text-[10px] font-mono bg-stone-100 border border-stone-200 rounded px-1.5 py-0.5 text-stone-600 focus:outline-none cursor-pointer"
                  />

                  <!-- Delete -->
                  <button
                    @click="removeTask(task.id)"
                    title="Delete milestone"
                    class="text-stone-300 hover:text-rose-600 p-0.5 rounded transition"
                  >
                    <Trash2 class="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Ungrouped Tasks Swimlane (if any tasks have no group) -->
          <div
            v-if="ungroupedTasks.length > 0"
            class="bg-white rounded-xl border border-dashed border-stone-300 shadow-2xs overflow-hidden"
          >
            <!-- Ungrouped Swimlane Header -->
            <div class="px-4 py-2.5 bg-stone-50 border-b border-stone-200 flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full bg-stone-400"></span>
                <span class="text-xs font-bold text-stone-600 tracking-tight">Ungrouped Tasks</span>
                <span class="text-[10px] font-mono px-2 py-0.2 rounded-full bg-stone-200 text-stone-600 font-semibold">
                  {{ ungroupedTasks.length }} tasks
                </span>
              </div>
              <button
                @click="addTaskToGroup('')"
                class="text-[11px] text-stone-600 hover:text-stone-900 hover:underline flex items-center gap-1 font-medium"
              >
                <Plus class="w-3 h-3" />
                <span>Add Task</span>
              </button>
            </div>

            <div class="p-3 space-y-2">
              <div
                v-for="task in ungroupedTasks"
                :key="task.id"
                class="p-2.5 rounded-lg border border-stone-200/80 hover:border-stone-300 hover:bg-stone-50/60 transition flex items-center justify-between gap-3 text-xs"
                :class="{ 'bg-stone-50/40 opacity-75': task.done }"
              >
                <div class="flex items-start gap-2.5 min-w-0 flex-1">
                  <button
                    @click="toggleTaskDone(task)"
                    type="button"
                    class="w-4 h-4 mt-0.5 rounded border flex items-center justify-center transition shrink-0"
                    :class="task.done ? 'bg-emerald-600 border-emerald-600 text-white' : 'border-stone-300 hover:border-brand-500 bg-white'"
                  >
                    <Check v-if="task.done" class="w-3 h-3 stroke-[3]" />
                  </button>
                  <div class="flex-1 min-w-0">
                    <input
                      v-model="task.title"
                      @input="emitChange"
                      type="text"
                      class="w-full bg-transparent border-none p-0 text-xs focus:outline-none focus:ring-0 leading-relaxed font-medium"
                      :class="task.done ? 'line-through text-stone-400' : 'text-stone-800'"
                    />
                    <div
                      v-if="task.notes"
                      @click="openTaskNoteModal(task)"
                      class="text-[10px] text-stone-500 font-mono mt-0.5 truncate max-w-xl flex items-center gap-1.5 cursor-pointer hover:text-brand-700"
                      title="Klik untuk membuka catatan teknis di jendela baru"
                    >
                      <StickyNote class="w-3 h-3 text-brand-600 shrink-0" />
                      <span class="text-stone-700 font-medium shrink-0">Catatan:</span>
                      <span class="truncate">{{ task.notes.replace(/\n/g, ' ') }}</span>
                    </div>
                  </div>
                </div>

                <div class="flex items-center gap-2 shrink-0">
                  <button
                    @click="openTaskNoteModal(task)"
                    :title="task.notes ? 'Buka Catatan Teknis (Sudah Terisi)' : 'Sisipkan Catatan / Spek (Buka Jendela Baru)'"
                    class="px-1.5 py-0.5 rounded transition flex items-center gap-1 text-[10px] cursor-pointer"
                    :class="task.notes ? 'bg-brand-50 text-brand-700 border border-brand-200 font-semibold' : 'text-stone-400 hover:text-stone-700 hover:bg-stone-100 border border-transparent'"
                  >
                    <FileText class="w-3.5 h-3.5" :class="task.notes ? 'text-brand-600' : 'text-stone-400'" />
                    <span v-if="task.notes" class="hidden sm:inline">Note</span>
                  </button>
                  <select
                    v-model="task.group"
                    @change="emitChange"
                    class="text-[9px] font-medium px-1.5 py-0.5 rounded bg-stone-100 border border-stone-200 text-stone-700 focus:outline-none max-w-[110px] truncate"
                  >
                    <option value="">Assign Group...</option>
                    <option v-for="g in allGroups" :key="g" :value="g">{{ g }}</option>
                  </select>

                  <span
                    class="text-[10px] font-medium px-2 py-0.5 rounded-full border"
                    :class="getStatusBadgeClass(task.status)"
                  >
                    {{ task.status }}
                  </span>

                  <span
                    class="text-[10px] px-2 py-0.5 rounded-md border font-mono"
                    :class="getRelativeDateBadge(task.due_date, task.done).class"
                  >
                    {{ getRelativeDateBadge(task.due_date, task.done).text }}
                  </span>

                  <input
                    v-model="task.due_date"
                    @change="emitChange"
                    type="date"
                    class="text-[10px] font-mono bg-stone-100 border border-stone-200 rounded px-1.5 py-0.5 text-stone-600 focus:outline-none cursor-pointer"
                  />

                  <button
                    @click="removeTask(task.id)"
                    title="Delete milestone"
                    class="text-stone-300 hover:text-rose-600 p-0.5 rounded transition"
                  >
                    <Trash2 class="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- TIMELINE CASE B: CHRONOLOGICAL SCHEDULE -->
        <div v-else class="bg-white rounded-xl border border-stone-200 shadow-2xs divide-y divide-stone-100 overflow-hidden">
          <div v-if="chronologicalTasks.length === 0" class="py-8 text-center text-xs text-stone-400">
            No tasks found.
          </div>

          <div
            v-for="task in chronologicalTasks"
            :key="task.id"
            class="p-3 hover:bg-stone-50/80 transition flex items-center justify-between gap-3 text-xs"
            :class="{ 'bg-stone-50/40 opacity-75': task.done }"
          >
            <!-- Left: Checkbox + Title + Group -->
            <div class="flex items-center gap-2.5 min-w-0 flex-1">
              <button
                @click="toggleTaskDone(task)"
                type="button"
                class="w-4 h-4 rounded border flex items-center justify-center transition shrink-0"
                :class="task.done ? 'bg-emerald-600 border-emerald-600 text-white' : 'border-stone-300 hover:border-brand-500 bg-white'"
              >
                <Check v-if="task.done" class="w-3 h-3 stroke-[3]" />
              </button>

              <div class="min-w-0 flex-1">
                <input
                  v-model="task.title"
                  @input="emitChange"
                  type="text"
                  class="w-full bg-transparent border-none p-0 text-xs focus:outline-none focus:ring-0 leading-relaxed font-medium"
                  :class="task.done ? 'line-through text-stone-400' : 'text-stone-800'"
                />
                <div v-if="task.group" class="flex items-center gap-1 mt-0.5">
                  <span class="text-[9px] px-1.5 py-0.2 rounded bg-brand-50 text-brand-700 border border-brand-200 font-medium">
                    {{ task.group }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Right: Due Date & Badges -->
            <div class="flex items-center gap-2 shrink-0">
              <span
                class="text-[10px] font-medium px-2 py-0.5 rounded-full border"
                :class="getStatusBadgeClass(task.status)"
              >
                {{ task.status }}
              </span>

              <span
                class="text-[10px] font-medium px-1.5 py-0.5 rounded border"
                :class="getPriorityClass(task.priority)"
              >
                {{ task.priority }}
              </span>

              <span
                class="text-[10px] px-2 py-0.5 rounded-md border font-mono"
                :class="getRelativeDateBadge(task.due_date, task.done).class"
              >
                {{ getRelativeDateBadge(task.due_date, task.done).text }}
              </span>

              <input
                v-model="task.due_date"
                @change="emitChange"
                type="date"
                class="text-[10px] font-mono bg-stone-100 border border-stone-200 rounded px-1.5 py-0.5 text-stone-600 focus:outline-none cursor-pointer"
              />

              <button
                @click="removeTask(task.id)"
                class="text-stone-300 hover:text-rose-600 p-0.5 rounded transition"
              >
                <Trash2 class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================================= -->
    <!-- VIEW 3: SIDEBAR LAYOUT (When docked to sidebar)              -->
    <!-- ============================================================= -->
    <div v-else-if="dockMode === 'sidebar'" class="divide-y divide-stone-100 max-h-[calc(100vh-220px)] overflow-y-auto">
      <div v-if="filteredTasks.length === 0" class="py-6 text-center text-xs text-stone-400">
        No tasks matching this filter.
      </div>

      <div
        v-for="task in filteredTasks"
        :key="task.id"
        class="group p-3 hover:bg-stone-50/90 transition text-xs space-y-2"
        :class="{ 'bg-stone-50/40': task.done }"
      >
        <!-- Row 1: Checkbox + Title + Note + Delete -->
        <div class="flex items-start gap-2">
          <button
            @click="toggleTaskDone(task)"
            type="button"
            class="w-4 h-4 mt-0.5 rounded border flex items-center justify-center transition shrink-0"
            :class="task.done ? 'bg-emerald-600 border-emerald-600 text-white' : 'border-stone-300 hover:border-brand-500 bg-white'"
          >
            <Check v-if="task.done" class="w-3 h-3 stroke-[3]" />
          </button>

          <div class="flex-1 min-w-0">
            <input
              v-model="task.title"
              @input="emitChange"
              @keydown.enter="handleEnterKey"
              type="text"
              placeholder="Task description..."
              class="w-full bg-transparent border-none p-0 text-xs focus:outline-none focus:ring-0 leading-relaxed"
              :class="task.done ? 'line-through text-stone-400' : 'text-stone-800 font-medium'"
            />
            <div
              v-if="task.notes"
              @click="openTaskNoteModal(task)"
              class="text-[10px] text-stone-500 font-mono mt-0.5 truncate max-w-xl flex items-center gap-1.5 cursor-pointer hover:text-brand-700"
              title="Klik untuk membuka catatan teknis di jendela baru"
            >
              <StickyNote class="w-3 h-3 text-brand-600 shrink-0" />
              <span class="text-stone-700 font-medium shrink-0">Catatan:</span>
              <span class="truncate">{{ task.notes.replace(/\n/g, ' ') }}</span>
            </div>
          </div>

          <button
            @click="openTaskNoteModal(task)"
            :title="task.notes ? 'Buka Catatan Teknis (Sudah Terisi)' : 'Sisipkan Catatan / Spek (Buka Jendela Baru)'"
            class="px-1.5 py-0.5 rounded transition shrink-0 flex items-center gap-1 text-[10px] cursor-pointer"
            :class="task.notes ? 'bg-brand-50 text-brand-700 border border-brand-200 font-semibold' : 'text-stone-400 hover:text-stone-700 hover:bg-stone-100 border border-transparent'"
          >
            <FileText class="w-3 h-3" :class="task.notes ? 'text-brand-600' : 'text-stone-400'" />
            <span v-if="task.notes" class="hidden sm:inline">Note</span>
          </button>

          <button
            @click="removeTask(task.id)"
            title="Delete task"
            class="text-stone-300 opacity-0 group-hover:opacity-100 hover:text-rose-600 p-0.5 rounded transition shrink-0 cursor-pointer"
          >
            <Trash2 class="w-3.5 h-3.5" />
          </button>
        </div>

        <!-- Row 2: Group Pill + Status + Priority + Due Date -->
        <div class="flex items-center justify-between gap-1.5 pl-6 flex-wrap">
          <div class="flex items-center gap-1.5 flex-wrap">
            <!-- Group Selector -->
            <select
              v-model="task.group"
              @change="emitChange"
              class="text-[9px] font-medium px-1.5 py-0.5 rounded bg-stone-100 border border-stone-200 text-stone-700 focus:outline-none max-w-[110px] truncate"
            >
              <option value="">No Group</option>
              <option v-for="g in allGroups" :key="g" :value="g">{{ g }}</option>
            </select>

            <!-- Status Pill -->
            <select
              v-model="task.status"
              @change="onStatusChange(task)"
              class="text-[10px] font-medium px-2 py-0.5 rounded-full border border-transparent appearance-none cursor-pointer focus:outline-none shadow-2xs"
              :class="getStatusBadgeClass(task.status)"
            >
              <option value="To Do">To Do</option>
              <option value="In Progress">In Progress</option>
              <option value="In Review">In Review</option>
              <option value="Done">Done</option>
              <option value="Blocked">Blocked</option>
            </select>

            <!-- Priority Pill -->
            <select
              v-model="task.priority"
              @change="emitChange"
              class="text-[10px] font-medium px-1.5 py-0.5 rounded border appearance-none cursor-pointer focus:outline-none shadow-2xs"
              :class="getPriorityClass(task.priority)"
            >
              <option value="Urgent">Urgent</option>
              <option value="High">High</option>
              <option value="Normal">Normal</option>
              <option value="Low">Low</option>
            </select>
          </div>

          <!-- Due Date -->
          <input
            v-model="task.due_date"
            @change="emitChange"
            type="date"
            class="text-[10px] font-mono bg-stone-100 border border-stone-200 rounded px-1.5 py-0.5 text-stone-600 focus:outline-none"
            :class="isOverdue(task.due_date, task.done) ? 'text-rose-600 border-rose-300 bg-rose-50' : ''"
          />
        </div>
      </div>
    </div>

    <!-- ============================================================= -->
    <!-- VIEW 4: INLINE TABLE LAYOUT (Document Flow, with Grouping)    -->
    <!-- ============================================================= -->
    <div v-else class="overflow-x-auto">
      <div class="min-w-[760px]">
        <!-- CASE 4A: GROUPED TABLE VIEW (Default) -->
        <div v-if="isGrouped" class="space-y-4 p-3 bg-stone-50/40">
          <div
            v-for="grp in displayGroups"
            :key="grp"
            class="rounded-xl border border-stone-200/90 bg-white overflow-hidden shadow-2xs"
          >
            <!-- Group Header Bar with CRUD Group Controls -->
            <div class="px-4 py-2.5 bg-stone-100/70 border-b border-stone-200/80 flex items-center justify-between gap-2">
              <div class="flex items-center gap-2 min-w-0">
                <button
                  @click="toggleGroupCollapse(grp)"
                  class="p-1 rounded text-stone-500 hover:text-stone-800 hover:bg-stone-200/70 transition"
                  title="Collapse/Expand group"
                >
                  <ChevronDown v-if="!collapsedGroups[grp]" class="w-3.5 h-3.5" />
                  <ChevronRight v-else class="w-3.5 h-3.5" />
                </button>

                <div class="flex items-center gap-2 truncate">
                  <span class="text-xs font-bold text-stone-800 tracking-tight flex items-center gap-1.5">
                    <span class="w-2.5 h-2.5 rounded-full bg-brand-600 shrink-0"></span>
                    <span class="truncate">{{ grp }}</span>
                  </span>
                  <span class="text-[10px] font-mono px-2 py-0.2 rounded-full bg-stone-200/80 text-stone-600 font-semibold shrink-0">
                    {{ getGroupCompletedCount(grp) }}/{{ getTasksInGroup(grp).length }} done
                  </span>
                </div>
              </div>

              <!-- Group Actions: Mini Progress Bar + Add Task + Rename + Delete -->
              <div class="flex items-center gap-1.5 shrink-0">
                <div class="w-16 bg-stone-200 h-1.5 rounded-full overflow-hidden hidden sm:block">
                  <div
                    class="h-full rounded-full transition-all duration-300"
                    :class="getGroupProgress(grp) === 100 ? 'bg-emerald-500' : 'bg-brand-500'"
                    :style="{ width: `${getGroupProgress(grp)}%` }"
                  ></div>
                </div>

                <button
                  @click="addTaskToGroup(grp)"
                  class="px-2 py-0.5 text-[11px] font-medium text-brand-700 bg-brand-50 hover:bg-brand-100 border border-brand-200 rounded-md transition flex items-center gap-1"
                  title="Add new task into this group"
                >
                  <Plus class="w-3 h-3 text-brand-600" />
                  <span>Add Task</span>
                </button>

                <button
                  @click="promptRenameGroup(grp)"
                  class="p-1 text-stone-400 hover:text-stone-800 hover:bg-stone-200/70 rounded transition"
                  title="Rename this group"
                >
                  <Edit2 class="w-3 h-3" />
                </button>

                <button
                  @click="promptDeleteGroup(grp)"
                  class="p-1 text-stone-400 hover:text-rose-600 hover:bg-rose-50 rounded transition"
                  title="Delete this group"
                >
                  <Trash2 class="w-3 h-3" />
                </button>
              </div>
            </div>

            <!-- Group Tasks Table Body (Collapsible) -->
            <div v-show="!collapsedGroups[grp]">
              <!-- Column Headers Inside Group -->
              <div class="grid grid-cols-12 gap-2 px-4 py-2 bg-stone-50/60 border-b border-stone-100 text-[10px] font-semibold text-stone-400 uppercase tracking-wider">
                <div class="col-span-1 text-center">Done</div>
                <div class="col-span-5">Task Description</div>
                <div class="col-span-2">Group Reassign</div>
                <div class="col-span-2">Status & Priority</div>
                <div class="col-span-2 text-right pr-2">Due Date</div>
              </div>

              <!-- Rows in this Group -->
              <div class="divide-y divide-stone-100">
                <div v-if="getTasksInGroup(grp).length === 0" class="py-4 text-center text-xs text-stone-400 italic">
                  No tasks in this group yet. Click "+ Add Task" above.
                </div>

                <div
                  v-for="task in getTasksInGroup(grp)"
                  :key="task.id"
                  class="group grid grid-cols-12 gap-2 px-4 py-2.5 items-center hover:bg-stone-50/80 transition text-xs"
                  :class="{ 'bg-stone-50/30': task.done }"
                >
                  <!-- Done Checkbox -->
                  <div class="col-span-1 flex items-center justify-center">
                    <button
                      @click="toggleTaskDone(task)"
                      type="button"
                      class="w-4 h-4 rounded border flex items-center justify-center transition"
                      :class="task.done ? 'bg-emerald-600 border-emerald-600 text-white' : 'border-stone-300 hover:border-brand-500 bg-white'"
                    >
                      <Check v-if="task.done" class="w-3 h-3 stroke-[3]" />
                    </button>
                  </div>

                  <!-- Task Title -->
                  <div class="col-span-5 flex items-center gap-2 pr-2">
                    <input
                      v-model="task.title"
                      @input="emitChange"
                      @keydown.enter="handleEnterKey"
                      type="text"
                      placeholder="What needs to be done?"
                      class="w-full bg-transparent border-none p-0 text-xs focus:outline-none focus:ring-0 leading-relaxed font-normal"
                      :class="task.done ? 'line-through text-stone-400' : 'text-stone-800 font-medium'"
                    />
                  </div>

                  <!-- Group Selector (Reassign on the fly) -->
                  <div class="col-span-2 pr-2">
                    <select
                      v-model="task.group"
                      @change="emitChange"
                      class="w-full text-[10px] font-medium bg-stone-100 hover:bg-stone-200/80 border border-stone-200 rounded px-1.5 py-1 text-stone-700 cursor-pointer focus:outline-none truncate"
                    >
                      <option value="">(No Group)</option>
                      <option v-for="g in allGroups" :key="g" :value="g">{{ g }}</option>
                    </select>
                  </div>

                  <!-- Status & Priority Combined -->
                  <div class="col-span-2 flex items-center gap-1.5">
                    <div class="relative flex-1">
                      <select
                        v-model="task.status"
                        @change="onStatusChange(task)"
                        class="w-full text-[10px] font-medium px-2 py-0.5 rounded-full border border-transparent appearance-none cursor-pointer focus:outline-none shadow-2xs pr-4 truncate"
                        :class="getStatusBadgeClass(task.status)"
                      >
                        <option value="To Do">To Do</option>
                        <option value="In Progress">In Progress</option>
                        <option value="In Review">In Review</option>
                        <option value="Done">Done</option>
                        <option value="Blocked">Blocked</option>
                      </select>
                    </div>

                    <div class="relative shrink-0">
                      <select
                        v-model="task.priority"
                        @change="emitChange"
                        class="text-[10px] font-medium px-1.5 py-0.5 rounded border appearance-none cursor-pointer focus:outline-none shadow-2xs"
                        :class="getPriorityClass(task.priority)"
                      >
                        <option value="Urgent">Urgent</option>
                        <option value="High">High</option>
                        <option value="Normal">Normal</option>
                        <option value="Low">Low</option>
                      </select>
                    </div>
                  </div>

                  <!-- Due Date & Delete Action -->
                  <div class="col-span-2 flex items-center justify-end gap-1.5">
                    <input
                      v-model="task.due_date"
                      @change="emitChange"
                      type="date"
                      class="text-[10px] font-mono bg-stone-100/70 border border-stone-200/80 rounded px-1.5 py-0.5 text-stone-600 focus:outline-none"
                      :class="isOverdue(task.due_date, task.done) ? 'text-rose-600 border-rose-300 bg-rose-50' : ''"
                    />
                    <button
                      @click="removeTask(task.id)"
                      title="Delete task row"
                      class="text-stone-300 opacity-0 group-hover:opacity-100 hover:text-rose-600 p-1 rounded transition"
                    >
                      <Trash2 class="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Ungrouped Tasks (if any tasks don't have a group) -->
          <div
            v-if="ungroupedTasks.length > 0"
            class="rounded-xl border border-dashed border-stone-300 bg-white overflow-hidden shadow-2xs"
          >
            <div class="px-4 py-2.5 bg-stone-50 border-b border-stone-200 flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="text-xs font-bold text-stone-500 tracking-tight">Ungrouped Tasks</span>
                <span class="text-[10px] font-mono px-2 py-0.2 rounded-full bg-stone-200 text-stone-600">
                  {{ ungroupedTasks.length }} tasks
                </span>
              </div>
            </div>

            <div class="divide-y divide-stone-100">
              <div
                v-for="task in ungroupedTasks"
                :key="task.id"
                class="group grid grid-cols-12 gap-2 px-4 py-2.5 items-center hover:bg-stone-50/80 transition text-xs"
                :class="{ 'bg-stone-50/30': task.done }"
              >
                <!-- Done Checkbox -->
                <div class="col-span-1 flex items-center justify-center">
                  <button
                    @click="toggleTaskDone(task)"
                    type="button"
                    class="w-4 h-4 rounded border flex items-center justify-center transition"
                    :class="task.done ? 'bg-emerald-600 border-emerald-600 text-white' : 'border-stone-300 hover:border-brand-500 bg-white'"
                  >
                    <Check v-if="task.done" class="w-3 h-3 stroke-[3]" />
                  </button>
                </div>

                <!-- Title -->
                <div class="col-span-5 flex items-center gap-2 pr-2">
                  <input
                    v-model="task.title"
                    @input="emitChange"
                    type="text"
                    placeholder="Task description..."
                    class="w-full bg-transparent border-none p-0 text-xs focus:outline-none focus:ring-0 leading-relaxed font-normal"
                    :class="task.done ? 'line-through text-stone-400' : 'text-stone-800 font-medium'"
                  />
                </div>

                <!-- Assign to Group -->
                <div class="col-span-2 pr-2">
                  <select
                    v-model="task.group"
                    @change="emitChange"
                    class="w-full text-[10px] font-medium bg-stone-100 hover:bg-stone-200 border border-stone-200 rounded px-1.5 py-1 text-stone-700 cursor-pointer focus:outline-none truncate"
                  >
                    <option value="">Assign to Group...</option>
                    <option v-for="g in allGroups" :key="g" :value="g">{{ g }}</option>
                  </select>
                </div>

                <!-- Status & Priority -->
                <div class="col-span-2 flex items-center gap-1.5">
                  <select
                    v-model="task.status"
                    @change="onStatusChange(task)"
                    class="w-full text-[10px] font-medium px-2 py-0.5 rounded-full border border-transparent appearance-none cursor-pointer focus:outline-none shadow-2xs pr-4 truncate"
                    :class="getStatusBadgeClass(task.status)"
                  >
                    <option value="To Do">To Do</option>
                    <option value="In Progress">In Progress</option>
                    <option value="In Review">In Review</option>
                    <option value="Done">Done</option>
                    <option value="Blocked">Blocked</option>
                  </select>
                  <select
                    v-model="task.priority"
                    @change="emitChange"
                    class="text-[10px] font-medium px-1.5 py-0.5 rounded border appearance-none cursor-pointer focus:outline-none shadow-2xs"
                    :class="getPriorityClass(task.priority)"
                  >
                    <option value="Urgent">Urgent</option>
                    <option value="High">High</option>
                    <option value="Normal">Normal</option>
                    <option value="Low">Low</option>
                  </select>
                </div>

                <!-- Due Date & Delete -->
                <div class="col-span-2 flex items-center justify-end gap-1.5">
                  <input
                    v-model="task.due_date"
                    @change="emitChange"
                    type="date"
                    class="text-[10px] font-mono bg-stone-100/70 border border-stone-200/80 rounded px-1.5 py-0.5 text-stone-600 focus:outline-none"
                    :class="isOverdue(task.due_date, task.done) ? 'text-rose-600 border-rose-300 bg-rose-50' : ''"
                  />
                  <button
                    @click="removeTask(task.id)"
                    class="text-stone-300 opacity-0 group-hover:opacity-100 hover:text-rose-600 p-1 rounded transition"
                  >
                    <Trash2 class="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- CASE 4B: FLAT TABLE VIEW (When isGrouped === false) -->
        <div v-else>
          <!-- Column Headers -->
          <div class="grid grid-cols-12 gap-2 px-5 py-2 bg-stone-50/50 border-b border-stone-100 text-[11px] font-semibold text-stone-400 uppercase tracking-wider">
            <div class="col-span-1 text-center">Done</div>
            <div class="col-span-5">Task Description</div>
            <div class="col-span-2">Group</div>
            <div class="col-span-2">Status & Priority</div>
            <div class="col-span-2 text-right pr-2">Due Date</div>
          </div>

          <!-- Task Rows List -->
          <div class="divide-y divide-stone-100">
            <div v-if="filteredTasks.length === 0" class="py-6 text-center text-xs text-stone-400">
              No tasks matching this filter.
            </div>

            <div
              v-for="task in filteredTasks"
              :key="task.id"
              class="group grid grid-cols-12 gap-2 px-5 py-2.5 items-center hover:bg-stone-50/80 transition text-xs"
              :class="{ 'bg-stone-50/30': task.done }"
            >
              <!-- Done Checkbox -->
              <div class="col-span-1 flex items-center justify-center">
                <button
                  @click="toggleTaskDone(task)"
                  type="button"
                  class="w-4 h-4 rounded border flex items-center justify-center transition"
                  :class="task.done ? 'bg-emerald-600 border-emerald-600 text-white' : 'border-stone-300 hover:border-brand-500 bg-white'"
                >
                  <Check v-if="task.done" class="w-3 h-3 stroke-[3]" />
                </button>
              </div>

              <!-- Task Title -->
              <div class="col-span-5 flex items-center gap-2 pr-2">
                <input
                  v-model="task.title"
                  @input="emitChange"
                  @keydown.enter="handleEnterKey"
                  type="text"
                  placeholder="What needs to be done?"
                  class="w-full bg-transparent border-none p-0 text-xs focus:outline-none focus:ring-0 leading-relaxed font-normal"
                  :class="task.done ? 'line-through text-stone-400' : 'text-stone-800 font-medium'"
                />
              </div>

              <!-- Group Selector -->
              <div class="col-span-2 pr-2">
                <select
                  v-model="task.group"
                  @change="emitChange"
                  class="w-full text-[10px] font-medium bg-stone-100 hover:bg-stone-200 border border-stone-200 rounded px-1.5 py-1 text-stone-700 cursor-pointer focus:outline-none truncate"
                >
                  <option value="">No Group</option>
                  <option v-for="g in allGroups" :key="g" :value="g">{{ g }}</option>
                </select>
              </div>

              <!-- Status & Priority Combined -->
              <div class="col-span-2 flex items-center gap-1.5">
                <select
                  v-model="task.status"
                  @change="onStatusChange(task)"
                  class="w-full text-[10px] font-medium px-2 py-0.5 rounded-full border border-transparent appearance-none cursor-pointer focus:outline-none shadow-2xs pr-4 truncate"
                  :class="getStatusBadgeClass(task.status)"
                >
                  <option value="To Do">To Do</option>
                  <option value="In Progress">In Progress</option>
                  <option value="In Review">In Review</option>
                  <option value="Done">Done</option>
                  <option value="Blocked">Blocked</option>
                </select>
                <select
                  v-model="task.priority"
                  @change="emitChange"
                  class="text-[10px] font-medium px-1.5 py-0.5 rounded border appearance-none cursor-pointer focus:outline-none shadow-2xs"
                  :class="getPriorityClass(task.priority)"
                >
                  <option value="Urgent">Urgent</option>
                  <option value="High">High</option>
                  <option value="Normal">Normal</option>
                  <option value="Low">Low</option>
                </select>
              </div>

              <!-- Due Date & Delete -->
              <div class="col-span-2 flex items-center justify-end gap-1.5">
                <input
                  v-model="task.due_date"
                  @change="emitChange"
                  type="date"
                  class="text-[10px] font-mono bg-stone-100/70 border border-stone-200/80 rounded px-1.5 py-0.5 text-stone-600 focus:outline-none"
                  :class="isOverdue(task.due_date, task.done) ? 'text-rose-600 border-rose-300 bg-rose-50' : ''"
                />
                <button
                  @click="removeTask(task.id)"
                  title="Delete task row"
                  class="text-stone-300 opacity-0 group-hover:opacity-100 hover:text-rose-600 p-1 rounded transition"
                >
                  <Trash2 class="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Add Task Bar (Available in Table & Flat View) -->
    <div v-if="checklistView === 'table'" class="px-4 py-2.5 bg-stone-50/70 border-t border-stone-100 flex items-center gap-2.5 flex-wrap sm:flex-nowrap">
      <Plus class="w-4 h-4 text-stone-400 shrink-0 ml-0.5" />
      <input
        v-model="newTaskTitle"
        @keydown.enter.prevent="addTask"
        type="text"
        placeholder="+ Add a task row (Type and press Enter)..."
        class="flex-1 text-xs bg-transparent border-none p-0 text-stone-800 placeholder-stone-400 focus:outline-none focus:ring-0 min-w-[200px]"
      />

      <!-- Assign to Group for New Task -->
      <select
        v-model="newTaskGroup"
        class="text-[11px] font-medium bg-white border border-stone-200 rounded-md px-2 py-1 text-stone-700 cursor-pointer focus:outline-none"
      >
        <option value="">Group: (None)</option>
        <option v-for="g in allGroups" :key="g" :value="g">Group: {{ g }}</option>
      </select>

      <button
        @click="addTask"
        :disabled="!newTaskTitle.trim()"
        class="text-xs px-3 py-1 bg-stone-900 hover:bg-stone-800 disabled:opacity-40 text-white rounded-md font-medium transition shrink-0 cursor-pointer"
      >
        Add Task
      </button>
    </div>

    <!-- ========================================================= -->
    <!-- MODAL: TASK DETAIL & NOTES ("JENDELA BARU CATATAN TUGAS") -->
    <!-- ========================================================= -->
    <div
      v-if="activeTaskNote"
      class="fixed inset-0 z-70 flex items-center justify-center p-4 bg-stone-900/60 backdrop-blur-xs select-none"
      @click.self="closeTaskNoteModal"
    >
      <div class="w-full max-w-2xl bg-white rounded-2xl shadow-2xl border border-stone-200 overflow-hidden flex flex-col max-h-[85vh] animate-in fade-in zoom-in-95 duration-150">
        <!-- Modal Header -->
        <div class="px-6 py-4 border-b border-stone-200 bg-stone-50/90 flex items-center justify-between gap-3">
          <div class="flex items-center gap-2.5 min-w-0">
            <div class="p-2 bg-brand-50 text-brand-700 border border-brand-200 rounded-xl shrink-0">
              <FileText class="w-5 h-5 text-brand-600" />
            </div>
            <div class="min-w-0">
              <div class="flex items-center gap-2">
                <span class="text-[10px] font-mono uppercase tracking-wider px-2 py-0.2 bg-stone-200 text-stone-700 rounded-md font-semibold">
                  {{ activeTaskNote.id }}
                </span>
                <span
                  class="text-[10px] font-medium px-2 py-0.5 rounded-full border"
                  :class="getStatusBadgeClass(activeTaskNote.status)"
                >
                  {{ activeTaskNote.status }}
                </span>
                <span
                  class="text-[10px] font-medium px-1.5 py-0.5 rounded border"
                  :class="getPriorityClass(activeTaskNote.priority)"
                >
                  {{ activeTaskNote.priority }}
                </span>
              </div>
              <h3 class="text-sm font-bold text-stone-900 truncate mt-1">
                {{ activeTaskNote.title }}
              </h3>
            </div>
          </div>

          <button
            @click="closeTaskNoteModal"
            class="text-stone-400 hover:text-stone-700 p-1.5 rounded-md hover:bg-stone-200/60 transition cursor-pointer"
          >
            <X class="w-5 h-5" />
          </button>
        </div>

        <!-- Metadata Strip -->
        <div class="px-6 py-2 bg-white border-b border-stone-100 flex items-center justify-between text-xs text-stone-500 flex-wrap gap-2">
          <div class="flex items-center gap-2">
            <span v-if="activeTaskNote.group" class="px-2 py-0.5 rounded bg-brand-50 text-brand-700 border border-brand-200 text-[10px] font-medium flex items-center gap-1">
              <Tag class="w-2.5 h-2.5 text-brand-600" />
              <span>{{ activeTaskNote.group }}</span>
            </span>
            <span v-if="activeTaskNote.due_date" class="font-mono text-[10px] text-stone-500 flex items-center gap-1">
              <Calendar class="w-3 h-3 text-stone-400" />
              <span>{{ activeTaskNote.due_date }}</span>
            </span>
          </div>

          <!-- Tab Switcher: Edit vs Preview -->
          <div class="flex bg-stone-100 p-0.5 rounded-lg text-xs font-medium text-stone-600">
            <button
              @click="taskNoteTab = 'edit'"
              :class="['px-2.5 py-0.5 rounded transition text-[11px]', taskNoteTab === 'edit' ? 'bg-white text-stone-900 shadow-2xs font-semibold' : 'hover:text-stone-900']"
            >
              Edit Markdown
            </button>
            <button
              @click="taskNoteTab = 'preview'"
              :class="['px-2.5 py-0.5 rounded transition text-[11px]', taskNoteTab === 'preview' ? 'bg-white text-stone-900 shadow-2xs font-semibold' : 'hover:text-stone-900']"
            >
              Preview Render
            </button>
          </div>
        </div>

        <!-- Modal Body -->
        <div class="flex-1 overflow-y-auto p-6 bg-stone-50/40">
          <!-- Quick Template Inserter -->
          <div v-if="taskNoteTab === 'edit'" class="mb-3 flex items-center gap-2 flex-wrap">
            <span class="text-[11px] font-semibold text-stone-500">Template Cepat:</span>
            <button
              type="button"
              @click="insertNetworkMatrixTemplate"
              class="px-2 py-1 bg-white hover:bg-stone-100 border border-stone-200 rounded text-[10px] font-medium text-stone-700 flex items-center gap-1 shadow-2xs transition cursor-pointer"
            >
              <Table class="w-3 h-3 text-brand-600" />
              <span>+ Matriks Jaringan (IP/Port/Firewall)</span>
            </button>
            <button
              type="button"
              @click="insertApiSpecTemplate"
              class="px-2 py-1 bg-white hover:bg-stone-100 border border-stone-200 rounded text-[10px] font-medium text-stone-700 flex items-center gap-1 shadow-2xs transition cursor-pointer"
            >
              <Code class="w-3 h-3 text-emerald-600" />
              <span>+ Spesifikasi Endpoint REST</span>
            </button>
          </div>

          <!-- Editor View -->
          <div v-if="taskNoteTab === 'edit'">
            <textarea
              v-model="editingTaskNoteContent"
              rows="12"
              placeholder="Tuliskan catatan teknis, matriks IP/port, checklist sub-task, atau spesifikasi implementasi di sini..."
              class="w-full p-3.5 bg-white border border-stone-200 rounded-xl focus:outline-none focus:ring-1 focus:ring-brand-500 text-xs font-mono leading-relaxed resize-none shadow-2xs"
            ></textarea>
          </div>

          <!-- Preview View -->
          <div v-else class="p-4 bg-white border border-stone-200 rounded-xl min-h-[260px] shadow-2xs">
            <div
              v-if="editingTaskNoteContent.trim()"
              class="markdown-body prose prose-stone max-w-none text-xs leading-relaxed"
              v-html="renderedTaskNoteMarkdown"
            ></div>
            <div v-else class="text-stone-400 italic text-center py-12 text-xs">
              Belum ada catatan untuk tugas ini. Beralih ke tab Edit untuk menulis.
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="px-6 py-3 border-t border-stone-200 bg-stone-50 flex items-center justify-between">
          <button
            v-if="editingTaskNoteContent.trim()"
            @click="clearTaskNote"
            class="text-xs text-rose-600 hover:text-rose-800 hover:underline font-medium cursor-pointer"
          >
            Hapus Catatan
          </button>
          <div v-else></div>

          <div class="flex items-center gap-2">
            <button
              @click="closeTaskNoteModal"
              class="px-3.5 py-1.5 bg-stone-100 hover:bg-stone-200 text-stone-700 rounded-lg text-xs font-medium transition cursor-pointer"
            >
              Tutup
            </button>
            <button
              @click="saveTaskNote"
              class="px-4 py-1.5 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-semibold shadow-2xs transition cursor-pointer flex items-center gap-1.5"
            >
              <Save class="w-3.5 h-3.5" />
              <span>Simpan Catatan</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { marked } from 'marked'
import {
  Check, CheckSquare, Plus, Trash2, ChevronDown, ChevronRight, X, Maximize2, Minimize2,
  Columns, List, Kanban, CalendarDays, Layers, Edit2, Clock, Pencil, FolderPlus, Target,
  FileText, Table, Code, Save, StickyNote, Tag, Calendar
} from 'lucide-vue-next'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  initialTargets: {
    type: Array,
    default: () => []
  },
  initialGroups: {
    type: Array,
    default: () => []
  },
  removable: {
    type: Boolean,
    default: false
  },
  dockMode: {
    type: String,
    default: 'inline' // 'inline' | 'sidebar'
  },
  minimized: {
    type: Boolean,
    default: false
  },
  canDock: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue', 'change', 'remove', 'toggleDock', 'toggleMinimize'])

const tasks = computed({
  get: () => props.modelValue,
  set: (val) => {
    emit('update:modelValue', val)
    emitChange()
  }
})

// Targets / Milestones state
const targets = ref([...(props.initialTargets || [])])
watch(() => props.initialTargets, (newVal) => {
  if (newVal) targets.value = [...newVal]
}, { deep: true })

// View mode state
const checklistView = ref('table') // 'table' | 'kanban' | 'timeline'
const timelineMode = ref('swimlane') // 'swimlane' | 'chronological'
const filterStatus = ref('all') // 'all' | 'active' | 'completed'
const selectedGroupFilter = ref('all') // 'all' | groupName

// Grouping State & CRUD
const isGrouped = ref(true)
const collapsedGroups = ref({})
const customGroups = ref([...(props.initialGroups || [])])
watch(() => props.initialGroups, (newVal) => {
  if (newVal) customGroups.value = [...newVal]
}, { deep: true })

const newTaskTitle = ref('')
const newTaskGroup = ref('')

// Compute all unique groups from tasks and custom additions
const allGroups = computed(() => {
  const set = new Set()
  customGroups.value.forEach(g => {
    if (g && g.trim()) set.add(g.trim())
  })
  tasks.value.forEach(t => {
    if (t.group && t.group.trim()) {
      set.add(t.group.trim())
    }
  })
  return Array.from(set)
})

// Groups filtered by selectedGroupFilter if active
const displayGroups = computed(() => {
  if (selectedGroupFilter.value && selectedGroupFilter.value !== 'all') {
    return allGroups.value.filter(g => g === selectedGroupFilter.value)
  }
  return allGroups.value
})

function getTasksInGroup(groupName) {
  return filteredTasks.value.filter(t => t.group === groupName)
}

function getSortedTasksInGroup(groupName) {
  return [...getTasksInGroup(groupName)].sort((a, b) => {
    if (!a.due_date && !b.due_date) return 0
    if (!a.due_date) return 1
    if (!b.due_date) return -1
    return new Date(a.due_date) - new Date(b.due_date)
  })
}

const ungroupedTasks = computed(() => {
  if (selectedGroupFilter.value && selectedGroupFilter.value !== 'all') {
    return []
  }
  return filteredTasks.value.filter(t => !t.group || !t.group.trim())
})

function getGroupCompletedCount(groupName) {
  return getTasksInGroup(groupName).filter(t => t.done).length
}

function getGroupProgress(groupName) {
  const grpTasks = getTasksInGroup(groupName)
  if (grpTasks.length === 0) return 0
  return Math.round((getGroupCompletedCount(groupName) / grpTasks.length) * 100)
}

function toggleGroupCollapse(groupName) {
  collapsedGroups.value[groupName] = !collapsedGroups.value[groupName]
}

// CRUD Target Goals Actions
function openAddTargetModal() {
  const title = prompt("Enter Target Milestone / Goal Title (e.g. 'Target Rilis Sprint 1', 'Launching MVP', 'Deadline Integrasi'):")
  if (!title || !title.trim()) return
  const date = prompt("Enter Target Deadline Date (YYYY-MM-DD):", new Date().toISOString().slice(0, 10))
  const badge = prompt("Enter Category / Phase Badge (e.g. 'Integrasi', 'Operasional', 'Milestone'):", "Milestone")
  const description = prompt("Enter Brief Description or Key Deliverables:") || ""

  const newTarget = {
    id: `tgt-${Date.now()}`,
    title: title.trim(),
    date: date ? date.trim() : "",
    badge: badge ? badge.trim() : "",
    description: description.trim()
  }
  targets.value.push(newTarget)
  emitChange()
}

function openEditTargetModal(target) {
  const title = prompt("Edit Target Title:", target.title)
  if (!title || !title.trim()) return
  const date = prompt("Edit Target Deadline Date (YYYY-MM-DD):", target.date || "")
  const badge = prompt("Edit Category Badge:", target.badge || "")
  const description = prompt("Edit Description:", target.description || "")

  target.title = title.trim()
  if (date !== null) target.date = date.trim()
  if (badge !== null) target.badge = badge.trim()
  if (description !== null) target.description = description.trim()
  emitChange()
}

function deleteTarget(targetId) {
  if (confirm("Delete this target milestone?")) {
    targets.value = targets.value.filter(t => t.id !== targetId)
    emitChange()
  }
}

// CRUD Group / Swimlane Actions
function promptAddGroup() {
  const name = prompt("Enter new Swimlane / Group name:")
  if (!name || !name.trim()) return
  const clean = name.trim()
  if (!customGroups.value.includes(clean)) {
    customGroups.value.push(clean)
  }
  isGrouped.value = true
  emitChange()
}

function promptRenameGroup(oldName) {
  const newName = prompt(`Rename swimlane "${oldName}" to:`, oldName)
  if (!newName || !newName.trim() || newName.trim() === oldName) return
  const clean = newName.trim()

  tasks.value.forEach(t => {
    if (t.group === oldName) {
      t.group = clean
    }
  })
  const idx = customGroups.value.indexOf(oldName)
  if (idx !== -1) {
    customGroups.value[idx] = clean
  } else {
    customGroups.value.push(clean)
  }
  emitChange()
}

function promptDeleteGroup(groupName) {
  const tasksInGrp = tasks.value.filter(t => t.group === groupName)
  const confirmMsg = tasksInGrp.length > 0
    ? `Swimlane "${groupName}" contains ${tasksInGrp.length} task(s).\n\nClick OK to delete swimlane (tasks will become Ungrouped).\nClick Cancel to abort.`
    : `Remove empty swimlane "${groupName}"?`

  if (!confirm(confirmMsg)) return

  tasks.value.forEach(t => {
    if (t.group === groupName) {
      t.group = ''
    }
  })
  customGroups.value = customGroups.value.filter(g => g !== groupName)
  emitChange()
}

function addTaskToGroup(groupName) {
  const title = prompt(`Add task under "${groupName}":`)
  if (!title || !title.trim()) return
  const newTask = {
    id: `task-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
    title: title.trim(),
    done: false,
    status: 'To Do',
    priority: 'Normal',
    due_date: '',
    group: groupName
  }
  tasks.value = [...tasks.value, newTask]
  emitChange()
}

// Kanban Columns definition
const kanbanColumns = [
  { status: 'To Do', title: 'To Do', dotClass: 'bg-stone-400' },
  { status: 'In Progress', title: 'In Progress', dotClass: 'bg-blue-500' },
  { status: 'In Review', title: 'In Review', dotClass: 'bg-amber-500' },
  { status: 'Done', title: 'Done', dotClass: 'bg-emerald-500' },
  { status: 'Blocked', title: 'Blocked', dotClass: 'bg-rose-500' }
]

function getTasksByStatus(status) {
  let list = tasks.value.filter(t => t.status === status)
  if (selectedGroupFilter.value && selectedGroupFilter.value !== 'all') {
    list = list.filter(t => t.group === selectedGroupFilter.value)
  }
  return list
}

function onKanbanStatusChange(task, newStatus) {
  task.status = newStatus
  task.done = newStatus === 'Done'
  emitChange()
}

function addKanbanTask(status) {
  const title = prompt(`Enter task title for "${status}":`)
  if (!title || !title.trim()) return
  const newTask = {
    id: `task-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
    title: title.trim(),
    done: status === 'Done',
    status: status,
    priority: status === 'Blocked' ? 'Urgent' : 'Normal',
    due_date: '',
    group: selectedGroupFilter.value !== 'all' ? selectedGroupFilter.value : ''
  }
  tasks.value = [...tasks.value, newTask]
  emitChange()
}

// Timeline Helper & Add Task
function addTimelineTask() {
  const title = prompt('Enter Milestone / Task description:')
  if (!title || !title.trim()) return
  const dateStr = prompt('Target Due Date (YYYY-MM-DD):', '2026-11-30')
  const defaultGrp = allGroups.value.length > 0 ? allGroups.value[0] : ''
  const grp = prompt('Group / Topic name:', defaultGrp) || ''

  const newTask = {
    id: `task-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
    title: title.trim(),
    done: false,
    status: 'To Do',
    priority: 'High',
    due_date: dateStr ? dateStr.trim() : '',
    group: grp.trim()
  }
  tasks.value = [...tasks.value, newTask]
  emitChange()
}

const chronologicalTasks = computed(() => {
  let list = [...filteredTasks.value]
  if (selectedGroupFilter.value && selectedGroupFilter.value !== 'all') {
    list = list.filter(t => t.group === selectedGroupFilter.value)
  }
  return list.sort((a, b) => {
    if (!a.due_date && !b.due_date) return 0
    if (!a.due_date) return 1
    if (!b.due_date) return -1
    return new Date(a.due_date) - new Date(b.due_date)
  })
})

function getRelativeDateBadge(dateStr, done) {
  if (!dateStr) return { text: 'No Date', class: 'text-stone-400 bg-stone-100 border-stone-200' }
  if (done) return { text: `Done (${dateStr})`, class: 'text-emerald-700 bg-emerald-50 border-emerald-200' }

  const target = new Date(dateStr)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  target.setHours(0, 0, 0, 0)
  const diffTime = target - today
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays < 0) {
    return { text: `Overdue (${Math.abs(diffDays)}d ago)`, class: 'text-rose-700 bg-rose-50 border-rose-300 font-semibold' }
  } else if (diffDays === 0) {
    return { text: 'Due Today', class: 'text-amber-700 bg-amber-50 border-amber-300 font-semibold' }
  } else if (diffDays === 1) {
    return { text: 'Due Tomorrow', class: 'text-amber-700 bg-amber-50 border-amber-300' }
  } else {
    return { text: `${diffDays}d left (${dateStr})`, class: 'text-stone-600 bg-stone-100 border-stone-200' }
  }
}

const completedCount = computed(() => {
  return tasks.value.filter(t => t.done).length
})

const progressPercent = computed(() => {
  if (tasks.value.length === 0) return 0
  return Math.round((completedCount.value / tasks.value.length) * 100)
})

const filteredTasks = computed(() => {
  let list = tasks.value
  if (selectedGroupFilter.value && selectedGroupFilter.value !== 'all') {
    list = list.filter(t => t.group === selectedGroupFilter.value)
  }
  if (filterStatus.value === 'active') {
    return list.filter(t => !t.done)
  }
  if (filterStatus.value === 'completed') {
    return list.filter(t => t.done)
  }
  return list
})

function emitChange() {
  emit('update:modelValue', [...tasks.value])
  emit('change', {
    tasks: [...tasks.value],
    targets: [...targets.value],
    groups: [...customGroups.value]
  })
}

function toggleTaskDone(task) {
  task.done = !task.done
  if (task.done && task.status !== 'Done') {
    task.status = 'Done'
  } else if (!task.done && task.status === 'Done') {
    task.status = 'To Do'
  }
  emitChange()
}

function onStatusChange(task) {
  if (task.status === 'Done') {
    task.done = true
  } else {
    task.done = false
  }
  emitChange()
}

function addTask() {
  if (!newTaskTitle.value.trim()) return
  const newTask = {
    id: `task-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
    title: newTaskTitle.value.trim(),
    done: false,
    status: 'To Do',
    priority: 'Normal',
    due_date: '',
    group: newTaskGroup.value || (allGroups.value.length > 0 ? allGroups.value[0] : ''),
    notes: ''
  }
  tasks.value = [...tasks.value, newTask]
  newTaskTitle.value = ''
  emitChange()
}

// Task Note Modal ("Jendela Baru Catatan / Spek Teknis")
const activeTaskNote = ref(null)
const editingTaskNoteContent = ref('')
const taskNoteTab = ref('edit') // 'edit' | 'preview'

const renderedTaskNoteMarkdown = computed(() => {
  return marked.parse(editingTaskNoteContent.value || '')
})

function openTaskNoteModal(task) {
  activeTaskNote.value = task
  editingTaskNoteContent.value = task.notes || ''
  taskNoteTab.value = (task.notes && task.notes.trim()) ? 'preview' : 'edit'
}

function closeTaskNoteModal() {
  activeTaskNote.value = null
  editingTaskNoteContent.value = ''
}

function saveTaskNote() {
  if (!activeTaskNote.value) return
  activeTaskNote.value.notes = editingTaskNoteContent.value.trim()
  emitChange()
  closeTaskNoteModal()
}

function clearTaskNote() {
  if (confirm('Hapus seluruh catatan pada tugas ini?')) {
    editingTaskNoteContent.value = ''
    saveTaskNote()
  }
}

function insertNetworkMatrixTemplate() {
  const tpl = `
### Network & Connectivity Matrix
| Parameter | Value / Configuration |
| :--- | :--- |
| **Source** | \`<source network>\` |
| **Destination** | \`<destination host>\` |
| **Protocol** | \`HTTPS / TCP\` |
| **Owner** | \`<team or contact>\` |
| **Status** | \`<planned / active / verified>\` |
`
  editingTaskNoteContent.value = (editingTaskNoteContent.value ? editingTaskNoteContent.value.trim() + '\n\n' : '') + tpl
}

function insertApiSpecTemplate() {
  const tpl = `
### REST API Specification
- **Base URL:** \`https://api.example.com/v1\`
- **Method:** \`GET / POST\`
- **Headers:** \`Content-Type: application/json\`
- **Authentication:** \`<authentication method>\`
- **Purpose:** \`<describe the operation>\`
`
  editingTaskNoteContent.value = (editingTaskNoteContent.value ? editingTaskNoteContent.value.trim() + '\n\n' : '') + tpl
}

function handleEnterKey() {
  addTask()
}

function removeTask(id) {
  tasks.value = tasks.value.filter(t => t.id !== id)
  emitChange()
}

function isOverdue(dateStr, done) {
  if (!dateStr || done) return false
  const target = new Date(dateStr)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return target < today
}

function getStatusBadgeClass(status) {
  switch (status) {
    case 'Done':
      return 'bg-emerald-100 text-emerald-800 border-emerald-200'
    case 'In Progress':
      return 'bg-blue-100 text-blue-800 border-blue-200'
    case 'In Review':
      return 'bg-amber-100 text-amber-800 border-amber-200'
    case 'Blocked':
      return 'bg-rose-100 text-rose-800 border-rose-200'
    default:
      return 'bg-stone-100 text-stone-700 border-stone-200'
  }
}

function getPriorityClass(priority) {
  switch (priority) {
    case 'Urgent':
      return 'bg-rose-50 text-rose-700 border-rose-300'
    case 'High':
      return 'bg-orange-50 text-orange-700 border-orange-300'
    case 'Normal':
      return 'bg-blue-50 text-blue-700 border-blue-200'
    default:
      return 'bg-stone-50 text-stone-600 border-stone-200'
  }
}
</script>
