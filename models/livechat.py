
from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class LivechatChannel(models.Model):
    _inherit = 'im_livechat.channel'
    
    @api.model
    def add_ophthalmology_users(self, channel_id):
        """Add all ophthalmology doctors and receptionists to the livechat channel"""
        channel = self.browse(channel_id)
        
        doctor_group = self.env.ref('ophthalmology.group_ophthalmology_doctor')
        receptionist_group = self.env.ref('ophthalmology.group_ophthalmology_receptionist')
        
        users = self.env['res.users'].search([
            '|',
            ('group_ids', 'in', doctor_group.id),
            ('group_ids', 'in', receptionist_group.id)
        ])
        
        for user in users:
            self.env['im_livechat.channel.user'].create({
                'channel_id': channel.id,
                'user_id': user.id,
            })
        
        return True
    
    @api.model
    def create_ophthalmology_internal_channel(self):
        """Create an internal channel for doctor-receptionist communication"""
        internal_channel = self.env.ref('ophthalmology.internal_communication_channel', False)
        
        if not internal_channel:
            internal_channel = self.create({
                'name': 'Ophthalmology Internal Communication',
                'button_text': 'Chat with Team',
                'default_message': 'Hello! How can I help you?',
                'channel_type': 'internal', 
            })
            
            self.add_ophthalmology_users(internal_channel.id)
            
            self.env['ir.model.data'].create({
                'name': 'internal_communication_channel',
                'module': 'ophthalmology',
                'model': 'im_livechat.channel',
                'res_id': internal_channel.id,
            })
        
        return internal_channel.id
    
    @api.model
    def get_mail_channel(self, livechat_channel_id):
        """Get or create a mail.channel for the internal communication"""
        try:
            current_user = self.env.user
            _logger.info(f"Current user: {current_user.name} (ID: {current_user.id})")
            
            doctor_group = self.env.ref('ophthalmology.group_ophthalmology_doctor')
            receptionist_group = self.env.ref('ophthalmology.group_ophthalmology_receptionist')
            
            if doctor_group.id in current_user.group_ids.ids:
                other_user = self.env['res.users'].search([
                    ('group_ids', 'in', receptionist_group.id),
                    ('id', '!=', current_user.id)
                ], limit=1)
                _logger.info(f"Found receptionist: {other_user.name if other_user else 'None'}")
            else:
                other_user = self.env['res.users'].search([
                    ('group_ids', 'in', doctor_group.id),
                    ('id', '!=', current_user.id)
                ], limit=1)
                _logger.info(f"Found doctor: {other_user.name if other_user else 'None'}")
            
            if not other_user:
                _logger.warning("No other user found, using current user as fallback")
                other_user = current_user
            
            ChannelModel = 'discuss.channel'
            if not self.env.registry.get(ChannelModel):
                ChannelModel = 'mail.channel'
            
            _logger.info(f"Using channel model: {ChannelModel}")
            
            if ChannelModel == 'discuss.channel':
                domain = [
                    ('channel_type', '=', 'chat'),
                    ('channel_member_ids.partner_id', '=', current_user.partner_id.id),
                    ('channel_member_ids.partner_id', '=', other_user.partner_id.id),
                ]
                channel = self.env[ChannelModel].search(domain, limit=1)
                
                if channel:
                    _logger.info(f"Found existing channel: {channel.id}")
                else:
                    _logger.info("Creating new channel")
                    
                    try:
                        channel = self.env[ChannelModel].search([
                            ('channel_type', '=', 'group'),
                            ('name', '=', f"Ophthalmology: {current_user.name} and {other_user.name}")
                        ], limit=1)
                        
                        if not channel:
                            channel = self.env[ChannelModel].create({
                                'name': f"Ophthalmology: {current_user.name} and {other_user.name}",
                                'channel_type': 'group',
                            })
                            _logger.info(f"Created group channel: {channel.id}")
                        else:
                            _logger.info(f"Found existing group channel: {channel.id}")
                        
                        member1 = self.env['discuss.channel.member'].search([
                            ('channel_id', '=', channel.id),
                            ('partner_id', '=', current_user.partner_id.id)
                        ], limit=1)
                        
                        if not member1:
                            member1 = self.env['discuss.channel.member'].create({
                                'channel_id': channel.id,
                                'partner_id': current_user.partner_id.id,
                            })
                            _logger.info(f"Added member 1: {member1.id}")
                        else:
                            _logger.info(f"Member 1 already exists: {member1.id}")
                        
                        member2 = self.env['discuss.channel.member'].search([
                            ('channel_id', '=', channel.id),
                            ('partner_id', '=', other_user.partner_id.id)
                        ], limit=1)
                        
                        if not member2:
                            member2 = self.env['discuss.channel.member'].create({
                                'channel_id': channel.id,
                                'partner_id': other_user.partner_id.id,
                            })
                            _logger.info(f"Added member 2: {member2.id}")
                        else:
                            _logger.info(f"Member 2 already exists: {member2.id}")
                        
                        if not self.env['mail.message'].search([
                            ('model', '=', ChannelModel),
                            ('res_id', '=', channel.id)
                        ], limit=1):
                            msg = channel.message_post(
                                body=f"Welcome to the Ophthalmology internal communication channel!",
                                message_type='comment',
                                subtype_xmlid='mail.mt_comment'
                            )
                            _logger.info(f"Posted welcome message: {msg.id}")
                    except Exception as e:
                        _logger.error(f"Error creating channel: {e}", exc_info=True)
                        raise
            else:
                channel = self.env[ChannelModel].search([
                    ('channel_type', '=', 'chat'),
                    ('channel_partner_ids', 'in', current_user.partner_id.id),
                    ('channel_partner_ids', 'in', other_user.partner_id.id),
                ], limit=1)
                
                if channel:
                    _logger.info(f"Found existing channel: {channel.id}")
                else:
                    _logger.info("Creating new channel using channel_get")
                    channel_info = self.env[ChannelModel].channel_get(partners_to=(other_user.partner_id.id,))
                    channel = self.env[ChannelModel].browse(channel_info['id'])
                    _logger.info(f"Created channel: {channel.id}")
                    
                    msg = channel.message_post(
                        body=f"Welcome to the Ophthalmology internal communication channel!",
                        message_type='comment',
                        subtype_xmlid='mail.mt_comment'
                    )
                    _logger.info(f"Posted welcome message: {msg.id}")
            
            return channel.id
        except Exception as e:
            _logger.error(f"Error in get_mail_channel: {e}", exc_info=True)
            return -1

class LivechatChannelExtended(models.Model):
    _inherit = 'im_livechat.channel'
    
    channel_type = fields.Selection([
        ('internal', 'Internal')
    ], string='Channel Type', default='internal')
