from odoo import models, fields, api
from odoo.exceptions import UserError

class OphthalmologyExamination(models.Model):
    _name = 'ophthalmology.examination'
    _description = 'Eye Examination Record'
    _order = 'date desc'

    patient_id = fields.Many2one('ophthalmology.patient', string="Patient", required=True)
    appointment_id = fields.Many2one('ophthalmology.appointment', string="Appointment", ondelete='set null')
    date = fields.Date(default=fields.Date.context_today, string="Examination Date")
    doctor_name = fields.Char(string="Doctor", required=True)

    eye_selection = fields.Selection([
        ('left', 'Left Eye'),
        ('right', 'Right Eye'),
        ('both', 'Both Eyes')
    ], string="Eye(s) Examined", required=True)

    visual_acuity_right = fields.Char(string="Visual Acuity Right Eye")
    visual_acuity_left = fields.Char(string="Visual Acuity Left Eye")
    intraocular_pressure_right = fields.Float(string="Intraocular Pressure Right Eye")
    intraocular_pressure_left = fields.Float(string="Intraocular Pressure Left Eye")
    eye_condition_notes = fields.Text(string="Eye Condition Notes")

    attachment_ids = fields.Many2many('ir.attachment', string="Attachments")

    prescription_ids = fields.One2many(
        'ophthalmology.prescription', 'examination_id',
        string="Prescriptions"
    )

    examination_price = fields.Float(string="Examination Price", default=200.0)


    def print_prescription(self):
        try:
            action = self.env.ref('ophthalmology.action_report_prescription_from_exam', raise_if_not_found=False)
            
            if not action:
                action = self.env['ir.actions.report'].create({
                    'name': 'Prescription from Examination',
                    'model': 'ophthalmology.examination',
                    'report_type': 'qweb-pdf',
                    'report_name': 'ophthalmology.report_prescription_document_from_exam',
                    'report_file': 'ophthalmology.report_prescription_document_from_exam',
                    'binding_model_id': self.env['ir.model'].search([('model', '=', 'ophthalmology.examination')], limit=1).id,
                    'print_report_name': "'Prescription - %s' % (object.patient_id.name)",
                })
                
            return action.report_action(self)
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Failed to find report: %s", str(e))
            raise UserError(f"Le rapport n'est pas trouvé. Erreur: {str(e)}")



    @api.onchange('appointment_id')
    def _onchange_appointment_id(self):
        if self.appointment_id:
            self.patient_id = self.appointment_id.patient_id.id
            self.doctor_name = self.appointment_id.doctor_name
