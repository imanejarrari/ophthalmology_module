from odoo import models, fields, api
from datetime import date

class Patient(models.Model):
    _name = 'ophthalmology.patient'
    _description = 'Patient details for the ophthalmology clinic'

    name = fields.Char(string='Patient Name', required=True)
    age = fields.Integer(string='Age')
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female')],
        string='Gender',
        default='male'
    )
    contact_number = fields.Char(string='Contact Number')
    email = fields.Char(string='Email')
    address = fields.Text(string='Address')

    general_health_history = fields.Text(string='General Health History')
    eye_health_history = fields.Text(string='Eye Health History')

    appointment_ids = fields.One2many('ophthalmology.appointment', 'patient_id', string='Appointments')
    vitals_ids = fields.One2many('ophthalmology.vitals', 'patient_id', string='Vitals')
    prescription_ids = fields.One2many('ophthalmology.prescription', 'patient_id', string='Prescriptions')

    appointment_count = fields.Integer(string='Appointment Count', compute='_compute_appointment_count')
    has_chronic_disease = fields.Boolean(string='Has Chronic Disease', compute='_compute_chronic_disease', store=True)
    appointment_status = fields.Char(string="Next Appointment Status", compute="_compute_appointment_status", store=True)
    active = fields.Boolean(string="Active", default=True)

    @api.depends('appointment_ids.date', 'appointment_ids.date_status')
    def _compute_appointment_status(self):
        today = date.today()
        for patient in self:
            status = "No Appointments"
            upcoming_appointments = sorted(
                [appt for appt in patient.appointment_ids if appt.date],
                key=lambda a: a.date
            )
            if upcoming_appointments:
                next_appt = upcoming_appointments[0]
                status = next_appt.date_status or "Unknown"
            patient.appointment_status = status

    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        for record in self:
            record.appointment_count = len(record.appointment_ids)

    @api.depends('general_health_history')
    def _compute_chronic_disease(self):
        for record in self:
            if record.general_health_history:
                keywords = ['diabetes', 'hypertension', 'asthma', 'cancer']
                record.has_chronic_disease = any(
                    keyword.lower() in record.general_health_history.lower() for keyword in keywords
                )
            else:
                record.has_chronic_disease = False

    @api.model
    def get_dashboard_data(self):
        today = fields.Date.today()
        now = fields.Datetime.now()

        patients = self.search([('active', '=', True)])
        new_patients = patients.filtered(lambda p: p.create_date.date() == today)
        old_patients = patients.filtered(lambda p: p.create_date.date() < today)

        appointments = self.env['ophthalmology.appointment'].search([('date', '>=', now)])
        today_appointments = appointments.filtered(lambda a: a.date.date() == today)

        return {
            'total_patients': len(patients),
            'new_patients': len(new_patients),
            'old_patients': len(old_patients),
            'today_appointments': [
                {
                    'patient_name': a.patient_id.name,
                    'time': a.date.strftime('%H:%M'),
                }
                for a in today_appointments
            ]
        }
