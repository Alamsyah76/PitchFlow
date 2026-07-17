export interface FailedProposition {
  sentence: string
  reason: string
}

export interface UploadPdfResponse {
  success?: boolean
  message?: string
  data?: { document_id?: string; id?: string; file_name?: string; filename?: string; error_message?: string; pages?: number; total_pages?: number; total_chunks?: number; total_modules?: number; is_cached?: boolean }
  document_id?: string
  id?: string
  filename?: string
  file_name?: string
  pages?: number
  total_pages?: number
  is_cached?: boolean
  total_chunks?: number
  total_modules?: number
  processing_time_seconds?: number
  detail?: ApiErrorDetail | string
  error_message?: string
}

export interface TopicsResponse {
  success?: boolean
  message?: string
  document_id?: string
  topics?: Array<string | {
    id?: string | number
    topic_id?: string
    title?: string
    text?: string
    score?: number
    potential?: string
    audience?: string
    business_angle?: string
    document_terms?: string[]
    evidence_chunks?: string[]
    approved?: boolean
  }>
  detail?: ApiErrorDetail | string
  error_message?: string
}

export interface GenerateCaptionRequest {
  document_id: string
  selected_topic: string
  topic: string | TopicCardItem
  target_audience?: string
  target_lang: string
  language: string
  topic_id?: string
  business_angle?: string
}

export interface ContextPayloadChunk {
  rank: number
  chunk_id: string
  document_id: string
  module_chunk_id?: number | null
  content: string
  similarity_score?: number
  rerank_score?: number
  metadata?: Record<string, unknown>
}

export interface CaptionContextPayload {
  selected_topic: string
  language?: string
  target_audience?: string
  document?: {
    id: string
    file_name?: string
    total_pages?: number
    is_cached?: boolean
    created_at?: string | null
  }
  top_3_context_chunks: ContextPayloadChunk[]
}

export interface GenerateCaptionResponse {
  success?: boolean
  reason?: string
  message?: string
  data?: { caption?: string; final_caption?: string; hashtags?: string[]; message?: string; error_message?: string; validity_score?: number; failed_propositions?: FailedProposition[]; content_id?: string }
  document_id?: string
  selected_topic?: string
  language?: string
  target_audience?: string
  content_id?: string
  final_caption?: string
  caption?: string
  hashtags?: string[]
  top_3_context_chunks?: ContextPayloadChunk[]
  retrieval_count?: number
  rerank_method?: string
  ready_for_caption_generation?: boolean
  context_payload?: CaptionContextPayload
  validity_score?: number
  failed_propositions?: FailedProposition[]
  detail?: ApiErrorDetail | string
  error_message?: string
}

export interface GenerateCarouselResponse {
  success?: boolean
  content_id?: string
  carousel_images_urls?: string[]
  detail?: ApiErrorDetail | string
  error_message?: string
}

export interface VisualStoryBrief {
  visual_headline: string
  on_image_text?: string
  core_visual_message: string
  scene_concept: string
  main_subject: string
  supporting_elements: string[]
  visual_metaphor: string
  mood_tone: string
  negative_constraints: string[]
  linkedin_image_prompt: string
  carousel_readiness_notes: string
}

export interface ImageStorytellingResponse {
  success?: boolean
  visual_brief?: VisualStoryBrief
  source_topic?: string
  source_document_id?: string
  error?: string
  detail?: ApiErrorDetail | string
  error_message?: string
}

export interface ApiErrorDetail {
  error_message?: string
  error_code?: string
  details?: string
}

export interface TopicCardItem {
  id: string
  title: string
  score?: number
  potential?: string
  business_angle?: string
  angle?: string
  key_points?: string[]
  document_terms?: string[]
  evidence_chunks?: string[]
  approved?: boolean
}

export interface UploadedDocumentMetadata {
  document_id: string
  file_name: string
  total_pages?: number
  total_chunks?: number
  total_modules?: number
  is_cached?: boolean
}
