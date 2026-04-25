export default function ScoreBar({ score = 0, color = '#7c6ff7', label = '', height = 6 }) {
  const c = score >= 80 ? '#34d399' : score >= 60 ? '#7c6ff7' : score >= 45 ? '#fbbf24' : '#f87171'
  const barColor = color !== '#7c6ff7' ? color : c
  return (
    <div className="w-full">
      {label && (
        <div className="flex justify-between mb-1">
          <span className="text-xs text-white/40 font-medium">{label}</span>
          <span className="text-xs font-bold font-mono" style={{ color: barColor }}>{score}</span>
        </div>
      )}
      <div className="w-full bg-white/[0.06] rounded-full overflow-hidden" style={{ height }}>
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${Math.min(score, 100)}%`, background: `linear-gradient(90deg, ${barColor}88, ${barColor})`, boxShadow: `0 0 8px ${barColor}55` }}
        />
      </div>
    </div>
  )
}
