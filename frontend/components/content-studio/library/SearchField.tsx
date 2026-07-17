'use client'

import { Search } from 'lucide-react'

type SearchFieldProps = {
  value: string
  onChange: (value: string) => void
}

export default function SearchField({ value, onChange }: SearchFieldProps) {
  return (
    <div className="relative flex items-center">
      <Search size={18} className="absolute left-4 text-slate-400" />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Search by filename or topic..."
        className="h-12 w-full rounded-2xl border border-slate-200/80 bg-white pl-11 pr-4 text-sm text-slate-900 placeholder-slate-400 shadow-[0_8px_20px_rgba(15,23,42,0.04)] outline-none transition-colors focus:border-[#6D5DFC] focus:ring-2 focus:ring-[#6D5DFC]/10"
      />
    </div>
  )
}
