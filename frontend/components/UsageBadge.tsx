'use client'

import { useEffect, useState } from 'react'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8027'

type UsageData = {
  tier: string
  tier_label: string
  konten: { used: number; limit: number | null }
  image: { used: number; limit: number | null; quality: string | null }
  chat: { used: number; limit: number | null }
}

export default function UsageBadge() {
  const [data, setData] = useState<UsageData | null>(null)

  useEffect(() => {
    fetch(`${API}/api/plan/status`)
      .then(r => r.json())
      .then(d => d.success && setData(d.data))
      .catch(() => {})
  }, [])

  if (!data) return null

  const tierColors: Record<string, string> = { free: 'bg-slate-200 text-slate-600', basic: 'bg-blue-100 text-blue-700', bisnis: 'bg-purple-100 text-purple-700', pro: 'bg-amber-100 text-amber-700' }
  const color = tierColors[data.tier] || tierColors.free

  return (
    <div className="fixed bottom-6 left-6 z-50 hidden md:block">
      <div className={`rounded-xl border border-slate-200/60 bg-white px-3 py-2 shadow-sm text-xs ${color.split(' ')[1]}`}>
        <div className="flex items-center gap-2">
          <span className={`rounded-md px-1.5 py-0.5 text-[10px] font-semibold uppercase ${color}`}>{data.tier_label}</span>
          {data.konten.limit !== null && (
            <span className="text-slate-500">Konten {data.konten.used}/{data.konten.limit}</span>
          )}
          {data.chat.limit !== null && (
            <span className="text-slate-500">· Chat {data.chat.used}/{data.chat.limit}</span>
          )}
        </div>
      </div>
    </div>
  )
}
