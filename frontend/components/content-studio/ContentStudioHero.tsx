import { ChangeEvent, RefObject } from 'react'
import { CloudUpload } from 'lucide-react'

type ContentStudioHeroProps = {
  onUploadClick: () => void
  fileInputRef: RefObject<HTMLInputElement | null>
  onFileChange: (event: ChangeEvent<HTMLInputElement>) => void
  isUploading?: boolean
  isGenerating?: boolean
}

export default function ContentStudioHero({
  onUploadClick,
  fileInputRef,
  onFileChange,
}: ContentStudioHeroProps) {
  return (
    <div className="xl:col-span-4">
      <div className="flex h-full flex-col justify-center px-6 py-12 xl:px-10">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-950 md:text-3xl">
            PitchFlow
          </h1>
          <p className="mt-3 text-base leading-relaxed text-slate-500">
            Transform PDFs into LinkedIn-ready content, visual assets, and thought leadership
            posts.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <button
              onClick={onUploadClick}
              className="inline-flex items-center gap-2 rounded-2xl bg-gradient-to-r from-[#0056b3] to-[#003d7a] px-6 py-3 text-sm font-semibold text-white shadow-[0_10px_24px_rgba(0,86,179,0.30)] transition-all hover:brightness-110">
              <CloudUpload size={18} />
              Upload PDF
            </button>
          </div>
        </div>

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={onFileChange}
        />
      </div>
    </div>
  )
}
