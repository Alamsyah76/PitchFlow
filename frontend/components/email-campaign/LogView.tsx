'use client'
import { useState, useEffect } from 'react'

type LogEntry = { timestamp: string; email: string; name: string; company: string; status: string; error: string }
type Report = { date: string; total_sent: number; total_failed: number; total_opens: number; unique_opens: number; open_rate: number; total_contacts: number; pending: number; recent: any[] }

type Props = { logs: LogEntry[]; API: string; onClear?: () => void }

export default function LogView({ logs, API, onClear }: Props) {
  const [clearing, setClearing] = useState(false)
  const [report, setReport] = useState<Report | null>(null)

  useEffect(() => {
    fetch(`${API}/api/email-campaign/daily-report`).then(r => r.json()).then(d => {
      if (d.success) setReport(d.data)
    }).catch(() => {})
  }, [API])

  async function handleClear() {
    if (!confirm('Clear all log entries?')) return
    setClearing(true)
    try {
      const r = await fetch(`${API}/api/email-campaign/log/clear`, { method: 'POST' })
      const d = await r.json()
      if (d.success && onClear) onClear()
      else alert(d.message || 'Failed to clear log')
    } catch {
      alert('Network error')
    } finally {
      setClearing(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* Report Card */}
      {report && (
        <div className="rounded-xl border border-slate-200 bg-white shadow-[0_1px_3px_rgba(0,0,0,0.04)]">
          <div className="border-b border-slate-100 px-5 py-3">
            <h3 className="text-sm font-semibold text-slate-900">📊 Today's Report — {report.date}</h3>
          </div>
          <div className="grid grid-cols-2 gap-3 p-5 md:grid-cols-5">
            <div className="rounded-lg bg-emerald-50 px-3 py-2.5 text-center">
              <p className="text-lg font-bold text-emerald-700">{report.total_sent}</p>
              <p className="text-[10px] font-medium uppercase tracking-wider text-emerald-600">Sent</p>
            </div>
            <div className="rounded-lg bg-red-50 px-3 py-2.5 text-center">
              <p className="text-lg font-bold text-red-600">{report.total_failed}</p>
              <p className="text-[10px] font-medium uppercase tracking-wider text-red-500">Failed</p>
            </div>
            <div className="rounded-lg bg-blue-50 px-3 py-2.5 text-center">
              <p className="text-lg font-bold text-blue-700">{report.unique_opens}</p>
              <p className="text-[10px] font-medium uppercase tracking-wider text-blue-600">Opened</p>
            </div>
            <div className="rounded-lg bg-purple-50 px-3 py-2.5 text-center">
              <p className="text-lg font-bold text-purple-700">{report.open_rate}%</p>
              <p className="text-[10px] font-medium uppercase tracking-wider text-purple-600">Open Rate</p>
            </div>
            <div className="rounded-lg bg-amber-50 px-3 py-2.5 text-center">
              <p className="text-lg font-bold text-amber-700">{report.pending}</p>
              <p className="text-[10px] font-medium uppercase tracking-wider text-amber-600">Pending</p>
            </div>
          </div>
        </div>
      )}

      {/* Log Table */}
      <div className="rounded-xl border border-slate-200 bg-white shadow-[0_1px_3px_rgba(0,0,0,0.04)]">
        <div className="flex items-center justify-between border-b border-slate-100 px-5 py-3.5">
          <div>
            <h2 className="text-base font-semibold text-slate-900">Send History</h2>
            <p className="mt-0.5 text-xs text-slate-500">{logs.length} entries</p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={handleClear} disabled={clearing || logs.length === 0}
              className="inline-flex items-center gap-1.5 rounded-lg border border-red-200 bg-white px-3 py-1.5 text-xs font-medium text-red-600 transition-colors hover:bg-red-50 disabled:opacity-40">
              Clear Log
            </button>
            <a href={`${API}/api/email-campaign/log/download`} download
              className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-50">
              Download CSV
            </a>
          </div>
        </div>

        {logs.length === 0 ? (
          <div className="flex flex-col items-center px-6 py-12">
            <p className="text-sm text-slate-500">No send history yet</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-xs font-semibold uppercase tracking-wider text-slate-500">
                  <th className="px-5 py-3.5">Time</th>
                  <th className="px-5 py-3.5">Name</th>
                  <th className="px-5 py-3.5">Email</th>
                  <th className="px-5 py-3.5">Company</th>
                  <th className="px-5 py-3.5">Status</th>
                  <th className="px-5 py-3.5">Note</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((e, i) => (
                  <tr key={i} className={`border-b border-slate-50 transition-colors hover:bg-slate-50 ${i % 2 === 0 ? 'bg-white' : 'bg-slate-50/30'}`}>
                    <td className="whitespace-nowrap px-5 py-3.5 text-xs text-slate-500">{e.timestamp}</td>
                    <td className="px-5 py-3.5 font-medium text-slate-900">{e.name}</td>
                    <td className="px-5 py-3.5 text-slate-600">{e.email}</td>
                    <td className="px-5 py-3.5 text-slate-500">{e.company}</td>
                    <td className="px-5 py-3.5">
                      <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium ring-1 ${
                        e.status === 'sent'
                          ? 'bg-emerald-50 text-emerald-700 ring-emerald-200'
                          : 'bg-red-50 text-red-700 ring-red-200'
                      }`}>
                        <span className={`h-1.5 w-1.5 rounded-full ${e.status === 'sent' ? 'bg-emerald-500' : 'bg-red-500'}`} />
                        {e.status === 'sent' ? 'Sent' : 'Failed'}
                      </span>
                    </td>
                    <td className="max-w-[200px] truncate px-5 py-3.5 text-xs text-slate-500">{e.error || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
