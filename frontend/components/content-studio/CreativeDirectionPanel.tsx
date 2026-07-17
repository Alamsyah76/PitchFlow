import React, { useCallback, useState } from 'react'
import { AlertCircle, Download, ImageIcon, Loader2, Sparkles } from 'lucide-react'
import { Button } from '../ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import type { VisualStoryBrief } from '../../lib/content-types'

export interface CreativeDirectionPanelProps {
  visualStoryBrief: VisualStoryBrief | null
  isGeneratingCreativeDirection: boolean
  creativeDirectionError?: string | null
  isGeneratingImage: boolean
  imageGenerationError?: string | null
  generatedImageUrl: string | null
  onGenerateCreativeDirection: () => void
  onGenerateImage: () => void
  topicHeadline?: string
  captionExcerpt?: string
  overlayHashtags?: string[]
}

function truncate(text: string, maxLen: number): string {
  if (text.length <= maxLen) return text
  const trimmed = text.slice(0, maxLen)
  const lastSpace = trimmed.lastIndexOf(' ')
  return (lastSpace > maxLen * 0.7 ? trimmed.slice(0, lastSpace) : trimmed) + '…'
}

export default function CreativeDirectionPanel({
  visualStoryBrief,
  isGeneratingCreativeDirection,
  creativeDirectionError,
  isGeneratingImage,
  imageGenerationError,
  generatedImageUrl,
  onGenerateCreativeDirection,
  onGenerateImage,
  topicHeadline = '',
  captionExcerpt = '',
  overlayHashtags,
}: CreativeDirectionPanelProps) {
  const [isDownloading, setIsDownloading] = useState(false)

  const headline = truncate(topicHeadline || '', 90)
  const excerpt = truncate(captionExcerpt || '', 180)
  const visibleHashtags = (overlayHashtags || []).slice(0, 3)

  const handleDownload = useCallback(async () => {
    if (!generatedImageUrl) return
    setIsDownloading(true)
    try {
      const resp = await fetch(generatedImageUrl, { mode: 'cors' })
      if (!resp.ok) throw new Error('fetch failed')
      const blob = await resp.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'sci-linkedin-visual.png'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch {
      window.open(generatedImageUrl, '_blank')
    } finally {
      setIsDownloading(false)
    }
  }, [generatedImageUrl])

  return (
    <section>
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between gap-4">
            <div>
              <CardTitle>Creative Direction</CardTitle>
              <CardDescription>Visual concept generated from selected topic and caption.</CardDescription>
            </div>
            <Button
              variant="gradient"
              size="sm"
              disabled={isGeneratingCreativeDirection}
              onClick={onGenerateCreativeDirection}
            >
              {isGeneratingCreativeDirection ? <Loader2 className="animate-spin" size={16} /> : <Sparkles size={16} />}
              {isGeneratingCreativeDirection ? 'Generating Creative Direction...' : 'Generate Creative Direction'}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {creativeDirectionError && (
            <div className="flex items-start gap-3 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-sm text-rose-800">
              <AlertCircle className="mt-0.5 shrink-0" size={18} />
              <span>{creativeDirectionError}</span>
            </div>
          )}

          {isGeneratingCreativeDirection && (
            <div className="space-y-4 animate-pulse">
              <div className="h-4 w-full rounded bg-slate-100" />
              <div className="h-4 w-5/6 rounded bg-slate-100" />
              <div className="h-4 w-4/5 rounded bg-slate-100" />
              <div className="h-20 w-full rounded-lg bg-slate-100 mt-4" />
            </div>
          )}

          {!visualStoryBrief && !isGeneratingCreativeDirection && !creativeDirectionError && (
            <div className="flex min-h-[90px] flex-col items-center justify-center text-center">
              <p className="text-sm text-slate-400">No visual direction yet</p>
            </div>
          )}

          {visualStoryBrief && (
          <div className="space-y-5">
            {visualStoryBrief?.core_visual_message && (
              <div className="rounded-xl border border-slate-200 bg-[#FAFBFF] px-4 py-3 text-sm leading-6 text-slate-700">
                {visualStoryBrief.core_visual_message}
              </div>
            )}

            {imageGenerationError && (
              <div className="flex items-start gap-3 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-sm text-rose-800">
                <AlertCircle className="mt-0.5 shrink-0" size={18} />
                <span>{imageGenerationError}</span>
              </div>
            )}

            <div className="pt-2">
              <Button
                variant="gradient"
                size="sm"
                disabled={isGeneratingImage || !visualStoryBrief?.linkedin_image_prompt}
                onClick={onGenerateImage}
              >
                {isGeneratingImage ? <Loader2 className="animate-spin" size={16} /> : <ImageIcon size={16} />}
                {isGeneratingImage ? 'Generating...' : 'Generate Image'}
              </Button>
            </div>

            {generatedImageUrl && (
              <div className="mt-4 rounded-xl border border-slate-200 bg-white p-2">
                <div className="relative">
                  <img src={generatedImageUrl} alt="Generated visual" className="w-full rounded-lg" />
                  <div className="pointer-events-none absolute inset-x-0 bottom-0 rounded-b-lg bg-gradient-to-t from-black/70 via-black/40 to-transparent px-3 pb-3 pt-8">
                    {headline && (
                      <p className="text-sm font-bold leading-tight text-white drop-shadow-sm break-words">
                        {headline}
                      </p>
                    )}
                    {excerpt && (
                      <p className="mt-1 text-[11px] leading-tight text-white/80 drop-shadow-sm break-words">
                        {excerpt}
                      </p>
                    )}
                    {visibleHashtags.length > 0 && (
                      <p className="mt-1 text-[10px] leading-tight text-white/60 drop-shadow-sm break-words">
                        {visibleHashtags.join('  ')}
                      </p>
                    )}
                  </div>
                </div>
                <p className="mt-2 text-xs text-slate-500 px-1">
                  LinkedIn-ready visual generated for this content.
                </p>
                <div className="mt-2 flex justify-end px-1">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={isDownloading}
                    onClick={handleDownload}
                  >
                    {isDownloading ? <Loader2 className="animate-spin" size={13} /> : <Download size={13} />}
                    {isDownloading ? 'Downloading...' : 'Download Image'}
                  </Button>
                </div>
              </div>
            )}
          </div>
          )}
        </CardContent>
      </Card>
    </section>
  )
}
