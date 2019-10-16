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

class AccountGlobalDiscount(models.TransientModel):
    """Global discount"""

    _name = "account.global.discount"
    _description = "Global Discount"
    
    account_id = fields.Many2one('account.account', string='Account', required=True)
    amount_discount = fields.Float('Discount untaxed')
    amount_untaxed = fields.Float('Invoice amount untaxed')
    description = fields.Char('Discount description')
    product_id = fields.Many2one('product.product', string='Apply discount as', domain=[('type','=','service')], required=True)
    rate = fields.Float('Discount Amount', digits=(16, 2))
    tax_ids = fields.Many2many('account.tax',
        'account_global_discount_tax', 'global_discount_id', 'tax_id',
        string='Taxes', domain=[('type_tax_use','!=','none'), '|', ('active', '=', False), ('active', '=', True)])
    type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount Type', default='percent')
    
    @api.multi
    def apply_discount(self):
        self.ensure_one()
        inv_obj = self.env['account.invoice']
        inv_line_obj = self.env['account.invoice.line']
        context = dict(self._context or {})
        for inv in inv_obj.browse(context.get('active_ids')):
            if self.rate <= 0.0:
                raise UserError('The value must be greater than zero')
            if self.type == 'percent':
                price_unit = self.amount_untaxed * self.rate / 100
            else:
                price_unit = self.rate      
            values = {
                    'account_id': self.account_id.id,
                    'name': _("Discount: ") + (self.description or _("Others")),
                    'price_unit': price_unit * -1,
                    'product_id': self.product_id.id,
                    'uom_id': self.product_id.uom_id.id,
                    'quantity': 1.0,
                    'invoice_line_tax_ids': [(6, 0, self.tax_ids.ids)],
                    'invoice_id': inv.id,
                    'sequence': 99,
                }
            discount_line = inv_line_obj.create(values)
            # Trigger the onchange to update the invoice taxes
            inv._onchange_invoice_line_ids()

    @api.onchange('product_id')
    def onchange_discount_product(self):
        inv_obj = self.env['account.invoice']
        inv_line_obj = self.env['account.invoice.line']
        context = dict(self._context or {})
        invoice = inv_obj.browse(context.get('active_id'))

        fpos = invoice.fiscal_position_id
        company = invoice.company_id
        type = invoice.type
        self.account_id = inv_line_obj.get_invoice_line_account(type, self.product_id, fpos, company)
        self.description = self.product_id.name

        # Take the default taxes on the product discount, mapped with the fiscal position
        self.tax_ids = self.product_id.taxes_id
        if fpos:
            self.tax_ids = invoice.fiscal_position_id.map_tax(self.tax_ids)
    
    @api.onchange('amount_untaxed','tax_ids','rate','type')
    def onchange_rate(self):
        inv_obj = self.env['account.invoice']
        context = dict(self._context or {})
        invoice = inv_obj.browse(context.get('active_id'))
        
        if self.type == 'percent':
            self.amount_discount = self.amount_untaxed * self.rate / 100
        else:      
            taxes = self.tax_ids.compute_all(self.rate, invoice.currency_id, 1, product=self.product_id, partner=invoice.partner_id)
            self.amount_discount = taxes['total_excluded']
