import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import type { Flag, FraudType, Severity } from './types'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function computeSeverity(flags: Flag[]): Severity {
  const total = flags.length
  const types = new Set(flags.map(f => f.fraud_type))
  if (total === 0) return 'NONE'
  if (total >= 3 || (types.has('Grade Inflation') && types.has('Submission Clustering'))) return 'HIGH'
  if (total >= 2) return 'MEDIUM'
  return 'LOW'
}

export function severityColor(severity: Severity): string {
  switch (severity) {
    case 'HIGH': return '#ef4444'
    case 'MEDIUM': return '#f59e0b'
    case 'LOW': return '#10B981'
    case 'NONE': return '#71717a'
  }
}

export function fraudTypeColor(type: FraudType): string {
  switch (type) {
    case 'Grade Inflation': return '#f59e0b'
    case 'CLO Inconsistency': return '#8b5cf6'
    case 'Submission Clustering': return '#3b82f6'
    case 'CO Completion Rate': return '#ef4444'
  }
}

export function formatTimestamp(ts: string): string {
  try {
    const d = new Date(ts)
    return d.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  } catch {
    return ts
  }
}

export function groupBy<T>(items: T[], key: (item: T) => string): Record<string, T[]> {
  const groups: Record<string, T[]> = {}
  for (const item of items) {
    const k = key(item)
    if (!groups[k]) groups[k] = []
    groups[k].push(item)
  }
  return groups
}

export function findCorrelations(flags: Flag[]): string[] {
  const studentMap = new Map<string, Set<string>>()
  for (const f of flags) {
    const rid = f.record_id || ''
    for (const part of rid.split('_')) {
      if (part.startsWith('S-') || part.startsWith('STU')) {
        if (!studentMap.has(part)) studentMap.set(part, new Set())
        studentMap.get(part)!.add(f.fraud_type)
      }
    }
  }
  const correlations: string[] = []
  for (const [sid, ftypes] of studentMap) {
    if (ftypes.size > 1) {
      correlations.push(`${sid} appears in ${[...ftypes].join(', ')}`)
    }
  }
  return correlations
}

export function countByType(flags: Flag[]): Record<string, number> {
  const counts: Record<string, number> = {}
  for (const f of flags) {
    counts[f.fraud_type] = (counts[f.fraud_type] || 0) + 1
  }
  return counts
}
