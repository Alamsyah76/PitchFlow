# PRD — Email Campaign Automation
## Project: SendQuick Sales & Marketing Automation
**Version:** 1.0  
**Date:** 16 July 2026  
**Author:** Alamsyah (Product Owner)  
**Status:** Draft — Final after review

---

## 1. Visi & Tujuan

Membangun **Email Campaign Automation** yang bertindak sebagai **Mini CRM / Marketing Automation** ala GoHighLevel, khusus untuk kebutuhan Sales & Marketing SendQuick — 100% milik sendiri, tanpa biaya lisensi bulanan.

**Target pengguna:** Internal sales team SendQuick (multi-user)
**Target audiens:** Perusahaan di Indonesia (Finance, Healthcare, Manufacturing, IT Services, Hospitality, dll)

---

## 2. Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────────┐
│                        TELEGRAM BOT                             │
│  (Command: kirim email, cek status, balas inbox)               │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────┼────────────────────────────────────────┐
│                        ▼                                        │
│               EMAIL CAMPAIGN ENGINE                              │
│  ┌────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Audience   │ │ Template │ │ Send +   │ │ Settings         │ │
│  │ Management │ │ Engine   │ │ Tracking │ │ (SMTP, Sender)   │ │
│  └────────────┘ └──────────┘ └──────────┘ └──────────────────┘ │
│                        │                                        │
│  ┌────────────┐ ┌──────────┐ ┌──────────┐                      │
│  │ Log &      │ │ Report   │ │ Inbox    │                      │
│  │ Analytics  │ │ Generator│ │ Monitor  │                      │
│  └────────────┘ └──────────┘ └──────────┘                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────┼────────────────────────────────────────┐
│                        ▼                                        │
│                      N8N (AUTOMATION ENGINE)                     │
│  ┌────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Schedule   │ │ Webhook  │ │ Scrape   │ │ Integration      │ │
│  │ 3 sesi/hr  │ │ Trigger  │ │ Monitor  │ │ (Apollo, dll)    │ │
│  └────────────┘ └──────────┘ └──────────┘ └──────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

---

## 3. Skala Prioritas

Prioritas ditentukan berdasarkan **keyakinan implementasi** (ease) dan **dampak sales**. Yang paling mudah dan berdampak dikerjakan duluan.

| Prioritas | Fase | Fitur | Keyakinan | Waktu |
|-----------|------|-------|-----------|-------|
| **P0** 🔥 | Fase 1 | Core Engine | ✅ 100% | ✅ **SELESAI** |
| **P1** 🟢 | Fase 2 | Blog Monitor | 100% | 1 hari |
| **P1** 🟢 | Fase 2 | Telegram Kirim Compro | 100% | 2 hari |
| **P1** 🟢 | Fase 2 | Content Library | 90% | 1 hari |
| **P1** 🟢 | Fase 3 | n8n Schedule (3 sesi) | 100% | 2 hari |
| **P1** 🟢 | Fase 3 | Daily Report Telegram | 100% | 1 hari |
| **P2** 🟡 | Fase 3 | Smart Template by Industry | 90% | 2 hari |
| **P2** 🟡 | Fase 4 | Open Tracking | 100% | 2 hari |
| **P2** 🟡 | Fase 4 | Auto Follow-up | 85% | 2 hari |
| **P3** 🟠 | Fase 4 | Bounce Detection | 70% | 2 hari |
| **P3** 🟠 | Fase 4 | Click Tracking | 80% | 2 hari |
| **P3** 🟠 | Fase 5 | Sales Dashboard | 90% | 3 hari |
| **P3** 🟠 | Fase 5 | Multi-User | 80% | 4-5 hari |
| **P4** 🔴 | Fase 6 | Inbox Monitor + Telegram Balas | 60% | 5 hari |
| **P4** 🔴 | Fase 6 | AI Agent 24jam | 40% | 7+ hari |

**Catatan:** P0 = sudah selesai. P1 = dikerjakan duluan. P4 = dikerjakan paling akhir. Urutan bisa berubah jika ada ide baru yang lebih mendesak.

---

### 🟢 FASE 1 — CORE ENGINE (P0 — SELESAI) ✅

