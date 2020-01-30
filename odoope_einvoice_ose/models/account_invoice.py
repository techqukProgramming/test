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
from datetime import datetime
import math
import json
import requests
import urllib3

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

CURRENCY = {
    'PEN': 1,        # Soles
    'USD': 2,        # Dollars
    'EUR': 3,        # Euros
}

# mapping invoice type to debit type
TYPE2DEBIT = {
    'out_invoice': 'out_invoice',        # Customer Invoice
    'in_invoice': 'in_invoice',          # Vendor Bill
}
SERVICE = 'odooperu'


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    sunat_transaction = fields.Selection(
                        [(1, 'VENTA INTERNA'),
                        (2, 'EXPORTACION'),
                        (3, 'NO DOMICILIADO'),
                        (4, 'VENTA INTERNA - ANTICIPOS'),
                        (5, 'VENTA ITINERANTE'),
                        (6, 'FACTURA GUIA'),
                        (7, 'VENTA ARROZ PILADO'),
                        (8, 'FACTURA - COMPROBANTE DE PERCEPCION'),
                        (10, 'FACTURA - GUIA REMITENTE'),
                        (11, 'FACTURA - GUIA TRANSPORTISTA'),
                        (12, 'BOLETA DE VENTA - COMPROBANTE DE PERCEPCION'),
                        (13, 'GASTO DEDUCIBLE PERSONA NATURAL'),
                        ], string='Transaction type', help='Default 1, the others are for very special types of operations, do not hesitate to consult with us for more information', default=1)
    detraction = fields.Boolean('Detraction')
    debit_invoice_id = fields.Many2one(
        'account.invoice', string="Invoice for which this invoice is the debit note")
    debit_invoice_ids = fields.One2many(
        'account.invoice', 'debit_invoice_id', string='Debit Invoices', readonly=True)
    edocument_type_code = fields.Char(
        string='Electronic invoice type code', related='edocument_type.code', store=True)
    einvoice_hash_code = fields.Char('Hash code', copy=False)
    einvoice_cdr_zip = fields.Binary('CDR zip', copy=False)
    einvoice_sunat_responsecode = fields.Char(
        'SUNAT Response code', copy=False)
    einvoice_sunat_soap_error = fields.Char('SUNAT SOAP error', copy=False)
    einvoice_sunat_accepted = fields.Boolean('Accepted by SUNAT', copy=False)
    einvoice_link_cdr = fields.Char('CDR link', copy=False)
    einvoice_link_pdf = fields.Char('PDF link', copy=False)
    einvoice_link_xml = fields.Char('XML link', copy=False)
    einvoice_link_invoice = fields.Char('Invoice link', copy=False)
    einvoice_log_ids = fields.One2many(
        'account.einvoice.log', 'invoice_id', string='E-invoice log', copy=False)
    einvoice_errors_sunat = ""
    einvoice_error = fields.Text(
        string="Error", compute="_get_einvoice_log_ids")
    einvoice_ose_accepted = fields.Boolean('Sent to PSE/OSE', copy=False)
    einvoice_sunat_note = fields.Text('Notes by SUNAT', copy=False)
    einvoice_vat = fields.Char(
        string="RUC/DNI", compute="_get_partner_document")
    is_contingency = fields.Boolean(
        'Is Contingency', related='journal_id.is_contingency', store=True)
    is_einvoice = fields.Boolean(
        'Is E-invoice', related='journal_id.is_einvoice', store=True)
    state_payment = fields.Selection(
                        [(1, 'POR COBRAR'),
                        (2, 'PAGADO'),
                        (3, 'PARCIALMENTE PAGADO'),
                        (4, 'ANULADO'),
                        ], string='Estado de Pago', help='Estados de pago de la factura por cliente.', default=1)

    @api.depends('partner_id')
    def _get_partner_document(self):
        for x in self:
            if x.partner_id:
                x.einvoice_vat = x.partner_id.vat
        return True

    # Getting the last error
    @api.depends('einvoice_log_ids')
    def _get_einvoice_log_ids(self):
        for x in self:
            if x.einvoice_log_ids:
                x.einvoice_error = x.einvoice_log_ids.sorted(
                    'date', reverse=True)[0].response
        return True

    def _get_ose_supplier(self):
        if not self.journal_id.shop_id:
            raise UserError(_('Please select a Shop for the journal \'%s\'') % (
                self.journal_id.name,))
        if not self.shop_id.einvoice_supplier:
            raise UserError(_('Please select a OSE supplier for the company %s') % (
                self.company_id.name,))
        if self.shop_id and (self.shop_id.company_id != self.company_id):
            raise UserError(_('The company of the invoice (%s) is different to the Shop company (%s)') % (
                self.company_id.name, self.shop_id.company_id.name))
        return self.shop_id.einvoice_supplier_code

    @api.model
    def create(self, vals):
        if 'edocument_type' not in vals and 'journal_id' in vals:
            vals['edocument_type'] = self.env['account.journal'].browse(
                vals['journal_id']).edocument_type.id
        return super(AccountInvoice, self).create(vals)

    @api.multi
    def _get_invoice_values_odoofact(self):
        if not self.journal_id.edocument_type:
            raise UserError(
                _('Please define Edocument type on the journal related to this invoice.'))
        if not self.journal_id.edocument_type.type_of:
            raise UserError(
                _('Please define the \'Document type\' on the \'Edocument type\' of the journal related to this invoice.'))
        currency = CURRENCY.get(self.currency_id.name, False)
        if not currency:
            raise UserError(_('Currency \'%s, %s\' is not available for Electronic invoice. Contact to the Administrator.') % (
                self.currency_id.name, self.currency_id.currency_unit_label))
        currency_exchange = self.currency_id.with_context(date=self.date_invoice)._get_conversion_rate(
            self.currency_id, self.company_id.currency_id, self.env.user.company_id, self.date_invoice)
        if currency_exchange == 0:
            raise UserError(
                _('The currency rate should be different to 0.0, Please check the rate at %s') % self.date_invoice)
        send_email = ''
        if self.shop_id.send_email == True:
            send_email = 'true'
        else:
            send_email = 'false'
        values = {
            'company_id': self.company_id.id,
            'shop_id': self.shop_id and self.shop_id.id or False,
            'invoice_id': self.id,
            "operacion": "generar_comprobante",
            'tipo_de_comprobante': self.edocument_type.type_of,
            'sunat_transaction': int(self.sunat_transaction),
            'serie': self.einv_serie,
            'numero': str(self.einv_number),
            'cliente_tipo_de_documento': self.commercial_partner_id.catalog_06_id and self.commercial_partner_id.catalog_06_id.code or '1',
            'cliente_numero_de_documento': self.commercial_partner_id.vat and self.commercial_partner_id.vat or '00000000',
            'cliente_denominacion': self.commercial_partner_id.registration_name or self.commercial_partner_id.name,
            'cliente_direccion': (self.commercial_partner_id.street or '')
                                + (self.commercial_partner_id.street2 or '')
                                + (self.commercial_partner_id.district_id and ', ' +
                                   self.commercial_partner_id.district_id.name or '')
                                + (self.commercial_partner_id.province_id and ', ' +
                                   self.commercial_partner_id.province_id.name or '')
                                + (self.commercial_partner_id.state_id and ', ' +
                                   self.commercial_partner_id.state_id.name or '')
                                + (self.commercial_partner_id.country_id and ', ' +
                                   self.commercial_partner_id.country_id.name or ''),
            'cliente_email': self.commercial_partner_id.email and self.commercial_partner_id.email or self.partner_id.email,
            'fecha_de_emision': datetime.strptime(str(self.date_invoice), "%Y-%m-%d").strftime("%d-%m-%Y"),
            'fecha_de_vencimiento': datetime.strptime(str(self.date_due), "%Y-%m-%d").strftime("%d-%m-%Y"),
            'moneda': currency,
            'tipo_de_cambio': round(1/currency_exchange, 3),
            'porcentaje_de_igv': self.igv_percent,
            'descuento_global': abs(self.global_discount),
            'total_descuento': abs(self.amount_discount),
            'total_gravada': abs(self.einv_amount_base),
            'total_inafecta': abs(self.einv_amount_unaffected),
            'total_exonerada': abs(self.einv_amount_exonerated),
            'total_igv': abs(self.einv_amount_igv),
            'total_otros_cargos': abs(self.einv_amount_others),
            'total': abs(self.amount_total),
            'detraccion': self.detraction and 'true' or 'false',
            'observaciones': self.comment,
            'documento_que_se_modifica_tipo': self.origin_document_id and (self.origin_document_serie[0] == 'F' and '1' or '2') or (self.einv_serie[0] == 'F' and '1' or '2') or '',
            'documento_que_se_modifica_serie': self.origin_document_serie or '',
            'documento_que_se_modifica_numero': self.origin_document_number or '',
            'tipo_de_nota_de_credito': self.credit_note_type and int(self.credit_note_type.code) or '',
            'tipo_de_nota_de_debito': self.debit_note_type and int(self.debit_note_type.code) or '',
            'enviar_automaticamente_al_cliente': send_email,
            'condiciones_de_pago': self.payment_term_id and self.payment_term_id.name or '',
            'items': getattr(self, '_get_invoice_line_values_%s' % self._get_ose_supplier())(self.invoice_line_ids),
            'generado_por_contingencia': self.is_contingency and 'true' or 'false'
            }
        return values

    @api.multi
    def _get_invoice_line_values_odoofact(self, lines):
        res = []
        for line in lines:
            if line.display_type == False:
                # The IGV must be > 0.01, it's mandatory in Odoofact, except when is exonerated or unaffected
                if line.igv_type.type in ['exonerado', 'inafecto']:
                    igv_amount = abs(line.igv_amount)
                else:
                    igv_amount = abs(line.igv_amount) > 0.01 and abs(
                        line.igv_amount) or 0.02
                values = {
                    'unidad_de_medida': line.product_id and (line.product_id.type != 'service' and 'NIU' or 'ZZ') or 'ZZ',
                    'codigo': line.product_id and line.product_id.default_code or '',
                    'descripcion': line.name,
                    'cantidad': abs(line.quantity),
                    'valor_unitario': abs(line.price_unit_excluded),
                    'precio_unitario': abs(line.price_unit_included),
                    'descuento': abs(line.amount_discount),
                    'subtotal': abs(line.price_subtotal),
                    'tipo_de_igv': line.igv_type.code_of,
                    'igv': igv_amount,
                    'total': abs(line.price_total),
                    }
                res.append(values)
        return res

    # CPE / OSE connector
    def api_connector_odoofact(self, invoice):
        data = json.dumps(invoice)
        company = self.env['res.company'].browse(invoice['company_id'])
        shop_id = invoice['shop_id']
        if invoice.get('shop_id', False):
            shop = self.env['einvoice.shop'].browse(invoice['shop_id'])
            url = ''
            authorization = ''
            if shop.einvoice_of_url:
                url = shop.einvoice_of_url
            if shop.einvoice_of_token:
                authorization = shop.einvoice_of_token
        else:
            raise UserError(_('The invoice is not assigned to a store'))
        headers = {'Content-type': 'application/json',
            'Authorization': authorization}
        try:
            r = requests.post(url, data, headers=headers, verify=True)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            raise UserError(
                _("Review URL settings and token for billing. \n %s") % (e))
        response = r.text
        response = response.replace("'", "\'")
        response = json.loads(response)

        if response.get('errors', False):
            document = invoice and (
                str(invoice.get('serie', ' ')) + '-' + invoice.get('numero', ' ')) or 'No number'
            self.einvoice_errors_sunat = (self.einvoice_errors_sunat and self.einvoice_errors_sunat or '') + \
                                          "\n Had the followed errors: \n %s, error in invoice: %s" % (
                                              response.get('errors', ''), document)
        ose_accepted = False
        if response.get('errors', False):
            ose_accepted = False
        else:
            ose_accepted = True
        json_invoice = json.loads(data)
        values_log = {
            'invoice_id': invoice['invoice_id'],
            'json_sent': json.dumps(json_invoice, indent=4, sort_keys=True),
            'json_response': json.dumps(response, indent=4, sort_keys=True),
            'einvoice_hash_code': response.get('codigo_hash', ''),
            'einvoice_sunat_responsecode': response.get('sunat_responsecode', ''),
            'einvoice_sunat_soap_error': response.get('sunat_soap_error', ''),
            'einvoice_sunat_accepted': response.get('aceptada_por_sunat', False),
            'einvoice_ose_accepted': ose_accepted,
            'einvoice_sunat_note': response.get('sunat_note', ''),
            'einvoice_link_cdr': response.get('enlace_del_cdr', ''),
            'einvoice_link_pdf': response.get('enlace_del_pdf', ''),
            'einvoice_link_xml': response.get('enlace_del_xml', ''),
            'einvoice_link_invoice': response.get('enlace', ''),
            'einvoice_cdr_zip': response.get('cdr_zip_base64', ''),
            'response': response.get('errors', False), }
        # ~ Register log
        log_id = self.env['account.einvoice.log'].create(values_log)
        if log_id:
            self.env['account.invoice'].browse(
                invoice['invoice_id']).write(values_log)

    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.filtered(lambda inv: not inv.sent).write({'sent': True})
        if self.shop_id.format_print == 'ticket':
            return self.env.ref('odoope_einvoice_ose.account_einvoice_report_ticket').report_action(self)
        else:
            return self.env.ref('odoope_einvoice_ose.account_einvoice_report').report_action(self)

    @api.multi
    def action_invoice_send(self):
        if not self.is_einvoice:
            raise UserError(_('The invoice is not a Electronic document'))
        # Get invoice data depending of OSE supplier
        einvoice_supplier = self._get_ose_supplier()
        einvoice_data = getattr(
            self, '_get_invoice_values_%s' % einvoice_supplier)()
        content = []
        content = getattr(self, 'api_connector_%s' %
                          einvoice_supplier)(einvoice_data)
        # Post a message when the invoice is sent
        if self.einvoice_ose_accepted:
            message = _(
                "Electrónic document <span style='color: #21b799;'>%s</span> has sent to PSE/OSE") % (self.number)
            self.message_post(body=message)
        # Commit the change
        self.env.cr.commit()
        return True

    @api.multi
    def action_invoice_check(self):
        # For Invoices canceled
        einvoice_supplier = self._get_ose_supplier()
        if self.state == 'cancel':
            values = getattr(
                self, '_get_invoice_cancel_values_check_%s' % einvoice_supplier)()
        else:
            values = getattr(self, '_get_invoice_values_check_%s' %
                             einvoice_supplier)()
        getattr(self, 'api_connector_%s' % einvoice_supplier)(values)
        return True

    @api.model
    def cron_send_invoices(self):
        invoice_ids = self.env['account.invoice'].search([('is_einvoice', '=', True), ('state', 'not in', ['draft', 'cancel']), (
            'einvoice_ose_accepted', '=', False), ('type', 'in', ['out_invoice', 'out_refund'])]).filtered(lambda inv: inv.date_invoice != False)
        for invoice in invoice_ids:
            invoice.action_invoice_send()

    @api.model
    def cron_check_invoice_ose(self):
        invoice_ids = self.env['account.invoice'].search([('is_einvoice', '=', True), ('state', '!=', 'draft'), ('einvoice_ose_accepted', '=', True), (
            'einvoice_sunat_accepted', '=', False), ('shop_id', '!=', False), ('type', 'in', ['out_invoice', 'out_refund'])])
        for invoice in invoice_ids:
            invoice.action_invoice_check()

    @api.multi
    def invoice_send_cancel(self):
        self.ensure_one()
        einvoice_supplier = self._get_ose_supplier()
        if not self.einvoice_ose_accepted:
            raise UserError(_("You need to send the invoice to SUNAT before cancel it. \n Invoice: %s-%s") %
                            (self.einv_serie, str(self.einv_number)))
        # Cancel invoice (Odoo method)
        self.action_invoice_cancel()
        # Cancel with OSE
        values = getattr(self, '_get_invoice_cancel_values_%s' %
                         einvoice_supplier)()
        getattr(self, 'api_connector_%s' % einvoice_supplier)(values)
        if self.state == 'cancel':
            message = _("Invoice <span style='color: #21b799;'>%s-%s</span> nulled by SUNAT") % (
                self.einv_serie, str(self.einv_number))
            self.message_post(body=message)
        else:
            raise UserError(_("It's not possible to cancel the invoice. Please check the log details \n Invoice: %s-%s") %
                            (self.einv_serie, str(self.einv_number)))
        return True

    @api.multi
    def _get_invoice_cancel_values_odoofact(self):
        self.ensure_one()
        values = {
            'company_id': self.company_id.id,
            'shop_id': self.shop_id and self.shop_id.id or False,
            'invoice_id': self.id,
            "operacion": "generar_anulacion",
            'tipo_de_comprobante': self.edocument_type.type_of,
            'motivo': self._context.get('reason', _('Null document')),
            'serie': self.einv_serie,
            'numero': str(self.einv_number),
            'codigo_unico': '%s|%s|%s-%s' % (SERVICE, self.company_id.partner_id.vat, self.einv_serie, str(self.einv_number)),
        }
        return values

    @api.multi
    def _get_invoice_cancel_values_check_odoofact(self):
        self.ensure_one()
        values = {
            'company_id': self.company_id.id,
            'shop_id': self.shop_id and self.shop_id.id or False,
            'invoice_id': self.id,
            "operacion": "consultar_anulacion",
            'tipo_de_comprobante': self.edocument_type.type_of,
            'serie': self.einv_serie,
            'numero': str(self.einv_number),
        }
        return values

    @api.multi
    def _get_invoice_values_check_odoofact(self):
        self.ensure_one()
        values = {
            'company_id': self.company_id.id,
            "shop_id": self.shop_id and self.shop_id.id or False,
            "invoice_id": self.id,
            "operacion": "consultar_comprobante",
            "tipo_de_comprobante": self.edocument_type.type_of,
            "serie": self.einv_serie,
            "numero": str(self.einv_number)
        }
        return values

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        values = super(AccountInvoice, self)._prepare_refund(
            invoice, date_invoice, date, description, journal_id)
        # ~ adding credit note type
        if self._context.get('credit_note_type') and self._context.get('invoice'):
            inv = self._context.get('invoice')
            einv_serie = inv.einv_serie
            einv_number = inv.einv_number
            reference = inv.reference
            if reference and inv.type == 'in_invoice':
                if len(reference.split('-')) == 2:
                    einv_serie = reference.split('-')[0]
                    einv_number = reference.split('-')[1]
            values.update({
                'credit_note_type': self._context.get('credit_note_type'),
                'edocument_type': inv.journal_id.edocument_credit and inv.journal_id.edocument_credit.id or False,
                'origin_document_id': inv.id,
                'origin_document_serie': einv_serie,
                'origin_document_number': einv_number,
                'shop_id': inv.shop_id.id,
                })
        return values

    @api.model
    def _prepare_debit(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        """ Prepare the dict of values to create the new debit note from the invoice.
            This method may be overridden to implement custom
            debit note generation (making sure to call super() to establish
            a clean extension chain).

            :param record invoice: invoice as credit note
            :param string date_invoice: credit note creation date from the wizard
            :param integer date: force date from the wizard
            :param string description: description of the credit note from the wizard
            :param integer journal_id: account.journal from the wizard
            :return: dict of value to create() the credit note
        """
        values = {}
        for field in self._get_refund_copy_fields():
            if invoice._fields[field].type == 'many2one':
                values[field] = invoice[field].id
            else:
                values[field] = invoice[field] or False

        values['invoice_line_ids'] = self._refund_cleanup_lines(
            invoice.invoice_line_ids)

        tax_lines = invoice.tax_line_ids
        cleaned_tax_lines = self._refund_cleanup_lines(tax_lines)
        values['tax_line_ids'] = cleaned_tax_lines

        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
        elif invoice['type'] == 'in_invoice':
            journal = self.env['account.journal'].search(
                [('type', '=', 'purchase')], limit=1)
        else:
            journal = self.env['account.journal'].search(
                [('type', '=', 'sale')], limit=1)
        values['journal_id'] = journal.id

        values['type'] = TYPE2DEBIT[invoice['type']]
        values['date_invoice'] = date_invoice or fields.Date.context_today(
            invoice)
        values['state'] = 'draft'
        values['number'] = False
        values['origin'] = invoice.number
        values['payment_term_id'] = False
        values['debit_invoice_id'] = invoice.id

        if date:
            values['date'] = date
        if description:
            values['name'] = description

        # E-invoice values
        einv_serie = invoice.einv_serie
        einv_number = invoice.einv_number
        reference = invoice.reference
        if reference and invoice.type == 'in_invoice':
            if len(reference.split('-')) == 2:
                einv_serie = reference.split('-')[0]
                einv_number = reference.split('-')[1]
        values['debit_note_type'] = self._context.get('debit_note_type')
        values['edocument_type'] = invoice.journal_id.edocument_debit and invoice.journal_id.edocument_debit.id or False
        values['origin_document_id'] = invoice.id
        values['origin_document_serie'] = einv_serie
        values['origin_document_number'] = einv_number
        values['shop_id'] = invoice.shop_id.id
        return values

    @api.multi
    @api.returns('self')
    def debit(self, date_invoice=None, date=None, description=None, journal_id=None):
        new_invoices = self.browse()
        for invoice in self:
            # create the new invoice
            values = self._prepare_debit(invoice, date_invoice=date_invoice, date=date,
                                    description=description, journal_id=journal_id)
            debit_invoice = self.create(values)
            if invoice.type == 'out_invoice':
                message = _("This customer invoice debit note has been created from: <a href=# data-oe-model=account.invoice data-oe-id=%d>%s</a><br>Reason: %s") % (
                    invoice.id, invoice.number, description)
            else:
                message = _("This vendor bill debit note has been created from: <a href=# data-oe-model=account.invoice data-oe-id=%d>%s</a><br>Reason: %s") % (
                    invoice.id, invoice.number, description)
            debit_invoice.message_post(body=message)
            new_invoices += debit_invoice
        return new_invoices


class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine, self)._onchange_product_id()
        res['value'] = {}
        return res


