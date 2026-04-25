export default function ChatSimulator({ conversation, candidateName }) {
  if (!conversation) return null
  return (
    <div className="bg-white/[0.03] rounded-xl p-4 space-y-3">
      <p className="text-xs font-bold text-white/30 uppercase tracking-wider">Simulated Outreach</p>
      {/* Recruiter email */}
      <div className="flex gap-2">
        <div className="w-7 h-7 rounded-full bg-purple-500/20 border border-purple-500/30 flex items-center justify-center text-xs font-bold text-purple-300 shrink-0">AI</div>
        <div className="flex-1 bg-purple-500/[0.07] border border-purple-500/20 rounded-2xl rounded-tl-sm px-4 py-3 text-sm text-white/70 leading-relaxed whitespace-pre-wrap">
          <p className="text-xs font-semibold text-purple-400 mb-2">Recruiter AI</p>
          {conversation.outreach_email}
        </div>
      </div>
      {/* Candidate reply */}
      <div className="flex gap-2 flex-row-reverse">
        <div className="w-7 h-7 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-xs font-bold text-emerald-300 shrink-0">{(candidateName||'?')[0]}</div>
        <div className="flex-1 bg-emerald-500/[0.06] border border-emerald-500/20 rounded-2xl rounded-tr-sm px-4 py-3 text-sm text-white/70 leading-relaxed whitespace-pre-wrap">
          <p className="text-xs font-semibold text-emerald-400 mb-2">{candidateName}</p>
          {conversation.candidate_reply}
        </div>
      </div>
      {/* Signals */}
      {(conversation.interest_signals || []).length > 0 && (
        <div className="flex flex-wrap gap-1.5 pt-1">
          {conversation.interest_signals.map(s => <span key={s} className="tag text-emerald-300 bg-emerald-500/10 border-emerald-500/20">{s}</span>)}
        </div>
      )}
    </div>
  )
}
