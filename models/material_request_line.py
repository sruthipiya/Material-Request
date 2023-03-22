from odoo import models, fields, _, api


class MaterialRequestLine(models.Model):
    _name = "material.request.line"

    def _default_source_location(self):
        return self.env['stock.location'].search(
            [('complete_name', '=', 'WH')])

    def _default_dest_location(self):
        return self.env['stock.location'].search(
            [('complete_name', '=', 'Partners')])

    request_line_id = fields.Many2one('material.request')
    product_id = fields.Many2one('product.product', string="Product")
    qty = fields.Integer(default=1, string="Quantity")
    product_route = fields.Selection(string="Type",
                                     selection=[('po', 'Purchase Order'), (
                                         'internal', 'Internal Transfer')])
    source_id = fields.Many2one('stock.location',
                                default=_default_source_location)
    dest_id = fields.Many2one('stock.location', default=_default_dest_location)