class AccountEinvoiceLog(models.Model):
    _name = 'account.einvoice.log'
    _description = 'Log response'
    _order = 'date desc'

    date = fields.Datetime('Date', default=fields.Datetime.now, required=True)
    invoice_id = fields.Many2one('account.invoice', string='Invoice')
    einvoice_cdr_zip = fields.Binary('CDR zip')
    einvoice_hash_code = fields.Char('Hash code')
    einvoice_link_cdr = fields.Char('CDR link')
    einvoice_link_pdf = fields.Char('PDF link')
    einvoice_link_xml = fields.Char('XML link')
    einvoice_link_invoice = fields.Char('Invoice link')
    einvoice_ose_accepted = fields.Boolean('Accepted by OSE')
    einvoice_sunat_responsecode = fields.Char('SUNAT Response code')
    einvoice_sunat_soap_error = fields.Char('SUNAT SOAP error')
    einvoice_sunat_accepted = fields.Boolean('Accepted by SUNAT')
    einvoice_sunat_note = fields.Text('Notes by SUNAT')
    json_sent = fields.Html('JSON sent')
    json_response = fields.Html('JSON response')
    response = fields.Text(string='Description')


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    medio_pago = fields.Selection(
                        [('Depósito','DEPÓSITO'),
                        ('Cheque','CHEQUE'),
                        ('Canje','CANJE'),
                        ('Transferencia','TRANSFERENCIA'),
                        ('Retención Sunat','RETENCIÓN SUNAT'),
                        ('Penalidad','PENALIDAD'),
                        ],string='Medio de Pago', help='Medios de pago por parte del cliente.', default='Depósito')

    factura_id = fields.Many2one('account.invoice', string='N° de Factura')

    @api.onchange('partner_id')
    def _get_invoice(self):
            if self.partner_id:
                    # arr = []
                    # for x in self.partner_id:      
                    #         for invoice_id in x.invoice_ids:
                    #                 arr.append(invoice_id.name)      
                    return {'domain':{'factura_id':[('partner_id.id','=',self.partner_id.id)]}}
                    # elif len(unico) == 2:       
                    #         return {'domain':{'partner_id':['|',('id','=',unico[0].id),('id','=',unico[1].id)]}}
                    # elif len(unico) == 3:       
                    #         return {'domain':{'partner_id':['|',('id','=',unico[0].id),('id','=',unico[1].id),('id','=',unico[2].id)]}}
                    # elif len(unico) == 4:       
                    #         return {'domain':{'partner_id':['|',('id','=',unico[0].id),('id','=',unico[1].id),('id','=',unico[2].id),('id','=',unico[3].id)]}}
                    # elif len(unico) == 5:       
                    #         return {'domain':{'partner_id':['|',('id','=',unico[0].id),('id','=',unico[1].id),('id','=',unico[2].id),('id','=',unico[3].id),('id','=',unico[4].id)]}}
                    # else:
                    #         return {
                    #         'warning': {
                    #                 'title': 'Advertencia!',
                    #                 'message': 'No puede seleccionar requermiento que tengan mas de 5 proveedores!'}
                    #         }
