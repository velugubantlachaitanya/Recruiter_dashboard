import { apiFetch } from './api'

/**
 * View or download a candidate resume PDF.
 * Uses fetch() so it always goes through the Vite proxy / VITE_API_URL.
 *
 * action = 'view'     → opens PDF in a new browser tab
 * action = 'download' → saves PDF to disk
 */
export async function handleResume(candidateId, candidateName, action = 'download', setLoading) {
  if (setLoading) setLoading(true)
  try {
    const res = await apiFetch(`/api/resume/${candidateId}`)
    if (!res.ok) {
      const msg = await res.text().catch(() => res.statusText)
      throw new Error(`Server error ${res.status}: ${msg}`)
    }
    const blob = await res.blob()
    if (blob.size === 0) throw new Error('Empty file received from server')

    const blobUrl = URL.createObjectURL(blob)
    const safeName = (candidateName || 'Candidate').replace(/\s+/g, '_')

    if (action === 'view') {
      // Open in new tab — browser PDF viewer renders it inline
      const tab = window.open('', '_blank')
      if (tab) {
        tab.location.href = blobUrl
      } else {
        // Popup blocked fallback — force download instead
        const a = document.createElement('a')
        a.href = blobUrl
        a.download = `${safeName}_Resume.pdf`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
      }
    } else {
      // Download
      const a = document.createElement('a')
      a.href = blobUrl
      a.download = `${safeName}_Resume.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
    }

    // Revoke blob URL after 60s to free memory
    setTimeout(() => URL.revokeObjectURL(blobUrl), 60000)
  } catch (err) {
    const msg = err.message || 'Unknown error'
    if (msg.includes('Failed to fetch') || msg.includes('NetworkError')) {
      alert('Cannot reach the backend server.\n\nMake sure the backend is running at http://localhost:8000\n\nError: ' + msg)
    } else {
      alert('Resume error: ' + msg)
    }
  } finally {
    if (setLoading) setLoading(false)
  }
}
