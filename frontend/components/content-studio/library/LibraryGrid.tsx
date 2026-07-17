'use client'

import type { LibraryItem } from './mockLibraryItems'
import ProjectCard from './ProjectCard'

type LibraryGridProps = {
  items: LibraryItem[]
}

export default function LibraryGrid({ items }: LibraryGridProps) {
  if (items.length === 0) {
    return (
      <div className="flex min-h-[200px] items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white/50">
        <p className="text-sm font-medium text-slate-500">
          No projects match your search.
        </p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
      {items.map((item) => (
        <ProjectCard key={item.id} item={item} />
      ))}
    </div>
  )
}
