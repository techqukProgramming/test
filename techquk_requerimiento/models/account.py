from odoo import api, fields, models

class AccountInvoiceLineInherit(models.Model):

        _inherit = 'account.invoice'

        @api.onchange('invoice_line_ids')
        def _set_comments(self):
            arr = []        
            if self.invoice_line_ids:
                for x in self.invoice_line_ids:      
                    for item in x.product_id:
                        if item.type == 'service':
                            arr.append('X')
            if len(arr) > 0:
                self.comment = 'OPERACIÓN SUJETA AL SPOT - DL 940 BANCO DE LA NACIÓN CTA.CTE. MN 00-231-155910'
                