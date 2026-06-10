export interface CsvMeta {
  name: string
  size: string
  rows: number
  columns: string[]
  data: Record<string, string>[]
}

export function parseCsv(text: string): { columns: string[]; rows: Record<string, string>[]; rowCount: number } {
  const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 0)
  if (lines.length < 2) return { columns: [], rows: [], rowCount: 0 }

  const headers = parseLine(lines[0])
  const rows: Record<string, string>[] = []

  for (let i = 1; i < lines.length; i++) {
    const vals = parseLine(lines[i])
    const row: Record<string, string> = {}
    headers.forEach((h, j) => { row[h] = vals[j] ?? '' })
    rows.push(row)
  }

  return { columns: headers, rows, rowCount: rows.length }
}

function parseLine(line: string): string[] {
  const result: string[] = []
  let current = ''
  let inQuotes = false

  for (const ch of line) {
    if (ch === '"') { inQuotes = !inQuotes; continue }
    if (ch === ',' && !inQuotes) { result.push(current.trim()); current = ''; continue }
    current += ch
  }
  result.push(current.trim())

  return result
}

export function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export function extractStudentIds(data: Record<string, string>[]): string[] {
  const ids = new Set<string>()
  for (const row of data) {
    for (const val of Object.values(row)) {
      const match = val.match(/STU\d{3,}/g)
      if (match) match.forEach(m => ids.add(m))
    }
  }
  return [...ids].sort()
}

export function extractCourseCodes(data: Record<string, string>[]): string[] {
  const codes = new Set<string>()
  for (const row of data) {
    for (const val of Object.values(row)) {
      const match = val.match(/[A-Z]{2,4}\d{3,4}/g)
      if (match) match.forEach(m => codes.add(m))
    }
  }
  return [...codes].sort()
}
