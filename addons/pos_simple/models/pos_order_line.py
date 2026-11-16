from odoo import models, fields, api


class PosOrderLine(models.Model):
    _name = 'pos.order.line.simple'
    _description = 'Line Item Penjualan PoS'

    order_id = fields.Many2one(
        'pos.order.simple',
        string='Order',
        ondelete='cascade',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Produk',
        required=True,
    )
    qty = fields.Float(
        string='Jumlah',
        required=True,
        default=1.0,
    )
    price_unit = fields.Float(
        string='Harga Satuan',
        required=True,
    )
    subtotal = fields.Float(
        string='Subtotal',
        compute='_compute_subtotal',
        store=True,
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Auto-fill harga satuan dari master produk."""
        if self.product_id:
            self.price_unit = self.product_id.list_price

    @api.depends('qty', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.qty * line.price_unit
