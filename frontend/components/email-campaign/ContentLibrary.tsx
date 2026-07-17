'use client'
import { useState, useEffect, useCallback } from 'react'

type FileItem = { name: string; category: string; category_label: string; size: number; size_label: string; modified: string }
type Props = { API: string; onBack: () => void }

export default function ContentLibrary({ API, onBack }: Props) {
  const [files, setFiles] = useState<FileItem[]>([])
  const [loading, setLoading] = useState(true)
  const [category, setCategory] = useState('')
  const [uploading, setUploading] = useState(false)
  const [msg, setMsg] = useState('')

  const fetchFiles = useCallback(async (cat?: string) => {
    setLoading(true)
    try {
      const r = await fetch(`${API}/api/email-campaign/content-library?category=${cat || ''}`)
      const d = await r.json()
      if (d.success) setFiles(d.data.files)
    } catch { setFiles([]) }
    setLoading(false)
  }, [API])

  useEffect(() => { fetchFiles(category) }, [category, fetchFiles])

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true); setMsg('')
    const form = new FormData()
    form.append('file', file)
    form.append('category', 'brochures')
    try {
      const r = await fetch(`${API}/api/email-campaign/content-library/upload`, { method: 'POST', body: form })
      const d = await r.json()
      if (d.success) { setMsg(`✅ ${file.name} uploaded`); fetchFiles(category) }
      else setMsg(`❌ ${d.detail || 'Upload failed'}`)
    } catch { setMsg('❌ Upload error') }
    setUploading(false)
  }

  const handleDelete = async (cat: string, name: string) => {
    if (!confirm(`Delete ${name}?`)) return
    try {
      await fetch(`${API}/api/email-campaign/content-library/${cat}/${name}`, { method: 'DELETE' })
      fetchFiles(category)
    } catch {}
  }

  const catLabels: Record<string, string> = { compro: 'Company Profile', brochures: 'Brochures', case_studies: 'Case Studies' }
  const catList = ['', ...Object.keys(catLabels)]

  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-[0_1px_3px_rgba(0,0,0,0.04)]">
      <div className="flex items-center justify-between border-b border-slate-100 px-5 py-3.5">
        <div className="flex items-center gap-3">
          <button onClick={onBack} className="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M19 12H5"/><polyline points="12 19 5 12 12 5"/></svg>
          </button>
          <h2 className="text-base font-semibold text-slate-900">Content Library</h2>
        </div>
        <div className="flex items-center gap-2">
          <label htmlFor="cl-upload" className={`inline-flex cursor-pointer items-center gap-1.5 rounded-lg bg-[#0056b3] px-3 py-1.5 text-xs font-semibold text-white transition-all hover:bg-[#003d7a] ${uploading ? 'opacity-50' : ''}`}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
            {uploading ? 'Uploading...' : 'Upload'}
          </label>
          <input id="cl-upload" type="file" className="hidden" onChange={handleUpload} accept=".pdf,.docx,.pptx,.jpg,.png" />
        </div>
      </div>

      {/* Category filter */}
      <div className="flex items-center gap-1 border-b border-slate-100 px-5 py-2">
        {catList.map(c => (
          <button key={c} onClick={() => setCategory(c)}
            className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${category === c ? 'bg-slate-100 text-slate-800' : 'text-slate-400 hover:text-slate-600'}`}>
            {c ? catLabels[c] : 'All'}
          </button>
        ))}
      </div>

      {msg && <div className="px-5 py-2 text-xs text-slate-600">{msg}</div>}

      {/* File list */}
      <div className="px-5 py-3">
        {loading ? (
          <p className="text-xs text-slate-400">Loading...</p>
        ) : files.length === 0 ? (
          <div className="flex flex-col items-center py-10">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" strokeWidth="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            <p className="mt-3 text-sm text-slate-500">No files yet</p>
            <p className="text-xs text-slate-400">Upload brochures, case studies, or company profiles</p>
          </div>
        ) : (
          <div className="space-y-1">
            {files.map(f => (
              <div key={f.name} className="flex items-center justify-between rounded-lg border border-slate-100 px-3 py-2.5 transition-colors hover:bg-slate-50">
                <div className="flex items-center gap-3 min-w-0">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-slate-800">{f.name}</p>
                    <p className="text-[10px] text-slate-400">{f.size_label} · {f.category_label}</p>
                  </div>
                </div>
                <button onClick={() => handleDelete(f.category, f.name)}
                  className="ml-3 shrink-0 rounded-md p-1.5 text-slate-300 transition-colors hover:bg-red-50 hover:text-red-500">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
