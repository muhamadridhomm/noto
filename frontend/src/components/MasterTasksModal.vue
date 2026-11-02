<template>
  <div
    v-if="notesStore.isMasterTasksOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-stone-900/40 backdrop-blur-xs select-none"
    @click.self="notesStore.isMasterTasksOpen = false"
  >
    <div class="w-full max-w-5xl bg-white rounded-2xl shadow-2xl h-[90vh] flex flex-col overflow-hidden border border-stone-200 animate-in fade-in zoom-in-95 duration-150">
      <!-- Modal Top Header -->
      <div class="px-6 py-4 border-b border-stone-200 bg-stone-50/90 flex flex-wrap items-center justify-between gap-3">
        <div class="flex items-center gap-3">
          <div class="p-2 rounded-xl bg-gradient-to-br from-brand-500 to-indigo-600 text-white shadow-xs">
            <CalendarDays class="w-5 h-5" />
          </div>
          <div>
            <h3 class="text-sm font-bold text-stone-900 flex items-center gap-2">
              <span>Combined Master Timeline & Task Hub</span>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-brand-50 text-brand-700 border border-brand-200 font-semibold">
                {{ allNotesList.length }} Notes • {{ allFoldersList.length }} Folders
              </span>
            </h3>
            <p class="text-xs text-stone-500">
              Sinkronisasi roadmap, target milestones, dan status tugas terintegrasi antar catatan dan folder.
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <!-- View Switcher: Combined Timeline vs Flat Task List -->
          <div class="flex bg-stone-200/80 p-0.5 rounded-lg text-xs font-medium text-stone-600">
            <button
              @click="activeView = 'timeline'"
              :class="['px-3 py-1 rounded-md transition text-xs flex items-center gap-1.5', activeView === 'timeline' ? 'bg-white text-stone-900 shadow-2xs font-semibold' : 'hover:text-stone-900']"
              title="View combined Gantt & Roadmap Timeline across notes"
            >
              <CalendarDays class="w-3.5 h-3.5 text-brand-600" />
              <span>Combined Timeline</span>
            </button>
            <button
              @click="activeView = 'list'"
              :class="['px-3 py-1 rounded-md transition text-xs flex items-center gap-1.5', activeView === 'list' ? 'bg-white text-stone-900 shadow-2xs font-semibold' : 'hover:text-stone-900']"
              title="View as detailed task list"
            >
              <List class="w-3.5 h-3.5" />
              <span>Task List</span>
            </button>
          </div>

          <!-- Export Dropdown -->
          <div class="relative">
            <button
              @click="isExportMenuOpen = !isExportMenuOpen"
              class="px-2.5 py-1 bg-white hover:bg-stone-100 border border-stone-200 text-stone-700 font-semibold rounded-lg text-xs flex items-center gap-1.5 shadow-2xs transition cursor-pointer"
              title="Export Timeline & Tasks to HTML or Excel"
            >
              <Download class="w-3.5 h-3.5 text-brand-600" />
              <span>Export</span>
              <ChevronDown class="w-3 h-3 text-stone-400" />
            </button>

            <!-- Dropdown Menu -->
            <div
              v-if="isExportMenuOpen"
              class="absolute right-0 mt-1.5 w-60 bg-white border border-stone-200 rounded-xl shadow-xl py-1.5 z-50 text-xs animate-in fade-in zoom-in-95 duration-100"
            >
              <div class="px-3 py-1 text-[10px] font-bold text-stone-400 uppercase tracking-wider">
                Pilihan Format Export
              </div>

              <button
                @click="exportTimeline('html', 'filtered')"
                :disabled="isExporting"
                class="w-full px-3 py-2 text-left hover:bg-brand-50 hover:text-brand-700 flex items-center gap-2.5 transition cursor-pointer disabled:opacity-50"
              >
                <Globe class="w-4 h-4 text-brand-600 shrink-0" />
                <div>
                  <div class="font-semibold text-stone-800">Export Standalone HTML</div>
                  <div class="text-[10px] text-stone-400">Interaktif, siap share & print ke PDF</div>
                </div>
              </button>

              <button
                @click="exportTimeline('excel', 'filtered')"
                :disabled="isExporting"
                class="w-full px-3 py-2 text-left hover:bg-emerald-50 hover:text-emerald-700 flex items-center gap-2.5 transition cursor-pointer disabled:opacity-50"
              >
                <FileSpreadsheet class="w-4 h-4 text-emerald-600 shrink-0" />
                <div>
                  <div class="font-semibold text-stone-800">Export Excel (.xlsx)</div>
                  <div class="text-[10px] text-stone-400">3 Sheet: Tasks, Targets, Summary</div>
                </div>
              </button>

              <div class="border-t border-stone-100 my-1"></div>

              <div class="px-3 py-1 text-[10px] text-stone-400">
                Scope: Sesuai filter aktif ({{ filteredTasks.length }} tugas)
              </div>
            </div>
          </div>

          <button
            @click="notesStore.isMasterTasksOpen = false"
            class="text-stone-400 hover:text-stone-700 p-1.5 rounded-md hover:bg-stone-200/60 transition"
          >
            <X class="w-5 h-5" />
          </button>
        </div>
      </div>

      <!-- Filter Sub-Toolbar -->
      <div class="px-6 py-2.5 border-b border-stone-200/80 bg-white flex flex-wrap items-center justify-between gap-3 text-xs">
        <div class="flex items-center gap-2 flex-wrap flex-1">
          <!-- Search input -->
          <div class="relative min-w-[180px] max-w-xs">
            <Search class="w-3.5 h-3.5 text-stone-400 absolute left-2.5 top-2.5" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search tasks, notes, groups..."
              class="w-full pl-8 pr-3 py-1 bg-stone-100 border border-stone-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-brand-500 text-xs"
            />
          </div>

          <!-- Filter by Folder -->
          <select
            v-if="allFoldersList.length > 0"
            v-model="filterFolder"
            class="text-[11px] font-medium bg-stone-100 border border-stone-200 rounded-lg px-2.5 py-1 text-stone-700 focus:outline-none"
          >
            <option value="all">Semua Folder ({{ allFoldersList.length }} Folders)</option>
            <option v-for="f in allFoldersList" :key="f.id" :value="f.id">
              {{ f.name }}
            </option>
          </select>

          <!-- Filter by Parent Note -->
          <select
            v-model="filterNote"
            class="text-[11px] font-medium bg-stone-100 border border-stone-200 rounded-lg px-2.5 py-1 text-stone-700 focus:outline-none"
          >
            <option value="all">Semua Catatan ({{ allNotesList.length }} Notes)</option>
            <option v-for="n in allNotesList" :key="n.id" :value="n.id">
              {{ n.title }}
            </option>
          </select>

          <!-- Filter by Group -->
          <select
            v-if="allGroupsList.length > 0"
            v-model="filterGroup"
            class="text-[11px] font-medium bg-stone-100 border border-stone-200 rounded-lg px-2.5 py-1 text-stone-700 focus:outline-none"
          >
            <option value="all">Semua Grup ({{ allGroupsList.length }} Groups)</option>
            <option v-for="g in allGroupsList" :key="g" :value="g">
              {{ g }}
            </option>
          </select>
        </div>

        <div class="flex items-center gap-2">
          <!-- Filter status tabs -->
          <div class="flex bg-stone-100 p-0.5 rounded-lg text-xs font-medium text-stone-600">
            <button
              @click="filterStatus = 'all'"
              :class="['px-2.5 py-0.5 rounded-md transition text-[11px]', filterStatus === 'all' ? 'bg-white text-stone-900 shadow-2xs font-semibold' : 'hover:text-stone-900']"
            >
              All ({{ notesStore.allMasterTasks.length }})
            </button>
            <button
              @click="filterStatus = 'active'"
              :class="['px-2.5 py-0.5 rounded-md transition text-[11px]', filterStatus === 'active' ? 'bg-white text-stone-900 shadow-2xs font-semibold' : 'hover:text-stone-900']"
            >
              Active ({{ activeCount }})
            </button>
            <button
              @click="filterStatus = 'completed'"
              :class="['px-2.5 py-0.5 rounded-md transition text-[11px]', filterStatus === 'completed' ? 'bg-white text-stone-900 shadow-2xs font-semibold' : 'hover:text-stone-900']"
            >
              Done ({{ completedCount }})
            </button>
          </div>

          <!-- Priority filter -->
          <select
            v-model="filterPriority"
            class="text-[11px] font-medium bg-stone-100 border border-stone-200 rounded-lg px-2 py-0.5 text-stone-700 focus:outline-none"
          >
            <option value="all">All Priorities</option>
            <option value="Urgent">Urgent</option>
            <option value="High">High</option>
            <option value="Normal">Normal</option>
            <option value="Low">Low</option>
          </select>
        </div>
      </div>

      <!-- ========================================================= -->
      <!-- TAB 1: COMBINED TIMELINE & GANTT ROADMAP VIEW             -->
      <!-- ========================================================= -->
      <div v-if="activeView === 'timeline'" class="flex-1 overflow-y-auto p-6 bg-stone-50/50 space-y-5">
        <!-- Milestone Goals Banner (Dynamic CRUD-able Targets) -->
        <div class="space-y-2.5">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-xs font-bold text-stone-700 uppercase tracking-wider flex items-center gap-1.5">
                <Target class="w-3.5 h-3.5 text-brand-600" />
                <span>Target Milestones & Phase Goals</span>
              </span>
              <span class="text-[10px] font-mono px-2 py-0.2 rounded-full bg-stone-200 text-stone-600 font-semibold">
                {{ activeTargets.length }} Goals
              </span>
            </div>

            <button
              @click="openAddMasterTargetModal"
              class="text-xs text-brand-600 hover:text-brand-800 font-semibold flex items-center gap-1 hover:underline cursor-pointer"
            >
              <Plus class="w-3.5 h-3.5" />
              <span>+ Add Target Goal</span>
            </button>
          </div>

          <!-- Target Cards Grid -->
          <div v-if="activeTargets.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            <div
              v-for="tgt in activeTargets"
              :key="tgt.id"
              class="p-3 bg-white border border-stone-200/90 hover:border-brand-300 rounded-xl flex flex-col justify-between shadow-2xs transition group"
            >
              <div>
                <div class="flex items-start justify-between gap-2">
                  <span class="text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider bg-brand-50 text-brand-700 border border-brand-200">
                    {{ tgt.badge || 'Milestone' }}
                  </span>
                  <div class="flex items-center gap-1">
                    <span v-if="tgt.date" class="text-[10px] font-mono font-medium text-stone-500 bg-stone-100 px-1.5 py-0.2 rounded">
                      {{ tgt.date }}
                    </span>
                    <button
                      @click="openEditMasterTargetModal(tgt)"
                      title="Edit Target"
                      class="opacity-0 group-hover:opacity-100 p-1 text-stone-400 hover:text-brand-600 hover:bg-stone-100 rounded transition cursor-pointer"
                    >
                      <Pencil class="w-3 h-3" />
                    </button>
                    <button
                      @click="deleteMasterTarget(tgt)"
                      title="Delete Target"
                      class="opacity-0 group-hover:opacity-100 p-1 text-stone-400 hover:text-rose-600 hover:bg-rose-50 rounded transition cursor-pointer"
                    >
                      <Trash2 class="w-3 h-3" />
                    </button>
                  </div>
                </div>

                <h4 class="text-xs font-bold text-stone-900 mt-2 leading-snug">
                  {{ tgt.title }}
                </h4>

                <p v-if="tgt.description" class="text-[11px] text-stone-600 mt-1 leading-snug line-clamp-2">
                  {{ tgt.description }}
                </p>
              </div>

              <!-- Target Source Note Link & Folder -->
              <div class="flex items-center justify-between text-[10px] text-stone-400 mt-3 pt-2 border-t border-stone-100">
                <button
                  @click="jumpToNote(tgt.note_id)"
                  class="font-semibold text-brand-600 hover:underline truncate max-w-[170px] flex items-center gap-1 text-left cursor-pointer"
                  title="Buka Catatan"
                >
                  <FileText class="w-3 h-3 text-brand-500 shrink-0" />
                  <span class="truncate">{{ tgt.note_title }}</span>
                  <ArrowRight class="w-2.5 h-2.5" />
                </button>
                <span v-if="tgt.folder_name" class="truncate max-w-[110px] text-stone-400 flex items-center gap-1">
                  <Folder class="w-2.5 h-2.5 text-stone-400" />
                  <span>{{ tgt.folder_name }}</span>
                </span>
              </div>
            </div>
          </div>

          <!-- Empty State for Targets -->
          <div
            v-else
            @click="openAddMasterTargetModal"
            class="p-4 border border-dashed border-stone-200 hover:border-brand-400 bg-stone-50/70 hover:bg-stone-100/60 rounded-xl text-center cursor-pointer transition flex items-center justify-center gap-2 text-xs text-stone-500 font-medium"
          >
            <Plus class="w-4 h-4 text-brand-600" />
            <span>Belum ada Target Goal. Klik untuk menambah Target Milestone (Target Sprint, Deadline Integrasi, dsb).</span>
          </div>
        </div>

        <!-- Timeline Mode Sub-Selector -->
        <div class="flex items-center justify-between pb-1 text-xs">
          <div class="flex items-center gap-2 flex-wrap">
            <span class="font-semibold text-stone-700">Display Swimlanes:</span>
            <div class="flex bg-stone-200/80 p-0.5 rounded-lg text-xs font-medium text-stone-600">
              <button
                @click="timelineGrouping = 'by_note'"
                :class="['px-2.5 py-0.5 rounded transition text-[11px]', timelineGrouping === 'by_note' ? 'bg-white text-stone-900 shadow-2xs font-semibold' : 'hover:text-stone-900']"
              >
                Per Catatan ({{ activeNotesList.length }})
              </button>
              <button
                @click="timelineGrouping = 'by_folder'"
                :class="['px-2.5 py-0.5 rounded transition text-[11px]', timelineGrouping === 'by_folder' ? 'bg-white text-stone-900 shadow-2xs font-semibold' : 'hover:text-stone-900']"
              >
                Per Folder ({{ activeFoldersList.length }})
              </button>
              <button
                @click="timelineGrouping = 'by_group'"
                :class="['px-2.5 py-0.5 rounded transition text-[11px]', timelineGrouping === 'by_group' ? 'bg-white text-stone-900 shadow-2xs font-semibold' : 'hover:text-stone-900']"
              >
                Per Grup ({{ activeGroupsList.length }})
              </button>
              <button
                @click="timelineGrouping = 'chronological'"
                :class="['px-2.5 py-0.5 rounded transition text-[11px]', timelineGrouping === 'chronological' ? 'bg-white text-stone-900 shadow-2xs font-semibold' : 'hover:text-stone-900']"
              >
                Jadwal Kronologis
              </button>
            </div>
          </div>

          <div class="text-[11px] text-stone-400 font-mono">
            Showing {{ filteredTasks.length }} tasks across {{ activeNotesList.length }} notes
          </div>
        </div>

        <!-- ================================================= -->
        <!-- TIMELINE CASE 1: SWIMLANES BY NOTE               -->
        <!-- ================================================= -->
        <div v-if="timelineGrouping === 'by_note'" class="space-y-4">
          <div
            v-for="note in activeNotesList"
            :key="note.id"
            class="bg-white rounded-xl border border-stone-200 shadow-2xs overflow-hidden"
          >
            <!-- Swimlane Note Header -->
            <div class="px-4 py-3 bg-stone-100/70 border-b border-stone-200/80 flex items-center justify-between gap-2">
              <div class="flex items-center gap-2.5 min-w-0 flex-1">
                <span class="w-2.5 h-2.5 rounded-full bg-brand-600 shrink-0"></span>
                <span class="text-xs font-bold text-stone-900 tracking-tight truncate">{{ note.title }}</span>
                <span v-if="note.folder_name" class="text-[10px] text-stone-500 bg-stone-200/70 px-2 py-0.2 rounded-md truncate max-w-[120px] flex items-center gap-1">
                  <Folder class="w-2.5 h-2.5 text-stone-400" />
                  <span>{{ note.folder_name }}</span>
                </span>
                <span class="text-[10px] font-mono px-2 py-0.2 rounded-full bg-stone-200/80 text-stone-600 font-semibold shrink-0">
                  {{ getTasksByNote(note.id).filter(t => t.done).length }}/{{ getTasksByNote(note.id).length }} done
                </span>
              </div>

              <div class="flex items-center gap-2 shrink-0">
                <button
                  @click="openAddTaskModal(note.id)"
                  class="text-[11px] font-medium text-stone-600 hover:text-brand-700 bg-white hover:bg-stone-50 border border-stone-200 rounded px-2 py-0.5 flex items-center gap-1 transition cursor-pointer"
                >
                  <Plus class="w-3 h-3" />
                  <span>Tambah Tugas</span>
                </button>
                <button
                  @click="jumpToNote(note.id)"
                  class="text-[11px] font-semibold text-brand-600 hover:text-brand-800 hover:underline flex items-center gap-1 cursor-pointer"
                >
                  <span>Buka Catatan</span>
                  <ArrowRight class="w-3 h-3" />
                </button>
              </div>
            </div>

            <!-- Task List inside Note Swimlane -->
            <div class="p-3 space-y-2">
              <div v-if="getTasksByNote(note.id).length === 0" class="py-4 text-center text-xs text-stone-400 italic">
                Tidak ada tugas yang sesuai dengan filter ini.
              </div>

              <div
                v-for="task in getSortedTasksByNote(note.id)"
                :key="task.id"
                class="p-2.5 rounded-lg border border-stone-200/80 hover:border-stone-300 hover:bg-stone-50/70 transition flex items-center justify-between gap-3 text-xs group"
                :class="{ 'bg-stone-50/40 opacity-70': task.done }"
              >
                <div class="flex items-center gap-2.5 min-w-0 flex-1">
                  <button
                    @click="toggleTask(task)"
                    class="w-4 h-4 rounded border flex items-center justify-center shrink-0 cursor-pointer transition"
                    :class="task.done ? 'bg-emerald-600 border-emerald-600 text-white' : 'border-stone-300 bg-white hover:border-brand-500'"
                    title="Toggle Task Done"
                  >
                    <Check v-if="task.done" class="w-3 h-3 stroke-[3]" />
                  </button>

                  <div class="min-w-0 flex-1">
                    <div
                      class="font-medium text-stone-900 truncate"
                      :class="{ 'line-through text-stone-400': task.done }"
                    >
                      {{ task.title }}
                    </div>
                    <div v-if="task.group" class="flex items-center gap-1 mt-0.5">
                      <span class="text-[9px] px-1.5 py-0.2 rounded bg-brand-50 text-brand-700 border border-brand-200 font-medium">
                        {{ task.group }}
                      </span>
                    </div>
                    <div
                      v-if="task.notes"
                      @click="openTaskNoteModal(task)"
                      class="text-[10px] text-stone-500 font-mono mt-0.5 truncate max-w-xl flex items-center gap-1.5 cursor-pointer hover:text-brand-700"
                      title="Klik untuk membuka catatan teknis di jendela baru"
                    >
                      <StickyNote class="w-2.5 h-2.5 text-brand-600 shrink-0" />
                      <span class="text-stone-700 font-medium shrink-0">Catatan:</span>
                      <span class="truncate">{{ task.notes.replace(/\n/g, ' ') }}</span>
                    </div>
                  </div>
                </div>

                <div class="flex items-center gap-2 shrink-0">
                  <!-- Note Button -->
                  <button
                    @click="openTaskNoteModal(task)"
                    :title="task.notes ? 'Buka Catatan Teknis (Sudah Terisi)' : 'Sisipkan Catatan / Spek (Buka Jendela Baru)'"
                    class="px-1.5 py-0.5 rounded transition flex items-center gap-1 text-[10px] cursor-pointer"
                    :class="task.notes ? 'bg-brand-50 text-brand-700 border border-brand-200 font-semibold' : 'text-stone-400 hover:text-stone-700 hover:bg-stone-100 border border-transparent'"
                  >
                    <FileText class="w-3.5 h-3.5" :class="task.notes ? 'text-brand-600' : 'text-stone-400'" />
                    <span v-if="task.notes" class="hidden sm:inline">Note</span>
                  </button>

                  <!-- Status dropdown -->
                  <select
                    :value="task.status"
                    @change="e => updateTaskStatus(task, e.target.value)"
                    class="text-[10px] font-medium px-2 py-0.5 rounded-full border cursor-pointer focus:outline-none"
                    :class="getStatusBadgeClass(task.status)"
                  >
                    <option value="To Do">To Do</option>
                    <option value="In Progress">In Progress</option>
                    <option value="In Review">In Review</option>
                    <option value="Done">Done</option>
                    <option value="Blocked">Blocked</option>
                  </select>

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

                  <button
                    @click="deleteTask(task)"
                    class="opacity-0 group-hover:opacity-100 p-1 text-stone-400 hover:text-rose-600 hover:bg-rose-50 rounded transition cursor-pointer"
                    title="Hapus Tugas"
                  >
                    <Trash2 class="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ================================================= -->
        <!-- TIMELINE CASE 2: SWIMLANES BY FOLDER             -->
        <!-- ================================================= -->
        <div v-else-if="timelineGrouping === 'by_folder'" class="space-y-4">
          <div
            v-for="f in activeFoldersList"
            :key="f.id"
            class="bg-white rounded-xl border border-stone-200 shadow-2xs overflow-hidden"
          >
            <!-- Swimlane Folder Header -->
            <div class="px-4 py-3 bg-stone-100/70 border-b border-stone-200/80 flex items-center justify-between">
              <div class="flex items-center gap-2 min-w-0">
                <Folder class="w-4 h-4 text-emerald-600 shrink-0" />
                <span class="text-xs font-bold text-stone-900 tracking-tight truncate">{{ f.name }}</span>
                <span class="text-[10px] font-mono px-2 py-0.2 rounded-full bg-stone-200 text-stone-600 font-semibold shrink-0">
                  {{ getTasksByFolder(f.id).filter(t => t.done).length }}/{{ getTasksByFolder(f.id).length }} done
                </span>
              </div>
            </div>

            <!-- Tasks in Folder Swimlane -->
            <div class="p-3 space-y-2">
              <div v-if="getTasksByFolder(f.id).length === 0" class="py-4 text-center text-xs text-stone-400 italic">
                Tidak ada tugas di folder ini.
              </div>

              <div
                v-for="task in getSortedTasksByFolder(f.id)"
                :key="task.id"
                class="p-2.5 rounded-lg border border-stone-200/80 hover:border-stone-300 hover:bg-stone-50/70 transition flex items-center justify-between gap-3 text-xs group"
                :class="{ 'bg-stone-50/40 opacity-70': task.done }"
              >
                <div class="flex items-center gap-2.5 min-w-0 flex-1">
                  <button
                    @click="toggleTask(task)"
                    class="w-4 h-4 rounded border flex items-center justify-center shrink-0 cursor-pointer transition"
                    :class="task.done ? 'bg-emerald-600 border-emerald-600 text-white' : 'border-stone-300 bg-white hover:border-brand-500'"
                  >
                    <Check v-if="task.done" class="w-3 h-3 stroke-[3]" />
                  </button>

                  <div class="min-w-0 flex-1">
                    <div
                      class="font-medium text-stone-900 truncate"
                      :class="{ 'line-through text-stone-400': task.done }"
                    >
                      {{ task.title }}
                    </div>
                    <div class="flex items-center gap-1.5 mt-0.5 text-[10px] text-stone-400 flex-wrap">
                      <span>Source:</span>
                      <button
                        @click="jumpToNote(task.note_id)"
                        class="font-semibold text-brand-600 hover:underline truncate max-w-[200px] cursor-pointer"
                      >
                        {{ task.note_title }} →
                      </button>
                      <span v-if="task.group" class="text-stone-300">•</span>
                      <span v-if="task.group" class="px-1.5 py-0.2 rounded bg-brand-50 text-brand-700 border border-brand-200 text-[9px] font-medium truncate max-w-[120px]">
                        {{ task.group }}
                      </span>
                    </div>
                    <div
                      v-if="task.notes"
                      @click="openTaskNoteModal(task)"
                      class="text-[10px] text-stone-500 font-mono mt-0.5 truncate max-w-xl flex items-center gap-1.5 cursor-pointer hover:text-brand-700"
                      title="Klik untuk membuka catatan teknis di jendela baru"
                    >
                      <StickyNote class="w-2.5 h-2.5 text-brand-600 shrink-0" />
                      <span class="text-stone-700 font-medium shrink-0">Catatan:</span>
                      <span class="truncate">{{ task.notes.replace(/\n/g, ' ') }}</span>
                    </div>
                  </div>
                </div>

                <div class="flex items-center gap-2 shrink-0">
                  <!-- Note Button -->
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
                    :value="task.status"
                    @change="e => updateTaskStatus(task, e.target.value)"
                    class="text-[10px] font-medium px-2 py-0.5 rounded-full border cursor-pointer focus:outline-none"
                    :class="getStatusBadgeClass(task.status)"
                  >
                    <option value="To Do">To Do</option>
                    <option value="In Progress">In Progress</option>
                    <option value="In Review">In Review</option>
                    <option value="Done">Done</option>
                    <option value="Blocked">Blocked</option>
                  </select>

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

                  <button
                    @click="deleteTask(task)"
                    class="opacity-0 group-hover:opacity-100 p-1 text-stone-400 hover:text-rose-600 hover:bg-rose-50 rounded transition cursor-pointer"
                    title="Hapus Tugas"
                  >
                    <Trash2 class="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ================================================= -->
        <!-- TIMELINE CASE 3: SWIMLANES BY GROUP / TOPIC      -->
        <!-- ================================================= -->
        <div v-else-if="timelineGrouping === 'by_group'" class="space-y-4">
          <div
            v-for="grp in activeGroupsList"
            :key="grp"
            class="bg-white rounded-xl border border-stone-200 shadow-2xs overflow-hidden"
          >
            <!-- Swimlane Group Header -->
            <div class="px-4 py-3 bg-stone-100/70 border-b border-stone-200/80 flex items-center justify-between">
              <div class="flex items-center gap-2 min-w-0">
                <Tag class="w-3.5 h-3.5 text-indigo-600 shrink-0" />
                <span class="text-xs font-bold text-stone-900 tracking-tight truncate">{{ grp }}</span>
                <span class="text-[10px] font-mono px-2 py-0.2 rounded-full bg-stone-200 text-stone-600 font-semibold shrink-0">
                  {{ getTasksByGroup(grp).filter(t => t.done).length }}/{{ getTasksByGroup(grp).length }} done
                </span>
              </div>
            </div>

            <!-- Tasks in this Group Swimlane -->
            <div class="p-3 space-y-2">
              <div
                v-for="task in getSortedTasksByGroup(grp)"
                :key="task.id"
                class="p-2.5 rounded-lg border border-stone-200/80 hover:border-stone-300 hover:bg-stone-50/70 transition flex items-center justify-between gap-3 text-xs group"
                :class="{ 'bg-stone-50/40 opacity-70': task.done }"
              >
                <div class="flex items-center gap-2.5 min-w-0 flex-1">
                  <button
                    @click="toggleTask(task)"
                    class="w-4 h-4 rounded border flex items-center justify-center shrink-0 cursor-pointer transition"
                    :class="task.done ? 'bg-emerald-600 border-emerald-600 text-white' : 'border-stone-300 bg-white hover:border-brand-500'"
                  >
                    <Check v-if="task.done" class="w-3 h-3 stroke-[3]" />
                  </button>

                  <div class="min-w-0 flex-1">
                    <div
                      class="font-medium text-stone-900 truncate"
                      :class="{ 'line-through text-stone-400': task.done }"
                    >
                      {{ task.title }}
                    </div>
                    <div class="flex items-center gap-1.5 mt-0.5 text-[10px] text-stone-400">
                      <span>Source:</span>
                      <button
                        @click="jumpToNote(task.note_id)"
                        class="font-semibold text-brand-600 hover:underline truncate max-w-[200px] cursor-pointer"
                      >
                        {{ task.note_title }} →
                      </button>
                      <span v-if="task.folder_name" class="text-stone-300">•</span>
                      <span v-if="task.folder_name" class="text-stone-400">
                        {{ task.folder_name }}
                      </span>
                    </div>
                    <div
                      v-if="task.notes"
                      @click="openTaskNoteModal(task)"
                      class="text-[10px] text-stone-500 font-mono mt-0.5 truncate max-w-xl flex items-center gap-1.5 cursor-pointer hover:text-brand-700"
                      title="Klik untuk membuka catatan teknis di jendela baru"
                    >
                      <StickyNote class="w-2.5 h-2.5 text-brand-600 shrink-0" />
                      <span class="text-stone-700 font-medium shrink-0">Catatan:</span>
                      <span class="truncate">{{ task.notes.replace(/\n/g, ' ') }}</span>
                    </div>
                  </div>
                </div>

                <div class="flex items-center gap-2 shrink-0">
                  <!-- Note Button -->
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
                    :value="task.status"
                    @change="e => updateTaskStatus(task, e.target.value)"
                    class="text-[10px] font-medium px-2 py-0.5 rounded-full border cursor-pointer focus:outline-none"
                    :class="getStatusBadgeClass(task.status)"
                  >
                    <option value="To Do">To Do</option>
                    <option value="In Progress">In Progress</option>
                    <option value="In Review">In Review</option>
                    <option value="Done">Done</option>
                    <option value="Blocked">Blocked</option>
                  </select>

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

                  <button
                    @click="deleteTask(task)"
                    class="opacity-0 group-hover:opacity-100 p-1 text-stone-400 hover:text-rose-600 hover:bg-rose-50 rounded transition cursor-pointer"
                    title="Hapus Tugas"
                  >
                    <Trash2 class="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Ungrouped Tasks Swimlane (if any exist) -->
          <div
            v-if="tasksWithoutGroup.length > 0"
            class="bg-white rounded-xl border border-stone-200 shadow-2xs overflow-hidden"
          >
            <div class="px-4 py-3 bg-stone-100/70 border-b border-stone-200/80 flex items-center justify-between">
              <div class="flex items-center gap-2 min-w-0">
                <span class="w-2.5 h-2.5 rounded-full bg-stone-400 shrink-0"></span>
                <span class="text-xs font-bold text-stone-700 tracking-tight">Tanpa Grup (Ungrouped)</span>
                <span class="text-[10px] font-mono px-2 py-0.2 rounded-full bg-stone-200 text-stone-600 font-semibold shrink-0">
                  {{ tasksWithoutGroup.filter(t => t.done).length }}/{{ tasksWithoutGroup.length }} done
                </span>
              </div>
            </div>
            <div class="p-3 space-y-2">
              <div
                v-for="task in tasksWithoutGroup"
                :key="task.id"
                class="p-2.5 rounded-lg border border-stone-200/80 hover:border-stone-300 hover:bg-stone-50/70 transition flex items-center justify-between gap-3 text-xs group"
                :class="{ 'bg-stone-50/40 opacity-70': task.done }"
              >
                <div class="flex items-center gap-2.5 min-w-0 flex-1">
                  <button
                    @click="toggleTask(task)"
                    class="w-4 h-4 rounded border flex items-center justify-center shrink-0 cursor-pointer transition"
                    :class="task.done ? 'bg-emerald-600 border-emerald-600 text-white' : 'border-stone-300 bg-white hover:border-brand-500'"
                  >
                    <Check v-if="task.done" class="w-3 h-3 stroke-[3]" />
                  </button>
                  <div class="min-w-0 flex-1">
                    <div class="font-medium text-stone-900 truncate" :class="{ 'line-through text-stone-400': task.done }">
                      {{ task.title }}
                    </div>
                    <div class="flex items-center gap-1.5 mt-0.5 text-[10px] text-stone-400">
                      <span>Source:</span>
                      <button @click="jumpToNote(task.note_id)" class="font-semibold text-brand-600 hover:underline truncate max-w-[200px] cursor-pointer">
                        {{ task.note_title }} →
                      </button>
                    </div>
                    <div
                      v-if="task.notes"
                      @click="openTaskNoteModal(task)"
                      class="text-[10px] text-stone-500 font-mono mt-0.5 truncate max-w-xl flex items-center gap-1.5 cursor-pointer hover:text-brand-700"
                      title="Klik untuk membuka catatan teknis di jendela baru"
                    >
                      <StickyNote class="w-2.5 h-2.5 text-brand-600 shrink-0" />
                      <span class="text-stone-700 font-medium shrink-0">Catatan:</span>
                      <span class="truncate">{{ task.notes.replace(/\n/g, ' ') }}</span>
                    </div>
                  </div>
                </div>

                <div class="flex items-center gap-2 shrink-0">
                  <!-- Note Button -->
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
                    :value="task.status"
                    @change="e => updateTaskStatus(task, e.target.value)"
                    class="text-[10px] font-medium px-2 py-0.5 rounded-full border cursor-pointer focus:outline-none"
                    :class="getStatusBadgeClass(task.status)"
                  >
                    <option value="To Do">To Do</option>
                    <option value="In Progress">In Progress</option>
                    <option value="In Review">In Review</option>
                    <option value="Done">Done</option>
                    <option value="Blocked">Blocked</option>
                  </select>
                  <span class="text-[10px] font-medium px-1.5 py-0.5 rounded border" :class="getPriorityClass(task.priority)">
                    {{ task.priority }}
                  </span>
                  <span class="text-[10px] px-2 py-0.5 rounded-md border font-mono" :class="getRelativeDateBadge(task.due_date, task.done).class">
                    {{ getRelativeDateBadge(task.due_date, task.done).text }}
                  </span>
                  <button
                    @click="deleteTask(task)"
                    class="opacity-0 group-hover:opacity-100 p-1 text-stone-400 hover:text-rose-600 hover:bg-rose-50 rounded transition cursor-pointer"
                    title="Hapus Tugas"
                  >
                    <Trash2 class="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ================================================= -->
        <!-- TIMELINE CASE 4: CHRONOLOGICAL SCHEDULE          -->
        <!-- ================================================= -->
        <div v-else class="bg-white rounded-xl border border-stone-200 shadow-2xs divide-y divide-stone-100 overflow-hidden">
          <div v-if="chronologicalTasks.length === 0" class="py-12 text-center text-xs text-stone-400">
            Tidak ada tugas yang sesuai kriteria pencarian.
          </div>

          <div
            v-for="task in chronologicalTasks"
            :key="task.id"
            class="p-3.5 hover:bg-stone-50/80 transition flex items-center justify-between gap-3 text-xs group"
            :class="{ 'bg-stone-50/40 opacity-70': task.done }"
          >
            <div class="flex items-center gap-3 min-w-0 flex-1">
              <button
                @click="toggleTask(task)"
                class="w-4 h-4 rounded border flex items-center justify-center shrink-0 cursor-pointer transition"
                :class="task.done ? 'bg-emerald-600 border-emerald-600 text-white' : 'border-stone-300 bg-white hover:border-brand-500'"
              >
                <Check v-if="task.done" class="w-3 h-3 stroke-[3]" />
              </button>

                  <div class="min-w-0 flex-1">
                    <div
                      class="font-medium text-stone-900 truncate"
                      :class="{ 'line-through text-stone-400': task.done }"
                    >
                      {{ task.title }}
                    </div>
                    <div class="flex items-center gap-2 mt-0.5 text-[10px] text-stone-400 flex-wrap">
                      <span>From:</span>
                      <button
                        @click="jumpToNote(task.note_id)"
                        class="font-semibold text-brand-600 hover:underline truncate max-w-[200px] cursor-pointer"
                      >
                        {{ task.note_title }} →
                      </button>
                      <span v-if="task.folder_name" class="text-stone-300">•</span>
                      <span v-if="task.folder_name" class="text-stone-400">
                        {{ task.folder_name }}
                      </span>
                      <span v-if="task.group" class="text-stone-300">•</span>
                      <span v-if="task.group" class="px-1.5 py-0.2 rounded bg-brand-50 text-brand-700 border border-brand-200 text-[9px] font-medium truncate max-w-[140px]">
                        {{ task.group }}
                      </span>
                    </div>
                    <div
                      v-if="task.notes"
                      @click="openTaskNoteModal(task)"
                      class="text-[10px] text-stone-500 font-mono mt-0.5 truncate max-w-xl flex items-center gap-1.5 cursor-pointer hover:text-brand-700"
                      title="Klik untuk membuka catatan teknis di jendela baru"
                    >
                      <StickyNote class="w-2.5 h-2.5 text-brand-600 shrink-0" />
                      <span class="text-stone-700 font-medium shrink-0">Catatan:</span>
                      <span class="truncate">{{ task.notes.replace(/\n/g, ' ') }}</span>
                    </div>
                  </div>
                </div>

                <div class="flex items-center gap-2 shrink-0">
                  <!-- Note Button -->
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
                :value="task.status"
                @change="e => updateTaskStatus(task, e.target.value)"
                class="text-[10px] font-medium px-2 py-0.5 rounded-full border cursor-pointer focus:outline-none"
                :class="getStatusBadgeClass(task.status)"
              >
                <option value="To Do">To Do</option>
                <option value="In Progress">In Progress</option>
                <option value="In Review">In Review</option>
                <option value="Done">Done</option>
                <option value="Blocked">Blocked</option>
              </select>

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

              <button
                @click="deleteTask(task)"
                class="opacity-0 group-hover:opacity-100 p-1 text-stone-400 hover:text-rose-600 hover:bg-rose-50 rounded transition cursor-pointer"
                title="Hapus Tugas"
              >
                <Trash2 class="w-3 h-3" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ========================================================= -->
      <!-- TAB 2: DETAILED FLAT TASK LIST VIEW                       -->
      <!-- ========================================================= -->
      <div v-else class="flex-1 overflow-y-auto divide-y divide-stone-100 p-6">
        <div v-if="filteredTasks.length === 0" class="py-16 text-center">
          <CheckSquare class="w-12 h-12 stroke-[1.2] mx-auto text-stone-300 mb-2" />
          <h4 class="text-xs font-semibold text-stone-700">No tasks found</h4>
          <p class="text-[11px] text-stone-400 mt-1">Sesuaikan kata kunci pencarian atau filter di atas.</p>
        </div>

        <div
          v-for="task in filteredTasks"
          :key="task.id"
          class="py-3 flex items-center justify-between gap-4 hover:bg-stone-50/60 px-3 rounded-lg transition text-xs group"
          :class="{ 'opacity-60': task.done }"
        >
          <!-- Left: Checkbox & Title & Parent Note Pill -->
          <div class="flex items-center gap-3 min-w-0 flex-1">
            <button
              @click="toggleTask(task)"
              class="w-4 h-4 rounded border flex items-center justify-center shrink-0 cursor-pointer transition"
              :class="task.done ? 'bg-emerald-600 border-emerald-600 text-white' : 'border-stone-300 bg-white hover:border-brand-500'"
            >
              <Check v-if="task.done" class="w-3 h-3 stroke-[3]" />
            </button>

            <div class="min-w-0 flex-1">
              <div
                class="font-medium text-stone-900 truncate"
                :class="{ 'line-through text-stone-400': task.done }"
              >
                {{ task.title }}
              </div>
              <div class="flex items-center gap-1.5 mt-0.5 text-[10px] text-stone-400 flex-wrap">
                <span>From:</span>
                <button
                  @click="jumpToNote(task.note_id)"
                  class="font-semibold text-brand-600 hover:underline truncate max-w-[200px] cursor-pointer"
                >
                  {{ task.note_title }} →
                </button>
                <span v-if="task.folder_name" class="text-stone-300">•</span>
                <span v-if="task.folder_name" class="text-stone-400">
                  {{ task.folder_name }}
                </span>
                <span v-if="task.group" class="text-stone-300">•</span>
                <span
                  v-if="task.group"
                  class="px-1.5 py-0.2 rounded bg-brand-50 text-brand-700 border border-brand-200 text-[9px] font-medium truncate max-w-[150px]"
                >
                  {{ task.group }}
                </span>
              </div>
              <div
                v-if="task.notes"
                @click="openTaskNoteModal(task)"
                class="text-[10px] text-stone-500 font-mono mt-0.5 truncate max-w-xl flex items-center gap-1.5 cursor-pointer hover:text-brand-700"
                title="Klik untuk membuka catatan teknis di jendela baru"
              >
                <StickyNote class="w-2.5 h-2.5 text-brand-600 shrink-0" />
                <span class="text-stone-700 font-medium shrink-0">Catatan:</span>
                <span class="truncate">{{ task.notes.replace(/\n/g, ' ') }}</span>
              </div>
            </div>
          </div>

          <!-- Right: Badges & Controls -->
          <div class="flex items-center gap-2 shrink-0">
            <!-- Note Button -->
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
              :value="task.status"
              @change="e => updateTaskStatus(task, e.target.value)"
              class="text-[10px] font-medium px-2 py-0.5 rounded-full border cursor-pointer focus:outline-none"
              :class="getStatusBadgeClass(task.status)"
            >
              <option value="To Do">To Do</option>
              <option value="In Progress">In Progress</option>
              <option value="In Review">In Review</option>
              <option value="Done">Done</option>
              <option value="Blocked">Blocked</option>
            </select>

            <span
              class="text-[10px] font-medium px-1.5 py-0.5 rounded border"
              :class="getPriorityClass(task.priority)"
            >
              {{ task.priority }}
            </span>

            <span
              v-if="task.due_date"
              class="text-[10px] font-mono text-stone-500 bg-stone-100 px-1.5 py-0.5 rounded"
            >
              {{ task.due_date }}
            </span>

            <button
              @click="deleteTask(task)"
              class="opacity-0 group-hover:opacity-100 p-1 text-stone-400 hover:text-rose-600 hover:bg-rose-50 rounded transition cursor-pointer"
              title="Hapus Tugas"
            >
              <Trash2 class="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>

      <!-- Footer Stats & Actions -->
      <div class="px-6 py-3 border-t border-stone-200 bg-stone-50 flex items-center justify-between text-xs text-stone-500">
        <div>
          <span>Menampilkan {{ filteredTasks.length }} dari {{ notesStore.allMasterTasks.length }} total tugas</span>
        </div>
        <div class="flex items-center gap-2">
          <!-- Quick Export Buttons -->
          <button
            @click="exportTimeline('html', 'filtered')"
            :disabled="isExporting"
            class="text-stone-700 hover:text-brand-700 bg-white hover:bg-stone-100 border border-stone-200 px-2.5 py-1 rounded-lg flex items-center gap-1.5 font-medium text-xs shadow-2xs transition cursor-pointer disabled:opacity-50"
            title="Download Standalone HTML Report"
          >
            <Globe class="w-3.5 h-3.5 text-brand-600" />
            <span>HTML</span>
          </button>
          <button
            @click="exportTimeline('excel', 'filtered')"
            :disabled="isExporting"
            class="text-stone-700 hover:text-emerald-700 bg-white hover:bg-stone-100 border border-stone-200 px-2.5 py-1 rounded-lg flex items-center gap-1.5 font-medium text-xs shadow-2xs transition cursor-pointer disabled:opacity-50"
            title="Download Excel Spreadsheet (.xlsx)"
          >
            <FileSpreadsheet class="w-3.5 h-3.5 text-emerald-600" />
            <span>Excel</span>
          </button>

          <button
            @click="openAddTaskModal()"
            class="text-stone-700 hover:text-brand-700 bg-white hover:bg-stone-100 border border-stone-200 px-3 py-1 rounded-lg flex items-center gap-1.5 font-medium text-xs shadow-2xs transition cursor-pointer"
          >
            <Plus class="w-3.5 h-3.5 text-brand-600" />
            <span>+ Tambah Tugas Baru</span>
          </button>
          <button
            @click="notesStore.fetchAllTasks()"
            class="text-brand-600 hover:underline flex items-center gap-1 font-medium text-xs cursor-pointer"
          >
            <RefreshCw class="w-3 h-3" />
            <span>Refresh Data</span>
          </button>
        </div>
      </div>
    </div>

    <!-- ========================================================= -->
    <!-- MODAL: ADD / EDIT TARGET MILESTONE                        -->
    <!-- ========================================================= -->
    <div
      v-if="isTargetModalOpen"
      class="fixed inset-0 z-60 flex items-center justify-center p-4 bg-stone-900/50 backdrop-blur-xs"
      @click.self="isTargetModalOpen = false"
    >
      <div class="w-full max-w-md bg-white rounded-xl shadow-2xl border border-stone-200 p-5 space-y-4 animate-in fade-in zoom-in-95 duration-100">
        <div class="flex items-center justify-between border-b border-stone-200 pb-3">
          <div class="flex items-center gap-2">
            <Target class="w-4 h-4 text-brand-600" />
            <h3 class="text-xs font-bold text-stone-900">
              {{ targetModalMode === 'add' ? 'Tambah Target Milestone Baru' : 'Edit Target Milestone' }}
            </h3>
          </div>
          <button @click="isTargetModalOpen = false" class="text-stone-400 hover:text-stone-600">
            <X class="w-4 h-4" />
          </button>
        </div>

        <form @submit.prevent="saveTargetModal" class="space-y-3 text-xs">
          <div>
            <label class="block font-semibold text-stone-700 mb-1">Catatan Sumber (Target Note)</label>
            <select
              v-model="targetForm.note_id"
              :disabled="targetModalMode === 'edit'"
              class="w-full px-2.5 py-1.5 bg-stone-50 border border-stone-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-brand-500 text-xs"
              required
            >
              <option v-for="n in allNotesList" :key="n.id" :value="n.id">
                {{ n.title }}
              </option>
            </select>
          </div>

          <div>
            <label class="block font-semibold text-stone-700 mb-1">Judul Target / Milestone</label>
            <input
              v-model="targetForm.title"
              type="text"
              placeholder="Contoh: Sprint 1 Launch, Deadline Integrasi, dsb"
              class="w-full px-2.5 py-1.5 bg-stone-50 border border-stone-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-brand-500 text-xs"
              required
            />
          </div>

          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="block font-semibold text-stone-700 mb-1">Kategori / Badge</label>
              <input
                v-model="targetForm.badge"
                type="text"
                placeholder="Milestone, Integrasi, etc."
                class="w-full px-2.5 py-1.5 bg-stone-50 border border-stone-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-brand-500 text-xs"
              />
            </div>
            <div>
              <label class="block font-semibold text-stone-700 mb-1">Tanggal Deadline</label>
              <input
                v-model="targetForm.date"
                type="date"
                class="w-full px-2.5 py-1.5 bg-stone-50 border border-stone-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-brand-500 text-xs"
              />
            </div>
          </div>

          <div>
            <label class="block font-semibold text-stone-700 mb-1">Deskripsi Singkat / Key Deliverables</label>
            <textarea
              v-model="targetForm.description"
              rows="3"
              placeholder="Keterangan pencapaian target, deliverables utama, dsb."
              class="w-full px-2.5 py-1.5 bg-stone-50 border border-stone-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-brand-500 text-xs resize-none"
            ></textarea>
          </div>

          <div class="flex items-center justify-end gap-2 pt-2 border-t border-stone-200">
            <button
              type="button"
              @click="isTargetModalOpen = false"
              class="px-3 py-1.5 bg-stone-100 hover:bg-stone-200 text-stone-700 rounded-lg text-xs font-medium cursor-pointer"
            >
              Batal
            </button>
            <button
              type="submit"
              :disabled="isSavingTarget"
              class="px-4 py-1.5 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-semibold shadow-2xs transition cursor-pointer disabled:opacity-50"
            >
              {{ isSavingTarget ? 'Menyimpan...' : 'Simpan Target' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ========================================================= -->
    <!-- MODAL: ADD TASK DIALOG                                    -->
    <!-- ========================================================= -->
    <div
      v-if="isTaskModalOpen"
      class="fixed inset-0 z-60 flex items-center justify-center p-4 bg-stone-900/50 backdrop-blur-xs"
      @click.self="isTaskModalOpen = false"
    >
      <div class="w-full max-w-md bg-white rounded-xl shadow-2xl border border-stone-200 p-5 space-y-4 animate-in fade-in zoom-in-95 duration-100">
        <div class="flex items-center justify-between border-b border-stone-200 pb-3">
          <div class="flex items-center gap-2">
            <CheckSquare class="w-4 h-4 text-brand-600" />
            <h3 class="text-xs font-bold text-stone-900">Tambah Tugas Baru ke Catatan</h3>
          </div>
          <button @click="isTaskModalOpen = false" class="text-stone-400 hover:text-stone-600">
            <X class="w-4 h-4" />
          </button>
        </div>

        <form @submit.prevent="saveTaskModal" class="space-y-3 text-xs">
          <div>
            <label class="block font-semibold text-stone-700 mb-1">Catatan Tujuan</label>
            <select
              v-model="taskForm.note_id"
              class="w-full px-2.5 py-1.5 bg-stone-50 border border-stone-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-brand-500 text-xs"
              required
            >
              <option v-for="n in allNotesList" :key="n.id" :value="n.id">
                {{ n.title }}
              </option>
            </select>
          </div>

          <div>
            <label class="block font-semibold text-stone-700 mb-1">Judul Tugas</label>
            <input
              v-model="taskForm.title"
              type="text"
              placeholder="Nama atau deskripsi tugas..."
              class="w-full px-2.5 py-1.5 bg-stone-50 border border-stone-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-brand-500 text-xs"
              required
            />
          </div>

          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="block font-semibold text-stone-700 mb-1">Grup / Swimlane</label>
              <input
                v-model="taskForm.group"
                type="text"
                placeholder="Grup topik (opsional)..."
                class="w-full px-2.5 py-1.5 bg-stone-50 border border-stone-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-brand-500 text-xs"
              />
            </div>
            <div>
              <label class="block font-semibold text-stone-700 mb-1">Prioritas</label>
              <select
                v-model="taskForm.priority"
                class="w-full px-2.5 py-1.5 bg-stone-50 border border-stone-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-brand-500 text-xs"
              >
                <option value="Normal">Normal</option>
                <option value="High">High</option>
                <option value="Urgent">Urgent</option>
                <option value="Low">Low</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="block font-semibold text-stone-700 mb-1">Status</label>
              <select
                v-model="taskForm.status"
                class="w-full px-2.5 py-1.5 bg-stone-50 border border-stone-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-brand-500 text-xs"
              >
                <option value="To Do">To Do</option>
                <option value="In Progress">In Progress</option>
                <option value="In Review">In Review</option>
                <option value="Done">Done</option>
                <option value="Blocked">Blocked</option>
              </select>
            </div>
            <div>
              <label class="block font-semibold text-stone-700 mb-1">Jatuh Tempo (Due Date)</label>
              <input
                v-model="taskForm.due_date"
                type="date"
                class="w-full px-2.5 py-1.5 bg-stone-50 border border-stone-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-brand-500 text-xs"
              />
            </div>
          </div>

          <div class="flex items-center justify-end gap-2 pt-2 border-t border-stone-200">
            <button
              type="button"
              @click="isTaskModalOpen = false"
              class="px-3 py-1.5 bg-stone-100 hover:bg-stone-200 text-stone-700 rounded-lg text-xs font-medium cursor-pointer"
            >
              Batal
            </button>
            <button
              type="submit"
              :disabled="isSavingTask"
              class="px-4 py-1.5 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-semibold shadow-2xs transition cursor-pointer disabled:opacity-50"
            >
              {{ isSavingTask ? 'Menyimpan...' : 'Tambah Tugas' }}
            </button>
          </div>
        </form>
      </div>
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
          <div class="flex items-center gap-2 flex-wrap">
            <span v-if="activeTaskNote.note_title" class="font-semibold text-brand-600 flex items-center gap-1">
              <FileText class="w-3.5 h-3.5 text-brand-600" />
              <span>{{ activeTaskNote.note_title }}</span>
            </span>
            <span v-if="activeTaskNote.folder_name" class="px-2 py-0.5 rounded bg-stone-100 text-stone-600 text-[10px] flex items-center gap-1">
              <Folder class="w-2.5 h-2.5 text-stone-500" />
              <span>{{ activeTaskNote.folder_name }}</span>
            </span>
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
              :disabled="isSavingTaskNote"
              class="px-4 py-1.5 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-semibold shadow-2xs transition cursor-pointer flex items-center gap-1.5 disabled:opacity-50"
            >
              <Save class="w-3.5 h-3.5" />
              <span>{{ isSavingTaskNote ? 'Menyimpan...' : 'Simpan Catatan' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { marked } from 'marked'
import { useNotesStore } from '../stores/notes'
import {
  CheckSquare, X, Search, Check, RefreshCw, CalendarDays, List, ArrowRight,
  Plus, Pencil, Trash2, Target, Download, FileSpreadsheet, Globe, ChevronDown,
  FileText, Table, Code, Save, StickyNote, Folder, Tag, Calendar
} from 'lucide-vue-next'

const notesStore = useNotesStore()

const activeView = ref('timeline') // 'timeline' | 'list'
const timelineGrouping = ref('by_note') // 'by_note' | 'by_folder' | 'by_group' | 'chronological'

const searchQuery = ref('')
const filterFolder = ref('all') // 'all' | folderId
const filterNote = ref('all') // 'all' | noteId
const filterGroup = ref('all') // 'all' | groupName
const filterStatus = ref('all') // 'all' | 'active' | 'completed'
const filterPriority = ref('all') // 'all' | 'Urgent' | 'High' | 'Normal' | 'Low'

// Export State
const isExportMenuOpen = ref(false)
const isExporting = ref(false)

function onDocumentClick(e) {
  if (isExportMenuOpen.value && !e.target.closest('.relative')) {
    isExportMenuOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', onDocumentClick)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', onDocumentClick)
})

async function exportTimeline(format = 'html', scope = 'filtered') {
  isExportMenuOpen.value = false
  isExporting.value = true

  const tasksToExport = (scope === 'filtered') ? filteredTasks.value : notesStore.allMasterTasks
  const targetsToExport = (scope === 'filtered') ? activeTargets.value : notesStore.allMasterTargets

  try {
    const payload = {
      title: "Noto Combined Master Timeline & Roadmap Report",
      tasks: tasksToExport,
      targets: targetsToExport
    }

    const endpoint = format === 'excel' ? '/api/export/excel' : '/api/export/html'
    const ext = format === 'excel' ? 'xlsx' : 'html'
    const mime = format === 'excel'
      ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      : 'text/html'

    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!res.ok) throw new Error(`Export failed with status ${res.status}`)

    const blob = await res.blob()
    const url = URL.createObjectURL(new Blob([blob], { type: mime }))
    const a = document.createElement('a')
    const dateStr = new Date().toISOString().slice(0, 10)
    a.href = url
    a.download = `noto-master-timeline-${dateStr}.${ext}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch (err) {
    console.error('Export failed:', err)
    alert(`Export gagal: ${err.message}`)
  } finally {
    isExporting.value = false
  }
}

// Modals State
const isTargetModalOpen = ref(false)
const targetModalMode = ref('add') // 'add' | 'edit'
const targetForm = ref({
  id: '',
  note_id: '',
  title: '',
  badge: 'Milestone',
  date: '',
  description: ''
})
const isSavingTarget = ref(false)

const isTaskModalOpen = ref(false)
const taskForm = ref({
  note_id: '',
  title: '',
  status: 'To Do',
  priority: 'Normal',
  due_date: '',
  group: ''
})
const isSavingTask = ref(false)

// Task Note Modal ("Jendela Baru Catatan / Spek Teknis")
const activeTaskNote = ref(null)
const editingTaskNoteContent = ref('')
const taskNoteTab = ref('edit') // 'edit' | 'preview'
const isSavingTaskNote = ref(false)

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

async function saveTaskNote() {
  if (!activeTaskNote.value) return
  isSavingTaskNote.value = true
  const newNotes = editingTaskNoteContent.value.trim()
  activeTaskNote.value.notes = newNotes
  try {
    await fetch(`/api/notes/${activeTaskNote.value.note_id}/tasks/${activeTaskNote.value.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notes: newNotes })
    })
    await notesStore.fetchAllTasks()
    closeTaskNoteModal()
  } catch (e) {
    console.error('Failed to save task notes:', e)
  } finally {
    isSavingTaskNote.value = false
  }
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

