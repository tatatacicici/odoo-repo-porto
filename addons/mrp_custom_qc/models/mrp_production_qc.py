from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # --- 1. FIELD QUALITY CONTROL & IOT TELEMETRY ---
    qc_status = fields.Selection([
        ('pending', 'Belum Diperiksa'),
        ('pass', 'Lolos QC (Pass)'),
        ('fail', 'Gagal QC (Fail & Scrap)')
    ], string='Status QC', default='pending', tracking=True)
    
    qc_notes = fields.Text(string='Catatan QC', tracking=True)
    qc_inspector_id = fields.Many2one('res.users', string='Inspektur QC', tracking=True)
    
    # Field khusus untuk menampung data dari alat IoT di QC Testing Station
    iot_voltage = fields.Float(string='Tegangan Uji IoT (V)', tracking=True)
    iot_current = fields.Float(string='Arus Uji IoT (A)', tracking=True)
    iot_last_sync = fields.Datetime(string='Waktu Sync IoT', readonly=True)

    # Referensi dokumen yang terbentuk otomatis saat QC Scrap
    scrap_move_id = fields.Many2one('account.move', string='Jurnal Kerugian QC', readonly=True)
    scrap_pr_id = fields.Many2one('purchase.request', string='Auto Purchase Request', readonly=True)
    scrap_cost = fields.Float(string='Biaya Kerugian Scrap QC', readonly=True, tracking=True)

    # --- 2. FIELD COST THRESHOLD & APPROVAL (COMPUTED FIELDS) ---
    cost_approval_state = fields.Selection([
        ('normal', 'Within Budget (<= 10%)'),
        ('waiting_cost_approval', 'Waiting Manager Approval (> 10%)'),
        ('approved', 'Cost Overrun Approved')
    ], string='Status Plafon Biaya', default='normal', tracking=True)

    estimated_material_cost = fields.Float(
        string='Estimasi Biaya Material (BoM)',
        compute='_compute_production_costs',
        store=True
    )
    estimated_operation_cost = fields.Float(
        string='Estimasi Biaya Work Center (BoM)',
        compute='_compute_production_costs',
        store=True
    )
    estimated_total_cost = fields.Float(
        string='Total Estimasi Biaya (BoM)',
        compute='_compute_production_costs',
        store=True
    )

    actual_material_cost = fields.Float(
        string='Aktual Biaya Material',
        compute='_compute_production_costs',
        store=True
    )
    actual_operation_cost = fields.Float(
        string='Aktual Biaya Work Center',
        compute='_compute_production_costs',
        store=True
    )
    actual_total_cost = fields.Float(
        string='Total Aktual Biaya Produksi',
        compute='_compute_production_costs',
        store=True
    )

    cost_variance_amount = fields.Float(
        string='Selisih Biaya (Rp)',
        compute='_compute_production_costs',
        store=True
    )
    cost_variance_pct = fields.Float(
        string='Persentase Selisih (%)',
        compute='_compute_production_costs',
        store=True
    )

    @api.depends(
        'product_qty',
        'bom_id',
        'bom_id.bom_line_ids.product_qty',
        'bom_id.bom_line_ids.product_id.standard_price',
        'bom_id.operation_ids.time_cycle_manual',
        'bom_id.operation_ids.workcenter_id.costs_hour',
        'move_raw_ids.product_uom_qty',
        'move_raw_ids.quantity',
        'move_raw_ids.state',
        'move_raw_ids.product_id.standard_price',
        'workorder_ids.duration',
        'workorder_ids.workcenter_id.costs_hour'
    )
    def _compute_production_costs(self):
        for record in self:
            # A. HITUNG ESTIMASI DARI BOM (Untuk jumlah product_qty yang diproduksi)
            est_mat = 0.0
            est_op = 0.0
            if record.bom_id:
                bom_ratio = record.product_qty / (record.bom_id.product_qty or 1.0)
                for line in record.bom_id.bom_line_ids:
                    est_mat += (line.product_qty * bom_ratio) * line.product_id.standard_price
                for op in record.bom_id.operation_ids:
                    # time_cycle_manual dalam menit, dibagi 60 jadi jam, dikali biaya per jam
                    hours = ((op.time_cycle_manual * bom_ratio) / 60.0)
                    est_op += hours * op.workcenter_id.costs_hour

            record.estimated_material_cost = est_mat
            record.estimated_operation_cost = est_op
            record.estimated_total_cost = est_mat + est_op

            # B. HITUNG AKTUAL DARI PERGERAKAN STOK & DURASI WORK ORDER
            act_mat = 0.0
            for move in record.move_raw_ids.filtered(lambda m: m.state != 'cancel'):
                # Ambil quantity aktual (jika sudah diisi) atau product_uom_qty
                qty_used = move.quantity if move.quantity > 0 else move.product_uom_qty
                act_mat += qty_used * move.product_id.standard_price

            act_op = 0.0
            for wo in record.workorder_ids:
                # wo.duration dalam menit -> konversi ke jam
                actual_hours = (wo.duration / 60.0) if wo.duration > 0 else (wo.duration_expected / 60.0)
                act_op += actual_hours * wo.workcenter_id.costs_hour

            record.actual_material_cost = act_mat
            record.actual_operation_cost = act_op
            record.actual_total_cost = act_mat + act_op

            # C. HITUNG VARIANCE (SELISIH)
            variance = record.actual_total_cost - record.estimated_total_cost
            record.cost_variance_amount = variance
            if record.estimated_total_cost > 0:
                record.cost_variance_pct = (variance / record.estimated_total_cost) * 100.0
            else:
                record.cost_variance_pct = 0.0

    # --- 3. TOMBOL REQUEST MANAGER APPROVAL & APPROVE COST ---
    def action_request_cost_approval(self):
        for record in self:
            record.cost_approval_state = 'waiting_cost_approval'
            record.message_post(
                body=f"⚠️ Permintaan Approval Plafon Biaya diajukan oleh {self.env.user.name}. "
                     f"Biaya aktual membengkak {record.cost_variance_pct:.2f}% (Rp {record.cost_variance_amount:,.2f})."
            )

    def action_approve_cost(self):
        if not self.env.user.has_group('mrp_custom_qc.group_mrp_cost_approver'):
            raise ValidationError("Akses Ditolak! Hanya MRP Manager (Cost Approver) yang berhak menyetujui kelebihan plafon biaya.")
        
        for record in self:
            record.cost_approval_state = 'approved'
            record.message_post(
                body=f"✅ Kelebihan biaya produksi (+{record.cost_variance_pct:.2f}%) telah DISETUJUI oleh Manager: {self.env.user.name}."
            )

    # --- 4. OVERRIDE BUTTON_MARK_DONE (VALIDASI QC & COST THRESHOLD 10%) ---
    def button_mark_done(self):
        for record in self:
            # Validasi 1: Wajib Lolos QC
            if record.qc_status != 'pass':
                raise ValidationError(
                    "Proses Produksi Diblokir!\n"
                    "MO tidak boleh diselesaikan (Mark as Done) sebelum melewati QC Check dengan status 'Lolos QC (Pass)'."
                )

            # Validasi 2: Cek Plafon Biaya (Cost Threshold > 10%)
            if record.cost_variance_pct > 10.0 and record.cost_approval_state != 'approved':
                record.cost_approval_state = 'waiting_cost_approval'
                if not self.env.user.has_group('mrp_custom_qc.group_mrp_cost_approver'):
                    raise ValidationError(
                        f"Plafon Biaya Terlampaui (+{record.cost_variance_pct:.2f}%)!\n"
                        f"Estimasi BoM: Rp {record.estimated_total_cost:,.2f}\n"
                        f"Aktual Produksi: Rp {record.actual_total_cost:,.2f}\n\n"
                        f"Teknisi tidak dapat menyelesaikan MO ini. Silakan klik tombol 'Request Manager Approval' "
                        f"atau minta MRP Manager melakukan Approve Cost."
                    )
                else:
                    raise ValidationError(
                        f"Perhatian Manager: Biaya MO ini melampaui estimasi BoM sebesar +{record.cost_variance_pct:.2f}%.\n"
                        f"Silakan klik tombol 'Approve Cost Overrun' di bagian atas terlebih dahulu sebelum menyelesaikan MO."
                    )

        return super(MrpProduction, self).button_mark_done()

    # --- 5. TOMBOL FAIL & SCRAP (AUTO PR + AUTO ACCOUNTING JOURNAL) ---
    def action_fail_and_scrap(self):
        for record in self:
            if record.scrap_move_id:
                raise UserError("Proses Fail & Scrap sudah pernah dijalankan untuk MO ini!")

            record.qc_status = 'fail'
            record.qc_inspector_id = self.env.user

            # Hitung total kerugian dari komponen yang terpakai
            loss_amount = record.actual_material_cost
            if loss_amount <= 0:
                raise UserError("Nilai material 0, tidak dapat mencatat jurnal kerugian.")

            # A. OTOMATIS BUAT DRAF PURCHASE REQUEST (Untuk mengganti komponen yang di-scrap)
            pr_lines = []
            for move in record.move_raw_ids.filtered(lambda m: m.state != 'cancel'):
                qty_scrap = move.quantity if move.quantity > 0 else move.product_uom_qty
                pr_lines.append((0, 0, {
                    'product_name': move.product_id.name,
                    'quantity': qty_scrap,
                    'uom': move.product_uom.name,
                    'estimated_price': move.product_id.standard_price,
                }))

            if pr_lines:
                new_pr = self.env['purchase.request'].create({
                    'nama': 'New',
                    'department': 'QC / Produksi (Replacement Scrap)',
                    'notes': f'Otomatis dibuat karena kegagalan QC (Scrap) pada MO: {record.name}',
                    'line_ids': pr_lines,
                })
                record.scrap_pr_id = new_pr.id

            # B. OTOMATIS BUAT JURNAL AKUNTANSI KERUGIAN QC (account.move)
            stock_account = record.product_id.categ_id.property_stock_valuation_account_id
            expense_account = record.product_id.categ_id.property_account_expense_categ_id

            if not stock_account or not expense_account:
                raise UserError("Akun Persediaan atau Akun Beban belum diatur di Kategori Produk!")

            journal = self.env['account.journal'].search([('type', '=', 'general')], limit=1)
            move_vals = {
                'journal_id': journal.id,
                'date': fields.Date.context_today(self),
                'ref': f"QC Defective Scrap - {record.name}",
                'line_ids': [
                    (0, 0, {
                        'name': f"Beban Kerugian QC (Scrap) - {record.name}",
                        'account_id': expense_account.id,
                        'debit': loss_amount,
                        'credit': 0.0,
                    }),
                    (0, 0, {
                        'name': f"Pengurangan Persediaan Scrap - {record.name}",
                        'account_id': stock_account.id,
                        'debit': 0.0,
                        'credit': loss_amount,
                    }),
                ]
            }
            new_move = self.env['account.move'].create(move_vals)
            new_move.action_post()

            record.scrap_move_id = new_move.id
            record.scrap_cost = loss_amount
            record.qc_notes = (
                f"[QC FAILED & SCRAPPED]\n"
                f"- Jurnal Kerugian: {new_move.name} (Rp {loss_amount:,.2f})\n"
                f"- Auto Purchase Request: {record.scrap_pr_id.nama if record.scrap_pr_id else '-'}"
            )