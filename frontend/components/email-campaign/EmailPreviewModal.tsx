'use client'

type Props = {
  open: boolean
  html: string
  subject: string
  onClose: () => void
}

export default function EmailPreviewModal({ open, html, subject, onClose }: Props) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" onClick={onClose}>
      <div className="mx-4 w-full max-w-3xl rounded-2xl bg-white shadow-2xl overflow-hidden" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0056b3" strokeWidth="2" strokeLinecap="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-900">Preview Email</h3>
              <p className="text-xs text-slate-500">{subject || '[Tidak ada subjek]'}</p>
            </div>
          </div>
          <button onClick={onClose} className="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-300 text-slate-400 hover:bg-slate-100 transition-colors">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <div className="max-h-[75vh] overflow-y-auto bg-slate-100">
          {html ? (
            <iframe srcDoc={html} className="w-full" style={{height:'70vh',border:'none'}} title="Email Preview" />
          ) : (
            <div className="flex items-center justify-center h-[50vh] text-sm text-slate-400">Tidak ada preview</div>
          )}
        </div>
      </div>
    </div>
  )
}
