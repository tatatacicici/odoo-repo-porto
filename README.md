# 🏭 Odoo 17 Custom Addons

Kumpulan modul custom Odoo 17 yang dikembangkan sebagai portofolio belajar Odoo development, mencakup manajemen pembelian, manufacturing, dan quality control.

## 🛠️ Tech Stack

| Teknologi | Keterangan |
|---|---|
| Odoo 17 Community | ERP Framework |
| Python 3 | Backend logic & ORM |
| XML (QWeb, Views) | View definitions & reports |
| PostgreSQL 15 | Database |
| Docker & Docker Compose | Containerized environment |

## 📦 Modul yang Tersedia

### 1. [`purchase_request`](./addons/purchase_request/)
Modul manajemen permintaan pembelian internal sebelum dibuat Purchase Order resmi.

- Approval workflow: **Draft → Diajukan → Disetujui / Ditolak**
- Nomor otomatis (format `PR/YYYY/001`)
- Reject wizard dengan alasan penolakan
- PDF report dengan tanda tangan

### 2. [`mrp_custom_qc`](./addons/mrp_custom_qc/)
Ekstensi modul Manufacturing (MRP) dengan fitur Quality Control terintegrasi.

- Tab Quality Control di form Manufacturing Order
- Blokir penyelesaian produksi jika QC belum lolos
- Auto-generate Purchase Request saat stok bahan baku kurang

### 3. [`my_first_module`](./addons/my_first_module/)
Modul latihan pertama — ekstensi pada Purchase Order untuk menambahkan catatan produk.

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
│   ├── mrp_custom_qc/        # Modul MRP + Quality Control
│   └── my_first_module/      # Modul latihan pertama
├── config/                   # Konfigurasi Odoo (odoo.conf)
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
> (karena `mrp_custom_qc` bergantung pada `purchase_request`)

---

## 👤 Author

**Hussain** — Undergraduate IT Student  
Portofolio project untuk belajar Odoo development.
