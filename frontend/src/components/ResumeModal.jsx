import { useEffect, useRef, useState } from 'react'
import { X, ExternalLink, Download, Loader2, AlertCircle } from 'lucide-react'
import { API_BASE } from '../lib/api'

/**
 * Full-screen PDF preview modal.
 * Opens the resume as an iframe inside the app.
 * Props:
 *   candidate  – { name, resume_url, domain, experience_years, location }
 *   onClose    – function to close the modal
 */
export default function ResumeModal({ candidate, onClose }) {
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState(false)
  const [downloaded, setDownloaded] = useState(false)
  const overlayRef = useRef(null)

  const fileUrl  = candidate?.resume_url ? `${API_BASE}${candidate.resume_url}` : null
  const safeName = (candidate?.name || 'Candidate').replace(/\s+/g, '_')

  // Close on Escape key
  useEffect(() => {
    const handler = e => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  // Prevent body scroll when modal is open
  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => { document.body.style.overflow = '' }
  }, [])

  // Close when clicking the dark overlay (not the modal itself)
  function handleOverlayClick(e) {
    if (e.target === overlayRef.current) onClose()
  }

  function handleDownload() {
    if (!fileUrl) return
    const link = document.createElement('a')
    link.href     = fileUrl
    link.download = `${safeName}_Resume.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    setDownloaded(true)
    setTimeout(() => setDownloaded(false), 3000)
  }

  return (
    <div
      ref={overlayRef}
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(0,0,0,0.80)', backdropFilter: 'blur(6px)' }}
      onClick={handleOverlayClick}>

      {/* Modal container */}
      <div
        className="relative flex flex-col w-full max-w-4xl rounded-2xl overflow-hidden animate-fade-up"
        style={{ height: '90vh', background: '#0f0f17', border: '1px solid rgba(255,255,255,0.10)' }}>

        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-white/[0.07] shrink-0">
          <div>
            <h2 className="font-bold text-lg">{candidate?.name}</h2>
            <p className="text-xs text-white/40 mt-0.5">
              {candidate?.domain} · {candidate?.experience_years}y exp · {candidate?.location}
            </p>
          </div>

          <div className="flex items-center gap-2">
            {/* View in new tab */}
            <a
              href={fileUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-white/[0.06] border border-white/10 text-white/70 hover:text-white hover:border-purple-500/40 transition-colors">
              <ExternalLink size={13}/> Open in New Tab
            </a>

            {/* Download */}
            <button
              onClick={handleDownload}
              className={`flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border transition-colors
                ${downloaded
                  ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-300'
                  : 'bg-purple-500/15 border-purple-500/30 text-purple-300 hover:bg-purple-500/25'}`}>
              <Download size={13}/>
              {downloaded ? 'Downloaded!' : 'Download PDF'}
            </button>

            {/* Close */}
            <button
              onClick={onClose}
              className="flex items-center justify-center w-8 h-8 rounded-lg bg-white/[0.06] border border-white/10 text-white/50 hover:text-white hover:bg-red-500/15 hover:border-red-500/30 transition-colors">
              <X size={16}/>
            </button>
          </div>
        </div>

        {/* PDF Viewer */}
        <div className="relative flex-1 bg-[#1a1a2e]">
          {/* Loading spinner */}
          {loading && !error && (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 z-10">
              <Loader2 size={28} className="animate-spin text-purple-400" />
              <p className="text-sm text-white/40">Loading resume…</p>
            </div>
          )}

          {/* Error state */}
          {error && (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-4">
              <AlertCircle size={36} className="text-red-400" />
              <p className="text-white/60 text-sm">Could not load the resume preview.</p>
              <div className="flex gap-3">
                <a
                  href={fileUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-secondary text-xs px-4 py-2 flex items-center gap-1.5">
                  <ExternalLink size={13}/> Open in New Tab Instead
                </a>
                <button onClick={handleDownload} className="btn-primary text-xs px-4 py-2 flex items-center gap-1.5">
                  <Download size={13}/> Download PDF
                </button>
              </div>
            </div>
          )}

          {/* The actual PDF iframe */}
          {fileUrl && (
            <iframe
              src={fileUrl}
              title={`${candidate?.name} Resume`}
              className="w-full h-full border-0"
              style={{ display: loading || error ? 'none' : 'block' }}
              onLoad={() => setLoading(false)}
              onError={() => { setLoading(false); setError(true) }}
            />
          )}

          {!fileUrl && (
            <div className="absolute inset-0 flex items-center justify-center">
              <p className="text-white/30">No resume available for this candidate.</p>
            </div>
          )}
        </div>

        {/* Footer hint */}
        <div className="px-5 py-2.5 border-t border-white/[0.05] text-[10px] text-white/20 text-center shrink-0">
          Press <kbd className="px-1.5 py-0.5 rounded bg-white/10 text-white/40">Esc</kbd> or click outside to close
        </div>
      </div>
    </div>
  )
}