| Fitur | Status |
|-------|--------|
| Template CRUD (create, edit, delete, activate) | ✅ |
| Import template dari SendQuick.com (produk + blog) | ✅ |
| SMTP Configuration via UI | ✅ |
| CC Email per template | ✅ |
| Audience management (upload XLS/CSV) | ✅ |
| Send email (selected + batch) | ✅ |
| Send log & history | ✅ |
| Test email whitelist (never blocked) | ✅ |
| Pagination + filter (all/pending/sent) | ✅ |
| English UI | ✅ |
| Orange theme (#F48120) | ✅ |
| Git rollback point | ✅ |

---

### 🟢 FASE 2 — IMMEDIATE (P1 — PRIORITAS PERTAMA, 4 Hari)

#### 2.1 Blog Monitor
**Deskripsi:** Sistem secara otomatis mendeteksi artikel/blog baru di www.sendquick.com/resources/blog/ dan mengirimkannya sebagai newsletter ke semua kontak di audience list.

**Cara kerja:**
1. Scheduler (n8n atau cron) cek halaman blog tiap 6 jam
2. Bandingkan judul artikel terakhir dengan yang sudah dikirim
3. Jika ada artikel baru → buat template → kirim newsletter ke semua kontak

**Acceptance Criteria:**
- [ ] Deteksi artikel baru dalam 6 jam setelah publikasi
- [ ] Auto-kirim newsletter ke semua kontak
- [ ] Link "Read more at sendquick.com" di setiap email
- [ ] Log pengiriman tetap tercatat

**Estimasi:** 1 hari | **Keyakinan:** 100%

#### 2.2 Telegram Command — Kirim Compro/File
**Deskripsi:** Sales bisa kirim perintah via Telegram dari HP untuk mengirimkan company profile atau file PDF ke email tujuan, tanpa harus buka laptop.

**Flow:**
```
Kamu di Telegram:
  /kirim compro ke budi@bankmandiri.com

Sistem:
  ├── Cari file "SendQuick Company Profile.pdf" di folder Content Library
  ├── Buka Email Campaign
  ├── Template: "Compro SendQuick"
  ├── Attachment: PDF compro
  ├── Kirim ke budi@bankmandiri.com
  └── Balas: ✅ Terkirim ke budi@bankmandiri.com

Kamu di Telegram:
  /kirim file "Conexa Brochure.pdf" ke cto@techcorp.com
  ─→ Sama seperti di atas, beda file
```

**Perintah Telegram:**
| Command | Format | Fungsi |
|---------|--------|--------|
| `/kirim` | `/kirim compro ke email@domain.com` | Kirim compro |
| `/kirim` | `/kirim file "nama file.pdf" ke email@domain.com` | Kirim file tertentu |
| `/status` | `/status` | Cek jumlah pending hari ini |
| `/bantuan` | `/bantuan` | Daftar perintah |

**Acceptance Criteria:**
- [ ] Bot Telegram merespon dalam 10 detik
- [ ] Error handling kalau file tidak ditemukan
- [ ] Log pengiriman tetap tercatat
- [ ] Attachment PDF terkirim dengan benar

**Estimasi:** 2 hari | **Keyakinan:** 100%

#### 2.3 Content Library
**Deskripsi:** Folder/file manager untuk menyimpan PDF, brosur, case study yang bisa dipanggil via Telegram command.

**Struktur:**
```
email_campaign/content_library/
├── compro/SendQuick Company Profile.pdf
├── brochures/SendQuick Alert Plus Brochure.pdf
├── brochures/SendQuick AI-in-a-Box Brochure.pdf
├── brochures/Conexa MFA Brochure.pdf
├── case_studies/BCA Implementation.pdf
└── case_studies/Hospitality Success Story.pdf
```

**Acceptance Criteria:**
- [ ] Upload file via Web UI
- [ ] List file via Telegram
- [ ] Kirim file via Telegram command

**Estimasi:** 1 hari | **Keyakinan:** 90%

---

### 🟡 FASE 3 — AUTOMATION (P1-P2, 5 Hari)

#### 3.1 n8n Automation Engine (P1 🟢)
**Deskripsi:** Setup n8n sebagai scheduler dan orchestrator untuk otomatisasi pengiriman.

**Schedule:**
| Sesi | Waktu | Jumlah |
|------|-------|--------|
| Pagi | 08:00 WIB | 10 email |
| Siang | 13:00 WIB | 10 email |
| Sore | 17:00 WIB | 10 email |
| **Total/hari** | | **30 email** |

**Cara kerja:**
1. n8n trigger tiap sesi
2. Panggil API Email Campaign: `POST /api/email-campaign/send`
3. Ambil pending contacts dari audience
4. Kirim sesuai daily limit (30/hari)
5. Log hasil pengiriman

**Docker:**
```yaml
services:
  n8n:
    image: n8nio/n8n
    ports:
      - "5678:5678"
    volumes:
      - n8n_data:/home/node/.n8n
    restart: unless-stopped
```

**Acceptance Criteria:**
- [ ] Email terkirim otomatis sesuai jadwal
- [ ] Tidak melebihi daily limit 30/hari
- [ ] Log tercatat di Email Campaign
- [ ] Notifikasi error ke Telegram jika gagal

**Estimasi:** 2 hari | **Keyakinan:** 100%

#### 3.2 Smart Template by Industry (P2 🟡)
**Deskripsi:** Saat upload kontak dari Apollo.io atau CSV, sistem otomatis memilihkan template yang sesuai dengan industri kontak.

**Mapping Industri → Template:**
| Industri | Template Default | Produk Rekomendasi |
|----------|-----------------|-------------------|
| Finance / Banking | Conexa MFA | MFA/FIDO2 Security |
| Healthcare | Alert Plus | IT Alert & Notifikasi |
| Manufacturing | OT Alerts | Operational Technology |
| Hospitality | Entera | Conversational AI |
| IT Services | AI-in-a-Box | Private LLM on-prem |
| Government | Conexa MFA | Secure Remote Access |
| Education | Alert Plus | IT Infrastructure |
| Retail | Entera | Business Process Automation |

**Cara kerja:**
1. Upload CSV via UI atau Apollo export
2. Sistem baca kolom "Industry" atau "Company"
3. Cari template yang sesuai di template list
4. Set template tersebut sebagai aktif untuk kontak baru
5. Konfirmasi ke user: "15 kontak Finance → template Conexa MFA aktifkan?"

**Acceptance Criteria:**
- [ ] Mapping industri → template bisa dikonfigurasi
- [ ] Auto-pilih template saat upload
- [ ] User bisa override pilihan template

**Estimasi:** 2 hari | **Keyakinan:** 90%

#### 3.3 Daily Report ke Telegram (P1 🟢)
**Deskripsi:** Setiap jam 20:00, sistem kirim report harian via Telegram.

**Format Report:**
```
📊 REPORT EMAIL CAMPAIGN — 16 July 2026

✅ Terkirim: 30/30
👁️ Dibuka: 12 (40%)
🔄 Belum dibuka: 18
📬 Reply: 2

🔥 Prospek panas:
  - budi@bankmandiri.com — Buka 3x
  - cto@techcorp.com — Reply "Tertarik, jadwalkan demo"

⏰ Follow-up besok:
  - 5 kontak belum buka (3 hari)
```

**Acceptance Criteria:**
- [ ] Report terkirim otomatis setiap jam 20:00
- [ ] Data akurat dari Email Campaign log

**Estimasi:** 1 hari | **Keyakinan:** 100%

---

### 🔴 FASE 4 — ADVANCED (P3 — SULIT, 8 Hari)

#### 4.1 Open Tracking
**Deskripsi:** Deteksi siapa yang membuka email yang dikirim via Email Campaign.

**Cara kerja:**
1. Setiap email disisipi gambar pixel 1x1 pixel (`<img src="https://domain.com/track/open?email=xxx&template=yyy" />`)
2. Saat penerima buka email, gambar ter-load → tercatat sebagai "opened"
3. Data open rate tampil di log dan report

**Acceptance Criteria:**
- [ ] Open tracking akurat (tidak double count)
- [ ] Tidak mempengaruhi deliverability email
- [ ] Data open rate di log

**Estimasi:** 2 hari | **Keyakinan:** 100%

#### 4.2 Bounce Detection
**Deskripsi:** Deteksi email bounce (gagal terkirim) dan auto-hapus dari audience list.

**Cara kerja:**
1. Baca email bounce dari SendQuick mail server (IMAP/API)
2. Cocokkan dengan email di audience list
3. Tandai sebagai "bounced" atau hapus
4. Report: "5 email bounce hari ini — dibersihkan"

**Acceptance Criteria:**
- [ ] Bounce terdeteksi dalam 24 jam
- [ ] Email bounce auto-dihapus dari audience
- [ ] Log bounce tercatat

**Estimasi:** 2 hari | **Keyakinan:** 70% (tergantung akses ke mail server)

#### 4.3 Auto Follow-up
**Deskripsi:** Jika kontak tidak membuka email dalam 3 hari, kirim ulang dengan subject berbeda.

**Flow:**
```
Hari 1: Kirim email →  "Introducing SendQuick AI-in-a-Box"
Hari 4: Follow-up → "Quick question about your AI strategy"
Hari 7: Follow-up → "Last chance — Free consultation"
```

**Acceptance Criteria:**
- [ ] Follow-up hanya ke yang belum buka
- [ ] Subject berbeda tiap sesi
- [ ] Maksimal 3 follow-up per kontak

**Estimasi:** 2 hari | **Keyakinan:** 85%

#### 4.4 Click Tracking
**Deskripsi:** Deteksi link mana yang diklik di dalam email.

**Cara kerja:**
1. Setiap link di email di-wrap dengan redirect URL (`https://domain.com/track/click?url=https://sendquick.com/...&email=xxx`)
2. Saat diklik, tercatat + redirect ke tujuan asli
3. Data click rate tampil di log

**Acceptance Criteria:**
- [ ] Click tracking akurat
- [ ] Redirect ke URL asli bekerja

**Estimasi:** 2 hari | **Keyakinan:** 80%

---

### 🔴 FASE 5 — CRM & DASHBOARD (P3 — SULIT, 7 Hari)

#### 5.1 Sales Dashboard
**Deskripsi:** Dashboard pipeline yang menampilkan seluruh aktifitas email campaign.

**Fitur:**
- Total terkirim, dibuka, diklik, reply
- Pipeline berdasarkan status (New → Contacted → Meeting → Negotiation)
- Follow-up reminder
- Export report ke CSV

**Estimasi:** 3 hari | **Keyakinan:** 90%

#### 5.2 Multi-User Support
**Deskripsi:** Email Campaign bisa dipakai oleh banyak sales sekaligus.

**Fitur:**
- Login & password per user
- Data terpisah per user (template, audience, log)
- Admin panel: manage users, lihat semua log
- SMTP sendiri-sendiri per user

**Estimasi:** 4-5 hari | **Keyakinan:** 80%

---

### 🔴 FASE 6 — AI & INTEGRATION (P4 — PALING SULIT & TERAKHIR, 12+ Hari)

#### 6.1 Inbox Monitoring + Balas via Telegram
**Deskripsi:** Sistem monitor inbox SendQuick, notifikasi ke Telegram, sales balas via Telegram, sistem kirim balasan email.

**Flow:**
```
Email masuk ke budi@bankmandiri.com
  → Sistem deteksi email baru (IMAP IDLE / polling)
  → Notifikasi ke Telegram: "📬 Email dari budi@bankmandiri.com — Tertarik dengan AI-in-a-Box"
  → Kamu balas: "kirim compro dan jadwalkan demo"
  → Sistem kirim email balasan otomatis
```

**Acceptance Criteria:**
- [ ] Deteksi email baru dalam 5 menit
- [ ] Notifikasi Telegram realtime
- [ ] Balas email via Telegram command

**Estimasi:** 5 hari | **Keyakinan:** 60%

#### 6.2 AI Agent (Future)
**Deskripsi:** Sistem bekerja 24/7 dengan AI sebagai asisten.

**Fitur:**
- AI bantu tulis subject line
- AI rekomendasi template berdasarkan konten
- AI jawab email sederhana otomatis (tanpa perintah)

**Estimasi:** 7+ hari | **Keyakinan:** 40%

---

## 4. Teknologi Stack

| Layer | Teknologi | Keterangan |
|-------|-----------|------------|
| Backend | Python + FastAPI | ✅ Sudah |
| Frontend | Next.js | ✅ Sudah |
| Database | JSON files (migrasi ke SQLite nanti) | ✅ Sudah |
| SMTP Server | Mail SendQuick | ✅ Sudah |
| Automation | n8n (Docker) | 🔜 Fase 3 |
| Telegram Bot | python-telegram-bot / API langsung | 🔜 Fase 2 |
| Scheduler | n8n cron | 🔜 Fase 3 |
| Open Tracking | Custom 1x1 pixel + API | 🔜 Fase 4 |
| AI | Gemini / OpenAI | 🔜 Fase 6 |

---

## 5. API Endpoints (Existing)

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| GET | `/api/email-campaign/templates` | List templates |
| POST | `/api/email-campaign/templates` | Create template |
| PUT | `/api/email-campaign/templates/{id}` | Update template |
| DELETE | `/api/email-campaign/templates/{id}` | Delete template |
| POST | `/api/email-campaign/templates/{id}/activate` | Activate template |
| GET | `/api/email-campaign/status` | Campaign stats |
| GET | `/api/email-campaign/preview` | Audience list |
| POST | `/api/email-campaign/upload` | Upload XLS/CSV |
| POST | `/api/email-campaign/send-selected` | Send selected contacts |
| GET | `/api/email-campaign/log` | Send log |
| GET | `/api/email-campaign/settings` | Get SMTP settings |
| POST | `/api/email-campaign/settings` | Save SMTP settings |
| GET | `/api/email-campaign/scrape/products` | List products from web |
| POST | `/api/email-campaign/scrape/product` | Scrape product page |
| GET | `/api/email-campaign/scrape/blog` | List blog posts |
| POST | `/api/email-campaign/scrape/blog-post` | Scrape blog post |

---

## 6. Non-Goals (Tidak Akan Dibangun)

| Fitur | Alasan |
|-------|--------|
| WA Chatbot | Risiko tinggi, kompleks, butuh integrasi WA API |
| AI Generate body email otomatis | Trauma — sebelumnya gagal (persona targeting + bilingual) |
| Multi-language support | Gagal di percobaan sebelumnya |
| Public registration | Internal tools — hanya untuk tim sales |

---

## 7. Risiko & Mitigasi

| Risiko | Dampak | Mitigasi |
|--------|--------|----------|
| Inbox monitoring gagal | Fase 6 terhambat | Cek dulu apakah SendQuick support IMAP IDLE / webhook |
| Bounce detection tidak akurat | Audience kotor | Fallback: manual review tiap bulan |
| Multi-user complex | Development molor | Mulai dengan 2-3 user dulu, scaling nanti |
| Over-promise AI | Wasted time | Mulai dari non-AI dulu (Fase 1-5), AI di akhir |

---

## 8. Timeline Estimasi (Urut Prioritas)

| Prioritas | Fitur | Keyakinan | Durasi | Mulai |
|-----------|-------|-----------|--------|-------|
| **P0** 🔥 | Core Engine | ✅ 100% | ✅ SELESAI | - |
| **P1** 🟢 | Blog Monitor | 100% | 1 hari | TBD |
| **P1** 🟢 | Telegram Kirim Compro | 100% | 2 hari | TBD |
| **P1** 🟢 | Content Library | 90% | 1 hari | TBD |
| **P1** 🟢 | n8n Schedule (3 sesi) | 100% | 2 hari | TBD |
| **P1** 🟢 | Daily Report Telegram | 100% | 1 hari | TBD |
| **P2** 🟡 | Smart Template by Industry | 90% | 2 hari | TBD |
| **P2** 🟡 | Open Tracking | 100% | 2 hari | TBD |
| **P2** 🟡 | Auto Follow-up | 85% | 2 hari | TBD |
| **P3** 🟠 | Bounce Detection | 70% | 2 hari | TBD |
| **P3** 🟠 | Click Tracking | 80% | 2 hari | TBD |
| **P3** 🟠 | Sales Dashboard | 90% | 3 hari | TBD |
| **P3** 🟠 | Multi-User | 80% | 4-5 hari | TBD |
| **P4** 🔴 | Inbox Monitor + Telegram | 60% | 5 hari | TBD |
| **P4** 🔴 | AI Agent 24jam | 40% | 7+ hari | TBD |

---
**Catatan:** Timeline bisa berubah. Jika ada ide baru di tengah jalan, PRD ini akan diperbarui.

## 9. Penambahan Roadmap Baru

PRD ini adalah **living document**. Jika dalam perjalanan muncul ide baru:

1. Ide baru didiskusikan
2. Ditambahkan ke PRD dengan prioritas yang sesuai
3. Jika ide lebih mendesak dari P1 saat ini → prioritas digeser
4. Jika ide belum waktunya → masuk sebagai **P4 (nanti)** atau **Non-Goals**

**Tidak ada fitur yang ditambahkan tanpa melalui PRD ini.**

---

## 9. Approval

| Role | Nama | Status |
|------|------|--------|
| Product Owner | Alamsyah | ⏳ Menunggu review |

---

*Dokumen ini akan diperbarui seiring perkembangan implementasi.*
