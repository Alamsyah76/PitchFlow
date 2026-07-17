import { useState } from 'react'
import { ChevronDown, ChevronRight, Code } from 'lucide-react'

type AdvancedDeveloperDetailsProps = {
  visualHeadline?: string
  onImageText?: string
  sceneConcept?: string
  linkedinImagePrompt?: string
  negativeConstraints?: string[]
}

export default function AdvancedDeveloperDetails({
  visualHeadline,
  onImageText,
  sceneConcept,
  linkedinImagePrompt,
  negativeConstraints,
}: AdvancedDeveloperDetailsProps) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="mt-4 rounded-2xl border border-slate-200/60 bg-white">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-2 px-4 py-3 text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors"
      >
        {expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        <Code size={16} />
        <span>Developer Details</span>
      </button>

      {expanded && (
        <div className="space-y-4 border-t border-slate-200/60 px-4 py-4 text-sm">
          {visualHeadline && (
            <div>
              <h4 className="mb-1 font-semibold text-slate-700">Visual Headline</h4>
              <p className="rounded-lg border border-slate-100 bg-[#FAFBFF] px-3 py-2 leading-6 text-slate-600">{visualHeadline}</p>
            </div>
          )}

          {onImageText && (
            <div>
              <h4 className="mb-1 font-semibold text-slate-700">On-Image Text</h4>
              <p className="rounded-lg border border-slate-100 bg-[#FAFBFF] px-3 py-2 leading-6 text-slate-600">{onImageText}</p>
            </div>
          )}

          {sceneConcept && (
            <div>
              <h4 className="mb-1 font-semibold text-slate-700">Scene Concept</h4>
              <p className="rounded-lg border border-slate-100 bg-[#FAFBFF] px-3 py-2 leading-6 text-slate-600">{sceneConcept}</p>
            </div>
          )}

          {linkedinImagePrompt && (
            <div>
              <h4 className="mb-1 font-semibold text-slate-700">LinkedIn Image Prompt</h4>
              <p className="rounded-lg border border-slate-100 bg-[#FAFBFF] px-3 py-2 text-slate-600 break-words">{linkedinImagePrompt}</p>
            </div>
          )}

          {negativeConstraints && negativeConstraints.length > 0 && (
            <div>
              <h4 className="mb-1 font-semibold text-slate-700">Negative Constraints</h4>
              <div className="flex flex-wrap gap-2">
                {negativeConstraints.map((c, i) => (
                  <span key={i} className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs text-slate-500">{c}</span>
                ))}
              </div>
            </div>
          )}

        </div>
      )}
    </div>
  )
}
