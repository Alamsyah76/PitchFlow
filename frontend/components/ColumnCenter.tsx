import React from 'react'

type Topic = { id?: string; text: string }

type Props = {
  loading?: boolean
  topics?: Topic[]
  onSelectTopic?: (topic: Topic) => void
  validityScore?: number
}

function Donut({ value = 0 }: { value: number }) {
  const size = 56
  const stroke = 8
  const radius = (size - stroke) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (value / 100) * circumference
  const color = value >= 95 ? 'text-emerald-500' : value >= 80 ? 'text-yellow-500' : 'text-red-500'
  return (
    <div className="flex items-center gap-3">
      <svg width={size} height={size} className={`${color}`}>
        <circle cx={size/2} cy={size/2} r={radius} stroke="#e6e7eb" strokeWidth={stroke} fill="none" />
        <circle cx={size/2} cy={size/2} r={radius} stroke="currentColor" strokeWidth={stroke} strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round" transform={`rotate(-90 ${size/2} ${size/2})`} fill="none" />
      </svg>
      <div className="text-sm">
        <div className="font-semibold">{value ?? '—'}%</div>
        <div className="text-xs text-slate-500">Validity</div>
      </div>
    </div>
  )
}

export default function ColumnCenter({ loading, topics = [], onSelectTopic, validityScore }: Props) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">AI Brainstorm & Facts</h2>
        <div>{typeof validityScore === 'number' ? <Donut value={validityScore} /> : <div className="text-sm text-slate-500">—</div>}</div>
      </div>

      {loading ? (
        <div className="p-6 bg-slate-50 rounded-md text-slate-500">Uploading & processing…</div>
      ) : topics.length === 0 ? (
        <div className="p-10 text-center text-slate-400">
          <svg className="mx-auto mb-3" width="80" height="48" viewBox="0 0 80 48" fill="none"><rect x="1" y="8" width="78" height="32" rx="4" stroke="#e6e7eb" strokeWidth="1.5"/></svg>
          <div className="text-sm">Upload a document to brainstorm topics and facts.</div>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3">
          {topics.map((t, i) => (
            <div key={t.id ?? i} onClick={()=>onSelectTopic?.(t)} className="p-4 bg-white border border-slate-100 rounded-md hover:border-sky-200 cursor-pointer transition-all duration-200 active:scale-[0.99] flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-sm font-medium text-slate-700">{i+1}</div>
              <div className="text-sm text-slate-800">{t.text}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
