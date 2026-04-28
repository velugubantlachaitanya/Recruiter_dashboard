import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Sparkles, AlertCircle, Loader2 } from 'lucide-react'
import { apiFetch, extractError } from '../lib/api'
import { usePipeline } from '../context/PipelineContext'
import JDUploader from '../components/JDUploader'

export default function JDPage() {
  const navigate = useNavigate()
  const { setParsedJD, setRawJD, setCandidates, setShortlist, resetPipeline } = usePipeline()

  const [loading, setLoading] = useState(false)
  const [loadMsg, setLoadMsg] = useState('')
  const [error, setError]     = useState('')

  function setErr(e) { setError(e); setLoading(false) }

  // JD parsed → match candidates → navigate to /candidates
  async function onJDParsed(jd, jdText) {
    resetPipeline()
    setParsedJD(jd); setRawJD(jdText); setError('')
    setLoading(true); setLoadMsg('ML matching candidates…')
    try {
      const res = await apiFetch('/api/match-candidates', {
        method: 'POST',
        body: JSON.stringify({ jd }),
      })
      if (!res.ok) throw new Error(await extractError(res))
      const data = await res.json()
      setCandidates(data.candidates || [])
      setLoading(false)
      navigate('/candidates')
    } catch (e) { setErr(e.message) }
  }

  // Full pipeline → navigate to /shortlist
  async function onFullPipeline(jdText) {
    resetPipeline()
    setLoading(true); setLoadMsg('Running full AI pipeline…'); setError('')
    try {
      const res = await apiFetch('/api/full-pipeline', {
        method: 'POST',
        body: JSON.stringify({ jd_text: jdText, engage_top_n: 6 }),
      })
      if (!res.ok) throw new Error(await extractError(res))
      const data = await res.json()
      setParsedJD(data.parsed_jd)
      const sl = data.shortlist || []
      setCandidates(sl)
      setShortlist(sl)
      setLoading(false)
      navigate('/shortlist')
    } catch (e) { setErr(e.message) }
  }

  return (
    <div className="flex-1 flex flex-col">
      {/* Header */}
      <div className="border-b border-white/[0.06] px-8 py-5">
        <h1 className="text-2xl font-black bg-gradient-to-r from-purple-300 to-blue-300 bg-clip-text text-transparent">
          Recruiter Dashboard
        </h1>
        <p className="text-sm text-white/35 mt-0.5">AI-Powered Talent Scouting & Engagement</p>
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 mt-3 text-xs text-white/30">
          <span className="text-purple-400 font-semibold">📋 Step 1: Paste Job Description</span>
          <span>›</span><span>🔍 Candidates</span>
          <span>›</span><span>⭐ Shortlist</span>
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

        <div className="grid md:grid-cols-2 gap-6 animate-fade-up">
          {/* JD uploader */}
          <div className="card">
            <JDUploader onParsed={onJDParsed} loading={loading} />
          </div>

          {/* Full pipeline shortcut */}
          <div className="card flex flex-col gap-4">
            <p className="text-xs font-bold text-white/30 uppercase tracking-widest">Or run full pipeline at once</p>
            <p className="text-sm text-white/50 leading-relaxed">
              Click <strong className="text-white/70">Run Full Pipeline</strong> to parse the JD, match all candidates,
              simulate outreach with the top 6, and generate the final star-rated shortlist — all in one shot.
            </p>
            <div className="flex-1 flex items-end">
              <button
                className="btn-primary w-full justify-center py-3"
                disabled={loading}
                onClick={() => {
                  const jdText = document.querySelector('textarea')?.value
                  if (!jdText?.trim()) {
                    setError('Please paste a Job Description first, or click Load Demo JD.')
                    return
                  }
                  onFullPipeline(jdText)
                }}>
                <Sparkles size={18} /> Run Full Pipeline
              </button>
            </div>
            <p className="text-xs text-white/20 text-center">Runs Steps 1–4 automatically · ~30–60s</p>
          </div>
        </div>
      </div>
    </div>
  )
}
