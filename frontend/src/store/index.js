import { v4 as uuidv4 } from 'uuid';
import { defineStore, storeToRefs } from 'pinia';
import api from '../services/apiService'
import { scrollToBottom } from '../services/scrollFunction.js';
import router from '../router';

export const useAppStore = defineStore('appstore', {
    state: () => ({
        ws: null,
        spaces: {},
        conversations: {},
        messages: {},
        selectedSpaceId: null,
        selectedConversationId: null,
        conversationSettings: {},
        programSettings: {},
        settingsOptions: null,
        openTabs: [],
        isMobile: window.innerWidth <= 640,
        sidebarOpen: window.innerWidth <= 640 ? false : true,
        contentWindowHeight: null,
        growMode: false,
        highlighting: false,
        notification: null,
        toolbarAlert: null,
        messageTimeout: null,
        conversationsLoading: false,
        messagesLoading: false,
        textInputHeight: 0,
        currentMessage: "",
        appState: {},
        userProfile: {},
        showXray: false,
        xray: {},
    }),
    getters: {
        selectedSpace(state) {
            return state.spaces[state.selectedSpaceId];
        },
        spacesOptions(state) {
            if (state.spaces) {
                let spaces = Object.values(state.spaces);
                let spaces_list = spaces.map(space => ({ 'value': space.id, 'option': space.name }));

                spaces_list.sort((a, b) => (a.value === -1 ? -1 : b.value === -1 ? 1 : 0));

                return spaces_list;
            } else {
                return [];
            }
        },
        selectedConversation(state) {
            return state.conversations[state.selectedConversationId];
        }
    },
    actions: {
        async initialize() {
            let initial_data;
            let initialSpaceId;
            let initialConversationId;

            try {
                initial_data = await api.getInitialData();
            } catch (error) {
                console.log(error)
                if ((!error || error.data.message != "initial_start") && (error.status != 401)) {
                    this.notification = { "type": "error", "message": "Can't connect to server", "sticky": true }
                }
                return
            }

            // Set spaces
            for (let space of initial_data.spaces) {
                this.spaces[space.id] = space;
            }

            // Append 'None' space option
            this.spaces[-1] = { 'id': -1, 'name': 'None', 'description': null, 'conversations': [] }

            // Set conversations
            for (let conversation of initial_data.conversations) {
                this.conversations[conversation.id] = this.initConversation(conversation);
            }

            // Set user profile
            this.userProfile = initial_data.user_profile;

            // Set app state
            if (initial_data.app_state) {
                let state = initial_data.app_state;
                initialSpaceId = state['selectedSpaceId'];
                initialConversationId = state['selectedConversationId'];
                this.openTabs = state['openTabs'];
                this.sidebarOpen = this.isMobile ? false : state['sidebarOpen'];
                this.growMode = state['growMode'];
            }
            else {
                initialSpaceId = null;
                initialConversationId = null;
            }

            // Load conversation or space if none
            if (initialConversationId) {
                this.selectedSpaceId = initialSpaceId;
                this.loadConversation(initialConversationId);
            }
            else if (Object.keys(this.conversations).length == 1 && this.conversations[1]) {
                this.selectedSpaceId = initialSpaceId;
                this.loadConversation(1);
            }
            else {
                this.selectedConversationId = initialConversationId;
                this.loadSpace(initialSpaceId);
            }
        },
        initConversation(conversation) {
            return {
                ...conversation,
                space_id: conversation.space_id === null ? -1 : conversation.space_id,
                // messages: [],
                isLoading: false,
                unreadMessages: false,
                showArchivedMessages: false,
            };
        },
        async addProfileField(field) {
            this.userProfile = { ...this.userProfile, ...field };
            await api.updateUserProfile(this.userProfile);
        },
        async reinitialize() {
            await this.initialize();
            await this.getMessages(this.selectedConversationId);
        },
        async loadConversation(conversationId, close) {
            if (close) {
                close();
            }
            if (!conversationId) {
                return
            }
            else if (conversationId == this.selectedConversationId) {
                router.push('/');
            }
            else {
                this.selectedConversationId = conversationId;
                await this.openTab(conversationId)
                await this.getMessages(conversationId);
                await this.saveState();
                router.push('/');
                await Promise.resolve();
                scrollToBottom(this.highlighting, true);
            }
        },
        async loadSpace(spaceId) {
            this.selectedSpaceId = spaceId;
            await this.saveState();
            router.push('/conversations');
        },
        async getMessages(conversationId, archived = true) {
            this.messagesLoading = true;
            const messagesData = await api.getMessages(conversationId, archived);
            messagesData.sort((a, b) => a.id - b.id);
            for (let message of messagesData) {
                this.messages[message.id] = message;
                if (!this.conversations[conversationId].messages.includes(message.id)) {
                    this.conversations[conversationId].messages.push(message.id);
                }
            }
            this.messagesLoading = false;
        },
        async archiveMessages(conversationId) {
            await api.archiveMessages(conversationId)
            const conversation = this.conversations[conversationId]
            conversation.messages.forEach((id) => {
                this.messages[id].is_archived = true;
            });
        },
        // App State
        async getState() {
            const stateData = await api.getState();
            this.appState = stateData;
            return stateData
        },
        async saveState() {
            let stateData = {}
            stateData = {
                'selectedSpaceId': this.selectedSpaceId,
                'selectedConversationId': this.selectedConversationId,
                'openTabs': this.openTabs,
                'sidebarOpen': this.sidebarOpen,
                'darkModeEnabled': this.darkModeEnabled,
                'growMode': this.growMode
            }
            await api.saveState(stateData);
        },
        // Tabs
        openTab(conversationId) {
            conversationId = Number(conversationId)
            if (!this.openTabs.includes(conversationId)) {
                this.openTabs.unshift(conversationId);
            }
        },
        closeTab(conversationId) {
            conversationId = Number(conversationId)
            const index = this.openTabs.indexOf(conversationId);
            if (index !== -1) {
                this.openTabs.splice(index, 1);
            }
            this.selectedConversationId = null;
            this.saveState();
            router.push('/conversations');
        },
        // Preferences
        toggleSidebar(action) {
            if (action && action == 'close') {
                this.sidebarOpen = false;
            }
            else if (action && action == 'open') {
                this.sidebarOpen = true;
            }
            else {
                this.sidebarOpen = !this.sidebarOpen
            }
            this.saveState();
        },
        // Spaces
        async createSpace() {
            const newSpace = await api.createSpace();
            this.spaces[newSpace.id] = newSpace;
        },
        async updateSpace(spaceId, spaceName) {
            const space = this.spaces[spaceId];
            space.name = spaceName;
            await api.updateSpace(spaceId, spaceName);
        },
        async deleteSpace(spaceId) {
            try {
                await api.deleteSpace(spaceId);
                this.selectedSpaceId = null;
                delete this.spaces[spaceId];
                this.notification = { "type": "success", "message": "Space deleted" }
            } catch (error) {
                console.error('Error archiving space:', error);
            }
        },
        newNotification(message, sticky = false, type = null) {
            this.notification = {
                "message": message,
                "sticky": sticky,
                "type": type
            }

            if (!sticky) {
                setTimeout(() => this.notification = null, 4000);
            }
        },
        // Conversations
        async createConversation(spaceId) {
            const newConversation = await api.createConversation(spaceId);
            this.conversations[newConversation.id] = this.initConversation(newConversation);
            if (spaceId) {
                this.spaces[spaceId].conversations.push(newConversation.id);
            }
            this.selectedConversationId = newConversation.id;
            this.openTab(newConversation.id);
            router.push('/');
        },
        async deleteConversation(conversationId) {
            await api.deleteConversation(conversationId);

            const conversationSpace = this.conversations[conversationId].space_id

            if (conversationSpace && conversationSpace > -1) {
                const index = this.spaces[conversationSpace].conversations.indexOf(conversationId);

                if (index !== -1) {
                    this.spaces[conversationSpace].conversations.splice(index, 1);
                }
            }

            this.closeTab(conversationId);
            delete this.conversations[conversationId];

            await this.saveState();
            router.push('/conversations');
            this.notification = { "type": "success", "message": "Conversation deleted" }
        },
        async updateConversation(conversation) {
            try {
                this.updateConversationSpace(conversation);
                let response = await api.updateConversation(conversation);
                this.conversations[conversation.id] = this.initConversation(response.data);
            }
            catch (error) {
                console.log(error);
            }
        },
        async updateConversationSpace(conversation) {
            for (let spaceId in this.spaces) {
                let index = this.spaces[spaceId].conversations.indexOf(conversation.id);

                if (index != -1 && spaceId != conversation.space_id) {
                    this.spaces[spaceId].conversations.splice(index, 1);
                }
            }

            if (conversation.space_id && conversation.space_id !== -1) {
                if (!this.spaces[conversation.space_id].conversations.includes(conversation.id)) {
                    this.spaces[conversation.space_id].conversations.push(conversation.id);
                }
            }
        },
        // Messages
        addMessage(message, conversationId) {
            if (!message.id) {
                message.tempId = uuidv4();
                message.id = message.tempId;
            }
            this.messages[message.id] = message;
            this.conversations[conversationId].messages.push(message.id);
        },
        removeMessage(messageId, conversationId) {
            delete this.messages[messageId];
            const index = this.conversations[conversationId].messages.indexOf(messageId);
            if (index !== -1) {
                this.conversations[conversationId].messages.splice(index, 1);
            }
        },
        updateLastMessage(message, messageId) {
            message.id = messageId
            this.messages[messageId] = message
        }
    },
});