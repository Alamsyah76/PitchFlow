import { Check, Loader2, Circle, X } from 'lucide-react'

export type WorkflowStepStatus = 'pending' | 'active' | 'completed' | 'error'

export interface WorkflowStep {
  label: string
  status: WorkflowStepStatus
}

export interface WorkflowStateBarProps {
  steps: WorkflowStep[]
}

function StepIcon({ status }: { status: WorkflowStepStatus }) {
  switch (status) {
    case 'completed':
      return (
        <div className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-100">
          <Check size={13} className="text-emerald-600" />
        </div>
      )
    case 'active':
      return (
        <div className="flex h-6 w-6 items-center justify-center rounded-full bg-[#6D5DFC]/10">
          <Loader2 size={13} className="animate-spin text-[#6D5DFC]" />
        </div>
      )
    case 'error':
      return (
        <div className="flex h-6 w-6 items-center justify-center rounded-full bg-rose-100">
          <X size={13} className="text-rose-500" />
        </div>
      )
    default:
      return (
        <div className="flex h-6 w-6 items-center justify-center rounded-full bg-slate-100">
          <Circle size={8} className="text-slate-300" />
        </div>
      )
  }
}

export default function WorkflowStateBar({ steps }: WorkflowStateBarProps) {
  const activeIndex = steps.findIndex((s) => s.status === 'active')

  return (
    <div className="flex items-center gap-0 border-b border-slate-200/70 bg-white px-4 py-2.5 md:px-8 lg:ml-[260px] xl:px-10">
      {steps.map((step, index) => {
        const isLast = index === steps.length - 1
        const isPast = index < activeIndex
        const isActive = index === activeIndex

        return (
          <div key={step.label} className="flex items-center gap-2">
            <div className="flex items-center gap-1.5">
              <StepIcon status={step.status} />
              <span
                className={`text-xs font-medium ${
                  step.status === 'completed'
                    ? 'text-emerald-700'
                    : step.status === 'active'
                      ? 'text-[#6D5DFC]'
                      : step.status === 'error'
                        ? 'text-rose-600'
                        : 'text-slate-400'
                }`}
              >
                {step.label}
              </span>
            </div>
            {!isLast && (
              <div
                className={`mx-2 h-px w-6 ${
                  isPast || isActive ? 'bg-[#6D5DFC]/30' : 'bg-slate-200'
                }`}
              />
            )}
          </div>
        )
      })}
    </div>
  )
}