const completedCount = computed(() => {
  return notesStore.allMasterTasks.filter(t => t.done).length
})

const activeCount = computed(() => {
  return notesStore.allMasterTasks.length - completedCount.value
})

// Auto-detected Folders list
const allFoldersList = computed(() => {
  const map = new Map()
  notesStore.allMasterTasks.forEach(t => {
    const fId = t.folder_id || 'root'
    const fName = t.folder_name || 'Tanpa Folder'
    if (!map.has(fId)) {
      map.set(fId, { id: fId, name: fName })
    }
  })
  if (notesStore.folders) {
    notesStore.folders.forEach(f => {
      if (!map.has(f.id)) {
        map.set(f.id, { id: f.id, name: f.name })
      }
    })
  }
  return Array.from(map.values())
})

const activeFoldersList = computed(() => {
  if (filterFolder.value !== 'all') {
    return allFoldersList.value.filter(f => f.id === filterFolder.value)
  }
  return allFoldersList.value
})

// Auto-detected Notes list
const allNotesList = computed(() => {
  const map = new Map()
  notesStore.allMasterTasks.forEach(t => {
    if (t.note_id && !map.has(t.note_id)) {
      map.set(t.note_id, {
        id: t.note_id,
        title: t.note_title,
        folder_id: t.folder_id,
        folder_name: t.folder_name
      })
    }
  })
  if (notesStore.notes) {
    notesStore.notes.forEach(n => {
      if (!map.has(n.id)) {
        map.set(n.id, {
          id: n.id,
          title: n.title,
          folder_id: n.folder_id,
          folder_name: n.folder_id ? (notesStore.folders.find(f => f.id === n.folder_id)?.name || '') : ''
        })
      }
    })
  }
  return Array.from(map.values())
})

