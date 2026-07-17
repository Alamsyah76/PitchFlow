'use client'
import { useState, useEffect } from 'react'

type ContactPreview = { name: string; email: string; company: string; job_title: string; phone?: string; status?: string; last_template?: string }

type Props = {
  contacts: ContactPreview[]
  selectedIdx: Set<number>
  searchQ: string
  loading: boolean
  status: any
  filter: 'all' | 'pending' | 'sent'
  onFilterChange: (f: 'all' | 'pending' | 'sent') => void
  onSearch: (q: string) => void
  onToggle: (i: number) => void
  onSelectAll: () => void
  onUpload: (e: React.ChangeEvent<HTMLInputElement>) => void
  onEdit: (i: number, c: ContactPreview) => void
  onDelete: (email: string) => void
  onBack: () => void
  onReview: () => void
  onAddClick?: () => void
}

export default function AudienceList({ contacts, selectedIdx, searchQ, loading, status, filter, onFilterChange, onSearch, onToggle, onSelectAll, onUpload, onEdit, onDelete, onBack, onReview, onAddClick }: Props) {
  const [pageSize, setPageSize] = useState(10);
  const [page, setPage] = useState(0);

  const filtered = contacts.filter(c => filter === 'all' || (filter === 'pending' ? c.status !== 'sent' : c.status === 'sent'));
  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const safePage = Math.min(page, totalPages - 1);
  const pageContacts = filtered.slice(safePage * pageSize, (safePage + 1) * pageSize);

  // Reset to page 0 when filter changes
  useEffect(() => { setPage(0); }, [filter]);

  return (
    <div className="rounded-2xl border border-slate-200/80 bg-white shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-100 px-6 py-4">
        <div className="flex items-center gap-4">
          <button onClick={onBack} className="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-300 text-slate-500 transition-colors hover:bg-slate-100" title="Back">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
          </button>
          <div>
            <h2 className="text-base font-semibold text-slate-900">Audience</h2>
            <p className="mt-0.5 text-xs text-slate-500">{status ? `${status.valid_emails} contacts` : '-'}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {/* Search */}
          <div className="relative">
            <svg className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input value={searchQ} onChange={e => onSearch(e.target.value)} placeholder="Search contacts..."
              className="w-56 rounded-xl border border-slate-300 bg-slate-50 py-2 pl-9 pr-3 text-sm text-slate-700 placeholder-slate-400 transition-colors focus:border-blue-400 focus:bg-white focus:outline-none" />
          </div>
          {/* Upload */}
          <input type="file" accept=".xls,.xlsx,.csv" onChange={onUpload} style={{display:'none'}} id="audience-upload" />
          {onAddClick && (
            <button onClick={onAddClick}
              className="inline-flex items-center gap-1.5 rounded-xl bg-[#0056b3] px-3.5 py-2 text-xs font-semibold text-white shadow-sm transition-all hover:bg-[#003d7a] active:scale-[0.97]">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              Add
            </button>
          )}
          <label htmlFor="audience-upload" className="inline-flex cursor-pointer items-center gap-1.5 rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-xs font-medium text-slate-600 shadow-sm transition-colors hover:bg-slate-50">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
            Upload
          </label>
        </div>
      </div>

      {/* Filter tabs */}
      <div className="flex items-center gap-1 border-b border-slate-100 px-6 py-2">
        {(['all', 'pending', 'sent'] as const).map((f: 'all' | 'pending' | 'sent') => (
          <button key={f} onClick={() => onFilterChange(f)}
            className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${filter === f ? 'bg-slate-100 text-slate-800' : 'text-slate-400 hover:text-slate-600'}`}>
            {f === 'all' ? 'All' : f === 'pending' ? '⏳ Pending' : '✅ Sent'}
          </button>
        ))}
      </div>

      {/* Content */}
      {loading ? (
        <div className="space-y-3 px-6 py-8">
          {[1,2,3,4,5].map(i => (
            <div key={i} className="flex items-center gap-4 animate-pulse">
              <div className="h-4 w-4 rounded bg-slate-200" />
              <div className="h-4 flex-1 rounded bg-slate-200" />
              <div className="h-4 w-48 rounded bg-slate-200" />
              <div className="h-4 w-32 rounded bg-slate-200" />
              <div className="h-6 w-20 rounded-full bg-slate-200" />
            </div>
          ))}
        </div>
      ) : contacts.length === 0 ? (
        <div className="flex flex-col items-center justify-center px-6 py-16">
          <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-100">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="1.5" strokeLinecap="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          </div>
          <p className="text-sm font-medium text-slate-700">No contacts yet</p>
          <p className="mt-1 text-xs text-slate-400">Upload an XLS or CSV file to add contacts</p>
          <label htmlFor="audience-upload" className="mt-4 inline-flex cursor-pointer items-center gap-1.5 rounded-xl bg-[#0056b3] px-4 py-2 text-sm font-semibold text-white shadow-sm transition-all hover:bg-[#003d7a]">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
            Upload File
          </label>
        </div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm table-fixed">
              <thead>
                <tr className="border-b border-slate-100 text-xs font-semibold uppercase tracking-wider text-slate-500">
                  <th className="sticky top-0 bg-white px-4 py-3.5 w-10">
                  <input type="checkbox"
                    checked={(()=>{
                      const limit=Math.min(status?.daily_limit||contacts.length, contacts.length)
                      const pendingIndices = contacts.slice(0, limit).reduce<number[]>((acc,c,i)=>{
                        if(c.status!=='sent' || c.email==='alams.kombet@gmail.com' || c.email==='alams.kombet@yahoo.com') acc.push(i)
                        return acc
                      },[])
                      return pendingIndices.length>0 && pendingIndices.every(i=>selectedIdx.has(i))
                    })()}
                    onChange={onSelectAll}
                    className="accent-[#0056b3] h-4 w-4 rounded border-slate-300" />
                  </th>
                  <th className="sticky top-0 bg-white px-4 py-3.5 w-[160px] min-w-[120px]">Name</th>
                  <th className="sticky top-0 bg-white px-4 py-3.5 w-[160px] min-w-[120px]">Email</th>
                  <th className="sticky top-0 bg-white px-4 py-3.5 w-[140px] min-w-[100px]">Company</th>
                  <th className="sticky top-0 bg-white px-4 py-3.5 w-20">Status</th>
                  <th className="sticky top-0 bg-white px-4 py-3.5 w-40"></th>
                </tr>
              </thead>
              <tbody>
                {pageContacts.map((c, idx) => {
                  const origIdx = contacts.indexOf(c);
                  return <tr key={origIdx} className={`border-b border-slate-50 transition-colors ${selectedIdx.has(origIdx) ? 'bg-blue-50/40' : 'hover:bg-slate-50'}`}>
                    <td className="px-4 py-3.5"><input type="checkbox" checked={selectedIdx.has(origIdx)} onChange={() => onToggle(origIdx)} className="accent-[#0056b3] h-4 w-4 rounded border-slate-300" /></td>
                    <td className="px-4 py-3.5 font-medium text-slate-900 truncate max-w-[200px]">{c.name}</td>
                    <td className="px-4 py-3.5 text-slate-600 truncate max-w-[250px]">{c.email}</td>
                    <td className="px-4 py-3.5 text-slate-500 truncate max-w-[180px]">{c.company}</td>
                    <td className="px-4 py-3.5">
                      {c.status === 'sent' ? (
                        <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700 ring-1 ring-emerald-200">
                          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                          Sent
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700 ring-1 ring-amber-200">
                          <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
                          Pending
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3.5 whitespace-nowrap">
                      <div className="flex items-center gap-1">
                        <button onClick={() => onEdit(origIdx, c)}
                          className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-600 shadow-sm transition-all hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700 active:scale-[0.95] whitespace-nowrap">
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                          Edit
                        </button>
                        <button onClick={() => onDelete(c.email)}
                          className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-medium text-red-400 shadow-sm transition-all hover:border-red-200 hover:bg-red-50 hover:text-red-600 active:scale-[0.95] whitespace-nowrap">
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                })}
              </tbody>
            </table>
          </div>
          {/* Footer */}
          <div className="flex items-center justify-between rounded-b-2xl border-t border-slate-100 bg-slate-50/50 px-6 py-3">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <span>Show</span>
                <select value={pageSize} onChange={e => { setPageSize(Number(e.target.value)); setPage(0) }}
                  className="rounded-md border border-slate-200 bg-white px-2 py-1 text-xs font-medium text-slate-600 focus:outline-none">
                  <option value={10}>10</option>
                  <option value={20}>20</option>
                  <option value={30}>30</option>
                </select>
                <span>per page</span>
              </div>
              <span className="text-xs text-slate-400">
                {filtered.length} contact{filtered.length !== 1 ? 's' : ''} · {selectedIdx.size} selected
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1 mr-2">
                <button onClick={() => setPage(p => Math.max(0, p - 1))} disabled={safePage === 0}
                  className="rounded-md border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-500 transition-colors hover:bg-slate-100 disabled:opacity-30 disabled:cursor-not-allowed">
                  Prev
                </button>
                <span className="text-xs text-slate-400 mx-1">{safePage + 1}/{totalPages}</span>
                <button onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))} disabled={safePage === totalPages - 1}
                  className="rounded-md border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-500 transition-colors hover:bg-slate-100 disabled:opacity-30 disabled:cursor-not-allowed">
                  Next
                </button>
              </div>
              <button onClick={onReview} disabled={selectedIdx.size === 0}
                className="inline-flex items-center gap-1.5 rounded-lg bg-[#0056b3] px-4 py-2 text-xs font-semibold text-white shadow-sm transition-all hover:bg-[#003d7a] active:scale-[0.97] disabled:opacity-40 disabled:cursor-not-allowed">
                Review &amp; Send ({selectedIdx.size})
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
