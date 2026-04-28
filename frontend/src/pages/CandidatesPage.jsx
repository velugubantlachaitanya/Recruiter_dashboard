import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Users, Trophy, ChevronRight, AlertCircle, Loader2, ArrowLeft } from 'lucide-react'
import { apiFetch, extractError } from '../lib/api'
import { usePipeline } from '../context/PipelineContext'
import CandidateCard from '../components/CandidateCard'

export default function CandidatesPage() {
  const navigate = useNavigate()
  const { parsedJD, candidates, setCandidates, setShortlist, engagedMap, setEngagedMap } = usePipeline()

  const [loading, setLoading] = useState(false)
  const [loadMsg, setLoadMsg] = useState('')
  const [error, setError]     = useState('')

  // Guard: if no JD parsed, go back to start
  useEffect(() => {
    if (!parsedJD) navigate('/', { replace: true })
  }, [parsedJD, navigate])

  function setErr(e) { setError(e); setLoading(false) }

  async function onEngage(candidateId) {
    setLoading(true); setLoadMsg('Simulating outreach conversation…')
    try {
      const res = await apiFetch(`/api/engage/${candidateId}`, {
        method: 'POST',
        body: JSON.stringify({ jd: parsedJD }),
      })
      if (!res.ok) throw new Error(await extractError(res))
      const data = await res.json()
      setEngagedMap(m => ({ ...m, [candidateId]: data }))
      setCandidates(cs => cs.map(c =>
        (c.candidate_id || c.id) === candidateId
          ? { ...c, conversation: data.conversation, interest_score: data.interest_score, interest_signals: data.signals_triggered }
          : c
      ))
      setLoading(false)
    } catch (e) { setErr(e.message) }
  }

  async function onInterview(candidateId) {
    setLoading(true); setLoadMsg('Running AI interview simulation…')
    try {
      const res = await apiFetch(`/api/interview/${candidateId}`, {
        method: 'POST',
        body: JSON.stringify({ jd: parsedJD }),
      })
      if (!res.ok) throw new Error(await extractError(res))
      const data = await res.json()
      setCandidates(cs => cs.map(c =>
        (c.candidate_id || c.id) === candidateId ? { ...c, interview: data } : c
      ))
      setLoading(false)
    } catch (e) { setErr(e.message) }
  }

  async function onBuildShortlist() {
    setLoading(true); setLoadMsg('Building ranked shortlist…')
    try {
      const res = await apiFetch('/api/shortlist', {
        method: 'POST',
        body: JSON.stringify({ jd: parsedJD }),
      })
      if (!res.ok) throw new Error(await extractError(res))
      const data = await res.json()
      setShortlist(data.shortlist || [])
      setLoading(false)
      navigate('/shortlist')
    } catch (e) { setErr(e.message) }
  }

  if (!parsedJD) return null

  return (
    <div className="flex-1 flex flex-col">
      {/* Header */}
      <div className="border-b border-white/[0.06] px-8 py-5 flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-black bg-gradient-to-r from-purple-300 to-blue-300 bg-clip-text text-transparent">
            Matched Candidates
          </h1>
          <p className="text-sm text-white/35 mt-0.5">{parsedJD.role_title} · {parsedJD.location}</p>
          {/* Breadcrumb */}
          <div className="flex items-center gap-2 mt-3 text-xs text-white/30">
            <button onClick={() => navigate('/')} className="hover:text-white/60 transition-colors">📋 JD Upload</button>
            <span>›</span>
            <span className="text-purple-400 font-semibold">🔍 Step 2: Candidates ({candidates.length})</span>
            <span>›</span><span>⭐ Shortlist</span>
          </div>
        </div>
        {/* Actions */}
        <div className="flex gap-2 flex-wrap">
          <button className="btn-secondary flex items-center gap-2 text-sm px-4 py-2"
            onClick={() => navigate(-1)}>
            <ArrowLeft size={14} /> Back
          </button>
          <button className="btn-primary" onClick={onBuildShortlist} disabled={loading}>
            <Trophy size={16} /> Build Shortlist <ChevronRight size={14} />
          </button>
        </div>
      </div>

      <div className="flex-1 p-8 space-y-6 max-w-5xl w-full mx-auto">
        {error && (
          <div className="flex gap-3 p-4 bg-red-500/8 border border-red-500/25 rounded-xl text-red-300 text-sm">
            <AlertCircle size={16} className="shrink-0 mt-0.5" />
            <div><strong>Error:</strong> {error}</div>
          </div>
        )}

        {loading && (
          <div className="flex items-center gap-3 p-4 bg-purple-500/8 border border-purple-500/25 rounded-xl text-purple-200 text-sm">
            <Loader2 size={18} className="spinner shrink-0" />
            {loadMsg || 'Processing…'}
          </div>
        )}

        {/* Parsed JD info bar */}
        <div className="card animate-fade-up">
          <div className="flex gap-4 flex-wrap">
            <div className="flex-1 min-w-[200px]">
              <p className="text-xs font-bold text-white/30 uppercase tracking-widest mb-2">Parsed JD</p>
              <p className="font-bold text-lg">{parsedJD.role_title}</p>
              <p className="text-sm text-white/40">
                📍 {parsedJD.location} · {parsedJD.min_experience_years}+ yrs · {parsedJD.employment_type}
              </p>
            </div>
            <div className="flex flex-wrap gap-1.5 items-start">
              {(parsedJD.required_skills || []).map(s => <span key={s} className="tag">{s}</span>)}
            </div>
          </div>
        </div>

        {/* Candidate cards */}
        <div className="animate-fade-up space-y-4">
          <div className="flex items-center gap-2 text-sm text-white/40">
            <Users size={16} />
            <span>{candidates.length} candidates sorted by match score · engage to simulate outreach</span>
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
      </div>
    </div>
  )
}
