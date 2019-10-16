# -*- coding: utf-8 -*-
from odoo import http

# class TechqukRequerimiento(http.Controller):
#     @http.route('/techquk_requerimiento/techquk_requerimiento/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/techquk_requerimiento/techquk_requerimiento/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('techquk_requerimiento.listing', {
#             'root': '/techquk_requerimiento/techquk_requerimiento',
#             'objects': http.request.env['techquk_requerimiento.techquk_requerimiento'].search([]),
#         })

#     @http.route('/techquk_requerimiento/techquk_requerimiento/objects/<model("techquk_requerimiento.techquk_requerimiento"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('techquk_requerimiento.object', {
#             'object': obj
#         })