'use client'

type Props = {
  open: boolean
  onClose: () => void
  onAdd: (data: {name:string; email:string; phone:string; job_title:string; company:string}) => void
  error: string
}

export default function AddContactModal({ open, onClose, onAdd, error }: Props) {
  if (!open) return null

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const fd = new FormData(e.target as HTMLFormElement)
    onAdd({
      name: (fd.get('name') as string)?.trim() || '',
      email: (fd.get('email') as string)?.trim() || '',
      phone: (fd.get('phone') as string)?.trim() || '',
      job_title: (fd.get('job_title') as string)?.trim() || '',
      company: (fd.get('company') as string)?.trim() || '',
    })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" onClick={onClose}>
      <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-5">
          <div>
            <h3 className="text-base font-semibold text-slate-900">Tambah Kontak</h3>
            <p className="mt-0.5 text-xs text-slate-500">Masukkan data kontak baru</p>
          </div>
          <button onClick={onClose} className="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-300 text-slate-400 hover:bg-slate-100 transition-colors">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>

        {error && (
          <div className="mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 flex items-center gap-2">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1.5 block text-xs font-medium text-slate-600">Nama <span className="text-red-400">*</span></label>
              <input name="name" required
                className="w-full rounded-xl border border-slate-300 bg-slate-50 px-3.5 py-2.5 text-sm text-slate-900 placeholder-slate-400 transition-colors focus:border-blue-400 focus:bg-white focus:outline-none"
                placeholder="Nama lengkap" />
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-medium text-slate-600">Email <span className="text-red-400">*</span></label>
              <input name="email" type="email" required
                className="w-full rounded-xl border border-slate-300 bg-slate-50 px-3.5 py-2.5 text-sm text-slate-900 placeholder-slate-400 transition-colors focus:border-blue-400 focus:bg-white focus:outline-none"
                placeholder="email@perusahaan.com" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1.5 block text-xs font-medium text-slate-600">No. Telp/WA</label>
              <div className="flex rounded-xl border border-slate-300 overflow-hidden focus-within:border-blue-400 focus-within:ring-1 focus-within:ring-blue-400 transition-colors">
                <span className="inline-flex items-center bg-slate-100 px-3 text-sm font-medium text-slate-500 border-r border-slate-300">+62</span>
                <input name="phone"
                  className="w-full bg-slate-50 px-3.5 py-2.5 text-sm outline-none focus:bg-white"
                  placeholder="8123456789" />
              </div>
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-medium text-slate-600">Jabatan</label>
              <input name="job_title"
                className="w-full rounded-xl border border-slate-300 bg-slate-50 px-3.5 py-2.5 text-sm text-slate-900 placeholder-slate-400 transition-colors focus:border-blue-400 focus:bg-white focus:outline-none"
                placeholder="CEO / Manager" />
            </div>
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium text-slate-600">Perusahaan</label>
            <input name="company"
              className="w-full rounded-xl border border-slate-300 bg-slate-50 px-3.5 py-2.5 text-sm text-slate-900 placeholder-slate-400 transition-colors focus:border-blue-400 focus:bg-white focus:outline-none"
              placeholder="Nama perusahaan" />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose}
              className="rounded-xl border border-slate-300 bg-white px-5 py-2.5 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-50">Batal</button>
            <button type="submit"
              className="rounded-xl bg-gradient-to-r from-[#0056b3] to-[#003d7a] px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:shadow-md hover:brightness-110 active:scale-[0.97]">
              <span className="flex items-center gap-2">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                Tambah Kontak
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
