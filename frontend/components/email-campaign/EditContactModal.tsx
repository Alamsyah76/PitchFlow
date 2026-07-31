'use client'

type Props = {
  idx: number | null
  name: string
  email: string
  onClose: () => void
  setName: (v: string) => void
  setEmail: (v: string) => void
  onSave: () => void
}

export default function EditContactModal({ idx, name, email, onClose, setName, setEmail, onSave }: Props) {
  if (idx === null) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40" onClick={onClose}>
      <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-2xl" onClick={e => e.stopPropagation()}>
        <h3 className="mb-4 text-base font-semibold text-slate-800">Edit Contact</h3>
        <div className="space-y-3">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">Name</label>
            <input value={name} onChange={e => setName(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none" />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">Email</label>
            <input value={email} onChange={e => setEmail(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none" />
          </div>
        </div>
        <div className="mt-5 flex justify-end gap-3">
          <button onClick={onClose} className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50">Cancel</button>
          <button onClick={onSave} className="rounded-lg bg-gradient-to-r from-[#0056b3] to-[#003d7a] px-4 py-2 text-sm font-semibold text-white hover:brightness-110">Save</button>
        </div>
      </div>
    </div>
  )
}
