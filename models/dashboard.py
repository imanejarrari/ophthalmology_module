from odoo import models, fields

class OphthalmologyDashboard(models.Model):
    _name = 'ophthalmology.dashboard'
    _description = 'Ophthalmology Dashboard'

    name = fields.Char(string="Dashboard Title")
