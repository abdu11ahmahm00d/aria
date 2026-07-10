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
      { "flagged": true, "fraud_type": "Grade Inflation", "record_id": "CS201_2", "confidence": 0.95, "reason": "z-score 1.92 exceeds threshold of 1.5", "evidence": { "z_score": 1.918, "avg_grade": 85.2, "historical_mean": 75.8 } },
      { "flagged": true, "fraud_type": "Grade Inflation", "record_id": "MATH301_2", "confidence": 0.95, "reason": "z-score 2.75 exceeds threshold of 1.5", "evidence": { "z_score": 2.75, "avg_grade": 99.2, "historical_mean": 79.4 } },
      { "flagged": true, "fraud_type": "Grade Inflation", "record_id": "ENG101_2", "confidence": 0.95, "reason": "z-score 1.82 exceeds threshold of 1.5", "evidence": { "z_score": 1.816, "avg_grade": 69.6, "historical_mean": 62.7 } },
      { "flagged": true, "fraud_type": "Grade Inflation", "record_id": "PHY101_3", "confidence": 0.95, "reason": "z-score 3.02 exceeds threshold of 1.5", "evidence": { "z_score": 3.015, "avg_grade": 90.4, "historical_mean": 70.2 } },
      { "flagged": true, "fraud_type": "Grade Inflation", "record_id": "CHM101_1", "confidence": 0.95, "reason": "z-score 3.06 exceeds threshold of 1.5", "evidence": { "z_score": 3.056, "avg_grade": 98.4, "historical_mean": 76.7 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU001_PHY101", "confidence": 0.95, "reason": "CLO score 24.7pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 75.3, "co_score": 100.0, "co_exam_gap": 24.7 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU022_MATH301", "confidence": 0.95, "reason": "CLO score 28.7pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 36.4, "co_score": 65.1, "co_exam_gap": 28.7 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU025_ENG101", "confidence": 0.95, "reason": "CLO score 39.1pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 47.7, "co_score": 86.8, "co_exam_gap": 39.1 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU064_MEC101", "confidence": 0.95, "reason": "CLO score 20.3pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 79.7, "co_score": 100.0, "co_exam_gap": 20.3 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU105_MATH301", "confidence": 0.95, "reason": "CLO score 27.9pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 38.7, "co_score": 66.6, "co_exam_gap": 27.9 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU125_CS201", "confidence": 0.95, "reason": "CLO score 25.0pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 75.0, "co_score": 100.0, "co_exam_gap": 25.0 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU151_CHM101", "confidence": 0.95, "reason": "CLO score 36.1pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 40.5, "co_score": 76.6, "co_exam_gap": 36.1 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU159_ENG101", "confidence": 0.95, "reason": "CLO score 27.0pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 53.3, "co_score": 80.3, "co_exam_gap": 27.0 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU159_CS201", "confidence": 0.95, "reason": "CLO score 24.1pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 75.9, "co_score": 100.0, "co_exam_gap": 24.1 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU193_MEC101", "confidence": 0.95, "reason": "CLO score 39.8pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 60.2, "co_score": 100.0, "co_exam_gap": 39.8 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU221_MATH201", "confidence": 0.95, "reason": "CLO score 28.6pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 32.7, "co_score": 61.3, "co_exam_gap": 28.6 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU225_CS101", "confidence": 0.95, "reason": "CLO score 29.1pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 42.8, "co_score": 71.9, "co_exam_gap": 29.1 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU260_CS101", "confidence": 0.95, "reason": "CLO score 32.4pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 55.3, "co_score": 87.7, "co_exam_gap": 32.4 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU262_MEC101", "confidence": 0.95, "reason": "CLO score 23.6pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 76.4, "co_score": 100.0, "co_exam_gap": 23.6 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU296_EEE101", "confidence": 0.95, "reason": "CLO score 26.7pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 32.9, "co_score": 59.6, "co_exam_gap": 26.7 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU303_MATH201", "confidence": 0.95, "reason": "CLO score 31.1pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 62.5, "co_score": 93.6, "co_exam_gap": 31.1 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU311_BUS101", "confidence": 0.95, "reason": "CLO score 32.7pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 36.3, "co_score": 69.0, "co_exam_gap": 32.7 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU312_MATH301", "confidence": 0.95, "reason": "CLO score 37.3pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 44.2, "co_score": 81.5, "co_exam_gap": 37.3 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU315_ENG101", "confidence": 0.95, "reason": "CLO score 21.0pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 79.0, "co_score": 100.0, "co_exam_gap": 21.0 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU319_CS102", "confidence": 0.95, "reason": "CLO score 27.3pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 72.7, "co_score": 100.0, "co_exam_gap": 27.3 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU319_CHM101", "confidence": 0.95, "reason": "CLO score 22.6pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 33.4, "co_score": 56.0, "co_exam_gap": 22.6 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU326_ENG201", "confidence": 0.95, "reason": "CLO score 26.0pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 73.3, "co_score": 99.3, "co_exam_gap": 26.0 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU329_PHY101", "confidence": 0.95, "reason": "CLO score 34.3pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 32.7, "co_score": 67.0, "co_exam_gap": 34.3 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU366_CS102", "confidence": 0.95, "reason": "CLO score 32.2pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 53.0, "co_score": 85.2, "co_exam_gap": 32.2 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU370_EEE101", "confidence": 0.95, "reason": "CLO score 23.8pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 76.2, "co_score": 100.0, "co_exam_gap": 23.8 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU378_CHM101", "confidence": 0.95, "reason": "CLO score 24.4pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 48.9, "co_score": 73.3, "co_exam_gap": 24.4 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU390_ENG201", "confidence": 0.95, "reason": "CLO score 24.2pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 67.1, "co_score": 91.3, "co_exam_gap": 24.2 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU403_ENG201", "confidence": 0.95, "reason": "CLO score 37.0pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 63.0, "co_score": 100.0, "co_exam_gap": 37.0 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU404_EEE101", "confidence": 0.95, "reason": "CLO score 31.6pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 64.8, "co_score": 96.4, "co_exam_gap": 31.6 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU406_CS101", "confidence": 0.95, "reason": "CLO score 25.0pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 38.5, "co_score": 63.5, "co_exam_gap": 25.0 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU412_CS102", "confidence": 0.95, "reason": "CLO score 28.1pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 43.6, "co_score": 71.7, "co_exam_gap": 28.1 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU429_CS201", "confidence": 0.95, "reason": "CLO score 22.8pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 77.2, "co_score": 100.0, "co_exam_gap": 22.8 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU435_PHY101", "confidence": 0.95, "reason": "CLO score 26.8pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 65.9, "co_score": 92.7, "co_exam_gap": 26.8 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU472_BUS101", "confidence": 0.95, "reason": "CLO score 39.0pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 61.0, "co_score": 100.0, "co_exam_gap": 39.0 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU499_CS201", "confidence": 0.95, "reason": "CLO score 32.4pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 39.2, "co_score": 71.6, "co_exam_gap": 32.4 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU503_CS201", "confidence": 0.95, "reason": "CLO score 26.5pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 37.0, "co_score": 63.5, "co_exam_gap": 26.5 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU510_CS101", "confidence": 0.95, "reason": "CLO score 39.3pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 57.1, "co_score": 96.4, "co_exam_gap": 39.3 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU511_CS102", "confidence": 0.95, "reason": "CLO score 26.0pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 62.3, "co_score": 88.3, "co_exam_gap": 26.0 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU514_CHM101", "confidence": 0.95, "reason": "CLO score 33.5pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 52.3, "co_score": 85.8, "co_exam_gap": 33.5 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU526_MATH201", "confidence": 0.95, "reason": "CLO score 25.0pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 71.5, "co_score": 96.5, "co_exam_gap": 25.0 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU526_ENG101", "confidence": 0.95, "reason": "CLO score 31.5pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 41.9, "co_score": 73.4, "co_exam_gap": 31.5 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU536_MATH301", "confidence": 0.95, "reason": "CLO score 36.0pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 45.9, "co_score": 81.9, "co_exam_gap": 36.0 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU542_PHY101", "confidence": 0.95, "reason": "CLO score 30.8pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 51.7, "co_score": 82.5, "co_exam_gap": 30.8 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU557_CS101", "confidence": 0.95, "reason": "CLO score 21.8pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 78.2, "co_score": 100.0, "co_exam_gap": 21.8 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU557_CS102", "confidence": 0.95, "reason": "CLO score 28.7pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 35.3, "co_score": 64.0, "co_exam_gap": 28.7 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU569_CHM101", "confidence": 0.95, "reason": "CLO score 29.0pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 48.1, "co_score": 77.1, "co_exam_gap": 29.0 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU588_EEE101", "confidence": 0.95, "reason": "CLO score 23.4pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 72.3, "co_score": 95.7, "co_exam_gap": 23.4 } },
      { "flagged": true, "fraud_type": "CLO Inconsistency", "record_id": "STU589_BUS101", "confidence": 0.95, "reason": "CLO score 27.3pts above exam exceeds 20pt threshold", "evidence": { "exam_score": 31.9, "co_score": 59.2, "co_exam_gap": 27.3 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN001_STU010_STU286", "confidence": 0.95, "reason": "Submissions 33s apart with 0.85 avg similarity", "evidence": { "time_diff_seconds": 33, "similarity_score": 0.855 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN003_STU331_STU031", "confidence": 0.95, "reason": "Submissions 33s apart with 0.85 avg similarity", "evidence": { "time_diff_seconds": 33, "similarity_score": 0.855 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN003_STU331_STU170", "confidence": 0.95, "reason": "Submissions 54s apart with 0.82 avg similarity", "evidence": { "time_diff_seconds": 54, "similarity_score": 0.825 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN003_STU031_STU170", "confidence": 0.95, "reason": "Submissions 21s apart with 0.85 avg similarity", "evidence": { "time_diff_seconds": 21, "similarity_score": 0.85 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN012_STU539_STU572", "confidence": 0.95, "reason": "Submissions 10s apart with 0.83 avg similarity", "evidence": { "time_diff_seconds": 10, "similarity_score": 0.83 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN013_STU415_STU086", "confidence": 0.95, "reason": "Submissions 20s apart with 0.88 avg similarity", "evidence": { "time_diff_seconds": 20, "similarity_score": 0.88 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN013_STU415_STU199", "confidence": 0.95, "reason": "Submissions 48s apart with 0.88 avg similarity", "evidence": { "time_diff_seconds": 48, "similarity_score": 0.88 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN013_STU415_STU280", "confidence": 0.95, "reason": "Submissions 81s apart with 0.86 avg similarity", "evidence": { "time_diff_seconds": 81, "similarity_score": 0.86 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN013_STU086_STU199", "confidence": 0.95, "reason": "Submissions 28s apart with 0.92 avg similarity", "evidence": { "time_diff_seconds": 28, "similarity_score": 0.92 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN013_STU086_STU280", "confidence": 0.95, "reason": "Submissions 61s apart with 0.90 avg similarity", "evidence": { "time_diff_seconds": 61, "similarity_score": 0.9 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN013_STU199_STU280", "confidence": 0.95, "reason": "Submissions 33s apart with 0.90 avg similarity", "evidence": { "time_diff_seconds": 33, "similarity_score": 0.9 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN014_STU068_STU447", "confidence": 0.95, "reason": "Submissions 20s apart with 0.86 avg similarity", "evidence": { "time_diff_seconds": 20, "similarity_score": 0.865 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN014_STU068_STU544", "confidence": 0.95, "reason": "Submissions 30s apart with 0.88 avg similarity", "evidence": { "time_diff_seconds": 30, "similarity_score": 0.875 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN014_STU447_STU544", "confidence": 0.95, "reason": "Submissions 10s apart with 0.86 avg similarity", "evidence": { "time_diff_seconds": 10, "similarity_score": 0.86 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN015_STU578_STU022", "confidence": 0.95, "reason": "Submissions 27s apart with 0.89 avg similarity", "evidence": { "time_diff_seconds": 27, "similarity_score": 0.885 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN015_STU578_STU243", "confidence": 0.95, "reason": "Submissions 38s apart with 0.88 avg similarity", "evidence": { "time_diff_seconds": 38, "similarity_score": 0.875 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN015_STU578_STU341", "confidence": 0.95, "reason": "Submissions 48s apart with 0.87 avg similarity", "evidence": { "time_diff_seconds": 48, "similarity_score": 0.87 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN015_STU022_STU243", "confidence": 0.95, "reason": "Submissions 11s apart with 0.90 avg similarity", "evidence": { "time_diff_seconds": 11, "similarity_score": 0.9 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN015_STU022_STU341", "confidence": 0.95, "reason": "Submissions 21s apart with 0.90 avg similarity", "evidence": { "time_diff_seconds": 21, "similarity_score": 0.895 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN015_STU243_STU341", "confidence": 0.95, "reason": "Submissions 10s apart with 0.89 avg similarity", "evidence": { "time_diff_seconds": 10, "similarity_score": 0.885 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN017_STU227_STU164", "confidence": 0.95, "reason": "Submissions 10s apart with 0.87 avg similarity", "evidence": { "time_diff_seconds": 10, "similarity_score": 0.87 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN018_STU227_STU049", "confidence": 0.95, "reason": "Submissions 21s apart with 0.86 avg similarity", "evidence": { "time_diff_seconds": 21, "similarity_score": 0.8600000000000001 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN019_STU446_STU250", "confidence": 0.95, "reason": "Submissions 34s apart with 0.87 avg similarity", "evidence": { "time_diff_seconds": 34, "similarity_score": 0.87 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN019_STU446_STU173", "confidence": 0.95, "reason": "Submissions 45s apart with 0.91 avg similarity", "evidence": { "time_diff_seconds": 45, "similarity_score": 0.91 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN019_STU446_STU320", "confidence": 0.95, "reason": "Submissions 54s apart with 0.91 avg similarity", "evidence": { "time_diff_seconds": 54, "similarity_score": 0.905 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN019_STU250_STU173", "confidence": 0.95, "reason": "Submissions 11s apart with 0.89 avg similarity", "evidence": { "time_diff_seconds": 11, "similarity_score": 0.89 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN019_STU250_STU320", "confidence": 0.95, "reason": "Submissions 20s apart with 0.89 avg similarity", "evidence": { "time_diff_seconds": 20, "similarity_score": 0.885 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN019_STU173_STU320", "confidence": 0.95, "reason": "Submissions 9s apart with 0.93 avg similarity", "evidence": { "time_diff_seconds": 9, "similarity_score": 0.925 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN025_STU367_STU137", "confidence": 0.95, "reason": "Submissions 17s apart with 0.94 avg similarity", "evidence": { "time_diff_seconds": 17, "similarity_score": 0.94 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN025_STU367_STU161", "confidence": 0.95, "reason": "Submissions 38s apart with 0.88 avg similarity", "evidence": { "time_diff_seconds": 38, "similarity_score": 0.875 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN025_STU137_STU161", "confidence": 0.95, "reason": "Submissions 21s apart with 0.89 avg similarity", "evidence": { "time_diff_seconds": 21, "similarity_score": 0.885 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN027_STU330_STU401", "confidence": 0.95, "reason": "Submissions 10s apart with 0.83 avg similarity", "evidence": { "time_diff_seconds": 10, "similarity_score": 0.8300000000000001 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN027_STU330_STU006", "confidence": 0.95, "reason": "Submissions 78s apart with 0.78 avg similarity", "evidence": { "time_diff_seconds": 78, "similarity_score": 0.775 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN027_STU401_STU006", "confidence": 0.95, "reason": "Submissions 68s apart with 0.83 avg similarity", "evidence": { "time_diff_seconds": 68, "similarity_score": 0.835 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN030_STU043_STU271", "confidence": 0.95, "reason": "Submissions 38s apart with 0.87 avg similarity", "evidence": { "time_diff_seconds": 38, "similarity_score": 0.87 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN038_STU460_STU251", "confidence": 0.95, "reason": "Submissions 11s apart with 0.82 avg similarity", "evidence": { "time_diff_seconds": 11, "similarity_score": 0.825 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN043_STU230_STU439", "confidence": 0.95, "reason": "Submissions 28s apart with 0.87 avg similarity", "evidence": { "time_diff_seconds": 28, "similarity_score": 0.8700000000000001 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN043_STU230_STU032", "confidence": 0.95, "reason": "Submissions 56s apart with 0.81 avg similarity", "evidence": { "time_diff_seconds": 56, "similarity_score": 0.805 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN043_STU439_STU032", "confidence": 0.95, "reason": "Submissions 28s apart with 0.86 avg similarity", "evidence": { "time_diff_seconds": 28, "similarity_score": 0.865 } },
      { "flagged": true, "fraud_type": "Submission Clustering", "record_id": "ASSIGN044_STU327_STU180", "confidence": 0.95, "reason": "Submissions 24s apart with 0.82 avg similarity", "evidence": { "time_diff_seconds": 24, "similarity_score": 0.825 } },
      { "flagged": true, "fraud_type": "CLO Completion Rate", "record_id": "PHY101_Fall2024", "confidence": 0.95, "reason": "100% attainment in cohort of 67 students is implausible", "evidence": { "student_count": 67, "co_attainment_rate": 1.0 } }
    ]
  }

  function generateMockReport(): string {
    return [
      'ACADEMIC INTEGRITY AND OBE ANALYTICS REPORT',
      '=============================================',
      '',
      'Total Flags Detected: 94',
      '',
      'Grade Inflation (5):',
      '  1. Record: CS201_2',
      '  2. Record: MATH301_2',
      '  3. Record: ENG101_2',
      '  4. Record: PHY101_3',
      '  5. Record: CHM101_1',
      '',
      'CLO Inconsistency (48):',
      '  1. Record: STU001_PHY101',
      '  2. Record: STU022_MATH301',
      '  3. Record: STU025_ENG101',
      '  4. Record: STU064_MEC101',
      '  5. Record: STU105_MATH301',
      '  6. Record: STU125_CS201',
      '  7. Record: STU151_CHM101',
      '  8. Record: STU159_ENG101',
      '  9. Record: STU159_CS201',
      '  10. Record: STU193_MEC101',
      '  11. Record: STU221_MATH201',
      '  12. Record: STU225_CS101',
      '  13. Record: STU260_CS101',
      '  14. Record: STU262_MEC101',
      '  15. Record: STU296_EEE101',
      '  16. Record: STU303_MATH201',
      '  17. Record: STU311_BUS101',
      '  18. Record: STU312_MATH301',
      '  19. Record: STU315_ENG101',
      '  20. Record: STU319_CS102',
      '  21. Record: STU319_CHM101',
      '  22. Record: STU326_ENG201',
      '  23. Record: STU329_PHY101',
      '  24. Record: STU366_CS102',
      '  25. Record: STU370_EEE101',
      '  26. Record: STU378_CHM101',
      '  27. Record: STU390_ENG201',
      '  28. Record: STU403_ENG201',
      '  29. Record: STU404_EEE101',
      '  30. Record: STU406_CS101',
      '  31. Record: STU412_CS102',
      '  32. Record: STU429_CS201',
      '  33. Record: STU435_PHY101',
      '  34. Record: STU472_BUS101',
      '  35. Record: STU499_CS201',
      '  36. Record: STU503_CS201',
      '  37. Record: STU510_CS101',
      '  38. Record: STU511_CS102',
      '  39. Record: STU514_CHM101',
      '  40. Record: STU526_MATH201',
      '  41. Record: STU526_ENG101',
      '  42. Record: STU536_MATH301',
      '  43. Record: STU542_PHY101',
      '  44. Record: STU557_CS101',
      '  45. Record: STU557_CS102',
      '  46. Record: STU569_CHM101',
      '  47. Record: STU588_EEE101',
      '  48. Record: STU589_BUS101',
      '',
      'Submission Clustering (40):',
      '  1. Record: ASSIGN001_STU010_STU286',
      '  2. Record: ASSIGN003_STU331_STU031',
      '  3. Record: ASSIGN003_STU331_STU170',
      '  4. Record: ASSIGN003_STU031_STU170',
      '  5. Record: ASSIGN012_STU539_STU572',
      '  6. Record: ASSIGN013_STU415_STU086',
      '  7. Record: ASSIGN013_STU415_STU199',
      '  8. Record: ASSIGN013_STU415_STU280',
      '  9. Record: ASSIGN013_STU086_STU199',
      '  10. Record: ASSIGN013_STU086_STU280',
      '  11. Record: ASSIGN013_STU199_STU280',
      '  12. Record: ASSIGN014_STU068_STU447',
      '  13. Record: ASSIGN014_STU068_STU544',
      '  14. Record: ASSIGN014_STU447_STU544',
      '  15. Record: ASSIGN015_STU578_STU022',
      '  16. Record: ASSIGN015_STU578_STU243',
      '  16. Record: ASSIGN015_STU578_STU341',
      '  17. Record: ASSIGN015_STU022_STU243',
      '  18. Record: ASSIGN015_STU022_STU341',
      '  19. Record: ASSIGN015_STU243_STU341',
      '  20. Record: ASSIGN017_STU227_STU164',
      '  21. Record: ASSIGN018_STU227_STU049',
      '  22. Record: ASSIGN019_STU446_STU250',
      '  23. Record: ASSIGN019_STU446_STU173',
      '  24. Record: ASSIGN019_STU446_STU320',
      '  25. Record: ASSIGN019_STU250_STU173',
      '  26. Record: ASSIGN019_STU250_STU320',
      '  27. Record: ASSIGN019_STU173_STU320',
      '  28. Record: ASSIGN025_STU367_STU137',
      '  29. Record: ASSIGN025_STU367_STU161',
      '  30. Record: ASSIGN025_STU137_STU161',
      '  31. Record: ASSIGN027_STU330_STU401',
      '  32. Record: ASSIGN027_STU330_STU006',
      '  33. Record: ASSIGN027_STU401_STU006',
      '  34. Record: ASSIGN030_STU043_STU271',
      '  35. Record: ASSIGN038_STU460_STU251',
      '  36. Record: ASSIGN043_STU230_STU439',
      '  37. Record: ASSIGN043_STU230_STU032',
      '  38. Record: ASSIGN043_STU439_STU032',
      '  39. Record: ASSIGN044_STU327_STU180',
      '',
      'CLO Completion Rate (1):',
      '  1. Record: PHY101_Fall2024',
      '',
      'Correlations Identified:',
      '  - Cross-type student: STU022 flagged in 2 fraud types (CLO Inconsistency, Submission Clustering)',
      '  - Multi-flagged course: CHM101 flagged in 2 fraud types (CLO Inconsistency, Grade Inflation)',
      '  - Multi-flagged course: CS201 flagged in 2 fraud types (CLO Inconsistency, Grade Inflation)',
      '  - Multi-flagged course: ENG101 flagged in 2 fraud types (CLO Inconsistency, Grade Inflation)',
      '  - Multi-flagged course: MATH301 flagged in 2 fraud types (CLO Inconsistency, Grade Inflation)',
      '  - Multi-flagged course: PHY101 flagged in 3 fraud types (CLO Inconsistency, CLO Completion Rate, Grade Inflation)',
      '  - Dense cluster assignment: ASSIGN013 has 6 flagged submission pairs',
      '  - Dense cluster assignment: ASSIGN015 has 6 flagged submission pairs',
      '  - Dense cluster assignment: ASSIGN019 has 6 flagged submission pairs',
      '  - Dense cluster assignment: ASSIGN003 has 3 flagged submission pairs',
      '  - Dense cluster assignment: ASSIGN014 has 3 flagged submission pairs',
      '  - Dense cluster assignment: ASSIGN025 has 3 flagged submission pairs',
      '  - Dense cluster assignment: ASSIGN027 has 3 flagged submission pairs',
      '  - Dense cluster assignment: ASSIGN043 has 3 flagged submission pairs',
      '  - Cross-assignment student: STU227 appears in clusters across 2 different assignments',
      '',
      'Estimated Impact on CLO Attainment: 1 CLO Completion Rate flag(s) detected. Exclusion of these records may reduce cohort attainment rates; requires recomputation of CLO attainment without flagged records.',
      '',
      'Overall Severity: HIGH',
      '',
      'Recommended Actions:',
      '  1. Review flagged records for potential academic misconduct.',
      '  2. Investigate grade anomalies in identified courses.',
      '  3. Examine submission timelines for potential collusion.',
      '  4. Verify CLO assessments and exam scores for discrepancies.',
      '  5. Audit cohort attainment rates for possible data errors.',
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
