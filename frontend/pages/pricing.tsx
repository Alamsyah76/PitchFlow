import { useEffect } from 'react'
import { useRouter } from 'next/router'

export default function PricingPage() {
  const router = useRouter()
  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.location.href = '/#pricing'
    }
  }, [])
  return null
}
