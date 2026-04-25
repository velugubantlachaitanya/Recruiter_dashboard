import StarRating from './StarRating'
import ScoreBar from './ScoreBar'

const REC_STYLE = {
  '🟢 Highly Recommended': 'text-emerald-400 bg-emerald-500/10 border-emerald-500/25',
  '🔵 Strong Candidate':   'text-blue-400 bg-blue-500/10 border-blue-500/25',
  '🟡 Good Potential':     'text-yellow-400 bg-yellow-500/10 border-yellow-500/25',
  '🟠 Needs Review':       'text-orange-400 bg-orange-500/10 border-orange-500/25',
  '🔴 Low Priority':       'text-red-400 bg-red-500/10 border-red-500/25',
}

export default function ShortlistTable({ shortlist, onExport }) {
  if (!shortlist?.length) return null
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-bold">Ranked Shortlist — {shortlist.length} Candidates</h2>
        <button className="btn-secondary text-xs px-4 py-2" onClick={onExport}>⬇ Export JSON</button>
      </div>
      {/* Summary stats */}
      <div className="grid grid-cols-5 gap-3">
        {[5,4,3,2,1].map(s => {
          const labels = { 5:'⭐⭐⭐⭐⭐ Highly Rec.', 4:'⭐⭐⭐⭐ Strong', 3:'⭐⭐⭐ Good', 2:'⭐⭐ Review', 1:'⭐ Low' }
          const colors = { 5:'text-emerald-400', 4:'text-blue-400', 3:'text-yellow-400', 2:'text-orange-400', 1:'text-red-400' }
          const count = shortlist.filter(e => e.star_rating === s).length
          return (
            <div key={s} className="card-sm text-center">
              <div className={`text-2xl font-black font-mono ${colors[s]}`}>{count}</div>
              <div className="text-xs text-white/30 mt-1">{labels[s]}</div>
            </div>
          )
        })}
      </div>
      {/* Table */}
      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/[0.06] bg-white/[0.03]">
                {['Rank','Name','Match','Interest','Combined ⭐','Recommendation'].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-bold text-white/30 uppercase tracking-wider whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {shortlist.map((e, i) => (
                <tr key={e.candidate_id} className="border-b border-white/[0.04] hover:bg-white/[0.03] transition-colors">
                  <td className="px-4 py-3">
                    <span className="w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs font-mono"
                      style={{ background: i===0?'rgba(52,211,153,0.15)':i===1?'rgba(90,140,248,0.12)':'rgba(255,255,255,0.05)',
                               color: i===0?'#34d399':i===1?'#5a8cf8':'#888' }}>
                      {e.rank}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="font-semibold">{e.name}</div>
                    <div className="text-xs text-white/35">{e.experience_years}y · {e.location?.split(',')[0]}</div>
                  </td>
                  <td className="px-4 py-3 min-w-[100px]">
                    <ScoreBar score={e.match_score} height={4} />
                  </td>
                  <td className="px-4 py-3 min-w-[100px]">
                    <ScoreBar score={e.interest_score} height={4} color="#34d399" />
                  </td>
                  <td className="px-4 py-3">
                    <div className="font-black text-xl font-mono mb-1" style={{color: e.combined_score>=70?'#34d399':e.combined_score>=55?'#7c6ff7':e.combined_score>=40?'#fbbf24':'#f87171'}}>
                      {e.combined_score?.toFixed(0)}
                    </div>
                    <StarRating stars={e.star_rating} size="sm" />
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border ${REC_STYLE[e.recommendation] || 'text-white/50 border-white/10'}`}>
                      {e.recommendation}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
