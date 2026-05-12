# 🔬 MRP Custom QC — Odoo 17 Custom Module

Modul ekstensi untuk **Manufacturing (MRP)** Odoo 17 yang menambahkan fitur **Quality Control (QC)** langsung pada Manufacturing Order, serta integrasi otomatis dengan modul `purchase_request` saat stok bahan baku tidak mencukupi.

---

## ✨ Fitur Utama

| Fitur | Keterangan |
|---|---|
| **Tab Quality Control** | Tab QC tersendiri di form Manufacturing Order |
| **Status QC** | Belum Diperiksa / Lolos QC / Gagal QC |
| **Blokir Penyelesaian** | MO tidak bisa di-*done* jika QC belum lolos |
| **Inspektur QC** | Field many2one ke user sebagai penanggung jawab QC |
| **Catatan QC** | Field teks bebas untuk hasil inspeksi |
| **Auto Purchase Request** | Saat MO dikonfirmasi & stok kurang → PR otomatis dibuat |
| **Tracking** | Semua perubahan QC tercatat di chatter MO |

---

## 🔄 Alur Kerja

### Quality Control
```
[Konfirmasi MO]
      │
      ▼
 Cek stok bahan baku
      │
      ├─ Stok kurang ──▶ [Auto-buat Purchase Request]
      │
      └─ Lanjut produksi
            │
            ▼
    [Isi form QC]
     - Pilih Status QC
     - Pilih Inspektur
     - Tulis catatan
            │
            ▼
   Status = "Lolos QC"?
      │              │
     Ya             Tidak
      │              │
      ▼              ▼
  [Mark Done]   ❌ Error: Tidak bisa
                   selesaikan produksi
```

### Auto Purchase Request
Ketika Manufacturing Order **dikonfirmasi**, sistem otomatis mengecek semua bahan baku (`move_raw_ids`). Jika `qty_available < product_uom_qty`, sistem membuat Purchase Request baru dengan:
- Nama: `Auto-PR dari [MO Name]`
- Departemen: `Produksi / Pabrik`
- Line item berisi produk yang kekurangan beserta jumlah kekurangannya

---

## 📋 Model & Field

### `mrp.production` (extend)

| Field | Tipe | Keterangan |
|---|---|---|
| `qc_status` | Selection | `pending` / `pass` / `fail` |
| `qc_notes` | Text | Catatan hasil inspeksi |
| `qc_inspector_id` | Many2one | User inspektur QC |

### Method yang Di-override / Ditambahkan

| Method | Keterangan |
|---|---|
| `button_mark_done()` | Override — validasi `qc_status == 'pass'` sebelum selesai |
| `action_confirm()` | Override — cek stok & buat PR otomatis jika kurang |

---

## 📁 Struktur Modul

```
mrp_custom_qc/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   └── mrp_production_qc.py   # Extend mrp.production
└── views/
    └── mrp_production_qc_views.xml  # Inherit form view MRP, tambah tab QC
```

---

## 🔗 Dependensi

| Modul | Alasan |
|---|---|
| `mrp` | Model `mrp.production` yang di-extend |
| `purchase_request` | Membuat PR otomatis saat stok kurang |

> **Urutan instalasi:** Install `purchase_request` terlebih dahulu, baru `mrp_custom_qc`.

---

## 🚀 Instalasi

1. Pastikan modul `purchase_request` sudah terinstal
2. Copy folder `mrp_custom_qc` ke direktori `addons` Odoo (atau mount via Docker)
3. Restart Odoo server
4. Aktifkan **Developer Mode** → Settings → Activate the developer mode
5. **Apps** → **Update Apps List**
6. Cari **"MRP Custom QC"** → **Install**

---

## 💡 Contoh Penggunaan

1. Buat Manufacturing Order baru
2. Klik **Konfirmasi** → jika ada bahan baku kurang, Purchase Request otomatis terbuat
3. Jalankan produksi, lalu buka tab **Quality Control**
4. Isi inspektur, pilih **Lolos QC**, tulis catatan
5. Klik **Mark as Done** → berhasil

Jika QC belum diisi atau statusnya **Gagal QC**, tombol Mark as Done akan menampilkan error:
> *"Tidak bisa menyelesaikan produksi! Status QC Harus 'Lolos QC!'"*

---

## 👤 Author

**Hussain** — Undergraduate IT Student
