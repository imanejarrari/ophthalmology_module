from odoo import models, api

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    @api.model
    def get_ophthalmology_user_info(self):
        """Get the current user's role in the ophthalmology module"""
        user = self.env.user
        
        doctor_group = self.env.ref('ophthalmology.group_ophthalmology_doctor')
        receptionist_group = self.env.ref('ophthalmology.group_ophthalmology_receptionist')
        
        role = 'unknown'
        if doctor_group.id in user.group_ids.ids:
            role = 'doctor'
        elif receptionist_group.id in user.group_ids.ids:
            role = 'receptionist'
            
        return {
            'role': role,
            'name': user.name
        }
    
    @api.model
    def get_ophthalmology_chat_partner(self):
        """Get the chat partner for the current user"""
        user = self.env.user
        
        doctor_group = self.env.ref('ophthalmology.group_ophthalmology_doctor')
        receptionist_group = self.env.ref('ophthalmology.group_ophthalmology_receptionist')
        
        if doctor_group.id in user.group_ids.ids:
            partner = self.search([
                ('group_ids', 'in', receptionist_group.id),
                ('id', '!=', user.id)
            ], limit=1)
        else:
            partner = self.search([
                ('group_ids', 'in', doctor_group.id),
                ('id', '!=', user.id)
            ], limit=1)
        
        return {
            'name': partner.name if partner else '',
            'id': partner.id if partner else 0
        }
