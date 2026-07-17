/** Library per-user via backend API — bukan localStorage */
const API = (typeof window !== 'undefined' && (window as any).__NEXT_DATA__?.env?.NEXT_PUBLIC_API_URL) || 'http://127.0.0.1:8027'

export interface LibraryItem {
  id: string
  pdf_filename: string
  selected_topic: string
  caption_text: string
  hashtags: string[]
  image_url: string | null
  industry: string
  score: number
  timestamp: string
}

function getUserEmail(): string {
  if (typeof window === 'undefined') return 'default'
  try {
    const raw = localStorage.getItem('pitchflow_user')
    if (raw) {
      const u = JSON.parse(raw)
      return u.email || u.identifier || 'default'
    }
  } catch {}
  return 'default'
}

export async function autoSaveProject(project: Omit<LibraryItem, 'id' | 'timestamp' | 'industry' | 'score'>, topic: string): Promise<LibraryItem | null> {
  const industry = detectIndustry(topic)
  const score = estimateScore({ ...project, industry })
  const newItem: LibraryItem = {
    ...project,
    industry,
    score,
    id: `lib-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    timestamp: new Date().toISOString(),
  }
  try {
    const r = await fetch(`${API}/api/library/add`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: getUserEmail(), item: newItem })
    })
    const d = await r.json()
    if (d.success) return newItem
  } catch {}
  return null
}

export async function getProjects(): Promise<LibraryItem[]> {
  try {
    const r = await fetch(`${API}/api/library/list`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: getUserEmail() })
    })
    const d = await r.json()
    if (d.success) return d.data.items
  } catch {}
  return []
}

function detectIndustry(topic: string): string {
  const t = topic.toLowerCase()
  if (/keamanan|security|siber|cyber|firewall|ids|ips/.test(t)) return 'IT Security'
  if (/keuangan|finansial|bank|finance|likuiditas|aset|modal/.test(t)) return 'Finance & Banking'
  if (/kesehatan|medis|medic|hospital|rumah sakit|alat kesehatan/.test(t)) return 'Kesehatan'
  if (/mobil|otomotif|kendaraan|automotive|obd|ecu|mesin/.test(t)) return 'Otomotif'
  if (/distribusi|logistik|supply chain|gudang|warehouse/.test(t)) return 'Distribusi & Logistik'
  if (/energi|migas|oil|gas|power|listrik/.test(t)) return 'Energi'
  if (/pendidikan|edukasi|education|riset|research|universitas/.test(t)) return 'Pendidikan & Riset'
  if (/telekomunikasi|telco|jaringan|network/.test(t)) return 'Telekomunikasi'
  if (/manufaktur|manufactur|pabrik|produksi/.test(t)) return 'Manufaktur'
  if (/ai|artificial intelligence|data|digital|robot|robotik/.test(t)) return 'Teknologi & AI'
  return 'Lainnya'
}

function estimateScore(item: { caption_text: string; hashtags: string[]; image_url: string | null; industry: string }): number {
  let score = 5
  if (item.caption_text.length > 200) score += 1
  if (item.hashtags.length >= 5) score += 1
  if (item.image_url) score += 1
  if (item.caption_text.length > 400) score += 1
  if (item.industry !== 'Lainnya') score += 1
  return score
}
