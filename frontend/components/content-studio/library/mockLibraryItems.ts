export interface LibraryItem {
  id: string
  pdf_filename: string
  selected_topic: string
  caption_text: string
  hashtags: string[]
  image_url: string | null
  timestamp: string
}

export const mockLibraryItems: LibraryItem[] = [
  {
    id: 'lib-001',
    pdf_filename: 'Q4_Supply_Chain_Optimization_Report.pdf',
    selected_topic: 'Reducing logistics friction through predictive analytics',
    caption_text:
      'Supply chain disruptions cost businesses millions every quarter. Our latest analysis of 200+ logistics networks reveals that predictive analytics can reduce delivery delays by up to 38% and cut inventory holding costs by 22%. The key? Real-time demand sensing paired with dynamic rerouting algorithms. Leaders who invest in this stack today will own the efficiency advantage tomorrow.',
    hashtags: ['#SupplyChain', '#PredictiveAnalytics', '#Logistics', '#DigitalTransformation', '#Efficiency'],
    image_url: null,
    timestamp: '2026-06-18T09:30:00Z',
  },
  {
    id: 'lib-002',
    pdf_filename: 'SaaS_GoToMarket_Playbook_2026.pdf',
    selected_topic: 'Zero-touch onboarding as a growth lever',
    caption_text:
      'The fastest-growing B2B SaaS companies share one trait: a zero-touch onboarding flow that converts free users in under 4 minutes. We analyzed 14 PLG leaders and found that reducing time-to-value by 30% correlates with a 2.4x increase in paid conversion. This playbook breaks down the exact trigger sequences, in-app guidance patterns, and friction audits that make self-serve work at scale.',
    hashtags: ['#SaaS', '#PLG', '#Onboarding', '#GrowthStrategy', '#B2B'],
    image_url: 'https://images.unsplash.com/photo-1553877522-43269d4ea984?w=600&q=80',
    timestamp: '2026-06-17T14:15:00Z',
  },
  {
    id: 'lib-003',
    pdf_filename: 'Cybersecurity_Threat_Landscape_2026_H1.pdf',
    selected_topic: 'Zero-trust architecture adoption in mid-market enterprises',
    caption_text:
      'Mid-market enterprises are accelerating zero-trust adoption at 3x the rate of large enterprises. Our survey of 600 IT decision-makers found that 67% of mid-market firms now have a zero-trust roadmap, driven by compliance mandates and ransomware insurance requirements. The most common starting point? Identity-aware microsegmentation for critical workloads.',
    hashtags: ['#Cybersecurity', '#ZeroTrust', '#MidMarket', '#Compliance', '#Ransomware'],
    image_url: null,
    timestamp: '2026-06-16T11:00:00Z',
  },
  {
    id: 'lib-004',
    pdf_filename: 'APAC_Cloud_Migration_Benchmark.pdf',
    selected_topic: 'Multi-cloud cost governance in ASEAN enterprises',
    caption_text:
      'ASEAN enterprises running multi-cloud environments waste an average of 34% of their cloud spend on orphaned resources and over-provisioned instances. This benchmark report across 85 organisations identifies the top three FinOps practices that close the gap: real-time cost anomaly detection, committed-use discount orchestration, and team-level chargeback visibility.',
    hashtags: ['#CloudMigration', '#FinOps', '#ASEAN', '#MultiCloud', '#CostGovernance'],
    image_url: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&q=80',
    timestamp: '2026-06-15T08:45:00Z',
  },
]
