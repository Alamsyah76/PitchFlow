'use client'

import { useState, useRef, useEffect } from 'react'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8027'

type Message = { role: 'user' | 'bot'; text: string }

export default function ChatBot() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    { role: 'bot', text: 'Halo! Ada yang bisa saya bantu tentang PitchFlow?' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  async function handleSend() {
    const msg = input.trim()
    if (!msg || loading) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', text: msg }])
    setLoading(true)
    try {
      const res = await fetch(`${API}/api/chatbot/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
      })
      const json = await res.json()
      if (json.success) {
        setMessages(prev => [...prev, { role: 'bot', text: json.data.reply }])
      } else {
        setMessages(prev => [...prev, { role: 'bot', text: json.message || 'Maaf, terjadi kesalahan.' }])
      }
    } catch {
      setMessages(prev => [...prev, { role: 'bot', text: 'Gagal terhubung ke server.' }])
    }
    setLoading(false)
  }

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Chat button */}
      {!open && (
        <button onClick={() => setOpen(true)}
          className="flex h-14 w-14 items-center justify-center overflow-hidden rounded-full shadow-lg hover:brightness-110 transition-all"
          title="Tanya PitchFlow">
          <img src="/pitchflow.png" alt="Chat" className="h-full w-full object-cover" />
        </button>
      )}

      {/* Chat window */}
      {open && (
        <div className="flex h-[500px] w-[380px] flex-col rounded-2xl border border-slate-200 bg-white shadow-2xl">
          {/* Header */}
          <div className="flex items-center justify-between rounded-t-2xl bg-gradient-to-r from-[#0056b3] to-[#003d7a] px-4 py-3 text-white">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white/20">
                <img src="/pitchflow.png" alt="P" className="h-6 w-6 rounded-full object-cover" />
              </div>
              <div>
                <div className="text-sm font-semibold">PitchFlow Assistant</div>
                <div className="text-[10px] text-white/70">Content Generation Platform</div>
              </div>
            </div>
            <button onClick={() => setOpen(false)} className="rounded-lg p-1 hover:bg-white/10">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                m.role === 'user'
                  ? 'bg-gradient-to-r from-[#0056b3] to-[#003d7a] text-white rounded-br-md'
                  : 'bg-slate-100 text-slate-700 rounded-bl-md'
                }`}>
                {m.text.split('\n').map((line, j) => (
                  <p key={j} className={line.startsWith('- ') ? 'ml-3' : line.match(/^\d+\. /) ? 'ml-3' : ''}>
                    {line || '\u00A0'}
                  </p>
                ))}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="rounded-2xl rounded-bl-md bg-slate-100 px-4 py-2.5 text-sm text-slate-500">
                  <span className="animate-pulse">Mengetik...</span>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="border-t border-slate-100 p-3">
            <div className="flex gap-2">
              <input value={input} onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSend()}
                placeholder="Tanya sesuatu..."
                className="flex-1 rounded-xl border border-slate-300 px-4 py-2 text-sm outline-none focus:border-blue-400"
              />
              <button onClick={handleSend} disabled={loading || !input.trim()}
                className="flex items-center justify-center rounded-xl bg-gradient-to-r from-[#0056b3] to-[#003d7a] px-3 py-2 text-white hover:brightness-110 disabled:opacity-50">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m22 2-7 20-4-9-9-4Z"/></svg>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
