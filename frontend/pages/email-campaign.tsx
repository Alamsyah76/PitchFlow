'use client'
import { useEffect, useState, useRef } from 'react'
import AppShell from '../components/app-shell/AppShell'
import StepProgress from '../components/email-campaign/StepProgress'
import TemplateList from '../components/email-campaign/TemplateList'
import AudienceList from '../components/email-campaign/AudienceList'
import ReviewSend from '../components/email-campaign/ReviewSend'
import LogView from '../components/email-campaign/LogView'
import EditContactModal from '../components/email-campaign/EditContactModal'
import AddContactModal from '../components/email-campaign/AddContactModal'
import TemplateEditorModal from '../components/email-campaign/TemplateEditorModal'
import EmailPreviewModal from '../components/email-campaign/EmailPreviewModal'
import TemplatePreviewModal from '../components/email-campaign/TemplatePreviewModal'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8042'

// Test emails — always selectable even if status=sent
const TEST_EMAILS = new Set(['alams.kombet@gmail.com', 'alams.kombet@yahoo.com'])

type CampaignStatus = { total_contacts: number; valid_emails: number; already_sent: number; pending: number; daily_limit: number; test_emails_available?: number }
type Contact = { name: string; email: string; company: string; job_title: string; phone?: string; status?: string; last_template?: string }
type LogEntry = { timestamp: string; email: string; name: string; company: string; status: string; error: string }

function stripHtml(h: string): string {
  if (!h) return ''
  return h.replace(/<[^>]*>/g, '').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&nbsp;/g, ' ').replace(/&#39;/g, "'").trim()
}

