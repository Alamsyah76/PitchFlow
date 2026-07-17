'use client'

type Props = {
  activeTpl: any
  selectedCount: number
  sending: boolean
  sendResult: string
  onBack: () => void
  onSend: () => void
}

export default function ReviewSend({ activeTpl, selectedCount, sending, sendResult, onBack, onSend }: Props) {
  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-slate-900">Review &amp; Kirim</h2>
          <p className="mt-0.5 text-xs text-slate-500">Periksa kembali sebelum mengirim</p>
        </div>
        <button onClick={onBack}
          className="inline-flex items-center gap-1.5 rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-600 shadow-sm transition-colors hover:bg-slate-50">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
          Kembali
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-3 gap-4">
        <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0056b3" strokeWidth="1.5" strokeLinecap="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
            </div>
            <div>
              <p className="text-xs font-medium text-slate-500">Template</p>
              <p className="mt-0.5 text-sm font-semibold text-slate-900">{activeTpl?.title || '-'}</p>
            </div>
          </div>
        </div>
        <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#059669" strokeWidth="1.5" strokeLinecap="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
            </div>
            <div>
              <p className="text-xs font-medium text-slate-500">Penerima</p>
              <p className="mt-0.5 text-sm font-semibold text-slate-900">{selectedCount} kontak</p>
            </div>
          </div>
        </div>
        <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm">
          {sendResult ? (
            <div className="flex items-center gap-3">
              <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${sendResult.startsWith('Terkirim') ? 'bg-emerald-50' : 'bg-red-50'}`}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
                  stroke={sendResult.startsWith('Terkirim') ? '#059669' : '#dc2626'} strokeWidth="1.5" strokeLinecap="round">
                  {sendResult.startsWith('Terkirim') ? <polyline points="20 6 9 17 4 12"/> : <><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></>}
                </svg>
              </div>
              <div>
                <p className={`text-sm font-semibold ${sendResult.startsWith('Terkirim') ? 'text-emerald-700' : 'text-red-700'}`}>{sendResult}</p>
              </div>
            </div>
          ) : (
            <div className="flex flex-col justify-between h-full">
              <p className="text-xs font-medium text-slate-500">Aksi</p>
              <button onClick={onSend} disabled={sending || selectedCount === 0}
                className="mt-3 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-[#0056b3] to-[#003d7a] px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:shadow-md hover:brightness-110 active:scale-[0.97] disabled:opacity-40 disabled:cursor-not-allowed">
                {sending ? (
                  <>
                    <svg className="animate-spin" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><circle cx="12" cy="12" r="10" strokeDasharray="32" strokeDashoffset="32" strokeLinecap="round"/></svg>
                    Mengirim...
                  </>
                ) : (
                  <>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                    Kirim ke {selectedCount} kontak
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
