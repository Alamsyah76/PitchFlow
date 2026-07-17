import { ChangeEvent, RefObject } from 'react'
import { AlertCircle, CloudUpload, FileText, Loader2, Sparkles } from 'lucide-react'
import { Button } from '../ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import type { UploadedDocumentMetadata } from '../../lib/content-types'

export interface UploadPanelProps {
  selectedFile: File | null
  uploadedDocument: UploadedDocumentMetadata | null
  documentId: string | null
  isUploading: boolean
  uploadError?: string
  topicsError?: string
  isGeneratingTopics: boolean
  compact?: boolean
  fileInputRef: RefObject<HTMLInputElement | null>
  onFileChange: (e: ChangeEvent<HTMLInputElement>) => void
  onChooseFile: () => void
  onGenerateTopics: () => void
}

function formatFileSize(bytes: number) {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

export default function UploadPanel({
  selectedFile,
  uploadedDocument,
  documentId,
  isUploading,
  uploadError,
  topicsError,
  isGeneratingTopics,
  compact,
  fileInputRef,
  onFileChange,
  onChooseFile,
  onGenerateTopics,
}: UploadPanelProps) {
  // Compact mode: show only a slim file summary, no upload UI, no Generate Topics
  if (compact) {
    const fileName = uploadedDocument?.file_name ?? selectedFile?.name ?? 'Document'
    const pageInfo = typeof uploadedDocument?.total_pages === 'number' ? `, ${uploadedDocument.total_pages} pages` : ''
    return (
      <div className="flex w-full items-center justify-between gap-3 rounded-xl border border-slate-200/80 bg-white px-4 py-3 shadow-sm">
        <div className="flex min-w-0 items-center gap-3">
          <FileText size={18} className="shrink-0 text-emerald-600" />
          <div className="min-w-0">
            <div className="truncate text-sm font-medium text-slate-900">{fileName}</div>
            <div className="text-xs text-emerald-700">Uploaded{pageInfo}</div>
          </div>
        </div>
        <button
          onClick={onChooseFile}
          className="shrink-0 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 transition-colors hover:border-slate-300 hover:bg-slate-50"
        >
          Change
        </button>
      </div>
    )
  }

  return (
    <section className="grid gap-6 xl:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Upload PDF Document</CardTitle>
          <CardDescription>Upload any PDF document to extract key insights.</CardDescription>
        </CardHeader>
        <CardContent>
          <input ref={fileInputRef} type="file" accept="application/pdf" className="hidden" onChange={onFileChange} />
          <div className="flex min-h-[230px] flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300/80 bg-[#FAFBFF] px-8 text-center shadow-inner">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-white text-[#6D5DFC] shadow-[0_14px_30px_rgba(15,23,42,0.08)]">
              {isUploading ? <Loader2 className="animate-spin" size={28} /> : <CloudUpload size={28} />}
            </div>
            <div className="mt-4 text-sm font-semibold text-slate-900">{selectedFile ? selectedFile.name : 'Drop your PDF here'}</div>
            <p className="mt-1 text-sm text-slate-500">{selectedFile ? formatFileSize(selectedFile.size) : 'PDF only, one file at a time.'}</p>
            <Button className="mt-5" variant="outline" disabled={isUploading} onClick={onChooseFile}>
              {isUploading ? 'Uploading...' : 'Choose File'}
            </Button>
          </div>

          {uploadError && (
            <div className="mt-5 flex items-start gap-3 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3.5 text-sm text-rose-800">
              <AlertCircle className="mt-0.5 shrink-0" size={18} />
              <span>{uploadError}</span>
            </div>
          )}

          {selectedFile && !uploadError && (
            <div className="mt-5 rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3.5">
              <div className="flex items-center gap-3">
                <FileText className="text-emerald-600" size={18} />
                <div className="min-w-0">
                  <div className="truncate text-sm font-medium text-slate-900">{selectedFile.name}</div>
                  <div className="text-xs text-emerald-700">
                    {uploadedDocument
                      ? `${uploadedDocument.file_name} ready${typeof uploadedDocument.total_pages === 'number' ? `, ${uploadedDocument.total_pages} pages` : ''}`
                      : documentId
                        ? `Document ready: ${documentId}`
                        : isUploading
                          ? 'Uploading and processing...'
                          : 'Ready to upload'}
                  </div>
                </div>
              </div>

              <Button className="mt-4 w-full" variant="gradient" size="lg" disabled={!documentId || isGeneratingTopics} onClick={onGenerateTopics}>
                {isGeneratingTopics ? <Loader2 className="animate-spin" size={18} /> : <Sparkles size={18} />}
                {isGeneratingTopics ? 'Generating Topics...' : 'Generate Topics'}
              </Button>
            </div>
          )}

          {topicsError && (
            <div className="mt-5 flex items-start gap-3 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-sm text-rose-800">
              <AlertCircle className="mt-0.5 shrink-0" size={18} />
              <span>{topicsError}</span>
            </div>
          )}
        </CardContent>
      </Card>
    </section>
  )
}
