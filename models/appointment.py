from odoo import models, fields, api, exceptions
from datetime import date
import pytz  

class Appointment(models.Model):
    _name = 'ophthalmology.appointment'
    _description = 'Ophthalmology Appointment'
    _rec_name = 'patient_serial'  
    
    patient_serial = fields.Char(related='patient_id.patient_serial', string='Patient Serial', store=True)
    
    _inherit = ['mail.thread', 'mail.activity.mixin']

    patient_id = fields.Many2one('ophthalmology.patient', string='Patient', required=True)
    date = fields.Datetime(string='Appointment Date', required=True)
    doctor_name = fields.Char(string='Doctor Name')
    purpose = fields.Text(string='Purpose of Visit')
    diagnosis = fields.Text(string='Diagnosis')
    treatment = fields.Text(string='Treatment')

    workflow_status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='work flow status', default='draft', tracking=True)

    date_status = fields.Char(string="Date Status", compute='_compute_date_status', store=True)

    prescription_ids = fields.One2many(
        'ophthalmology.prescription',
        'appointment_id',
        string='Prescriptions'
    )

    examination_ids = fields.One2many('ophthalmology.examination', 'appointment_id', string="Examinations")

    examination_count = fields.Integer(string="Examination Count", compute="_compute_examination_count")
    prescription_count = fields.Integer(string="Prescription Count", compute="_compute_prescription_count")

    patient_appointment_ids = fields.One2many(
        'ophthalmology.appointment',
        compute='_compute_patient_appointments',
        string="Other Appointments",
        store=False
    )




    @api.depends('patient_id')
    def _compute_patient_appointments(self):
        for rec in self:
            if rec.patient_id:
                rec.patient_appointment_ids = self.search([
                    ('patient_id', '=', rec.patient_id.id),
                    ('id', '!=', rec.id)
                ])
            else:
                rec.patient_appointment_ids = False

    @api.depends('examination_ids')
    def _compute_examination_count(self):
        for rec in self:
            rec.examination_count = len(rec.examination_ids)

    @api.depends('prescription_ids')
    def _compute_prescription_count(self):
        for rec in self:
            rec.prescription_count = len(rec.prescription_ids)

    @api.depends('date')
    def _compute_date_status(self):
        for rec in self:
            if not rec.date:
                rec.date_status = 'No appointment'
            else:
                user_tz = pytz.timezone(self.env.user.tz or 'UTC')
                appointment_date_tz = pytz.utc.localize(rec.date).astimezone(user_tz).date()
                today = date.today()
                if appointment_date_tz == today:
                    rec.date_status = 'Today'
                elif appointment_date_tz < today:
                    rec.date_status = 'Missed'
                else:
                    rec.date_status = 'Upcoming'


    @api.model
    def create(self, vals):
        result = super(Appointment, self).create(vals)
        
        if result.patient_id and not result.patient_id.patient_serial:
            serial = self.env['ir.sequence'].next_by_code('ophthalmology.patient.serial')
            result.patient_id.write({'patient_serial': serial})
        
        return result


    @api.constrains('date', 'patient_id')
    def _check_overlapping_appointments(self):
        for rec in self:
            domain = [
                ('patient_id', '=', rec.patient_id.id),
                ('date', '=', rec.date),
                ('id', '!=', rec.id),
            ]
            overlapping_appointments = self.search(domain)
            if overlapping_appointments:
                raise exceptions.ValidationError("This patient already has an appointment at this time.")

    def name_get(self):
        result = []
        for rec in self:
            name = rec.patient_serial or f"ophthalmology.appointment,{rec.id}"
            result.append((rec.id, name))
        return result



    def start_examination_popup(self):
     return {
        'type': 'ir.actions.act_window',
        'name': 'Start Examination',
        'res_model': 'ophthalmology.examination',
        'view_mode': 'form',
        'target': 'new',  
        'context': {
            'default_appointment_id': self.id,
            'default_patient_id': self.patient_id.id,
        },
    }
