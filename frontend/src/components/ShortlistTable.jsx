import { useState } from 'react'
import StarRating from './StarRating'
import ScoreBar from './ScoreBar'
import { viewResume, downloadResume } from '../lib/resumeUtils'

const REC_STYLE = {
  '🟢 Highly Recommended': 'text-emerald-400 bg-emerald-500/10 border-emerald-500/25',
  '🔵 Strong Candidate':   'text-blue-400 bg-blue-500/10 border-blue-500/25',
  '🟡 Good Potential':     'text-yellow-400 bg-yellow-500/10 border-yellow-500/25',
  '🟠 Needs Review':       'text-orange-400 bg-orange-500/10 border-orange-500/25',
  '🔴 Low Priority':       'text-red-400 bg-red-500/10 border-red-500/25',
}

function ResumeButtons({ candidateId, candidateName, resumeUrl }) {
  const [loading, setLoading] = useState(false)
  return (
    <div className="flex flex-col gap-1.5">
      <button
        onClick={() => viewResume(resumeUrl, candidateName)}
        className="text-[10px] px-2.5 py-1 rounded-lg bg-white/[0.04] border border-white/10 text-white/60 hover:text-white hover:border-purple-500/40 transition-colors cursor-pointer">
        👁 View
      </button>
      <button
        onClick={() => downloadResume(candidateId, candidateName, resumeUrl, setLoading)}
        disabled={loading}
        className="text-[10px] px-2.5 py-1 rounded-lg bg-purple-500/10 border border-purple-500/25 text-purple-300 hover:bg-purple-500/20 transition-colors cursor-pointer disabled:opacity-50">
        {loading ? '⏳' : '⬇ Download'}
      </button>
    </div>
  )
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
          const count  = shortlist.filter(e => e.star_rating === s).length
          return (
            <div key={s} className="card-sm text-center">
              <div className={`text-2xl font-black font-mono ${colors[s]}`}>{count}</div>
              <div className="text-xs text-white/30 mt-1">{labels[s]}</div>
            </div>
          )
        })}
      </div>

      {/* AI interview priority notice */}
      {shortlist.some(e => e.interview?.passed) && (
        <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-blue-500/8 border border-blue-500/20 text-blue-300 text-sm">
          🎤 <strong>AI Interview Priority active</strong> — candidates who passed the interview are ranked higher regardless of other scores.
        </div>
      )}

      {/* Table */}
      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/[0.06] bg-white/[0.03]">
                {['Rank','Candidate','Match','Resume Quality','Final Score ⭐','Recommendation','Resume'].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-bold text-white/30 uppercase tracking-wider whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {shortlist.map((e, i) => {
                const interviewPassed = e.interview?.passed
                return (
                  <tr key={e.candidate_id}
                    className={`border-b border-white/[0.04] hover:bg-white/[0.03] transition-colors ${interviewPassed ? 'bg-blue-500/[0.03]' : ''}`}>
                    <td className="px-4 py-3">
                      <span className="w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs font-mono"
                        style={{
                          background: i===0?'rgba(52,211,153,0.15)':i===1?'rgba(90,140,248,0.12)':'rgba(255,255,255,0.05)',
                          color: i===0?'#34d399':i===1?'#5a8cf8':'#888'
                        }}>
                        {e.rank}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="font-semibold">{e.name}</div>
                      <div className="text-xs text-white/35">{e.experience_years}y · {e.location?.split(',')[0]}</div>
                      <div className="flex gap-1 mt-1 flex-wrap">
                        {e.capable_for_role && (
                          <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">✓ Capable</span>
                        )}
                        {interviewPassed && (
                          <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-300">🎤 Interview ✓</span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3 min-w-[90px]">
                      <ScoreBar score={e.match_score} height={4} />
                    </td>
                    <td className="px-4 py-3 min-w-[90px]">
                      <ScoreBar score={e.resume_quality_score || 0} height={4} color="#fbbf24" />
                      <div className="text-[10px] text-white/30 mt-1">
                        {e.resume_analysis?.fit_label || ''}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="font-black text-xl font-mono mb-1"
                        style={{ color: e.combined_score>=70?'#34d399':e.combined_score>=52?'#7c6ff7':e.combined_score>=38?'#fbbf24':'#f87171' }}>
                        {e.combined_score?.toFixed(0)}
                      </div>
                      <StarRating stars={e.star_rating} size="sm" />
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border ${REC_STYLE[e.recommendation] || 'text-white/50 border-white/10'}`}>
                        {e.recommendation}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <ResumeButtons candidateId={e.candidate_id} candidateName={e.name} resumeUrl={e.resume_url} />
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Explainability cards for top 3 */}
      <div className="space-y-2">
        <p className="text-xs font-bold text-white/30 uppercase tracking-widest">AI Explanation — Top Picks</p>
        {shortlist.slice(0, 3).map(e => e.resume_analysis && (
          <div key={e.candidate_id} className="bg-white/[0.02] border border-white/[0.06] rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-bold text-sm">{e.name}</span>
              <span className="text-xs text-white/30">#{e.rank}</span>
              <span className={`text-xs px-2 py-0.5 rounded-full border font-semibold
                ${e.resume_analysis.fit_label === 'Excellent Fit' ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/25'
                : e.resume_analysis.fit_label === 'Good Fit'      ? 'text-blue-400 bg-blue-500/10 border-blue-500/25'
                : 'text-yellow-400 bg-yellow-500/10 border-yellow-500/25'}`}>
                {e.resume_analysis.fit_label}
              </span>
            </div>
            <p className="text-xs text-white/50 leading-relaxed">{e.resume_analysis.why_preferred}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
