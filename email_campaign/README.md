# SendQuick Email Campaign Automation

## 📋 Deskripsi
Script otomatis untuk mengirim email promosi SendQuick ke potential customer dari database Excel.
Dibuat khusus untuk **Alamsyah — SendQuick Pte. Ltd (Singapore) — Indonesia Region**.

## 📁 Struktur Folder
```
email_campaign/
├── .env                  # Konfigurasi SMTP (isi sendiri)
├── .env.example          # Template konfigurasi
├── send_email.py         # Script utama
├── log.csv               # Log pengiriman (auto-generated)
├── requirements.txt      # Dependencies
└── README.md             # Panduan ini
```

## ⚙️ Setup Awal (hanya sekali)

### 1. Edit file `.env`
Buka file `email_campaign/.env` dan isi SMTP credentials SendQuick kamu:

```
SMTP_HOST=mail.sendquick.com      ← SMTP server kamu
SMTP_PORT=587                      ← Port SMTP (587 untuk TLS)
SMTP_USERNAME=alamsyah@sendquick.com
SMTP_PASSWORD=password_asli_kamu   ← GANTI dengan password asli
SENDER_NAME=Alamsyah
SENDER_EMAIL=alamsyah@sendquick.com
DAILY_LIMIT=10                     ← Maksimal 10 email/hari
```

### 2. Install dependencies (cukup sekali)
```bash
cd email_campaign
uv pip install xlrd
```

## 🚀 Cara Pakai

### 🔍 Dry Run (test dulu — tanpa kirim email)
```bash
cd email_campaign
python send_email.py --dry-run --preview 5
```
Ini akan menampilkan 5 kontak pertama yang akan diemail tanpa mengirim apa pun.

### 📨 Kirim Email Beneran
```bash
cd email_campaign
python send_email.py
```
Script akan:
1. Baca kontak dari sheet **Namecards** di `Report/Alams-Tekno database.xls`
2. Filter kontak yang sudah pernah dikirim (dicek dari `log.csv`)
3. Kirim maksimal **10 email** (configurable di `.env`)
4. Jeda 3 detik antar email (anti spam flag)
5. Simpan log ke `log.csv`

### 📊 Cek Log Pengiriman
Buka file `log.csv` di Excel atau text editor. Format:
```
timestamp,email,name,company,status,error
2026-07-10 19:00:00,agus@adsnet.co.id,Agus Budi Raharjo,PT Ambhara Duta Shamti,sent,
2026-07-10 19:00:03,m.alie@dtp.net.id,Ma'ruf Alie,PT. Dwi Tunggal Putra,sent,
```

## 📝 Template Email
Template otomatis menyertakan:
- ✅ Perkenalan: **Alamsyah dari SendQuick, Pte. Ltd Singapore untuk Indonesia Region**
- ✅ Produk: SQ AlertPlus, SQ AlertSMS, SQ OneWay
- ✅ Value proposition: integrasi monitoring tools, multi-channel alerting
- ✅ CTA: ajakan brief meeting 15-20 menit
- ✅ Email signature dengan kontak Alamsyah

## 🔄 Schedule Harian
Untuk kirim otomatis setiap hari, kamu bisa:
1. **Manual**: jalankan `python send_email.py` setiap hari
2. **Cron (Linux/Mac)**: 
   ```bash
   0 9 * * * cd /path/to/email_campaign && python send_email.py
   ```
3. **Task Scheduler (Windows)**: buat task harian jam 09:00

## 📈 Scaling
Mau kirim lebih banyak? Tinggal ganti `DAILY_LIMIT` di `.env` dan pastikan SMTP server kamu mendukung volumenya.

## ⚠️ Catatan Penting
- Jangan commit file `.env` ke Git (sudah di-ignore otomatis)
- Log `log.csv` aman untuk di-track karena hanya berisi data kontak publik
- Script otomatis skip kontak yang sudah pernah dikirim — aman di-run berkali-kali
- Untuk ganti template/edit konten email, edit fungsi `build_email_body()` di `send_email.py`
