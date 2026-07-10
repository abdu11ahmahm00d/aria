<script lang="ts">
import { currentView, flags, isRunning, runProgress, report, error } from './lib/stores'
  import { gradesFile, studentsFile, submissionsFile, allFilesReady, loadFile } from './lib/uploads'
  import Sidebar from './lib/components/Sidebar.svelte'
  import UploadRow from './lib/components/UploadRow.svelte'
  import Dashboard from './pages/Dashboard.svelte'
  import FlagsPage from './pages/FlagsPage.svelte'
  import CoursesPage from './pages/CoursesPage.svelte'
  import StudentsPage from './pages/StudentsPage.svelte'
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

  const delay = (ms: number) => new Promise(r => setTimeout(r, ms))

  function runHeroPipeline() {
    isRunning.set(true)
    runProgress.set('Initializing ARIA pipeline...')
    error.set(null)

    setTimeout(async () => {
      runProgress.set('Analyzing grade inflation...')
      await delay(150)
      runProgress.set('Checking CLO consistency...')
      await delay(150)
      runProgress.set('Detecting submission clusters...')
      await delay(150)
      runProgress.set('Checking completion rates...')
      await delay(150)
      runProgress.set('Generating report...')

      const mockFlags: Flag[] = [
        { flagged: true, fraud_type: 'Grade Inflation', record_id: 'CS201_2', confidence: 0.95, reason: 'z-score 1.92 exceeds threshold of 1.5', evidence: { z_score: 1.918, avg_grade: 85.2, historical_mean: 75.8 } },
        { flagged: true, fraud_type: 'Grade Inflation', record_id: 'MATH301_2', confidence: 0.95, reason: 'z-score 2.75 exceeds threshold of 1.5', evidence: { z_score: 2.75, avg_grade: 99.2, historical_mean: 79.4 } },
        { flagged: true, fraud_type: 'Grade Inflation', record_id: 'ENG101_2', confidence: 0.95, reason: 'z-score 1.82 exceeds threshold of 1.5', evidence: { z_score: 1.816, avg_grade: 69.6, historical_mean: 62.7 } },
        { flagged: true, fraud_type: 'Grade Inflation', record_id: 'PHY101_3', confidence: 0.95, reason: 'z-score 3.02 exceeds threshold of 1.5', evidence: { z_score: 3.015, avg_grade: 90.4, historical_mean: 70.2 } },
        { flagged: true, fraud_type: 'Grade Inflation', record_id: 'CHM101_1', confidence: 0.95, reason: 'z-score 3.06 exceeds threshold of 1.5', evidence: { z_score: 3.056, avg_grade: 98.4, historical_mean: 76.7 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU001_PHY101', confidence: 0.95, reason: 'CLO score 24.7pts above exam exceeds 20pt threshold', evidence: { exam_score: 75.3, co_score: 100.0, co_exam_gap: 24.7 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU022_MATH301', confidence: 0.95, reason: 'CLO score 28.7pts above exam exceeds 20pt threshold', evidence: { exam_score: 36.4, co_score: 65.1, co_exam_gap: 28.7 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU025_ENG101', confidence: 0.95, reason: 'CLO score 39.1pts above exam exceeds 20pt threshold', evidence: { exam_score: 47.7, co_score: 86.8, co_exam_gap: 39.1 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU064_MEC101', confidence: 0.95, reason: 'CLO score 20.3pts above exam exceeds 20pt threshold', evidence: { exam_score: 79.7, co_score: 100.0, co_exam_gap: 20.3 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU105_MATH301', confidence: 0.95, reason: 'CLO score 27.9pts above exam exceeds 20pt threshold', evidence: { exam_score: 38.7, co_score: 66.6, co_exam_gap: 27.9 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU125_CS201', confidence: 0.95, reason: 'CLO score 25.0pts above exam exceeds 20pt threshold', evidence: { exam_score: 75.0, co_score: 100.0, co_exam_gap: 25.0 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU151_CHM101', confidence: 0.95, reason: 'CLO score 36.1pts above exam exceeds 20pt threshold', evidence: { exam_score: 40.5, co_score: 76.6, co_exam_gap: 36.1 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU159_ENG101', confidence: 0.95, reason: 'CLO score 27.0pts above exam exceeds 20pt threshold', evidence: { exam_score: 53.3, co_score: 80.3, co_exam_gap: 27.0 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU159_CS201', confidence: 0.95, reason: 'CLO score 24.1pts above exam exceeds 20pt threshold', evidence: { exam_score: 75.9, co_score: 100.0, co_exam_gap: 24.1 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU193_MEC101', confidence: 0.95, reason: 'CLO score 39.8pts above exam exceeds 20pt threshold', evidence: { exam_score: 60.2, co_score: 100.0, co_exam_gap: 39.8 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU221_MATH201', confidence: 0.95, reason: 'CLO score 28.6pts above exam exceeds 20pt threshold', evidence: { exam_score: 32.7, co_score: 61.3, co_exam_gap: 28.6 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU225_CS101', confidence: 0.95, reason: 'CLO score 29.1pts above exam exceeds 20pt threshold', evidence: { exam_score: 42.8, co_score: 71.9, co_exam_gap: 29.1 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU260_CS101', confidence: 0.95, reason: 'CLO score 32.4pts above exam exceeds 20pt threshold', evidence: { exam_score: 55.3, co_score: 87.7, co_exam_gap: 32.4 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU262_MEC101', confidence: 0.95, reason: 'CLO score 23.6pts above exam exceeds 20pt threshold', evidence: { exam_score: 76.4, co_score: 100.0, co_exam_gap: 23.6 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU296_EEE101', confidence: 0.95, reason: 'CLO score 26.7pts above exam exceeds 20pt threshold', evidence: { exam_score: 32.9, co_score: 59.6, co_exam_gap: 26.7 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU303_MATH201', confidence: 0.95, reason: 'CLO score 31.1pts above exam exceeds 20pt threshold', evidence: { exam_score: 62.5, co_score: 93.6, co_exam_gap: 31.1 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU311_BUS101', confidence: 0.95, reason: 'CLO score 32.7pts above exam exceeds 20pt threshold', evidence: { exam_score: 36.3, co_score: 69.0, co_exam_gap: 32.7 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU312_MATH301', confidence: 0.95, reason: 'CLO score 37.3pts above exam exceeds 20pt threshold', evidence: { exam_score: 44.2, co_score: 81.5, co_exam_gap: 37.3 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU315_ENG101', confidence: 0.95, reason: 'CLO score 21.0pts above exam exceeds 20pt threshold', evidence: { exam_score: 79.0, co_score: 100.0, co_exam_gap: 21.0 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU319_CS102', confidence: 0.95, reason: 'CLO score 27.3pts above exam exceeds 20pt threshold', evidence: { exam_score: 72.7, co_score: 100.0, co_exam_gap: 27.3 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU319_CHM101', confidence: 0.95, reason: 'CLO score 22.6pts above exam exceeds 20pt threshold', evidence: { exam_score: 33.4, co_score: 56.0, co_exam_gap: 22.6 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU326_ENG201', confidence: 0.95, reason: 'CLO score 26.0pts above exam exceeds 20pt threshold', evidence: { exam_score: 73.3, co_score: 99.3, co_exam_gap: 26.0 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU329_PHY101', confidence: 0.95, reason: 'CLO score 34.3pts above exam exceeds 20pt threshold', evidence: { exam_score: 32.7, co_score: 67.0, co_exam_gap: 34.3 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU366_CS102', confidence: 0.95, reason: 'CLO score 32.2pts above exam exceeds 20pt threshold', evidence: { exam_score: 53.0, co_score: 85.2, co_exam_gap: 32.2 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU370_EEE101', confidence: 0.95, reason: 'CLO score 23.8pts above exam exceeds 20pt threshold', evidence: { exam_score: 76.2, co_score: 100.0, co_exam_gap: 23.8 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU378_CHM101', confidence: 0.95, reason: 'CLO score 24.4pts above exam exceeds 20pt threshold', evidence: { exam_score: 48.9, co_score: 73.3, co_exam_gap: 24.4 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU390_ENG201', confidence: 0.95, reason: 'CLO score 24.2pts above exam exceeds 20pt threshold', evidence: { exam_score: 67.1, co_score: 91.3, co_exam_gap: 24.2 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU403_ENG201', confidence: 0.95, reason: 'CLO score 37.0pts above exam exceeds 20pt threshold', evidence: { exam_score: 63.0, co_score: 100.0, co_exam_gap: 37.0 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU404_EEE101', confidence: 0.95, reason: 'CLO score 31.6pts above exam exceeds 20pt threshold', evidence: { exam_score: 64.8, co_score: 96.4, co_exam_gap: 31.6 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU406_CS101', confidence: 0.95, reason: 'CLO score 25.0pts above exam exceeds 20pt threshold', evidence: { exam_score: 38.5, co_score: 63.5, co_exam_gap: 25.0 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU412_CS102', confidence: 0.95, reason: 'CLO score 28.1pts above exam exceeds 20pt threshold', evidence: { exam_score: 43.6, co_score: 71.7, co_exam_gap: 28.1 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU429_CS201', confidence: 0.95, reason: 'CLO score 22.8pts above exam exceeds 20pt threshold', evidence: { exam_score: 77.2, co_score: 100.0, co_exam_gap: 22.8 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU435_PHY101', confidence: 0.95, reason: 'CLO score 26.8pts above exam exceeds 20pt threshold', evidence: { exam_score: 65.9, co_score: 92.7, co_exam_gap: 26.8 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU472_BUS101', confidence: 0.95, reason: 'CLO score 39.0pts above exam exceeds 20pt threshold', evidence: { exam_score: 61.0, co_score: 100.0, co_exam_gap: 39.0 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU499_CS201', confidence: 0.95, reason: 'CLO score 32.4pts above exam exceeds 20pt threshold', evidence: { exam_score: 39.2, co_score: 71.6, co_exam_gap: 32.4 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU503_CS201', confidence: 0.95, reason: 'CLO score 26.5pts above exam exceeds 20pt threshold', evidence: { exam_score: 37.0, co_score: 63.5, co_exam_gap: 26.5 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU510_CS101', confidence: 0.95, reason: 'CLO score 39.3pts above exam exceeds 20pt threshold', evidence: { exam_score: 57.1, co_score: 96.4, co_exam_gap: 39.3 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU511_CS102', confidence: 0.95, reason: 'CLO score 26.0pts above exam exceeds 20pt threshold', evidence: { exam_score: 62.3, co_score: 88.3, co_exam_gap: 26.0 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU514_CHM101', confidence: 0.95, reason: 'CLO score 33.5pts above exam exceeds 20pt threshold', evidence: { exam_score: 52.3, co_score: 85.8, co_exam_gap: 33.5 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU526_MATH201', confidence: 0.95, reason: 'CLO score 25.0pts above exam exceeds 20pt threshold', evidence: { exam_score: 71.5, co_score: 96.5, co_exam_gap: 25.0 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU526_ENG101', confidence: 0.95, reason: 'CLO score 31.5pts above exam exceeds 20pt threshold', evidence: { exam_score: 41.9, co_score: 73.4, co_exam_gap: 31.5 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU536_MATH301', confidence: 0.95, reason: 'CLO score 36.0pts above exam exceeds 20pt threshold', evidence: { exam_score: 45.9, co_score: 81.9, co_exam_gap: 36.0 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU542_PHY101', confidence: 0.95, reason: 'CLO score 30.8pts above exam exceeds 20pt threshold', evidence: { exam_score: 51.7, co_score: 82.5, co_exam_gap: 30.8 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU557_CS101', confidence: 0.95, reason: 'CLO score 21.8pts above exam exceeds 20pt threshold', evidence: { exam_score: 78.2, co_score: 100.0, co_exam_gap: 21.8 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU557_CS102', confidence: 0.95, reason: 'CLO score 28.7pts above exam exceeds 20pt threshold', evidence: { exam_score: 35.3, co_score: 64.0, co_exam_gap: 28.7 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU569_CHM101', confidence: 0.95, reason: 'CLO score 29.0pts above exam exceeds 20pt threshold', evidence: { exam_score: 48.1, co_score: 77.1, co_exam_gap: 29.0 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU588_EEE101', confidence: 0.95, reason: 'CLO score 23.4pts above exam exceeds 20pt threshold', evidence: { exam_score: 72.3, co_score: 95.7, co_exam_gap: 23.4 } },
        { flagged: true, fraud_type: 'CLO Inconsistency', record_id: 'STU589_BUS101', confidence: 0.95, reason: 'CLO score 27.3pts above exam exceeds 20pt threshold', evidence: { exam_score: 31.9, co_score: 59.2, co_exam_gap: 27.3 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN001_STU010_STU286', confidence: 0.95, reason: 'Submissions 33s apart with 0.85 avg similarity', evidence: { time_diff_seconds: 33, similarity_score: 0.855 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN003_STU331_STU031', confidence: 0.95, reason: 'Submissions 33s apart with 0.85 avg similarity', evidence: { time_diff_seconds: 33, similarity_score: 0.855 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN003_STU331_STU170', confidence: 0.95, reason: 'Submissions 54s apart with 0.82 avg similarity', evidence: { time_diff_seconds: 54, similarity_score: 0.825 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN003_STU031_STU170', confidence: 0.95, reason: 'Submissions 21s apart with 0.85 avg similarity', evidence: { time_diff_seconds: 21, similarity_score: 0.85 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN012_STU539_STU572', confidence: 0.95, reason: 'Submissions 10s apart with 0.83 avg similarity', evidence: { time_diff_seconds: 10, similarity_score: 0.83 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN013_STU415_STU086', confidence: 0.95, reason: 'Submissions 20s apart with 0.88 avg similarity', evidence: { time_diff_seconds: 20, similarity_score: 0.88 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN013_STU415_STU199', confidence: 0.95, reason: 'Submissions 48s apart with 0.88 avg similarity', evidence: { time_diff_seconds: 48, similarity_score: 0.88 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN013_STU415_STU280', confidence: 0.95, reason: 'Submissions 81s apart with 0.86 avg similarity', evidence: { time_diff_seconds: 81, similarity_score: 0.86 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN013_STU086_STU199', confidence: 0.95, reason: 'Submissions 28s apart with 0.92 avg similarity', evidence: { time_diff_seconds: 28, similarity_score: 0.92 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN013_STU086_STU280', confidence: 0.95, reason: 'Submissions 61s apart with 0.90 avg similarity', evidence: { time_diff_seconds: 61, similarity_score: 0.9 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN013_STU199_STU280', confidence: 0.95, reason: 'Submissions 33s apart with 0.90 avg similarity', evidence: { time_diff_seconds: 33, similarity_score: 0.9 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN014_STU068_STU447', confidence: 0.95, reason: 'Submissions 20s apart with 0.86 avg similarity', evidence: { time_diff_seconds: 20, similarity_score: 0.865 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN014_STU068_STU544', confidence: 0.95, reason: 'Submissions 30s apart with 0.88 avg similarity', evidence: { time_diff_seconds: 30, similarity_score: 0.875 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN014_STU447_STU544', confidence: 0.95, reason: 'Submissions 10s apart with 0.86 avg similarity', evidence: { time_diff_seconds: 10, similarity_score: 0.86 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN015_STU578_STU022', confidence: 0.95, reason: 'Submissions 27s apart with 0.89 avg similarity', evidence: { time_diff_seconds: 27, similarity_score: 0.885 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN015_STU578_STU243', confidence: 0.95, reason: 'Submissions 38s apart with 0.88 avg similarity', evidence: { time_diff_seconds: 38, similarity_score: 0.875 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN015_STU578_STU341', confidence: 0.95, reason: 'Submissions 48s apart with 0.87 avg similarity', evidence: { time_diff_seconds: 48, similarity_score: 0.87 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN015_STU022_STU243', confidence: 0.95, reason: 'Submissions 11s apart with 0.90 avg similarity', evidence: { time_diff_seconds: 11, similarity_score: 0.9 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN015_STU022_STU341', confidence: 0.95, reason: 'Submissions 21s apart with 0.90 avg similarity', evidence: { time_diff_seconds: 21, similarity_score: 0.895 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN015_STU243_STU341', confidence: 0.95, reason: 'Submissions 10s apart with 0.89 avg similarity', evidence: { time_diff_seconds: 10, similarity_score: 0.885 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN017_STU227_STU164', confidence: 0.95, reason: 'Submissions 10s apart with 0.87 avg similarity', evidence: { time_diff_seconds: 10, similarity_score: 0.87 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN018_STU227_STU049', confidence: 0.95, reason: 'Submissions 21s apart with 0.86 avg similarity', evidence: { time_diff_seconds: 21, similarity_score: 0.8600000000000001 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN019_STU446_STU250', confidence: 0.95, reason: 'Submissions 34s apart with 0.87 avg similarity', evidence: { time_diff_seconds: 34, similarity_score: 0.87 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN019_STU446_STU173', confidence: 0.95, reason: 'Submissions 45s apart with 0.91 avg similarity', evidence: { time_diff_seconds: 45, similarity_score: 0.91 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN019_STU446_STU320', confidence: 0.95, reason: 'Submissions 54s apart with 0.91 avg similarity', evidence: { time_diff_seconds: 54, similarity_score: 0.905 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN019_STU250_STU173', confidence: 0.95, reason: 'Submissions 11s apart with 0.89 avg similarity', evidence: { time_diff_seconds: 11, similarity_score: 0.89 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN019_STU250_STU320', confidence: 0.95, reason: 'Submissions 20s apart with 0.89 avg similarity', evidence: { time_diff_seconds: 20, similarity_score: 0.885 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN019_STU173_STU320', confidence: 0.95, reason: 'Submissions 9s apart with 0.93 avg similarity', evidence: { time_diff_seconds: 9, similarity_score: 0.925 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN025_STU367_STU137', confidence: 0.95, reason: 'Submissions 17s apart with 0.94 avg similarity', evidence: { time_diff_seconds: 17, similarity_score: 0.94 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN025_STU367_STU161', confidence: 0.95, reason: 'Submissions 38s apart with 0.88 avg similarity', evidence: { time_diff_seconds: 38, similarity_score: 0.875 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN025_STU137_STU161', confidence: 0.95, reason: 'Submissions 21s apart with 0.89 avg similarity', evidence: { time_diff_seconds: 21, similarity_score: 0.885 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN027_STU330_STU401', confidence: 0.95, reason: 'Submissions 10s apart with 0.83 avg similarity', evidence: { time_diff_seconds: 10, similarity_score: 0.8300000000000001 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN027_STU330_STU006', confidence: 0.95, reason: 'Submissions 78s apart with 0.78 avg similarity', evidence: { time_diff_seconds: 78, similarity_score: 0.775 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN027_STU401_STU006', confidence: 0.95, reason: 'Submissions 68s apart with 0.83 avg similarity', evidence: { time_diff_seconds: 68, similarity_score: 0.835 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN030_STU043_STU271', confidence: 0.95, reason: 'Submissions 38s apart with 0.87 avg similarity', evidence: { time_diff_seconds: 38, similarity_score: 0.87 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN038_STU460_STU251', confidence: 0.95, reason: 'Submissions 11s apart with 0.82 avg similarity', evidence: { time_diff_seconds: 11, similarity_score: 0.825 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN043_STU230_STU439', confidence: 0.95, reason: 'Submissions 28s apart with 0.87 avg similarity', evidence: { time_diff_seconds: 28, similarity_score: 0.8700000000000001 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN043_STU230_STU032', confidence: 0.95, reason: 'Submissions 56s apart with 0.81 avg similarity', evidence: { time_diff_seconds: 56, similarity_score: 0.805 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN043_STU439_STU032', confidence: 0.95, reason: 'Submissions 28s apart with 0.86 avg similarity', evidence: { time_diff_seconds: 28, similarity_score: 0.865 } },
        { flagged: true, fraud_type: 'Submission Clustering', record_id: 'ASSIGN044_STU327_STU180', confidence: 0.95, reason: 'Submissions 24s apart with 0.82 avg similarity', evidence: { time_diff_seconds: 24, similarity_score: 0.825 } },
        { flagged: true, fraud_type: 'CO Completion Rate', record_id: 'PHY101_Fall2024', confidence: 0.95, reason: '100% attainment in cohort of 67 students is implausible', evidence: { student_count: 67, co_attainment_rate: 1.0 } },
      ]

      flags.set(mockFlags)
      report.set('ACADEMIC INTEGRITY AND OBE ANALYTICS REPORT\n' +
        '=============================================\n\n' +
        `Total Flags Detected: ${mockFlags.length}\n\n` +
        'Grade Inflation (5):\n  1. Record: CS201_2\n  2. Record: MATH301_2\n  3. Record: ENG101_2\n  4. Record: PHY101_3\n  5. Record: CHM101_1\n\n' +
        'CLO Inconsistency (48):\n  (see dashboard for full list)\n\n' +
        'Submission Clustering (40):\n  (see dashboard for full list)\n\n' +
        'CO Completion Rate (1):\n  1. Record: PHY101_Fall2024\n\n' +
        'Correlations Identified:\n  - Cross-type student: STU022 flagged in 2 fraud types (CLO Inconsistency, Submission Clustering)\n  - Multi-flagged course: CHM101 flagged in 2 fraud types (CLO Inconsistency, Grade Inflation)\n  - Multi-flagged course: CS201 flagged in 2 fraud types (CLO Inconsistency, Grade Inflation)\n  - Multi-flagged course: ENG101 flagged in 2 fraud types (CLO Inconsistency, Grade Inflation)\n  - Multi-flagged course: MATH301 flagged in 2 fraud types (CLO Inconsistency, Grade Inflation)\n  - Multi-flagged course: PHY101 flagged in 3 fraud types (CLO Inconsistency, CO Completion Rate, Grade Inflation)\n  - Dense cluster assignment: ASSIGN013 has 6 flagged submission pairs\n  - Dense cluster assignment: ASSIGN015 has 6 flagged submission pairs\n  - Dense cluster assignment: ASSIGN019 has 6 flagged submission pairs\n  - Dense cluster assignment: ASSIGN003 has 3 flagged submission pairs\n  - Dense cluster assignment: ASSIGN014 has 3 flagged submission pairs\n  - Dense cluster assignment: ASSIGN025 has 3 flagged submission pairs\n  - Dense cluster assignment: ASSIGN027 has 3 flagged submission pairs\n  - Dense cluster assignment: ASSIGN043 has 3 flagged submission pairs\n  - Cross-assignment student: STU227 appears in clusters across 2 different assignments\n\n' +
        'Overall Severity: HIGH\n\n' +
        'Recommended Actions:\n  1. Review flagged records for potential academic misconduct.\n  2. Investigate grade anomalies in identified courses.\n  3. Examine submission timelines for potential collusion.\n  4. Verify CLO assessments and exam scores for discrepancies.\n  5. Audit cohort attainment rates for possible data errors.')
      isRunning.set(false)
      runProgress.set('')

      currentView.set('dashboard')
    }, 1500)
  }
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