export default function EmailCampaignRoute() {
  const [status, setStatus] = useState<CampaignStatus | null>(null)
  const [contacts, setContacts] = useState<Contact[]>([])
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [sendResult, setSendResult] = useState('')
  const [step, setStep] = useState<1|2|3|4>(1)
  const [selectedIdx, setSelectedIdx] = useState<Set<number>>(new Set())
  const [searchQ, setSearchQ] = useState('')
  const [templates, setTemplates] = useState<any[]>([])
  const [activeTplId, setActiveTplId] = useState('default')
  const [editIdx, setEditIdx] = useState<number|null>(null)
  const [editName, setEditName] = useState('')
  const [editEmail, setEditEmail] = useState('')
  const [showAdd, setShowAdd] = useState(false)
  const [addError, setAddError] = useState('')
  const [limitInput, setLimitInput] = useState('10')
  const [showLimit, setShowLimit] = useState(false)
  const [editTpl, setEditTpl] = useState<any>(null)
  const [showEditor, setShowEditor] = useState(false)
  const [previewHtml, setPreviewHtml] = useState('')
  const [previewSubject, setPreviewSubject] = useState('')
  const [showPreview, setShowPreview] = useState(false)
  const [viewTpl, setViewTpl] = useState<any>(null)
  const [showTplPreview, setShowTplPreview] = useState(false)
  const [senderCfg, setSenderCfg] = useState<any>({name:'',email:'',company:'',logo_b64:''})
  const [filter, setFilter] = useState<'all' | 'pending' | 'sent' | 'bounced' | 'unsubscribed'>('all')
  const [scanningBounces, setScanningBounces] = useState(false)
  const searchTimer = useRef<NodeJS.Timeout|null>(null)

  // ── Data ──
  async function fetchTemplates() {
    try { const r=await fetch(`${API}/api/email-campaign/templates`); const d=await r.json(); if(d.success){setTemplates(d.data.templates||[]); setActiveTplId(d.data.active_template_id||d.data.active_template||'default')} } catch {}
  }
  async function fetchStatus() {
    try { const r=await fetch(`${API}/api/email-campaign/status`); const d=await r.json(); if(d.success){setStatus(d.data);setLimitInput(String(d.data.daily_limit))} } catch {}
  }
  async function fetchContacts(q?: string) {
    setLoading(true)
    try { const url=`${API}/api/email-campaign/preview?limit=500${(q??searchQ)?'&q='+encodeURIComponent(q??searchQ):''}`; const r=await fetch(url); const d=await r.json(); if(d.success) setContacts(d.data.preview) } catch {}
    setLoading(false)
  }
  async function fetchLog() { try { const r=await fetch(`${API}/api/email-campaign/log?limit=50`); const d=await r.json(); if(d.success) setLogs(d.data) } catch {} }
  async function fetchSenderCfg() { try { const r=await fetch(`${API}/api/email-campaign/sender-settings`); const d=await r.json(); if(d.success) setSenderCfg({name:d.data?.name||'',email:d.data?.email||'',company:d.data?.company||'',logo_b64:d.data?.logo_b64||''}) } catch {} }
  useEffect(() => { fetchStatus(); fetchContacts(); fetchLog(); fetchTemplates() }, [])
  useEffect(() => { if(searchTimer.current) clearTimeout(searchTimer.current); searchTimer.current=setTimeout(()=>fetchContacts(searchQ),300); return ()=>{if(searchTimer.current) clearTimeout(searchTimer.current)} }, [searchQ])

  // ── Template ──
  async function activateTpl(tid: string) { try { await fetch(`${API}/api/email-campaign/templates/${tid}/activate`,{method:'POST'}); await fetchTemplates() } catch {} }
  async function deleteTpl(tid: string) { if(!confirm('Hapus template ini?')) return; try { await fetch(`${API}/api/email-campaign/templates/${tid}`,{method:'DELETE'}); await fetchTemplates() } catch {} }
  async function saveTemplate(data: any) {
    if (!data.title) { alert('Please fill in the Template Name'); return }
    const isNew = !data.id
    const url = isNew ? `${API}/api/email-campaign/templates` : `${API}/api/email-campaign/templates/${data.id}`
    const body = JSON.stringify({title:data.title,subject:data.subject,body_html:data.body_html||'',body_text:data.body_text||'',sections:data.sections||{}})
    console.log('SAVE URL:', url)
    console.log('SAVE BODY:', body)
    try {
      const r = await fetch(url, {
        method: isNew ? 'POST' : 'PUT',
        headers: {'Content-Type':'application/json'},
        body
      })
      const d = await r.json()
      console.log('SAVE RESPONSE:', d)
      if (d.success) { setShowEditor(false); setEditTpl(null); await fetchTemplates() }
      else alert('Save failed: ' + (d.detail || d.message || d.error || 'Unknown error'))
    } catch (e: any) { alert('Network error: ' + e.message) }
  }
  function openEditor(tpl: any) { setEditTpl(tpl); setShowEditor(true); fetchSenderCfg() }

  // ── Send ──
  function sendSelected() {
    if(selectedIdx.size===0||sending) return
    setSending(true); setSendResult('')
    fetch(`${API}/api/email-campaign/send-selected`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({indices:Array.from(selectedIdx)})})
      .then(r=>r.json()).then(d=>{setSendResult(d.success?`Terkirim ${d.sent_count}`:`Gagal: ${d.message}`); setSelectedIdx(new Set()); fetchStatus(); fetchContacts(); fetchLog()})
      .catch(e=>setSendResult(`Gagal: ${e.message}`)).finally(()=>setSending(false))
  }

  // ── Preview ──
  async function loadPreview(idx: number) {
    try {
      const r = await fetch(`${API}/api/email-campaign/preview-email/${idx}`)
      const d = await r.json()
      if (d.success) { setPreviewHtml(d.data.html); setPreviewSubject(d.data.subject); setShowPreview(true) }
    } catch {}
  }

  // ── Contact ──
  function openEdit(i:number,c:Contact){setEditIdx(i);setEditName(c.name);setEditEmail(c.email)}
  async function saveEdit() { if(editIdx===null) return; try { await fetch(`${API}/api/email-campaign/contacts/edit`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({index:editIdx,name:editName,email:editEmail})}) } catch {}; setEditIdx(null) }
  async function deleteContact(email:string){if(!confirm('Hapus kontak ini?'))return; try{await fetch(`${API}/api/email-campaign/contacts/delete-by-email`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email})});await fetchContacts();await fetchStatus()}catch{}}
  async function handleUpload(e:React.ChangeEvent<HTMLInputElement>){const f=e.target.files?.[0];if(!f)return;const fd=new FormData();fd.append('file',f);try{const r=await fetch(`${API}/api/email-campaign/upload`,{method:'POST',body:fd});const d=await r.json();if(d.success){setSearchQ('');await fetchContacts('');await fetchStatus()}}catch{}}
  async function handleScanBounces(){setScanningBounces(true);try{const r=await fetch(`${API}/api/email-campaign/bounces/scan`,{method:'POST'});const d=await r.json();alert(d.message||(d.success?'Bounce scan done':'Scan failed'));if(d.success){await fetchContacts('');await fetchStatus();await fetchLog()}}catch{alert('Gagal terhubung ke server')}setScanningBounces(false)}
  async function handleAddManual(data:{name:string;email:string;phone:string;job_title:string;company:string}) {
    setAddError('')
    try {
      const r=await fetch(`${API}/api/email-campaign/contacts/manual`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)})
      const d=await r.json()
      if(d.success){setShowAdd(false);setSearchQ('');await fetchContacts('');await fetchStatus()}
      else setAddError(d.detail||d.message||'Gagal')
    } catch { setAddError('Gagal terhubung') }
  }

  // ── Daily Limit ──
  async function saveLimit(val: number) { try { await fetch(`${API}/api/email-campaign/settings`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({daily_limit:val})}); await fetchStatus() } catch {}; setShowLimit(false) }

  // ── Selection ──
  function toggleSelect(i:number){
    const c = contacts[i]
    // Jangan izinkan pilih kontak yang sudah terkirim, bounced, atau unsubscribed, kecuali test email
    if((c?.status === 'sent' || c?.status === 'bounced' || c?.status === 'unsubscribed') && !TEST_EMAILS.has(c.email)) return
    setSelectedIdx(p=>{const n=new Set(p);n.has(i)?n.delete(i):n.add(i);return n})
  }
  function selectAll(){
    const limit=Math.min(status?.daily_limit||contacts.length, contacts.length)
    // Hanya hitung kontak pending (belum terkirim) + test email dalam range limit
    const pendingIndices = contacts.slice(0, limit).reduce<number[]>((acc, c, i) => {
      if(c.status !== 'sent' || TEST_EMAILS.has(c.email)) acc.push(i)
      return acc
    }, [])
    const selectedPending = pendingIndices.filter(i => selectedIdx.has(i))
    const allPendingSelected = selectedPending.length === pendingIndices.length
    setSelectedIdx(p=>{
      const n=new Set(p)
      if(allPendingSelected){
        // Unselect semua pending di range
        pendingIndices.forEach(i => n.delete(i))
      } else {
        // Select semua pending di range
        pendingIndices.forEach(i => n.add(i))
      }
      return n
    })
  }

  const activeTpl = templates.find((t:any)=>t.id===activeTplId)

  return (
    <AppShell activeRoute="/email-campaign">
      <main className="p-6 pt-4">
        <div className="mx-auto max-w-screen-2xl">
          {status && (
            <div className="mb-5 grid grid-cols-5 gap-3">
              <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-[0_1px_2px_rgba(0,0,0,0.04)]">
                <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Total</p>
                <p className="mt-1 text-xl font-bold text-slate-900">{status.total_contacts}</p>
              </div>
              <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-[0_1px_2px_rgba(0,0,0,0.04)]">
                <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Valid</p>
                <p className="mt-1 text-xl font-bold text-emerald-600">{status.valid_emails}</p>
              </div>
              <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-[0_1px_2px_rgba(0,0,0,0.04)]">
                <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Sent</p>
                <p className="mt-1 text-xl font-bold text-blue-600">{status.already_sent}</p>
              </div>
              <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-[0_1px_2px_rgba(0,0,0,0.04)]">
                <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Pending</p>
                <p className="mt-1 text-xl font-bold text-amber-600">{status.pending}</p>
              </div>
              <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-[0_1px_2px_rgba(0,0,0,0.04)] relative">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Daily Limit</p>
                    <p className="mt-1 text-xl font-bold text-slate-900">{status.daily_limit}</p>
                  </div>
                  <button onClick={()=>setShowLimit(!showLimit)} className="flex h-7 w-7 items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
                  </button>
                </div>
                {showLimit && (
                  <div className="absolute right-0 top-full mt-2 z-10 w-56 rounded-xl border border-slate-200 bg-white p-4 shadow-xl">
                    <p className="mb-2 text-xs font-medium text-slate-600">Change daily limit</p>
                    <div className="flex items-center gap-2">
                      <input type="number" min="1" max="999" value={limitInput} onChange={e=>setLimitInput(e.target.value.replace(/\D/g,''))}
                        className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-center font-semibold focus:border-blue-400 focus:outline-none" />
                      <button onClick={()=>saveLimit(Number(limitInput))}
                        className="rounded-lg bg-gradient-to-r from-[#0056b3] to-[#003d7a] px-3 py-2 text-xs font-semibold text-white hover:brightness-110 whitespace-nowrap">Save</button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          <StepProgress step={step} setStep={setStep} />

          {step===1 && <TemplateList templates={templates} activeTplId={activeTplId} onActivate={activateTpl} onEdit={openEditor} onView={(t)=>{setViewTpl(t);setShowTplPreview(true)}} onDelete={deleteTpl} onNew={()=>{setEditTpl(null);setShowEditor(true);fetchSenderCfg()}} onNext={()=>setStep(2)} activeTpl={activeTpl} />}
          {step===2 && <AudienceList contacts={contacts} selectedIdx={selectedIdx} searchQ={searchQ} loading={loading} status={status} filter={filter} onFilterChange={setFilter} onSearch={setSearchQ} onToggle={toggleSelect} onSelectAll={selectAll} onUpload={handleUpload} onEdit={openEdit} onDelete={deleteContact} onBack={()=>setStep(1)} onReview={()=>{setStep(3); setSendResult('')}} onAddClick={()=>{setAddError('');setShowAdd(true)}} onScanBounces={handleScanBounces} scanningBounces={scanningBounces} />}
          {step===3 && <ReviewSend activeTpl={activeTpl} selectedCount={selectedIdx.size} sending={sending} sendResult={sendResult} onBack={()=>{setStep(2); setSendResult('')}} onSend={sendSelected} />}
          {step===4 && <LogView logs={logs} API={API} onClear={()=>{fetchLog();fetchStatus();fetchContacts()}} />}
        </div>

        {/* Modals */}
        <EditContactModal idx={editIdx} name={editName} email={editEmail} onClose={()=>setEditIdx(null)} setName={setEditName} setEmail={setEditEmail} onSave={saveEdit} />
        <AddContactModal open={showAdd} onClose={()=>setShowAdd(false)} onAdd={handleAddManual} error={addError} />
        <TemplateEditorModal open={showEditor} tpl={editTpl} onSave={saveTemplate} onClose={()=>{setShowEditor(false);setEditTpl(null)}} senderCfg={senderCfg} />
        <EmailPreviewModal open={showPreview} html={previewHtml} subject={previewSubject} onClose={()=>setShowPreview(false)} />
        <TemplatePreviewModal open={showTplPreview} tpl={viewTpl} onClose={()=>{setShowTplPreview(false);setViewTpl(null)}}
          onEdit={()=>{setShowTplPreview(false);openEditor(viewTpl)}} API={API} />
      </main>
    </AppShell>
  )
}
