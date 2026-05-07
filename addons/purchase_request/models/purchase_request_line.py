from odoo import models, fields

class PurchaseRequestLine(models.Model):
    _name = 'purchase.request.line'
    _description = 'Line Item Permintaan Pembelian'

    request_id = fields.Many2one('purchase.request', string='Permintaan Pembelian', ondelete='cascade')
    product_name = fields.Char(string='Nama Produk', required=True)
    quantity = fields.Float(string='Jumlah', required=True)
    uom = fields.Char(string='Satuan (pcs, kg, box, dll)', required=True)
    estimated_price = fields.Float(string='Harga Perkiraan')
   