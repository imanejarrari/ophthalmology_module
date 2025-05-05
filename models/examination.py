from odoo import models, fields, api
from datetime import date

class OphthalmologyExamination(models.Model):
    _name = 'ophthalmology.examination'
    _description = 'Eye Examination Record'
    _order = 'date desc'

    patient_id = fields.Many2one('ophthalmology.patient', string="Patient", required=True)
    appointment_id = fields.Many2one('ophthalmology.appointment', string="Appointment", ondelete='set null')
    date = fields.Date(string="Examination Date", default=date.today, required=True)
    doctor_name = fields.Char(string="Doctor", required=True)

    visual_acuity_right = fields.Char(string="Visual Acuity (Right Eye)")
    visual_acuity_left = fields.Char(string="Visual Acuity (Left Eye)")
    intraocular_pressure_right = fields.Float(string="Intraocular Pressure (Right Eye)")
    intraocular_pressure_left = fields.Float(string="Intraocular Pressure (Left Eye)")
    eye_condition_notes = fields.Text(string="Eye Condition Notes")

    attachment_ids = fields.Many2many('ir.attachment', string="Attachments")

    @api.onchange('appointment_id')
    def _onchange_appointment_id(self):
        if self.appointment_id:
            self.patient_id = self.appointment_id.patient_id.id
            self.doctor_name = self.appointment_id.doctor_name
