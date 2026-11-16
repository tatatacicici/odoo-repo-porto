{
    'name': 'Nusantara MRP Quality, Cost Control & IoT',
    'version': '17.0.2.0.0',
    'category': 'Manufacturing',
    'summary': 'QC Scrap Accounting, Cost Threshold Approval, IoT API & Job Costing Reports',
    'author': 'Hussain',
    'license': 'LGPL-3',
    'depends': ['mrp', 'account', 'purchase_request'],
    'data': [
        'security/mrp_security.xml',
        'security/ir.model.access.csv',
        'views/mrp_production_qc_views.xml',
        'reports/mrp_qc_certificate_report.xml',
        'wizards/mrp_cost_excel_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
}