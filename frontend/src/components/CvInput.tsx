import { Upload } from 'lucide-react'
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
      <div className="tabs" role="tablist">
        <button
          type="button"
          role="tab"
          aria-selected={mode === 'file'}
          className={`tab ${mode === 'file' ? 'active' : ''}`}
          onClick={() => onModeChange('file')}
        >
          {t('newAnalysis.cvModeFile')}
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={mode === 'text'}
          className={`tab ${mode === 'text' ? 'active' : ''}`}
          onClick={() => onModeChange('text')}
        >
          {t('newAnalysis.cvModeText')}
        </button>
      </div>

      {mode === 'file' ? (
        <label className="file-drop">
          <Upload size={22} />
          <span className="file-name">
            {cvFile ? cvFile.name : t('newAnalysis.cvFileCta')}
          </span>
          {!cvFile && <span className="hint">{t('newAnalysis.cvFileHint')}</span>}
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={(event) => onCvFileChange(event.target.files?.[0] ?? null)}
          />
        </label>
      ) : (
        <textarea
          value={cvText}
          onChange={(event) => onCvTextChange(event.target.value)}
          placeholder={t('newAnalysis.cvTextPlaceholder')}
          rows={8}
        />
      )}
    </div>
  )
}