const activeNotesList = computed(() => {
  let list = allNotesList.value
  if (filterFolder.value !== 'all') {
    list = list.filter(n => (n.folder_id || 'root') === filterFolder.value)
  }
  if (filterNote.value !== 'all') {
    list = list.filter(n => n.id === filterNote.value)
  }
  return list
})

// Auto-detected Groups list
const allGroupsList = computed(() => {
  const set = new Set()
  notesStore.allMasterTasks.forEach(t => {
    if (t.group && t.group.trim()) {
      set.add(t.group.trim())
    }
  })
  return Array.from(set)
})

const activeGroupsList = computed(() => {
  if (filterGroup.value !== 'all') {
    return allGroupsList.value.filter(g => g === filterGroup.value)
  }
  return allGroupsList.value
})

// Dynamic Targets list filtered by folder/note/search
const activeTargets = computed(() => {
  return notesStore.allMasterTargets.filter(tgt => {
    if (filterFolder.value !== 'all') {
      const fId = tgt.folder_id || 'root'
      if (fId !== filterFolder.value) return false
    }
    if (filterNote.value !== 'all' && tgt.note_id !== filterNote.value) {
      return false
    }
    if (searchQuery.value.trim()) {
      const q = searchQuery.value.toLowerCase()
      const matchTitle = (tgt.title || '').toLowerCase().includes(q)
      const matchDesc = (tgt.description || '').toLowerCase().includes(q)
      const matchBadge = (tgt.badge || '').toLowerCase().includes(q)
      const matchNote = (tgt.note_title || '').toLowerCase().includes(q)
      if (!matchTitle && !matchDesc && !matchBadge && !matchNote) return false
    }
    return true
  })
})

