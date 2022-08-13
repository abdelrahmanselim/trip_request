from odoo import fields, models, api


class Employee(models.Model):
    _inherit = 'hr.employee'
    hr_contract = fields.One2many('hr.contract.history', 'employee_id')
    allowed_destination = fields.Many2many('res.country')
    trip_request = fields.One2many('trip.request', 'emp_id')
    trip_count = fields.Integer(string='Trip Count', compute='_compute_trip_count')

    @api.depends('trip_request')
    def _compute_trip_count(self):
        for trip in self:
            trip_count = self.env['trip.request'].search_count([('emp_id', '=', trip.id)])
            trip.trip_count = trip_count
    def trip_req(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'trip',
            'res_model': 'trip.request',
            'domain': [('emp_id', '=', self.id)],
            'context': {'default_emp_id': self.id},
            'view_mode': 'tree,form',
            'target': 'current',
        }
