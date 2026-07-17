'use client'

type Props = { step: number; setStep: (s: 1|2|3|4) => void }

export default function StepProgress({ step, setStep }: Props) {
  const steps = [
    { n: 1 as const, l: 'Template', i: '📝' },
    { n: 2 as const, l: 'Audience', i: '👥' },
    { n: 3 as const, l: 'Review', i: '🚀' },
    { n: 4 as const, l: 'History', i: '📊' },
  ]
  return (
    <div className="mb-6">
      <div className="flex items-center justify-center gap-0">
        {steps.map((s, i) => (
          <div key={s.n} className="flex items-center">
            <button onClick={() => setStep(s.n)}
              className={`relative flex items-center gap-2.5 rounded-lg px-4 py-2.5 text-sm font-medium transition-all ${
                step === s.n
                  ? 'bg-[#0056b3] text-white shadow-sm'
                  : step > s.n
                  ? 'text-emerald-700 hover:bg-slate-100'
                  : 'text-slate-400 hover:text-slate-600 hover:bg-slate-50'
              }`}>
              <span className="flex h-5 w-5 items-center justify-center text-sm">
                {step > s.n ? (
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                ) : (
                  <span>{s.i}</span>
                )}
              </span>
              <span className={step === s.n ? '' : step > s.n ? '' : 'opacity-50'}>{s.l}</span>
            </button>
            {i < 3 && (
              <div className={`mx-2 h-px w-12 ${step > s.n ? 'bg-emerald-300' : 'bg-slate-200'}`} />
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