const filteredTasks = computed(() => {
  return notesStore.allMasterTasks.filter(t => {
    // Folder filter
    if (filterFolder.value !== 'all') {
      const fId = t.folder_id || 'root'
      if (fId !== filterFolder.value) return false
    }

    // Note filter
    if (filterNote.value !== 'all' && t.note_id !== filterNote.value) return false

    // Group filter
    if (filterGroup.value !== 'all' && t.group !== filterGroup.value) return false

    // Status filter
    if (filterStatus.value === 'active' && t.done) return false
    if (filterStatus.value === 'completed' && !t.done) return false

    // Priority filter
    if (filterPriority.value !== 'all' && t.priority !== filterPriority.value) return false

    // Search query
    if (searchQuery.value.trim()) {
      const q = searchQuery.value.toLowerCase()
      const matchTitle = (t.title || '').toLowerCase().includes(q)
      const matchNote = (t.note_title || '').toLowerCase().includes(q)
      const matchGroup = (t.group || '').toLowerCase().includes(q)
      const matchFolder = (t.folder_name || '').toLowerCase().includes(q)
      if (!matchTitle && !matchNote && !matchGroup && !matchFolder) return false
    }

    return true
  })
})

function getTasksByNote(noteId) {
  return filteredTasks.value.filter(t => t.note_id === noteId)
}

