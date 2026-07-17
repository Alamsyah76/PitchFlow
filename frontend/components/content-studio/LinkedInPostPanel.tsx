import { AlertCircle, Copy, Hash, Loader2 } from 'lucide-react'
import type { TopicCardItem } from '../../lib/content-types'

export interface LinkedInPostPanelProps {
  selectedTopic: TopicCardItem | null
  generatedCaption: string
  hashtags: string[]
  isGenerating: boolean
  captionError?: string
  isCopied: boolean
  onCopyCaption: () => void
}

export default function LinkedInPostPanel({
  selectedTopic,
  generatedCaption,
  hashtags,
  isGenerating,
  captionError,
  isCopied,
  onCopyCaption,
}: LinkedInPostPanelProps) {
  return (
    <div>
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="text-lg font-semibold text-slate-950">LinkedIn Post</h2>
          <p className="text-sm text-slate-500 mt-0.5">
            {selectedTopic ? selectedTopic.title : 'Select a topic before generating.'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={onCopyCaption}
            disabled={!generatedCaption}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-600 transition-colors hover:border-slate-300 hover:bg-slate-50 disabled:opacity-40"
          >
            <Copy size={14} />
            {isCopied ? 'Copied!' : 'Copy'}
          </button>
        </div>
      </div>

      {captionError && (
        <div className="mb-4 flex items-start gap-3 rounded-xl border border-rose-100 bg-rose-50 px-4 py-3 text-sm text-rose-800">
          <AlertCircle className="mt-0.5 shrink-0" size={16} />
          <span>{captionError}</span>
        </div>
      )}

      <div className="rounded-xl border border-slate-200/80 bg-white shadow-sm">
        <div className="p-6">
          {isGenerating && (
            <div className="space-y-3">
              <p className="text-sm text-slate-500 flex items-center gap-2">
                <Loader2 className="animate-spin text-[#6D5DFC]" size={14} />
                Generating LinkedIn post...
              </p>
              <div className="space-y-4 animate-pulse">
              <div className="h-5 w-3/4 rounded bg-slate-200" />
              <div className="h-4 w-full rounded bg-slate-100" />
              <div className="h-4 w-full rounded bg-slate-100" />
              <div className="h-4 w-5/6 rounded bg-slate-100" />
              <div className="h-4 w-4/5 rounded bg-slate-100" />
              <div className="mt-4 flex gap-2">
                <div className="h-6 w-20 rounded-full bg-slate-100" />
                <div className="h-6 w-24 rounded-full bg-slate-100" />
                <div className="h-6 w-16 rounded-full bg-slate-100" />
              </div>
            </div>
            </div>
          )}

          {!isGenerating && !generatedCaption && (
            <div className="flex min-h-[100px] flex-col items-center justify-center text-center">
              <p className="text-sm text-slate-400">No LinkedIn post yet</p>
            </div>
          )}

          {!isGenerating && generatedCaption && (
            <div className="max-w-prose">
              <h3 className="text-lg font-semibold text-slate-950">{selectedTopic?.title}</h3>
              <div className="mt-4 space-y-4 text-base leading-7 text-slate-700 lg:text-justify">
                {(generatedCaption.includes('\n\n')
                  ? generatedCaption.split(/\n\n+/)
                  : (() => {
                      const sentences = generatedCaption.match(/[^.!?]*[.!?]+/g) || [generatedCaption];
                      const groups: string[] = [];
                      for (let i = 0; i < sentences.length; i += 2) {
                        groups.push(sentences.slice(i, i + 2).join(' ').trim());
                      }
                      return groups.filter(Boolean);
                    })()
                ).map((paragraph, i) => (
                  <p key={i}>{paragraph.trim()}</p>
                ))}
              </div>
              {hashtags.length > 0 && (
                <div className="mt-6 flex flex-wrap gap-2 border-t border-slate-100 pt-4">
                  {hashtags.map((tag) => (
                    <span
                      key={tag}
                      className="inline-flex items-center gap-1 rounded-full border border-[#6D5DFC]/10 bg-[#6D5DFC]/[0.04] px-3 py-1 text-xs font-medium text-[#5A4BE8]"
                    >
                      <Hash size={11} />
                      {tag.replace('#', '')}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
