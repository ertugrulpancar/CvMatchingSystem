import type { AnalysisResult } from '../api/client'
import { useLanguage } from '../i18n/useLanguage'

type ScoreCardProps = {
  overallScore: AnalysisResult['overall_score']
  categoryScores: AnalysisResult['category_scores']
}

export function ScoreCard({ overallScore, categoryScores }: ScoreCardProps) {
  const { t } = useLanguage()

  return (
    <div className="score-card">
      <h2>{t('result.overallScore')}</h2>
      <p className="overall-score">%{overallScore}</p>

      <h3>{t('result.categoryScores')}</h3>
      <ul>
        {categoryScores.map((score) => (
          <li key={score.category}>
            {t(`category.${score.category}`)}: %{score.score}
          </li>
        ))}
      </ul>
    </div>
  )
}
