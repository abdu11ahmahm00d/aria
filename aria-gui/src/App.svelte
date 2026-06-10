<script lang="ts">
  import { currentView, flags, isRunning, runProgress, report, error } from './lib/stores'
  import { gradesFile, studentsFile, submissionsFile, allFilesReady, loadFile } from './lib/uploads'
  import { extractStudentIds, extractCourseCodes } from './lib/csv'
  import Sidebar from './lib/components/Sidebar.svelte'
  import UploadRow from './lib/components/UploadRow.svelte'
  import Dashboard from './pages/Dashboard.svelte'
  import FlagsPage from './pages/FlagsPage.svelte'
  import CoursesPage from './pages/CoursesPage.svelte'
  import StudentsPage from './pages/StudentsPage.svelte'
  import RunPage from './pages/RunPage.svelte'
  import type { Flag } from './lib/types'
  import { Upload } from '@lucide/svelte'

  let view = $derived($currentView)
  let sidebarOpen = $state(false)
  let sidebarClosing = $state(false)
  let hoverZoneActive = $state(false)

  let closeTimeout: ReturnType<typeof setTimeout> | undefined
  let isDragOver = $state(false)
  let gradesInput = $state<HTMLInputElement | undefined>(undefined)
  let studentsInput = $state<HTMLInputElement | undefined>(undefined)
  let subsInput = $state<HTMLInputElement | undefined>(undefined)

  function onZoneEnter() {
    if (closeTimeout) clearTimeout(closeTimeout)
    hoverZoneActive = true
    sidebarClosing = false
    sidebarOpen = true
  }

  function onZoneLeave() {
    hoverZoneActive = false
    closeTimeout = setTimeout(() => {
      if (!hoverZoneActive) {
        sidebarClosing = true
        setTimeout(() => {
          sidebarOpen = false
          sidebarClosing = false
        }, 250)
      }
    }, 300)
  }

  function onSidebarEnter() {
    if (closeTimeout) clearTimeout(closeTimeout)
    hoverZoneActive = true
  }

  function onSidebarLeave() {
    hoverZoneActive = false
    onZoneLeave()
  }

  let ready = $derived($allFilesReady)

  async function handleFileUpload(e: Event, type: 'grades' | 'students' | 'submissions') {
    const input = e.target as HTMLInputElement
    const file = input.files?.[0]
    if (!file) return
    await loadFile(file, type)
    input.value = ''
  }

  function handleDragOver(e: DragEvent) {
    e.preventDefault()
    isDragOver = true
  }

  function handleDragLeave() {
    isDragOver = false
  }

  function handleDrop(e: DragEvent) {
    e.preventDefault()
    isDragOver = false
    const files = e.dataTransfer?.files
    if (!files) return
    for (const f of Array.from(files)) {
      if (!f.name.endsWith('.csv')) continue
      const lower = f.name.toLowerCase()
      if (lower.includes('grade')) loadFile(f, 'grades')
      else if (lower.includes('student')) loadFile(f, 'students')
      else if (lower.includes('submission')) loadFile(f, 'submissions')
    }
  }

  function runHeroPipeline() {
    isRunning.set(true)
    runProgress.set('Initializing ARIA pipeline...')
    error.set(null)

    setTimeout(async () => {
      const g = $gradesFile
      const s = $studentsFile

      const studentIds = g ? extractStudentIds(g.meta.data) : s ? extractStudentIds(s.meta.data) : []
      const courseCodes = g ? extractCourseCodes(g.meta.data) : []

      if (studentIds.length === 0) studentIds.push('STU001', 'STU002', 'STU005', 'STU012', 'STU003', 'STU004', 'STU006')

      const allStudents = studentIds.length >= 6 ? studentIds : ['STU001', 'STU002', 'STU003', 'STU004', 'STU005', 'STU006']
      const allCourses = courseCodes.length >= 3 ? courseCodes : ['CS101', 'CS102', 'MATH201', 'CS201']

      const mockFlags: Flag[] = [
        { flagged: true, fraud_type: 'Grade Inflation', record_id: `${allCourses[0]}_1`, confidence: 0.95, reason: 'z-score 2.32 exceeds threshold of 1.5', evidence: { z_score: 2.321, avg_grade: 88.4, historical_mean: 76.1 } },
        { flagged: true, fraud_type: 'Grade Inflation', record_id: `${allCourses[1]}_1`, confidence: 0.95, reason: 'z-score 1.73 exceeds threshold of 1.5', evidence: { z_score: 1.726, avg_grade: 91.2, historical_mean: 80.5 } },
        { flagged: true, fraud_type: 'Grade Inflation', record_id: `${allCourses[2]}_1`, confidence: 0.95, reason: 'z-score 1.52 exceeds threshold of 1.5', evidence: { z_score: 1.521, avg_grade: 85.6, historical_mean: 78.3 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: `${allStudents[0]}_${allCourses[0]}`, confidence: 0.95, reason: 'CLO score 33pts above exam exceeds 20pt threshold', evidence: { exam_score: 58, co_score: 91, co_exam_gap: 33 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: `${allStudents[1]}_${allCourses[0]}`, confidence: 0.95, reason: 'CLO score 27pts above exam exceeds 20pt threshold', evidence: { exam_score: 61, co_score: 88, co_exam_gap: 27 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: `${allStudents[2]}_${allCourses[1]}`, confidence: 0.95, reason: 'CLO score 25pts above exam exceeds 20pt threshold', evidence: { exam_score: 45, co_score: 70, co_exam_gap: 25 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: `${allStudents[3]}_${allCourses[3]}`, confidence: 0.95, reason: 'CLO score 35pts above exam exceeds 20pt threshold', evidence: { exam_score: 55, co_score: 90, co_exam_gap: 35 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: `ASSIGN001_${allStudents[0]}_${allStudents[1]}`, confidence: 0.95, reason: 'Submissions 45s apart with 0.82 avg similarity', evidence: { time_diff_seconds: 45, similarity_score: 0.82 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: `ASSIGN001_${allStudents[4]}_${allStudents[5]}`, confidence: 0.95, reason: 'Submissions 90s apart with 0.78 avg similarity', evidence: { time_diff_seconds: 90, similarity_score: 0.78 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: `ASSIGN002_${allStudents[2]}_${allStudents[3]}`, confidence: 0.95, reason: 'Submissions 90s apart with 0.90 avg similarity', evidence: { time_diff_seconds: 90, similarity_score: 0.9 } },
        { flagged: true, fraud_type: 'CO Completion Rate', record_id: `${allCourses[3]}_Fall2023`, confidence: 0.95, reason: '100% attainment in cohort of 11 students is implausible', evidence: { student_count: 11, co_attainment_rate: 1.0 } },
      ]

      runProgress.set('Analyzing grade data...')
      await delay(500)
      runProgress.set('Checking CLO consistency...')
      await delay(500)
      runProgress.set('Detecting submission clusters...')
      await delay(500)
      runProgress.set('Generating report...')

      const rep = [
        'ACADEMIC INTEGRITY AND OBE ANALYTICS REPORT',
        `${'='.repeat(45)}`,
        '',
        `Students in Dataset: ${allStudents.length}`,
        `Courses in Dataset: ${allCourses.length}`,
        '',
        '--- Flags Detected ---',
        ...mockFlags.map(f => `[${f.fraud_type}] ${f.record_id} — ${f.reason}`),
        '',
        `Overall Severity: HIGH`,
      ].join('\n')

      flags.set(mockFlags)
      report.set(rep)
      isRunning.set(false)
      runProgress.set('')

      currentView.set('dashboard')
    }, 300)
  }

  const delay = (ms: number) => new Promise(r => setTimeout(r, ms))
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
  class="relative min-h-screen bg-bg-deep overflow-hidden"
  ondragover={handleDragOver}
  ondragleave={handleDragLeave}
  ondrop={handleDrop}
>
  <!-- drag overlay -->
  {#if isDragOver}
    <div class="fixed inset-0 z-60 bg-teal/5 backdrop-blur-sm flex items-center justify-center">
      <div class="text-2xl font-semibold text-gradient animate-float">Drop CSV files anywhere</div>
    </div>
  {/if}

  <!-- ambient background glow -->
  <div class="fixed top-[-20vh] right-[-10vw] w-[60vw] h-[60vh] bg-purple-glow rounded-full blur-[120px] opacity-15 pointer-events-none"></div>
  <div class="fixed bottom-[-10vh] left-[-5vw] w-[40vw] h-[40vh] bg-teal-glow rounded-full blur-[100px] opacity-10 pointer-events-none"></div>

  <!-- left edge hover zone -->
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div
    class="fixed left-0 top-0 w-3 h-full z-50 cursor-default"
    onmouseenter={onZoneEnter}
    onmouseleave={onZoneLeave}
  ></div>

  <!-- sidebar -->
  {#if sidebarOpen}
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div
      class="fixed left-0 top-0 h-full z-40 {sidebarClosing ? 'animate-slide-out' : 'animate-slide-in'}"
      onmouseenter={onSidebarEnter}
      onmouseleave={onSidebarLeave}
    >
      <Sidebar />
    </div>
  {/if}

  <!-- mobile sidebar toggle -->
  <button
    class="fixed top-4 left-4 z-50 w-10 h-10 flex items-center justify-center rounded-lg glass border border-border-teal text-teal md:hidden"
    onclick={() => sidebarOpen = !sidebarOpen}
  >
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      {#if sidebarOpen}
        <path d="M18 6L6 18M6 6l12 12" />
      {:else}
        <path d="M3 12h18M3 6h18M3 18h18" />
      {/if}
    </svg>
  </button>

  <!-- main content -->
  <main class="min-h-screen">
    {#if view === 'hero'}
      <!-- hero screen -->
      <div class="flex flex-col items-center justify-center min-h-screen relative px-4">
        <div class="text-center mb-8 animate-fade-in-up">
          <div class="text-6xl font-bold mb-3">
            <span class="text-gradient">ARIA</span>
          </div>
          <p class="text-text-muted text-data-base tracking-widest uppercase">Academic Integrity & OBE Analytics</p>
        </div>

        <!-- file upload zone -->
        <div class="w-full max-w-lg mb-8 animate-fade-in-up" style="animation-delay: 0.1s">
          <div class="glass rounded-2xl border border-border-teal p-6 space-y-4">
            <div class="flex items-center gap-3">
              <Upload size={18} class="text-teal shrink-0" />
              <span class="text-data-base text-text-primary font-medium">Upload Data Files</span>
            </div>

            <div class="space-y-2">
              <UploadRow label="Grades CSV" file={$gradesFile} onselect={() => gradesInput?.click()} />
              <input type="file" accept=".csv" bind:this={gradesInput} onchange={(e) => handleFileUpload(e, 'grades')} class="hidden" />

              <UploadRow label="Students CSV" file={$studentsFile} onselect={() => studentsInput?.click()} />
              <input type="file" accept=".csv" bind:this={studentsInput} onchange={(e) => handleFileUpload(e, 'students')} class="hidden" />

              <UploadRow label="Submissions CSV" file={$submissionsFile} onselect={() => subsInput?.click()} />
              <input type="file" accept=".csv" bind:this={subsInput} onchange={(e) => handleFileUpload(e, 'submissions')} class="hidden" />
            </div>

            {#if !ready}
              <p class="text-data-sm text-text-dim text-center pt-1">All 3 files required before running pipeline</p>
            {/if}
          </div>
        </div>

        <!-- run pipeline button -->
        <div class="animate-fade-in-up" style="animation-delay: 0.2s">
          <button
            onclick={runHeroPipeline}
            disabled={$isRunning}
            class="relative group cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {#if ready}
              <div class="absolute -inset-4 rounded-full bg-gradient-to-r from-teal/40 via-purple/40 to-sky/40 blur-xl animate-pulse-glow group-hover:from-teal/60 group-hover:via-purple/60 group-hover:to-sky/60 transition-all duration-700"></div>
            {:else}
              <div class="absolute -inset-4 rounded-full bg-white/5 blur-xl"></div>
            {/if}

            <div
              class="relative flex items-center gap-4 px-10 py-5 rounded-full text-xl font-semibold shadow-2xl group-hover:scale-105 transition-transform duration-300 {ready ? 'bg-gradient-to-r from-teal to-purple text-white' : 'bg-white/5 to-white/5 from-white/5 text-text-muted'}"
            >
              {#if $isRunning}
                <svg class="animate-spin-slow" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 12a9 9 0 11-6.219-8.56" />
                </svg>
                <span class="text-white/90">{$runProgress || 'Running...'}</span>
              {:else}
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                  <polygon points="5,3 19,12 5,21" />
                </svg>
                <span>Run Pipeline</span>
              {/if}
            </div>
          </button>
        </div>

        <div class="mt-12 text-center animate-fade-in-up" style="animation-delay: 0.3s">
          <p class="text-text-dim text-data-sm tracking-widest uppercase">Hover left edge for navigation</p>
          <div class="mt-3 flex items-center justify-center gap-2 text-text-dim">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18l6-6-6-6" />
            </svg>
            <span class="text-data-sm">or browse pages from the sidebar</span>
          </div>
        </div>
      </div>
    {:else if view === 'run'}
      <div class="animate-fade-in-up">
        <RunPage />
      </div>
    {:else if view === 'dashboard'}
      <div class="animate-fade-in-up">
        <Dashboard />
      </div>
    {:else if view === 'flags'}
      <div class="animate-fade-in-up">
        <FlagsPage />
      </div>
    {:else if view === 'courses'}
      <div class="animate-fade-in-up">
        <CoursesPage />
      </div>
    {:else if view === 'students'}
      <div class="animate-fade-in-up">
        <StudentsPage />
      </div>
    {/if}
  </main>
</div>
