import ChatBot from '../components/ChatBot'
import UsageBadge from '../components/UsageBadge'
import { useState, useEffect } from 'react'
import Link from 'next/link'

const FEATURES = [
  { icon: '📄', title: 'PDF to Content', desc: 'Upload any technical PDF and turn it into LinkedIn captions, emails, and images in one click.' },
  { icon: '🎯', title: 'RAG Grounded', desc: 'Every piece of content is verified against your original document. Zero hallucination.' },
  { icon: '🤖', title: 'AI-ish Filter', desc: '80+ AI phrases are blocked. Output sounds human, not templated. Soft-selling, not spam.' },
  { icon: '🖼️', title: 'Image Storytelling', desc: 'Generate images from your content via AI. Scene plus title and 3 key points. Ready to post.' },
  { icon: '🧠', title: 'Dynamic Persona', desc: 'Persona adapts automatically to the industry — IT, Finance, HR, Healthcare, and more.' },
  { icon: '📦', title: 'Export ZIP', desc: 'Download results as a ZIP. No metadata. Your files belong to you.' },
]

const STEPS = [
  { num: '01', title: 'Upload PDF', desc: 'Upload your product PDF, brochure, or technical document.' },
  { num: '02', title: 'Generate', desc: 'The system automatically creates topics, 3-paragraph captions, hashtags, and images.' },
  { num: '03', title: 'Download & Post', desc: 'Download the ZIP or copy directly to LinkedIn. Ready to publish.' },
]

const PRICING = [
  {
    name: 'Free', price: 'Rp 0', period: '',
    konten: '3 files/month', image: '1x trial', email: false, chat: '3/day', library: false,
    cta: 'Start Free', highlight: false
  },
  {
    name: 'Basic', price: 'Rp 49k', period: '/month',
    konten: '20 files/month', image: 'Standard', email: false, chat: '20/day', library: '2/industry',
    cta: 'Subscribe', highlight: false
  },
  {
    name: 'Business', price: 'Rp 149k', period: '/month',
    konten: '100 files/month', image: '1024×1024', email: '100 contacts', chat: '100/day', library: '5/industry',
    cta: 'Subscribe', highlight: true
  },
  {
    name: 'Pro', price: 'Rp 299k', period: '/month',
    konten: 'Unlimited', image: '1024×1024', email: 'Unlimited', chat: 'Unlimited', library: 'Unlimited',
    cta: 'Contact Us', highlight: false
  },
]

const INDUSTRIES = ['IT & Cybersecurity', 'Banking & Finance', 'Healthcare & Medical', 'Manufacturing & Automotive', 'Distribution & Logistics', 'Energy & Oil Gas', 'Education & Research', 'Telecommunications']

