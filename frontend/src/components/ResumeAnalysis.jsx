import ScoreBar from './ScoreBar'
import { API_BASE } from '../lib/api'

const FIT_STYLES = {
  'Excellent Fit': 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
  'Good Fit':      'text-blue-400   bg-blue-500/10   border-blue-500/30',
  'Moderate Fit':  'text-yellow-400 bg-yellow-500/10 border-yellow-500/30',
  'Weak Fit':      'text-red-400    bg-red-500/10    border-red-500/30',
}

function Pill({ label, color }) {
  const styles = {
    emerald: 'text-emerald-300 bg-emerald-500/10 border-emerald-500/25',
    blue:    'text-blue-300   bg-blue-500/10   border-blue-500/25',
    red:     'text-red-300    bg-red-500/10    border-red-500/25',
  }
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${styles[color] || styles.blue}`}>
      {label}
    </span>
  )
}

export default function ResumeAnalysis({ analysis, candidateId, candidateName, resumeUrl }) {
  if (!analysis) return null
  const fileUrl = resumeUrl ? `${API_BASE}${resumeUrl}` : null

  const {
    resume_quality_score: rqs = 0,
    resume_quality_breakdown: rqb = {},
    fit_label,
    verdict,
    why_preferred,
    strengths = [],
    concerns = [],
    capable_for_role,
    skills_matched = [],
    skills_missing = [],
    scoring_method,
  } = analysis

  const fitStyle = FIT_STYLES[fit_label] || FIT_STYLES['Moderate Fit']

  return (
    <div className="mt-4 space-y-4 border-t border-white/[0.06] pt-4">

      {/* Header row */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-3">
          <p className="text-xs font-bold text-white/30 uppercase tracking-widest">AI Resume Analysis</p>
          <span className={`px-3 py-1 rounded-full text-xs font-bold border ${fitStyle}`}>{fit_label}</span>
          {capable_for_role !== undefined && (
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${
              capable_for_role
                ? 'text-emerald-300 bg-emerald-500/10 border-emerald-500/25'
                : 'text-red-300 bg-red-500/10 border-red-500/25'
            }`}>
              {capable_for_role ? '✓ Capable for Role' : '✗ Below Threshold'}
            </span>
          )}
        </div>

        {/* Resume buttons */}
        {fileUrl && (
          <div className="flex gap-2">
            <a
              href={fileUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary text-xs px-3 py-1.5 flex items-center gap-1.5">
              👁 View Resume
            </a>
            <a
              href={fileUrl}
              download={`${(candidateName || 'Candidate').replace(/\s+/g,'_')}_Resume.pdf`}
              className="btn-primary text-xs px-3 py-1.5 flex items-center gap-1.5">
              ⬇ Download PDF
            </a>
          </div>
        )}
      </div>

      {/* Resume quality score bars */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div className="bg-white/[0.03] rounded-xl p-4 space-y-2.5">
          <p className="text-xs font-bold text-white/30 uppercase tracking-wider mb-3">
            Resume Quality Score — {rqs}/100
          </p>
          <ScoreBar score={rqb.yoe       || 0} label="Years of Experience"  color="#7c6ff7" />
          <ScoreBar score={rqb.projects  || 0} label="Real-World Projects"  color="#34d399" />
          <ScoreBar score={rqb.skills    || 0} label="Technical Skills"     color="#5a8cf8" />
          <ScoreBar score={rqb.education || 0} label="Education Tier"       color="#fbbf24" />
        </div>

        <div className="bg-white/[0.03] rounded-xl p-4 space-y-3">
          <p className="text-xs font-bold text-white/30 uppercase tracking-wider mb-2">Skill Match</p>
          {skills_matched.length > 0 && (
            <div>
              <p className="text-[10px] text-emerald-400 font-semibold mb-1.5">✓ Matched Skills</p>
              <div className="flex flex-wrap gap-1">
                {skills_matched.map(s => <Pill key={s} label={s} color="emerald" />)}
              </div>
            </div>
          )}
          {skills_missing.length > 0 && (
            <div>
              <p className="text-[10px] text-red-400 font-semibold mb-1.5">✗ Missing Skills</p>
              <div className="flex flex-wrap gap-1">
                {skills_missing.map(s => <Pill key={s} label={s} color="red" />)}
              </div>
            </div>
          )}
          {scoring_method && (
            <p className="text-[10px] text-white/25 mt-2">Scored via: {scoring_method}</p>
          )}
        </div>
      </div>

      {/* Why preferred */}
      {why_preferred && (
        <div className="bg-purple-500/[0.06] border border-purple-500/20 rounded-xl p-4">
          <p className="text-xs font-bold text-purple-400 mb-2">🤖 Why This Resume Stands Out</p>
          <p className="text-sm text-purple-200 leading-relaxed">{why_preferred}</p>
        </div>
      )}

      {/* Verdict */}
      {verdict && (
        <div className={`rounded-xl p-3 text-sm leading-relaxed border ${fitStyle}`}>
          <span className="font-semibold">AI Verdict: </span>{verdict}
        </div>
      )}

      {/* Strengths & Concerns */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {strengths.length > 0 && (
          <div className="bg-emerald-500/[0.04] border border-emerald-500/15 rounded-xl p-4">
            <p className="text-xs font-bold text-emerald-400 mb-2">💪 Resume Strengths</p>
            <ul className="space-y-1.5">
              {strengths.map((s, i) => (
                <li key={i} className="text-xs text-emerald-200/80 flex gap-2 leading-relaxed">
                  <span className="shrink-0 text-emerald-400">✓</span> {s}
                </li>
              ))}
            </ul>
          </div>
        )}
        {concerns.length > 0 && (
          <div className="bg-orange-500/[0.04] border border-orange-500/15 rounded-xl p-4">
            <p className="text-xs font-bold text-orange-400 mb-2">⚠ Areas of Concern</p>
            <ul className="space-y-1.5">
              {concerns.map((c, i) => (
                <li key={i} className="text-xs text-orange-200/80 flex gap-2 leading-relaxed">
                  <span className="shrink-0 text-orange-400">!</span> {c}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
