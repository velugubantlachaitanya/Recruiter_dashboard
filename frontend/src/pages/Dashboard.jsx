import { useState } from 'react'
import { Sparkles, Users, Trophy, Loader2, ChevronRight, AlertCircle } from 'lucide-react'
import { apiFetch } from '../lib/api'
import JDUploader from '../components/JDUploader'
import CandidateCard from '../components/CandidateCard'
import ShortlistTable from '../components/ShortlistTable'

const STEPS = [
  { id: 0, label: 'Parse JD',    icon: '📋' },
  { id: 1, label: 'Match',       icon: '🔍' },
  { id: 2, label: 'Engage',      icon: '💬' },
  { id: 3, label: 'Shortlist',   icon: '⭐' },
]

function StepBadge({ step, current }) {
  const done = current > step.id
  const active = current === step.id
  return (
    <div className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all
      ${active ? 'bg-purple-500/20 border border-purple-500/40 text-purple-200' :
        done ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-300' :
               'bg-white/[0.03] border border-white/[0.06] text-white/30'}`}>
      <span>{done ? '✓' : step.icon}</span>
      <span>{step.label}</span>
    </div>
  )
}

export default function Dashboard() {
  const [step, setStep]           = useState(0)
  const [loading, setLoading]     = useState(false)
  const [loadMsg, setLoadMsg]     = useState('')
  const [error, setError]         = useState('')
  const [parsedJD, setParsedJD]   = useState(null)
  const [rawJD, setRawJD]         = useState('')
  const [candidates, setCandidates] = useState([])
  const [shortlist, setShortlist]   = useState([])
  const [engagedMap, setEngagedMap] = useState({}) // cid -> result

  function setErr(e) { setError(e); setLoading(false) }

  // Step 1 → 2: JD parsed, now match candidates
  async function onJDParsed(jd, jdText) {
    setParsedJD(jd); setRawJD(jdText); setError('')
    setLoading(true); setLoadMsg('ML matching 50 candidates…')
    try {
      const res = await apiFetch('/api/match-candidates', {
        method: 'POST',
        body: JSON.stringify({ jd })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Match failed')
      setCandidates(data.candidates || [])
      setStep(1); setLoading(false); setLoadMsg('')
    } catch(e) { setErr(e.message) }
  }

  // Engage a single candidate (outreach simulation)
  async function onEngage(candidateId) {
    setLoading(true); setLoadMsg('Simulating outreach conversation…')
    try {
      const res = await apiFetch(`/api/engage/${candidateId}`, {
        method: 'POST',
        body: JSON.stringify({ jd: parsedJD })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Engage failed')
      setEngagedMap(m => ({ ...m, [candidateId]: data }))
      // Patch candidate in list
      setCandidates(cs => cs.map(c => {
        if ((c.candidate_id || c.id) === candidateId) {
          return { ...c, conversation: data.conversation, interest_score: data.interest_score, interest_signals: data.signals_triggered }
        }
        return c
      }))
      setStep(2); setLoading(false); setLoadMsg('')
    } catch(e) { setErr(e.message) }
  }

  // AI interview for a candidate
  async function onInterview(candidateId) {
    setLoading(true); setLoadMsg('Running AI interview simulation…')
    try {
      const res = await apiFetch(`/api/interview/${candidateId}`, {
        method: 'POST',
        body: JSON.stringify({ jd: parsedJD })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Interview failed')
      setCandidates(cs => cs.map(c => {
        if ((c.candidate_id || c.id) === candidateId) return { ...c, interview: data }
        return c
      }))
      setLoading(false); setLoadMsg('')
    } catch(e) { setErr(e.message) }
  }

  // Build final shortlist
  async function onBuildShortlist() {
    setLoading(true); setLoadMsg('Building ranked shortlist…')
    try {
      const res = await apiFetch('/api/shortlist', {
        method: 'POST',
        body: JSON.stringify({ jd: parsedJD })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Shortlist failed')
      setShortlist(data.shortlist || [])
      setStep(3); setLoading(false); setLoadMsg('')
    } catch(e) { setErr(e.message) }
  }

  // Full pipeline in one shot
  async function onFullPipeline(jdText) {
    setParsedJD(null); setCandidates([]); setShortlist([]); setEngagedMap({})
    setLoading(true); setLoadMsg('Running full AI pipeline (parse → match → engage top 6 → shortlist)…'); setError('')
    try {
      const res = await apiFetch('/api/full-pipeline', {
        method: 'POST',
        body: JSON.stringify({ jd_text: jdText, engage_top_n: 6 })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Pipeline failed')
      setParsedJD(data.parsed_jd)
      // Merge shortlist data back into candidates view
      const sl = data.shortlist || []
      setCandidates(sl)
      setShortlist(sl)
      setStep(3); setLoading(false); setLoadMsg('')
    } catch(e) { setErr(e.message) }
  }

  function exportShortlist() {
    const blob = new Blob([JSON.stringify(shortlist, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = 'shortlist_output.json'; a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="flex-1 flex flex-col">
      {/* Header */}
      <div className="border-b border-white/[0.06] px-8 py-5 flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-black bg-gradient-to-r from-purple-300 to-blue-300 bg-clip-text text-transparent">
            Recruiter Dashboard
          </h1>
          <p className="text-sm text-white/35 mt-0.5">AI-Powered Talent Scouting & Engagement</p>
        </div>
        <div className="flex gap-2 flex-wrap">
          {STEPS.map(s => <StepBadge key={s.id} step={s} current={step} />)}
        </div>
      </div>

      <div className="flex-1 p-8 space-y-6 max-w-5xl w-full mx-auto">
        {/* Error */}
        {error && (
          <div className="flex gap-3 p-4 bg-red-500/8 border border-red-500/25 rounded-xl text-red-300 text-sm">
            <AlertCircle size={16} className="shrink-0 mt-0.5" />
            <div><strong>Error:</strong> {error}</div>
          </div>
        )}

        {/* Loading overlay */}
        {loading && (
          <div className="flex items-center gap-3 p-4 bg-purple-500/8 border border-purple-500/25 rounded-xl text-purple-200 text-sm">
            <Loader2 size={18} className="spinner shrink-0" />
            {loadMsg || 'Processing…'}
          </div>
        )}

        {/* Step 0: JD Input */}
        {step === 0 && (
          <div className="grid md:grid-cols-2 gap-6 animate-fade-up">
            <div className="card">
              <JDUploader onParsed={onJDParsed} loading={loading} />
            </div>
            <div className="card flex flex-col gap-4">
              <p className="text-xs font-bold text-white/30 uppercase tracking-widest">Or run full pipeline at once</p>
              <p className="text-sm text-white/50 leading-relaxed">
                Click "Full Pipeline" to parse the JD, match all 50 candidates, simulate outreach with the top 6, and generate the final star-rated shortlist — all in one shot.
              </p>
              <div className="flex-1 flex items-end">
                <button className="btn-primary w-full justify-center py-3"
                  onClick={async () => {
                    const jdContent = document.querySelector('textarea')?.value
                    if (!jdContent?.trim()) { setError('Please paste a Job Description first, or click Load Demo JD.'); return }
                    await onFullPipeline(jdContent)
                  }}
                  disabled={loading}>
                  <Sparkles size={18}/> Run Full Pipeline
                </button>
              </div>
              <p className="text-xs text-white/20 text-center">Runs Steps 1–4 automatically · takes ~30–60s</p>
            </div>
          </div>
        )}

        {/* Parsed JD panel */}
        {parsedJD && step > 0 && (
          <div className="card animate-fade-up">
            <div className="flex gap-4 flex-wrap">
              <div className="flex-1 min-w-[200px]">
                <p className="text-xs font-bold text-white/30 uppercase tracking-widest mb-2">Parsed JD</p>
                <p className="font-bold text-lg">{parsedJD.role_title}</p>
                <p className="text-sm text-white/40">📍 {parsedJD.location} · {parsedJD.min_experience_years}+ yrs · {parsedJD.employment_type}</p>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {(parsedJD.required_skills || []).map(s => <span key={s} className="tag">{s}</span>)}
              </div>
            </div>
          </div>
        )}

        {/* Steps 1-2: Candidates */}
        {(step === 1 || step === 2) && candidates.length > 0 && (
          <div className="animate-fade-up space-y-4">
            <div className="flex justify-between items-center flex-wrap gap-3">
              <div>
                <h2 className="font-bold text-lg flex items-center gap-2"><Users size={18}/> {candidates.length} Matched Candidates</h2>
                <p className="text-sm text-white/40">Sorted by match score · click any card to expand · engage to simulate outreach</p>
              </div>
              <button className="btn-primary" onClick={onBuildShortlist} disabled={loading}>
                <Trophy size={16}/> Build Shortlist <ChevronRight size={14}/>
              </button>
            </div>
            {candidates.map((c, i) => (
              <CandidateCard
                key={c.candidate_id || c.id || i}
                candidate={c}
                index={i}
                onEngage={onEngage}
                onInterview={onInterview}
                loading={loading}
              />
            ))}
          </div>
        )}

        {/* Step 3: Shortlist */}
        {step === 3 && shortlist.length > 0 && (
          <div className="animate-fade-up">
            <ShortlistTable shortlist={shortlist} onExport={exportShortlist} />
          </div>
        )}
      </div>
    </div>
  )
}
