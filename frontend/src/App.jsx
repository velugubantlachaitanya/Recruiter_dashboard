import { Routes, Route, NavLink, useLocation } from 'react-router-dom'
import { Zap, LayoutDashboard, Users } from 'lucide-react'
import JDPage from './pages/JDPage'
import CandidatesPage from './pages/CandidatesPage'
import ShortlistPage from './pages/ShortlistPage'
import RecruiterView from './pages/RecruiterView'
import Toast from './components/Toast'

// Sidebar nav items — only top-level sections
const NAV = [
  { to: '/',         label: 'Dashboard',      icon: LayoutDashboard, sub: 'Step-by-step pipeline',  exact: true },
  { to: '/recruiter',label: 'Recruiter View', icon: Users,           sub: 'One-shot full pipeline', exact: false },
]

// Pipeline breadcrumb steps for the header
const STEPS = [
  { path: '/',            label: '📋 Parse JD'  },
  { path: '/candidates',  label: '🔍 Candidates' },
  { path: '/shortlist',   label: '⭐ Shortlist'  },
]

function Sidebar() {
  const location = useLocation()
  const isDashboardArea = ['/', '/candidates', '/shortlist'].includes(location.pathname)

  return (
    <aside className="w-60 shrink-0 bg-[#0f0f1e] border-r border-white/[0.06] flex flex-col fixed inset-y-0 left-0 z-50">
      {/* Logo */}
      <div className="px-5 py-6 border-b border-white/[0.06]">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#7c6ff7] to-[#5a8cf8] flex items-center justify-center shadow-lg shadow-purple-900/50">
            <Zap size={16} fill="white" color="white" />
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
        {NAV.map(({ to, label, icon: Icon, sub, exact }) => {
          const active = exact ? location.pathname === to : location.pathname.startsWith(to)
          // Dashboard section is active for all three pipeline routes
          const dashboardActive = to === '/' && isDashboardArea
          const isActive = dashboardActive || (!exact && active)
          return (
            <NavLink key={to} to={to}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-all text-sm
                ${isActive
                  ? 'bg-purple-500/15 border border-purple-500/30 text-white'
                  : 'text-white/50 hover:bg-white/[0.04] hover:text-white/80'}`}>
              <Icon size={16} className={isActive ? 'text-purple-400' : ''} />
              <div>
                <div className="font-semibold leading-tight">{label}</div>
                <div className="text-[10px] text-white/30 leading-tight">{sub}</div>
              </div>
            </NavLink>
          )
        })}

        {/* Pipeline progress — only shown in dashboard area */}
        {isDashboardArea && (
          <div className="mt-4 pt-4 border-t border-white/[0.04]">
            <p className="px-3 pb-2 text-[10px] font-bold text-white/20 uppercase tracking-widest">Pipeline Steps</p>
            {STEPS.map(({ path, label }) => {
              const active = location.pathname === path
              const done = (
                (path === '/' && ['/candidates', '/shortlist'].includes(location.pathname)) ||
                (path === '/candidates' && location.pathname === '/shortlist')
              )
              return (
                <div key={path}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold
                    ${active ? 'text-purple-300' : done ? 'text-emerald-400' : 'text-white/20'}`}>
                  <span>{done ? '✓' : '·'}</span>
                  <span>{label}</span>
                </div>
              )
            })}
          </div>
        )}
      </nav>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-white/[0.06] space-y-1 text-[10px] text-white/25 text-center">
        <div>Deccan AI · Catalyst Hackathon 2026</div>
        <div>Chaitanya Prasad Velugubantla</div>
        <div>Open-source ML + FastAPI</div>
      </div>
    </aside>
  )
}

export default function App() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />

      <main className="flex-1 ml-60 flex flex-col min-h-screen">
        <Routes>
          <Route path="/"           element={<JDPage />} />
          <Route path="/candidates" element={<CandidatesPage />} />
          <Route path="/shortlist"  element={<ShortlistPage />} />
          <Route path="/recruiter"  element={<RecruiterView />} />
          {/* Fallback */}
          <Route path="*"           element={<JDPage />} />
        </Routes>
      </main>

      <Toast />
    </div>
  )
}
