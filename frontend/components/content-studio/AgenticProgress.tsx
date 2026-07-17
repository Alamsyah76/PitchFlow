'use client'
import { useEffect, useState } from 'react'
import { apiUrl } from '../../lib/api'

interface ProgressEvent {
  agent: string
  status: string
  progress: number
  message: string
}

interface AgenticProgressProps {
  documentId: string
  isActive: boolean
  onComplete: (result: any) => void
  onError: (error: string) => void
}

const AGENT_COLORS: Record<string, string> = {
  Strategy: 'from-blue-400 to-blue-600',
  Data: 'from-emerald-400 to-emerald-600',
  Reporting: 'from-violet-400 to-violet-600',
  Complete: 'from-green-400 to-green-600',
}

const AGENT_LABELS: Record<string, string> = {
  Strategy: '🧠 Strategy Agent',
  Data: '📊 Data Agent',
  Reporting: '✍️ Reporting Agent',
  Complete: '✅ Selesai',
}

export default function AgenticProgress({ documentId, isActive, onComplete, onError }: AgenticProgressProps) {
  const [events, setEvents] = useState<ProgressEvent[]>([])
  const [currentProgress, setCurrentProgress] = useState(0)
  const [currentMessage, setCurrentMessage] = useState('')

  useEffect(() => {
    if (!isActive || !documentId) return

    setEvents([])
    setCurrentProgress(0)

    const url = apiUrl(`/api/v1/content/topics/agentic/stream?doc_id=${encodeURIComponent(documentId)}`)
    const source = new EventSource(url)

    source.onmessage = (e) => {
      try {
        const data: ProgressEvent = JSON.parse(e.data)
        setEvents((prev) => [...prev, data])
        setCurrentProgress(data.progress)
        setCurrentMessage(data.message)

        if (data.agent === 'Complete' && data.status === 'done') {
          // Result will come via onresult event
        }
        if (data.agent === 'Error') {
          onError(data.message)
          source.close()
        }
      } catch { }
    }

    source.addEventListener('result', (e: MessageEvent) => {
      try {
        const data = JSON.parse(e.data)
        onComplete(data)
      } catch { }
      source.close()
    })

    source.addEventListener('error', (e: MessageEvent) => {
      try {
        const data = JSON.parse(e.data)
        onError(data.message || 'Unknown error')
      } catch {
        onError('Connection lost')
      }
      source.close()
    })

    source.onerror = () => {
      // EventSource auto-reconnects, but if progress never reached 100, it's an error
      if (currentProgress < 100) {
        onError('Connection interrupted. Please try again.')
      }
      source.close()
    }

    return () => source.close()
  }, [isActive, documentId])

  if (!isActive) return null

  return (
    <div className="space-y-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      {/* Progress bar */}
      <div className="h-2 overflow-hidden rounded-full bg-slate-100">
        <div
          className={`h-full rounded-full bg-gradient-to-r from-blue-500 via-emerald-500 to-violet-500 transition-all duration-500 ease-out`}
          style={{ width: `${currentProgress}%` }}
        />
      </div>

      {/* Current step */}
      <div className="flex items-center gap-2 text-sm">
        <span className="text-slate-400">{currentProgress}%</span>
        <span className="font-medium text-slate-700">{currentMessage}</span>
      </div>

      {/* Agent timeline */}
      <div className="flex gap-2">
        {['Strategy', 'Data', 'Reporting', 'Complete'].map((agent) => {
          const done = events.some((e) => e.agent === agent && e.status === 'done')
          const active = events.some((e) => e.agent === agent && e.status === 'running') && !done
          return (
            <div
              key={agent}
              className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium transition-all ${
                done
                  ? 'bg-emerald-50 text-emerald-700'
                  : active
                  ? 'bg-blue-50 text-blue-700 ring-1 ring-blue-200'
                  : 'bg-slate-50 text-slate-400'
              }`}
            >
              <span className={`h-1.5 w-1.5 rounded-full ${
                done ? 'bg-emerald-500' : active ? 'bg-blue-500 animate-pulse' : 'bg-slate-300'
              }`} />
              {AGENT_LABELS[agent] || agent}
              {done && ' ✓'}
            </div>
          )
        })}
      </div>
    </div>
  )
}
