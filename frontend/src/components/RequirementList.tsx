import type { AnalysisResult } from '../api/client'
import { useLanguage } from '../i18n/useLanguage'

type RequirementListProps = {
  matches: AnalysisResult['matches']
}

export function RequirementList({ matches }: RequirementListProps) {
  const { t } = useLanguage()

  return (
    <div className="requirement-list">
      <h3>{t('result.requirements')}</h3>
      <ul>
        {matches.map((match, index) => (
          <li key={index} className={`status-${match.status}`}>
            <strong>{match.requirement_text}</strong>
            <span className="meta">
              {t(`category.${match.category}`)} · {t(`importance.${match.importance}`)} ·{' '}
              {t(`status.${match.status}`)}
            </span>
            {match.evidence && <p className="evidence">"{match.evidence}"</p>}
            <p className="explanation">{match.explanation}</p>
          </li>
        ))}
      </ul>
    </div>
  )
}
