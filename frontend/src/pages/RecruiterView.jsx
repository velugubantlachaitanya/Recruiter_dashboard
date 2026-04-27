import { useState } from 'react'
import { Loader2, BarChart3 } from 'lucide-react'
import { apiFetch, extractError } from '../lib/api'
import ShortlistTable from '../components/ShortlistTable'

export default function RecruiterView() {
  const [jdText, setJdText]     = useState('')
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState('')
  const [shortlist, setShortlist] = useState([])
  const [parsedJD, setParsedJD] = useState(null)
  const [stats, setStats]       = useState(null)

  async function run() {
    if (!jdText.trim()) { setError('Paste a JD first.'); return }
    setLoading(true); setError(''); setShortlist([]); setParsedJD(null); setStats(null)
    try {
      const res = await apiFetch('/api/full-pipeline', {
        method: 'POST',
        body: JSON.stringify({ jd_text: jdText, engage_top_n: 8 })
      })
      if (!res.ok) throw new Error(await extractError(res))
      const data = await res.json()
      setShortlist(data.shortlist || [])
      setParsedJD(data.parsed_jd)
      const sl = data.shortlist || []
      setStats({
        total: sl.length,
        fiveStar: sl.filter(e => e.star_rating === 5).length,
        fourStar: sl.filter(e => e.star_rating === 4).length,
        avgCombined: sl.length ? (sl.reduce((s,e) => s + e.combined_score, 0) / sl.length).toFixed(1) : 0,
        engaged: data.engaged_candidates,
      })
    } catch(e) { setError(e.message) }
    setLoading(false)
  }

  function exportJSON() {
    const blob = new Blob([JSON.stringify(shortlist, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob); const a = document.createElement('a')
    a.href = url; a.download = 'shortlist_output.json'; a.click(); URL.revokeObjectURL(url)
  }

  return (
    <div className="flex-1 flex flex-col">
      <div className="border-b border-white/[0.06] px-8 py-5">
        <h1 className="text-2xl font-black bg-gradient-to-r from-blue-300 to-purple-300 bg-clip-text text-transparent">Recruiter View</h1>
        <p className="text-sm text-white/35 mt-0.5">Full pipeline · paste JD → get star-rated shortlist instantly</p>
      </div>
      <div className="flex-1 p-8 max-w-5xl w-full mx-auto space-y-6">
        <div className="card space-y-4">
          <label className="text-xs font-bold text-white/30 uppercase tracking-widest">Job Description</label>
          <textarea className="input min-h-[180px] resize-y" placeholder="Paste JD here…" value={jdText} onChange={e=>setJdText(e.target.value)} />
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <button className="btn-primary py-3 justify-center w-full" onClick={run} disabled={loading}>
            {loading ? <Loader2 size={18} className="spinner"/> : <BarChart3 size={18}/>}
            {loading ? 'Running full AI pipeline… (~30–60s)' : 'Run Full Pipeline & Generate Shortlist'}
          </button>
        </div>

        {parsedJD && (
          <div className="card animate-fade-up">
            <p className="text-xs font-bold text-white/30 uppercase tracking-widest mb-3">Extracted JD</p>
            <p className="font-bold text-lg">{parsedJD.role_title}</p>
            <p className="text-sm text-white/40">📍 {parsedJD.location} · {parsedJD.min_experience_years}+ yrs · {parsedJD.employment_type} · Remote: {parsedJD.remote_allowed ? 'Yes' : 'No'}</p>
            <div className="flex flex-wrap gap-1.5 mt-3">
              {(parsedJD.required_skills||[]).map(s=><span key={s} className="tag">{s}</span>)}
            </div>
          </div>
        )}

        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 animate-fade-up">
            {[
              { label:'Total Candidates', val: stats.total, color:'text-white' },
              { label:'⭐⭐⭐⭐⭐ Highly Rec.', val: stats.fiveStar, color:'text-emerald-400' },
              { label:'⭐⭐⭐⭐ Strong', val: stats.fourStar, color:'text-blue-400' },
              { label:'Avg Combined Score', val: stats.avgCombined, color:'text-purple-400' },
            ].map(s => (
              <div key={s.label} className="card-sm text-center">
                <div className={`text-3xl font-black font-mono ${s.color}`}>{s.val}</div>
                <div className="text-xs text-white/30 mt-1">{s.label}</div>
              </div>
            ))}
          </div>
        )}

        {shortlist.length > 0 && (
          <div className="animate-fade-up">
            <ShortlistTable shortlist={shortlist} onExport={exportJSON} />
          </div>
        )}
      </div>
    </div>
  )
}
