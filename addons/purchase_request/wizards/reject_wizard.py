from odoo import models, fields

class PurchaseRequestRejectWizard(models.TransientModel):
    _name = 'purchase.request.reject.wizard'
    _description = 'Wizard Penolakan Purchase'

    request_id = fields.Many2one('purchase.request', string='Purchase Request')
    reason = fields.Text(string='Alasan Penolakan', required=True)

    def action_confirm_reject(self):
        self.request_id.write({
            'purchase_request_state':'rejected',
            'rejection_reason' : self.reason
        })
        return{'type':'ir.actions.act_window_close'}