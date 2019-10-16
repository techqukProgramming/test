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

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError


class AccountInvoiceRefund(models.TransientModel):
    """Credit Notes"""

    _inherit = "account.invoice.refund"
    _description = "Credit Note"
    
    @api.model
    def _default_type(self):
        return self.env['einvoice.catalog.09'].search([('code','=','01')],limit=1)
    
    credit_note_type = fields.Many2one('einvoice.catalog.09', string='Credit note type', required=True, help='Catalog 09: Type of Credit note', default=_default_type)
    shop_id = fields.Many2one('einvoice.shop', 'Shop')
    
    @api.onchange('credit_note_type')
    def onchange_credit_note_type(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        if active_id:
            inv = self.env['account.invoice'].browse(active_id)
        if not self.description and self.credit_note_type:
            self.description = (active_id and (str(inv.einv_serie) + '-' + str(inv.einv_number)) or '') + ', ' + self.credit_note_type.name
    
    @api.multi
    def invoice_refund(self):
        data_refund = self.read(['filter_refund'])[0]['filter_refund']
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        if active_id:
            inv = self.env['account.invoice'].browse(active_id)
        if self.credit_note_type and active_id:
            return self.with_context(credit_note_type = self.credit_note_type.id,
                                     invoice = inv).compute_refund(data_refund)
        return super(AccountInvoiceRefund, self).invoice_refund()
