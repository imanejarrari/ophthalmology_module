/** @odoo-module **/

import { Component, useState, onWillStart, onMounted, useRef } from '@odoo/owl';
import { xml } from '@odoo/owl';
import { useService } from '@web/core/utils/hooks';
import { registry } from '@web/core/registry';
import { session } from '@web/session';

export class OphthalmologyInternalChat extends Component {
    setup() {
        try {
            this.orm = useService("orm");
            this.userId = session.uid;
        } catch (error) {
            console.error("Error loading services:", error);
            this.orm = {
                call: async () => {
                    console.warn("ORM service not available");
                    return [];
                }
            };
            this.userId = 0;
        }
        
        this.messagesRef = useRef("messages");
        
        this.inDashboard = false;
        
        this.state = useState({
            isLoading: true,
            channelId: null,
            userRole: null,
            messages: [],
            newMessage: "",
            chatPartner: "",
            chatPartnerName: "",
            chatOpen: false,
            serviceError: false
        });
        
        onWillStart(async () => {
            try {
                const userInfo = await this.orm.call(
                    'res.users',
                    'get_ophthalmology_user_info',
                    []
                );
                this.state.userRole = userInfo.role;
                this.state.chatPartner = this.state.userRole === 'doctor' ? 'Receptionist' : 'Doctor';
                
                const partnerInfo = await this.orm.call(
                    'res.users',
                    'get_ophthalmology_chat_partner',
                    []
                );
                this.state.chatPartnerName = partnerInfo.name || this.state.chatPartner;
                
                const channelId = await this.orm.call(
                    'im_livechat.channel',
                    'create_ophthalmology_internal_channel',
                    []
                );
                this.state.channelId = channelId;
                
                const mailChannelId = await this.orm.call(
                    'im_livechat.channel',
                    'get_mail_channel',
                    [channelId]
                );
                
                if (mailChannelId < 0) {
                    throw new Error("Failed to get mail channel");
                }
                
                this.state.mailChannelId = mailChannelId;
                this.state.isLoading = false;
            } catch (error) {
                console.error("Error initializing chat:", error);
                this.state.isLoading = false;
                this.state.serviceError = true;
            }
        });
        
        onMounted(() => {
            const dashboardElement = document.querySelector('.ophthalmology-dashboard');
            this.inDashboard = !!dashboardElement;
            
            if (this.inDashboard && !this.state.isLoading && !this.state.serviceError) {
                this.state.chatOpen = true;
                this.loadMessages().then(() => {
                    this.setupMessagePolling();
                    this.scrollToBottom();
                }).catch(error => {
                    console.error("Error loading messages:", error);
                    this.state.serviceError = true;
                });
            }
        });
    }
    
    async openChat() {
        if (this.state.serviceError) {
            alert("Chat service is currently unavailable. Please try again later.");
            return;
        }
        
        this.state.chatOpen = true;
        try {
            await this.loadMessages();
            this.setupMessagePolling();
            this.scrollToBottom();
        } catch (error) {
            console.error("Error opening chat:", error);
            this.state.serviceError = true;
            this.state.chatOpen = false;
            alert("Failed to open chat. Please try again later.");
        }
    }
    
    async loadMessages() {
        if (!this.state.mailChannelId || this.state.mailChannelId < 0) {
            this.state.serviceError = true;
            throw new Error("Invalid mail channel ID");
        }
        
        try {
            const messages = await this.orm.call(
                'mail.message',
                'get_channel_messages',
                [this.state.mailChannelId, 20]  
            );
            
            this.state.messages = messages.map(msg => ({
                id: msg.id,
                text: msg.body.replace(/<[^>]*>/g, ''),  
                sender: msg.author_id[0] === this.userId ? 'user' : 'partner',
                senderName: msg.author_id[1] || (msg.author_id[0] === this.userId ? 'You' : this.state.chatPartnerName),
                time: this.formatTime(msg.date),
                isNew: false
            }));
        } catch (error) {
            console.error("Failed to load messages:", error);
            this.state.serviceError = true;
            throw error;
        }
    }
    
    setupMessagePolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }
        
        this.pollingInterval = setInterval(async () => {
            if (this.state.messages.length > 0) {
                const lastMsgId = Math.max(...this.state.messages.map(m => m.id));
                await this.fetchNewMessages(lastMsgId);
            } else {
                await this.loadMessages();
            }
        }, 5000);
    }
    
    async fetchNewMessages(lastId) {
        if (!this.state.mailChannelId) return;
        
        try {
            const newMessages = await this.orm.call(
                'mail.message',
                'get_new_channel_messages',
                [this.state.mailChannelId, lastId]
            );
            
            if (newMessages.length > 0) {
                const formattedMessages = newMessages.map(msg => ({
                    id: msg.id,
                    text: msg.body.replace(/<[^>]*>/g, ''),  
                    sender: msg.author_id[0] === this.userId ? 'user' : 'partner',
                    senderName: msg.author_id[1] || (msg.author_id[0] === this.userId ? 'You' : this.state.chatPartnerName),
                    time: this.formatTime(msg.date),
                    isNew: true
                }));
                
                this.state.messages.push(...formattedMessages);
                this.scrollToBottom();
            }
        } catch (error) {
            console.error("Failed to fetch new messages:", error);
        }
    }
    
    formatTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }
    
    scrollToBottom() {
        if (this.messagesRef.el) {
            this.messagesRef.el.scrollTop = this.messagesRef.el.scrollHeight;
        }
    }
    
    updateNewMessage(event) {
        this.state.newMessage = event.target.value;
    }
    
    async sendMessage(event) {
        if (event.key === 'Enter' || event.type === 'click') {
            if (this.state.newMessage.trim() && this.state.mailChannelId) {
                // Optimistically add message to UI
                const tempId = Date.now();
                const messageTime = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                
                this.state.messages.push({
                    id: tempId,
                    text: this.state.newMessage,
                    sender: "user",
                    time: messageTime,
                    isNew: true,
                    pending: true
                });
                
                const messageContent = this.state.newMessage;
                this.state.newMessage = "";
                
                setTimeout(() => {
                    this.scrollToBottom();
                }, 100);
                
                try {
                    const result = await this.orm.call(
                        'mail.message',
                        'post_message_to_channel',
                        [this.state.mailChannelId, messageContent]
                    );
                    
                    const msgIndex = this.state.messages.findIndex(m => m.id === tempId);
                    if (msgIndex !== -1) {
                        this.state.messages[msgIndex].id = result;
                        this.state.messages[msgIndex].pending = false;
                    }
                } catch (error) {
                    console.error("Failed to send message:", error);
                    const msgIndex = this.state.messages.findIndex(m => m.id === tempId);
                    if (msgIndex !== -1) {
                        this.state.messages[msgIndex].failed = true;
                    }
                }
            }
            
            if (event.type === 'keydown') {
                event.preventDefault();
            }
        }
    }
    
    closeChat() {
        this.state.chatOpen = false;
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }
    }
    
    static template = xml/* xml */`
        <div class="o_livechat_widget">
            <div t-if="state.isLoading" class="text-center p-3">
                <i class="fa fa-spinner fa-spin"></i> Loading chat...
            </div>
            <div t-elif="state.serviceError" class="text-center p-3 text-danger">
                <i class="fa fa-exclamation-triangle"></i> Chat service unavailable
            </div>
            <div t-elif="!state.chatOpen" class="o_livechat_button">
                <button class="btn btn-primary" t-on-click="openChat">
                    <i class="fa fa-comments"></i> 
                    <t t-if="state.userRole === 'doctor'">Chat with Receptionist</t>
                    <t t-elif="state.userRole === 'receptionist'">Chat with Doctor</t>
                    <t t-else="">Open Internal Chat</t>
                </button>
            </div>
            <div t-else="" class="o_livechat_conversation">
                <!-- Chat header -->
                <div class="o_livechat_header">
                    <span class="o_livechat_title">
                        <t t-if="state.userRole === 'doctor'">Chat with Receptionist</t>
                        <t t-elif="state.userRole === 'receptionist'">Chat with Doctor</t>
                        <t t-else="">Internal Chat</t>
                    </span>
                    <button class="o_livechat_close" t-on-click="closeChat">×</button>
                </div>
                
                <!-- Chat body -->
                <div class="o_livechat_body" t-ref="messages">
                    <div t-if="state.messages.length === 0" class="o_livechat_no_message">
                        <i class="fa fa-comments-o"></i>
                        <p>No messages yet. Start the conversation!</p>
                    </div>
                    <div t-else="" class="o_livechat_welcome">
                        Welcome to the Ophthalmology internal communication channel!
                    </div>
                    <t t-foreach="state.messages" t-as="message" t-key="message.id">
                        <div t-attf-class="o_livechat_message {{message.sender === 'user' ? 'o_livechat_message_mine' : 'o_livechat_message_other'}}">
                            <div class="o_livechat_message_content">
                                <div class="o_livechat_message_author" t-esc="message.sender === 'user' ? 'You' : state.chatPartnerName"/>
                                <div class="o_livechat_message_body" t-esc="message.text"/>
                                <div class="o_livechat_message_date" t-esc="message.time"/>
                            </div>
                        </div>
                    </t>
                </div>
                
                <!-- Chat input -->
                <div class="o_livechat_footer">
                    <div class="o_composer_container">
                        <input type="text" 
                               class="o_composer_text_field" 
                               placeholder="Type a message..." 
                               t-att-value="state.newMessage"
                               t-on-input="updateNewMessage"
                               t-on-keydown="sendMessage"/>
                        <button class="o_composer_button_send" t-on-click="sendMessage">
                            <i class="fa fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Register the component in the registry
registry.category("components").add("OphthalmologyInternalChat", OphthalmologyInternalChat);
