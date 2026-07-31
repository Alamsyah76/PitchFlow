'use client'
import { useState, useEffect } from 'react'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8042'

type Props = {
  show: boolean
  onClose: () => void
  onImport: (data: { title: string; subject: string; body_html: string; body_text: string; sections: any }) => void
}

type Tab = 'product' | 'blog'

export default function ImportFromWebModal({ show, onClose, onImport }: Props) {
  const [tab, setTab] = useState<Tab>('product')
  const [products, setProducts] = useState<any[]>([])
  const [posts, setPosts] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [selected, setSelected] = useState<any>(null)
  const [preview, setPreview] = useState<any>(null)
  const [previewLoading, setPreviewLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!show) return
    setTab('product')
    setSelected(null)
    setPreview(null)
    setError('')
    fetchProducts()
    fetchPosts()
  }, [show])

  async function fetchProducts() {
    setLoading(true)
    try {
      const r = await fetch(`${API}/api/email-campaign/scrape/products`)
      const d = await r.json()
      if (d.success) setProducts(d.data.products)
    } catch { setError('Failed to load products') }
    setLoading(false)
  }

  async function fetchPosts() {
    try {
      const r = await fetch(`${API}/api/email-campaign/scrape/blog`)
      const d = await r.json()
      if (d.success) setPosts(d.data.posts)
    } catch {}
  }

  async function loadPreview(item: any) {
    setSelected(item)
    setPreviewLoading(true)
    setError('')
    try {
      const endpoint = tab === 'product'
        ? `${API}/api/email-campaign/scrape/product`
        : `${API}/api/email-campaign/scrape/blog-post`
      const r = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: item.url }),
      })
      const d = await r.json()
      if (d.success) setPreview(d.data)
      else setError(d.detail || 'Failed to load content')
    } catch { setError('Network error') }
    setPreviewLoading(false)
  }

  function doImport() {
    if (!preview) return
    const title = preview.title || selected?.title || ''
    onImport({
      title: title.length > 100 ? title.slice(0, 100) : title,
      subject: tab === 'blog' ? title.slice(0, 100) : `Introducing ${title}`,
      body_html: preview.content_html || preview.body_html || '',
      body_text: preview.content_text || preview.body_text || '',
      sections: preview.sections || {},
    })
    onClose()
  }

  if (!show) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <div className="mx-4 w-full max-w-2xl rounded-2xl bg-white shadow-2xl" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <h3 className="text-base font-semibold text-slate-900">Import Content dari Web</h3>
          <button onClick={onClose} type="button" className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-slate-200 px-6">
          <button onClick={() => { setTab('product'); setSelected(null); setPreview(null) }}
            type="button"
            className={`pb-3 pt-4 text-sm font-medium border-b-2 transition-colors ${tab === 'product' ? 'border-[#0056b3] text-[#0056b3]' : 'border-transparent text-slate-500 hover:text-slate-700'}`}>
            📦 Produk
          </button>
          <button onClick={() => { setTab('blog'); setSelected(null); setPreview(null) }}
            type="button"
            className={`ml-6 pb-3 pt-4 text-sm font-medium border-b-2 transition-colors ${tab === 'blog' ? 'border-[#0056b3] text-[#0056b3]' : 'border-transparent text-slate-500 hover:text-slate-700'}`}>
            📝 Blog
          </button>
        </div>

        {/* Body */}
        <div className="max-h-[400px] overflow-y-auto px-6 py-4">
          {error && <p className="mb-3 rounded-lg bg-red-50 px-3 py-2 text-xs text-red-600">{error}</p>}

          {tab === 'product' && (
            <div className="grid grid-cols-2 gap-2">
              {products.map((p: any) => (
                <button key={p.slug} onClick={() => loadPreview(p)} type="button"
                  className={`rounded-xl border px-4 py-3 text-left text-sm transition-all ${
                    selected?.slug === p.slug
                      ? 'border-[#0056b3] bg-blue-50 ring-1 ring-[#0056b3]'
                      : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                  }`}>
                  <div className="font-medium text-slate-900">{p.title}</div>
                  <div className="mt-0.5 text-xs text-slate-400">{p.available ? '✓ Tersedia' : '✗ Tidak tersedia'}</div>
                </button>
              ))}
            </div>
          )}

          {tab === 'blog' && (
            <div className="space-y-1">
              {posts.map((post: any, i: number) => (
                <button key={i} onClick={() => loadPreview(post)} type="button"
                  className={`w-full rounded-xl border px-4 py-3 text-left text-sm transition-all ${
                    selected?.url === post.url
                      ? 'border-[#0056b3] bg-blue-50 ring-1 ring-[#0056b3]'
                      : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                  }`}>
                  <div className="font-medium text-slate-900">{post.title}</div>
                  <div className="mt-0.5 text-xs text-slate-400">{post.date || ''}</div>
                </button>
              ))}
            </div>
          )}

          {/* Preview */}
          {previewLoading && (
            <div className="mt-4 flex items-center justify-center py-8">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-[#0056b3] border-t-transparent" />
              <span className="ml-2 text-sm text-slate-500">Loading content...</span>
            </div>
          )}

          {preview && !previewLoading && (
            <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
              <h4 className="mb-2 text-sm font-semibold text-slate-900">Preview: {preview.title?.slice(0, 80)}</h4>
              <div className="max-h-40 overflow-y-auto rounded-lg bg-white p-3 text-xs leading-relaxed text-slate-600">
                {(preview.content_text || preview.body_text || '').slice(0, 1000)}
              </div>
              <p className="mt-2 text-xs text-slate-400">Konten akan diimport sebagai template baru</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 border-t border-slate-200 px-6 py-4">
          <button onClick={onClose} type="button"
            className="rounded-xl border border-slate-300 bg-white px-5 py-2.5 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-50">
            Cancel
          </button>
          <button onClick={doImport} disabled={!preview} type="button"
            className="rounded-xl bg-gradient-to-r from-[#0056b3] to-[#003d7a] px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:brightness-110 disabled:opacity-40 disabled:cursor-not-allowed">
            Gunakan sebagai Template
          </button>
        </div>
      </div>
    </div>
  )
}
