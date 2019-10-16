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

class AccountInvoiceDebit(models.TransientModel):
    """Debit Notes"""

    _name = "account.invoice.debit"
    _description = "Debit Note"

    @api.model
    def _get_reason(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        if active_id:
            inv = self.env['account.invoice'].browse(active_id)
            return inv.name
        return ''

    @api.model
    def _default_type(self):
        return self.env['einvoice.catalog.09'].search([('code','=','02')],limit=1)
    
    date_invoice = fields.Date(string='Debit Note Date', default=fields.Date.context_today, required=True)
    date = fields.Date(string='Accounting Date')
    description = fields.Char(string='Reason', required=True, default=_get_reason)
    debit_note_type = fields.Many2one('einvoice.catalog.10', string='Debit note type', required=True, help='Catalog 10: Type of Debit note', default=_default_type)
    shop_id = fields.Many2one('einvoice.shop', 'Shop')

    @api.onchange('debit_note_type')
    def onchange_debit_note_type(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        if active_id:
            inv = self.env['account.invoice'].browse(active_id)
            self.description = (active_id and (str(inv.einv_serie) + '-' + str(inv.einv_number)) or '') + ', ' + self.debit_note_type.name
    
    @api.multi
    def compute_debit(self):
        inv_obj = self.env['account.invoice']
        inv_tax_obj = self.env['account.invoice.tax']
        inv_line_obj = self.env['account.invoice.line']
        context = dict(self._context or {})
        xml_id = False

        for form in self:
            created_inv = []
            date = False
            description = False
            for inv in inv_obj.browse(context.get('active_ids')):
                if inv.state in ['draft', 'cancel']:
                    raise UserError(_('Cannot create debit note for the draft/cancelled invoice.'))

                date = form.date or False
                description = form.description or inv.name
                debit = inv.debit(form.date_invoice, date, description, inv.journal_id.id)

                created_inv.append(debit.id)
                xml_id = inv.type == 'out_invoice' and 'action_invoice_tree1' or \
                         inv.type == 'in_invoice' and 'action_invoice_tree2'
        if xml_id:
            result = self.env.ref('account.%s' % (xml_id)).read()[0]
            invoice_domain = safe_eval(result['domain'])
            invoice_domain.append(('id', 'in', created_inv))
            result['domain'] = invoice_domain
            return result
        return True

    @api.multi
    def invoice_debit(self):
        context = dict(self._context or {})
        return self.with_context(debit_note_type = self.debit_note_type.id).compute_debit()

