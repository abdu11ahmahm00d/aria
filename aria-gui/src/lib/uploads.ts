import { writable, derived } from 'svelte/store'
import { parseCsv, type CsvMeta } from './csv'

export interface UploadedFile {
  name: string
  meta: CsvMeta
  raw: string
}

const _grades = writable<UploadedFile | null>(null)
const _students = writable<UploadedFile | null>(null)
const _submissions = writable<UploadedFile | null>(null)

export const gradesFile = _grades
export const studentsFile = _students
export const submissionsFile = _submissions

export const allFilesReady = derived(
  [_grades, _students, _submissions],
  ([$g, $s, $sub]) => $g !== null && $s !== null && $sub !== null
)

export const uploadedNames = derived(
  [_grades, _students, _submissions],
  ([$g, $s, $sub]) => ({
    grades: $g?.meta.name ?? null,
    students: $s?.meta.name ?? null,
    submissions: $sub?.meta.name ?? null,
  })
)

export async function loadFile(file: File, type: 'grades' | 'students' | 'submissions'): Promise<void> {
  const text = await file.text()
  const parsed = parseCsv(text)
  const store = type === 'grades' ? _grades : type === 'students' ? _students : _submissions
  store.set({
    name: file.name,
    raw: text,
    meta: {
      name: file.name,
      size: formatFileSize(file.size),
      rows: parsed.rowCount,
      columns: parsed.columns,
      data: parsed.rows,
    },
  })
}

export function clearUploads() {
  _grades.set(null)
  _students.set(null)
  _submissions.set(null)
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
