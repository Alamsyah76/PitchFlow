import ChatBot from '../components/ChatBot'
import UsageBadge from '../components/UsageBadge'
import { useState, useEffect } from 'react'
import Link from 'next/link'

const FEATURES = [
  { icon: '📄', title: 'PDF to Content', desc: 'Upload PDF teknis apapun menjadi caption LinkedIn, email, dan gambar dalam 1 klik.' },
  { icon: '🎯', title: 'RAG Grounded', desc: 'Setiap konten diverifikasi terhadap dokumen asli. Zero hallucination.' },
  { icon: '🤖', title: 'AI-ish Filter', desc: '80+ frasa AI diblokir. Output natural seperti manusia. Softselling, bukan template.' },
  { icon: '🖼️', title: 'Image Storytelling', desc: 'Generate gambar dari konten via AI. Scene plus judul dan 3 poin utama. Siap upload.' },
  { icon: '🧠', title: 'Dynamic Persona', desc: 'Persona otomatis sesuai industri — IT, Finance, HR, Kesehatan, dan lainnya.' },
  { icon: '📦', title: 'Export ZIP', desc: 'Download hasil sebagai ZIP. Tidak ada metadata. File Anda milik Anda.' },
]

const STEPS = [
  { num: '01', title: 'Upload PDF', desc: 'Upload file PDF produk, brosur, atau dokumen teknis Anda.' },
  { num: '02', title: 'Generate', desc: 'Sistem otomatis buat topic, caption 3 paragraf, hashtag, dan gambar.' },
  { num: '03', title: 'Download & Post', desc: 'Download ZIP atau copy langsung ke LinkedIn. Siap publikasi.' },
]

const PRICING = [
  {
    name: 'Free', price: 'Rp 0', period: '',
    konten: '3 file/bulan', image: '1x trial', email: false, chat: '3/hari', library: false,
    cta: 'Mulai Gratis', highlight: false
  },
  {
    name: 'Basic', price: 'Rp 49rb', period: '/bulan',
    konten: '20 file/bulan', image: 'Standard', email: false, chat: '20/hari', library: '2/industri',
    cta: 'Langganan', highlight: false
  },
  {
    name: 'Bisnis', price: 'Rp 149rb', period: '/bulan',
    konten: '100 file/bulan', image: '1024×1024', email: '100 kontak', chat: '100/hari', library: '5/industri',
    cta: 'Langganan', highlight: true
  },
  {
    name: 'Pro', price: 'Rp 299rb', period: '/bulan',
    konten: 'Unlimited', image: '1024×1024', email: 'Unlimited', chat: 'Unlimited', library: 'Unlimited',
    cta: 'Hubungi Kami', highlight: false
  },
]

const INDUSTRIES = ['IT & Cybersecurity', 'Perbankan & Finance', 'Kesehatan & Medis', 'Manufaktur & Otomotif', 'Distribusi & Logistik', 'Energi & Migas', 'Pendidikan & Riset', 'Telekomunikasi']

