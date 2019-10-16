from odoo import api, fields, models
import datetime

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
                                                arr.append((0, 0, {'product_id': item.name.id,'name': item.name.name,'date_planned': datetime.datetime.now(),'product_qty': item.cantidad,'product_uom':item.unidad}))
                        self.order_line = arr

