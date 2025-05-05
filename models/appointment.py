from odoo import models, fields, api
from datetime import date

class Appointment(models.Model):
    _name = 'ophthalmology.appointment'
    _description = 'Appointment for Ophthalmology Patients'
    _inherit = ['mail.thread', 'mail.activity.mixin']  


    patient_id = fields.Many2one('ophthalmology.patient', string='Patient', ondelete='cascade')
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
    ], string='Status', default='draft')

    date_status = fields.Char(string="Date Status", compute='_compute_date_status', store=True)

    prescription_ids = fields.One2many(
        'ophthalmology.prescription',
        'appointment_id',
        string='Prescriptions'
    )

    examination_ids = fields.One2many('ophthalmology.examination', 'appointment_id', string="Examinations")

    examination_count = fields.Integer(string="Examination Count", compute="_compute_examination_count")

    @api.depends('examination_ids')
    def _compute_examination_count(self):
        for rec in self:
            rec.examination_count = len(rec.examination_ids)

    @api.depends('date')
    def _compute_date_status(self):
        today = date.today()
        for rec in self:
            if not rec.date:
                rec.date_status = 'No appointment'
            else:
                appointment_date = rec.date.date()
                if appointment_date == today:
                    rec.date_status = 'Today'
                elif appointment_date < today:
                    rec.date_status = 'Missed'
                else:
                    rec.date_status = 'Upcoming'

    def action_confirm(self):
        for rec in self:
            rec.workflow_status = 'confirmed'

    def action_mark_done(self):
        for rec in self:
            rec.workflow_status = 'done'

    def action_cancel(self):
        for rec in self:
            rec.workflow_status = 'cancelled'
