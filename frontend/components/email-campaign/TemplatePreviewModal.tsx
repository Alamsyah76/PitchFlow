'use client'

import { useState, useEffect } from 'react'

type Props = {
  open: boolean
  tpl: any
  onClose: () => void
  onEdit: () => void
  API: string
}

export default function TemplatePreviewModal({ open, tpl, onClose, onEdit, API }: Props) {
  if (!open || !tpl) return null

  const [html, setHtml] = useState('')
  const [subject, setSubject] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!open || !tpl) return
    setLoading(true)
    // Fetch preview from backend with contact index 0 (sample contact)
    fetch(`${API}/api/email-campaign/preview-email/0?template_id=${tpl.id}`)
      .then(r => r.json())
      .then(d => {
        if (d.success) { setHtml(d.data.html); setSubject(d.data.subject) }
        else setHtml('<p class="text-slate-400 p-8">Preview unavailable. Make sure there is a contact in the Audience.</p>')
      })
      .catch(() => setHtml('<p class="text-slate-400 p-8">Failed to load preview.</p>'))
      .finally(() => setLoading(false))
  }, [open, tpl?.id])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" onClick={onClose}>
      <div className="mx-4 w-full max-w-4xl rounded-2xl bg-white shadow-2xl overflow-hidden" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0056b3" strokeWidth="1.5" strokeLinecap="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-semibold text-slate-900">{tpl.title || 'Template'}</h3>
                {tpl.subject && <span className="hidden sm:inline text-xs text-slate-400">— {tpl.subject}</span>}
              </div>
              <p className="text-xs text-slate-500">Preview template email</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={onEdit}
              className="inline-flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-[#0056b3] to-[#003d7a] px-4 py-2 text-sm font-semibold text-white shadow-sm transition-all hover:shadow-md hover:brightness-110 active:scale-[0.97]">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
              Edit Template
            </button>
            <button onClick={onClose} className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-300 text-slate-400 hover:bg-slate-100 transition-colors" title="Tutup">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="bg-slate-100">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-24 gap-3">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
              <p className="text-sm text-slate-400">Loading preview...</p>
            </div>
          ) : (
            <iframe srcDoc={html} className="w-full" style={{height:'70vh',border:'none'}} title="Template Preview" />
          )}
        </div>

        {/* Footer info */}
        <div className="border-t border-slate-200 px-6 py-3 flex items-center justify-between text-xs text-slate-400">
          <span>
            Preview uses the first contact in the Audience as a sample.
            <span className="ml-1 text-slate-300">Placeholder: {`{name}`}, {`{company}`}, {`{email}`}</span>
          </span>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-700 font-medium">Close</button>
        </div>
      </div>
    </div>
  )
}
