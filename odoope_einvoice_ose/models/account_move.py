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

import time
from datetime import date
from collections import OrderedDict
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools.misc import formatLang, format_date
from odoo.tools import float_is_zero, float_compare
from odoo.tools.safe_eval import safe_eval
from odoo.addons import decimal_precision as dp
from lxml import etree

#----------------------------------------------------------
# Entries
#----------------------------------------------------------

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def post(self, invoice=False):
        for move in self:
            if move.name == '/':
                new_name = False
                journal = move.journal_id

                if invoice and invoice.move_name and invoice.move_name != '/':
                    new_name = invoice.move_name
                else:
                    if journal.sequence_id:                       
                        # If invoice is actually debit and journal has a debit_sequence then use that one or use the regular one
                        sequence = journal.sequence_id
                        if invoice and invoice.edocument_type_code in ['08', '88','98'] and journal.debit_sequence:
                            if not journal.debit_sequence_id:
                                raise UserError(_('Please define a sequence for the debit notes'))
                            sequence = journal.debit_sequence_id
                        # If invoice is actually refund and journal has a refund_sequence
                        elif invoice and invoice.type in ['out_refund', 'in_refund'] and journal.refund_sequence:
                            if not journal.refund_sequence_id:
                                raise UserError(_('Please define a sequence for the credit notes'))
                            sequence = journal.refund_sequence_id

                        new_name = sequence.with_context(ir_sequence_date=move.date).next_by_id()
                    else:
                        raise UserError(_('Please define a sequence on the journal.'))

                if new_name:
                    move.name = new_name

        return super(AccountMove, self).post(invoice)
