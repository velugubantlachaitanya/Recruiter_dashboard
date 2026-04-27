import { useEffect, useState } from 'react'

let _setToast = null

export function showToast(message, type = 'error', duration = 5000) {
  if (_setToast) _setToast({ message, type, id: Date.now() })
}

export default function Toast() {
  const [toast, setToast] = useState(null)
  _setToast = setToast

  useEffect(() => {
    if (!toast) return
    const t = setTimeout(() => setToast(null), toast.duration || 5000)
    return () => clearTimeout(t)
  }, [toast])

  if (!toast) return null

  const styles = {
    error:   'bg-red-950/90 border-red-500/40 text-red-200',
    success: 'bg-emerald-950/90 border-emerald-500/40 text-emerald-200',
    info:    'bg-blue-950/90 border-blue-500/40 text-blue-200',
  }
  const icons = { error: '✕', success: '✓', info: 'ℹ' }

  return (
    <div className={`fixed bottom-6 right-6 z-[999] flex items-start gap-3 px-5 py-4 rounded-2xl border shadow-2xl backdrop-blur-sm max-w-sm animate-fade-up ${styles[toast.type] || styles.error}`}>
      <span className="text-lg shrink-0 mt-0.5">{icons[toast.type] || icons.error}</span>
      <div>
        <p className="font-semibold text-sm">
          {toast.type === 'error' ? 'Error' : toast.type === 'success' ? 'Success' : 'Info'}
        </p>
        <p className="text-xs mt-0.5 opacity-80 leading-relaxed whitespace-pre-line">{toast.message}</p>
      </div>
      <button onClick={() => setToast(null)} className="ml-2 opacity-50 hover:opacity-100 text-lg leading-none shrink-0">×</button>
    </div>
  )
}
