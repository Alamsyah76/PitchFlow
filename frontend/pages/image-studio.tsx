import AppShell from '../components/app-shell/AppShell'
import ComingSoon from '../components/ComingSoon'

export default function ImageStudioRoute() {
  return (
    <AppShell activeRoute="/image-studio">
      <ComingSoon
        icon="🖼️"
        title="Image Studio"
        description="Generate branded visuals directly from your content — scene, title, and key points rendered automatically. Standalone image workflows coming soon."
      />
    </AppShell>
  )
}
