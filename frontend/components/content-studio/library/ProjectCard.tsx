'use client'

import { useState } from 'react'
import { Clock, FileText, ImageIcon } from 'lucide-react'
import type { LibraryItem } from './mockLibraryItems'

type ProjectCardProps = {
  item: LibraryItem
}

function formatTimestamp(iso: string): string {
  const d = new Date(iso)
  return d.toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
  })
}

export default function ProjectCard({ item }: ProjectCardProps) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="group relative overflow-hidden rounded-2xl border border-slate-200/70 bg-white shadow-[0_8px_18px_rgba(15,23,42,0.04)] transition-all hover:shadow-[0_12px_28px_rgba(15,23,42,0.08)]">
      <div className="p-5">
        {/* Header */}
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0 flex-1">
            <h3 className="truncate text-sm font-semibold text-slate-900" title={item.pdf_filename}>
              {item.pdf_filename}
            </h3>
            <p className="mt-1 truncate text-xs text-slate-500" title={item.selected_topic}>
              {item.selected_topic}
            </p>
          </div>
          {item.image_url && (
            <div className="shrink-0">
              <img src={item.image_url} alt="" className="h-16 w-16 rounded-xl border border-slate-100 object-cover" />
            </div>
          )}
        </div>

        {/* Info row */}
        <div className="mt-3 flex items-center gap-3 text-xs text-slate-400">
          <div className="flex items-center gap-1"><FileText size={12} /> {item.caption_text.length} chars</div>
          {item.hashtags?.length > 0 && <div className="flex items-center gap-1">#{item.hashtags.length} tags</div>}
          <div className="flex items-center gap-1"><Clock size={12} /><span>{formatTimestamp(item.timestamp)}</span></div>
        </div>

        {/* Expanded caption */}
        {expanded && item.caption_text && (
          <div className="mt-3 rounded-xl border border-slate-100 bg-slate-50/60 p-3">
            <p className="text-xs leading-relaxed text-slate-600 whitespace-pre-wrap">{item.caption_text}</p>
          </div>
        )}

        {/* Actions */}
        <div className="mt-4 flex items-center gap-2 border-t border-slate-100 pt-4">
          <button
            onClick={() => setExpanded(!expanded)}
            className="inline-flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-[#0056b3] to-[#003d7a] px-3.5 py-2 text-xs font-medium text-white shadow-[0_6px_16px_rgba(0,86,179,0.18)] hover:brightness-110"
          >
            {expanded ? 'Show Less' : 'View Details'}
          </button>
        </div>
      </div>
    </div>
  )
}
