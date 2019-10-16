# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2019-TODAY Odoo Peru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.odooperu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
###############################################################################
{
    'name' : 'Factura Electronica Peru - PSE/OSE',
    'version' : '1.0.2',
    "license": "OPL-1",
    'author' : 'Odoo Peru',
    'category' : 'Accounting & Finance',
    'summary': 'Factura Electronica - OSE',
    'description' : """
    Electronic invoice.
    ====================================

    More information in the description.
    """,
    'website': 'hhttp://www.odooperu.pe/facturacion-electronica',
    'depends' : ['base','odoope_einvoice_base','account','account_cancel'],
    'data': [
        'wizard/send_invoice_cancel_views.xml',
        'wizard/account_invoice_debit_view.xml',
        'wizard/account_global_discount_view.xml',
        'views/account_invoice_views.xml',
        'views/account_views.xml', 
        'views/einvoice_views.xml',  
        'views/res_config_settings_views.xml',  
        'views/account_invoice_report.xml',
        'views/report_invoice.xml',
        'views/report_ticket.xml',
        'views/shop_views.xml',
        'views/company_views.xml',
        'wizard/send_multi_sunat.xml',        
        'wizard/account_invoice_refund_view.xml',        
        'data/einvoice_data.xml',      
        'security/ir.model.access.csv',
        'data/cron_account_invoice.xml',
    ],
    'qweb' : [
        
    ],
    'demo': [
        
    ],
    'test': [
        
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 560.00,
    'currency': 'EUR',
    "sequence": 1,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
