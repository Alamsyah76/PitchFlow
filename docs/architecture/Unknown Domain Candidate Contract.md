# Unknown Domain Candidate Contract

## Purpose

`unknown_domain_candidate` adalah klasifikasi sementara untuk PDF yang diunggah ketika fingerprint semantiknya belum cukup kuat untuk masuk ke domain permanen yang sudah ada.

Tujuannya:

* mencegah sistem memaksa PDF ke domain ERP, network/security, hardware, atau alerting secara keliru,
* menjaga output tetap konservatif dan evidence-grounded,
* memberi jalur aman sebelum domain baru dipromosikan menjadi profil permanen.

---

## Behavior

Ketika `domain = unknown_domain_candidate`:

* jangan memaksa framing ERP / network / hardware / alerting,
* jangan memakai fallback monitoring generik,
* jangan memakai template domain-spesifik yang sudah ada,
* hasilkan output yang konservatif dan hanya berbasis evidence saat ini,
* prioritaskan 1 topik kuat dibanding 2 topik lemah,
* gunakan hanya konsep yang benar-benar muncul di evidence dokumen aktif,
* jangan mempromosikan domain ini menjadi domain permanen secara otomatis.

---

## Output Rules

### Topic Rules

Topik harus:

* lahir hanya dari evidence dokumen aktif,
* sempit, konkret, dan bisa ditelusuri ke snippet evidence,
* menghindari klaim platform yang terlalu luas,
* menghindari istilah stale dari domain lain,
* menghindari keyword concatenation atau label kategori yang tidak didukung evidence.

Topik tidak boleh:

* meminjam framing domain permanen yang belum terbukti,
* memakai istilah monitoring/network/security/hardware/ERP hanya karena fallback lama,
* mengisi kuota topik jika evidence tidak cukup.

### Caption Rules

Caption harus:

* menjelaskan problem atau value yang memang muncul dari dokumen itu sendiri,
* tetap berhati-hati dan evidence-grounded,
* menghindari keyword-dump phrasing,
* menghindari label brand/category yang tidak didukung evidence,
* menghindari fallback monitoring/network generik.

Caption tidak boleh:

* mengimpor framing known domain tanpa bukti,
* menyebut stale terms dari domain upload sebelumnya,
* memakai kategori produk/bisnis yang tidak eksplisit di evidence.

---

## Promotion Rules

`unknown_domain_candidate` hanya boleh dipromosikan ke domain permanen setelah review manusia dan bukti berulang.

Promosi memerlukan:

* vocabulary yang jelas berbeda dari domain yang sudah ada,
* business workflow yang jelas berbeda,
* risiko kontaminasi domain yang jelas dan terdokumentasi,
* minimal satu golden sample,
* profil domain permanen ditambahkan secara manual.

Tidak ada promosi otomatis dari runtime output.

---

## Failure Rules

Hard fail atau kurangi output jika:

* evidence terlalu lemah,
* topik terlalu generik,
* caption mengimpor framing known-domain tanpa evidence,
* output mengandung stale terms dari domain sebelumnya,
* confidence domain rendah tetapi sistem tetap mencoba menghasilkan framing luas.

Aturan reduksi:

* jika confidence rendah, batasi ke 1 topik kuat,
* jika tidak ada topik yang cukup kuat, lebih baik tidak menghasilkan topik tambahan,
* jika caption tidak bisa tetap grounded, sistem harus memilih output yang lebih sempit dan lebih berhati-hati.

---

## Non-Negotiable Rule

`unknown_domain_candidate` adalah mode penahanan kualitas.

Prioritasnya:

* lebih sedikit output,
* lebih sempit,
* lebih grounded,

bukan:

* lebih banyak output,
* lebih percaya diri,
* lebih generik.
