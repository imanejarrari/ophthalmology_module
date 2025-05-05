from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class Prescription(models.Model):
    _name = 'ophthalmology.prescription'
    _description = 'Prescription details for ophthalmology patients'

    name = fields.Char(string='Prescription Name', required=True)
    patient_id = fields.Many2one('ophthalmology.patient', string='Patient', ondelete='cascade')
    appointment_id = fields.Many2one('ophthalmology.appointment', string='Appointment')
    date_prescribed = fields.Datetime(string='Date Prescribed', default=fields.Datetime.now)
    doctor_id = fields.Many2one('res.users', string='Doctor')
    medications = fields.Text(string='Medications Prescribed')
    notes = fields.Text(string='Notes')

    @api.model
    def create(self, vals_list):
        _logger.debug('Creating prescription with vals_list: %s', vals_list)

        if isinstance(vals_list, list):  
            for vals in vals_list:
                if not vals.get('name'):
                    vals['name'] = 'New Prescription'
        else:  
            if not vals_list.get('name'):
                vals_list['name'] = 'New Prescription'

        return super(Prescription, self).create(vals_list)
