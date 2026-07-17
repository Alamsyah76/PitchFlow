'use client'
import { useState, useEffect } from 'react'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8042'

type Settings = {
  daily_limit: number
  sender_name: string
  sender_email: string
  smtp_host: string
  smtp_port: number
  smtp_username: string
  smtp_password: string
  imap_host: string
  imap_port: number
}

export default function CampaignSettings({ onBack }: { onBack?: () => void }) {
  const [settings, setSettings] = useState<Settings>({
    daily_limit: 10, sender_name: '', sender_email: '',
    smtp_host: '', smtp_port: 465, smtp_username: '', smtp_password: '',
    imap_host: '', imap_port: 993,
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [showPw, setShowPw] = useState(false)

  useEffect(() => {
    fetch(`${API}/api/email-campaign/settings`)
      .then(r => r.json())
      .then(d => { if (d.success) setSettings(prev => ({ ...prev, ...d.data })) })
      .catch(() => setMessage('Failed to load settings'))
      .finally(() => setLoading(false))
  }, [])

  async function handleSave() {
    setSaving(true)
    setMessage('')
    try {
      const r = await fetch(`${API}/api/email-campaign/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
      })
      const d = await r.json()
      if (d.success) setMessage('✅ Settings saved successfully')
      else setMessage('❌ ' + (d.detail || 'Save failed'))
    } catch { setMessage('❌ Network error') }
    setSaving(false)
  }

  if (loading) return <div className="flex items-center justify-center py-16"><div className="h-6 w-6 animate-spin rounded-full border-2 border-[#0056b3] border-t-transparent" /></div>

  const Field = ({ label, value, onChange, type = 'text', placeholder = '', hint = '' }: { label: string; value: string; onChange: (v: string) => void; type?: string; placeholder?: string; hint?: string }) => (
    <div>
      <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-500">{label}</label>
      <input type={type} value={value} onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 placeholder-slate-400 transition-colors focus:border-blue-400 focus:ring-2 focus:ring-blue-100 focus:outline-none" />
      {hint && <p className="mt-1 text-[10px] text-slate-400">{hint}</p>}
    </div>
  )

  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-[0_1px_3px_rgba(0,0,0,0.04)]">
      <div className="flex items-center justify-between border-b border-slate-100 px-5 py-3.5">
        <div className="flex items-center gap-3">
          {onBack && (
            <button onClick={onBack} type="button" className="flex h-7 w-7 items-center justify-center rounded-md text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
            </button>
          )}
          <div>
            <h2 className="text-sm font-semibold text-slate-900">SMTP Configuration</h2>
            <p className="mt-0.5 text-xs text-slate-400">Configure email sender and SMTP server settings</p>
          </div>
        </div>
      </div>

      <div className="space-y-5 px-6 py-5 max-h-[500px] overflow-y-auto">
        {message && (
          <div className={`rounded-xl px-4 py-3 text-sm ${message.startsWith('✅') ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600'}`}>
            {message}
          </div>
        )}

        <div className="border-b border-slate-100 pb-1">
          <h3 className="text-sm font-semibold text-slate-800">Sender Identity</h3>
        </div>

        <Field label="Sender Name" value={settings.sender_name} onChange={v => setSettings(s => ({ ...s, sender_name: v }))}
          placeholder="e.g. Alamsyah" hint="Display name recipients will see" />

        <Field label="Sender Email" value={settings.sender_email} onChange={v => setSettings(s => ({ ...s, sender_email: v }))}
          placeholder="e.g. alamsyah@example.com" hint="Must match SMTP credentials" />

        <div className="border-b border-slate-100 pb-1 pt-2">
          <h3 className="text-sm font-semibold text-slate-800">SMTP Server</h3>
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div className="col-span-2">
            <Field label="SMTP Host" value={settings.smtp_host} onChange={v => setSettings(s => ({ ...s, smtp_host: v }))}
              placeholder="mail.example.com" />
          </div>
          <Field label="Port" value={String(settings.smtp_port)} onChange={v => setSettings(s => ({ ...s, smtp_port: parseInt(v) || 465 }))}
            placeholder="465" />
        </div>

        <Field label="SMTP Username" value={settings.smtp_username} onChange={v => setSettings(s => ({ ...s, smtp_username: v }))}
          placeholder="alamsyah@example.com" />

        <div>
          <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-500">SMTP Password</label>
          <div className="relative">
            <input type={showPw ? 'text' : 'password'} value={settings.smtp_password}
              onChange={e => setSettings(s => ({ ...s, smtp_password: e.target.value }))}
              placeholder="Enter SMTP password"
              className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 pr-10 text-sm text-slate-900 placeholder-slate-400 transition-colors focus:border-blue-400 focus:ring-2 focus:ring-blue-100 focus:outline-none" />
            <button onClick={() => setShowPw(!showPw)} type="button"
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
              {showPw ? '🙈' : '👁️'}
            </button>
          </div>
        </div>

        <div className="border-b border-slate-100 pb-1 pt-2">
          <h3 className="text-sm font-semibold text-slate-800">IMAP (Sent folder copy)</h3>
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div className="col-span-2">
            <Field label="IMAP Host" value={settings.imap_host} onChange={v => setSettings(s => ({ ...s, imap_host: v }))}
              placeholder="mail.example.com" hint="Usually same as SMTP host" />
          </div>
          <Field label="Port" value={String(settings.imap_port)} onChange={v => setSettings(s => ({ ...s, imap_port: parseInt(v) || 993 }))}
            placeholder="993" />
        </div>

        <div className="border-b border-slate-100 pb-1 pt-2">
          <h3 className="text-sm font-semibold text-slate-800">Campaign</h3>
        </div>

        <Field label="Daily Send Limit" value={String(settings.daily_limit)} onChange={v => setSettings(s => ({ ...s, daily_limit: parseInt(v) || 10 }))}
          type="number" placeholder="10" hint="Maximum emails sent per day (1-100)" />
      </div>

      <div className="flex items-center justify-end border-t border-slate-100 px-6 py-4">
        <button onClick={handleSave} disabled={saving}
          className="inline-flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-[#0056b3] to-[#003d7a] px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:shadow-md hover:brightness-110 active:scale-[0.97] disabled:opacity-50">
          {saving ? 'Saving...' : 'Save Settings'}
        </button>
      </div>
    </div>
  )
}
