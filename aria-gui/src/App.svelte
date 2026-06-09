<script lang="ts">
  import { currentView, flags, isRunning, runProgress, report, error } from './lib/stores'
  import { gradesFile, studentsFile, submissionsFile, allFilesReady, loadFile } from './lib/uploads'
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
      const sub = $submissionsFile

      const gradesRows = g?.meta.data ?? []
      const studentsRows = s?.meta.data ?? []
      const subsRows = sub?.meta.data ?? []

      const mockFlags: Flag[] = []

      // 1 — Grade Inflation
      runProgress.set('Checking grade inflation...')
      await delay(200)
      for (const row of gradesRows) {
        const avg = parseFloat(row.avg_grade)
        const mean = parseFloat(row.historical_mean)
        const std = parseFloat(row.historical_std) || 1
        const z = (avg - mean) / std
        if (z > 1.5) {
          mockFlags.push({
            flagged: true,
            fraud_type: 'Grade Inflation',
            record_id: `${row.course_id}_${row.section_id}`,
            confidence: Math.min(0.7 + (z - 1.5) * 0.15, 0.99),
            reason: `z-score ${z.toFixed(2)} exceeds threshold of 1.5`,
            evidence: { z_score: Math.round(z * 1000) / 1000, avg_grade: avg, historical_mean: mean },
          })
        }
      }

      // 2 — CLO Inconsistency Check
      runProgress.set('Checking CLO consistency...')
      await delay(200)
      for (const row of studentsRows) {
        const exam = parseFloat(row.exam_score)
        const clo = parseFloat(row.co_score)
        const gap = clo - exam
        if (gap > 20) {
          mockFlags.push({
            flagged: true,
            fraud_type: 'CLO Inconsistency',
            record_id: `${row.student_id}_${row.course_id}`,
            confidence: Math.min(0.7 + (gap - 20) * 0.015, 0.99),
            reason: `CLO score ${gap}pts above exam exceeds 20pt threshold`,
            evidence: { exam_score: exam, co_score: clo, co_exam_gap: Math.round(gap * 100) / 100 },
          })
        }
      }

      // 3 — Submission Clustering Check
      runProgress.set('Detecting submission clusters...')
      await delay(200)
      const byAssignment: Record<string, any[]> = {}
      for (const row of subsRows) {
        const aid = row.assignment_id
        if (!byAssignment[aid]) byAssignment[aid] = []
        byAssignment[aid].push(row)
      }
      for (const [aid, group] of Object.entries(byAssignment)) {
        const sorted = group.sort((a, b) => a.timestamp.localeCompare(b.timestamp))
        for (let i = 0; i < sorted.length; i++) {
          for (let j = i + 1; j < sorted.length; j++) {
            const t1 = Date.parse(sorted[i].timestamp)
            const t2 = Date.parse(sorted[j].timestamp)
            if (isNaN(t1) || isNaN(t2)) continue
            const td = Math.abs(t2 - t1) / 1000
            if (td <= 120) {
              const sim1 = parseFloat(sorted[i].similarity_score) || 0
              const sim2 = parseFloat(sorted[j].similarity_score) || 0
              const avgSim = (sim1 + sim2) / 2
              if (avgSim > 0.75) {
                mockFlags.push({
                  flagged: true,
                  fraud_type: 'Submission Clustering',
                  record_id: `${aid}_${sorted[i].student_id}_${sorted[j].student_id}`,
                  confidence: Math.min(0.7 + avgSim * 0.2, 0.99),
                  reason: `Submissions ${Math.round(td)}s apart with ${avgSim.toFixed(2)} avg similarity`,
                  evidence: { time_diff_seconds: Math.round(td), similarity_score: Math.round(avgSim * 100) / 100 },
                })
              }
            }
          }
        }
      }

      // 4 — CO Completion Rate Check
      runProgress.set('Checking completion rates...')
      await delay(200)
      const byCourse: Record<string, any[]> = {}
      for (const row of studentsRows) {
        const key = `${row.course_id}_${row.semester}`
        if (!byCourse[key]) byCourse[key] = []
        byCourse[key].push(row)
      }
      for (const [key, group] of Object.entries(byCourse)) {
        if (group.length >= 8 && group.every(r => parseFloat(r.co_attainment_rate) === 1.0)) {
          mockFlags.push({
            flagged: true,
            fraud_type: 'CO Completion Rate',
            record_id: key,
            confidence: 0.75 + Math.min(group.length, 50) * 0.005,
            reason: `100% attainment in cohort of ${group.length} students is implausible`,
            evidence: { student_count: group.length, co_attainment_rate: 1.0 },
          })
        }
      }

      runProgress.set('Generating report...')

      const severityLabel = mockFlags.length >= 3 ? 'HIGH' : mockFlags.length >= 1 ? 'MEDIUM' : 'LOW'
      const byType: Record<string, number> = {}
      for (const f of mockFlags) byType[f.fraud_type] = (byType[f.fraud_type] || 0) + 1

      const rep = [
        'ACADEMIC INTEGRITY AND OBE ANALYTICS REPORT',
        '='.repeat(45),
        '',
        `Total Students: ${studentsRows.length}`,
        `Total Submissions: ${subsRows.length}`,
        `Total Course-Sections: ${gradesRows.length}`,
        '',
        '--- Flags Detected ---',
        ...Object.entries(byType).map(([t, c]) => `  ${t}: ${c}`),
        '',
        ...mockFlags.map(f => `[${f.fraud_type}] ${f.record_id} — ${f.reason}`),
        '',
        `Overall Severity: ${severityLabel}`,
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
