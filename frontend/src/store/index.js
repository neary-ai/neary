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
        selectedConversation(state) {
            return state.conversations[state.selectedConversationId];
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
        }
    },
    actions: {
        // Initial Data
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

            // Append 'None' space option and set to -1 for UI
            this.spaces[-1] = {'id': -1, 'name': 'None', 'description': null, 'conversations': []}

            // Set conversations
            for (let conversation of initial_data.conversations) {
                this.conversations[conversation.id] = {
                    ...conversation,
                    space_id: conversation.space_id === null ? -1 : conversation.space_id,
                    messages: [],
                    isLoading: false,
                    unreadMessages: false,
                    showArchivedMessages: false,
                }
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

            // Load conversation, space, or welcome message
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
        async reinitialize() {
            await this.initialize();
            await this.getMessages(this.selectedConversationId);
        },
        showConversations() {
            router.push('/conversations');
        },
        showMessages() {
            router.push('/');
        },
        async getSpaces() {
            const spacesData = await api.getSpaces();
            for (let space of spacesData) {
                this.spaces[space.id] = space;
            }
        },
        async getConversationSettings(conversationId) {
            let settings = await api.getConversationSettings(conversationId);
            this.conversationSettings = settings.conversation
            this.programSettings = settings.program
            if (!this.conversationSettings.space.value) {
                this.conversationSettings.space.value = -1;
            }
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
                await this.getConversationSettings(conversationId);
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
        // Conversation settings
        async updateConversationSettings(conversationId, newSettings) {
            try {
                const conversation = this.conversations[conversationId];
                for (const setting in newSettings) {
                    if (setting == 'title') {
                        this.conversationSettings.title.value = newSettings['title']
                        conversation.title = newSettings['title']
                    }

                    if (setting == 'space') {
                        this.conversationSettings.space.value = newSettings['space']
                        if (this.selectedSpace) {
                            let index = this.selectedSpace.conversations.indexOf(conversationId);
                            if (index != -1) {
                                this.selectedSpace.conversations.splice(index, 1);
                            }
                        }
                        if (newSettings['space'] && newSettings['space'] !== -1) {
                            if (!this.spaces[newSettings['space']].conversations.includes(conversationId)) {
                                this.spaces[newSettings['space']].conversations.push(conversationId);
                            }
                        }
                    }                    

                    if (setting == 'program') {
                        this.conversationSettings.program.value = newSettings['program']
                        if (newSettings['program'] && newSettings['program'] !== 'DefaultProgram') {
                            let program_info = this.conversationSettings.program.options.find((object) => object.value == newSettings['program']);
                            conversation.program.name = newSettings['program'];
                            conversation.program.metadata.display_name = program_info.option;
                            conversation.program.metadata.icon = program_info.icon;
                        }
                    }
                }
                await api.saveConversationSettings(conversationId, {'conversation': this.conversationSettings});
            }
            catch (error) {
                console.log(error);
            }
        },
        async updateProgramSettings(conversationId, newSettings) {
            try {
                for (const setting in this.programSettings) {
                    if (newSettings.hasOwnProperty(setting)) {
                        this.programSettings[setting].value = newSettings[setting];
                    }
                }
                await api.saveConversationSettings(conversationId, {'program': this.programSettings});
            }
            catch (error) {
                console.log(error);
            }
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
            this.showConversations();
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
        async deleteSpace (spaceId) {
            try {
              await api.deleteSpace(spaceId);
              this.selectedSpaceId = null;
              delete this.spaces[spaceId];
              this.notification = { "type": "success", "message": "Space deleted" } 
            } catch (error) {
              console.error('Error archiving space:', error);
            }
        },
        // Conversations
        async createConversation(spaceId) {
            const newConversation = await api.createConversation(spaceId);
            this.conversations[newConversation.id] = {
                ...newConversation,
                space_id: newConversation.space_id === null ? -1 : newConversation.space_id,
                messages: [],
                isLoading: false,
                unreadMessages: false,
                showArchivedMessages: false,
            }
            if (spaceId) {
                this.spaces[spaceId].conversations.push(newConversation.id);
            }
            await this.getConversationSettings(newConversation.id);
            this.selectedConversationId = newConversation.id;
            this.openTab(newConversation.id);
            this.showMessages();
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
            this.showConversations();
            this.notification = { "type": "success", "message": "Conversation deleted" }            
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
        },
    },
});