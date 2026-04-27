// In dev: VITE_API_URL is undefined → empty string → Vite proxy forwards /api/* to localhost:8000
// In production (Vercel): VITE_API_URL = your Render backend URL
export const API_BASE = import.meta.env.VITE_API_URL || ''

/** JSON API fetch — adds Content-Type: application/json */
export async function apiFetch(path, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    })
    return res
  } catch (err) {
    if (err.message === 'Failed to fetch' || err.name === 'TypeError') {
      throw new Error('Backend server is not running. Please double-click run.bat to start the servers.')
    }
    throw err
  }
}

/** Binary fetch — for PDF/file endpoints, no Content-Type override */
export async function binaryFetch(path) {
  try {
    const res = await fetch(`${API_BASE}${path}`)
    return res
  } catch (err) {
    if (err.message === 'Failed to fetch' || err.name === 'TypeError') {
      throw new Error('Backend server is not running. Please double-click run.bat to start the servers.')
    }
    throw err
  }
}

/** Extract a readable error message from a non-ok Response */
export async function extractError(res) {
  try {
    const text = await res.text()
    if (!text) return `Server returned error ${res.status}. Please restart the backend.`
    try {
      const json = JSON.parse(text)
      return json.detail || json.message || json.error || text.substring(0, 200)
    } catch {
      return text.substring(0, 200) || `Server returned error ${res.status}.`
    }
  } catch {
    return `Server returned error ${res.status}.`
  }
}
