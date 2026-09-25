import { useLanguage } from '../i18n/useLanguage'

type JobInputProps = {
  value: string
  onChange: (value: string) => void
}

export function JobInput({ value, onChange }: JobInputProps) {
  const { t } = useLanguage()

  return (
    <div className="field">
      <label htmlFor="job-text">{t('newAnalysis.jobLabel')}</label>
      <textarea
        id="job-text"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={t('newAnalysis.jobPlaceholder')}
        rows={10}
      />
    </div>
  )
}
