import AppShell from '../components/app-shell/AppShell'

export default function ImageStudioRoute() {
  return (
    <AppShell activeRoute="/image-studio">
      <main className="flex min-h-[360px] items-center justify-center text-center">
        <p className="text-base font-medium text-slate-600">Fitur Premium ini sedang dalam pengembangan.</p>
      </main>
    </AppShell>
  )
}
