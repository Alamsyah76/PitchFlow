import Link from 'next/link'
import { Banknote, Bookmark, Home, LayoutDashboard, Mail, Settings, Sparkles } from 'lucide-react'

const menuItems = [
  { label: 'Beranda', icon: Home, route: '/' },
  { label: 'Content Studio', icon: Sparkles, route: '/content-studio' },
  { label: 'Email Campaign', icon: Mail, route: '/email-campaign' },
  { label: 'Dashboard', icon: LayoutDashboard, route: '/dashboard' },
  { label: 'Library', icon: Bookmark, route: '/library' },
  { label: 'Pricing', icon: Banknote, route: '/pricing' },
  { label: 'Settings', icon: Settings, route: '/settings' },
]

type StudioSidebarProps = {
  activeRoute?: string
}

export default function StudioSidebar({ activeRoute = '/content-studio' }: StudioSidebarProps) {
  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-[260px] flex-col border-r border-slate-200/80 bg-white/95 px-4 py-5 shadow-[12px_0_36px_rgba(15,23,42,0.03)] lg:flex">
      <div className="flex h-12 items-center gap-3 px-2">
        <img src="/pitchflow.png" alt="PitchFlow" className="h-9 w-auto" />
        <div className="flex flex-col">
          <div className="text-lg font-semibold tracking-normal text-slate-950 leading-none">PitchFlow</div>
          <div className="text-[9px] font-medium text-slate-400 tracking-wide leading-none mt-0.5">Content Generation Platform</div>
        </div>
      </div>

      <nav className="mt-9 space-y-1.5">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = activeRoute === item.route
          const activeClass = isActive
            ? 'bg-gradient-to-r from-[#0056b3] to-[#003d7a] text-white shadow-[0_6px_16px_rgba(0,86,179,0.30)]'
            : 'text-slate-600 hover:bg-slate-100 hover:text-slate-950'

          return (
            <Link
              key={item.route}
              href={item.route}
              className={`flex h-11 items-center gap-3 rounded-2xl px-3 text-sm font-medium transition-colors ${activeClass}`}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
