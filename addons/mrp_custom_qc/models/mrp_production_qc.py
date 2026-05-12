from odoo import models, fields, api
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    qc_status = fields.Selection([
        ('pending', 'Belum di Periksa'),
        ('pass', 'Lolos QC'),
        ('fail', 'Gagal QC')
    ], string='Status QC', default='pending', tracking=True)

    qc_notes = fields.Text(string='Catatan QC', tracking=True)
    qc_inspector_id = fields.Many2one('res.users', string='Inspektur QC', tracking=True)

    def button_mark_done(self):
        for record in self:
            if record.qc_status != 'pass':
                raise UserError("Tidak bisa menyelesaikan produksi! Status QC Harus 'Lolos  QC!'")
        return super(MrpProduction, self).button_mark_done()
    
    def action_confirm(self):
        res = super(MrpProduction, self).action_confirm()

        for record in self:
            shortage_lines= []

            for move in record.move_raw_ids:
                if move.product_id.qty_available < move.product_uom_qty:
                    kekurangan = move.product_uom_qty - move.product_id.qty_available

                    shortage_lines.append((0, 0, {
                        'product_name': move.product_id.name,
                        'quantity': kekurangan,
                        'uom': move.product_uom.name,
                        'estimated_price': move.product_id.standard_price,
                    }))
            
            if shortage_lines:
                self.env['purchase.request'].create({
                    'nama': 'Auto-PR dari ' + record.name,
                    'department': 'Produksi / Pabrik',
                    'notes': 'Dibuat otomatis karena stok bahan baku kurang untuk MO: ' + record.name,
                    'line_ids': shortage_lines
                })
        return res
    