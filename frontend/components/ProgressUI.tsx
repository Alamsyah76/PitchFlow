import React from 'react'

type Props = {
  progress: number // 0-100
  stepLabel?: string
}

export default function ProgressUI({ progress, stepLabel }: Props) {
  return (
    <div className="pdf-progress">
      <div className="text-sm font-medium">Generating PDF</div>
      <div className="bar mt-3"><i style={{ width: `${progress}%` }}></i></div>
      <div className="meta">{stepLabel || 'Preparing...' } — {Math.round(progress)}%</div>
    </div>
  )
}
