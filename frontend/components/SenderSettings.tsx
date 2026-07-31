'use client'

import { useEffect, useState } from 'react'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8027'

export default function SenderSettings() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [company, setCompany] = useState('')
  const [logoPreview, setLogoPreview] = useState('')
  const [logoB64, setLogoB64] = useState('')
  const [saved, setSaved] = useState(false)
  const [loading, setLoading] = useState(true)

  // Profile / Avatar
  const [avatarPreview, setAvatarPreview] = useState('')
  const [avatarB64, setAvatarB64] = useState('')
  const [userEmail, setUserEmail] = useState('')
  const [profileSaved, setProfileSaved] = useState(false)

  useEffect(() => {
    // Load sender settings
    fetch(`${API}/api/email-campaign/sender-settings`)
      .then(r => r.json())
      .then(d => {
        if (d.success) {
          setName(d.data.name || '')
          setEmail(d.data.email || '')
          setCompany(d.data.company || '')
          setLogoPreview(d.data.logo_b64 || '')
          setLogoB64(d.data.logo_b64 || '')
        }
      })
    
    // Load profile / avatar
    try {
      const raw = localStorage.getItem('pitchflow_user')
      if (raw) {
        const u = JSON.parse(raw)
        setUserEmail(u.email || '')
        setAvatarPreview(u.avatar || '')
        setAvatarB64(u.avatar || '')
      }
    } catch {}
    
    setLoading(false)
  }, [])

  async function handleSave() {
    setSaved(false)
    setProfileSaved(false)
    try {
      const r = await fetch(`${API}/api/email-campaign/sender-settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, company, logo_b64: logoB64 })
      })
      const d = await r.json()
      if (d.success) setSaved(true)
    } catch {}
  }

  function handleLogo(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      const b64 = reader.result as string
      setLogoPreview(b64)
      setLogoB64(b64.split(',')[1] || b64)
    }
    reader.readAsDataURL(file)
  }

  function handleAvatar(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      const b64 = reader.result as string
      setAvatarPreview(b64)
      setAvatarB64(b64.split(',')[1] || b64)
    }
    reader.readAsDataURL(file)
  }

  async function saveProfile() {
    setProfileSaved(false)
    if (!userEmail) return
    try {
      const r = await fetch(`${API}/api/profile/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: userEmail, avatar: avatarB64 })
      })
      const d = await r.json()
      if (d.success) {
        // Also update localStorage
        try {
          const raw = localStorage.getItem('pitchflow_user')
          if (raw) {
            const u = JSON.parse(raw)
            u.avatar = avatarB64
            localStorage.setItem('pitchflow_user', JSON.stringify(u))
          }
        } catch {}
        setProfileSaved(true)
      }
    } catch {}
  }

  if (loading) return <div className="rounded-xl border border-slate-200/70 bg-white p-6 shadow-sm text-sm text-slate-500">Loading...</div>

  return (
    <div className="rounded-xl border border-slate-200/70 bg-white shadow-sm">
      <div className="border-b border-slate-100 px-5 py-3.5">
        <h3 className="text-sm font-semibold text-slate-800">⚙️ Sender Settings</h3>
      </div>
      <div className="space-y-5 p-5">
        {/* Logo */}
        <div>
          <label className="mb-1.5 block text-xs font-medium text-slate-500">Company Logo</label>
          <div className="flex items-center gap-4">
            <div className="flex h-16 w-36 items-center justify-center rounded-xl border border-dashed border-slate-300 bg-slate-50 overflow-hidden">
              {logoPreview ? (
                <img src={logoPreview.startsWith('data:') ? logoPreview : `data:image/png;base64,${logoPreview}`} alt="Logo" className="h-full w-full object-contain p-2" />
              ) : (
                <span className="text-[10px] text-slate-400">No logo yet</span>
              )}
            </div>
            <label className="cursor-pointer rounded-lg border border-blue-200 bg-white px-4 py-2 text-xs font-medium text-blue-600 hover:bg-blue-50">
              Choose File
              <input type="file" accept="image/*" onChange={handleLogo} className="hidden" />
            </label>
            {logoPreview && (
              <button onClick={() => { setLogoPreview(''); setLogoB64('') }}
                className="text-xs text-red-500 hover:text-red-700">Remove</button>
            )}
          </div>
          <p className="mt-1 text-[10px] text-slate-400">Format: PNG/JPG. Size: max 300x100px</p>
        </div>

        {/* Profile Photo */}
        <div className="border-t border-slate-100 pt-5">
          <h4 className="mb-3 text-sm font-semibold text-slate-700">📷 Profile Photo</h4>
          <div className="flex items-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full border border-dashed border-slate-300 bg-slate-50 overflow-hidden">
              {avatarPreview ? (
                <img src={avatarPreview.startsWith('data:') ? avatarPreview : `data:image/png;base64,${avatarPreview}`} alt="Avatar" className="h-full w-full object-cover" />
              ) : (
                <span className="text-2xl font-semibold text-slate-400">{'?'}</span>
              )}
            </div>
            <label className="cursor-pointer rounded-lg border border-blue-200 bg-white px-4 py-2 text-xs font-medium text-blue-600 hover:bg-blue-50">
              Choose Photo
              <input type="file" accept="image/*" onChange={handleAvatar} className="hidden" />
            </label>
            {avatarPreview && (
              <button onClick={() => { setAvatarPreview(''); setAvatarB64('') }}
                className="text-xs text-red-500 hover:text-red-700">Remove</button>
            )}
            {userEmail && (
              <button onClick={saveProfile}
                className="rounded-lg bg-gradient-to-r from-[#0056b3] to-[#003d7a] px-4 py-2 text-xs font-semibold text-white hover:brightness-110">
                Save Photo
              </button>
            )}
            {profileSaved && <span className="text-xs text-emerald-600">✅ Saved</span>}
          </div>
          <p className="mt-1 text-[10px] text-slate-400">Photo will appear in the top-right corner after refresh.</p>
        </div>

        {/* Name */}
        <div>
          <label className="mb-1 block text-xs font-medium text-slate-500">Sender Name</label>
          <input value={name} onChange={e => setName(e.target.value)}
            className="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-sm outline-none focus:border-blue-400"
            placeholder="e.g. John Doe" />
        </div>

        {/* Email */}
        <div>
          <label className="mb-1 block text-xs font-medium text-slate-500">Sender Email</label>
          <input value={email} onChange={e => setEmail(e.target.value)}
            className="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-sm outline-none focus:border-blue-400"
            placeholder="email@company.com" />
        </div>

        {/* Company */}
        <div>
          <label className="mb-1 block text-xs font-medium text-slate-500">Company Name</label>
          <input value={company} onChange={e => setCompany(e.target.value)}
            className="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-sm outline-none focus:border-blue-400"
            placeholder="e.g. PitchFlow" />
        </div>

        {/* Save */}
        <button onClick={handleSave}
          className="rounded-xl bg-gradient-to-r from-[#0056b3] to-[#003d7a] px-6 py-2.5 text-sm font-semibold text-white hover:brightness-110">
          Save Settings
        </button>
        {saved && <span className="ml-3 text-sm text-emerald-600">✅ Saved</span>}
      </div>
    </div>
  )
}
