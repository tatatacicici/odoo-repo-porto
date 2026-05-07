from odoo.exceptions import ValidationError 
from odoo import models, fields, api

class PurchaseRequest(models.Model):
    _name = 'purchase.request'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'nama'
    _description = 'Permintaan Pembelian'

    nama = fields.Char(string="Nama", readonly=True, default='New', tracking=True)
    request_date = fields.Date(string="Tanggal Permintaan", default=fields.Date.context_today, tracking=True)
    requested_by = fields.Many2one('res.users', string="Diminta Oleh", default=lambda self: self.env.user, tracking=True)
    department = fields.Text(string="Departemen", tracking=True)
    purchase_request_state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted','Diajukan'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
    ], string='Status Permintaan', default='draft', readonly=True, tracking=True)
    notes  = fields.Text(string = 'Catatan')
    line_ids = fields.One2many(
        'purchase.request.line', 
        'request_id', 
        string='Lines')
    rejection_reason = fields.Text(string='Alasan Penolakan', readonly=True, tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'nama' not in vals or vals['nama'] == 'New':
                vals['nama'] = self.env['ir.sequence'].next_by_code('purchase.request') or 'New'
        return super(PurchaseRequest, self).create(vals_list)



    def action_submit(self):
        for record in self:
            if not record.line_ids:
                raise ValidationError('Tidak dapat mengajukan permintaan pembelian tanpa line item.')
            record.purchase_request_state = 'submitted'
    def action_approve(self):
        for record in self:
            if record.purchase_request_state != 'submitted':
                raise ValidationError('Hanya permintaan pembelian yang sudah diajukan yang dapat disetujui.')
            record.purchase_request_state = 'approved'
    def action_reject(self):
        return {
        'type': 'ir.actions.act_window',
        'name': 'Alasan Penolakan',
        'res_model': 'purchase.request.reject.wizard',
        'view_mode': 'form',
        'views': [(False, 'form')],
        'target': 'new',
        'context': {
            'default_request_id': self.id,
        }
    }
    def action_set_to_draft(self):
        for record in self:
            record.purchase_request_state = 'draft'
            
    
