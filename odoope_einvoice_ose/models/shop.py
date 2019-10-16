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

from datetime import date, datetime, timedelta
from odoo.fields import Date, Datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, AccessError

class EinvoiceShop(models.Model):
    _inherit = 'einvoice.shop'
    
    einvoice_of_url = fields.Char('URL')
    einvoice_of_token = fields.Char('Token')
    einvoice_supplier = fields.Many2one('einvoice.supplier', string='PSE / OSE', related='company_id.einvoice_supplier')   
    einvoice_supplier_code = fields.Char('Code of supplier', related='einvoice_supplier.code')
    format_print = fields.Selection(string='Format print', selection=[('a4', 'A4'), ('ticket', 'Ticket'),])
    