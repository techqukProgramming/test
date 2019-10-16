# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import math
import re
import time
import traceback

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)

try:
    from num2words import num2words
except ImportError:
    _logger.warning("The num2words python library is not installed, amount-to-text features won't be fully available.")
    num2words = None

CURRENCY_DISPLAY_PATTERN = re.compile(r'(\w+)\s*(?:\((.*)\))?')

class Currency(models.Model):
    _inherit = "res.currency"
    
    @api.multi
    def amount_to_text(self, amount):
        amount_words = super(Currency, self).amount_to_text(amount)
        
        self.ensure_one()
        def _num2words(number, lang):
            try:
                return num2words(number, lang=lang).title()
            except NotImplementedError:
                return num2words(number, lang='en').title()

        formatted = "%.{0}f".format(self.decimal_places) % amount
        parts = formatted.partition('.')
        integer_value = int(parts[0])
        fractional_value = int(parts[2] or 0)

        lang_code = self.env.context.get('lang') or self.env.user.lang
        # If the lang is es_PE
        if lang_code == 'es_PE':
            lang = self.env['res.lang'].with_context(active_test=False).search([('code', '=', lang_code)])
            amount_words = tools.ustr('{amt_value} {amt_word}').format(
                            amt_value=_num2words(integer_value, lang=lang.iso_code) + ' ' + _('with') + ' %s/%s' %(fractional_value, str(10**len(parts[2]))),
                            amt_word=self.currency_unit_label,
                            )
        
        return amount_words.upper()