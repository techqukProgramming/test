# -*- coding: utf-8 -*-
{
    'name': "MODULO GUIA DE REMISION",

    'summary': """
        Módulo desarrollado para Odoo V.10+ """,

    'description': """
        Módulo que permite generar las guias de remisión de comprobantes.
    """,

    'author': "Techquk SAC",
    'version' : '1.0.0',
    'website': "http://www.techquk.com",
    "license": "OPL-1",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting & Finance',

    # any module necessary for this one to work correctly
    'depends': ['base','odoope_einvoice_base','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/vista_principal.xml',
        'views/vista_guide.xml',
        'views/guide_report.xml',
        'views/report_guide.xml',
        'views/sequence.xml',
        'data/uom_data.xml'
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 100.00,
    'currency': 'USD',
    "sequence": 1,
}