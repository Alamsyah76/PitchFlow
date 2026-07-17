import React, { useEffect } from 'react'

type Props = {
  message: string
  type?: 'success' | 'error'
  onClose?: () => void
  duration?: number
}

export default function Toast({ message, type = 'success', onClose, duration = 4000 }: Props) {
  useEffect(() => {
    const t = setTimeout(() => onClose && onClose(), duration)
    return () => clearTimeout(t)
  }, [onClose, duration])

  return (
    <div className="toast-container">
      <div className={`toast ${type}`} role="alert">
        <div className="title">{type === 'success' ? 'Success' : 'Error'}</div>
        <div className="msg mt-1">{message}</div>
      </div>
    </div>
  )
}
