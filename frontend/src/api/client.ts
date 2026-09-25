import { supabase } from '../lib/supabase'
import type { components } from './schema'

export type AnalysisResult = components['schemas']['AnalysisResult']

// Prod'da backend Vercel URL'i buraya gelir; lokalde boş bırakılır, vite.config.ts
// içindeki proxy /api isteklerini backend'e yönlendirir (bkz. PLAN.md §9).
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function authHeaders(): Promise<HeadersInit> {
  const {
    data: { session },
  } = await supabase.auth.getSession()
  return session ? { Authorization: `Bearer ${session.access_token}` } : {}
}

type CreateAnalysisParams = {
  jobText: string
  outputLanguage: 'tr' | 'en'
  cvText?: string
  cvFile?: File
}

export async function createAnalysis(params: CreateAnalysisParams): Promise<AnalysisResult> {
  const formData = new FormData()
  formData.set('job_text', params.jobText)
  formData.set('output_language', params.outputLanguage)
  if (params.cvFile) {
    formData.set('cv_file', params.cvFile)
  } else if (params.cvText) {
    formData.set('cv_text', params.cvText)
  }

  const response = await fetch(`${BASE_URL}/api/v1/analyses`, {
    method: 'POST',
    headers: await authHeaders(),
    body: formData,
  })

  if (!response.ok) {
    const body: { detail?: string } | null = await response.json().catch(() => null)
    throw new ApiError(response.status, body?.detail ?? `İstek başarısız oldu (${response.status})`)
  }

  return response.json()
}
