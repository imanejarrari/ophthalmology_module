from odoo import models, fields

class Vitals(models.Model):
    _name = 'ophthalmology.vitals'
    _description = 'Vitals Information for Patients'

    patient_id = fields.Many2one('ophthalmology.patient', string='Patient', ondelete='cascade')
    date = fields.Date(string='Date', required=True)
    blood_pressure = fields.Char(string='Blood Pressure')
    heart_rate = fields.Integer(string='Heart Rate')
    vision_right = fields.Char(string='Right Eye Vision')
    vision_left = fields.Char(string='Left Eye Vision')
    notes = fields.Text(string='Additional Notes')
