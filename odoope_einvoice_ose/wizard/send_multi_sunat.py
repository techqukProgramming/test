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

class SendMultiSunat(models.TransientModel):
    _name = 'send.multi.sunat'
    _description = 'Send invoices to SUNAT'
    
    @api.multi
    def send_multi_sunat(self):
        #getting invoice_ids selected
        active_ids = self.env.context.get('active_ids',[])
        for invoice in active_ids:
            #calling method "action_invoice_send" sending invoice
            if self.env.context.get('type',False) == 'send':
                self.env['account.invoice'].browse(invoice).action_invoice_send()
            else:
                self.env['account.invoice'].browse(invoice).action_check_status_ose()
        return True