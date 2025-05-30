from odoo import models, api, fields

class MailMessage(models.Model):
    _inherit = 'mail.message'
    
    @api.model
    def get_channel_messages(self, channel_id, limit=20):
        """Get the last messages from a channel"""
        channel_model = 'discuss.channel'
        if not self.env.registry.get(channel_model):
            channel_model = 'mail.channel'
            
        messages = self.search([
            ('model', '=', channel_model),
            ('res_id', '=', channel_id)
        ], order='date desc', limit=limit)
        
        return messages.sorted(key=lambda r: r.date).read(['id', 'body', 'author_id', 'date'])
    
    @api.model
    def get_new_channel_messages(self, channel_id, last_message_id):
        """Get new messages since the last message id"""
        channel_model = 'discuss.channel'
        if not self.env.registry.get(channel_model):
            channel_model = 'mail.channel'
            
        messages = self.search([
            ('model', '=', channel_model),
            ('res_id', '=', channel_id),
            ('id', '>', last_message_id)
        ], order='date asc')
        
        return messages.read(['id', 'body', 'author_id', 'date'])
    
    @api.model
    def post_message_to_channel(self, channel_id, body):
        """Post a message to a channel, handling model name differences in Odoo 18"""
        channel_model = 'discuss.channel'
        if not self.env.registry.get(channel_model):
            channel_model = 'mail.channel'
            
        channel = self.env[channel_model].browse(channel_id)
        message = channel.message_post(
            body=body,
            message_type='comment',
            subtype_xmlid='mail.mt_comment'
        )
        
        return message.id