function getSortedTasksByNote(noteId) {
  return [...getTasksByNote(noteId)].sort((a, b) => {
    if (!a.due_date && !b.due_date) return 0
    if (!a.due_date) return 1
    if (!b.due_date) return -1
    return new Date(a.due_date) - new Date(b.due_date)
  })
}

function getTasksByFolder(folderId) {
  if (folderId === 'root') {
    return filteredTasks.value.filter(t => !t.folder_id || t.folder_id === 'root')
  }
  return filteredTasks.value.filter(t => t.folder_id === folderId)
}

function getSortedTasksByFolder(folderId) {
  return [...getTasksByFolder(folderId)].sort((a, b) => {
    if (!a.due_date && !b.due_date) return 0
    if (!a.due_date) return 1
    if (!b.due_date) return -1
    return new Date(a.due_date) - new Date(b.due_date)
  })
}

function getTasksByGroup(groupName) {
  return filteredTasks.value.filter(t => t.group === groupName)
}

function getSortedTasksByGroup(groupName) {
  return [...getTasksByGroup(groupName)].sort((a, b) => {
    if (!a.due_date && !b.due_date) return 0
    if (!a.due_date) return 1
    if (!b.due_date) return -1
    return new Date(a.due_date) - new Date(b.due_date)
  })
}

