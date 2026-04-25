import { useState } from 'react'
import { Zap, LayoutDashboard, Users } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import RecruiterView from './pages/RecruiterView'

const NAV = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, sub: 'Step-by-step pipeline' },
  { id: 'recruiter', label: 'Recruiter View', icon: Users, sub: 'One-shot full pipeline' },
]

export default function App() {
  const [page, setPage] = useState('dashboard')

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="w-60 shrink-0 bg-[#0f0f1e] border-r border-white/[0.06] flex flex-col fixed inset-y-0 left-0 z-50">
        {/* Logo */}
        <div className="px-5 py-6 border-b border-white/[0.06]">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#7c6ff7] to-[#5a8cf8] flex items-center justify-center shadow-lg shadow-purple-900/50">
              <Zap size={16} fill="white" color="white"/>
            </div>
            <div>
              <div className="font-black text-sm leading-tight">TalentScout AI</div>
              <div className="text-[10px] text-white/30 tracking-widest uppercase">Catalyst Hackathon</div>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 p-3 space-y-1">
          <p className="px-3 py-2 text-[10px] font-bold text-white/20 uppercase tracking-widest">Navigation</p>
          {NAV.map(n => {
            const Icon = n.icon
            const active = page === n.id
            return (
              <button key={n.id} onClick={() => setPage(n.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-all text-sm
                  ${active ? 'bg-purple-500/15 border border-purple-500/30 text-white' : 'text-white/50 hover:bg-white/[0.04] hover:text-white/80'}`}>
                <Icon size={16} className={active ? 'text-purple-400' : ''} />
                <div>
                  <div className="font-semibold leading-tight">{n.label}</div>
                  <div className="text-[10px] text-white/30 leading-tight">{n.sub}</div>
                </div>
              </button>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="px-5 py-4 border-t border-white/[0.06] space-y-1 text-[10px] text-white/25 text-center">
          <div>Deccan AI · Catalyst Hackathon 2026</div>
          <div>Chaitanya Prasad Velugubantla</div>
          <div>Claude API + sklearn ML</div>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 ml-60 flex flex-col min-h-screen">
        {page === 'dashboard' ? <Dashboard /> : <RecruiterView />}
      </main>
    </div>
  )
}
