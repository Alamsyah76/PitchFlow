import { Check } from 'lucide-react'
import { cn } from '../../lib/utils'

export type WorkflowStep = {
  id: number
  title: string
  status?: 'complete' | 'active' | 'pending'
}

type WorkflowStepperProps = {
  steps: readonly WorkflowStep[]
}

export default function WorkflowStepper({ steps }: WorkflowStepperProps) {
  return (
    <section className="overflow-x-auto rounded-2xl border border-slate-200/80 bg-white p-4 shadow-[0_18px_52px_rgba(15,23,42,0.07)]">
      <ol className="flex min-w-[760px] items-center">
        {steps.map((step, index) => {
          const status = step.status ?? 'pending'
          const isActive = status === 'active'
          const isComplete = status === 'complete'

          return (
            <li key={step.id} className="flex flex-1 items-center">
              <div className="flex items-center gap-3">
                <div
                  className={cn(
                    'flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl border text-sm font-semibold shadow-[0_8px_18px_rgba(15,23,42,0.04)]',
                    isComplete && 'border-[#6D5DFC] bg-[#6D5DFC] text-white',
                    isActive && 'border-[#6D5DFC] bg-[#6D5DFC]/10 text-[#5A4BE8]',
                    !isComplete && !isActive && 'border-slate-200 bg-slate-50 text-slate-400'
                  )}
                >
                  {isComplete ? <Check size={18} /> : step.id}
                </div>
                <div className="min-w-0">
                  <div className="text-xs font-medium uppercase tracking-wide text-slate-400">Step {step.id}</div>
                  <div className={cn('text-sm font-semibold', isActive ? 'text-slate-950' : 'text-slate-500')}>{step.title}</div>
                </div>
              </div>

              {index < steps.length - 1 && (
                <div className="mx-4 h-px flex-1 bg-slate-200">
                  <div className={cn('h-px bg-[#6D5DFC]', isComplete ? 'w-full' : 'w-0')} />
                </div>
              )}
            </li>
          )
        })}
      </ol>
    </section>
  )
}
