import AppShell from '../components/app-shell/AppShell'

export default function SavedRoute() {
  return (
    <AppShell activeRoute="/saved">
      <main className="flex min-h-[360px] items-center justify-center text-center">
        <p className="text-base font-medium text-slate-600">This premium feature is under development.</p>
      </main>
    </AppShell>
  )
}
