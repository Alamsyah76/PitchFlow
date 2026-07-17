import { Bell, Menu, Search } from 'lucide-react'
import { Button } from '../ui/button'
import { uiConfig } from '../../data/ui-config'

export default function HeaderBar() {
  return (
    <header className="sticky top-0 z-20 flex h-20 items-center justify-between border-b border-slate-200/70 bg-white/82 px-4 backdrop-blur-xl md:px-8 lg:ml-[260px] xl:px-10">
      <div className="flex min-w-0 items-center gap-3">
        <Button className="lg:hidden" variant="ghost" size="icon" aria-label="Open navigation">
          <Menu size={20} />
        </Button>
        <div className="min-w-0">
          <h1 className="truncate text-xl font-semibold tracking-normal text-slate-950 md:text-[1.625rem]">{uiConfig.header.title}</h1>
          <p className="mt-1 hidden truncate text-sm leading-6 text-slate-500 sm:block">{uiConfig.header.subtitle}</p>
        </div>
      </div>

      <div className="flex items-center gap-2 md:gap-3">
        <div className="hidden h-11 items-center gap-2 rounded-2xl border border-slate-200/80 bg-white px-4 text-sm text-slate-400 shadow-[0_8px_20px_rgba(15,23,42,0.04)] xl:flex">
          <Search size={16} />
          <span>Search content</span>
        </div>

        <div className="hidden rounded-2xl border border-slate-200/80 bg-white px-3.5 py-2.5 text-sm font-medium text-slate-700 shadow-[0_8px_20px_rgba(15,23,42,0.04)] sm:block">
          {uiConfig.header.credits.value.toLocaleString()} <span className="text-slate-400">{uiConfig.header.credits.label}</span>
        </div>

        <Button variant="outline" size="icon" aria-label="Notifications">
          <Bell size={18} />
        </Button>

        <div className="flex items-center gap-3">
          <div className="hidden text-right md:block">
            <div className="text-sm font-medium text-slate-900">{uiConfig.header.user.name}</div>
            <div className="text-xs text-slate-500">Creator</div>
          </div>
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-[#5F54F2] to-[#8B5CF6] text-sm font-semibold text-white shadow-[0_12px_28px_rgba(109,93,252,0.22)]">
            JD
          </div>
        </div>
      </div>
    </header>
  )
}
