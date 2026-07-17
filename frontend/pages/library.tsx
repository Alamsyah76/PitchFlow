'use client'

import { useState, useMemo, useEffect } from 'react'
import StudioSidebar from '../components/content-studio/StudioSidebar'
import StudioHeader from '../components/content-studio/StudioHeader'
import SearchField from '../components/content-studio/library/SearchField'
import LibraryGrid from '../components/content-studio/library/LibraryGrid'
import { getProjects } from '../lib/workspace-storage'
import { mockLibraryItems } from '../components/content-studio/library/mockLibraryItems'

export default function LibraryRoute() {
  const [searchQuery, setSearchQuery] = useState('')
  const [items, setItems] = useState(mockLibraryItems)
  const [hydrated, setHydrated] = useState(false)

  useEffect(() => {
    getProjects().then(saved => {
      if (saved.length > 0) setItems(saved)
      setHydrated(true)
    })
  }, [])

  const filteredItems = useMemo(() => {
    if (!searchQuery.trim()) return items
    const q = searchQuery.toLowerCase()
    return items.filter(
      (item) =>
        item.pdf_filename.toLowerCase().includes(q) ||
        item.selected_topic.toLowerCase().includes(q),
    )
  }, [searchQuery, items])

  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,#FAFBFF_0%,#F7F8FB_42%,#F5F6FA_100%)] text-slate-950">
      <StudioSidebar activeRoute="/library" />
      <StudioHeader title="Library" />
      <main className="space-y-6 px-4 py-4 md:px-8 md:py-6 lg:ml-[260px] xl:px-10">
        <div className="mx-auto max-w-screen-2xl pb-28">
          <SearchField value={searchQuery} onChange={setSearchQuery} />
          <div className="mt-6">
            <LibraryGrid items={filteredItems} />
          </div>
        </div>
      </main>
    </div>
  )
}
