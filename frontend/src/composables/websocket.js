import { useAppStore } from '@/store/index.js';

export default function useWebSocket() {
    const store = useAppStore();

    const getWebSocketUrl = () => {
        if (import.meta.env.VITE_API_BASE_URL === '') {
            const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            return `${wsProtocol}//${window.location.host}/ws`;
        }

        return import.meta.env.VITE_WS_URL;
    }

    const initWebSocket = async () => {
        if (!store.ws || store.ws.readyState === WebSocket.CLOSED) {
            try {
                const ws = new WebSocket(getWebSocketUrl());

                ws.onmessage = handleMessage;
                ws.onopen = () => store.isWebSocketActive = true;
                ws.onclose = async () => {
                    await new Promise((resolve) => setTimeout(resolve, 2000));
                    store.isWebSocketActive = false;
                    await initWebSocket();
                };
                ws.onerror = async (error) => {
                    await new Promise((resolve) => setTimeout(resolve, 2000));
                    store.isWebSocketActive = false;
                    await initWebSocket();
                };

                store.ws = ws;

            } catch (error) {
                console.error('Failed to create WebSocket:', error);
                store.isWebSocketActive = false;
                await new Promise((resolve) => setTimeout(resolve, 2000));
                await initWebSocket();
            }
        }
    };

    const handleMessage = async (event) => {
        clearTimeout(store.messageTimeout);

        if (store.highlighting) {
            store.bufferedMessages.push(event);
            return;
        }

        const message = JSON.parse(event.data);
        if (!message) {
            return;
        }

        if (message.xray) {
            store.xray = message.xray;
        }

        const conversation = store.conversations[message.conversation_id];

        if (message.role == 'command') {
            await handleCommand(message);
            return;
        }

        else if (message.role == 'alert') {
            await handleAlert(message);
            return
        }

        else if (message.role == 'status') {
            console.log("Received status message: ", message)
            await handleStatus(message);
            return
        }

        if (message.status == "incomplete" || message.status == "complete") {
            if (message.status == "incomplete") {
                store.messageTimeout = setTimeout(() => {
                    store.newNotification('Waiting for response from chat server');
                }, 10000);
                conversation.isLoading = true;
            }
            else {
                conversation.isLoading = false;
            }

            if (conversation.message_ids.length > 0) {
                let lastMessageId = conversation.message_ids[conversation.message_ids.length - 1]
                let lastMessage = store.messages[lastMessageId];

                if (lastMessage && lastMessage.role === 'assistant' && lastMessage.status == 'incomplete') {
                    store.updateLastMessage(message, lastMessageId);
                } else {
                    store.addMessage(message, message.conversation_id);
                }
            }
            return;
        }
        else {
            store.addMessage(message, message.conversation_id);
        }

        if (message.conversation_id != store.selectedConversationId) {
            conversation.unreadMessages = true;
        }
    };

    const handleCommand = async (message) => {
        if (message.content == 'reload') {
            await store.reinitialize();
        }
    }

    const handleAlert = async (message) => {
        store.newNotification(message.content, false, message.type);
    }

    const handleStatus = async (message) => {
        if (message.content.approval_response_processed) {
            store.removeMessage(message.content.approval_response_processed, message.conversation_id);
        }
        else if (message.content.tool_start) {
            store.newNotification(message.content.tool_start, false, 'tool_start');
        }
        else if (message.content.tool_success) {
            store.notification = null;
            store.newNotification(message.content.tool_success, false, 'tool_success');
        }
        else if (message.content.tool_error) {
            store.notification = null;
            store.newNotification(message.content.tool_error, false, 'tool_error');
        }
    }

    const sendMessageThroughWebSocket = (message) => {
        if (store.ws && store.ws.readyState === WebSocket.OPEN) {
            store.ws.send(JSON.stringify(message));
        } else {
            throw new Error('WebSocket is not open');
        }
    };

    return {
        initWebSocket,
        handleMessage,
        sendMessageThroughWebSocket
    }
}