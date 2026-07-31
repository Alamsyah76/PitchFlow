import AppShell from '../components/app-shell/AppShell'
import ComingSoon from '../components/ComingSoon'

export default function HistoryRoute() {
  return (
    <AppShell activeRoute="/history">
      <ComingSoon
        icon="🕘"
        title="Campaign History"
        description="A complete timeline of your email campaigns, sends, opens, and clicks — all in one place. Full audit trail coming soon."
      />
    </AppShell>
  )
}
