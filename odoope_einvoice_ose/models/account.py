# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class AccountJournal(models.Model):
    _inherit = "account.journal"

    debit_sequence_id = fields.Many2one('ir.sequence', string='Debit Note Entry Sequence',
        help="This field contains the information related to the numbering of the debit note entries of this journal.", copy=False)
    debit_sequence_number_next = fields.Integer(string='Debit Notes: Next Number',
        help='The next sequence number will be used for the next debit note.',
        compute='_compute_debit_seq_number_next',
        inverse='_inverse_debit_seq_number_next')
    debit_sequence = fields.Boolean(string='Dedicated Debit Note Sequence', help="Check this box if you don't want to share the same sequence for invoices and debit notes made from this journal", default=False)
    is_contingency = fields.Boolean('Is Contingency')
    is_einvoice = fields.Boolean('Is E-invoice', default=True)

    @api.multi
    # do not depend on 'debit_sequence_id.date_range_ids', because
    # debit_sequence_id._get_current_sequence() may invalidate it!
    @api.depends('debit_sequence_id.use_date_range', 'debit_sequence_id.number_next_actual')
    def _compute_debit_seq_number_next(self):
        '''Compute 'sequence_number_next' according to the current sequence in use,
        an ir.sequence or an ir.sequence.date_range.
        '''
        for journal in self:
            if journal.debit_sequence_id and journal.debit_sequence:
                sequence = journal.debit_sequence_id._get_current_sequence()
                journal.debit_sequence_number_next = sequence.number_next_actual
            else:
                journal.debit_sequence_number_next = 1

    @api.multi
    def _inverse_debit_seq_number_next(self):
        '''Inverse 'debit_sequence_number_next' to edit the current sequence next number.
        '''
        for journal in self:
            if journal.debit_sequence_id and journal.debit_sequence and journal.debit_sequence_number_next:
                sequence = journal.debit_sequence_id._get_current_sequence()
                sequence.number_next = journal.debit_sequence_number_next
            
    @api.multi
    def write(self, vals):
        result = super(AccountJournal, self).write(vals) 
        if vals.get('debit_sequence'):
            for journal in self.filtered(lambda j: j.type in ('sale', 'purchase') and not j.debit_sequence_id):
                journal_vals = {
                    'name': journal.name,
                    'company_id': journal.company_id.id,
                    'code': journal.code,
                    'debit_sequence_number_next': vals.get('debit_sequence_number_next', journal.debit_sequence_number_next),
                }
                journal.debit_sequence_id = self.sudo()._create_debit_sequence(journal_vals).id       
        return result
    
    @api.model
    def create(self, vals):
        if vals.get('type') in ('sale', 'purchase') and vals.get('debit_sequence') and not vals.get('debit_sequence_id'):
            vals.update({'debit_sequence_id': self.sudo()._create_debit_sequence(vals).id})
        journal = super(AccountJournal, self).create(vals)
        return journal

    @api.model
    def _create_debit_sequence(self, vals):
        """ Create new no_gap entry sequence for every new Journal"""
        prefix = vals['code'].upper()
        prefix = 'D' + prefix
        seq_name = vals['code'] + _(': Debit') or vals['code']
        seq = {
            'name': _('%s Sequence') % seq_name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': 4,
            'number_increment': 1,
            'use_date_range': False,
        }
        if 'company_id' in vals:
            seq['company_id'] = vals['company_id']
        seq = self.env['ir.sequence'].create(seq)
        seq_date_range = seq._get_current_sequence()
        seq_date_range.number_next = vals.get('debit_sequence_number_next', 1) or vals.get('sequence_number_next', 1)
        return seq