export default function LandingPage() {
  const [menuOpen, setMenuOpen] = useState(false)

  // Scroll ke atas setiap refresh
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
              <Link href="/content-studio" className="mt-2 rounded-lg bg-gradient-to-r from-[#0056b3] to-[#003d7a] px-4 py-2 text-center font-semibold text-white" onClick={() => setMenuOpen(false)}>Mulai Gratis</Link>
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
            Satu Dokumen Jadi<br />
            <span className="bg-gradient-to-r from-blue-500 to-indigo-600 bg-clip-text text-transparent">Konten Siap Publikasi</span>
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-base leading-relaxed text-slate-500 md:text-lg">
            Upload PDF teknis apapun. Dapatkan caption LinkedIn, email marketing, 
            dan gambar dalam 1 klik. Grounded ke dokumen, zero hallucination, siap pakai.
          </p>
          <div className="mt-6 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
            <Link href="/content-studio" className="rounded-xl bg-gradient-to-r from-[#0056b3] to-[#003d7a] px-8 py-3.5 text-base font-semibold text-white shadow-lg shadow-blue-200 hover:shadow-xl transition-shadow">
              Coba Gratis
            </Link>
            <a href="#features" className="rounded-xl border border-slate-300 bg-white px-8 py-3.5 text-base font-medium text-slate-700 hover:bg-slate-50 transition-colors">
              Lihat Fitur
            </a>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="border-t border-slate-100 bg-slate-50/50 pt-10 pb-10 md:pt-12 md:pb-12">
        <div className="mx-auto max-w-5xl px-5">
          <h2 className="text-center text-2xl font-bold md:text-3xl">Cara Kerja</h2>
          <p className="mx-auto mt-3 max-w-xl text-center text-slate-500">3 langkah sederhana dari dokumen ke konten siap publikasi.</p>
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
          <h2 className="text-center text-2xl font-bold md:text-3xl">Fitur Utama</h2>
          <p className="mx-auto mt-3 max-w-xl text-center text-slate-500">Apa yang membuat PitchFlow berbeda dari tools lain.</p>
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
          <h2 className="text-center text-2xl font-bold md:text-3xl">Kenapa PitchFlow Berbeda</h2>
          <p className="mx-auto mt-3 max-w-xl text-center text-slate-500">Tools AI umum butuh prompt dan trial-error. PitchFlow langsung jadi dari dokumen Anda.</p>
          <div className="mt-10 overflow-hidden rounded-2xl border border-slate-200/70 bg-white shadow-sm">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50/80">
                  <th className="px-5 py-4 font-semibold text-slate-700">Fitur</th>
                  <th className="px-5 py-4 font-semibold text-blue-600">PitchFlow</th>
                  <th className="px-5 py-4 font-semibold text-slate-400">Tools AI Umum</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-slate-100">
                  <td className="px-5 py-4 font-medium text-slate-700">Cara kerja</td>
                  <td className="px-5 py-4 text-slate-600">Upload PDF → konten jadi otomatis</td>
                  <td className="px-5 py-4 text-slate-400">Harus bikin prompt, trial-error, refine</td>
                </tr>
                <tr className="border-b border-slate-100 bg-slate-50/30">
                  <td className="px-5 py-4 font-medium text-slate-700">Keakuratan</td>
                  <td className="px-5 py-4 text-slate-600">RAG grounded — setiap klaim diverifikasi ke dokumen asli</td>
                  <td className="px-5 py-4 text-slate-400">Halusinasi tinggi, sering mengarang fakta</td>
                </tr>
                <tr className="border-b border-slate-100">
                  <td className="px-5 py-4 font-medium text-slate-700">Output AI-ish</td>
                  <td className="px-5 py-4 text-slate-600">80+ frasa AI diblokir + filter naturalisasi</td>
                  <td className="px-5 py-4 text-slate-400">Mudah dikenali sebagai hasil AI</td>
                </tr>
                <tr className="border-b border-slate-100 bg-slate-50/30">
                  <td className="px-5 py-4 font-medium text-slate-700">Persona</td>
                  <td className="px-5 py-4 text-slate-600">Dinamis — otomatis sesuai industri dokumen</td>
                  <td className="px-5 py-4 text-slate-400">Harus manual ganti prompt per industri</td>
                </tr>
                <tr className="border-b border-slate-100">
                  <td className="px-5 py-4 font-medium text-slate-700">Format output</td>
                  <td className="px-5 py-4 text-slate-600">LinkedIn caption + email + gambar + ZIP</td>
                  <td className="px-5 py-4 text-slate-400">Teks saja, gambar dan email terpisah</td>
                </tr>
                <tr className="border-b border-slate-100 bg-slate-50/30">
                  <td className="px-5 py-4 font-medium text-slate-700">Export</td>
                  <td className="px-5 py-4 text-slate-600">ZIP — topic, konten, image, tanpa metadata</td>
                  <td className="px-5 py-4 text-slate-400">Copy-paste manual atau format proprietary</td>
                </tr>
                <tr>
                  <td className="px-5 py-4 font-medium text-slate-700">Bahasa Indonesia</td>
                  <td className="px-5 py-4 text-slate-600">Native, dengan AVOID list bahasa Indonesia</td>
                  <td className="px-5 py-4 text-slate-400">Inggris dulu, Indonesia seadanya</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p className="mt-4 text-center text-sm text-slate-400">PitchFlow dirancang khusus untuk profesional Marketing & Sales di Indonesia yang butuh konten berkualitas dari dokumen teknis tanpa ribet.</p>
        </div>
      </section>

      {/* USE CASES */}
      <section className="border-t border-slate-100 bg-slate-50/50 pt-10 pb-10 md:pt-12 md:pb-10">
        <div className="mx-auto max-w-5xl px-5 text-center">
          <h2 className="text-2xl font-bold md:text-3xl">Untuk Semua Industri</h2>
          <p className="mx-auto mt-3 max-w-2xl text-slate-500">
            Terbukti di berbagai sektor. Dari PDF teknis apapun konten siap pakai.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-2.5">
            {INDUSTRIES.map((ind, i) => (
              <span key={i} className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm">{ind}</span>
            ))}
          </div>
          <p className="mt-6 text-sm text-slate-400">Sistem berlaku universal untuk semua PDF.</p>
        </div>
      </section>

      {/* PRICING */}
      <section id="pricing" className="pt-10 pb-16 md:pt-12 md:pb-20">
        <div className="mx-auto max-w-5xl px-5">
          <h2 className="text-center text-2xl font-bold md:text-3xl">Pilih Paket</h2>
          <p className="mx-auto mt-3 max-w-xl text-center text-slate-500">Mulai gratis. Upgrade kapan saja.</p>
          <div className="mt-10 grid gap-6 md:grid-cols-4">
            {PRICING.map((p, i) => (
              <div key={i} className="flex flex-col">
                {p.highlight && <span className="-mb-3 z-10 mx-auto inline-block rounded-full bg-blue-500 px-3 py-0.5 text-xs font-medium text-white">Paling Populer</span>}
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
