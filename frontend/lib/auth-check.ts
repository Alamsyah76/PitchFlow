/** Auth check — redirect to /auth if not logged in */

function isDevMode(): boolean {
  if (typeof window === 'undefined') return false
  try {
    const params = new URLSearchParams(window.location.search)
    // ?dev=0 → hapus dev mode
    if (params.get('dev') === '0') {
      localStorage.removeItem('pitchflow_dev')
      return false
    }
    // ?dev=1 → enable dev mode
    if (params.get('dev') === '1') {
      localStorage.setItem('pitchflow_dev', 'true')
      return true
    }
    return localStorage.getItem('pitchflow_dev') === 'true'
  } catch {}
  return false
}

export function isLoggedIn(): boolean {
  if (typeof window === 'undefined') return false
  if (isDevMode()) return true
  return !!localStorage.getItem('pitchflow_user')
}

export function requireLogin(): boolean {
  if (isDevMode()) return true
  if (!isLoggedIn()) {
    localStorage.setItem('login_redirect', window.location.pathname)
    window.location.href = '/auth'
    return false
  }
  return true
}

export function getCurrentUser(): { email: string; name: string } | null {
  if (typeof window === 'undefined') return null
  if (isDevMode()) return { email: 'dev@pitchflow.com', name: 'Developer' }
  try {
    const raw = localStorage.getItem('pitchflow_user')
    return raw ? JSON.parse(raw) : null
  } catch { return null }
}

export function enableDevMode() {
  if (typeof window !== 'undefined')
    localStorage.setItem('pitchflow_dev', 'true')
}