const tasksWithoutGroup = computed(() => {
  return filteredTasks.value.filter(t => !t.group || !t.group.trim())
})

const chronologicalTasks = computed(() => {
  return [...filteredTasks.value].sort((a, b) => {
    if (!a.due_date && !b.due_date) return 0
    if (!a.due_date) return 1
    if (!b.due_date) return -1
    return new Date(a.due_date) - new Date(b.due_date)
  })
})

function jumpToNote(noteId) {
  notesStore.selectNote(noteId)
  notesStore.isMasterTasksOpen = false
}

// Interactive Task Actions
async function toggleTask(task) {
  const newDone = !task.done
  const newStatus = newDone ? 'Done' : (task.status === 'Done' ? 'To Do' : task.status)
  task.done = newDone
  task.status = newStatus
  try {
    const res = await fetch(`/api/notes/${task.note_id}/tasks/${task.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ done: newDone, status: newStatus })
    })
    if (!res.ok) {
      await notesStore.fetchAllTasks()
    }
  } catch (e) {
    console.error('Failed to toggle task:', e)
    await notesStore.fetchAllTasks()
  }
}

async function updateTaskStatus(task, newStatus) {
  task.status = newStatus
  task.done = (newStatus === 'Done')
  try {
    await fetch(`/api/notes/${task.note_id}/tasks/${task.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus, done: task.done })
    })
  } catch (e) {
    console.error('Failed to update task status:', e)
    await notesStore.fetchAllTasks()
  }
}

