export type JobState = 'PENDING' | 'PROGRESS' | 'SUCCESS' | 'FAILURE' | 'REVOKED'

export interface Job {
  localId: string
  file: File
  id?: string
  state: JobState
  info?: { n: number; total: number }
  previewUrl?: string
  outputPreviewUrl?: string
  pollTimer?: number
}

export type LanguageOptions = Record<string, string>


