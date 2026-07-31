export const uiConfig = {
  app: {
    name: 'PitchFlow',
    description: 'Generate engaging content from your documents in seconds.'
  },
  sidebar: {
    logo: {
      icon: 'hexagon',
      text: 'PitchFlow'
    },
    menu: [
      { label: 'Beranda', icon: 'home', route: '/' },
      { label: 'Dashboard', icon: 'layout-dashboard', route: '/dashboard' },
      { label: 'Content Studio', icon: 'sparkles', route: '/content-studio', active: true },
      { label: 'Email Campaign', icon: 'mail', route: '/email-campaign' },
      { label: 'History', icon: 'history', route: '/history' },
      { label: 'Saved', icon: 'bookmark', route: '/saved' },
      { label: 'Settings', icon: 'settings', route: '/settings' }
    ],
    recentGenerations: [
      { title: 'Marketing Strategy.pdf', type: 'AI Generated Post', time: '2 minutes ago' },
      { title: 'Digital Transformation.pdf', type: 'LinkedIn Post', time: '1 hour ago' },
      { title: 'Productivity Tips.pdf', type: 'Instagram Caption', time: '3 hours ago' }
    ],
    upgradeCard: {
      title: 'Unlock More Power',
      description: 'Upgrade to Pro for unlimited generations and advanced features.',
      button: 'Upgrade Now'
    }
  },
  header: {
    title: 'PitchFlow',
    subtitle: 'Content Generation Platform',
    credits: {
      value: 1250,
      label: 'Credits'
    },
    user: {
      name: 'John Doe'
    }
  },
  workflowStepper: {
    steps: [
      { id: 1, title: 'Upload PDF', status: 'active' },
      { id: 2, title: 'Generate Topics' },
      { id: 3, title: 'Select Topic' },
      { id: 4, title: 'Generate Caption' },
      { id: 5, title: 'Generate Image' }
    ]
  }
} as const
