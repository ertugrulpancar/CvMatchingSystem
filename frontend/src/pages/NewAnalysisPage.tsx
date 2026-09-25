import { useState, type FormEvent } from 'react'
import { ApiError, createAnalysis, type AnalysisResult } from '../api/client'
import { CvInput } from '../components/CvInput'
import { JobInput } from '../components/JobInput'
import { RequirementList } from '../components/RequirementList'
import { ScoreCard } from '../components/ScoreCard'
import { useLanguage } from '../i18n/useLanguage'

export function NewAnalysisPage() {
  const { t, language } = useLanguage()

  const [jobText, setJobText] = useState('')
  const [cvMode, setCvMode] = useState<'file' | 'text'>('file')
  const [cvText, setCvText] = useState('')
  const [cvFile, setCvFile] = useState<File | null>(null)

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<AnalysisResult | null>(null)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)

    if (!jobText.trim()) {
      setError(t('newAnalysis.errorMissingJob'))
      return
    }
    if (cvMode === 'file' && !cvFile) {
      setError(t('newAnalysis.errorMissingCv'))
      return
    }
    if (cvMode === 'text' && !cvText.trim()) {
      setError(t('newAnalysis.errorMissingCv'))
      return
    }

    setIsSubmitting(true)
    setResult(null)
    try {
      const analysis = await createAnalysis({
        jobText,
        outputLanguage: language,
        cvText: cvMode === 'text' ? cvText : undefined,
        cvFile: cvMode === 'file' ? (cvFile ?? undefined) : undefined,
      })
      setResult(analysis)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t('newAnalysis.errorGeneric'))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="new-analysis-page">
      <form onSubmit={handleSubmit}>
        <JobInput value={jobText} onChange={setJobText} />
        <CvInput
          mode={cvMode}
          onModeChange={setCvMode}
          cvText={cvText}
          onCvTextChange={setCvText}
          cvFile={cvFile}
          onCvFileChange={setCvFile}
        />
        <p className="privacy-notice">{t('newAnalysis.privacyNotice')}</p>
        {error && (
          <p role="alert" className="error">
            {error}
          </p>
        )}
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? t('newAnalysis.submitting') : t('newAnalysis.submit')}
        </button>
      </form>

      {result && (
        <section className="result">
          <h2>{t('result.title')}</h2>
          <ScoreCard overallScore={result.overall_score} categoryScores={result.category_scores} />
          <RequirementList matches={result.matches} />
        </section>
      )}
    </div>
  )
}
