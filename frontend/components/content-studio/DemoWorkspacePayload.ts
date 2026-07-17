import type { VisualStoryBrief } from '../../lib/content-types'

export interface DemoWorkspace {
  pdf_filename: string
  topics: { id: string; title: string }[]
  selected_topic: string
  caption_text: string
  hashtags: string[]
  creative_direction: VisualStoryBrief
  image_url: null
}

export const demoWorkspace: DemoWorkspace = {
  pdf_filename: 'Enterprise Cloud Transformation Strategy.pdf',
  topics: [
    { id: 'demo-1', title: 'Building multi-cloud governance for enterprise resilience' },
    { id: 'demo-2', title: 'Improving operational visibility across distributed infrastructure' },
    { id: 'demo-3', title: 'Aligning cloud investment with business continuity goals' },
  ],
  selected_topic: 'Building multi-cloud governance for enterprise resilience',
  caption_text:
    'Enterprise cloud transformation is no longer only about migration speed. The more important question is whether teams can govern cost, visibility, and operational risk across distributed environments. A strong multi-cloud strategy gives leaders the ability to scale infrastructure while keeping accountability, resilience, and business continuity in focus.',
  hashtags: ['#CloudStrategy', '#DigitalTransformation', '#EnterpriseIT', '#BusinessContinuity', '#OperationalResilience'],
  creative_direction: {
    core_visual_message:
      'A unified command center showing distributed cloud environments connected through governance, visibility, and resilience layers.',
    visual_headline: 'From Cloud Expansion to Cloud Control',
    scene_concept:
      'A modern enterprise operations room with abstract cloud nodes, governance lines, and resilience indicators across multiple regions.',
    main_subject: 'Abstract enterprise cloud infrastructure command center',
    supporting_elements: [
      'Multiple cloud region nodes',
      'Governance connection lines',
      'Resilience indicator layers',
      'Clean data flow visualizations',
    ],
    visual_metaphor: 'A command center as a central nervous system connecting distributed cloud environments',
    mood_tone: 'Premium, confident, corporate, forward-looking',
    linkedin_image_prompt:
      'Create a premium B2B LinkedIn visual showing an enterprise command center overseeing multiple cloud environments through governance, visibility, and resilience layers. Use a clean corporate aesthetic, abstract infrastructure elements, and no readable text.',
    negative_constraints: [
      'No human faces, no brand logos, no fictional data charts, no cluttered dashboards, no exaggerated cyber visuals.',
    ],
    carousel_readiness_notes: 'Single-image format suitable for LinkedIn carousel cover slide.',
  },
  image_url: null,
}
