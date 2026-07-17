import { useState, useRef, ChangeEvent } from 'react'
import { AlertCircle, Bookmark, Check, Loader2, Sparkles } from 'lucide-react'
import UploadPanel from './UploadPanel'
import TopicSelectionGrid from './TopicSelectionGrid'
import LinkedInPostPanel from './LinkedInPostPanel'
import CreativeDirectionPanel from './CreativeDirectionPanel'
import WorkspaceBlueprint from './WorkspaceBlueprint'
import LoadingButton from './LoadingButton'
import WorkflowStateBar from './WorkflowStateBar'
import ContentStudioHero from './ContentStudioHero'
import { fetchTopics, generateCaption, generateImageFromPrompt, generateImageStorytelling, uploadPdf, apiUrl, authHeaders } from '../../lib/api'
import { autoSaveProject } from '../../lib/workspace-storage'
import { requireLogin } from '../../lib/auth-check'
import type { CaptionContextPayload, FailedProposition, GenerateCaptionRequest, TopicCardItem, UploadedDocumentMetadata, VisualStoryBrief } from '../../lib/content-types'

interface LoadingState {
  upload: boolean
  topics: boolean
  caption: boolean
  carousel: boolean
}

interface ErrorState {
  upload?: string
  topics?: string
  caption?: string
  carousel?: string
  global?: string
}

function getErrorMessage(error: unknown, fallback: string) {
  if (typeof error === 'string') return error
  if (error && typeof error === 'object') {
    const err = error as {
      detail?: string | { error_message?: string; details?: string }
      error_message?: string
      message?: string
      details?: string
    }
    if (typeof err.detail === 'string') return err.detail
    if (err.detail?.error_message) return err.detail.error_message
    if (err.detail?.details) return err.detail.details
    if (err.error_message) return err.error_message
    if (err.message) return err.message
    if (err.details) return err.details
  }
  return fallback
}

function debugTopics(message: string, payload?: unknown) {
  if (process.env.NODE_ENV === 'development') {
    console.debug(`[ContentStudio topics] ${message}`, payload)
  }
}

function debugCaption(message: string, payload?: unknown) {
  if (process.env.NODE_ENV === 'development') {
    console.debug(`[ContentStudio caption] ${message}`, payload)
  }
}

function getTopicCandidates(input: unknown): unknown[] {
  if (Array.isArray(input)) return input
  if (typeof input === 'string') {
    return input.split(/\r?\n|,/).map((item) => item.trim()).filter(Boolean)
  }
  if (input && typeof input === 'object') {
    const item = input as { topics?: unknown; data?: { topics?: unknown }; topic?: unknown; title?: unknown; text?: unknown }
    if (Array.isArray(item.topics)) return item.topics
    if (Array.isArray(item.data?.topics)) return item.data.topics
    if (typeof item.topics === 'string') return getTopicCandidates(item.topics)
    if (typeof item.data?.topics === 'string') return getTopicCandidates(item.data.topics)
    if (item.topic || item.title || item.text) return [item]
  }
  return []
}

function normalizeTopics(rawInput: unknown): TopicCardItem[] {
  const rawTopics = getTopicCandidates(rawInput)
  return rawTopics
    .map((topic, index) => {
      if (typeof topic === 'string') {
        return { id: String(index + 1), title: topic }
      }
      if (topic && typeof topic === 'object') {
        const item = topic as {
          id?: string | number; topic_id?: string; topic?: string; title?: string; text?: string
          audience?: string; score?: number; potential?: string; business_angle?: string; angle?: string; key_points?: string[]; document_terms?: string[]; evidence_chunks?: string[]; approved?: boolean
        }
        return {
          id: String(item.topic_id ?? item.id ?? index + 1),
          title: item.topic ?? item.title ?? item.text ?? '',
          score: item.score,
          potential: item.potential ?? item.audience,
          business_angle: item.business_angle ?? item.angle,
          angle: item.angle ?? item.business_angle,
          key_points: item.key_points,
          document_terms: Array.isArray(item.document_terms) ? item.document_terms : undefined,
          evidence_chunks: Array.isArray(item.evidence_chunks) ? item.evidence_chunks : undefined,
          approved: item.approved,
        }
      }
      return { id: String(index + 1), title: '' }
    })
    .filter((topic) => topic.title.trim().length > 0)
}

