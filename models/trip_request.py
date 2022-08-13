from odoo import fields, models, api
from odoo.exceptions import UserError
from datetime import datetime


class Trip_Request(models.Model):
    _name = "trip.request"
    start_date = fields.Date()
    end_date = fields.Date()
    rest_days = fields.Integer()
    trip_days = fields.Integer(compute="calc_trip_days")
    emp_id = fields.Many2one('hr.employee', domain=[('contract_id.state', '=', 'open')])
    destination = fields.Many2one('res.country')
    update_status_employee = fields.Many2one('res.users')
    state = fields.Selection([
        ('draft', 'draft'),
        ('confirmed', 'confirmed'),
        ('ended', 'ended'),
        ('cancelled', 'cancelled'),
    ])

    def write(self, vals):
        super(Trip_Request, self).write(vals)
        for emp in self:
            if 'state' in vals:
                emp.update_status_employee = self._uid
    @api.onchange("emp_id")
    def allowed_destination(self):
        for trip in self:
            if trip.emp_id:
                return {'domain': {'destination': [('id', 'in', self.emp_id.allowed_destination.ids)]}}
    @api.depends("start_date", "end_date")
    def calc_trip_days(self):
        for trip in self:
            if trip.start_date and trip.end_date:
                delta = (trip.end_date - trip.start_date).days
                if delta > 0:
                    trip.trip_days = delta
                else:
                    trip.trip_days = 0
            else:
                trip.trip_days = 0

    @api.onchange('start_date')
    def change_end_date(self):
        self.end_date = None

    def draft(self):
        self.state = 'draft'

    def confirmed(self):
        self.state = 'confirmed'

    def cancelled(self):
        self.state = 'cancelled'

    def ended(self):
        self.state = 'ended'

    @api.constrains("end_date")
    def check_end_dat(self):
        start_date = self.start_date.strftime('%Y-%m-%d')
        end_date = self.end_date.strftime('%Y-%m-%d')
        if start_date > end_date:
            raise UserError("End Date Invalid")

    @api.model
    def trip_crone_job(self):
        list = self.search([(1, '=', 1)])
        for trip in list:
            today = fields.Date.today()
            end_date = trip.end_date
            if trip.state == 'confirmed':
                if today > end_date:
                    trip.state = 'ended'


