// In dev: VITE_API_URL is undefined → empty string → Vite proxy forwards /api/* to localhost:8000
// In production (Vercel): VITE_API_URL = your Render backend URL (e.g. https://talentscout-ai-backend.onrender.com)
export const API_BASE = import.meta.env.VITE_API_URL || ''

export async function apiFetch(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  return res
}
