from odoo import http
from odoo.http import request
import json

class PurchaseRequestController(http.Controller):

    @http.route('/api/purchase-request',
                auth='user',
                methods=['GET'],
                type='http',
                csrf=False)
    def get_purchase_requests(self, **kwargs):
        records = request.env['purchase.request'].search([])
        data = []
        for r in records:
            data.append({
                'id': r.id,
                'nama': r.nama,
                'tanggal': str(r.request_date),
                'diminta_oleh': r.requested_by.name,
                'departmen': r.department or '',
                'status': r.purchase_request_state,
                'jumlah_item': len(r.line_ids),
            })
        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')]
        )

    @http.route('/api/purchase-request/<int:request_id>',
                auth='user',
                methods=['GET'],
                type='http',
                csrf=False)
    def get_purchase_request_detail(self, record_id, **kwargs):
        record = request.env['purchase.request'].browse[record_id]
        if not record.exist():
            return request.make_response(
                json.dumps({'error':'Record not found'}),
                headers=[('Content-Type','Application/json')],
                status=404
                )
        data={
            'id': record.id,
            'nama': record.nama,
            'tanggal': str(record.request_date),
            'diminta_oleh': record.requested_by.name,
            'departemen': record.department or '',
            'status': record.purchase_request_state,
            'catatan': record.notes or '',
            'items': [{
                'product_name': line.product.name,
                'quantity': line.quantity,
                'uom': line.uom,
                'estimated_price': line.estimated_price,
            }for line in record.line_ids]
        }
        return request.make_response(
            json.dumps(data, indent=2),
            headers= [('Content-Type', 'application/json')]
        )