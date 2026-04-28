import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { usePipeline } from '../context/PipelineContext'
import ShortlistTable from '../components/ShortlistTable'

export default function ShortlistPage() {
  const navigate = useNavigate()
  const { parsedJD, shortlist } = usePipeline()

  // Guard: if no shortlist, redirect to start
  useEffect(() => {
    if (!shortlist.length) navigate('/', { replace: true })
  }, [shortlist, navigate])

  function exportShortlist() {
    const blob = new Blob([JSON.stringify(shortlist, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = 'shortlist_output.json'; a.click()
    URL.revokeObjectURL(url)
  }

  if (!shortlist.length) return null

  return (
    <div className="flex-1 flex flex-col">
      {/* Header */}
      <div className="border-b border-white/[0.06] px-8 py-5 flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-black bg-gradient-to-r from-purple-300 to-blue-300 bg-clip-text text-transparent">
            Ranked Shortlist
          </h1>
          <p className="text-sm text-white/35 mt-0.5">
            {parsedJD?.role_title || 'Role'} · {shortlist.length} candidates ranked
          </p>
          {/* Breadcrumb */}
          <div className="flex items-center gap-2 mt-3 text-xs text-white/30">
            <button onClick={() => navigate('/')} className="hover:text-white/60 transition-colors">📋 JD Upload</button>
            <span>›</span>
            <button onClick={() => navigate('/candidates')} className="hover:text-white/60 transition-colors">🔍 Candidates</button>
            <span>›</span>
            <span className="text-purple-400 font-semibold">⭐ Step 3: Shortlist</span>
          </div>
        </div>
        <button className="btn-secondary flex items-center gap-2 text-sm px-4 py-2"
          onClick={() => navigate(-1)}>
          <ArrowLeft size={14} /> Back to Candidates
        </button>
      </div>

      <div className="flex-1 p-8 max-w-6xl w-full mx-auto">
        <div className="animate-fade-up">
          <ShortlistTable shortlist={shortlist} onExport={exportShortlist} />
        </div>
      </div>
    </div>
  )
}