async function deleteTask(task) {
  if (!confirm(`Hapus tugas "${task.title}"?`)) return
  try {
    const res = await fetch(`/api/notes/${task.note_id}/tasks/${task.id}`, {
      method: 'DELETE'
    })
    if (res.ok) {
      notesStore.allMasterTasks = notesStore.allMasterTasks.filter(t => t.id !== task.id)
    }
  } catch (e) {
    console.error('Failed to delete task:', e)
    await notesStore.fetchAllTasks()
  }
}

// Interactive Target Goals CRUD Actions
function openAddMasterTargetModal() {
  targetModalMode.value = 'add'
  targetForm.value = {
    id: '',
    note_id: (allNotesList.value.length > 0 ? allNotesList.value[0].id : ''),
    title: '',
    badge: 'Milestone',
    date: new Date().toISOString().slice(0, 10),
    description: ''
  }
  isTargetModalOpen.value = true
}

function openEditMasterTargetModal(tgt) {
  targetModalMode.value = 'edit'
  targetForm.value = {
    id: tgt.id,
    note_id: tgt.note_id,
    title: tgt.title,
    badge: tgt.badge || 'Milestone',
    date: tgt.date || '',
    description: tgt.description || ''
  }
  isTargetModalOpen.value = true
}

async function saveTargetModal() {
  if (!targetForm.value.title.trim() || !targetForm.value.note_id) return
  isSavingTarget.value = true
  try {
    if (targetModalMode.value === 'add') {
      await fetch(`/api/notes/${targetForm.value.note_id}/targets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: targetForm.value.title.trim(),
          badge: targetForm.value.badge.trim(),
          date: targetForm.value.date.trim(),
          description: targetForm.value.description.trim()
        })
      })
    } else {
      await fetch(`/api/notes/${targetForm.value.note_id}/targets/${targetForm.value.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: targetForm.value.title.trim(),
          badge: targetForm.value.badge.trim(),
          date: targetForm.value.date.trim(),
          description: targetForm.value.description.trim()
        })
      })
    }
    await notesStore.fetchAllTasks()
    isTargetModalOpen.value = false
  } catch (e) {
    console.error('Failed to save target:', e)
  } finally {
    isSavingTarget.value = false
  }
}

