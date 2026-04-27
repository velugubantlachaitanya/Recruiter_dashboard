import { binaryFetch } from './api'
import { showToast } from '../components/Toast'

/**
 * VIEW RESUME — opens the candidate's real open-source resume PDF directly.
 * Uses the resume_url from candidate data → no backend needed, instant.
 */
export function viewResume(resumeUrl, candidateName) {
  if (!resumeUrl) {
    showToast('No resume URL available for this candidate.', 'error', 4000)
    return
  }
  const tab = window.open(resumeUrl, '_blank', 'noopener,noreferrer')
  if (!tab) {
    // Popup blocked — copy URL to clipboard as fallback
    navigator.clipboard?.writeText(resumeUrl).then(() => {
      showToast('Popup blocked. Resume URL copied to clipboard!', 'info', 5000)
    }).catch(() => {
      showToast(`Popup blocked. Resume URL: ${resumeUrl}`, 'info', 8000)
    })
  } else {
    showToast(`Opening ${candidateName}'s resume…`, 'success', 2500)
  }
}

/**
 * DOWNLOAD RESUME — downloads a personalized PDF from the backend.
 * Falls back to opening the resume_url directly if backend is unreachable.
 */
export async function downloadResume(candidateId, candidateName, resumeUrl, setLoading) {
  if (setLoading) setLoading(true)
  try {
    const res = await binaryFetch(`/api/resume/${candidateId}`)

    if (!res.ok) throw new Error(`HTTP ${res.status}`)

    const blob = await res.blob()
    if (!blob || blob.size === 0) throw new Error('Empty response')

    const blobUrl = URL.createObjectURL(blob)
    const safeName = (candidateName || 'Candidate').replace(/\s+/g, '_')
    const a = document.createElement('a')
    a.href = blobUrl
    a.download = `${safeName}_Resume.pdf`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    setTimeout(() => URL.revokeObjectURL(blobUrl), 60000)
    showToast(`Downloading ${candidateName}'s resume…`, 'success', 3000)

  } catch {
    // Backend unreachable — open resume_url as fallback
    if (resumeUrl) {
      showToast(
        `Backend offline — opening sample resume for ${candidateName} instead.`,
        'info', 4000
      )
      window.open(resumeUrl, '_blank', 'noopener,noreferrer')
    } else {
      showToast(
        'Backend is not running. Start it with run.bat',
        'error', 6000
      )
    }
  } finally {
    if (setLoading) setLoading(false)
  }
}
