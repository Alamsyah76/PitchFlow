import Link from 'next/link'
import {
  Bookmark,
  FileText,
  History,
  Home,
  Image,
  LayoutDashboard,
  Mail,
  Settings,
  Sparkles
} from 'lucide-react'
import { Button } from '../ui/button'
import { Card } from '../ui/card'
import { cn } from '../../lib/utils'
import { uiConfig } from '../../data/ui-config'

const iconMap = {
  bookmark: Bookmark,
  'file-text': FileText,
  history: History,
  home: Home,
  image: Image,
  mail: Mail,
  'layout-dashboard': LayoutDashboard,
  settings: Settings,
  sparkles: Sparkles
}

type SidebarProps = {
  activeRoute?: string
}

export default function Sidebar({ activeRoute = '/content-studio' }: SidebarProps) {
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
        {uiConfig.sidebar.menu.map((item) => {
          const Icon = iconMap[item.icon as keyof typeof iconMap]
          const isActive = activeRoute === item.route

          return (
            <Link
              key={item.route}
              href={item.route}
              className={cn(
                'flex h-11 items-center gap-3 rounded-2xl px-3 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-gradient-to-r from-[#0056b3] to-[#003d7a] text-white shadow-[0_6px_16px_rgba(0,86,179,0.30)]'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-950'
              )}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>

      <Card className="mt-auto overflow-hidden border-0 bg-gradient-to-br from-slate-950 via-[#181A33] to-[#4C3FD8] p-4 text-white shadow-[0_18px_44px_rgba(15,23,42,0.18)]">
        <div className="text-sm font-semibold">{uiConfig.sidebar.upgradeCard.title}</div>
        <p className="mt-2 text-xs leading-5 text-white/75">{uiConfig.sidebar.upgradeCard.description}</p>
        <Button className="mt-4 w-full bg-white text-slate-950 hover:bg-slate-100" variant="secondary" size="sm">
          {uiConfig.sidebar.upgradeCard.button}
        </Button>
      </Card>
    </aside>
  )
}
