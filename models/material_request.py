from odoo import models, fields, _, api


class MaterialRequest(models.Model):
    _name = "material.request"
    _description = "Material Request"
    _rec_name = 'request'
    _inherit = 'mail.thread'

    def _default_user(self):
        return self.env.user.partner_id

    request = fields.Char(default=lambda self: _('New'), readonly=True)
    name_id = fields.Many2one('res.partner', default=_default_user,
                              readonly=True)
    date = fields.Datetime(default=fields.Date.today())
    product_line_ids = fields.One2many('material.request.line',
                                       'request_line_id')
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('toapprove', 'To Approve'), ('approved', 'Approved'),
        ('rejected', 'Rejected')],
        string="Status", required=True, readonly=True,
        copy=False,
        tracking=True, default='draft')
    po_count = fields.Integer(compute='compute_count_po')
    internal_count = fields.Integer(compute='compute_count_internal')

    @api.model
    def create(self, vals):
        if vals.get('request', 'New') == 'New':
            vals['request'] = self.env['ir.sequence'].next_by_code(
                'material.request') or 'New'
        res = super(MaterialRequest, self).create(vals)
        return res

    def action_submit(self):
        self.state = 'toapprove'

    def action_approve(self):
        for line in self.product_line_ids:
            if line.product_route == 'po':
                for rec in line.product_id.seller_ids:
                    self.env['purchase.order'].create({
                        'partner_id': rec.partner_id.id,
                        'partner_ref': self.request,
                        'order_line': [(0, 0, {
                            'product_id': line.product_id.id,
                            'product_qty': line.qty,

                        })]
                    })
            else:
                self.env['stock.picking'].create({
                    'partner_id': self.name_id.id,
                    'picking_type_id': self.env.ref(
                        'stock.picking_type_internal').id,
                    'location_id': line.source_id.id,
                    'location_dest_id': line.dest_id.id,
                    'origin': self.request,
                    'move_ids_without_package': [(0, 0, {
                        'product_id': line.product_id.id,
                        'quantity_done': line.qty,
                        'location_id': line.source_id.id,
                        'location_dest_id': line.dest_id.id,
                        'name': 'Test',

                    })]
                })
        self.state = 'approved'

    def action_reject(self):
        self.state = 'rejected'

    def get_po_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Order',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': [('partner_ref', '=', self.request)],
            'context': "{'create': False}"
        }

    def get_internal_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Order',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': [('origin', '=', self.request)],
            'context': "{'create': False}"
        }

    def compute_count_po(self):
        self.po_count = self.env['purchase.order'].search_count(
            [('partner_ref', '=', self.request)])

    def compute_count_internal(self):
        self.internal_count = self.env['stock.picking'].search_count(
            [('origin', '=', self.request)])
