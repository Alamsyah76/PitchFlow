import AppShell from '../components/app-shell/AppShell'
import ComingSoon from '../components/ComingSoon'

export default function SavedRoute() {
  return (
    <AppShell activeRoute="/saved">
      <ComingSoon
        icon="🔖"
        title="Saved Content"
        description="Your bookmarked captions, images, and campaign drafts will live here. Quickly revisit any content you've created without re-generating."
      />
    </AppShell>
  )
}
