# -*- coding: utf-8 -*-
{
    'name': "REQUERIMIENTOS TQ",

    'summary': """
        El proposito en que se ha desarrollado este modulo es para facilitar la tarea de gestionar los requerimientos de los trabajadores
        en sus diferentes puestos de trabajo.
        """,

    'description': """
        Módulo que nos ayudará a gestionar los requerimientos. 
    """,

    'author': "Sistemas TQ",
    'website': "http://www.techquk.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchases',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/view_requeriment.xml',
        'views/sequence.xml',
        'views/purchase_purchase_views.xml'
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 1.00,
    'currency': 'USD',
    "sequence": 1,
}