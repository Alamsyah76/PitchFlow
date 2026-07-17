import type { ReactNode } from 'react'
import HeaderBar from './HeaderBar'
import Sidebar from './Sidebar'
import ChatBot from '../ChatBot'

type AppShellProps = {
  children: ReactNode
  activeRoute?: string
}

export default function AppShell({ children, activeRoute }: AppShellProps) {
  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,#FAFBFF_0%,#F7F8FB_42%,#F5F6FA_100%)] text-slate-950">
      <Sidebar activeRoute={activeRoute} />
      <HeaderBar />
      <main className="px-4 py-6 md:px-8 md:py-8 lg:ml-[260px] xl:px-10">
        <div className="mx-auto max-w-[1440px] pb-28">{children}</div>
      </main>
      <ChatBot />
    </div>
  )
}
