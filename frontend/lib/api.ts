import type {
  GenerateCaptionRequest,
  GenerateCaptionResponse,
  GenerateCarouselResponse,
  ImageStorytellingResponse,
  TopicsResponse,
  UploadPdfResponse
} from './content-types'

const RAW_API_BASE = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8027'
const LOCAL_DEV_JWT =
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJhdXRoZW50aWNhdGVkIiwic3ViIjoiMDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAxIiwiZW1haWwiOiJ1c2VyQGRldi5sb2NhbCIsInJvbGUiOiJhdXRoZW50aWNhdGVkIiwiaWF0IjoxNzc5ODUyMzY4LCJleHAiOjIwOTUyMTIzNjh9.jCsCM82ZRb9kSMYIi8ZLqB1CBj2d9KBn1HYDjYs70Oo'

function isLocalDevelopmentApi() {
  if (process.env.NODE_ENV === 'production') return false

  try {
    const parsed = new URL(RAW_API_BASE)
    return ['127.0.0.1', 'localhost'].includes(parsed.hostname)
  } catch {
    return RAW_API_BASE.includes('127.0.0.1') || RAW_API_BASE.includes('localhost')
  }
}

function isLikelyUsableJwt(token: string) {
  const trimmed = token.trim()
  const parts = trimmed.split('.')
  if (parts.length !== 3) return false

  try {
    const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')))
    if (!payload || typeof payload !== 'object') return false

    if (typeof payload.exp === 'number') {
      const now = Math.floor(Date.now() / 1000)
      if (payload.exp <= now) return false
    }

    return typeof payload.sub === 'string' && payload.sub.length > 0
  } catch {
    return false
  }
}

function clearStoredAuthTokens() {
  if (typeof window === 'undefined') return

  try {
    window.localStorage.removeItem('supabase_access_token')
    window.localStorage.removeItem('access_token')
    window.sessionStorage.removeItem('supabase_access_token')
    window.sessionStorage.removeItem('access_token')
  } catch {
    // Ignore storage cleanup issues in the browser.
  }
}

export function apiUrl(path: string) {
  const base = RAW_API_BASE.replace(/\/$/, '')
  const normalizedPath = path.startsWith('/') ? path : `/${path}`

  if (base.endsWith('/api/v1') && normalizedPath.startsWith('/api/v1/')) {
    return `${base}${normalizedPath.replace('/api/v1', '')}`
  }

  return `${base}${normalizedPath}`
}

async function parseJsonResponse<T>(resp: Response): Promise<T> {
  const data = await resp.json().catch(() => ({}))

  if (!resp.ok) {
    throw data
  }

  return data as T
}

function getAuthToken() {
  const localDevApi = isLocalDevelopmentApi()

  if (typeof window !== 'undefined') {
    const storedToken =
      window.localStorage.getItem('supabase_access_token') ||
      window.localStorage.getItem('access_token') ||
      window.sessionStorage.getItem('supabase_access_token') ||
      window.sessionStorage.getItem('access_token')

    if (storedToken && isLikelyUsableJwt(storedToken)) return storedToken
    if (storedToken) clearStoredAuthTokens()
  }

  if (process.env.NEXT_PUBLIC_DEV_AUTH_TOKEN && isLikelyUsableJwt(process.env.NEXT_PUBLIC_DEV_AUTH_TOKEN)) {
    return process.env.NEXT_PUBLIC_DEV_AUTH_TOKEN
  }

  if (localDevApi) {
    return ''
  }

  return process.env.NODE_ENV !== 'production' && isLikelyUsableJwt(LOCAL_DEV_JWT) ? LOCAL_DEV_JWT : ''
}

export function authHeaders(): HeadersInit {
  const token = getAuthToken()
  if (process.env.NODE_ENV === 'development') {
    console.log('AUTH TOKEN:', token)
  }

  if (!token || token === 'undefined' || token === 'null') {
    return {}
  }

  if (isLocalDevelopmentApi()) {
    return {}
  }

  return { Authorization: `Bearer ${token}` }
}

function debugApi(label: string, payload?: unknown) {
  if (process.env.NODE_ENV === 'development') {
    console.debug(`[ContentStudio api] ${label}`, payload)
  }
}

export async function uploadPdf(file: File, form?: FormData): Promise<UploadPdfResponse> {
  const body = form ?? (() => {
    const fd = new FormData()
    fd.append('file', file)
    return fd
  })()

  const resp = await fetch(apiUrl('/api/v1/content/upload'), {
    method: 'POST',
    headers: authHeaders(),
    body
  })
  return parseJsonResponse<UploadPdfResponse>(resp)
}

export async function generateCaption(payload: GenerateCaptionRequest, signal?: AbortSignal): Promise<GenerateCaptionResponse> {
  const url = apiUrl('/api/v1/content/generate-caption')
  debugApi('generateCaption request', { url, body: payload })
  const resp = await fetch(url, {
    method: 'POST',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    signal,
  })
  return parseJsonResponse<GenerateCaptionResponse>(resp)
}

export async function generateCarousel(content_id: string): Promise<GenerateCarouselResponse> {
  const resp = await fetch(apiUrl(`/api/v1/content/generate-carousel?content_id=${encodeURIComponent(content_id)}`), {
    headers: authHeaders()
  })
  return parseJsonResponse<GenerateCarouselResponse>(resp)
}

export async function fetchTopics(document_id: string, lang = 'en', signal?: AbortSignal): Promise<TopicsResponse> {
  const params = new URLSearchParams({
    document_id,
    lang
  })
  const url = apiUrl(`/api/v1/content/topics?${params.toString()}`)
  debugApi('generateTopics request', { url, document_id, lang })
  const resp = await fetch(url, {
    headers: authHeaders(),
    signal,
  })
  return parseJsonResponse<TopicsResponse>(resp)
}

export async function generateImageFromPrompt(payload: {
  linkedin_image_prompt: string
  image_size?: string
}): Promise<{
  success?: boolean
  image_url?: string
  error_message?: string
  is_transient_url?: boolean
  expires_in_seconds?: number
}> {
  const url = apiUrl('/api/v1/image-generation/generate')
  debugApi('generateImageFromPrompt request', { url, promptLength: payload.linkedin_image_prompt.length })
  const resp = await fetch(url, {
    method: 'POST',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  return parseJsonResponse(resp)
}

export async function generateImageStorytelling(payload: {
  document_id: string
  selected_topic: string
  caption: string
  hashtags?: string[]
}): Promise<ImageStorytellingResponse> {
  const url = apiUrl('/api/v1/image-storytelling/generate')
  debugApi('generateImageStorytelling request', { url, body: payload })
  const resp = await fetch(url, {
    method: 'POST',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  return parseJsonResponse<ImageStorytellingResponse>(resp)
}
