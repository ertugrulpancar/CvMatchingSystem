import { AlertTriangle, CheckCircle2, XCircle } from 'lucide-react'
import type { AnalysisResult } from '../api/client'
import { useLanguage } from '../i18n/useLanguage'

type RequirementListProps = {
  matches: AnalysisResult['matches']
}

const STATUS_ICONS = {
  met: CheckCircle2,
  partial: AlertTriangle,
  missing: XCircle,
} as const

export function RequirementList({ matches }: RequirementListProps) {
  const { t } = useLanguage()

  return (
    <div className="requirement-list">
      {matches.map((match, index) => {
        const StatusIcon = STATUS_ICONS[match.status]
        return (
          <div className="requirement-item" key={index}>
            <StatusIcon className={`requirement-icon status-${match.status}`} aria-hidden />
            <div className="requirement-body">
              <span className="requirement-title">{match.requirement_text}</span>
              <span className="requirement-meta">
                {t(`category.${match.category}`)} · {t(`importance.${match.importance}`)} ·{' '}
                {t(`status.${match.status}`)}
              </span>
              {match.evidence && <p className="requirement-evidence">"{match.evidence}"</p>}
              <p className="requirement-explanation">{match.explanation}</p>
            </div>
          </div>
        )
      })}
    </div>
  )
}
