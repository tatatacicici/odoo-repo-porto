# 🏭 Odoo 17 Custom Addons — PT Nusantara Panel Mandiri

Kumpulan modul custom Odoo 17 Community yang dikembangkan untuk implementasi ERP **Manufacturing, Cost Control, Accounting Integration & IoT Telemetry** (studi kasus **PT Nusantara Panel Mandiri**), beserta modul pendukung dan latihan pengembangan Odoo.

## 📚 Dokumentasi Proyek (Notion)

Dokumentasi lengkap perancangan fungsional, arsitektur teknis, spesifikasi API, dan hasil verifikasi _System Integration Testing (SIT)_ tersedia pada tautan berikut:

- **Functional Configuration:** [Buka Dokumentasi Functional Configuration di Notion](https://app.notion.com/p/Functional-Configuration-41a64a9d8ba580a7a296c78884a98788?source=copy_link)
- **Technical Configuration (TDD & SIT Report):** [Buka Dokumentasi Technical Configuration di Notion](https://app.notion.com/p/Technical-Configuration-41a64a9d8ba5805b9067d5301848acd1?source=copy_link)

## 🛠️ Tech Stack

| Teknologi               | Keterangan                                         |
| ----------------------- | -------------------------------------------------- |
| Odoo 17 Community       | ERP Framework (`mrp`, `account`, `mail`)           |
| Python 3.10+            | Backend logic, ORM, REST Controller & `xlsxwriter` |
| XML (QWeb, Views)       | View inheritance, security rules & PDF reports     |
| PostgreSQL 15           | Database                                           |
| Docker & Docker Compose | Containerized environment                          |

## 📦 Modul yang Tersedia

### 1. [`purchase_request`](./addons/purchase_request/)

Modul manajemen permintaan pembelian internal sebelum dibuat Purchase Order resmi.

- Approval workflow: **Draft → Diajukan → Disetujui / Ditolak**
- Nomor otomatis (format `PR/YYYY/001`)
- Reject wizard dengan alasan penolakan
- PDF report dengan tanda tangan

### 2. [`mrp_custom_qc`](./addons/mrp_custom_qc/) _(Nusantara MRP Quality, Cost Control & IoT)_

Ekstensi modul Manufacturing (`mrp`) & Accounting (`account`) untuk kontrol kualitas produksi, pengendalian biaya (_job costing_), pelaporan, dan integrasi perangkat penguji IoT.

- **GAP-01 (Automated Scrap PR & Journal):** Eksekusi _Fail & Scrap_ otomatis membuat `purchase.request` pengganti dan menjurnal kerugian bahan baku ke `account.move` (_Posted_)
- **GAP-02 (Cost Variance & Approval):** Perhitungan estimasi vs aktual biaya produksi; selisih biaya `> 10%` memblokir `button_mark_done()` hingga disetujui manager (`group_mrp_cost_approver`)
- **GAP-03 (Job Costing PDF & Excel COGS):** Cetak sertifikat QC & Job Costing (QWeb PDF dengan Barcode Code128) serta wizard ekspor laporan HPP bulanan (`.xlsx`)
- **GAP-04 (IoT Telemetry REST API):** Endpoint `POST /api/v1/mrp/qc-result` dengan autentikasi `X-API-Key` beserta simulator [`iot_simulator.py`](./iot_simulator.py)

### 3. Modul Pendukung & Latihan

- [`pos_simple`](./addons/pos_simple/) — Modul latihan Point of Sale sederhana (order, sequence, cancel wizard, receipt PDF)
- [`my_first_module`](./addons/my_first_module/) — Modul latihan pertama (ekstensi Purchase Order)

---

## 🚀 Cara Menjalankan (Docker)

### Prasyarat

- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/) terinstal

### Langkah

```bash
# 1. Clone repo ini
git clone <repo-url>
cd odoo-dev

# 2. Jalankan semua service
docker compose up -d

# 3. Buka browser
#    Odoo → http://localhost:8069
#    Default login: admin / admin
```

### Struktur Docker

```
docker-compose.yml
├── db        → PostgreSQL 15
└── odoo      → Odoo 17.0
               ├── ./addons  → /mnt/extra-addons
               └── ./config  → /etc/odoo
```

> **Dev mode** sudah aktif otomatis lewat flag `--dev=all` di `docker-compose.yml`.

---

## 📁 Struktur Direktori

```
odoo-dev/
├── addons/
│   ├── purchase_request/     # Modul Purchase Request
│   ├── mrp_custom_qc/        # Modul MRP QC, Cost Control, Reporting & IoT API
│   ├── pos_simple/           # Modul latihan Point of Sale sederhana
│   └── my_first_module/      # Modul latihan pertama
├── config/                   # Konfigurasi Odoo (odoo.conf)
├── iot_simulator.py          # Script simulator pengirim telemetri IoT
├── docker-compose.yml
└── README.md
```

---

## 🔧 Instalasi Modul

1. Pastikan Odoo sudah berjalan via Docker
2. Buka **http://localhost:8069**
3. Aktifkan **Developer Mode** → Settings → Activate the developer mode
4. Menu **Apps** → klik **Update Apps List**
5. Cari nama modul → **Install**

> Urutan instalasi yang disarankan: `purchase_request` → `mrp_custom_qc`  
> (karena `mrp_custom_qc` bergantung pada `mrp`, `account`, dan `purchase_request`)

---

## 👤 Author

**Hussain** — Technical Developer / Undergraduate IT Student  
Implementasi & pengembangan custom module Odoo 17 Community.
