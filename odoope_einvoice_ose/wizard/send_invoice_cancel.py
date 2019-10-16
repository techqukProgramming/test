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

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class SendInvoiceCancel(models.TransientModel):
    _name = 'send.invoice.cancel'
    _description = 'Send invoice cancel'
    
    description = fields.Char('Reason')
    
    @api.multi
    def send_invoice_cancel(self):
        #getting invoice_ids selected
        active_ids = self.env.context.get('active_ids',[])
        for invoice in active_ids:
            #calling method "invoice_send_cancel" sending invoice
            self.env['account.invoice'].browse(invoice).with_context(reason=self.description).invoice_send_cancel()
