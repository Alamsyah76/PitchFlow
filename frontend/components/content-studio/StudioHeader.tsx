import { useEffect, useState, useRef } from 'react'
import { useRouter } from 'next/router'

type StudioHeaderProps = {
  title?: string
}

type UserData = {
  email: string
  name: string
  role?: string
  avatar?: string
}

const API = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8027'

export default function StudioHeader({ title = 'Content Studio' }: StudioHeaderProps) {
  const [user, setUser] = useState<UserData | null>(null)
  const [menuOpen, setMenuOpen] = useState(false)
  const [devMode, setDevMode] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)
  const router = useRouter()

  useEffect(() => {
    try {
      const raw = localStorage.getItem('pitchflow_user')
      if (raw) setUser(JSON.parse(raw))
    } catch {}
    setDevMode(localStorage.getItem('pitchflow_dev') === 'true')
  }, [])

  // Close menu on click outside
  useEffect(() => {
    if (!menuOpen) return
    const handler = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node))
        setMenuOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [menuOpen])

  // Hide menu on route change
  useEffect(() => {
    setMenuOpen(false)
  }, [router.asPath])

  const initials = user?.name
    ? user.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()
    : devMode ? 'DV' : '?'

  const displayName = user?.name || (devMode ? 'Developer' : 'Guest')
  const avatarUrl = user?.avatar

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-slate-200/70 bg-white/82 px-4 backdrop-blur-xl md:px-8 lg:ml-[260px] xl:px-10">
      <div className="flex min-w-0 items-center gap-2">
        <div className="min-w-0">
          <h1 className="truncate text-lg font-semibold tracking-normal text-slate-950 md:text-xl">{title}</h1>
          <p className="hidden truncate text-sm leading-5 text-slate-500 sm:block">
            AI-powered document marketing workspace
          </p>
        </div>
      </div>

      <div className="relative" ref={menuRef}>
        <button onClick={() => setMenuOpen(!menuOpen)}
          className="flex items-center gap-2 rounded-xl px-2 py-1.5 hover:bg-slate-100 transition-colors">
          <div className="hidden text-right md:block">
            <div className="text-sm font-medium text-slate-900">{displayName}</div>
            <div className="text-[10px] text-slate-400">{user?.email || (devMode ? 'Developer Mode' : 'Belum login')}</div>
          </div>
          <div className="flex h-9 w-9 items-center justify-center rounded-2xl bg-gradient-to-br from-[#0056b3] to-[#003d7a] text-sm font-semibold text-white shadow-sm overflow-hidden">
            {avatarUrl ? (
              <img src={avatarUrl.startsWith('data:') ? avatarUrl : `data:image/png;base64,${avatarUrl}`} alt="" className="h-full w-full object-cover" />
            ) : (
              initials
            )}
          </div>
        </button>

        {menuOpen && (
          <div className="absolute right-0 top-full mt-2 w-56 rounded-2xl border border-slate-200/70 bg-white p-2 shadow-xl ring-1 ring-slate-900/5">
            {user && (
              <div className="px-3 py-2 border-b border-slate-100 mb-1">
                <div className="text-sm font-semibold text-slate-900">{user.name}</div>
                <div className="text-xs text-slate-400">{user.email}</div>
              </div>
            )}
            <button onClick={() => {
              localStorage.removeItem('pitchflow_user')
              localStorage.removeItem('pitchflow_dev')
              setUser(null)
              router.push('/auth')
            }}
              className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
              Logout
            </button>
          </div>
        )}
      </div>
    </header>
  )
}
