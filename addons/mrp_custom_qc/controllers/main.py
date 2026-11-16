from odoo import http, fields
from odoo.http import request
from markupsafe import Markup
import json


class MrpQcController(http.Controller):

    @http.route('/api/v1/mrp/qc-result', type='http', auth='public', methods=['POST'], csrf=False)
    def receive_qc_result(self, **kwargs):
        try:
            # 1. Validasi Autentikasi API Key dari Header (X-API-Key)
            api_key_header = request.httprequest.headers.get('X-API-Key')
            valid_api_key = request.env['ir.config_parameter'].sudo().get_param(
                'nusantara.iot_api_key', default='NUSANTARA-IOT-SECRET-2026'
            )

            if not api_key_header or api_key_header != valid_api_key:
                return request.make_response(
                    json.dumps({
                        'status': 'error',
                        'code': 401,
                        'message': 'Unauthorized: Invalid or missing X-API-Key header.'
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=401
                )

            # 2. Parse Payload JSON dari Perangkat IoT
            payload = json.loads(request.httprequest.data.decode('utf-8'))
            mo_name = payload.get('mo_name')
            voltage = payload.get('voltage')
            current = payload.get('current')
            qc_status = payload.get('status')  # 'pass' atau 'fail'
            qc_notes = payload.get('notes', '')
            auto_scrap = payload.get('auto_scrap', False)

            if not mo_name or qc_status not in ('pass', 'fail') or voltage is None or current is None:
                return request.make_response(
                    json.dumps({
                        'status': 'error',
                        'code': 400,
                        'message': 'Bad Request: Field mo_name, voltage, current, dan status (pass/fail) wajib diisi.'
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            # 3. Cari Dokumen Manufacturing Order (MO)
            mo = request.env['mrp.production'].sudo().search([('name', '=', mo_name)], limit=1)
            if not mo:
                return request.make_response(
                    json.dumps({
                        'status': 'error',
                        'code': 404,
                        'message': f'Manufacturing Order {mo_name} tidak ditemukan.'
                    }),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )

            # 4. Update Data Telemetri IoT & Status QC pada MO
            sync_time = fields.Datetime.now()
            mo.sudo().write({
                'iot_voltage': float(voltage),
                'iot_current': float(current),
                'iot_last_sync': sync_time,
                'qc_status': qc_status,
                'qc_notes': f"[IoT QC Station] V={voltage}V | I={current}A. {qc_notes}".strip()
            })

            # 5. Catat Log ke Chatter (Audit Trail)
            status_badge = "✅ LOLOS UJI (PASS)" if qc_status == 'pass' else "❌ GAGAL UJI (FAIL)"
            chatter_body = Markup(f"""
                <b>📡 Telemetri IoT QC Testing Station Diterima</b>
                <ul>
                    <li><b>Hasil Uji:</b> {status_badge}</li>
                    <li><b>Tegangan (Voltage):</b> {voltage} V</li>
                    <li><b>Arus (Current):</b> {current} A</li>
                    <li><b>Waktu Sinkronisasi:</b> {sync_time} UTC</li>
                    <li><b>Catatan Mesin:</b> {qc_notes or '-'}</li>
                </ul>
            """)
            mo.sudo().message_post(body=chatter_body)

            # 6. Opsional: Jika Gagal QC dan auto_scrap=True, langsung jalankan Fail & Scrap (Bikin PR + Jurnal)
            scrap_info = None
            if qc_status == 'fail' and auto_scrap and not mo.scrap_move_id:
                mo.sudo().action_fail_and_scrap()
                scrap_info = {
                    'auto_pr': mo.scrap_pr_id.nama if mo.scrap_pr_id else None,
                    'scrap_journal': mo.scrap_move_id.name if mo.scrap_move_id else None,
                    'scrap_cost': mo.scrap_cost
                }

            return request.make_response(
                json.dumps({
                    'status': 'success',
                    'code': 200,
                    'message': f'Telemetri IoT untuk {mo_name} berhasil disimpan.',
                    'data': {
                        'mo_name': mo.name,
                        'qc_status': mo.qc_status,
                        'iot_voltage': mo.iot_voltage,
                        'iot_current': mo.iot_current,
                        'synced_at': str(sync_time),
                        'scrap_Execution': scrap_info
                    }
                }),
                headers=[('Content-Type', 'application/json')],
                status=200
            )

        except Exception as e:
            return request.make_response(
                json.dumps({'status': 'error', 'code': 500, 'message': str(e)}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )