import StudioSidebar from '../components/content-studio/StudioSidebar'
import StudioHeader from '../components/content-studio/StudioHeader'

export default function TemplatesRoute() {
  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,#FAFBFF_0%,#F7F8FB_42%,#F5F6FA_100%)] text-slate-950">
      <StudioSidebar activeRoute="/templates" />
      <StudioHeader title="Templates" />
      <main className="px-4 py-4 md:px-8 md:py-6 lg:ml-[260px] xl:px-10">
        <div className="mx-auto flex min-h-[360px] max-w-screen-2xl items-center justify-center pb-28 text-center">
          <p className="text-base font-medium text-slate-600">
            Templates feature coming soon in Phase 2.
          </p>
        </div>
      </main>
    </div>
  )
}
