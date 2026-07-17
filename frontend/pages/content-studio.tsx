import StudioSidebar from '../components/content-studio/StudioSidebar'
import StudioHeader from '../components/content-studio/StudioHeader'
import ContentStudioPage from '../components/content-studio/ContentStudioPage'
import ChatBot from '../components/ChatBot'
import UsageBadge from '../components/UsageBadge'

export default function ContentStudioRoute() {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.10),transparent_28%),radial-gradient(circle_at_top_right,rgba(14,165,233,0.08),transparent_24%),linear-gradient(180deg,#F8FAFF_0%,#F6F8FC_45%,#F4F6FA_100%)] text-slate-950">
      <StudioSidebar activeRoute="/content-studio" />
      <StudioHeader />
      <main className="px-4 py-4 md:px-8 md:py-6 lg:ml-[260px] xl:px-10">
        <ContentStudioPage />
      </main>
      <ChatBot />
      <UsageBadge />
    </div>
  )
}
