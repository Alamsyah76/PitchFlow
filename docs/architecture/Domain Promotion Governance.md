# Domain Promotion Governance

## Production Rule

Dalam production:

* sistem boleh mengklasifikasikan PDF yang tidak yakin sebagai `unknown_domain_candidate`,
* sistem tidak boleh membuat domain permanen secara otomatis,
* sistem tidak boleh menulis profile domain baru, guardrail matrix baru, atau aturan domain baru tanpa persetujuan manusia.

Aturan inti:

> unknown classification is allowed; automatic permanent domain creation is forbidden.

---

## Candidate Lifecycle

Setiap candidate domain harus mengikuti lifecycle berikut:

1. **detected**
   - sistem menemukan fingerprint semantik yang tidak cukup cocok dengan domain permanen yang ada

2. **logged**
   - metadata candidate disimpan untuk review

3. **reviewed**
   - manusia mengevaluasi apakah candidate benar-benar domain baru atau hanya variasi dari domain yang sudah ada

4. **promoted**
   - candidate diangkat menjadi domain permanen setelah semua syarat terpenuhi dan approval diberikan

5. **rejected**
   - candidate ditolak karena evidence tidak cukup, terlalu generik, atau tidak stabil

6. **merged into existing domain**
   - candidate tidak menjadi domain baru, tetapi digabung sebagai variasi/example dari domain permanen yang sudah ada

---

## Promotion Requirements

Sebuah `unknown_domain_candidate` hanya boleh dipromosikan menjadi domain permanen jika semua syarat ini terpenuhi:

* minimal **3 PDF berbeda**
* fingerprint semantik konsisten di ketiga atau lebih sample tersebut
* business workflow jelas berbeda dari domain permanen yang sudah ada
* daftar allowed concepts jelas
* daftar forbidden contamination terms jelas
* minimal **1 golden regression sample**
* approval admin / reviewer manusia

Jika salah satu syarat tidak terpenuhi:

* jangan promosi domain,
* tetap jadikan candidate sebagai unknown atau merge ke domain yang sudah ada.

---

## Candidate Storage

Path yang disarankan:

`data/domain_candidates/`

Setiap candidate sebaiknya menyimpan:

* fingerprint
* confidence scores
* source document metadata
* dominant concepts
* closest existing domains
* timestamp deteksi
* status lifecycle

Contoh informasi minimal:

```json
{
  "candidate_id": "unknown_domain_candidate_xxx",
  "fingerprint": "...",
  "confidence_scores": {
    "unknown_domain_candidate": 0.61,
    "closest_domain": 0.42
  },
  "source_documents": [
    {
      "document_id": "...",
      "file_name": "...",
      "uploaded_at": "..."
    }
  ],
  "dominant_concepts": ["..."],
  "closest_existing_domains": ["erp_operations", "business_hardware"],
  "status": "detected"
}
```

---

## Safety Behavior

Ketika sebuah PDF jatuh ke `unknown_domain_candidate`:

* output harus konservatif dan grounded,
* tidak boleh memakai fallback monitoring/network generik,
* tidak boleh menghasilkan profile domain permanen otomatis,
* tidak boleh mengubah guardrail matrix tanpa approval,
* tidak boleh menambah permanent domain registry secara runtime.

Tujuannya adalah containment:

* tahan domain baru sebagai candidate,
* kumpulkan bukti,
* review dulu,
* baru putuskan promosi.

---

## Rejection / Merge Rule

Jika candidate ternyata hanya variasi dari domain permanen yang sudah ada:

* merge ke domain yang sudah ada sebagai contoh / coverage tambahan,
* jangan buat domain baru.

Candidate harus **ditolak** jika:

* vocabulary tidak cukup berbeda,
* business workflow sama dengan domain existing,
* contamination risk tidak unik,
* evidence terlalu sedikit,
* semantik tidak stabil antar PDF.

Candidate harus **di-merge** jika:

* masih berada dalam semantik domain existing,
* hanya memperluas contoh, bukan memperkenalkan kelas domain baru.

---

## Governance Principle

Domain permanen adalah aset produksi.

Karena itu:

* penambahan domain harus lambat,
* berbasis bukti berulang,
* punya regression coverage,
* dan disetujui manusia.

Sistem boleh mendeteksi candidate.
Sistem tidak boleh mempromosikan candidate sendiri.