export default function LandingPage() {
  const [menuOpen, setMenuOpen] = useState(false)

  // Scroll to top on every refresh
  useEffect(() => {
    window.scrollTo(0, 0)
    if (window.location.hash) {
      history.replaceState(null, '', window.location.pathname)
    }
  }, [])

  return (
    <div className="min-h-screen bg-white text-slate-900">
      {/* NAVBAR */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-slate-200/60 bg-white/90 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-3.5">
          <Link href="/" className="flex items-center gap-2">
            <img src="/pitchflow.png" alt="PitchFlow" className="h-14 w-auto" />
            <div className="flex flex-col">
              <span className="text-lg font-bold tracking-tight leading-none">PitchFlow</span>
              <span className="text-[10px] font-medium text-slate-400 tracking-wide leading-none">Content Generation Platform</span>
            </div>
          </Link>
          <div className="hidden items-center gap-6 text-sm font-medium text-slate-600 md:flex">
            <a href="#features">Features</a>
            <a href="#pricing">Pricing</a>
            <Link href="/content-studio">Content Studio</Link>
            <Link href="/email-campaign">Email Campaign</Link>
            <Link href="/dashboard">Dashboard</Link>
            <Link href="/settings">Settings</Link>
            <Link href="/auth" className="rounded-lg bg-gradient-to-r from-[#0056b3] to-[#003d7a] px-4 py-2 text-sm font-semibold text-white shadow-sm hover:shadow-md transition-shadow">
              Login
            </Link>
          </div>
          <button onClick={() => setMenuOpen(!menuOpen)} className="flex items-center justify-center rounded-lg border border-slate-200 p-2 md:hidden">
            <span className="text-sm">{menuOpen ? 'X' : '='}</span>
          </button>
        </div>
        {menuOpen && (
          <div className="border-t border-slate-100 bg-white px-5 py-4 md:hidden">
            <div className="flex flex-col gap-3 text-sm font-medium text-slate-600">
              <a href="#features" onClick={() => setMenuOpen(false)}>Features</a>
              <a href="#pricing" onClick={() => setMenuOpen(false)}>Pricing</a>
              <Link href="/content-studio" onClick={() => setMenuOpen(false)}>Content Studio</Link>
              <Link href="/email-campaign" onClick={() => setMenuOpen(false)}>Email Campaign</Link>
              <Link href="/dashboard" onClick={() => setMenuOpen(false)}>Dashboard</Link>
              <Link href="/settings" onClick={() => setMenuOpen(false)}>Settings</Link>
              <Link href="/content-studio" className="mt-2 rounded-lg bg-gradient-to-r from-[#0056b3] to-[#003d7a] px-4 py-2 text-center font-semibold text-white" onClick={() => setMenuOpen(false)}>Start Free</Link>
            </div>
          </div>
        )}
      </nav>

      {/* HERO */}
      <section className="relative overflow-hidden pt-24 pb-8 md:pt-[88px] md:pb-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.12),transparent_40%),radial-gradient(circle_at_bottom_right,rgba(99,102,241,0.08),transparent_40%)]" />
        <div className="relative mx-auto max-w-5xl px-5 text-center">
          <div className="inline-flex items-center justify-center rounded-2xl bg-white p-3 shadow-sm mb-3">
            <img src="/pitchflow.png" alt="PitchFlow" className="h-52 w-auto block" />
          </div>
          <h1 className="text-4xl font-bold leading-tight tracking-tight md:text-5xl lg:text-6xl">
            One Document In,<br />
            <span className="bg-gradient-to-r from-blue-500 to-indigo-600 bg-clip-text text-transparent">Publish-Ready Content Out</span>
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-base leading-relaxed text-slate-500 md:text-lg">
            Upload any technical PDF. Get LinkedIn captions, marketing emails,
            and images in one click. Grounded to your document, zero hallucination, ready to use.
          </p>
          <div className="mt-6 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
            <Link href="/content-studio" className="rounded-xl bg-gradient-to-r from-[#0056b3] to-[#003d7a] px-8 py-3.5 text-base font-semibold text-white shadow-lg shadow-blue-200 hover:shadow-xl transition-shadow">
              Try It Free
            </Link>
            <a href="#features" className="rounded-xl border border-slate-300 bg-white px-8 py-3.5 text-base font-medium text-slate-700 hover:bg-slate-50 transition-colors">
              See Features
            </a>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="border-t border-slate-100 bg-slate-50/50 pt-10 pb-10 md:pt-12 md:pb-12">
        <div className="mx-auto max-w-5xl px-5">
          <h2 className="text-center text-2xl font-bold md:text-3xl">How It Works</h2>
          <p className="mx-auto mt-3 max-w-xl text-center text-slate-500">3 simple steps from document to publish-ready content.</p>
          <div className="mt-10 grid gap-6 md:grid-cols-3">
            {STEPS.map((s, i) => (
              <div key={i} className="rounded-2xl border border-slate-200/70 bg-white p-6 shadow-sm">
                <span className="text-2xl font-bold text-blue-500">{s.num}</span>
                <h3 className="mt-3 text-lg font-semibold">{s.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-500">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section id="features" className="pt-10 pb-10 md:pt-12 md:pb-12">
        <div className="mx-auto max-w-5xl px-5">
          <h2 className="text-center text-2xl font-bold md:text-3xl">Key Features</h2>
          <p className="mx-auto mt-3 max-w-xl text-center text-slate-500">What makes PitchFlow different from other tools.</p>
          <div className="mt-10 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map((f, i) => (
              <div key={i} className="rounded-2xl border border-slate-200/70 bg-white p-6 shadow-sm transition-shadow hover:shadow-md">
                <span className="text-2xl">{f.icon}</span>
                <h3 className="mt-3 text-base font-semibold">{f.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-500">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* COMPARISON */}
      <section className="py-10 md:py-12">
        <div className="mx-auto max-w-5xl px-5">
          <h2 className="text-center text-2xl font-bold md:text-3xl">Why PitchFlow Stands Out</h2>
          <p className="mx-auto mt-3 max-w-xl text-center text-slate-500">Generic AI tools require prompts and trial-and-error. PitchFlow goes straight from your document to done.</p>
          <div className="mt-10 overflow-hidden rounded-2xl border border-slate-200/70 bg-white shadow-sm">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50/80">
                  <th className="px-5 py-4 font-semibold text-slate-700">Feature</th>
                  <th className="px-5 py-4 font-semibold text-blue-600">PitchFlow</th>
                  <th className="px-5 py-4 font-semibold text-slate-400">Generic AI Tools</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-slate-100">
                  <td className="px-5 py-4 font-medium text-slate-700">Workflow</td>
                  <td className="px-5 py-4 text-slate-600">Upload PDF → content ready automatically</td>
                  <td className="px-5 py-4 text-slate-400">Write prompts, trial-and-error, refine</td>
                </tr>
                <tr className="border-b border-slate-100 bg-slate-50/30">
                  <td className="px-5 py-4 font-medium text-slate-700">Accuracy</td>
                  <td className="px-5 py-4 text-slate-600">RAG grounded — every claim verified against the source document</td>
                  <td className="px-5 py-4 text-slate-400">High hallucination, often fabricates facts</td>
                </tr>
                <tr className="border-b border-slate-100">
                  <td className="px-5 py-4 font-medium text-slate-700">AI-ish Output</td>
                  <td className="px-5 py-4 text-slate-600">80+ AI phrases blocked + naturalization filter</td>
                  <td className="px-5 py-4 text-slate-400">Easily recognizable as AI-generated</td>
                </tr>
                <tr className="border-b border-slate-100 bg-slate-50/30">
                  <td className="px-5 py-4 font-medium text-slate-700">Persona</td>
                  <td className="px-5 py-4 text-slate-600">Dynamic — adapts automatically to the document's industry</td>
                  <td className="px-5 py-4 text-slate-400">Manual prompt changes per industry</td>
                </tr>
                <tr className="border-b border-slate-100">
                  <td className="px-5 py-4 font-medium text-slate-700">Output format</td>
                  <td className="px-5 py-4 text-slate-600">LinkedIn caption + email + image + ZIP</td>
                  <td className="px-5 py-4 text-slate-400">Text only, images and emails separate</td>
                </tr>
                <tr className="border-b border-slate-100 bg-slate-50/30">
                  <td className="px-5 py-4 font-medium text-slate-700">Export</td>
                  <td className="px-5 py-4 text-slate-600">ZIP — topics, content, images, no metadata</td>
                  <td className="px-5 py-4 text-slate-400">Manual copy-paste or proprietary formats</td>
                </tr>
                <tr>
                  <td className="px-5 py-4 font-medium text-slate-700">Local Language</td>
                  <td className="px-5 py-4 text-slate-600">Native, with AVOID list for natural phrasing</td>
                  <td className="px-5 py-4 text-slate-400">English first, local language as an afterthought</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p className="mt-4 text-center text-sm text-slate-400">PitchFlow is built for Marketing &amp; Sales professionals who need quality content from technical documents — without the hassle.</p>
        </div>
      </section>

      {/* USE CASES */}
      <section className="border-t border-slate-100 bg-slate-50/50 pt-10 pb-10 md:pt-12 md:pb-10">
        <div className="mx-auto max-w-5xl px-5 text-center">
          <h2 className="text-2xl font-bold md:text-3xl">Built for Every Industry</h2>
          <p className="mx-auto mt-3 max-w-2xl text-slate-500">
            Proven across sectors. Publish-ready content from any technical PDF.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-2.5">
            {INDUSTRIES.map((ind, i) => (
              <span key={i} className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm">{ind}</span>
            ))}
          </div>
          <p className="mt-6 text-sm text-slate-400">The system works universally across all PDFs.</p>
        </div>
      </section>

      {/* PRICING */}
      <section id="pricing" className="pt-10 pb-16 md:pt-12 md:pb-20">
        <div className="mx-auto max-w-5xl px-5">
          <h2 className="text-center text-2xl font-bold md:text-3xl">Choose Your Plan</h2>
          <p className="mx-auto mt-3 max-w-xl text-center text-slate-500">Start free. Upgrade anytime.</p>
          <div className="mt-10 grid gap-6 md:grid-cols-4">
            {PRICING.map((p, i) => (
              <div key={i} className="flex flex-col">
                {p.highlight && <span className="-mb-3 z-10 mx-auto inline-block rounded-full bg-blue-500 px-3 py-0.5 text-xs font-medium text-white">Most Popular</span>}
                <div className={`rounded-2xl border p-6 shadow-sm flex flex-col flex-1 ${p.highlight ? 'border-blue-200 bg-gradient-to-b from-blue-50 to-white shadow-blue-100 ring-1 ring-blue-200' : 'border-slate-200/70 bg-white'}`}>
                <h3 className="text-lg font-semibold">{p.name}</h3>
                <div className="mt-2 flex items-baseline gap-1">
                  <span className="text-3xl font-bold">{p.price}</span>
                  {p.period && <span className="text-sm text-slate-400">{p.period}</span>}
                </div>
                <ul className="mt-5 space-y-2.5 text-sm text-slate-600 flex-1">
                  <li className="flex items-center gap-2">{'\u2705'} Content Studio</li>
                  <li className="flex items-center gap-2">{'\u2705'} {p.konten}</li>
                  <li className="flex items-center gap-2">{'\u2705'} Image {p.image}</li>
                  {p.library && <li className="flex items-center gap-2">{'\u2705'} Library {p.library}</li>}
                  <li className="flex items-center gap-2">{p.email ? '\u2705' : '\u274C'} Email {p.email || '—'}</li>
                  {!p.library && <li className="flex items-center gap-2">{'\u274C'} Library —</li>}
                </ul>
                <Link href={p.name === 'Pro' ? 'mailto:sales@pitchflow.com' : '/content-studio'} className={`mt-6 flex items-center justify-center rounded-xl py-2.5 text-sm font-semibold transition-colors ${p.highlight ? 'bg-gradient-to-r from-[#0056b3] to-[#003d7a] text-white shadow-sm hover:shadow-md' : 'border border-slate-300 bg-white text-slate-700 hover:bg-slate-50'}`}>
                  {p.cta}
                </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t border-slate-100 bg-slate-50 py-6">
        <div className="mx-auto max-w-5xl px-5">
          <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
            <div className="flex items-center gap-2">
              <img src="/pitchflow.png" alt="PitchFlow" className="h-12 w-auto" />
              <div>
                <span className="text-sm font-semibold leading-none">PitchFlow</span>
                <span className="block text-[10px] text-slate-400 leading-none mt-0.5">Content Generation Platform</span>
              </div>
            </div>
            <div className="flex gap-6 text-sm text-slate-500">
              <Link href="/content-studio">Content Studio</Link>
              <a href="#features">Features</a>
              <a href="#pricing">Pricing</a>
            </div>
            <p className="text-xs text-slate-400">{'\u00A9'} 2026 PitchFlow. All rights reserved.</p>
          </div>
        </div>
      </footer>
      <UsageBadge />
      <ChatBot />
    </div>
  )
}
