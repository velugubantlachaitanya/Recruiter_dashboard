import { useState } from 'react'
import { ChevronDown, ChevronUp, Briefcase, MapPin } from 'lucide-react'
import StarRating from './StarRating'
import ScoreBar from './ScoreBar'
import ChatSimulator from './ChatSimulator'

const AVATAR_COLORS = ['#7c6ff7','#5a8cf8','#34d399','#fbbf24','#f87171','#a78bfa']

function Avatar({ name, color }) {
  const initials = name.split(' ').map(w => w[0]).join('').slice(0,2).toUpperCase()
  return (
    <div className="w-11 h-11 rounded-full flex items-center justify-center font-bold text-sm shrink-0"
      style={{ background: `${color}22`, border: `2px solid ${color}55`, color }}>
      {initials}
    </div>
  )
}

export default function CandidateCard({ candidate, index, onEngage, onInterview, loading }) {
  const [expanded, setExpanded] = useState(false)
  const color = AVATAR_COLORS[index % AVATAR_COLORS.length]
  const bd = candidate.match_breakdown || {}
  const stars = candidate.star_rating || 1
  const rec = candidate.recommendation || ''
  const recColor = rec.includes('Highly') ? 'text-emerald-400' : rec.includes('Strong') ? 'text-blue-400'
    : rec.includes('Good') ? 'text-yellow-400' : rec.includes('Needs') ? 'text-orange-400' : 'text-red-400'

  return (
    <div className="card animate-fade-up mb-3 hover:border-purple-500/30 transition-all">
      <div className="flex gap-4 items-start cursor-pointer" onClick={() => setExpanded(!expanded)}>
        <Avatar name={candidate.name} color={color} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <span className="font-bold">{candidate.name}</span>
            <span className={`text-xs font-semibold px-2 py-0.5 rounded-full bg-white/5 border border-white/10 font-mono`}>#{candidate.rank || index+1}</span>
          </div>
          <div className="text-sm text-white/50 flex items-center gap-3 flex-wrap">
            <span className="flex items-center gap-1"><Briefcase size={12}/> {candidate.experience_years}y exp</span>
            <span className="flex items-center gap-1"><MapPin size={12}/> {candidate.location}</span>
            <span>Tier {candidate.education?.tier || '?'} — {candidate.education?.institution}</span>
          </div>
          <div className="flex flex-wrap gap-1.5 mt-2">
            {(candidate.skills || []).slice(0,6).map(s => <span key={s} className="tag">{s}</span>)}
          </div>
        </div>
        <div className="flex flex-col items-end gap-1 shrink-0">
          <StarRating stars={stars} size="md" />
          <span className={`text-xs font-semibold ${recColor}`}>{rec.replace(/^[^\s]+\s/,'')}</span>
          <span className="text-2xl font-black font-mono" style={{ color: candidate.combined_score >= 70 ? '#34d399' : candidate.combined_score >= 50 ? '#7c6ff7' : '#fbbf24' }}>
            {candidate.combined_score?.toFixed(0)}
          </span>
          {expanded ? <ChevronUp size={16} className="text-white/30"/> : <ChevronDown size={16} className="text-white/30"/>}
        </div>
      </div>

      {expanded && (
        <div className="mt-5 pt-5 border-t border-white/[0.06] space-y-4">
          {/* Score breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="bg-white/[0.03] rounded-xl p-4 space-y-2.5">
              <p className="text-xs font-bold text-white/30 uppercase tracking-wider mb-3">Match Breakdown</p>
              <ScoreBar score={bd.skills || 0} label="Skills" />
              <ScoreBar score={bd.experience || 0} label="Experience" />
              <ScoreBar score={bd.location || 0} label="Location" />
              <ScoreBar score={bd.education || 0} label="Education" />
              <ScoreBar score={bd.employment_type || 0} label="Employment" />
            </div>
            <div className="bg-white/[0.03] rounded-xl p-4">
              <p className="text-xs font-bold text-white/30 uppercase tracking-wider mb-3">Score Summary</p>
              <ScoreBar score={candidate.match_score || 0} label="Match Score" color="#7c6ff7" />
              <div className="mt-2.5">
                <ScoreBar score={candidate.interest_score || 0} label="Interest Score" color="#34d399" />
              </div>
              <div className="mt-2.5">
                <ScoreBar score={candidate.combined_score || 0} label="Combined" color="#5a8cf8" height={8} />
              </div>
              {(candidate.interest_signals || []).length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {candidate.interest_signals.map(s => <span key={s} className="tag text-emerald-300 border-emerald-500/20 bg-emerald-500/10">{s}</span>)}
                </div>
              )}
            </div>
          </div>

          {/* Explainability */}
          {candidate.explainability && (
            <div className="bg-purple-500/[0.06] border border-purple-500/20 rounded-xl p-3 text-sm text-purple-200">
              💡 {candidate.explainability}
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-2 flex-wrap">
            <button className="btn-primary text-xs px-4 py-2" onClick={() => onEngage(candidate.candidate_id || candidate.id)} disabled={loading}>
              {loading ? '⏳' : '📧'} Simulate Outreach
            </button>
            <button className="btn-secondary text-xs px-4 py-2" onClick={() => onInterview(candidate.candidate_id || candidate.id)} disabled={loading}>
              🎤 AI Interview
            </button>
          </div>

          {/* Chat simulation */}
          {candidate.conversation && <ChatSimulator conversation={candidate.conversation} candidateName={candidate.name} />}
          {candidate.interview && (
            <div className="bg-white/[0.03] rounded-xl p-4">
              <p className="text-xs font-bold text-white/30 uppercase tracking-wider mb-3">Interview Result</p>
              <div className="flex items-center gap-3 mb-2">
                <span className={`font-bold text-lg font-mono ${candidate.interview.passed ? 'text-emerald-400' : 'text-red-400'}`}>{candidate.interview.interview_score?.toFixed(0)}/100</span>
                <span className={`tag ${candidate.interview.passed ? 'text-emerald-300 bg-emerald-500/10 border-emerald-500/20' : 'text-red-300 bg-red-500/10 border-red-500/20'}`}>{candidate.interview.passed ? '✓ Passed' : '✗ Did not pass'}</span>
              </div>
              <p className="text-sm text-white/50">{candidate.interview.evaluation}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
