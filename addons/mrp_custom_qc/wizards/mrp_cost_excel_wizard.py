from odoo import models, fields
from odoo.exceptions import UserError
import io
import base64

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class MrpCostExcelWizard(models.TransientModel):
    _name = 'mrp.cost.excel.wizard'
    _description = 'Wizard Laporan HPP Produksi Bulanan (Excel)'

    date_from = fields.Date(string='Dari Tanggal', required=True, default=fields.Date.context_today)
    date_to = fields.Date(string='Sampai Tanggal', required=True, default=fields.Date.context_today)
    state_filter = fields.Selection([
        ('all', 'Semua Status'),
        ('done', 'Hanya yang Selesai (Done)')
    ], string='Filter Status MO', default='all', required=True)

    excel_file = fields.Binary(string='File Excel', readonly=True)
    file_name = fields.Char(string='Nama File', readonly=True)

    def action_export_excel(self):
        self.ensure_one()
        if not xlsxwriter:
            raise UserError("Library python 'xlsxwriter' belum terinstal di server Odoo.")

        domain = [
            ('create_date', '>=', fields.Datetime.to_datetime(self.date_from)),
            ('create_date', '<=', fields.Datetime.end_of(fields.Datetime.to_datetime(self.date_to), 'day')),
        ]
        if self.state_filter == 'done':
            domain.append(('state', '=', 'done'))

        productions = self.env['mrp.production'].search(domain, order='create_date asc, id asc')
        if not productions:
            raise UserError("Tidak ditemukan data Manufacturing Order pada rentang tanggal tersebut.")

        # Buat file Excel di dalam memori (RAM)
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Rekap HPP Produksi')

        # Styling Format Excel
        title_fmt = workbook.add_format({'bold': True, 'font_size': 14})
        sub_fmt = workbook.add_format({'italic': True, 'font_size': 10, 'font_color': '#555555'})
        header_fmt = workbook.add_format({
            'bold': True, 'bg_color': '#1F4E78', 'font_color': 'white',
            'border': 1, 'align': 'center', 'valign': 'vcenter'
        })
        text_fmt = workbook.add_format({'border': 1})
        num_fmt = workbook.add_format({'border': 1, 'num_format': '#,##0.00'})
        pct_fmt = workbook.add_format({'border': 1, 'num_format': '0.00"%"'})
        total_label_fmt = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2', 'border': 1})
        total_num_fmt = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2', 'border': 1, 'num_format': '#,##0.00'})

        # Judul Laporan
        sheet.write(0, 0, 'PT NUSANTARA PANEL MANDIRI - LAPORAN REALISASI HPP PRODUKSI', title_fmt)
        sheet.write(1, 0, f'Periode: {self.date_from} s/d {self.date_to}', sub_fmt)

        # Header Kolom
        headers = [
            'No MO', 'Tanggal', 'Produk', 'Qty', 'Status MO', 'Status QC',
            'Estimasi BoM (Rp)', 'Biaya Material (Rp)', 'Biaya Operasional WC (Rp)',
            'Biaya Scrap QC (Rp)', 'Total HPP Aktual (Rp)', 'Variance (%)'
        ]
        col_widths = [16, 14, 30, 8, 12, 16, 20, 20, 24, 20, 22, 14]
        for col, (h_text, width) in enumerate(zip(headers, col_widths)):
            sheet.set_column(col, col, width)
            sheet.write(3, col, h_text, header_fmt)

        # Isi Baris Data
        row = 4
        sum_est = sum_mat = sum_op = sum_scrap = sum_total_hpp = 0.0

        for mo in productions:
            total_hpp_row = mo.actual_total_cost + mo.scrap_cost
            sheet.write(row, 0, mo.name, text_fmt)
            sheet.write(row, 1, str(mo.create_date.date()), text_fmt)
            sheet.write(row, 2, mo.product_id.display_name, text_fmt)
            sheet.write(row, 3, mo.product_qty, num_fmt)
            sheet.write(row, 4, mo.state, text_fmt)
            sheet.write(row, 5, dict(mo._fields['qc_status'].selection).get(mo.qc_status, ''), text_fmt)
            sheet.write(row, 6, mo.estimated_total_cost, num_fmt)
            sheet.write(row, 7, mo.actual_material_cost, num_fmt)
            sheet.write(row, 8, mo.actual_operation_cost, num_fmt)
            sheet.write(row, 9, mo.scrap_cost, num_fmt)
            sheet.write(row, 10, total_hpp_row, num_fmt)
            sheet.write(row, 11, mo.cost_variance_pct, pct_fmt)

            sum_est += mo.estimated_total_cost
            sum_mat += mo.actual_material_cost
            sum_op += mo.actual_operation_cost
            sum_scrap += mo.scrap_cost
            sum_total_hpp += total_hpp_row
            row += 1

        # Baris Grand Total di Bawah
        sheet.merge_range(row, 0, row, 5, 'GRAND TOTAL', total_label_fmt)
        sheet.write(row, 6, sum_est, total_num_fmt)
        sheet.write(row, 7, sum_mat, total_num_fmt)
        sheet.write(row, 8, sum_op, total_num_fmt)
        sheet.write(row, 9, sum_scrap, total_num_fmt)
        sheet.write(row, 10, sum_total_hpp, total_num_fmt)
        sheet.write(row, 11, '', total_label_fmt)

        workbook.close()
        output.seek(0)

        filename = f"Laporan_HPP_Produksi_{self.date_from}_{self.date_to}.xlsx"
        self.write({
            'excel_file': base64.b64encode(output.read()),
            'file_name': filename
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/?model=mrp.cost.excel.wizard&id={self.id}&field=excel_file&filename_field=file_name&download=true',
            'target': 'self',
        }