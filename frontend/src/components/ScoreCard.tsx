import type { AnalysisResult } from '../api/client'
import { useLanguage } from '../i18n/useLanguage'
import { ScoreRing } from './ScoreRing'

type ScoreCardProps = {
  overallScore: AnalysisResult['overall_score']
  categoryScores: AnalysisResult['category_scores']
}

export function ScoreCard({ overallScore, categoryScores }: ScoreCardProps) {
  const { t } = useLanguage()

  return (
    <div>
      <ScoreRing score={overallScore} label={t('result.overallScore')} />

      {categoryScores.length > 0 && (
        <div className="category-scores">
          {categoryScores.map((score) => (
            <div className="category-row" key={score.category}>
              <span className="category-name">{t(`category.${score.category}`)}</span>
              <span className="bar-track">
                <span className="bar-fill" style={{ width: `${score.score}%` }} />
              </span>
              <span className="category-value">{score.score}%</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
