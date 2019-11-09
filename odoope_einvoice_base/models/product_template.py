# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009-TODAY Odoo Peru(<http://www.odooperu.pe>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import api, fields, models
from random import randrange,choice

class ProductTemplate(models.Model):
        _name = 'product.template'
        _inherit = ['product.template']

        igv_type = fields.Many2one("einvoice.catalog.07", string='IGV type')
        product_code_sunat = fields.Many2one("einvoice.catalog.25", string='Product code SUNAT')
        product_code = fields.Char("Codigo")
        product_marca = fields.Char("Marca",default='-')
        margen = fields.Float(string="Margen(%)",digits=(10,2),default='20')
        descuento = fields.Float(string="Descuento(%)",digits=(10,2),default='0')
        gasto_administrativo = fields.Float(string="Gasto Adm.(%)",digits=(10,2),default='2')
        costo_flete = fields.Float(string="Costo Flete",digits=(10,2),default='0')
        ganancia = fields.Float(string="Ganancia",digits=(10,2),default='0')

        #Validar producto que no se repita el código.
        @api.onchange('product_code')
        def validate_duplicate_product(self):
                validate = self.env['product.template'].search([('product_code','=',self.product_code)], limit=1)
                if len(validate) > 0:
                        self.default_code = ''
                        self.product_code = ''
                        return {
                                'warning': {
                                                'title': 'Advertencia!',
                                                'message': 'El código del producto es duplicado. Porfavor, cambielo!'}
                                        }
                elif self.product_code:
                        self.default_code = self.product_code   

        @api.onchange('type')
        def _get_number_aleatory(self):
                value = ''
                for val in range(0,6):
                        a = randrange(10)
                        value += str(a)
                        extra = choice(["TQA", "TQB"])
                self.product_code = extra+'-'+value

        @api.onchange('standard_price')
        def calcularPrecioVenta0(self):
                if self.standard_price >= 0 and self.margen >= 20 and self.gasto_administrativo >= 2:
                                self.list_price = (float(self.margen) * self.standard_price/100.00 + self.standard_price)
                                self.list_price = self.list_price - (float(self.gasto_administrativo)*self.list_price/100.00)
                                self.ganancia = self.list_price - self.standard_price
                else:
                        return {
                                'warning': {
                                                'title': 'Advertencia!',
                                                'message': 'Debe ingresar el costo(precio de compra), el margen de ganancia debe ser MAYOR a 20% y el gasto administrativo MAYOR al 2%!'}
                                        }

        @api.onchange('margen')
        def calcularPrecioVenta(self):
                if self.standard_price >= 0 and self.margen >= 20 and self.gasto_administrativo >= 2:
                                 self.list_price = (float(self.margen) *  self.standard_price/100.00 +  self.standard_price)
                                 self.list_price = self.list_price - (float(self.gasto_administrativo)*self.list_price/100.00) 
                                 self.ganancia = self.list_price - self.standard_price                  
                else:
                        self.margen = 20
                        return {
                                'warning': {
                                                'title': 'Advertencia!',
                                                'message': 'Debe ingresar el costo(precio de compra), el margen de ganancia debe ser MAYOR a 20% y el gasto administrativo MAYOR al 2%!'}
                                        }

        @api.onchange('costo_flete')
        def calcularPrecioVenta2(self):
                if self.standard_price >= 0 and self.margen >= 20 and self.gasto_administrativo >= 2:
                        if self.costo_flete >= 0:
                                self.list_price = (float(self.margen) *  self.standard_price/100.00 +  self.standard_price)
                                self.list_price = self.list_price - (float(self.gasto_administrativo)*self.list_price/100.00)
                                self.list_price = (self.list_price + self.costo_flete) 
                                self.ganancia = self.list_price - self.standard_price
                else:
                        self.costo_flete = 0
                        return {
                                'warning': {
                                                'title': 'Advertencia!',
                                                'message': 'Debe ingresar el costo(precio de compra), el margen de ganancia debe ser MAYOR a 20% y el gasto administrativo MAYOR al 2%!'}
                                        }
        
        @api.onchange('gasto_administrativo')
        def calcularPrecioVenta3(self):
                if self.standard_price >= 0 and self.margen >= 20 and self.gasto_administrativo >= 2:
                        if self.gasto_administrativo >= 0:
                                self.list_price = (float(self.margen) *  self.standard_price/100.00 +  self.standard_price)
                                self.list_price = self.list_price - (float(self.gasto_administrativo)*self.list_price/100.00)
                                self.list_price = (self.list_price + self.costo_flete) 
                                self.ganancia = self.list_price - self.standard_price
                else:
                        self.gasto_administrativo = 2
                        return {
                                'warning': {
                                                'title': 'Advertencia!',
                                                'message': 'Debe ingresar el costo(precio de compra), el margen de ganancia debe ser MAYOR a 20% y el gasto administrativo MAYOR al 2%!'}
                                        }
        
        @api.onchange('descuento')
        def calcularPrecioVenta4(self):
                if self.standard_price >= 0 and self.margen >= 20 and self.gasto_administrativo >= 2:
                        if self.descuento >= 0:
                                self.list_price = (float(self.margen) *  self.standard_price/100.00 +  self.standard_price)
                                self.list_price = self.list_price - (float(self.gasto_administrativo)*self.list_price/100.00)
                                self.list_price = (self.list_price + self.costo_flete) 
                                self.list_price = (self.list_price - float(self.descuento)*self.list_price/100.00)
                                self.ganancia = self.list_price - self.standard_price
                else:
                        self.gasto_administrativo = 0
                        return {
                                'warning': {
                                                'title': 'Advertencia!',
                                                'message': 'Debe ingresar el costo(precio de compra), el margen de ganancia debe ser MAYOR a 20% y el gasto administrativo MAYOR al 2%!'}
                                        }

