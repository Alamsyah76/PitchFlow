import React, { useEffect, useState, useRef } from 'react'
import dynamic from 'next/dynamic'
import { Copy, Download } from 'lucide-react'

const RichEditor = dynamic(() => import('./RichEditorTiptap'), { ssr: false })

type Props = {
  draft?: string
  failedPropositions?: { sentence: string; reason: string }[]
  onCopy?: () => void
  onDownload?: () => void
}

export default function ColumnRight({ draft='', failedPropositions=[], onCopy, onDownload }: Props) {
  const [html, setHtml] = useState(draft)
  const editorRef = useRef<any>(null)

  useEffect(()=> setHtml(draft), [draft])

  function handleCopy() {
    try {
      const plain = editorRef.current ? editorRef.current.getText() : html.replace(/<[^>]+>/g, '')
      const withTags = `${plain}\n\n#YourBrand`
      navigator.clipboard.writeText(withTags)
      onCopy?.()
    } catch (e) {
      console.error('Copy failed', e)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Human Editor & Output</h2>
        <div className="flex gap-2">
          <button onClick={handleCopy} className="inline-flex items-center gap-2 bg-slate-900 text-white rounded-lg font-medium px-4 py-2.5 text-sm shadow-sm transition-all">
            <Copy size={16} /> Copy Text
          </button>
          <button onClick={() => onDownload?.()} className="inline-flex items-center gap-2 bg-sky-600 text-white rounded-lg font-medium px-4 py-2.5 text-sm shadow-sm transition-all">
            <Download size={16} /> Download Carousel
          </button>
        </div>
      </div>

      <div>
        <RichEditor value={html} onChange={(v:string)=>setHtml(v)} failedPropositions={failedPropositions} onEditorReady={(ed:any)=>editorRef.current = ed} />
      </div>
    </div>
  )
}
