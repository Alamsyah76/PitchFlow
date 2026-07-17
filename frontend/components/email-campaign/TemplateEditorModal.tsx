'use client'
import { useState, useRef, useEffect } from 'react'
import ImportFromWebModal from './ImportFromWebModal'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8042'

type Props = {
  open: boolean
  tpl: any
  onSave: (data: any) => void
  onClose: () => void
  senderCfg?: { name: string; email: string; company: string; logo_b64: string }
}

export default function TemplateEditorModal({ open, tpl, onSave, onClose, senderCfg }: Props) {
  if (!open) return null

  const [title, setTitle] = useState(tpl?.title || '')
  const [subject, setSubject] = useState(tpl?.subject || '')
  const [ccEmail, setCcEmail] = useState(tpl?.cc_email || '')
  const [logo, setLogo] = useState(tpl?.logo_b64 || senderCfg?.logo_b64 || '')
  const [intro, setIntro] = useState(tpl?.sections?.intro || '')
  const [body, setBody] = useState(tpl?.body_html || '')
  const [closing, setClosing] = useState(tpl?.sections?.closing || '')
  const [signature, setSignature] = useState(tpl?.sections?.signature || '')
  const [attachments, setAttachments] = useState<{filename:string;size:number}[]>([])
  const [uploading, setUploading] = useState(false)
  const [showImport, setShowImport] = useState(false)

  const logoRef = useRef<HTMLInputElement>(null)
  const fileRef = useRef<HTMLInputElement>(null)
  const tid = tpl?.id || ''

  // Load attachments when modal opens
  useEffect(() => {
    if (!tid) { setAttachments([]); return }
    fetch(`${API}/api/email-campaign/templates/${tid}/attachments`)
      .then(r => r.json())
      .then(d => { if (d.success) setAttachments(d.data.attachments) })
      .catch(() => setAttachments([]))
  }, [tid])

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file || !tid) return
    setUploading(true)
    const fd = new FormData()
    fd.append('file', file)
    try {
      const r = await fetch(`${API}/api/email-campaign/templates/${tid}/attachments`, { method: 'POST', body: fd })
      const d = await r.json()
      if (d.success) {
        setAttachments(prev => [...prev, d.data])
      } else alert(d.detail || 'Upload failed')
    } catch { alert('Upload gagal') }
    setUploading(false)
    if (fileRef.current) fileRef.current.value = ''
  }

  const handleDeleteAttachment = async (filename: string) => {
    if (!tid) return
    try {
      const r = await fetch(`${API}/api/email-campaign/templates/${tid}/attachments/${filename}`, { method: 'DELETE' })
      const d = await r.json()
      if (d.success) setAttachments(prev => prev.filter(a => a.filename !== filename))
    } catch { alert('Hapus gagal') }
  }

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024*1024) return (bytes/1024).toFixed(1) + ' KB'
    return (bytes/(1024*1024)).toFixed(1) + ' MB'
  }

  const handleLogo = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      const b64 = reader.result as string
      setLogo(b64.split(',')[1] || b64)
    }
    reader.readAsDataURL(file)
  }

  const handleSave = () => {
    const headerHtml = logo
      ? `<div class="header"><img src="data:image/png;base64,${logo}" alt="Logo" class="logo-img" style="max-width:200px;height:auto" /></div>`
      : ''
    onSave({
      ...tpl,
      title, subject,
      cc_email: ccEmail,
      logo_b64: logo,
      body_html: body,
      body_text: body.replace(/<[^>]*>/g, ''),
      sections: { header: headerHtml, greeting: '', intro, closing, signature, footer: '' },
    })
  }

  const handleWebImport = (data: { title: string; subject: string; body_html: string; body_text: string; sections: any }) => {
    setTitle(data.title)
    setSubject(data.subject)
    if (data.body_html) setBody(data.body_html)
    if (data.sections?.intro) setIntro(data.sections.intro)
    if (data.sections?.closing) setClosing(data.sections.closing)
    if (data.sections?.signature) setSignature(data.sections.signature)
  }

  const execCmd = (cmd: string) => { document.execCommand(cmd) }

  // ── Build preview HTML (fully rendered email) ──
  const previewHtml = `<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
  body{font-family:'Segoe UI',Arial,sans-serif;line-height:1.7;color:#333;margin:0;padding:0;background:#f5f7fa}
  .wrap{max-width:580px;margin:20px auto;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08)}
  .hd{padding:24px 28px 8px;text-align:center;border-bottom:1px solid #e8e8e8}
  .bd{padding:24px 28px}
  .ft{padding:16px 28px;font-size:11px;color:#999;border-top:1px solid #e8e8e8;background:#fafafa;text-align:center}
  .greeting{font-size:16px;font-weight:600;color:#111;margin-bottom:18px}
  .intro-box{border-left:4px solid #0056b3;background:#eef4fb;padding:14px 18px;margin:16px 0;border-radius:0 6px 6px 0;font-size:14px}
  .sig{border-top:1px solid #e8e8e8;padding-top:16px;margin-top:16px;font-size:13px}
  p{margin:0 0 12px}
</style></head><body>
<div class="wrap">
  ${logo ? `<div class="hd"><img src="data:image/png;base64,${logo}" style="max-height:50px" /></div>` : ''}
  <div class="bd">
    <p class="greeting">Kepada Yth. Bapak/Ibu <strong>Nama Kontak</strong>${senderCfg?.company ? ',<br>'+senderCfg.company : ''}</p>
    <div style="font-size:12px;color:#999;padding:8px 12px;background:#f9f9f9;border-radius:6px;margin-bottom:16px">Subject: ${subject || '<span style="color:#ccc">[not set]</span>'}</div>
    ${intro ? '<div class="intro-box">'+intro+'</div>' : ''}
    ${body ? '<div>'+body+'</div>' : '<div style="padding:20px;text-align:center;color:#ccc;border:1px dashed #ddd;border-radius:6px;font-size:13px">Content area — start typing</div>'}
    ${closing ? '<p style="margin-top:16px">'+closing+'</p>' : ''}
    ${signature ? '<div class="sig">'+signature+'</div>' : ''}
  </div>
  <div class="ft">${senderCfg?.company || ''} &mdash; Email Campaign</div>
</div>
</body></html>`

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/40 backdrop-blur-sm py-8" onClick={onClose}>
      <div className="mx-4 w-full max-w-6xl rounded-2xl bg-white shadow-2xl overflow-hidden" onClick={e => e.stopPropagation()}>

        {/* ── Top Bar ── */}
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4 bg-white sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-50 to-blue-100">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0056b3" strokeWidth="1.5" strokeLinecap="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/></svg>
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-900">{tpl?.id ? 'Edit Template' : 'New Template'}</h2>
              <p className="text-xs text-slate-500">Use {'{name}'}, {'{company}'}, {'{email}'} as placeholders</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={onClose} className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors">Cancel</button>
            <button onClick={handleSave}
              className="inline-flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-[#0056b3] to-[#003d7a] px-5 py-2 text-sm font-semibold text-white shadow-sm hover:shadow-md hover:brightness-110 active:scale-[0.97] transition-all">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><polyline points="20 6 9 17 4 12"/></svg>
              Save Template
            </button>
          </div>
        </div>

        {/* ── Body ── */}
        <div className="grid grid-cols-2 gap-0">
          {/* ── LEFT: Form ── */}
          <div className="border-r border-slate-200 p-6 space-y-5 max-h-[calc(100vh-160px)] overflow-y-auto">

            {/* Template Name */}
            <div>
              <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-500">Template Name</label>
              <input value={title} onChange={e => setTitle(e.target.value)}
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 placeholder-slate-400 transition-colors focus:border-blue-400 focus:ring-2 focus:ring-blue-100 focus:outline-none"
                placeholder="e.g. Product Introduction" />
            </div>

            {/* Subject */}
            <div>
              <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-500">Subject Line</label>
              <input value={subject} onChange={e => setSubject(e.target.value)}
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 placeholder-slate-400 transition-colors focus:border-blue-400 focus:ring-2 focus:ring-blue-100 focus:outline-none"
                placeholder="Enter email subject" />
            </div>

            {/* Import from Web */}
            <div>
              <button onClick={() => setShowImport(true)}
                className="inline-flex w-full items-center justify-center gap-2 rounded-xl border-2 border-dashed border-blue-300 bg-blue-50 px-4 py-3 text-sm font-medium text-blue-700 transition-all hover:border-blue-400 hover:bg-blue-100">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                Import dari Web
              </button>
            </div>

            {/* CC Email */}
            <div>
              <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-500">CC Email</label>
              <input value={ccEmail} onChange={e => setCcEmail(e.target.value)}
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 placeholder-slate-400 transition-colors focus:border-blue-400 focus:ring-2 focus:ring-blue-100 focus:outline-none"
                placeholder="cc@example.com (optional)" />
              <p className="mt-1 text-[10px] text-slate-400">All sent emails will be CC'd to this address</p>
            </div>

            {/* Logo */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-500">Company Logo</label>
                {logo && <button onClick={() => setLogo('')} className="text-[11px] text-red-400 hover:text-red-600 font-medium">Remove</button>}
              </div>
              <div className="flex items-center gap-4">
                <div className="flex-shrink-0 w-20 h-20 rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 flex items-center justify-center overflow-hidden">
                  {logo ? (
                    <img src={`data:image/png;base64,${logo}`} alt="Logo" className="max-w-full max-h-full object-contain p-2" />
                  ) : (
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="1.5" strokeLinecap="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
                  )}
                </div>
                <div>
                  <input ref={logoRef} type="file" accept="image/*" onChange={handleLogo} className="hidden" />
                  <button onClick={() => logoRef.current?.click()}
                    className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-xs font-medium text-slate-600 hover:bg-slate-50 transition-colors">
                    {logo ? 'Change Logo' : 'Upload Logo'}
                  </button>
                  <p className="mt-1 text-[10px] text-slate-400">PNG/JPG, max 2MB</p>
                </div>
              </div>
            </div>

            <div className="border-t border-slate-100" />

            {/* Intro */}
            <div>
              <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-500">Intro</label>
              <div contentEditable suppressContentEditableWarning
                onInput={e => setIntro(e.currentTarget.innerHTML)}
                className="min-h-[60px] rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 transition-colors focus:border-blue-400 focus:ring-2 focus:ring-blue-100 focus:outline-none"
                dangerouslySetInnerHTML={{__html: intro || ''}} />
              <p className="mt-1 text-[10px] text-slate-400">Opening paragraph before main content</p>
            </div>

            {/* Content */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-500">Content</label>
                <div className="flex items-center gap-1 rounded-lg border border-slate-200 bg-white p-0.5 shadow-sm">
                  <button onMouseDown={e => { e.preventDefault(); execCmd('bold') }}
                    className="rounded-md px-2.5 py-1 text-xs font-bold text-slate-600 hover:bg-slate-100 transition-colors" title="Bold (Ctrl+B)">B</button>
                  <button onMouseDown={e => { e.preventDefault(); execCmd('italic') }}
                    className="rounded-md px-2.5 py-1 text-xs italic text-slate-600 hover:bg-slate-100 transition-colors" title="Italic (Ctrl+I)">I</button>
                  <span className="text-[10px] text-slate-300">|</span>
                  <button onMouseDown={e => { e.preventDefault(); execCmd('insertUnorderedList') }}
                    className="rounded-md px-2 py-1 text-xs text-slate-600 hover:bg-slate-100" title="Bullet list">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
                  </button>
                </div>
              </div>
              <div contentEditable suppressContentEditableWarning
                onInput={e => setBody(e.currentTarget.innerHTML)}
                className="min-h-[200px] rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 transition-colors focus:border-blue-400 focus:ring-2 focus:ring-blue-100 focus:outline-none"
                dangerouslySetInnerHTML={{__html: body || ''}} />
            </div>

            {/* Closing */}
            <div>
              <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-500">Closing</label>
              <div contentEditable suppressContentEditableWarning
                onInput={e => setClosing(e.currentTarget.innerHTML)}
                className="min-h-[60px] rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 transition-colors focus:border-blue-400 focus:ring-2 focus:ring-blue-100 focus:outline-none"
                dangerouslySetInnerHTML={{__html: closing || ''}} />
            </div>

            {/* Signature */}
            <div>
              <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-500">Signature</label>
              <div contentEditable suppressContentEditableWarning
                onInput={e => setSignature(e.currentTarget.innerHTML)}
                className="min-h-[80px] rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 transition-colors focus:border-blue-400 focus:ring-2 focus:ring-blue-100 focus:outline-none"
                dangerouslySetInnerHTML={{__html: signature || ''}} />
              <p className="mt-1 text-[10px] text-slate-400">Name, position, contact info</p>
            </div>

            {/* ── Attachments ── */}
            <div className="border-t border-slate-100 pt-4">
              <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-slate-500">Attachments</label>
              <input ref={fileRef} type="file" onChange={handleUpload} className="hidden" />
              <button onClick={() => fileRef.current?.click()} disabled={uploading || !tid}
                className="inline-flex items-center gap-1.5 rounded-xl border border-slate-300 bg-white px-4 py-2 text-xs font-medium text-slate-600 hover:bg-slate-50 transition-colors disabled:opacity-40">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                {uploading ? 'Uploading...' : 'Upload File'}
              </button>
              <p className="mt-1 text-[10px] text-slate-400">Max 10MB per file</p>

              {attachments.length > 0 && (
                <div className="mt-3 space-y-2">
                  {attachments.map((a, i) => (
                    <div key={i} className="flex items-center justify-between rounded-lg border border-slate-200 bg-slate-50 px-3 py-2">
                      <div className="flex items-center gap-2 min-w-0">
                        <svg className="flex-shrink-0" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                        <span className="truncate text-xs font-medium text-slate-700">{a.filename}</span>
                        <span className="text-[10px] text-slate-400 flex-shrink-0">{formatSize(a.size)}</span>
                      </div>
                      <button onClick={() => handleDeleteAttachment(a.filename)}
                        className="flex-shrink-0 ml-2 rounded-md p-1 text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                      </button>
                    </div>
                  ))}
                </div>
              )}
              {!tid && <p className="mt-2 text-[10px] text-amber-500">Save template first to enable file uploads</p>}
            </div>

          </div>

          {/* ── RIGHT: Live Preview (iframe) ── */}
          <div className="bg-slate-50/70 p-6 max-h-[calc(100vh-160px)] overflow-y-auto">
            <div className="flex items-center gap-2 mb-4">
              <div className="h-2 w-2 rounded-full bg-emerald-400" />
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Live Preview</p>
            </div>

            <iframe
              srcDoc={previewHtml}
              className="w-full rounded-2xl border border-slate-200 bg-white shadow-sm"
              style={{height:'500px',border:'none'}}
              title="Email Preview"
            />

            <div className="mt-4 rounded-xl border border-slate-200 bg-white p-3">
              <p className="text-[10px] font-medium text-slate-500 mb-2">Available Placeholders</p>
              <div className="flex flex-wrap gap-1.5">
                {['{name}','{company}','{email}','{job_title}','{phone}'].map(p => (
                  <code key={p} className="rounded-md bg-slate-100 px-2 py-0.5 text-[10px] font-mono text-slate-600">{p}</code>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      <ImportFromWebModal
        show={showImport}
        onClose={() => setShowImport(false)}
        onImport={handleWebImport}
      />
    </div>
  )
}
