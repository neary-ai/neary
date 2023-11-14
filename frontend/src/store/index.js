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
        isWebSocketActive: false,
        availablePresets: null,
        availablePlugins: null,
        integrations: null,
        bufferedMessages: [],
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
        },
        conversationPreset: (state) => (conversation) => {
            return state.availablePresets.find(preset => preset.id === conversation.preset_id);
        },
        getEnabledFunctions: (state) => (functionType) => {
            let functions = [];
            state.selectedConversation.plugins.forEach(plugin_instance => {
                if (plugin_instance.plugin.is_enabled) {
                    plugin_instance.function_instances.forEach(func => {
                        let function_info = func.function
                        if (function_info.type === functionType) {
                            functions.push({
                                name: function_info.name,
                                display_name: function_info.display_name,
                                description: function_info.description,
                                plugin_icon: plugin_instance.plugin.icon,
                                plugin_id: plugin_instance.plugin_id,
                                plugin_instance_id: plugin_instance.id,
                                function_id: function_info.id,
                                function_instance_id: func.id

                            });
                        }
                    });
                }
            });
            return functions;
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
                if ((!error || error.data.message != "initial_start") && (error && error.status != 401)) {
                    this.newNotification("Can't connect to server", true)
                }
                return
            }

            // Set spaces
            for (let space of initial_data.spaces) {
                this.spaces[space.id] = space;
            }

            // Append 'None' space option
            this.spaces[-1] = { 'id': -1, 'name': 'None', 'description': null, 'conversation_ids': [] }

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

            // Set presets
            this.availablePresets = initial_data.presets;

            // Set plugins
            this.availablePlugins = initial_data.plugins;

            // Set integrations
            this.integrations = initial_data.integrations;

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
                isLoading: false,
                unreadMessages: false,
                showArchivedMessages: false,
            };
        },
        async addProfileField(field) {
            this.userProfile = { ...this.userProfile, ...field };
            await this.updateUserProfile();
        },
        async updateUserProfile() {
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
        async getMessages(conversationId) {
            let conversation = this.conversations[conversationId]
            if (conversation.message_ids && conversation.message_ids.length > 0
                && this.messages[conversation.message_ids[0]]) {
                return;
            }
            this.messagesLoading = true;
            const messagesData = await api.getMessages(conversationId, conversation.showArchivedMessages);

            messagesData.sort((a, b) => a.id - b.id);
            for (let message of messagesData) {
                this.messages[message.id] = message;
                if (!this.conversations[conversationId].message_ids.includes(message.id)) {
                    this.conversations[conversationId].message_ids.push(message.id);
                }
            }
            this.messagesLoading = false;
        },
        async getConversations() {
            let conversations = await api.getConversations()
            for (let conversation of conversations) {
                this.conversations[conversation.id] = this.initConversation(conversation);
            }
        },
        async loadSpace(spaceId) {
            this.selectedSpaceId = spaceId;
            await this.saveState();
            router.push('/conversations');
        },
        async archiveMessages(conversationId) {
            await api.archiveMessages(conversationId)
            const conversation = this.conversations[conversationId]
            conversation.message_ids.forEach((id) => {
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
            let spaceData = { "name": spaceName }
            await api.updateSpace(spaceId, spaceData);
        },
        async deleteSpace(spaceId) {
            try {
                await api.deleteSpace(spaceId);
                this.selectedSpaceId = null;

                for (let id in this.conversations) {
                    if (this.conversations[id].space_id === spaceId) {
                        this.conversations[id].space_id = -1;
                    }
                }

                delete this.spaces[spaceId];
                this.newNotification("Space deleted")
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

            if (type == 'tool_start') {
                // stay visible until cleared
            }
            else if (!sticky) {
                if (type == 'tool_success' || type == 'tool_error') {
                    setTimeout(() => this.notification = null, 2000);
                }
                else {
                    setTimeout(() => this.notification = null, 3000);
                }

            }
        },
        // Conversations
        async createConversation(spaceId) {
            const newConversation = await api.createConversation(spaceId);
            this.conversations[newConversation.id] = this.initConversation(newConversation);
            if (spaceId) {
                this.spaces[spaceId].conversation_ids.push(newConversation.id);
            }
            this.loadConversation(newConversation.id);
        },
        async deleteConversation(conversationId) {
            await api.deleteConversation(conversationId);

            const conversationSpace = this.conversations[conversationId].space_id

            if (conversationSpace && conversationSpace > -1) {
                const index = this.spaces[conversationSpace].conversation_ids.indexOf(conversationId);

                if (index !== -1) {
                    this.spaces[conversationSpace].conversation_ids.splice(index, 1);
                }
            }

            this.closeTab(conversationId);
            delete this.conversations[conversationId];

            await this.saveState();
            router.push('/conversations');
            this.newNotification("Conversation deleted")
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
        async updateConversationPreset(conversation, preset) {
            try {
                let response = await api.updateConversationPreset(conversation, preset);
                this.conversations[conversation.id] = this.initConversation(response.data);
            }
            catch (error) {
                console.log(error);
            }
        },
        async updateConversationSpace(conversation) {
            for (let spaceId in this.spaces) {
                console.log(this.spaces[spaceId]);
                let index = this.spaces[spaceId].conversation_ids.indexOf(conversation.id);

                if (index != -1 && spaceId != conversation.space_id) {
                    this.spaces[spaceId].conversation_ids.splice(index, 1);
                }
            }

            if (conversation.space_id && conversation.space_id !== -1) {
                if (!this.spaces[conversation.space_id].conversation_ids.includes(conversation.id)) {
                    this.spaces[conversation.space_id].conversation_ids.push(conversation.id);
                }
            }
        },
        async addConversationFunction(functionData, conversationId) {
            try {
                let response = await api.addConversationFunction(functionData, conversationId)
                this.conversations[conversationId] = this.initConversation(response.data);
            }
            catch (error) {
                console.log(error);
            }
        },
        async removeConversationFunction(functionData, conversationId) {
            try {
                let response = await api.removeConversationFunction(functionData, conversationId)
                let updatedConvo = this.initConversation(response.data)
                this.conversations[conversationId] = updatedConvo;
            }
            catch (error) {
                console.log(error);
            }
        },
        async updateConversationPlugin(conversation, plugin) {

        },
        // Messages
        addMessage(message, conversationId) {
            if (!message.id) {
                message.tempId = uuidv4();
                message.id = message.tempId;
            }
            this.messages[message.id] = message;
            this.conversations[conversationId].message_ids.push(message.id);
            this.conversations[conversationId].excerpt = message.content
        },
        removeMessage(messageId, conversationId) {
            delete this.messages[messageId];
            const index = this.conversations[conversationId].message_ids.indexOf(messageId);
            if (index !== -1) {
                this.conversations[conversationId].message_ids.splice(index, 1);
            }
        },
        updateLastMessage(message, messageId) {
            message.id = messageId
            this.messages[messageId] = message
            this.conversations[message.conversation_id].excerpt = message.content
        },
        // Plugins
        async enablePlugin(pluginId) {
            try {
                await api.enablePlugin(pluginId);
                let plugin = this.availablePlugins.find(plugin => plugin.id === pluginId)
                if (plugin) {
                    plugin.is_enabled = true;
                    let instance = this.selectedConversation.plugins.find(plugin => plugin.plugin_id === pluginId)
                    if (instance) {
                        instance.is_enabled = true;
                    }
                }
            }
            catch (e) {
                console.log('Error enabling plugin: ', e)
            }
        },
        async disablePlugin(pluginId) {
            try {
                await api.disablePlugin(pluginId);
                let plugin = this.availablePlugins.find(plugin => plugin.id === pluginId)
                if (plugin) {
                    plugin.is_enabled = false;

                    let instance = this.selectedConversation.plugins.find(plugin => plugin.plugin_id === pluginId)
                    if (instance) {
                        instance.is_enabled = false;
                    }
                }
            }
            catch (e) {
                console.log('Error disabling plugin: ', e)
            }
        },
        async getAvailablePresets() {
            this.availablePresets = await api.getAvailablePresets();
        },
        async deletePreset(preset) {
            await api.deletePreset(preset);
            this.getAvailablePresets();
            this.getConversations();

        }
    },
});