import { apiFetch } from './api'

/**
 * Fetch the resume PDF via apiFetch (goes through Vite proxy / VITE_API_URL)
 * then open it in a new tab or trigger a download.
 */
export async function handleResume(candidateId, candidateName, action = 'download') {
  try {
    const res = await apiFetch(`/api/resume/${candidateId}`)
    if (!res.ok) throw new Error(`Server returned ${res.status}`)
    const blob = await res.blob()
    const blobUrl = URL.createObjectURL(blob)

    if (action === 'view') {
      window.open(blobUrl, '_blank')
    } else {
      const a = document.createElement('a')
      a.href = blobUrl
      a.download = `${(candidateName || 'Candidate').replace(/\s+/g, '_')}_Resume.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
    }
    // Revoke blob URL after 30s
    setTimeout(() => URL.revokeObjectURL(blobUrl), 30000)
  } catch (err) {
    alert(`Resume unavailable: ${err.message}`)
  }
}
