from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PosOrder(models.Model):
    _name = 'pos.order.simple'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Order Point of Sale'
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Nomor Order',
        readonly=True,
        default='New',
        tracking=True,
    )
    date = fields.Datetime(
        string='Tanggal & Waktu',
        default=fields.Datetime.now,
        tracking=True,
    )
    cashier_id = fields.Many2one(
        'res.users',
        string='Kasir',
        default=lambda self: self.env.user,
        tracking=True,
    )
    customer_name = fields.Char(
        string='Nama Pelanggan',
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Dikonfirmasi'),
        ('paid', 'Dibayar'),
        ('cancelled', 'Dibatalkan'),
    ], string='Status', default='draft', readonly=True, tracking=True)

    line_ids = fields.One2many(
        'pos.order.line.simple',
        'order_id',
        string='Daftar Belanja',
    )
    notes = fields.Text(string='Catatan')

    # === Computed Fields ===
    amount_total = fields.Float(
        string='Total',
        compute='_compute_amount_total',
        store=True,
    )
    amount_paid = fields.Float(
        string='Jumlah Dibayar',
    )
    amount_change = fields.Float(
        string='Kembalian',
        compute='_compute_amount_change',
        store=True,
    )

    # === Cancel Fields ===
    cancel_reason = fields.Text(
        string='Alasan Pembatalan',
        readonly=True,
        tracking=True,
    )

    # === Auto Sequence ===
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'name' not in vals or vals['name'] == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'pos.order.simple'
                ) or 'New'
        return super().create(vals_list)

    # === Computed Methods ===
    @api.depends('line_ids.subtotal')
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = sum(order.line_ids.mapped('subtotal'))

    @api.depends('amount_total', 'amount_paid')
    def _compute_amount_change(self):
        for order in self:
            order.amount_change = order.amount_paid - order.amount_total

    # === Workflow Actions ===
    def action_confirm(self):
        for order in self:
            if not order.line_ids:
                raise ValidationError(
                    'Tidak dapat mengkonfirmasi order tanpa item belanja!'
                )
            order.state = 'confirmed'

    def action_pay(self):
        for order in self:
            if order.state != 'confirmed':
                raise ValidationError(
                    'Hanya order yang sudah dikonfirmasi yang dapat dibayar.'
                )
            if order.amount_paid <= 0:
                raise ValidationError(
                    'Masukkan jumlah pembayaran terlebih dahulu!'
                )
            if order.amount_paid < order.amount_total:
                raise ValidationError(
                    'Jumlah pembayaran kurang dari total belanja!\n'
                    f'Total: {order.amount_total:,.0f} | '
                    f'Dibayar: {order.amount_paid:,.0f}'
                )
            order.state = 'paid'

    def action_cancel(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Alasan Pembatalan',
            'res_model': 'pos.order.cancel.wizard',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'new',
            'context': {
                'default_order_id': self.id,
            },
        }

    def action_set_to_draft(self):
        for order in self:
            order.state = 'draft'
