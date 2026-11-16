{
    'name': 'POS Simple',
    'version': '17.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Sales/Point of Sales',
    'summary': 'Modul Latihan Point of Sale Sederhana',
    'author': 'Hussain',
    'depends': ['base','mail','product'],
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'wizards/cancel_wizard_views.xml',
        'views/pos_order_views.xml',
        'reports/report_pos_receipt.xml'
    ],
    'installable': True,
    'auto_install': False,

}