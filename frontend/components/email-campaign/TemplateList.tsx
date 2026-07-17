'use client'

type Props = {
  templates: any[]
  activeTplId: string
  onActivate: (id: string) => void
  onEdit: (tpl: any) => void
  onView: (tpl: any) => void
  onDelete: (id: string) => void
  onNew: () => void
  onNext: () => void
  activeTpl: any
}

export default function TemplateList({ templates, activeTplId, onActivate, onEdit, onView, onDelete, onNew, onNext, activeTpl }: Props) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-[0_1px_3px_rgba(0,0,0,0.04)]">
      <div className="flex items-center justify-between border-b border-slate-100 px-5 py-3.5">
        <div>
          <h2 className="text-sm font-semibold text-slate-900">Email Template</h2>
          <p className="mt-0.5 text-xs text-slate-400">{templates.length} template{templates.length !== 1 ? 's' : ''} available</p>
        </div>
        <button onClick={onNew}
          className="inline-flex items-center gap-1.5 rounded-lg bg-[#0056b3] px-3.5 py-2 text-xs font-semibold text-white shadow-sm transition-all hover:bg-[#003d7a] active:scale-[0.97]">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          New Template
        </button>
      </div>

      {templates.length === 0 ? (
        <div className="flex flex-col items-center justify-center px-6 py-14">
          <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-slate-100">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="1.5" strokeLinecap="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
          </div>
          <p className="text-sm font-medium text-slate-600">No templates yet</p>
          <p className="mt-1 text-xs text-slate-400">Create your first template to start your campaign</p>
        </div>
      ) : (
        <div className="divide-y divide-slate-100">
          {templates.map((t: any) => (
            <div key={t.id}
              className={`flex items-center justify-between px-5 py-3.5 transition-colors ${
                t.id === activeTplId ? 'bg-blue-50/40' : 'hover:bg-slate-50'
              }`}>
              <div className="flex items-center gap-3.5 min-w-0 flex-1">
                <div className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-md border-2 transition-colors cursor-pointer ${
                  t.id === activeTplId
                    ? 'border-[#0056b3] bg-[#0056b3]'
                    : 'border-slate-300 hover:border-slate-400'
                }`} onClick={() => onActivate(t.id)}>
                  {t.id === activeTplId && (
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3" strokeLinecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                  )}
                </div>
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="truncate text-sm font-medium text-slate-900">{t.title}</span>
                    {t.id === activeTplId && (
                      <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-semibold text-emerald-600">Active</span>
                    )}
                  </div>
                  <p className="mt-0.5 text-xs text-slate-400">{t.subject || 'No subject'}</p>
                </div>
              </div>
              <div className="flex items-center gap-1.5 shrink-0">
                <button onClick={() => onView(t)}
                  className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-600 shadow-sm transition-all hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700 active:scale-[0.95] whitespace-nowrap">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  View
                </button>
                <button onClick={() => onEdit(t)}
                  className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-600 shadow-sm transition-all hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700 active:scale-[0.95] whitespace-nowrap">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                  Edit
                </button>
                <button onClick={() => onDelete(t.id)}
                  className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-medium text-red-400 shadow-sm transition-all hover:border-red-200 hover:bg-red-50 hover:text-red-600 active:scale-[0.95] whitespace-nowrap">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="flex items-center justify-between rounded-b-xl border-t border-slate-100 bg-slate-50/50 px-5 py-3.5">
        <span className="text-xs text-slate-400">
          {activeTpl ? `Active: ${activeTpl.title}` : 'Select a template to continue'}
        </span>
        <button onClick={onNext} disabled={!activeTplId}
          className="inline-flex items-center gap-1.5 rounded-lg bg-[#0056b3] px-4 py-2 text-xs font-semibold text-white shadow-sm transition-all hover:bg-[#003d7a] active:scale-[0.97] disabled:opacity-40 disabled:cursor-not-allowed">
          Continue to Audience
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
        </button>
      </div>
    </div>
  )
}
