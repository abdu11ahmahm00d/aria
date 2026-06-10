import { writable, derived } from 'svelte/store'
import type { Flag, RunConfig, Severity, NavItem } from './types'
import { computeSeverity, countByType } from './utils'

export const currentView = writable('hero')

export const flags = writable<Flag[]>([])
export const report = writable('')
export const isRunning = writable(false)
export const runProgress = writable('')
export const error = writable<string | null>(null)

export const severity = derived(flags, ($f) => computeSeverity($f))
export const flagCounts = derived(flags, ($f) => countByType($f))
export const totalFlags = derived(flags, ($f) => $f.length)

export const navItems: NavItem[] = [
  { id: 'dashboard', label: 'Dashboard', icon: 'LayoutDashboard' },
  { id: 'flags', label: 'Flags', icon: 'FlagTriangleRight' },
  { id: 'courses', label: 'Courses', icon: 'BookOpen' },
  { id: 'students', label: 'Students', icon: 'Users' },
  { id: 'run', label: 'Run Pipeline', icon: 'Play' },
]

export const defaultRunConfig: RunConfig = {
  gradesPath: 'data/synthetic/grades.csv',
  studentsPath: 'data/synthetic/students.csv',
  submissionsPath: 'data/synthetic/submissions.csv',
  outputDir: 'output',
  useMock: true,
}

export const runConfig = writable<RunConfig>({ ...defaultRunConfig })
