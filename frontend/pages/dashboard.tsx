'use client'
import AppShell from '../components/app-shell/AppShell'
import { useEffect, useState } from 'react'
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, AreaChart, Area, Legend,
} from 'recharts'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8042'

const COLORS = {
  primary: '#0056b3',
  success: '#22C55E',
  danger: '#EF4444',
  warning: '#F59E0B',
  slate: '#94A3B8',
  dark: '#1E293B',
  light: '#F1F5F9',
}

const PIE_COLORS = ['#22C55E', '#0056b3', '#EF4444', '#94A3B8']

interface Summary {
  total_sent: number; total_failed: number; today_sent: number; today_failed: number
  total_opens: number; unique_opens: number; open_rate: number
  total_contacts: number; pending: number; blog_posts_sent: number
  total_bounced?: number; bounce_rate?: number
  last_checked: string
}

interface ContentStats {
  total_documents: number; total_chunks: number; total_saved_contents: number
}

interface Campaign {
  template_id: string; name: string; sent: number; failed: number; bounced: number
  open_rate: number; first_sent: string; last_sent: string
}

interface TimelineDay { date: string; sent: number; failed: number; opens: number; unique_opens: number }
interface Activity { timestamp: string; email: string; name: string; status: string; error: string }

export default function DashboardRoute() {
  const [summary, setSummary] = useState<Summary | null>(null)
  const [contentStats, setContentStats] = useState<ContentStats | null>(null)
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [timeline, setTimeline] = useState<TimelineDay[]>([])
  const [activities, setActivities] = useState<Activity[]>([])
  const [loading, setLoading] = useState(true)
  const [range, setRange] = useState<7 | 14 | 30>(30)

  useEffect(() => {
    fetchAll()
  }, [range])

  async function fetchAll() {
    setLoading(true)
    try {
      const [sumRes, timeRes, actRes, contentRes, campRes] = await Promise.all([
        fetch(`${API}/api/email-campaign/report/summary`),
        fetch(`${API}/api/email-campaign/report/timeline?days=${range}`),
        fetch(`${API}/api/email-campaign/report/recent-activity?limit=8`),
        fetch(`${API}/api/v1/content/stats`),
        fetch(`${API}/api/email-campaign/report/campaigns?limit=10`),
      ])
      const [sumData, timeData, actData, contentData, campData] = await Promise.all([
        sumRes.json(), timeRes.json(), actRes.json(), contentRes.json(), campRes.json(),
      ])
      if (sumData.success) setSummary(sumData.data)
      if (timeData.success) setTimeline(timeData.data.timeline)
      if (actData.success) setActivities(actData.data)
      if (contentData.success) setContentStats(contentData.data)
      if (campData.success) setCampaigns(campData.data.campaigns || [])
    } catch (e) {
      console.error('Dashboard fetch error:', e)
    } finally {
      setLoading(false)
    }
  }

  const sentVsPending = summary ? [
    { name: 'Sent', value: summary.total_sent },
    { name: 'Pending', value: summary.pending },
    { name: 'Failed', value: summary.total_failed + (summary.total_bounced || 0) },
    { name: 'Open (unique)', value: summary.unique_opens },
  ] : []

  function fmt(n: number) { return n.toLocaleString('en-US') }

  if (loading && !summary) {
    return (
      <AppShell activeRoute="/dashboard">
        <div className="flex h-[70vh] items-center justify-center">
          <div className="flex flex-col items-center gap-3">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-[#0056b3] border-t-transparent" />
            <p className="text-sm text-slate-500">Loading dashboard...</p>
          </div>
        </div>
      </AppShell>
    )
  }

  return (
    <AppShell activeRoute="/dashboard">
      <div className="mx-auto max-w-7xl space-y-6 p-6">
        {/* ── Header ── */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
            <p className="mt-1 text-sm text-slate-500">Overview of Content Studio &amp; Email Campaign performance</p>
          </div>
          <button
            onClick={fetchAll}
            className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
            Refresh
          </button>
        </div>

        {/* ── Content Studio Panel (top) ── */}
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-slate-900">🎨 Content Studio</h3>
              <p className="text-xs text-slate-400">Documents processed &amp; content generated</p>
            </div>
            <a href="/content-studio" className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600 transition hover:bg-slate-50">Open Studio →</a>
          </div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="rounded-xl bg-slate-50 p-4">
              <p className="text-xs font-medium uppercase tracking-wider text-slate-500">Documents Uploaded</p>
              <p className="mt-1.5 text-2xl font-bold text-slate-900">{fmt(contentStats?.total_documents || 0)}</p>
              <p className="mt-1 text-xs text-slate-400">PDF processed</p>
            </div>
            <div className="rounded-xl bg-slate-50 p-4">
              <p className="text-xs font-medium uppercase tracking-wider text-slate-500">Knowledge Chunks</p>
              <p className="mt-1.5 text-2xl font-bold text-slate-900">{fmt(contentStats?.total_chunks || 0)}</p>
              <p className="mt-1 text-xs text-slate-400">RAG embeddings</p>
            </div>
            <div className="rounded-xl bg-slate-50 p-4">
              <p className="text-xs font-medium uppercase tracking-wider text-slate-500">Contents Saved</p>
              <p className="mt-1.5 text-2xl font-bold text-slate-900">{fmt(contentStats?.total_saved_contents || 0)}</p>
              <p className="mt-1 text-xs text-slate-400">Captions generated</p>
            </div>
          </div>
        </div>

        {/* ── Email Campaign Section ── */}
        <div className="pt-2">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-slate-900">📧 Email Campaign</h3>
              <p className="text-xs text-slate-400">Campaign performance &amp; delivery stats</p>
            </div>
            <a href="/email-campaign" className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600 transition hover:bg-slate-50">Open Campaign →</a>
          </div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <KpiCard
              title="Total Sent"
              value={fmt(summary?.total_sent || 0)}
              subtitle={`${summary?.today_sent || 0} today`}
              color={COLORS.success}
              icon={<SentIcon />}
            />
            <KpiCard
              title="Open Rate"
              value={`${summary?.open_rate || 0}%`}
              subtitle={`${summary?.unique_opens || 0} unique opens`}
              color={COLORS.primary}
              icon={<OpenIcon />}
            />
            <KpiCard
              title="Bounce Rate"
              value={`${summary?.bounce_rate || 0}%`}
              subtitle={`${summary?.total_bounced || 0} bounced`}
              color={COLORS.danger}
              icon={<BounceIcon />}
            />
            <KpiCard
              title="Total Contacts"
              value={fmt(summary?.total_contacts || 0)}
              subtitle={`${summary?.pending || 0} pending`}
              color={COLORS.dark}
              icon={<ContactIcon />}
            />
          </div>
        </div>

        {/* ── Two-column charts ── */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Line Chart: Daily Sends */}
          <ChartCard title="📈 Daily Sends" subtitle="Last 30 days" className="lg:col-span-2">
            <div className="mb-3 flex gap-2">
              {([7, 14, 30] as const).map(d => (
                <button
                  key={d}
                  onClick={() => setRange(d)}
                  className={`rounded-md px-3 py-1 text-xs font-medium transition ${
                    range === d
                      ? 'bg-[#0056b3] text-white'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {d}d
                </button>
              ))}
            </div>
            <ResponsiveContainer width="100%" height={260}>
              <AreaChart data={timeline}>
                <defs>
                  <linearGradient id="sentGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={COLORS.primary} stopOpacity={0.2} />
                    <stop offset="95%" stopColor={COLORS.primary} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={d => d.slice(5)} stroke="#94A3B8" />
                <YAxis tick={{ fontSize: 11 }} stroke="#94A3B8" allowDecimals={false} />
                <Tooltip
                  contentStyle={{ borderRadius: 8, border: '1px solid #E2E8F0', boxShadow: '0 4px 12px rgba(0,0,0,0.08)' }}
                  labelFormatter={d => `Date: ${d}`}
                />
                <Area type="monotone" dataKey="sent" stroke={COLORS.primary} fill="url(#sentGrad)" strokeWidth={2} name="Sent" />
                <Line type="monotone" dataKey="opens" stroke={COLORS.success} strokeWidth={2} dot={false} name="Opens" strokeDasharray="4 4" />
              </AreaChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Donut: Sent vs Pending */}
          <ChartCard title="🥧 Campaign Overview" subtitle="Distribution">
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={sentVsPending}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {sentVsPending.map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ borderRadius: 8, border: '1px solid #E2E8F0' }}
                  formatter={(value: any, name: any) => [fmt(Number(value) || 0), name]}
                />
                <Legend
                  verticalAlign="bottom"
                  iconType="circle"
                  iconSize={8}
                  formatter={(value: string) => <span className="text-xs text-slate-600">{value}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* ── Bar Chart: Daily Failed vs Sent (stacked) ── */}
        <ChartCard title="📊 Send Performance" subtitle="Green = success, Red = failed">
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={timeline.slice(-14)}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={d => d.slice(5)} stroke="#94A3B8" />
              <YAxis tick={{ fontSize: 11 }} stroke="#94A3B8" allowDecimals={false} />
              <Tooltip
                contentStyle={{ borderRadius: 8, border: '1px solid #E2E8F0' }}
                labelFormatter={d => `Date: ${d}`}
              />
              <Bar dataKey="sent" stackId="a" fill={COLORS.success} name="Sent" radius={[2, 2, 0, 0]} />
              <Bar dataKey="failed" stackId="a" fill={COLORS.danger} name="Failed" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* ── Campaigns Table (Mailchimp-style) ── */}
        <ChartCard title="🚀 Campaigns" subtitle="Per template performance">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-xs uppercase text-slate-500">
                  <th className="pb-2 pr-4 font-medium">Campaign</th>
                  <th className="pb-2 pr-4 font-medium">Sent</th>
                  <th className="pb-2 pr-4 font-medium">Opens</th>
                  <th className="pb-2 pr-4 font-medium">Open Rate</th>
                  <th className="pb-2 pr-4 font-medium">Bounced</th>
                  <th className="pb-2 font-medium">Last Sent</th>
                </tr>
              </thead>
              <tbody>
                {campaigns.length === 0 ? (
                  <tr><td colSpan={6} className="py-8 text-center text-sm text-slate-400">No campaigns yet — send your first email campaign</td></tr>
                ) : campaigns.map((c, i) => (
                  <tr key={i} className="border-b border-slate-100 hover:bg-slate-50">
                    <td className="py-2.5 pr-4 font-medium text-slate-700 max-w-[220px] truncate">{c.name}</td>
                    <td className="py-2.5 pr-4 text-slate-600">{fmt(c.sent)}</td>
                    <td className="py-2.5 pr-4 text-slate-600">{c.sent > 0 ? Math.round(c.open_rate / 100 * c.sent) : 0}</td>
                    <td className="py-2.5 pr-4">
                      <span className="inline-flex items-center rounded-full bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700">{c.open_rate}%</span>
                    </td>
                    <td className="py-2.5 pr-4">
                      {c.bounced > 0 ? (
                        <span className="inline-flex items-center rounded-full bg-red-50 px-2 py-0.5 text-xs font-medium text-red-700">{c.bounced}</span>
                      ) : (
                        <span className="text-slate-400">0</span>
                      )}
                    </td>
                    <td className="py-2.5 text-xs text-slate-500 whitespace-nowrap">{c.last_sent?.slice(0, 16) || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </ChartCard>

        {/* ── Recent Activity ── */}
        <ChartCard title="📋 Recent Activity" subtitle="Last 8 sends">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-xs uppercase text-slate-500">
                  <th className="pb-2 pr-4 font-medium">Time</th>
                  <th className="pb-2 pr-4 font-medium">Email</th>
                  <th className="pb-2 pr-4 font-medium">Status</th>
                  <th className="pb-2 font-medium">Error</th>
                </tr>
              </thead>
              <tbody>
                {activities.length === 0 ? (
                  <tr><td colSpan={4} className="py-8 text-center text-sm text-slate-400">No activity yet</td></tr>
                ) : activities.map((a, i) => (
                  <tr key={i} className="border-b border-slate-100 hover:bg-slate-50">
                    <td className="py-2.5 pr-4 text-xs text-slate-500 whitespace-nowrap">{a.timestamp?.slice(11, 19)}</td>
                    <td className="py-2.5 pr-4 text-slate-600">{a.email}</td>
                    <td className="py-2.5 pr-4">
                      {a.status === 'sent' ? (
                        <span className="inline-flex items-center rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">✅ Sent</span>
                      ) : a.status === 'bounced' ? (
                        <span className="inline-flex items-center rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700">❌ Bounced</span>
                      ) : (
                        <span className="inline-flex items-center rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700">❌ Failed</span>
                      )}
                    </td>
                    <td className="py-2.5 text-xs text-slate-400 max-w-[200px] truncate">{a.error || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </ChartCard>
      </div>
    </AppShell>
  )
}

// ── Sub-components ──

function KpiCard({ title, value, subtitle, color, icon }: {
  title: string; value: string; subtitle: string; color: string; icon: React.ReactNode
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">{title}</p>
          <p className="mt-1.5 text-2xl font-bold text-slate-900">{value}</p>
          <p className="mt-1 text-xs text-slate-400">{subtitle}</p>
        </div>
        <div className="flex h-10 w-10 items-center justify-center rounded-lg" style={{ backgroundColor: color + '15' }}>
          <div style={{ color }}>{icon}</div>
        </div>
      </div>
    </div>
  )
}

function ChartCard({ title, subtitle, children, className = '' }: {
  title: string; subtitle?: string; children: React.ReactNode; className?: string
}) {
  return (
    <div className={`rounded-xl border border-slate-200 bg-white p-5 shadow-sm ${className}`}>
      <div className="mb-3">
        <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
        {subtitle && <p className="text-xs text-slate-400">{subtitle}</p>}
      </div>
      {children}
    </div>
  )
}

// ── Icons ──
function SentIcon() {
  return <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
}
function OpenIcon() {
  return <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
}
function BounceIcon() {
  return <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h2m4 0h4M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
}
function ContactIcon() {
  return <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
}
function BlogIcon() {
  return <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" /></svg>
}
