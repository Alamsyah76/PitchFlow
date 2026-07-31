'use client'
import { useState, useEffect } from 'react'
import { Loader2, Check, Eye, EyeOff, Key } from 'lucide-react'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8027'

export default function ApiKeySettings() {
  const [email, setEmail] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [hasKey, setHasKey] = useState(false)
  const [keyPreview, setKeyPreview] = useState('')
  const [showKey, setShowKey] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem('pitchflow_user') || '{}')
    if (user.email) {
      setEmail(user.email)
      checkKeyStatus(user.email)
    } else {
      setChecking(false)
    }
  }, [])

  async function checkKeyStatus(email: string) {
    try {
      const r = await fetch(`${API}/api/profile/get-api-key-status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      })
      const d = await r.json()
      if (d.success) {
        setHasKey(d.data.has_key)
        setKeyPreview(d.data.key_preview)
      }
    } catch {}
    setChecking(false)
  }

  async function handleSave() {
    setMessage(''); setError('')
    if (!apiKey.trim()) { setError('API Key cannot be empty'); return }
    if (!apiKey.trim().startsWith('sk-')) { setError('API Key must start with "sk-"'); return }
    setLoading(true)
    try {
      const r = await fetch(`${API}/api/profile/save-api-key`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, api_key: apiKey.trim() }),
      })
      const d = await r.json()
      if (d.success) {
        setMessage('API Key saved successfully!')
        setHasKey(true)
        setKeyPreview(apiKey.trim().slice(0, 8) + '...' + apiKey.trim().slice(-4))
        setApiKey('')
      } else {
        setError(d.detail || d.message || 'Failed to save')
      }
    } catch { setError('Failed to connect to server') }
    setLoading(false)
  }

  async function handleRemove() {
    setMessage(''); setError('')
    setLoading(true)
    try {
      const r = await fetch(`${API}/api/profile/save-api-key`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, api_key: '' }),
      })
      const d = await r.json()
      if (d.success) {
        setMessage('API Key removed. Global key will be used.')
        setHasKey(false)
        setKeyPreview('')
      }
    } catch { setError('Failed to connect to server') }
    setLoading(false)
  }

  if (checking) return <div className="flex items-center gap-2 text-sm text-slate-500"><Loader2 className="animate-spin" size={16} />Loading...</div>
  if (!email) return <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">Please log in to manage your API Key.</div>

  return (
    <div className="max-w-lg">
      <h2 className="text-lg font-semibold text-slate-900 mb-1">Bring Your Own Key (BYOK)</h2>
      <p className="text-sm text-slate-500 mb-6">
        Use your own OpenAI API Key. Usage will be billed to your OpenAI account.
        {!hasKey && ' Leave empty to use the system global key.'}
      </p>

      {hasKey && (
        <div className="mb-6 rounded-xl border border-emerald-200 bg-emerald-50 p-4">
          <div className="flex items-center gap-2 text-emerald-700 font-medium text-sm mb-1">
            <Key size={16} /> Active API Key
          </div>
          <p className="text-xs text-emerald-600 font-mono">{keyPreview}</p>
        </div>
      )}

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">OpenAI API Key</label>
          <div className="relative">
            <input
              type={showKey ? 'text' : 'password'}
              value={apiKey}
              onChange={e => setApiKey(e.target.value)}
              placeholder={hasKey ? 'Type a new key to replace...' : 'sk-proj-...'}
              className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 pr-10 text-sm font-mono focus:border-[#0056b3] focus:outline-none focus:ring-2 focus:ring-[#0056b3]/20"
            />
            <button
              onClick={() => setShowKey(!showKey)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              {showKey ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
          <p className="mt-1 text-xs text-slate-400">Keys start with <code className="bg-slate-100 px-1 rounded">sk-</code>. Get one at platform.openai.com/api-keys</p>
        </div>

        {error && <div className="rounded-xl bg-red-50 border border-red-200 p-3 text-sm text-red-700">{error}</div>}
        {message && <div className="rounded-xl bg-emerald-50 border border-emerald-200 p-3 text-sm text-emerald-700 flex items-center gap-2"><Check size={16} />{message}</div>}

        <div className="flex gap-3">
          <button
            onClick={handleSave}
            disabled={loading || !apiKey.trim()}
            className="rounded-xl bg-gradient-to-r from-[#0056b3] to-[#003d7a] px-5 py-2.5 text-sm font-medium text-white disabled:opacity-50 hover:brightness-110 flex items-center gap-2"
          >
            {loading ? <Loader2 className="animate-spin" size={16} /> : <Key size={16} />}
            Save API Key
          </button>
          {hasKey && (
            <button
              onClick={handleRemove}
              disabled={loading}
              className="rounded-xl border border-red-300 px-5 py-2.5 text-sm font-medium text-red-600 hover:bg-red-50"
            >
              Remove Key
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
