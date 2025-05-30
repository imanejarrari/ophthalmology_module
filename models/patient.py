from odoo import models, fields, api
from datetime import date, timedelta

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
    patient_serial = fields.Char(string='Patient Serial', readonly=True, copy=False)

    general_health_history = fields.Text(string='General Health History')
    eye_health_history = fields.Text(string='Eye Health History')

    appointment_ids = fields.One2many('ophthalmology.appointment', 'patient_id', string='Appointments')
    vitals_ids = fields.One2many('ophthalmology.vitals', 'patient_id', string='Vitals')
    prescription_ids = fields.One2many('ophthalmology.prescription', 'patient_id', string='Prescriptions')

    appointment_count = fields.Integer(string='Appointment Count', compute='_compute_appointment_count')
    has_chronic_disease = fields.Boolean(string='Has Chronic Disease', compute='_compute_chronic_disease', store=True)
    appointment_status = fields.Char(string="Appointment Status", compute="_compute_appointment_status", store=True)
    active = fields.Boolean(string="Active", default=True)

    @api.depends('appointment_ids.date', 'appointment_ids.date_status')
    def _compute_appointment_status(self):
        today = date.today()
        for patient in self:
            status = "No Appointment"
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
        
        PatientModel = self.env['ophthalmology.patient']
        total_patients = PatientModel.search_count([])
        
        thirty_days_ago = today - timedelta(days=30)
        new_patients = PatientModel.search_count([
            ('create_date', '>=', thirty_days_ago)
        ])
        
        AppointmentModel = self.env['ophthalmology.appointment']
        total_appointments = AppointmentModel.search_count([])
        
        missed_appointments = AppointmentModel.search_count([
            ('date_status', '=', 'Missed')
        ])
        
        today_start = fields.Datetime.to_string(fields.Datetime.context_timestamp(self, now).replace(hour=0, minute=0, second=0))
        today_end = fields.Datetime.to_string(fields.Datetime.context_timestamp(self, now).replace(hour=23, minute=59, second=59))
        
        today_appointments = AppointmentModel.search([
            ('date', '>=', today_start),
            ('date', '<=', today_end)
        ], order='date asc')
        
        tomorrow = fields.Datetime.to_string(fields.Datetime.context_timestamp(self, now + timedelta(days=1)).replace(hour=0, minute=0, second=0))
        next_week = fields.Datetime.to_string(fields.Datetime.context_timestamp(self, now + timedelta(days=7)).replace(hour=23, minute=59, second=59))
        
        upcoming_appointments = AppointmentModel.search([
            ('date', '>=', tomorrow),
            ('date', '<=', next_week)
        ], order='date asc', limit=5)
        
        ExaminationModel = self.env['ophthalmology.examination']
        
        all_examinations = ExaminationModel.search([])
        total_revenue = sum(exam.examination_price for exam in all_examinations)
        
        # Weekly revenue
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        weekly_examinations = ExaminationModel.search([
            ('date', '>=', week_start),
            ('date', '<=', week_end)
        ])
        weekly_revenue = sum(exam.examination_price for exam in weekly_examinations)
        
        # Monthly revenue
        first_day_of_month = today.replace(day=1)
        last_day_of_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        monthly_examinations = ExaminationModel.search([
            ('date', '>=', first_day_of_month),
            ('date', '<=', last_day_of_month)
        ])
        monthly_revenue = sum(exam.examination_price for exam in monthly_examinations)
        
        # Yearly revenue
        first_day_of_year = today.replace(month=1, day=1)
        last_day_of_year = today.replace(month=12, day=31)
        yearly_examinations = ExaminationModel.search([
            ('date', '>=', first_day_of_year),
            ('date', '<=', last_day_of_year)
        ])
        yearly_revenue = sum(exam.examination_price for exam in yearly_examinations)
        
        # Calculate average examination price
        exam_count = len(all_examinations)
        average_examination_price = 0
        if exam_count > 0:
            average_examination_price = round(total_revenue / exam_count, 2)
        
        weekly_data = []
        weekly_labels = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_exams = ExaminationModel.search([
                ('date', '=', day)
            ])
            day_revenue = sum(exam.examination_price for exam in day_exams)
            weekly_data.append(day_revenue)
            weekly_labels.append(day.strftime('%a'))
        
        monthly_data = []
        monthly_labels = []
        for i in range(4):
            week_start = today - timedelta(days=today.weekday() + (i * 7))
            week_end = week_start + timedelta(days=6)
            week_exams = ExaminationModel.search([
                ('date', '>=', week_start),
                ('date', '<=', week_end)
            ])
            week_revenue = sum(exam.examination_price for exam in week_exams)
            monthly_data.append(week_revenue)
            monthly_labels.append(f'Week {4-i}')
        
        monthly_data.reverse()
        monthly_labels.reverse()
        
        yearly_data = []
        yearly_labels = []
        for i in range(12):
            month = today.month - i
            year = today.year
            if month <= 0:
                month += 12
                year -= 1
            
            month_start = date(year, month, 1)
            if month == 12:
                month_end = date(year, month, 31)
            else:
                month_end = date(year, month + 1, 1) - timedelta(days=1)
            
            month_exams = ExaminationModel.search([
                ('date', '>=', month_start),
                ('date', '<=', month_end)
            ])
            month_revenue = sum(exam.examination_price for exam in month_exams)
            yearly_data.append(month_revenue)
            yearly_labels.append(month_start.strftime('%b'))
        
        yearly_data.reverse()
        yearly_labels.reverse()
        
        AppointmentModel = self.env['ophthalmology.appointment']
        
        weekly_appointment_data = []
        weekly_labels = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_appointments = AppointmentModel.search_count([
                ('date', '>=', day.strftime('%Y-%m-%d 00:00:00')),
                ('date', '<=', day.strftime('%Y-%m-%d 23:59:59'))
            ])
            weekly_appointment_data.append(day_appointments)
            weekly_labels.append(day.strftime('%a'))
        
        monthly_appointment_data = []
        monthly_labels = []
        for i in range(4):
            week_start = today - timedelta(days=today.weekday() + (i * 7))
            week_end = week_start + timedelta(days=6)
            week_appointments = AppointmentModel.search_count([
                ('date', '>=', week_start.strftime('%Y-%m-%d 00:00:00')),
                ('date', '<=', week_end.strftime('%Y-%m-%d 23:59:59'))
            ])
            monthly_appointment_data.append(week_appointments)
            monthly_labels.append(f'Week {4-i}')
        
        monthly_appointment_data.reverse()
        monthly_labels.reverse()
        
        yearly_appointment_data = []
        yearly_labels = []
        for i in range(12):
            month = today.month - i
            year = today.year
            if month <= 0:
                month += 12
                year -= 1
            
            month_start = date(year, month, 1)
            if month == 12:
                month_end = date(year, month, 31)
            else:
                month_end = date(year, month + 1, 1) - timedelta(days=1)
            
            month_appointments = AppointmentModel.search_count([
                ('date', '>=', month_start.strftime('%Y-%m-%d 00:00:00')),
                ('date', '<=', month_end.strftime('%Y-%m-%d 23:59:59'))
            ])
            yearly_appointment_data.append(month_appointments)
            yearly_labels.append(month_start.strftime('%b'))
        
        yearly_appointment_data.reverse()
        yearly_labels.reverse()
        
        # Return all dashboard data
        return {
            'total_patients': total_patients,
            'new_patients': new_patients,
            'total_appointments': total_appointments,
            'missed_appointments': missed_appointments,
            'today_appointments': [{
                'id': appt.id,
                'patient_name': appt.patient_id.name,
                'time': fields.Datetime.from_string(appt.date).strftime('%H:%M'),
                'doctor_name': appt.doctor_name,
                'purpose': appt.purpose,
            } for appt in today_appointments],
            'upcoming_appointments': [{
                'id': appt.id,
                'patient_name': appt.patient_id.name,
                'date': fields.Datetime.from_string(appt.date).strftime('%Y-%m-%d'),
                'time': fields.Datetime.from_string(appt.date).strftime('%H:%M'),
                'purpose': appt.purpose,
            } for appt in upcoming_appointments],
            
            # Add financial data
            'total_revenue': total_revenue,
            'weekly_revenue': weekly_revenue,
            'monthly_revenue': monthly_revenue,
            'yearly_revenue': yearly_revenue,
            'average_examination_price': average_examination_price,
            
            # Add chart data
            'weekly_revenue_data': {
                'labels': weekly_labels,
                'values': weekly_data
            },
            'monthly_revenue_data': {
                'labels': monthly_labels,
                'values': monthly_data
            },
            'yearly_revenue_data': {
                'labels': yearly_labels,
                'values': yearly_data
            },
            
            # Add appointment chart data
            'weekly_appointment_data': {
                'labels': weekly_labels,
                'values': weekly_appointment_data
            },
            'monthly_appointment_data': {
                'labels': monthly_labels,
                'values': monthly_appointment_data
            },
            'yearly_appointment_data': {
                'labels': yearly_labels,
                'values': yearly_appointment_data
            }
        }

        
    badge_class = fields.Char(compute='_compute_badge_class')

    @api.depends('appointment_status')
    def _compute_badge_class(self):
        for rec in self:
            status = rec.appointment_status or ""
            mapping = {
                'Missed': 'badge-danger',
                'Today': 'badge-success',
                'Upcoming': 'badge-warning',
                'No Appointment': 'badge-secondary',
            }
            rec.badge_class = mapping.get(status, '')

    @api.model
    def create(self, vals):
        result = super(Patient, self).create(vals)
        
        if not result.patient_serial or result.patient_serial == 'New':
            serial = self.env['ir.sequence'].next_by_code('ophthalmology.patient.serial') or 'New'
            result.write({'patient_serial': serial})
        
        return result

        
