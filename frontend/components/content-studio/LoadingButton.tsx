import { Loader2 } from 'lucide-react'
import type { ButtonHTMLAttributes, ReactNode } from 'react'

export interface LoadingButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  loading?: boolean
  loadingText?: string
  icon?: ReactNode
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
}

const baseClasses =
  'inline-flex items-center justify-center gap-2 font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#6D5DFC] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'

const variantClasses = {
  primary:
    'rounded-xl bg-gradient-to-r from-[#5F54F2] to-[#755CF5] text-white shadow-[0_8px_20px_rgba(109,93,252,0.18)] hover:opacity-95',
  secondary: 'rounded-xl border border-slate-200 bg-white text-slate-700 shadow-sm hover:border-slate-300 hover:bg-slate-50',
  ghost: 'rounded-lg text-slate-600 hover:bg-slate-100',
}

const sizeClasses = {
  sm: 'px-3 py-2 text-xs',
  md: 'px-5 py-2.5 text-sm',
  lg: 'px-6 py-3 text-sm',
}

export default function LoadingButton({
  loading = false,
  loadingText,
  icon,
  variant = 'primary',
  size = 'md',
  children,
  disabled,
  className = '',
  ...props
}: LoadingButtonProps) {
  return (
    <button
      disabled={disabled || loading}
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      {...props}
    >
      {loading ? <Loader2 className="animate-spin shrink-0" size={size === 'sm' ? 14 : 16} /> : icon ?? null}
      {loading && loadingText ? loadingText : children}
    </button>
  )
}