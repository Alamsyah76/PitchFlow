import React from 'react'

type Props = { left: React.ReactNode; center: React.ReactNode; right: React.ReactNode }

export default function ThreeColumnLayout({ left, center, right }: Props) {
  return (
    <div className="min-h-screen bg-slate-50 font-sans leading-relaxed text-slate-800">
      <header className="px-6 py-6 border-b bg-transparent">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-white rounded-full shadow-sm flex items-center justify-center border border-slate-200">AI</div>
            <h1 className="text-xl font-semibold">Content Engine</h1>
          </div>
          <div className="text-sm text-slate-500">Enterprise • Dashboard</div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8 grid grid-cols-12 gap-6">
        <aside className="col-span-3 p-6 bg-white border border-slate-200/80 shadow-sm rounded-xl">{left}</aside>
        <section className="col-span-6 p-6 bg-white border border-slate-200/80 shadow-sm rounded-xl">{center}</section>
        <aside className="col-span-3 p-6 bg-white border border-slate-200/80 shadow-sm rounded-xl">{right}</aside>
      </main>
    </div>
  )
}
