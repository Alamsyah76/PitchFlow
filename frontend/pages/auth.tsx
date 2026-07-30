'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { enableDevMode } from '../lib/auth-check'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8027'

type Step = 'register' | 'otp' | 'welcome' | 'admin'

export default function AuthPage() {
  const [tab, setTab] = useState<'register' | 'login' | 'admin'>('register')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [code, setCode] = useState('')
  const [step, setStep] = useState<Step>('register')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [user, setUser] = useState<{ email: string; name: string } | null>(null)
  const router = useRouter()

  // Auto bypass development mode
  useEffect(() => {
    if (router.query.dev === '1') {
      enableDevMode()
      router.push('/content-studio')
    }
  }, [router.query])

  function reset() {
    setMessage(''); setError(''); setLoading(false)
  }

  async function handleRegister() {
    reset()
    if (!name.trim() || !email.trim()) { setError('Nama dan email wajib diisi.'); return }
    setLoading(true)
    try {
      const r = await fetch(`${API}/api/auth/register`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name.trim(), email: email.trim() })
      })
      const d = await r.json()
      if (d.success) { setMessage('Kode OTP sudah dikirim ke email kamu.'); setStep('otp') }
      else setError(d.detail || d.message || 'Gagal daftar.')
    } catch { setError('Gagal terhubung ke server.') }
    setLoading(false)
  }

  async function handleRequestOtp() {
    reset()
    if (!email.trim()) { setError('Email wajib diisi.'); return }
    setLoading(true)
    try {
      const r = await fetch(`${API}/api/auth/request-otp`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim() })
      })
      const d = await r.json()
      if (d.success) { setMessage('Kode OTP sudah dikirim ke email kamu.'); setStep('otp') }
      else setError(d.detail || d.message || 'Email tidak terdaftar.')
    } catch { setError('Gagal terhubung ke server.') }
    setLoading(false)
  }

  async function handleVerifyOtp() {
    reset()
    if (!code.trim()) { setError('Kode OTP wajib diisi.'); return }
    setLoading(true)
    try {
      const r = await fetch(`${API}/api/auth/verify-otp`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim().toLowerCase(), code: code.trim() })
      })
      const d = await r.json()
      if (d.success) {
        setUser({ email: d.data.email, name: d.data.name })
        setStep('welcome')
        localStorage.setItem('pitchflow_user', JSON.stringify(d.data))
        if (d.data.token) localStorage.setItem('access_token', d.data.token)
      } else setError(d.detail || d.message || 'Kode OTP salah.')
    } catch { setError('Gagal terhubung ke server.') }
    setLoading(false)
  }

  async function handleAdminLogin() {
    reset()
    if (!email.trim() || !password.trim()) { setError('Email dan password wajib diisi.'); return }
    setLoading(true)
    try {
      const r = await fetch(`${API}/api/auth/admin-login`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), password })
      })
      const d = await r.json()
      if (d.success) {
        setUser({ email: d.data.email, name: d.data.name })
        setStep('welcome')
        localStorage.setItem('pitchflow_user', JSON.stringify(d.data))
        localStorage.setItem('pitchflow_admin', 'true')
        if (d.data.token) localStorage.setItem('access_token', d.data.token)
      } else setError(d.detail || d.message || 'Login gagal.')
    } catch { setError('Gagal terhubung ke server.') }
    setLoading(false)
  }

  // Welcome screen
  if (step === 'welcome' && user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
        <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-xl">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-r from-[#0056b3] to-[#003d7a] text-2xl">🎉</div>
          <h2 className="mt-4 text-xl font-bold">Selamat Datang, {user.name}!</h2>
          <p className="mt-2 text-sm text-slate-500">{user.email}</p>
          <p className="mt-1 text-xs text-slate-400">Login berhasil</p>
          <div className="mt-6 flex flex-col gap-3">
            <Link href="/content-studio" className="rounded-xl bg-gradient-to-r from-[#0056b3] to-[#003d7a] px-5 py-3 text-sm font-semibold text-white text-center hover:brightness-110">
              Masuk ke Content Studio
            </Link>
            <Link href="/" className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-medium text-slate-600 text-center hover:bg-slate-50">
              Ke Landing Page
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-6 shadow-xl">
        {/* Logo */}
        <div className="flex flex-col items-center">
          <img src="/pitchflow.png" alt="PitchFlow" className="h-12 w-auto" />
          <h1 className="mt-2 text-lg font-bold">PitchFlow</h1>
          <p className="text-xs text-slate-400">Content Generation Platform</p>
        </div>

        {/* Tabs */}
        {step !== 'otp' && (
          <div className="mt-6 flex gap-1 rounded-xl bg-slate-100 p-1">
            <button onClick={() => { setTab('register'); reset() }}
              className={`flex-1 rounded-lg py-2 text-sm font-medium transition-all ${tab === 'register' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500'}`}>Daftar</button>
            <button onClick={() => { setTab('login'); reset() }}
              className={`flex-1 rounded-lg py-2 text-sm font-medium transition-all ${tab === 'login' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500'}`}>Login</button>
          </div>
        )}

        {/* Error / Message */}
        {error && <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>}
        {message && <div className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm text-emerald-700">{message}</div>}

        {/* OTP Step */}
        {step === 'otp' ? (
          <div className="mt-6 space-y-4">
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-500">Kode OTP</label>
              <input value={code} onChange={e => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="Masukkan 6 digit kode"
                className="w-full rounded-xl border border-slate-300 px-4 py-3 text-center text-2xl tracking-[0.5em] font-bold outline-none focus:border-blue-400"
                maxLength={6} />
            </div>
            <button onClick={handleVerifyOtp} disabled={loading || code.length !== 6}
              className="w-full rounded-xl bg-gradient-to-r from-[#0056b3] to-[#003d7a] py-3 text-sm font-semibold text-white hover:brightness-110 disabled:opacity-50">
              {loading ? '⏳ Memverifikasi...' : 'Verifikasi'}
            </button>
            <button onClick={() => { setStep(tab === 'admin' ? 'admin' : 'register'); setCode(''); setMessage('') }}
              className="w-full text-center text-xs text-slate-400 hover:text-slate-600">← Kembali</button>
          </div>
        ) : tab === 'register' ? (
          /* Register Form */
          <div className="mt-6 space-y-4">
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-500">Nama</label>
              <input value={name} onChange={e => setName(e.target.value)}
                className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-blue-400" placeholder="Nama lengkap" />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-500">Email</label>
              <input value={email} onChange={e => setEmail(e.target.value)}
                className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-blue-400" placeholder="email@perusahaan.com" />
            </div>
            <button onClick={handleRegister} disabled={loading}
              className="w-full rounded-xl bg-gradient-to-r from-[#0056b3] to-[#003d7a] py-3 text-sm font-semibold text-white hover:brightness-110 disabled:opacity-50">
              {loading ? '⏳ Mendaftar...' : 'Daftar'}
            </button>
          </div>
        ) : tab === 'login' ? (
          /* Login Form */
          <div className="mt-6 space-y-4">
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-500">Email</label>
              <input value={email} onChange={e => setEmail(e.target.value)}
                className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-blue-400" placeholder="email@perusahaan.com" />
            </div>
            <button onClick={handleRequestOtp} disabled={loading}
              className="w-full rounded-xl bg-gradient-to-r from-[#0056b3] to-[#003d7a] py-3 text-sm font-semibold text-white hover:brightness-110 disabled:opacity-50">
              {loading ? '⏳ Mengirim...' : 'Kirim Kode OTP'}
            </button>
            <div className="relative">
              <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-slate-200" /></div>
              <div className="relative flex justify-center"><span className="bg-white px-3 text-xs text-slate-400">atau</span></div>
            </div>
            <button onClick={() => { setTab('admin'); reset(); setPassword('') }}
              className="w-full rounded-xl border border-slate-300 py-3 text-sm font-medium text-slate-600 hover:bg-slate-50">
              Login Admin
            </button>
          </div>
        ) : (
          /* Admin Login */
          <div className="mt-6 space-y-4">
            <div className="rounded-lg bg-amber-50 border border-amber-200 px-4 py-2 text-xs text-amber-700">🔐 Login sebagai Administrator</div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-500">Email Admin</label>
              <input value={email} onChange={e => setEmail(e.target.value)}
                className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-blue-400" placeholder="admin@pitchflow.com" />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-500">Password</label>
              <input type="password" value={password} onChange={e => setPassword(e.target.value)}
                className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-blue-400" placeholder="••••••••" />
            </div>
            <button onClick={handleAdminLogin} disabled={loading}
              className="w-full rounded-xl bg-gradient-to-r from-[#0056b3] to-[#003d7a] py-3 text-sm font-semibold text-white hover:brightness-110 disabled:opacity-50">
              {loading ? '⏳ Login...' : 'Login Admin'}
            </button>
            <button onClick={() => { setTab('login'); reset() }}
              className="w-full text-center text-xs text-slate-400 hover:text-slate-600">← Kembali ke Login</button>
          </div>
        )}
+
+        {/* Dev mode bypass */}
+        <div className="mt-6 text-center">
+          <Link href="/auth?dev=1" className="text-xs text-slate-300 hover:text-slate-400">
+            Developer Mode (skip login)
+          </Link>
+        </div>
       </div>
     </div>
   )
}
