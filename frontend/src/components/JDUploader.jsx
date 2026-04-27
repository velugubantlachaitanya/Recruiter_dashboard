import { useState } from 'react'
import { FileText, Sparkles, Loader2 } from 'lucide-react'
import { apiFetch } from '../lib/api'

const DEMO_JD = `Senior ML Engineer – AI Products
Company: NovaBridge Technologies (Series B, Hyderabad + Remote)

We are looking for a passionate Senior ML Engineer to join our AI Products team.

Requirements:
- 5+ years ML/AI experience
- Python, PyTorch, TensorFlow (proficient)
- LLM/Transformer experience (fine-tuning, RAG, LangChain)
- MLflow or similar experiment tracking
- FastAPI or similar backend framework
- AWS or GCP cloud deployment

Nice to have:
- Kubernetes, Docker
- Open-source contributions (Hugging Face, LangChain)
- Experience with RAG pipelines

Responsibilities:
- Train and deploy production ML models
- Build LLM-powered features for our SaaS platform
- Collaborate with engineers on model serving
- Mentor junior ML engineers

Location: Hyderabad, India (hybrid/remote OK)
Employment: Full-time
Compensation: ₹30–50 LPA + equity`

export default function JDUploader({ onParsed, loading }) {
  const [jdText, setJdText] = useState('')
  const [error, setError] = useState('')

  async function handleParse() {
    if (!jdText.trim()) { setError('Please paste a job description first.'); return }
    setError('')
    try {
      const res = await apiFetch('/api/parse-jd', {
        method: 'POST',
        body: JSON.stringify({ jd_text: jdText })
      })
      
      if (!res.ok) {
        const errorText = await res.text()
        console.error('Backend error:', errorText)
        try {
          const data = JSON.parse(errorText)
          throw new Error(data.detail || 'Parse failed')
        } catch {
          throw new Error(`Server error: ${errorText.substring(0, 100)}`)
        }
      }
      
      const data = await res.json()
      onParsed(data.parsed_jd, jdText)
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <label className="text-xs font-bold text-white/30 uppercase tracking-widest flex items-center gap-2">
          <FileText size={13}/> Job Description
        </label>
        <button className="btn-secondary text-xs px-3 py-1.5" onClick={() => setJdText(DEMO_JD)}>Load Demo JD</button>
      </div>
      <textarea
        className="input min-h-[260px] resize-y leading-relaxed"
        placeholder="Paste your job description here…&#10;&#10;Include: title, company, requirements, responsibilities, compensation."
        value={jdText}
        onChange={e => { setJdText(e.target.value); setError('') }}
      />
      {error && <p className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-2">{error}</p>}
      <button className="btn-primary w-full justify-center py-3 text-base" onClick={handleParse} disabled={loading || !jdText.trim()}>
        {loading ? <Loader2 size={18} className="spinner"/> : <Sparkles size={18}/>}
        {loading ? 'Parsing JD…' : 'Parse JD & Start Matching'}
      </button>
      <p className="text-center text-xs text-white/25">Claude API will extract role, skills, location, experience requirements</p>
    </div>
  )
}
