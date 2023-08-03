import axios from 'axios';
import router from '../router.js';

function getApiBaseUrl() {
    if (import.meta.env.VITE_USE_DYNAMIC_BACKEND === 'true') {
        const currentDomain = window.location.hostname;
        const backendSubdomain = 'backend';
        return `https://${backendSubdomain}.${currentDomain}`;
    }
    return import.meta.env.VITE_API_BASE_URL;
}

const apiBaseUrl = getApiBaseUrl();

axios.interceptors.response.use(null, function (error) {
    if (error.response && error.response.status === 401) {
        if (error.response.data.message == "initial_start") {
            router.push('/welcome');
        }
        else {
            router.push('/login');
        }
    }
    return Promise.reject(error.response);
});

const api = {
    // Auth calls
    async registerUser(user) {
        try {
            const response = await axios.post(`${apiBaseUrl}/auth/register`, user, { withCredentials: true });
            return response;
        }
        catch (error) {
            throw error;
        }
    },
    async loginUser(email, password) {
        const response = await axios.post(`${apiBaseUrl}/auth/token`, new URLSearchParams({ email, password }), {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            withCredentials: true,
        });

        return response;
    },
    async logoutUser() {
        try {
            const response = await axios.get(`${apiBaseUrl}/auth/logout`, { withCredentials: true });
            return response.data
        } catch (error) {
            console.error('Error logging out:', error);
        }
    },
    async changeUserPassword(newPassword) {
        try {
            const response = await axios.post(
                `${apiBaseUrl}/auth/password`,
                { new_password: newPassword },
                { withCredentials: true }
            );
            return response;
        } catch (error) {
            throw(error);
        }
    },
    async saveApiKey(newApiKey) {
        try {
            const response = await axios.post(
                `${apiBaseUrl}/auth/apikey`,
                { api_key: newApiKey },
                { withCredentials: true }
            );
            return response;
        } catch (error) {
            throw(error);
        }
    },
    // General calls
    async getInitialData() {
        try {
            const response = await axios.get(`${apiBaseUrl}/api/initialize`, { withCredentials: true });
            return response.data;
        } catch (error) {
            throw error;
        }
    },
    async getSpaces() {
        try {
            const response = await axios.get(`${apiBaseUrl}/api/spaces`, { withCredentials: true });
            return response.data;
        } catch (error) {
            throw error;
        }
    },
    async getConversations(spaceId) {
        try {
            const response = await axios.get(`${apiBaseUrl}/api/spaces/${spaceId}/conversations`, { withCredentials: true });
            return response.data;
        } catch (error) {
            console.error('Error getting spaces:', error);
        }
    },
    async getMessages(conversationId, archived) {
        try {
            const response = await axios.get(`${apiBaseUrl}/api/conversations/${conversationId}/messages`, { withCredentials: true, params: { archived: archived } });
            return response.data.messages;
        } catch (error) {
            console.error('Error getting messages:', error);
        }
    },
    async archiveMessages(conversationId) {
        try {
            const response = await axios.post(`${apiBaseUrl}/api/conversations/${conversationId}/messages/archive`, {}, { withCredentials: true });
            return response.data;
        } catch (error) {
            console.error('Error archiving messages:', error);
        }
    },
    async createSpace(spaceData) {
        try {
            const response = await axios.post(`${apiBaseUrl}/api/spaces`, spaceData, { withCredentials: true });
            return response.data;
        } catch (error) {
            throw (error);
        }
    },
    async updateSpace(spaceId, spaceData) {
        try {
            const response = await axios.put(`${apiBaseUrl}/api/spaces/${spaceId}`, spaceData, { withCredentials: true });
            return response.data;
        } catch (error) {
            throw (error);
        }
    },
    async deleteSpace(spaceId) {
        try {
            const response = await axios.patch(`${apiBaseUrl}/api/spaces/${spaceId}`, {}, { withCredentials: true });
            return response;
        } catch (error) {
            throw (error);
        }
    },
    async createConversation(spaceId) {
        try {
            const url = spaceId ? `${apiBaseUrl}/api/spaces/${spaceId}/conversations` : `${apiBaseUrl}/api/conversations`;
            const response = await axios.post(url, {}, { withCredentials: true });
            return response.data;
        } catch (error) {
            console.error('Error creating conversation:', error);
        }
    },
    async deleteConversation(conversationId) {
        try {
            const response = await axios.patch(`${apiBaseUrl}/api/conversations/${conversationId}`, {}, { withCredentials: true });
            return response.data;
        } catch (error) {
            console.error('Error deleting conversation:', error);
        }
    },
    async archiveMessage(messageId) {
        try {
            const response = await axios.patch(`${apiBaseUrl}/api/messages/${messageId}`, {}, { withCredentials: true });
            return response.data;
        } catch (error) {
            console.error('Error archiving message:', error);
        }
    },
    async getConversationSettings(conversationId) {
        const response = await axios.get(`${apiBaseUrl}/api/conversations/${conversationId}/settings`, { withCredentials: true });
        return response.data;
    },
    async saveConversationSettings(conversationId, settings) {
        const response = await axios.put(
            `${apiBaseUrl}/api/conversations/${conversationId}/settings`,
            settings,
            { withCredentials: true }
        );
        return response;
    },
    // State calls
    async getState() {
        try {
            const response = await axios.get(`${apiBaseUrl}/api/state`, { withCredentials: true });
            return response.data;
        } catch (error) {
            console.error('Error getting state:', error);
        }
    },
    async saveState(stateData) {
        try {
            const response = axios.post(`${apiBaseUrl}/api/state`, stateData, { withCredentials: true });
            return response.data;
        } catch (error) {
            console.error('Error saving state:', error);
        }
    },
    // Documents
    async getDocuments(conversationId) {
        try {
            const response = await axios.get(`${apiBaseUrl}/api/conversations/${conversationId}/documents`, { withCredentials: true });
            return response.data
        } catch (error) {
            console.error("Error fetching documents:", error);
        }
    },
    async createDocumentFromURL(conversationId, url) {
        try {
            const response = await axios.post( `${apiBaseUrl}/api/conversations/${conversationId}/documents/add_url`, url, { withCredentials: true });
            return response.data;
        } catch (error) {
            console.error("Error creating document from URL:", error);
        }
    },
    async createDocumentFromFile(conversationId, file) {
        try {
            const formData = new FormData();
            formData.append("file", file);
            const response = await axios.post(
                `${apiBaseUrl}/api/conversations/${conversationId}/documents/add_file`,
                formData,
                {
                    withCredentials: true,
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                }
            );
            return response.data;
        } catch (error) {
            console.error("Error creating document from file:", error);
            throw error;
        }
    },
    async deleteDocument(docKey) {
        try {
            const response = await axios.delete(`${apiBaseUrl}/api/documents/${docKey}`, { withCredentials: true });
            return response.data;
        } catch (error) {
            console.error("Error deleting document:", error);
        }
    },
    async addDocumentToConversation(docKey, conversationId) {
        try {
            const response = await axios.patch(`${apiBaseUrl}/api/documents/${docKey}/conversations/${conversationId}`, "add", { withCredentials: true });
            return response.data;
        } catch (error) {
            console.error("Error creating documents:", error);
        }
    },
    async removeDocumentFromConversation(docKey, conversationId) {
        try {
            const response = await axios.patch(`${apiBaseUrl}/api/documents/${docKey}/conversations/${conversationId}`, "remove", { withCredentials: true });
            return response.data;
        } catch (error) {
            console.error("Error creating documents:", error);
        }
    },
    // Misc. calls
   async postActionResponse(action, messageId) {
        const response = await axios.post(
            `${apiBaseUrl}/api/action/response`,
            {
                name: action.name,
                conversation_id: action.conversation_id,
                data: action.data,
                message_id: messageId
            },
            { withCredentials: true }
        );
        return response;
    },
    async exportConversation(conversationId, exportFormat = "txt") {
        try {
            const response = await axios.get(`${apiBaseUrl}/api/conversations/${conversationId}/export`, {
                params: { export_format: exportFormat },
                responseType: "blob",
                withCredentials: true,
            });
            return response.data;
        } catch (error) {
            console.error("Error exporting conversation:", error);
        }
    },
}

export default api;