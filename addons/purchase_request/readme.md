# 🛒 Purchase Request — Odoo 17 Custom Module

Modul custom Odoo 17 untuk manajemen **permintaan pembelian internal** sebelum dibuatkan Purchase Order resmi. Mendukung approval workflow lengkap dengan penolakan beralasan dan laporan PDF.

---

## ✨ Fitur Utama

| Fitur | Keterangan |
|---|---|
| **Nomor Otomatis** | Format `PR/YYYY/001` via ir.sequence |
| **Approval Workflow** | Draft → Diajukan → Disetujui / Ditolak |
| **Reject Wizard** | Dialog konfirmasi penolakan beserta alasan |
| **Validasi Submit** | Tidak bisa diajukan tanpa line item |
| **PDF Report** | Cetak permintaan pembelian dengan tanda tangan |
| **Chatter & Tracking** | Log perubahan status secara otomatis |
| **Auto-PR dari MRP** | Purchase Request dibuat otomatis jika stok MO kurang *(via modul `mrp_custom_qc`)* |

---

## 🔄 Workflow Status

```
[Draft] ──submit──▶ [Diajukan] ──approve──▶ [Disetujui]
   ▲                     │
   │                  reject
   │                     ▼
   └──── reset ──── [Ditolak]
```

| Tombol | Aksi | Syarat |
|---|---|---|
| **Ajukan** | Draft → Diajukan | Harus ada minimal 1 line item |
| **Setujui** | Diajukan → Disetujui | Status harus "Diajukan" |
| **Tolak** | → Ditolak (+ alasan) | Buka wizard isi alasan penolakan |
| **Reset ke Draft** | Ditolak → Draft | — |

---

## 📋 Model & Field

### `purchase.request` (Header)

| Field | Tipe | Keterangan |
|---|---|---|
| `nama` | Char | Nomor PR otomatis (readonly) |
| `request_date` | Date | Tanggal permintaan |
| `requested_by` | Many2one | User yang membuat PR |
| `department` | Text | Nama departemen pemohon |
| `purchase_request_state` | Selection | Status workflow |
| `notes` | Text | Catatan tambahan |
| `rejection_reason` | Text | Diisi saat ditolak (readonly) |
| `line_ids` | One2many | Daftar item yang diminta |

### `purchase.request.line` (Detail Item)

| Field | Tipe | Keterangan |
|---|---|---|
| `product_name` | Char | Nama produk/barang |
| `quantity` | Float | Jumlah yang diminta |
| `uom` | Char | Satuan (pcs, kg, box, dll) |
| `estimated_price` | Float | Harga perkiraan per satuan |

### `purchase.request.reject.wizard` (Wizard)

| Field | Tipe | Keterangan |
|---|---|---|
| `request_id` | Many2one | Relasi ke PR yang ditolak |
| `reason` | Text | Alasan penolakan (wajib diisi) |

---

## 📁 Struktur Modul

```
purchase_request/
├── __manifest__.py
├── __init__.py
├── data/
│   └── sequence.xml              # Sequence PR/YYYY/001
├── models/
│   ├── __init__.py
│   ├── purchase_request.py       # Model header & workflow actions
│   └── purchase_request_line.py  # Model line item
├── wizards/
│   ├── __init__.py
│   ├── reject_wizard.py          # TransientModel untuk penolakan
│   └── reject_wizard_views.xml   # Form dialog reject
├── reports/
│   └── report_purchase_request.xml  # QWeb PDF template
├── security/
│   └── ir.model.access.csv       # Hak akses model
└── views/
    └── purchase_request_views.xml   # List, form, action, menu
```

---

## 🚀 Instalasi

1. Copy folder `purchase_request` ke direktori `addons` Odoo (atau mount via Docker)
2. Restart Odoo server
3. Aktifkan **Developer Mode** → Settings → Activate the developer mode
4. **Apps** → **Update Apps List**
5. Cari **"Purchase Request"** → **Install**

---

## 📸 Screenshot

**Daftar Purchase Request**
![Halaman daftar semua purchase request](image-1.png)

**Form Purchase Request**
![Form input dan approval workflow](image.png)

**PDF Report**
![Hasil cetak purchase request](image-2.png)

---

## 🔗 Dependensi

- `base` — Odoo core
- `mail` — Chatter & activity tracking

---

## 👤 Author

**Hussain** — Undergraduate IT Student