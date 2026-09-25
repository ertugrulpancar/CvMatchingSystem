const SIZE = 128
const STROKE = 10
const RADIUS = (SIZE - STROKE) / 2
const CIRCUMFERENCE = 2 * Math.PI * RADIUS

type ScoreRingProps = {
  score: number
  label: string
}

export function ScoreRing({ score, label }: ScoreRingProps) {
  const offset = CIRCUMFERENCE * (1 - score / 100)

  return (
    <div className="score-hero">
      <svg width={SIZE} height={SIZE} viewBox={`0 0 ${SIZE} ${SIZE}`}>
        <circle
          cx={SIZE / 2}
          cy={SIZE / 2}
          r={RADIUS}
          fill="none"
          stroke="var(--color-bg-subtle)"
          strokeWidth={STROKE}
        />
        <circle
          cx={SIZE / 2}
          cy={SIZE / 2}
          r={RADIUS}
          fill="none"
          stroke="var(--color-primary)"
          strokeWidth={STROKE}
          strokeLinecap="round"
          strokeDasharray={CIRCUMFERENCE}
          strokeDashoffset={offset}
          transform={`rotate(-90 ${SIZE / 2} ${SIZE / 2})`}
        />
        <text
          x="50%"
          y="50%"
          textAnchor="middle"
          dominantBaseline="central"
          className="score-ring-value"
          fill="var(--color-text)"
        >
          {score}
        </text>
      </svg>
      <span className="score-ring-label">{label}</span>
    </div>
  )
}
