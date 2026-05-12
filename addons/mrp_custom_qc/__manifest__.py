{
    'name': 'MRP Custom QC',
    'version': '17.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Menambahkan fitur Quality Control pada Manufacturing Order',
    'author': 'Hussain',
    'depends': ['mrp','purchase_request'], 
    'data':[
        'views/mrp_production_qc_views.xml',
    ],
    'installable': True,
    'application': False,
}