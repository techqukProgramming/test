#clase horario
#creado por: juan mejia

from odoo import models,fields,api,_
from datetime import datetime
import json,requests
from odoo.exceptions import UserError,Warning

def get_data_doc_number(tipo_doc, numero_doc, format='json'):
        user, password = 'demorest', 'demo1234'
        url = 'http://py-devs.com/api'
        url = '%s/%s/%s' % (url, tipo_doc, str(numero_doc))
        res = {'error': True, 'message': None, 'data': {}}
        try:
            response = requests.get(url, auth=(user, password))
        except requests.exceptions.ConnectionError as e:
            res['message'] = 'Error en la conexion'
            return res

        if response.status_code == 200:
            res['error'] = False
            res['data'] = response.json()
        else:
            try:
                res['message'] = response.json()['detail']
            except Exception as e:
                res['error'] = True
        return res

class Guide(models.Model):
    _name = 'test_techquk.guide'
    _inherit = 'account.invoice'
    _description = 'Modelo guía de remisión para facturación'
    

    id_factura = fields.Many2one('account.invoice','Factura',required=True)
    name = fields.Char("N° de Guia de Remisión",default=lambda self: self._get_next_guidename(), store=True, readonly=True)
    fecha_emision = fields.Date('Fecha Emisión',default=fields.Date.today(),required=True)
    fecha_inicio_tras = fields.Date('Fecha Traslado',default=fields.Date.today(),required=True)
    tipo_comprobante = fields.Selection(string='Tipo Comprobante', 
    selection=[
        ('01', 'FACTURA'),
        ('03', 'BOLETA DE VENTA'),
        ('07', 'NOTA DE CRÉDITO'),
        ('08', 'NOTA DE DÉBITO'),
        ('09', 'GUIA DE REMISIÓN REMITENTE'),
        ('12', 'TICKET DE MAQUINA REGISTRADORA'),
        ('13', 'DOCUMENTO EMITIDO POR BANCOS, INSTITUCIONES FINANCIERAS, CREDITÍCIAS Y DE SEGUROS QUE SE ENCUENTREN BAJO EL CONTROL DE LA SUPERINTENDENCIA DE BANCA Y SEGUROS'),
        ('14', 'RECIBO SERVICIOS PÚBLICOS'),
        ('16', 'BOLETO DE VIAJE EMITIDO POR LAS EMPRESAS DE TRANSPORTE PÚBLICO INTERPROVINCIAL DE PASAJEROS'),
        ('18', 'DOCUMENTOS EMITIDOS POR LAS AFP'),
        ('20', 'COMPROBANTE DE RETENCIÓN'),
        ('31', 'GUIA DE REMISIÓN TRANSPORTISTA'),
        ('40', 'COMPROBANTE DE PERCEPCIÓN'),
        ('41', 'COMPROBANTE DE PERCEPCIÓN – VENTA INTERNA (FÍSICO-FORMATO IMPRESO'),
        ('56', 'COMPROBANTE DE PAGO SEAE'),
        ('71', 'GUIA DE REMISIÓN REMITENTE COMPLEMENTARIA'),
        ('72', 'GUIA DE REMISIÓN TRANSPORTISTA COMPLEMENTARIA')
        ],default='09')
    

    #Remitente
    tipo_documento = fields.Selection(string='Tipo Documento', 
    selection=[
        ('0', 'OTROS TIPOS DE DOCUMENTOS'),
        ('1', 'DOCUMENTO NACIONAL DE IDENTIDAD (DNI)'),
        ('4', 'CARNET DE EXTRANJERIA'),
        ('6', 'REGISTRO ÚNICO DE CONTRIBUYENTES (RUC)'),
        ('7', 'PASAPORTE'),
        ('A', 'CÉDULA DIPLOMÁTICA DE IDENTIDAD')
        ],default='6',required=True)
    num_documento = fields.Char("Numero Documento",required=True)
    nom_remitente = fields.Char("Nombre / Razon Social",required=True)
    mot_traslado = fields.Selection(string='Motivo de Traslado', 
    selection=[
        ('01', 'VENTA'),
        ('14', 'VENTA SUJETA A CONFIRMACION DEL COMPRADOR'),
        ('02', 'COMPRA'),
        ('04', 'TRASLADO ENTRE ESTABLECIMIENTOS DE LA EMPRESA'),
        ('18', 'TRASLADO EMISOR ITINERANTE CP'),
        ('08', 'IMPORTACIÓN'),
        ('09', 'EXPORTACIÓN'),
        ('19', 'TRASLADO A ZONA PRIMARIA'),
        ('13', 'OTROS MOTIVOS'),
        ],default='01',required=True)
    otr_traslado = fields.Char("Otro Motivo")
    des_traslado = fields.Char("Descripción del traslado")
    num_dam = fields.Char("Numeración DAM")

    #Destinatario
    tipo_documento_d = fields.Selection(string='Tipo Documento', 
    selection=[
        ('0', 'OTROS TIPOS DE DOCUMENTOS'),
        ('1', 'DOCUMENTO NACIONAL DE IDENTIDAD (DNI)'),
        ('4', 'CARNET DE EXTRANJERIA'),
        ('6', 'REGISTRO ÚNICO DE CONTRIBUYENTES (RUC)'),
        ('7', 'PASAPORTE'),
        ('A', 'CÉDULA DIPLOMÁTICA DE IDENTIDAD')
        ],default='6',required=True)
    num_documento_d = fields.Char("Numero Documento",required=True)
    nom_remitente_d = fields.Char("Nombre / Razon Social",required=True)
    tip_transporte = fields.Selection(string='Tipo Transporte', 
    selection=[
        ('01', 'TRANSPORTE PÚBLICO'),
        ('02', 'TRANSPORTE PRIVADO')
        ],default='01',required=True)
    mul_destinos = fields.Boolean("Múltiples puntos de destino")
    otr_documentos = fields.Many2many('ir.attachment',string="Otros documentos relacionados")

    #Punto de partida
    cod_departamento = fields.Many2one("res.country.state","Departamento",domain=[('country_id.name', '=', 'Perú'),('code','in',['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25'])])
    cod_provincia = fields.Many2one("res.country.state","Provincia")
    cod_distrito = fields.Many2one("res.country.state","Distrito")
    cod_ubigeo = fields.Char("Cód. Ubigeo")
    cod_direccion = fields.Char("Dirección") 

    #Punto de llegada 
    cod_departamento_pl = fields.Many2one("res.country.state","Departamento",domain=[('country_id.name', '=', 'Perú'),('code','in',['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25'])])
    cod_provincia_pl = fields.Many2one("res.country.state","Provincia")
    cod_distrito_pl = fields.Many2one("res.country.state","Distrito")
    cod_ubigeo_pl = fields.Char("Cód. Ubigeo")
    cod_direccion_pl = fields.Char("Dirección")

    #Transporte Privado
    num_placa = fields.Char("Número Placa")

    #Conductores
    tipo_documento_c = fields.Selection(string='Tipo Documento', 
    selection=[
        ('0', 'OTROS TIPOS DE DOCUMENTOS'),
        ('1', 'DOCUMENTO NACIONAL DE IDENTIDAD (DNI)'),
        ('4', 'CARNET DE EXTRANJERIA'),
        ('6', 'REGISTRO ÚNICO DE CONTRIBUYENTES (RUC)'),
        ('7', 'PASAPORTE'),
        ('A', 'CÉDULA DIPLOMÁTICA DE IDENTIDAD')
        ],default='6')
    num_documento_c = fields.Char("Número Documento")
    nom_c = fields.Char("Nombre / Razon Social")

    #Extras
    trans_programado = fields.Boolean('Es transbordo programado?')
    obs = fields.Text('Observación')

    #Data
    showData = fields.Text('JSON')
    responseMessage = fields.Text('RESPUESTA')

    #Items de la Guía de Remisión
    items_id_guide = fields.One2many('test_techquk.item','guide_id',string="Items")
    items_ids_guide = fields.Many2many('test_techquk.item','items_id_guide',string="Items")

    #Peso Bruto Total
    peso_bruto_total = fields.Float("Peso Bruto Total(KGM)")

    state = fields.Selection([
    ('enviar', 'ENVIAR'),
    ('cancelar', 'CANCELAR'),
    ], string='Estado:', default='enviar')

    @api.onchange('cod_direccion')
    def onchage_mayus_cod_direccion(self):
        if self.cod_direccion:
            self.cod_direccion = self.cod_direccion.upper()
    
    @api.onchange('cod_direccion_pl')
    def onchage_mayus_cod_direccion_pl(self):
        if self.cod_direccion_pl:
            self.cod_direccion_pl = self.cod_direccion_pl.upper()
    
    @api.onchange('cod_departamento')
    def onchange_departamento(self):

        if self.cod_departamento:
            arr = []
            departamento_id = self.env['res.country.state'].search([('code', '=', self.cod_departamento.code),('country_id.name', '=', 'Perú')]).id
            provincia_id = self.env['res.country.state'].search([('state_id.id', '=', departamento_id)])
            for x in provincia_id:
                if len(x.code) == 4:
                    arr.append(x.code)
            return {'domain':{'cod_provincia':[('code','in',arr)]}}
    
    @api.onchange('cod_provincia')
    def onchange_provincia(self):
        if self.cod_provincia:
            arr = []
            provincia_id = self.env['res.country.state'].search([('code', '=', self.cod_provincia.code),('country_id.name', '=', 'Perú')]).id
            distrito_id = self.env['res.country.state'].search([('province_id.id', '=', provincia_id)])
            for x in distrito_id:
                if len(x.code) == 6:
                    arr.append(x.code)
            return {'domain':{'cod_distrito':[('code','in',arr)]}}

    @api.onchange('cod_departamento_pl')
    def onchange_departamento_pl(self):

        if self.cod_departamento_pl:
            arr = []
            departamento_id = self.env['res.country.state'].search([('code', '=', self.cod_departamento_pl.code),('country_id.name', '=', 'Perú')]).id
            provincia_id = self.env['res.country.state'].search([('state_id.id', '=', departamento_id)])
            for x in provincia_id:
                if len(x.code) == 4:
                    arr.append(x.code)
            return {'domain':{'cod_provincia_pl':[('code','in',arr)]}}
    
    @api.onchange('cod_provincia_pl')
    def onchange_provincia_pl(self):
        if self.cod_provincia_pl:
            arr = []
            provincia_id = self.env['res.country.state'].search([('code', '=', self.cod_provincia_pl.code),('country_id.name', '=', 'Perú')]).id
            distrito_id = self.env['res.country.state'].search([('province_id.id', '=', provincia_id)])
            for x in distrito_id:
                if len(x.code) == 6:
                    arr.append(x.code)
            return {'domain':{'cod_distrito_pl':[('code','in',arr)]}}
            

    @api.onchange('cod_distrito_pl')
    def onchange_distrito_pl(self):
        if self.cod_distrito_pl:
            codigo = self.cod_distrito_pl.code
            self.cod_ubigeo_pl = codigo

    # Onchange para actualizar el codigo de distrito
    @api.onchange('cod_distrito')
    def onchange_distrito(self):
        if self.cod_distrito:
            codigo = self.cod_distrito.code
            self.cod_ubigeo = codigo

            

    @api.model
    def _get_next_guidename(self):
        sequence = self.env['ir.sequence'].search([('code','=','test_techquk.guia')]) #next = 8
        next= sequence.get_next_char(sequence.number_next_actual) #next = 9
        return next #retorno 9

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('test_techquk.guia') #10
        result = super(Guide, self).create(vals) #se crea el nuevo requerimiento con el name 10 por defecto
        return result   

    @api.onchange('id_factura')
    def _get_items_guia_remision(self):
        self.items_ids_guide = [(6, 0, {})]
        numeracion = 0
        arr = []
        suma = 0        
        if self.id_factura:
                for x in self.id_factura:      
                        for item in x.invoice_line_ids:
                            numeracion = numeracion + 1
                            suma = suma + item.product_id.weight
                            arr.append((0, 0, {'numero_orden': numeracion,'codigo_bien': item.product_id.default_code,'name': item.product_id.name,'unidad_medida': item.product_id.uom_id.codigo,'cantidad':item.quantity}))
                self.items_ids_guide = arr
                self.peso_bruto_total = suma

    @api.onchange('num_documento')
    def vat_change(self):
        self.update_document()

    @api.onchange('num_documento_d')
    def vat_change_r(self):
        self.update_document_d()

    @api.onchange('num_documento_c')
    def vat_change_c(self):
        self.update_document_c()
        
    @api.one
    def update_document(self):
        if self.tipo_documento and self.num_documento and self.num_documento != '':
            # Valida RUC
            if len(self.num_documento) == 11 and self.tipo_documento == '6':
                d = get_data_doc_number(
                    'ruc', self.num_documento, format='json')
                if d['error']:
                    return True
                d = d['data']

                #~ Busca el distrito
                ditrict_obj = self.env['res.country.state']
                state_ids = ditrict_obj.search([('name', '=', d['departamento']),
                                               ('province_id', '=', False),
                                               ('state_id', '=', False)])
                prov_ids = ditrict_obj.search([('name', '=', d['provincia']),
                                               ('province_id', '=', False),
                                               ('state_id', '!=', False)])
                dist_ids = ditrict_obj.search([('name', '=', d['distrito']+'(Distrito)'),
                                              ('province_id', '!=', False),
                                              ('state_id', '!=', False)])
                if prov_ids:
                    self.cod_provincia = prov_ids
                    self.cod_departamento = state_ids
                    self.cod_distrito = dist_ids
                    
                self.nom_remitente = d['nombre'] != '-' and d['nombre'] or d['nombre_comercial']
                self.cod_direccion = d['domicilio_fiscal']
            else:
                raise Warning('Solo se puede consultar RUC por SUNAT..!')
        else:
            True

    @api.one
    def update_document_d(self):
        if self.tipo_documento_d and self.num_documento_d and self.num_documento_d != '':
            # Valida RUC
            if len(self.num_documento_d) == 11 and self.tipo_documento_d == '6':
                d = get_data_doc_number(
                    'ruc', self.num_documento_d, format='json')
                if d['error']:
                    return True
                d = d['data']
                self.nom_remitente_d = d['nombre_comercial'] != '-' and d['nombre_comercial'] or d['nombre']
                self.cod_direccion_pl = d['domicilio_fiscal']

                #~ Busca el distrito
                ditrict_obj = self.env['res.country.state']
                state_ids = ditrict_obj.search([('name', '=', d['departamento']),
                                               ('province_id', '=', False),
                                               ('state_id', '=', False)])
                prov_ids = ditrict_obj.search([('name', '=', d['provincia']),
                                               ('province_id', '=', False),
                                               ('state_id', '!=', False)])
                dist_ids = ditrict_obj.search([('name', '=', d['distrito']+'(Distrito)'),
                                              ('province_id', '!=', False),
                                              ('state_id', '!=', False)])
                if prov_ids:
                    self.cod_provincia_pl = prov_ids
                    self.cod_departamento_pl = state_ids
                    self.cod_distrito_pl = dist_ids
            else:
                raise Warning('Solo se puede consultar RUC por SUNAT..!')
        else:
            True

    @api.one
    def update_document_c(self):
        if self.tipo_documento_c and self.num_documento_c and self.num_documento_c != '':
            # Valida RUC
            if len(self.num_documento_c) == 11 and self.tipo_documento_c == '6':
                d = get_data_doc_number(
                    'ruc', self.num_documento_c, format='json')
                if d['error']:
                    return True
                d = d['data']
                self.nom_c = d['nombre_comercial'] != '-' and d['nombre_comercial'] or d['nombre']
            else:
                raise Warning('Solo se puede consultar RUC por SUNAT..!')
        else:
            True

class ItemGuide(models.Model):

        _name = 'test_techquk.item'
        _description = 'Item(Bien o Servicio) de la Guía de Remisión'

        guide_id = fields.Many2one('test_techquk.guide',"Guía de Remisión")
        name = fields.Char('Descripción Detallada',required=True)
        numero_orden = fields.Char("Nro")
        codigo_bien = fields.Char("Código del Bien")
        unidad_medida = fields.Char("Unidad de Medida")
        cantidad = fields.Float("Cantidad")

class UoM(models.Model):

        _inherit = 'uom.uom'
        codigo = fields.Char('Codigo')


