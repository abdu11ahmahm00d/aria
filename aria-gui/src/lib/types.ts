export interface Flag {
  flagged: boolean;
  fraud_type: FraudType;
  record_id: string;
  confidence: number;
  reason: string;
  evidence: Record<string, unknown>;
}

export type FraudType = 'Grade Inflation' | 'CLO Inconsistency' | 'Submission Clustering' | 'CO Completion Rate';

export type Severity = 'NONE' | 'LOW' | 'MEDIUM' | 'HIGH';

export interface PipelineResult {
  flags: Flag[];
  report: string;
}

export interface RunConfig {
  gradesPath: string;
  studentsPath: string;
  submissionsPath: string;
  outputDir: string;
  useMock: boolean;
}

export interface NavItem {
  id: string;
  label: string;
  icon: string;
  badge?: number;
}
