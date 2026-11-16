from odoo import models, fields


class PosOrderCancelWizard(models.TransientModel):
    _name = 'pos.order.cancel.wizard'
    _description = 'Wizard Pembatalan Order PoS'

    order_id = fields.Many2one(
        'pos.order.simple',
        string='Order',
    )
    reason = fields.Text(
        string='Alasan Pembatalan',
        required=True,
    )

    def action_confirm_cancel(self):
        self.order_id.write({
            'state': 'cancelled',
            'cancel_reason': self.reason,
        })
        return {'type': 'ir.actions.act_window_close'}
