import { useLanguage } from '../i18n/useLanguage'

type CvMode = 'file' | 'text'

type CvInputProps = {
  mode: CvMode
  onModeChange: (mode: CvMode) => void
  cvText: string
  onCvTextChange: (text: string) => void
  cvFile: File | null
  onCvFileChange: (file: File | null) => void
}

export function CvInput({
  mode,
  onModeChange,
  cvText,
  onCvTextChange,
  cvFile,
  onCvFileChange,
}: CvInputProps) {
  const { t } = useLanguage()

  return (
    <div className="field">
      <label>{t('newAnalysis.cvLabel')}</label>
      <div className="mode-toggle">
        <button
          type="button"
          className={mode === 'file' ? 'active' : ''}
          onClick={() => onModeChange('file')}
        >
          {t('newAnalysis.cvModeFile')}
        </button>
        <button
          type="button"
          className={mode === 'text' ? 'active' : ''}
          onClick={() => onModeChange('text')}
        >
          {t('newAnalysis.cvModeText')}
        </button>
      </div>

      {mode === 'file' ? (
        <div>
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={(event) => onCvFileChange(event.target.files?.[0] ?? null)}
          />
          <p className="hint">{t('newAnalysis.cvFileHint')}</p>
          {cvFile && <p className="hint">{cvFile.name}</p>}
        </div>
      ) : (
        <textarea
          value={cvText}
          onChange={(event) => onCvTextChange(event.target.value)}
          placeholder={t('newAnalysis.cvTextPlaceholder')}
          rows={10}
        />
      )}
    </div>
  )
}
