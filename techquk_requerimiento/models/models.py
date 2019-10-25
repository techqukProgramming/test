# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime

class Requeriment(models.Model):

    _name = 'techquk_requerimiento.requerimiento'
    _description = 'Modelo de requerimiento'

    area = fields.Many2one("techquk_requerimiento.area","Area",required=True)
    centrocosto = fields.Many2one("techquk_requerimiento.centro","Centro de Costo",required=True)
    name = fields.Char("N° de Requerimiento",readonly=True,default=lambda self: self.env['ir.sequence'].next_by_code('techquk_requerimiento.requerimiento'))
    fecha_inicio = fields.Date("Fecha de Creación", required=True,default=fields.Date.today())

    rnombre = fields.Many2one("res.users","Nombre",default=lambda self: self.env.user)
    realizado = fields.Boolean("",default=False)
    renombre = fields.Many2one("res.users","Nombre")
    revisado = fields.Boolean("",default=False)
    anombre = fields.Many2one("res.users","Nombre")
    autorizado = fields.Boolean("",default=False)
    atnombre = fields.Many2one("res.users","Nombre")
    atendido = fields.Boolean("",default=False)
    observador = fields.Text("Descripcion",size=50)
    observacion = fields.Boolean("",default=False)

    items_id = fields.One2many('techquk_requerimiento.item','requerimiento_id',string="Items")
    items_ids = fields.Many2many('techquk_requerimiento.item','items_id',string="Items")

    state = fields.Selection([
    ('observado', 'Observado'),
    ('realizado', 'Realizado'),
    ('revisado', 'Revisado'),
    ('autorizado', 'Autorizado'),
    ('atendido', 'Atendido'),
    ], string='Estado')

    @api.onchange('realizado')
    def _change_state_realizado(self):
        if self.realizado == True and self.rnombre:
            self.state = 'realizado'
        elif not self.rnombre:
            self.realizado = False
            
    @api.onchange('revisado')
    def _change_state_revisado(self):
        if self.revisado == True and self.renombre:
            self.state = 'revisado'
            self.realizado = True
        elif not self.renombre:
            self.revisado = False
    
    @api.onchange('autorizado')
    def _change_state_autorizado(self):
        if self.autorizado == True and self.anombre:
            self.state = 'autorizado'
            self.revisado = True
            self.realizado = True
        elif not self.anombre:
            self.autorizado = False
    
    @api.onchange('atendido')
    def _change_state_atendido(self):
        if self.atendido == True and self.atnombre:
            self.state = 'atendido'
            self.autorizado = True
            self.revisado = True
            self.realizado = True
        elif not self.atnombre:
            self.atendido = False

    @api.onchange('observacion')
    def _change_state_observado(self):
        if self.observacion==True and self.observador:
            self.state = 'observado'
        elif not self.observador:
            self.observacion = False

        else:
            self.observador = ''
            if self.atendido == True:
                self.state = 'atendido'
            elif self.autorizado == True:
                self.state = 'autorizado'
            elif self.revisado == True:
                self.state = 'revisado'
            elif self.realizado == True:
                self.state = 'realizado'

    @api.onchange('centrocosto')
    def _get_partner_id(self):
        context = self._context
        current_uid = context.get('uid')
        user = self.env['res.users'].browse(current_uid)
        return {'domain':{'rnombre':[('id','=',user.id)]}}

    @api.model
    def _get_next_requerimentname(self):
        sequence = self.env['ir.sequence'].search([('code','=','techquk_requerimiento.requerimiento')]) #next = 8
        next= sequence.get_next_char(sequence.number_next_actual) #next = 9
        return next #retorno 9

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('techquk_requerimiento.requerimiento') #10
        result = super(Requeriment, self).create(vals) #se crea el nuevo requerimiento con el name 10 por defecto
        return result   

class Item(models.Model):

    _name = 'techquk_requerimiento.item'
    _description = 'item del requerimiento'

    requerimiento_id = fields.Many2one('techquk_requerimiento.requerimiento',"Requerimiento")
    name = fields.Many2one('product.template','Descripción',required=True)
    numeroparte = fields.Char("Numero de Parte")
    unidad = fields.Many2one('uom.uom','Medida')
    cantidad = fields.Float("Cantidad")
    fechaentrega = fields.Date("Fecha de Entrega",default=fields.Date.today())
    tiporequerimiento = fields.Selection([
    ('prestamo', 'Prestamo'),
    ('abastecimiento', 'Abastecimiento'),
    ('servicio', 'Servicio')
    ],'Tipo',default='abastecimiento')
    proveedorsugerido = fields.Many2one('res.partner','Proveedores',context={'search_default_supplier':1,'default_supplier':1,'default_customer':0},domain="[('supplier','=',True)]",required=True)
    observaciones = fields.Text("Observaciones")
    documentacion = fields.Many2many('ir.attachment',string="Documentacion")

    @api.onchange('name')
    def _get_unidad(self):
        if self.name:    
            self.unidad = self.name.uom_id
        else:
            self.descripcion = ''
    
class Document(models.Model):
    
    _name = 'techquk_requerimiento.document'
    _description= 'Documento para Item'

    name = fields.Char('Nombre')
    descripcion = fields.Char('Descripcion')

class Area(models.Model):
    
    _name = 'techquk_requerimiento.area'
    _description= 'Area para el requerimiento'

    name = fields.Char('Nombre')
    descripcion = fields.Char('Descripcion')

class Centro(models.Model):
    
    _name = 'techquk_requerimiento.centro'
    _description= 'Centro para el requerimiento'

    name = fields.Char('Nombre')
    descripcion = fields.Char('Descripcion')

   