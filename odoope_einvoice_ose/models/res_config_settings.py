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

from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    einvoice_supplier = fields.Many2one('einvoice.supplier', string='PSE / OSE', related='company_id.einvoice_supplier', readonly=False)
    einvoice_supplier_code = fields.Char('Code of supplier', related='einvoice_supplier.code')


