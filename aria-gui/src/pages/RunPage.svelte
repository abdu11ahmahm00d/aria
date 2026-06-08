<script lang="ts">
  import { isRunning, runProgress, runConfig, flags, report, error } from '../lib/stores'
  import Card from '../lib/components/Card.svelte'
  import Button from '../lib/components/Button.svelte'
  import Input from '../lib/components/Input.svelte'
  import Toast from '../lib/components/Toast.svelte'
  import { Play, FolderOpen } from '@lucide/svelte'
  import type { Flag } from '../lib/types'

  let cfg = $state({ ...$runConfig })
  let toastMessage = $state('')
  let toastType = $state<'success' | 'error'>('success')

  function generateMockFlags(): Flag[] {
    return [
      { flagged: true, fraud_type: 'Grade Inflation', record_id: 'CS101_1', confidence: 0.95, reason: 'z-score 2.32 exceeds threshold of 1.5', evidence: { z_score: 2.321, avg_grade: 88.4, historical_mean: 76.1 } },
      { flagged: true, fraud_type: 'Grade Inflation', record_id: 'CS102_1', confidence: 0.95, reason: 'z-score 1.73 exceeds threshold of 1.5', evidence: { z_score: 1.726, avg_grade: 91.2, historical_mean: 80.5 } },
      { flagged: true, fraud_type: 'Grade Inflation', record_id: 'MATH201_1', confidence: 0.95, reason: 'z-score 1.52 exceeds threshold of 1.5', evidence: { z_score: 1.521, avg_grade: 85.6, historical_mean: 78.3 } },
      { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU001_CS101', confidence: 0.95, reason: 'CLO score 33pts above exam exceeds 20pt threshold', evidence: { exam_score: 58, co_score: 91, co_exam_gap: 33 } },
      { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU002_CS101', confidence: 0.95, reason: 'CLO score 27pts above exam exceeds 20pt threshold', evidence: { exam_score: 61, co_score: 88, co_exam_gap: 27 } },
      { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU005_CS102', confidence: 0.95, reason: 'CLO score 25pts above exam exceeds 20pt threshold', evidence: { exam_score: 45, co_score: 70, co_exam_gap: 25 } },
      { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU012_CS201', confidence: 0.95, reason: 'CLO score 35pts above exam exceeds 20pt threshold', evidence: { exam_score: 55, co_score: 90, co_exam_gap: 35 } },
      { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN001_STU001_STU002', confidence: 0.95, reason: 'Submissions 45s apart with 0.82 avg similarity', evidence: { time_diff_seconds: 45, similarity_score: 0.82 } },
      { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN001_STU003_STU004', confidence: 0.95, reason: 'Submissions 90s apart with 0.78 avg similarity', evidence: { time_diff_seconds: 90, similarity_score: 0.78 } },
      { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN002_STU005_STU006', confidence: 0.95, reason: 'Submissions 90s apart with 0.90 avg similarity', evidence: { time_diff_seconds: 90, similarity_score: 0.9 } },
      { flagged: true, fraud_type: 'CO Completion Rate', record_id: 'CS201_Fall2023', confidence: 0.95, reason: '100% attainment in cohort of 11 students is implausible', evidence: { student_count: 11, co_attainment_rate: 1.0 } },
    ]
  }

  function generateMockReport(): string {
    return [
      'ACADEMIC INTEGRITY AND OBE ANALYTICS REPORT',
      '=============================================',
      '',
      'Total Flags Detected: 11',
      '',
      'Grade Inflation (3):',
      '  1. Record: CS101_1',
      '  2. Record: CS102_1',
      '  3. Record: MATH201_1',
      '',
      'CLO Inconsistency (4):',
      '  1. Record: STU001_CS101',
      '  2. Record: STU002_CS101',
      '  3. Record: STU005_CS102',
      '  4. Record: STU012_CS201',
      '',
      'Submission Clustering (3):',
      '  1. Record: ASSIGN001_STU001_STU002',
      '  2. Record: ASSIGN001_STU003_STU004',
      '  3. Record: ASSIGN002_STU005_STU006',
      '',
      'CO Completion Rate (1):',
      '  1. Record: CS201_Fall2023',
      '',
      'Overall Severity: HIGH',
      '',
      'Students flagged in multiple fraud types: STU001 (CLO Inconsistency, Submission Clustering), STU005 (CLO Inconsistency, Submission Clustering)',
    ].join('\n')
  }

  async function runDemo() {
    isRunning.set(true)
    runProgress.set('Generating demo data...')
    error.set(null)

    await new Promise(r => setTimeout(r, 800))

    const mockFlags = generateMockFlags()
    const mockReport = generateMockReport()

    flags.set(mockFlags)
    report.set(mockReport)
    isRunning.set(false)
    runProgress.set('')
    toastMessage = `Demo complete: ${mockFlags.length} flags generated`
    toastType = 'success'
  }

  async function loadResults() {
    try {
      const flagResp = await fetch(cfg.outputDir + '/flags.json')
      const reportResp = await fetch(cfg.outputDir + '/report.txt')
      if (!flagResp.ok || !reportResp.ok) throw new Error('Results not found')
      flags.set(await flagResp.json())
      report.set(await reportResp.text())
      toastMessage = 'Results loaded from ' + cfg.outputDir
      toastType = 'success'
    } catch (e: unknown) {
      error.set('No pipeline results found. Run python main.py first, or use the demo mode below.')
      toastMessage = 'Failed to load results'
      toastType = 'error'
    }
  }
</script>

<div class="p-6 pt-16 md:pt-6 space-y-6 max-w-2xl">
  <div>
    <h1 class="text-2xl font-bold"><span class="text-gradient">Pipeline</span></h1>
    <p class="text-text-muted text-data-base mt-1">Run from command line or load results</p>
  </div>

  <div class="grid grid-cols-2 gap-4">
    <Card>
      <div class="space-y-4">
        <h2 class="text-data-base font-semibold text-text-primary">Load Existing Results</h2>
        <p class="text-data-sm text-text-muted">Load flags and report from a previous pipeline run.</p>
        <Input label="Output Directory" bind:value={cfg.outputDir} placeholder="output" />
        <Button variant="secondary" onclick={loadResults}>
          <FolderOpen size={16} /> Load Results
        </Button>
      </div>
    </Card>
    <Card>
      <div class="space-y-4">
        <h2 class="text-data-base font-semibold text-text-primary">Demo Mode</h2>
        <p class="text-data-sm text-text-muted">Generate sample data instantly for demonstration.</p>
        <Input label="Grades CSV" bind:value={cfg.gradesPath} disabled={true} />
        <Button variant="primary" disabled={$isRunning} onclick={runDemo}>
          {#if $isRunning}
            <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            Generating...
          {:else}
            <Play size={16} /> Run Demo
          {/if}
        </Button>
      </div>
    </Card>
  </div>

  {#if $runProgress}
    <Card>
      <div class="relative h-8 bg-bg-deep rounded-xl overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-r from-teal/10 via-purple/10 to-sky/10 animate-scan-line"></div>
      </div>
      <p class="font-mono text-data-sm text-text-muted mt-2">{$runProgress}</p>
    </Card>
  {/if}

  {#if $error}
    <Card accent="critical">
      <div class="flex items-start gap-3">
        <span class="text-accent-critical text-data-base font-semibold">Note</span>
        <p class="font-mono text-data-sm text-text-muted">{$error}</p>
      </div>
    </Card>
  {/if}

  {#if toastMessage}
    <Toast message={toastMessage} type={toastType} ondismiss={() => toastMessage = ''} />
  {/if}
</div>
