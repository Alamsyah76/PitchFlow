import { Sparkles, Loader2, Check, ArrowRight } from 'lucide-react'
import type { TopicCardItem } from '../../lib/content-types'

export interface TopicSelectionGridProps {
  topics: TopicCardItem[]
  selectedTopic: TopicCardItem | null
  isGeneratingTopics: boolean
  onSelectTopic: (topic: TopicCardItem) => void
}

export default function TopicSelectionGrid({
  topics,
  selectedTopic,
  isGeneratingTopics,
  onSelectTopic,
}: TopicSelectionGridProps) {
  if (isGeneratingTopics) {
    return (
      <div className="flex min-h-[100px] items-center justify-center gap-3 text-sm text-slate-500">
        <Loader2 className="animate-spin text-[#6D5DFC]" size={18} />
        Generating topics from the uploaded document...
      </div>
    )
  }

  if (topics.length === 0) {
    return (
      <div className="flex min-h-[100px] flex-col items-center justify-center text-center">
        <Sparkles className="text-slate-300" size={24} />
        <div className="mt-2 text-sm font-medium text-slate-700">No topics generated yet</div>
        <p className="mt-1 text-sm text-slate-500">Upload a PDF, then generate topics to continue.</p>
      </div>
    )
  }

  return (
    <div>
      <h2 className="mb-2 text-sm font-semibold text-slate-950">Recommended Content Angles</h2>
      <div className="flex flex-col gap-2">
        {topics.map((topic) => {
          const isSelected = selectedTopic?.id === topic.id
          return (
            <button
              key={topic.id}
              onClick={() => onSelectTopic(topic)}
              className={`flex w-full min-h-[100px] items-center gap-3 rounded-xl border px-4 py-3 text-left transition-all ${
                isSelected
                  ? 'border-[#6D5DFC]/70 bg-[#6D5DFC]/[0.04] ring-2 ring-[#6D5DFC]/12'
                  : 'border-slate-200/80 bg-white shadow-sm hover:border-slate-300 hover:shadow-md'
              }`}
            >
              <div className="min-w-0 flex-1">
                <h3 className={`text-sm font-medium leading-5 line-clamp-4 ${isSelected ? 'text-[#5A4BE8]' : 'text-slate-950'}`}>
                  {topic.title}
                </h3>
              </div>
              <div className={`flex shrink-0 items-center justify-center rounded-lg ${
                isSelected ? 'bg-[#6D5DFC] text-white' : 'border border-slate-200 text-slate-400'
              } h-7 w-7`}>
                {isSelected ? <Check size={14} /> : <ArrowRight size={14} />}
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
