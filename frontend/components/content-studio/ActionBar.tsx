import { Copy, ImageIcon, Loader2, Sparkles } from 'lucide-react'
import { Button } from '../ui/button'

export interface ActionBarProps {
  hasCaption: boolean
  hasCreativeDirection: boolean
  isCopied: boolean
  isGeneratingCreativeDirection: boolean
  onCopyCaption: () => void
  onGenerateCreativeDirection: () => void
}

export default function ActionBar({
  hasCaption,
  hasCreativeDirection,
  isCopied,
  isGeneratingCreativeDirection,
  onCopyCaption,
  onGenerateCreativeDirection,
}: ActionBarProps) {
  return (
    <div className="rounded-2xl border border-slate-200/80 bg-white/92 p-3 shadow-[0_24px_60px_rgba(15,23,42,0.16)] backdrop-blur-xl">
      <div className="mx-auto flex max-w-[1440px] flex-col gap-3 sm:flex-row sm:justify-end">
        <Button variant="secondary" className="sm:w-auto" disabled={!hasCaption} onClick={onCopyCaption}>
          {isCopied ? '✓ Copied!' : 'Copy Caption'}
        </Button>
        <Button variant="gradient" className="sm:w-auto" disabled={!hasCaption || isGeneratingCreativeDirection} onClick={onGenerateCreativeDirection}>
          {isGeneratingCreativeDirection ? <Loader2 className="animate-spin" size={18} /> : <Sparkles size={18} />}
          {isGeneratingCreativeDirection ? 'Generating Creative Direction...' : 'Generate Creative Direction'}
        </Button>
      </div>
    </div>
  )
}