function getDerivedHashtags(caption: string) {
  const embeddedTags = Array.from(new Set(caption.match(/#[A-Za-z0-9]+/g) ?? []))
  if (embeddedTags.length > 0) return embeddedTags.slice(0, 5)
  const stopwords = new Set([
    'about', 'after', 'business', 'data', 'document', 'emerges', 'factual', 'friction', 'operational',
    'reference', 'source', 'their', 'these', 'without', 'dalam', 'dengan', 'dokumen', 'karena',
    'lebih', 'masalahnya', 'operasional', 'referensi', 'sebagai', 'secara', 'tanpa', 'untuk', 'yang',
  ])
  const words = caption
    .replace(/<[^>]+>/g, ' ')
    .replace(/[^a-zA-Z0-9\s]/g, ' ')
    .split(/\s+/)
    .map((word) => word.toLowerCase())
    .filter((word) => word.length > 3 && !stopwords.has(word))
  const phrases: string[] = []
  for (let index = 0; index < words.length - 1; index += 1) {
    const phrase = `${words[index]} ${words[index + 1]}`
    if (!phrases.includes(phrase)) phrases.push(phrase)
    if (phrases.length === 5) break
  }
  return phrases.map((phrase) =>
    `#${phrase.split(' ').map((word) => `${word.charAt(0).toUpperCase()}${word.slice(1)}`).join('')}`
  )
}

export default function ContentStudioPage() {
  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadedDocument, setUploadedDocument] = useState<UploadedDocumentMetadata | null>(null)
  const [documentId, setDocumentId] = useState<string | null>(null)
  const [topics, setTopics] = useState<TopicCardItem[]>([])
  const [selectedTopic, setSelectedTopic] = useState<TopicCardItem | null>(null)
  const [generatedCaption, setGeneratedCaption] = useState('')
  const [captionHashtags, setCaptionHashtags] = useState<string[]>([])
  const [captionContext, setCaptionContext] = useState<CaptionContextPayload | null>(null)
  const [validityScore, setValidityScore] = useState<number | null>(null)
  const [failedPropositions, setFailedPropositions] = useState<FailedProposition[]>([])
  const [contentId, setContentId] = useState<string | null>(null)
  const [carouselImageUrls, setCarouselImageUrls] = useState<string[]>([])
  const [imageStorytellingLoading, setImageStorytellingLoading] = useState(false)
  const [visualStoryBrief, setVisualStoryBrief] = useState<VisualStoryBrief | null>(null)
  const [imageStorytellingError, setImageStorytellingError] = useState<string | null>(null)
  const [imageGenerationLoading, setImageGenerationLoading] = useState(false)
  const [generatedImageUrl, setGeneratedImageUrl] = useState<string | null>(null)
  const [imageGenerationError, setImageGenerationError] = useState<string | null>(null)
  const [hasGeneratedImage, setHasGeneratedImage] = useState(false)
  const outputLanguage: 'id' = 'id'
  const [loading, setLoading] = useState<LoadingState>({ upload: false, topics: false, caption: false, carousel: false })
  const [errors, setErrors] = useState<ErrorState>({})
  const [apiError, setApiError] = useState<string | null>(null)
  const [isCopied, setIsCopied] = useState(false)
  const [saveToast, setSaveToast] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)

  // Request generation guard: increment on every new request to discard stale responses
  const requestGeneration = useRef(0)
  const topicsAbortRef = useRef<AbortController | null>(null)
  const captionAbortRef = useRef<AbortController | null>(null)

  const hashtags = captionHashtags.length > 0 ? captionHashtags : getDerivedHashtags(generatedCaption)

  async function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    if (!requireLogin()) return
    const file = event.target.files?.[0]
    if (!file) return
    // Increment request generation to invalidate stale in-flight responses
    requestGeneration.current += 1
    const gen = requestGeneration.current
    // Abort any in-flight topics/caption requests
    topicsAbortRef.current?.abort()
    topicsAbortRef.current = null
    captionAbortRef.current?.abort()
    captionAbortRef.current = null
    // Reset all state
    setSelectedFile(file)
    setUploadedDocument(null)
    setDocumentId(null)
    setTopics([])
    setSelectedTopic(null)
    setGeneratedCaption('')
    setCaptionHashtags([])
    setCaptionContext(null)
    setValidityScore(null)
    setFailedPropositions([])
    setContentId(null)
    setCarouselImageUrls([])
    setVisualStoryBrief(null)
    setImageStorytellingError(null)
    setImageGenerationError(null)
    setGeneratedImageUrl(null)
    setErrors({})
    setApiError(null)
    setLoading((s) => ({ ...s, upload: true }))
    try {
      const response = await uploadPdf(file)
      // Guard: discard stale response
      if (gen !== requestGeneration.current) return
      const data = response.data ?? response
      const nextDocumentId = data.document_id ?? data.id
      if (!nextDocumentId) {
        throw new Error(data.error_message ?? 'Upload succeeded but no document_id was returned.')
      }
      setUploadedDocument({
        document_id: nextDocumentId,
        file_name: data.filename ?? data.file_name ?? file.name,
        total_pages: data.pages ?? data.total_pages,
        total_chunks: data.total_chunks,
        total_modules: data.total_modules,
        is_cached: data.is_cached,
      })
      setDocumentId(nextDocumentId)
    } catch (error) {
      const message = getErrorMessage(error, 'Failed to upload PDF.')
      console.error('Upload failed:', error)
      setApiError(message)
      setErrors((s) => ({ ...s, upload: message }))
    } finally {
      setLoading((s) => ({ ...s, upload: false }))
    }
  }

  async function handleGenerateTopics() {
    if (!documentId) {
      setErrors((s) => ({ ...s, topics: 'Upload a PDF before generating topics.' }))
      return
    }
    // Increment generation guard
    requestGeneration.current += 1
    const gen = requestGeneration.current
    // Abort previous topics request
    topicsAbortRef.current?.abort()
    const abortController = new AbortController()
    topicsAbortRef.current = abortController
    setErrors((s) => ({ ...s, topics: undefined, caption: undefined, carousel: undefined }))
    setTopics([])
    setSelectedTopic(null)
    setGeneratedCaption('')
    setCaptionHashtags([])
    setCaptionContext(null)
    setValidityScore(null)
    setFailedPropositions([])
    setContentId(null)
    setCarouselImageUrls([])
    setLoading((s) => ({ ...s, topics: true }))
    setApiError(null)
    try {
      debugTopics('generateTopics request', {
        active_uploaded_filename: uploadedDocument?.file_name ?? selectedFile?.name ?? null,
        active_document_id: documentId,
        selected_language: outputLanguage,
      })
      const response = await fetchTopics(documentId, outputLanguage, abortController.signal)
      // Guard: discard stale response
      if (gen !== requestGeneration.current) return
      const rawNormalized = normalizeTopics(response)
      const normalized = Array.isArray(rawNormalized) ? rawNormalized : []
      debugTopics('raw response', response)
      debugTopics('response topic titles', normalized.map((t) => t.title))
      if (normalized.length === 0) {
        const msg = 'No topics were returned for this document. The PDF may not contain enough readable text, or the topic generator returned an unexpected response.'
        setApiError(msg)
        setErrors((s) => ({ ...s, topics: msg }))
        return
      }
      setTopics((prev) => {
        debugTopics('topics state transition', { before: prev.map((t) => t.title), after: normalized.map((t) => t.title) })
        return normalized
      })
    } catch (error: unknown) {
      // Ignore aborted errors silently
      if (error instanceof DOMException && error.name === 'AbortError') return
      const message = getErrorMessage(error, 'Failed to generate topics.')
      console.error('Topic generation failed:', error)
      setApiError(message)
      setErrors((s) => ({ ...s, topics: message }))
    } finally {
      if (topicsAbortRef.current === abortController) topicsAbortRef.current = null
      setLoading((s) => ({ ...s, topics: false }))
    }
  }

  function handleSelectTopic(topic: TopicCardItem) {
    if (selectedTopic?.id === topic.id) return
    setSelectedTopic(topic)
    setGeneratedCaption('')
    setCaptionHashtags([])
    setCaptionContext(null)
    setValidityScore(null)
    setFailedPropositions([])
    setContentId(null)
    setCarouselImageUrls([])
    setVisualStoryBrief(null)
    setImageStorytellingError(null)
    setImageGenerationError(null)
    setGeneratedImageUrl(null)
    setErrors((s) => ({ ...s, caption: undefined, carousel: undefined }))
  }

  async function handleGenerateCaption() {
    if (!documentId || !selectedTopic) {
      setErrors((s) => ({ ...s, caption: 'Select a topic before generating a caption.' }))
      return
    }
    // Increment generation guard
    requestGeneration.current += 1
    const gen = requestGeneration.current
    // Abort previous caption request
    captionAbortRef.current?.abort()
    const abortController = new AbortController()
    captionAbortRef.current = abortController
    setErrors((s) => ({ ...s, caption: undefined, carousel: undefined }))
    setGeneratedCaption('')
    setCaptionHashtags([])
    setCaptionContext(null)
    setValidityScore(null)
    setFailedPropositions([])
    setContentId(null)
    setCarouselImageUrls([])
    setVisualStoryBrief(null)
    setImageStorytellingError(null)
    setImageGenerationError(null)
    setGeneratedImageUrl(null)
    setLoading((s) => ({ ...s, caption: true }))
    setApiError(null)
    const payload: GenerateCaptionRequest = {
      document_id: documentId,
      selected_topic: selectedTopic.title,
      topic: selectedTopic,
      target_lang: outputLanguage,
      language: outputLanguage,
      topic_id: selectedTopic.id,
      business_angle: selectedTopic.business_angle,
    }
    try {
      debugCaption('generateCaption request', {
        active_uploaded_filename: uploadedDocument?.file_name ?? selectedFile?.name ?? null,
        document_id: documentId,
        topic_id: selectedTopic.id,
        selected_topic: selectedTopic.title,
        business_angle: selectedTopic.business_angle,
        evidence_chunks: selectedTopic.evidence_chunks ?? [],
      })
      const response = await generateCaption(payload, abortController.signal)
      // Guard: discard stale response
      if (gen !== requestGeneration.current) return
      const capData = response.data ?? response
      const rawCaption = capData.caption ?? capData.final_caption ?? ''
      const finalCaption = (typeof rawCaption === 'string' ? rawCaption : '').trim()
      const hasCaptionText = finalCaption.length > 0
      const shouldDisplayCaption = hasCaptionText
      debugCaption('raw response', response)
      debugCaption('caption gate', {
        finalCaption,
        finalCaptionLength: finalCaption.length,
        responseSuccess: response.success,
        shouldDisplayCaption,
        captionPreview: finalCaption.slice(0, 280),
      })
      if (!shouldDisplayCaption) {
        const msg = capData.message ?? capData.error_message ?? 'Caption generation did not complete yet.'
        setGeneratedCaption('')
        setCaptionContext(null)
        setCaptionHashtags([])
        setValidityScore(null)
        setFailedPropositions([])
        setContentId(null)
        setErrors((s) => ({ ...s, caption: msg }))
        return
      }
      setCaptionContext(null)
      setGeneratedCaption((prev) => {
        debugCaption('caption state transition', { before: prev.slice(0, 280), after: finalCaption.slice(0, 280) })
        return finalCaption
      })
      setCaptionHashtags(capData.hashtags ?? [])
      setValidityScore(typeof capData.validity_score === 'number' ? capData.validity_score : null)
      setFailedPropositions(capData.failed_propositions ?? [])
      setContentId(capData.content_id ?? null)
    } catch (error: unknown) {
      // Ignore aborted errors silently
      if (error instanceof DOMException && error.name === 'AbortError') return
      const message = getErrorMessage(error, 'Failed to prepare caption context.')
      console.error('Caption context request failed:', error)
      setApiError(message)
      setErrors((s) => ({ ...s, caption: message }))
    } finally {
      if (captionAbortRef.current === abortController) captionAbortRef.current = null
      setLoading((s) => ({ ...s, caption: false }))
    }
  }

  async function handleGenerateCarousel() {
    if (!documentId || !generatedCaption || !selectedTopic) return
    setImageStorytellingError(null)
    setCarouselImageUrls([])
    setImageGenerationError(null)
    setGeneratedImageUrl(null)
    setImageStorytellingLoading(true)
    try {
      const payload = {
        document_id: documentId,
        caption: generatedCaption,
        topic: selectedTopic.title,
        hashtags: hashtags.length > 0 ? hashtags : undefined,
      }
      const resp = await fetch(apiUrl('/api/v1/content/generate-carousel'), {
        method: 'POST',
        headers: { ...authHeaders(), 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const json = await resp.json()
      if (!json.success) {
        setImageStorytellingError(json.detail ?? 'Image generation failed.'); return
      }
      const baseUrl = apiUrl('').replace(/\/$/, '')
      const imgUrl = `${baseUrl}${json.data.image_url}`
      setGeneratedImageUrl(imgUrl)
      setHasGeneratedImage(true)
      // Auto-save to Library
      autoSaveProject({
        pdf_filename: uploadedDocument?.file_name ?? selectedFile?.name ?? 'Unknown.pdf',
        selected_topic: selectedTopic?.title ?? '(no topic)',
        caption_text: generatedCaption,
        hashtags,
        image_url: imgUrl,
      }, selectedTopic?.title ?? '')
    } catch (error) {
      const message = getErrorMessage(error, 'Failed to generate image.')
      setImageStorytellingError(message)
    } finally {
      setImageStorytellingLoading(false)
    }
  }

  async function handleGenerateImageFromPrompt() {
    if (!visualStoryBrief?.linkedin_image_prompt) return
    setImageGenerationError(null)
    setGeneratedImageUrl(null)
    setImageGenerationLoading(true)
    try {
      const payload = { linkedin_image_prompt: visualStoryBrief.linkedin_image_prompt }
      const response = await generateImageFromPrompt(payload)
      if (!response.success || !response.image_url) {
        const msg = response.error_message ?? 'Image generation failed.'
        setImageGenerationError(msg); return
      }
      setGeneratedImageUrl(response.image_url)
    } catch (error) {
      const message = getErrorMessage(error, 'Failed to generate image.')
      console.error('Image generation failed:', error)
      setImageGenerationError(message)
    } finally {
      setImageGenerationLoading(false)
    }
  }

  async function handleCopyCaption() {
    if (!generatedCaption) return
    const sections = [
      selectedTopic?.title,
      generatedCaption,
      hashtags.length > 0 ? hashtags.join(' ') : null,
    ].filter((section): section is string => Boolean(section && section.trim().length > 0))
    const text = sections.join('\n\n')
    await navigator.clipboard.writeText(text)
    setIsCopied(true)
    window.setTimeout(() => setIsCopied(false), 2000)
  }

  async function handleSaveToLibrary() {
    if (!uploadedDocument && !selectedFile && !generatedCaption) return
    setIsSaving(true)
    await new Promise(r => setTimeout(r, 300))
    autoSaveProject({
      pdf_filename: uploadedDocument?.file_name ?? selectedFile?.name ?? 'Unknown.pdf',
      selected_topic: selectedTopic?.title ?? '(no topic)',
      caption_text: generatedCaption,
      hashtags,
      image_url: generatedImageUrl,
    }, selectedTopic?.title ?? '')
    setIsSaving(false)
    setSaveToast('Project saved to Library')
    window.setTimeout(() => setSaveToast(null), 3000)
  }

  async function handleDownloadZip() {
    if (!generatedCaption || !selectedTopic) return
    setIsSaving(true)
    try {
      const payload: Record<string, any> = {
        topic: selectedTopic.title,
        caption: generatedCaption,
      }
      if (hashtags.length > 0) payload.hashtags = hashtags
      if (generatedImageUrl) {
        try { payload.image_path = new URL(generatedImageUrl).pathname }
        catch { payload.image_path = generatedImageUrl }
      }
      const resp = await fetch(apiUrl('/api/v1/content/download-zip'), {
        method: 'POST',
        headers: { ...authHeaders(), 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!resp.ok) { setSaveToast('Download failed'); setIsSaving(false); return }
      const blob = await resp.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url; a.download = `${selectedTopic.title.slice(0, 30)}.zip`
      document.body.appendChild(a); a.click(); document.body.removeChild(a)
      URL.revokeObjectURL(url)
      setSaveToast('Downloaded!')
      window.setTimeout(() => setSaveToast(null), 3000)
    } catch { setSaveToast('Download failed') }
    setIsSaving(false)
  }

  const isEmpty = !uploadedDocument && !selectedFile && !generatedCaption && topics.length === 0
  const hasTopics = Array.isArray(topics) && topics.length > 0

  const workflowSteps = [
    { label: 'Upload', status: documentId ? 'completed' as const : loading.upload ? 'active' as const : 'pending' as const },
    { label: 'Topics', status: topics.length > 0 ? 'completed' as const : loading.topics ? 'active' as const : documentId ? 'pending' as const : 'pending' as const },
    { label: 'Caption', status: generatedCaption ? 'completed' as const : loading.caption ? 'active' as const : selectedTopic ? 'pending' as const : 'pending' as const },
    { label: 'Image', status: generatedImageUrl ? 'completed' as const : imageStorytellingLoading ? 'active' as const : generatedCaption ? 'pending' as const : 'pending' as const },
    { label: 'Save', status: saveToast ? 'completed' as const : isSaving ? 'active' as const : generatedImageUrl ? 'pending' as const : 'pending' as const },
  ]

  return (
    <>
      {!isEmpty && <WorkflowStateBar steps={workflowSteps} />}
      {/* === EMPTY STATE: Hero Workspace === */}
      {isEmpty && (
        <div className="grid min-h-[calc(100vh-9rem)] grid-cols-1 divide-y xl:grid-cols-12 xl:divide-x xl:divide-y-0 divide-slate-200/70">
          <ContentStudioHero
            onUploadClick={() => fileInputRef.current?.click()}
            fileInputRef={fileInputRef}
            onFileChange={handleFileChange}
          />

          <div className="xl:col-span-8">
            <WorkspaceBlueprint />
          </div>
        </div>
      )}

      {/* === ACTIVE STATE: Existing Workflow === */}
      {!isEmpty && (
      <div className="mx-auto flex h-[calc(100vh-7rem)] max-w-screen-2xl flex-col overflow-hidden">
      <div className="flex flex-1 flex-row overflow-hidden">
        {/* Left column — fixed-height flex column */}
        <div className="flex w-[280px] shrink-0 flex-col border-r border-slate-200/60">
          <div className="shrink-0 space-y-4 p-3 md:p-4">
            {/* Hidden file input — always rendered so Change button works */}
            <input ref={fileInputRef} type="file" accept="application/pdf" className="hidden" onChange={handleFileChange} />
            {errors.global && (
            <div className="flex items-start gap-3 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-sm text-rose-800">
              <AlertCircle className="mt-0.5 shrink-0" size={18} />
              <span>{errors.global}</span>
            </div>
          )}

          {apiError && (
            <div className="flex items-start gap-3 rounded-2xl border border-amber-100 bg-amber-50 px-4 py-3 text-sm text-amber-900">
              <AlertCircle className="mt-0.5 shrink-0" size={18} />
              <span>{apiError}</span>
            </div>
          )}

          <UploadPanel
            selectedFile={selectedFile}
            uploadedDocument={uploadedDocument}
            documentId={documentId}
            isUploading={loading.upload}
            uploadError={errors.upload}
            topicsError={errors.topics}
            isGeneratingTopics={loading.topics}
            compact={Boolean(selectedFile || uploadedDocument)}
            fileInputRef={fileInputRef}
            onFileChange={handleFileChange}
            onChooseFile={() => fileInputRef.current?.click()}
            onGenerateTopics={handleGenerateTopics}
          />
          </div>

          {hasTopics && (
          <div className="min-h-0 flex-1 overflow-y-auto border-t border-slate-100 bg-slate-50/50 p-3 md:p-4">
            <TopicSelectionGrid
              topics={topics}
              selectedTopic={selectedTopic}
              isGeneratingTopics={loading.topics}
              onSelectTopic={handleSelectTopic}
            />
          </div>
          )}
        </div>

        {/* Right column — output canvas */}
        <div className="min-w-0 flex-1 space-y-6 overflow-y-auto p-4 md:p-6">
          {errors.caption && (
            <div className="flex items-start gap-3 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-sm text-rose-800">
              <AlertCircle className="mt-0.5 shrink-0" size={18} />
              <span>{errors.caption}</span>
            </div>
          )}

          {/* Generate Topics loading state */}
          {loading.topics && (
            <div className="flex h-full min-h-[300px] flex-col items-center justify-center text-center">
              <Loader2 className="animate-spin text-[#6D5DFC]" size={36} />
              <h2 className="mt-5 text-xl font-bold text-slate-900">Generating Content Angles</h2>
              <p className="mt-2 max-w-md text-sm leading-relaxed text-slate-500">
                Analyzing your document and preparing recommended topics.
              </p>
            </div>
          )}

          {/* Post-upload pre-generation: compact bar left, Generate Topics CTA right */}
          {!generatedCaption && !loading.topics && !hasTopics && (uploadedDocument || selectedFile) && (
            <div className="flex h-full min-h-[300px] flex-col items-center justify-center text-center">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-[#6D5DFC]/10 to-[#8B5CF6]/10">
                <Sparkles size={26} className="text-[#6D5DFC]" />
              </div>
              <h2 className="mt-5 text-xl font-bold text-slate-900">Ready to Generate Content Angles</h2>
              <p className="mt-2 max-w-md text-sm leading-relaxed text-slate-500">
                Your document is uploaded. Generate recommended LinkedIn content angles to get started.
              </p>
              <LoadingButton
                onClick={handleGenerateTopics}
                disabled={!documentId || loading.topics}
                loading={loading.topics}
                loadingText="Generating Topics..."
                icon={<Sparkles size={18} />}
                size="lg"
              >
                Generate Topics
              </LoadingButton>
            </div>
          )}

          {/* Topics ready — no caption generated yet */}
          {!generatedCaption && !loading.caption && hasTopics && !selectedTopic && (
            <div className="flex h-full min-h-[200px] flex-col items-center justify-center text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100">
                <Sparkles size={22} className="text-slate-400" />
              </div>
              <h3 className="mt-4 text-base font-semibold text-slate-800">Topics are ready</h3>
              <p className="mt-1.5 max-w-xs text-sm text-slate-500">
                Select a recommended content angle from the left panel to generate your post.
              </p>
            </div>
          )}

          {/* Topic selected — ready to generate caption */}
          {!generatedCaption && !loading.caption && selectedTopic && hasTopics && (
            <div className="flex h-full min-h-[200px] flex-col items-center justify-center text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100">
                <Sparkles size={22} className="text-slate-400" />
              </div>
              <h3 className="mt-4 text-base font-semibold text-slate-800">Topic selected</h3>
              <p className="mt-1.5 max-w-xs text-sm text-slate-500">
                Generate a LinkedIn post based on your selected topic.
              </p>
              <LoadingButton
                onClick={handleGenerateCaption}
                disabled={loading.caption}
                loading={loading.caption}
                loadingText="Generating LinkedIn Post..."
                icon={<Sparkles size={16} />}
              >
                Generate LinkedIn Post
              </LoadingButton>
            </div>
          )}

          {/* LinkedIn Post Panel — also shown while caption is generating */}
          {(generatedCaption || loading.caption) && (
            <LinkedInPostPanel
              selectedTopic={selectedTopic}
              generatedCaption={generatedCaption}
              hashtags={hashtags}
              isGenerating={loading.caption}
              captionError={errors.caption}
              isCopied={isCopied}
              onCopyCaption={handleCopyCaption}
            />
          )}

          {/* Next Step: Creative Direction cue */}
          {generatedCaption && !hasGeneratedImage && !imageStorytellingLoading && !imageStorytellingError && (
            <div className="rounded-2xl border border-dashed border-[#6D5DFC]/30 bg-gradient-to-br from-[#6D5DFC]/[0.03] to-[#8B5CF6]/[0.03] p-6">
              <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[#6D5DFC]">
                <Sparkles size={14} />
                Next Step
              </div>
              <h3 className="mt-3 text-base font-semibold text-slate-950">Generate Image</h3>
              <p className="mt-1.5 text-sm leading-relaxed text-slate-500">
                Generate image with background scene, topic title, and 3 key points from your content.
              </p>
              <LoadingButton
                onClick={handleGenerateCarousel}
                disabled={imageStorytellingLoading}
                loading={imageStorytellingLoading}
                loadingText="Generating Carousel..."
                icon={imageStorytellingLoading ? undefined : <Sparkles size={16} />}
                size="md"
              >
                Generate Image
              </LoadingButton>
            </div>
          )}

          {(generatedImageUrl || imageStorytellingLoading || imageStorytellingError) && (
            <div className="rounded-2xl border border-slate-200/80 bg-white p-4 shadow-sm">
              <h3 className="mb-3 text-sm font-semibold text-slate-950">Image Preview</h3>
              {imageStorytellingLoading && (
                <div className="flex items-center gap-2 text-sm text-slate-500">
                  <Loader2 className="animate-spin" size={16} /> Generating image with text...
                </div>
              )}
              {imageStorytellingError && (
                <p className="text-sm text-red-500">{imageStorytellingError}</p>
              )}
              {generatedImageUrl && (
                <img
                  src={generatedImageUrl}
                  alt="Content image"
                  className="w-full rounded-lg border border-slate-200 shadow-sm"
                />
              )}
            </div>
          )}

          {/* Save To Library — only after caption AND creative direction */}
          {generatedCaption && generatedImageUrl && (
            <div className="flex items-center justify-between rounded-2xl border border-slate-200/80 bg-white p-4 shadow-[0_8px_20px_rgba(15,23,42,0.04)]">
              <span className="text-sm font-medium text-slate-700">
                {saveToast ?? 'Download topic, content, hashtags & image as ZIP'}
              </span>
              <LoadingButton
                onClick={handleDownloadZip}
                disabled={isSaving || !!saveToast}
                loading={isSaving}
                loadingText="Packaging..."
                icon={saveToast ? <Check size={16} /> : <Bookmark size={16} />}
                size="sm"
              >
                {saveToast ? 'Downloaded' : 'Download ZIP'}
              </LoadingButton>
            </div>
          )}
        </div>
      </div>
      </div>
      )}
    </>
  )
}