async function deleteMasterTarget(tgt) {
  if (!confirm(`Hapus target milestone "${tgt.title}"?`)) return
  try {
    const res = await fetch(`/api/notes/${tgt.note_id}/targets/${tgt.id}`, {
      method: 'DELETE'
    })
    if (res.ok) {
      notesStore.allMasterTargets = notesStore.allMasterTargets.filter(t => t.id !== tgt.id)
    }
  } catch (e) {
    console.error('Failed to delete target:', e)
    await notesStore.fetchAllTasks()
  }
}

function openAddTaskModal(noteId = null) {
  taskForm.value = {
    note_id: noteId || (allNotesList.value.length > 0 ? allNotesList.value[0].id : ''),
    title: '',
    status: 'To Do',
    priority: 'Normal',
    due_date: '',
    group: ''
  }
  isTaskModalOpen.value = true
}

async function saveTaskModal() {
  if (!taskForm.value.title.trim() || !taskForm.value.note_id) return
  isSavingTask.value = true
  try {
    await fetch(`/api/notes/${taskForm.value.note_id}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: taskForm.value.title.trim(),
        status: taskForm.value.status,
        priority: taskForm.value.priority,
        due_date: taskForm.value.due_date,
        group: taskForm.value.group.trim()
      })
    })
    await notesStore.fetchAllTasks()
    isTaskModalOpen.value = false
  } catch (e) {
    console.error('Failed to add task:', e)
  } finally {
    isSavingTask.value = false
  }
}

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
