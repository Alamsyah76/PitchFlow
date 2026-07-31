'use client'
import Link from 'next/link'

export default function ComingSoon({ icon, title, description }: {
  icon: string
  title: string
  description: string
}) {
  return (
    <main className="flex min-h-[60vh] items-center justify-center px-4 py-12">
      <div className="w-full max-w-lg text-center">
        <div className="relative mx-auto flex h-24 w-24 items-center justify-center rounded-3xl bg-gradient-to-br from-[#0056b3] to-[#003d7a] shadow-[0_10px_40px_rgba(0,86,179,0.3)]">
          <span className="text-5xl drop-shadow-sm">{icon}</span>
          <span className="absolute -right-2 -top-2 flex h-8 w-8 items-center justify-center rounded-full bg-emerald-500 text-[10px] font-bold text-white ring-4 ring-white">
            SOON
          </span>
        </div>
        <h1 className="mt-6 text-2xl font-bold tracking-tight text-slate-900">{title}</h1>
        <p className="mx-auto mt-3 max-w-md text-sm leading-relaxed text-slate-500">{description}</p>
        <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Link href="/content-studio" className="rounded-xl bg-gradient-to-r from-[#0056b3] to-[#003d7a] px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-200 transition hover:shadow-xl">
            Open Content Studio
          </Link>
          <Link href="/dashboard" className="rounded-xl border border-slate-300 bg-white px-6 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50">
            View Dashboard
          </Link>
        </div>
      </div>
    </main>
  )
}
