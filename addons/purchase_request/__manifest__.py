{
    'name': 'Purchase Request',
    'version': '17.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Custom',
    'summary':'Modul Untuk Re-check Request Pembelian',
    'author': 'Hussain',
    'depends': ['base','mail'],
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'wizards/reject_wizard_views.xml',
        'views/purchase_request_views.xml',
        'reports/report_purchase_request.xml',
    ],
    'installable': True,
    'auto_install': False,
}