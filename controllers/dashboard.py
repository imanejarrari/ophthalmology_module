from odoo import http, fields
from odoo.http import request

class OphthalmologyDashboard(http.Controller):

    @http.route('/ophthalmology/dashboard', auth='user', website=True)
    def dashboard(self, **kwargs):
        # Optimized searches for patients and appointments
        patients = request.env['ophthalmology.patient'].search([('active', '=', True)])
        appointments = request.env['ophthalmology.appointment'].search([('date', '>=', fields.Datetime.now())])

        # Filter today's appointments
        today_appointments = appointments.filtered(lambda a: a.date.date() == fields.Date.today())

        values = {
            'total_patients': len(patients),
            'new_patients': len(patients.filtered(lambda p: p.create_date.date() == fields.Date.today())),
            'old_patients': len(patients.filtered(lambda p: p.create_date.date() < fields.Date.today())),
            'today_appointments': today_appointments,
        }
        return request.render('ophthalmology.dashboard_template', values)
