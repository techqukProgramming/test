from odoo import api, fields, models
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class PurchaseInherit(models.Model):

        _inherit = 'purchase.order'

        id_requerimiento = fields.Many2one("techquk_requerimiento.requerimiento","Requerimiento")

        @api.onchange('id_requerimiento')
        def _get_suppliers(self):
                if self.id_requerimiento:
                        arr = []
                        unico = []
                        for x in self.id_requerimiento:      
                                for item in x.items_ids:
                                        arr.append(item.proveedorsugerido)
                        for x in arr:
                                if x not in unico:
                                        unico.append(x)

                        if len(unico) == 1:       
                                return {'domain':{'partner_id':[('id','=',unico[0].id)]}}
                        elif len(unico) == 2:       
                                return {'domain':{'partner_id':['|',('id','=',unico[0].id),('id','=',unico[1].id)]}}
                        elif len(unico) == 3:       
                                return {'domain':{'partner_id':['|',('id','=',unico[0].id),('id','=',unico[1].id),('id','=',unico[2].id)]}}
                        elif len(unico) == 4:       
                                return {'domain':{'partner_id':['|',('id','=',unico[0].id),('id','=',unico[1].id),('id','=',unico[2].id),('id','=',unico[3].id)]}}
                        elif len(unico) == 5:       
                                return {'domain':{'partner_id':['|',('id','=',unico[0].id),('id','=',unico[1].id),('id','=',unico[2].id),('id','=',unico[3].id),('id','=',unico[4].id)]}}
                        else:
                             return {
                                'warning': {
                                        'title': 'Advertencia!',
                                        'message': 'No puede seleccionar requermiento que tengan mas de 5 proveedores!'}
                                }

        @api.onchange('partner_id')
        def _get_items(self):
                self.order_line = [(6, 0, {})]
                arr = []        
                if self.partner_id and self.id_requerimiento:
                        for x in self.id_requerimiento:      
                                for item in x.items_ids:
                                        if self.partner_id.id == item.proveedorsugerido.id:
                                                arr.append((0, 0, {'product_id': item.name.id,'name': item.name.name,'date_planned': datetime.now(),'product_qty': item.cantidad,'product_uom':item.unidad,'price_unit':item.name.list_price,'standard_price':item.name.standard_price,'margen':item.name.margen,'gasto_administrativo':item.name.gasto_administrativo,'costo_flete':item.name.costo_flete,'descuento':item.name.descuento,'ganancia':item.name.ganancia,'taxes_id':item.name.supplier_taxes_id}))
                        self.order_line = arr

class PurchaseOrderLineInherit(models.Model):

        _inherit = 'purchase.order.line'

        descuento = fields.Float(string="Descuento(%)",digits=(10,2),default='0')
        margen = fields.Float(string="Margen(%)",digits=(10,2),default='20')
        gasto_administrativo = fields.Float(string="Gasto Adm.(%)",digits=(10,2),default='2')
        costo_flete = fields.Float(string="Costo Flete",digits=(10,2),default='0')
        ganancia = fields.Float(string="Ganancia",digits=(10,2),default='0')
        standard_price = fields.Float(string="Costo",digits=(10,2),default='0')

        @api.onchange('product_id')
        def onchange_product_id_2(self):
                result = {}
                if not self.product_id:
                        return result

                # Reset date, price and quantity since _onchange_quantity will provide default values
                self.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                self.price_unit = self.product_qty = 0.0
                self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
                result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

                product_lang = self.product_id.with_context(
                lang=self.partner_id.lang,
                partner_id=self.partner_id.id,
                )
                self.name = product_lang.display_name
                self.descuento = product_lang.descuento
                self.margen = product_lang.margen
                self.gasto_administrativo = product_lang.gasto_administrativo
                self.costo_flete = product_lang.costo_flete
                self.ganancia = product_lang.ganancia
                self.price_unit = product_lang.list_price
                self.standard_price = product_lang.standard_price

                if product_lang.description_purchase:
                        self.name += '\n' + product_lang.description_purchase
                        self._compute_tax_id()
                        self._suggest_quantity()
                        self._onchange_quantity()

                return result

        @api.onchange('standard_price')
        def calcularPrecioVenta0(self):
                        if self.standard_price >= 0 and self.margen >= 20 and self.gasto_administrativo >= 2:
                                        self.price_unit = (float(self.margen) * self.standard_price/100.00 + self.standard_price)
                                        self.price_unit = self.price_unit - (float(self.gasto_administrativo)*self.price_unit/100.00)
                                        self.ganancia = self.price_unit - self.standard_price
                        else:
                                return {
                                        'warning': {
                                                        'title': 'Advertencia!',
                                                        'message': 'Debe ingresar el costo(precio de compra), el margen de ganancia debe ser MAYOR a 20% y el gasto administrativo MAYOR al 2%!'}
                                                }

        @api.onchange('margen')
        def calcularPrecioVenta(self):
                        if self.standard_price >= 0 and self.margen >= 20 and self.gasto_administrativo >= 2:
                                        self.price_unit = (float(self.margen) *  self.standard_price/100.00 +  self.standard_price)
                                        self.price_unit = self.price_unit - (float(self.gasto_administrativo)*self.price_unit/100.00) 
                                        self.ganancia = self.price_unit - self.standard_price                  
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
                                        self.price_unit = (float(self.margen) *  self.standard_price/100.00 +  self.standard_price)
                                        self.price_unit = self.price_unit - (float(self.gasto_administrativo)*self.price_unit/100.00)
                                        self.price_unit = (self.price_unit + self.costo_flete) 
                                        self.ganancia = self.price_unit - self.standard_price
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
                                        self.price_unit = (float(self.margen) *  self.standard_price/100.00 +  self.standard_price)
                                        self.price_unit = self.price_unit - (float(self.gasto_administrativo)*self.price_unit/100.00)
                                        self.price_unit = (self.price_unit + self.costo_flete) 
                                        self.ganancia = self.price_unit - self.standard_price
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
                                        self.price_unit = (float(self.margen) *  self.standard_price/100.00 +  self.standard_price)
                                        self.price_unit = self.price_unit - (float(self.gasto_administrativo)*self.price_unit/100.00)
                                        self.price_unit = (self.price_unit + self.costo_flete) 
                                        self.price_unit = (self.price_unit - float(self.descuento)*self.price_unit/100.00)
                                        self.ganancia = self.price_unit - self.standard_price
                        else:
                                self.gasto_administrativo = 0
                                return {
                                        'warning': {
                                                        'title': 'Advertencia!',
                                                        'message': 'Debe ingresar el costo(precio de compra), el margen de ganancia debe ser MAYOR a 20% y el gasto administrativo MAYOR al 2%!'}
                                                }
