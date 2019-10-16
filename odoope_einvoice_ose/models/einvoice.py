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

from odoo import models, fields, api

class EinvoiceSupplier(models.Model):
    _name = 'einvoice.supplier'
    _description = 'OSE Supplier'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Name', size=128, index=True, required=True)
    invoice_url = fields.Char(string='URL for invoices')
    authorization_message = fields.Html(string='Authorization Message', help="The message will be printed on the invoice")

class EinvoiceCatalog01(models.Model):
    _inherit = "einvoice.catalog.01"

    type_of = fields.Selection([('1','FACTURA'),('2','BOLETA'),('3','NOTA DE CREDITO'),('4','NOTA DE DEBITO')],
                    string='Type of document', 
                    help='Used by Odoo Fact. \n'\
                            '1 = FACTURA \n'\
                            '2 = BOLETA \n'\
                            '3 = NOTA DE CRÉDITO \n'\
                            '4 = NOTA DE DÉBITO \n')
                            
class EinvoiceCatalog07(models.Model):
    _inherit = "einvoice.catalog.07"

    code_of = fields.Char(string="Code by Odoo Fact")
    
