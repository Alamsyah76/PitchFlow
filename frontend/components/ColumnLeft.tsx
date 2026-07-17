import React, { useRef, useState, DragEvent } from 'react'

type Props = {
  onUpload?: (file: File) => void
}

export default function ColumnLeft({ onUpload }: Props) {
  const fileRef = useRef<HTMLInputElement | null>(null)
  const [audience, setAudience] = useState('CIO')
  const [lang, setLang] = useState('en')
  const [primary, setPrimary] = useState('#0A84FF')
  const [secondary, setSecondary] = useState('#FFFFFF')
  const [logoFile, setLogoFile] = useState<File | null>(null)
  const [dragOver, setDragOver] = useState(false)

  function handleFileSelect(f?: File) {
    if (f && onUpload) onUpload(f)
  }

  function handleInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0]
    handleFileSelect(f)
  }

  function handleDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault()
    setDragOver(false)
    const f = e.dataTransfer.files?.[0]
    handleFileSelect(f)
  }

  function handleDragOver(e: DragEvent<HTMLDivElement>) {
    e.preventDefault()
    setDragOver(true)
  }

  return (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-slate-700">Source Document</label>
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={() => setDragOver(false)}
          onClick={() => fileRef.current?.click()}
          className={`mt-3 border-dashed border-2 rounded-lg p-6 text-center transition cursor-pointer ${dragOver ? 'bg-slate-50' : 'bg-white'} border-slate-200`}
        >
          <input ref={fileRef} type="file" accept="application/pdf" onChange={handleInputChange} className="hidden" />
          <svg className="mx-auto mb-2" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><path d="M14 2v6h6" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
          <div className="text-sm text-slate-500">Drag & drop a PDF here, or click to select</div>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700">Target Audience</label>
        <select value={audience} onChange={(e) => setAudience(e.target.value)} className="mt-3 w-full rounded-md border border-slate-200 px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-slate-300">
          <option>CIO</option>
          <option>IT Manager</option>
          <option>UMKM</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700">Language</label>
        <div className="mt-3 inline-flex rounded-md bg-white border border-slate-200 shadow-sm">
          <button onClick={() => setLang('en')} className={`px-3 py-2 text-sm ${lang==='en' ? 'bg-slate-50 text-slate-900' : 'text-slate-500'}`}>EN</button>
          <button onClick={() => setLang('id')} className={`px-3 py-2 text-sm ${lang==='id' ? 'bg-slate-50 text-slate-900' : 'text-slate-500'}`}>ID</button>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700">Brand Kit</label>
        <div className="mt-3 bg-white border border-slate-100 p-3 rounded-md">
          <div className="flex gap-2 items-center">
            <input value={primary} onChange={(e)=>setPrimary(e.target.value)} className="w-1/2 rounded-md border border-slate-200 px-2 py-1" />
            <input value={secondary} onChange={(e)=>setSecondary(e.target.value)} className="w-1/2 rounded-md border border-slate-200 px-2 py-1" />
          </div>
          <div className="mt-3">
            <label className="block text-sm text-slate-600">Logo</label>
            <input type="file" accept="image/*" onChange={(e)=> setLogoFile(e.target.files?.[0] ?? null)} className="mt-2" />
          </div>
        </div>
      </div>
    </div>
  )
}
