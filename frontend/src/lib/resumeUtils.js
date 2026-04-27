import { binaryFetch } from './api'
import { showToast } from '../components/Toast'

/**
 * View or download a candidate resume PDF via fetch+blob.
 * Uses binaryFetch so it goes through Vite proxy / VITE_API_URL.
 *
 * action = 'view'     → opens PDF in a new browser tab
 * action = 'download' → saves PDF to disk as CandidateName_Resume.pdf
 */
export async function handleResume(candidateId, candidateName, action = 'download', setLoading) {
  if (setLoading) setLoading(true)
  try {
    const res = await binaryFetch(`/api/resume/${candidateId}`)

    if (!res.ok) {
      throw new Error(`Server returned ${res.status} — ${res.statusText}`)
    }

    const blob = await res.blob()
    if (blob.size === 0) throw new Error('Empty file received')

    const blobUrl = URL.createObjectURL(blob)
    const safeName = (candidateName || 'Candidate').replace(/\s+/g, '_')

    if (action === 'view') {
      const tab = window.open('', '_blank')
      if (tab) {
        tab.location.href = blobUrl
        showToast(`Opening ${candidateName}'s resume in new tab`, 'success', 3000)
      } else {
        // Popup blocked — fall back to download
        const a = document.createElement('a')
        a.href = blobUrl
        a.download = `${safeName}_Resume.pdf`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        showToast('Popup blocked — resume downloaded instead', 'info', 4000)
      }
    } else {
      const a = document.createElement('a')
      a.href = blobUrl
      a.download = `${safeName}_Resume.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      showToast(`Downloading ${candidateName}'s resume…`, 'success', 3000)
    }

    setTimeout(() => URL.revokeObjectURL(blobUrl), 60000)
  } catch (err) {
    const msg = err.message || 'Unknown error'
    if (msg.includes('Failed to fetch') || msg.includes('NetworkError') || msg.includes('fetch')) {
      showToast(
        'Backend server is not running.\nPlease double-click run.bat to start the servers.',
        'error',
        8000
      )
    } else {
      showToast('Resume error: ' + msg, 'error', 6000)
    }
  } finally {
    if (setLoading) setLoading(false)
  }
}
