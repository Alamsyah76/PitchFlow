'use client'

import { ArrowRight, FileText, ImageIcon, Lightbulb, MessageSquareText, Sparkles } from 'lucide-react'

const steps = [
  { icon: FileText, label: 'Extract business context' },
  { icon: Lightbulb, label: 'Recommend content angles' },
  { icon: MessageSquareText, label: 'Generate LinkedIn post' },
  { icon: ImageIcon, label: 'Build creative direction' },
  { icon: Sparkles, label: 'Create AI visual' },
]

export default function WorkspaceBlueprint() {
  return (
    <div className="flex h-full flex-col justify-center px-6 py-12 xl:px-10">
      <h3 className="text-sm font-semibold text-slate-950">How it works</h3>
      <p className="mt-1 text-xs text-slate-500">
        From document to publishable content in five steps.
      </p>
      <ol className="mt-6 space-y-5">
        {steps.map((step, i) => {
          const Icon = step.icon
          return (
            <li key={step.label} className="flex items-start gap-3">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-[#5F54F2]/10 to-[#8B5CF6]/10">
                <Icon size={17} className="text-[#6D5DFC]" />
              </div>
              <div className="flex min-w-0 flex-1 items-center gap-2 pt-1">
                <span className="text-sm font-medium text-slate-700">{step.label}</span>
                {i < steps.length - 1 && <ArrowRight size={14} className="shrink-0 text-slate-300" />}
              </div>
            </li>
          )
        })}
      </ol>
    </div>
  )
}
