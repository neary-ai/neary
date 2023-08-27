<template>
  <div class="h-full flex flex-col bg-nearyblue-300">
    <Sidebar />
    <NavBar />
    <main class="relative flex flex-col flex-grow" :class="[(store.sidebarOpen && !store.isMobile) ? 'ml-44' : 'ml-0']"
      :style="{ height: `calc(${windowHeight}px - ${store.textInputHeight}px)` }">
      <router-view></router-view>
      <ToolbarAlert />
    </main>
    <ChatBox v-if="inChatWindow" />
  </div>
</template>

<script setup>
import { onMounted, watch, ref, computed, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import { scrollToBottom } from '../services/scrollFunction.js';
import { useAppStore } from '@/store/index.js';
import Sidebar from '@/components/Sidebar.vue';
import NavBar from '@/components/NavBar.vue';
import ToolbarAlert from '@/components/common/ToolbarAlert.vue';
import ChatBox from '../components/ChatBox.vue';

const store = useAppStore();
const route = useRoute();

const bufferedMessages = ref([]);
const windowHeight = ref(window.innerHeight);
const inChatWindow = computed(() => {
  return route.path === '/'
});

const handleMessage = async (event) => {
  clearTimeout(store.messageTimeout);

  if (store.highlighting) {
    bufferedMessages.value.push(event);
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

  if (message.status == "incomplete" || message.status == "complete") {
    if (message.status == "incomplete") {
      store.messageTimeout = setTimeout(() => {
        store.notification = { 'type': 'alert', 'message': 'Waiting for response from chat server' };
      }, 10000);
      conversation.isLoading = true;
    }
    else {
      conversation.isLoading = false;
    }

    if (conversation.messages.length > 0) {
      let lastMessageId = conversation.messages[conversation.messages.length - 1]
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
  store.notification = { 'type': 'alert', 'message': message.content };
}

const getWebSocketUrl = () => {
  if (import.meta.env.VITE_API_BASE_URL === '') {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${wsProtocol}//${window.location.host}/ws`;
  }

  return import.meta.env.VITE_WS_URL;
}

const initWebSocket = async () => {
  if (!store.ws || store.ws.readyState === WebSocket.CLOSED) {
    const ws = new WebSocket(getWebSocketUrl());
    ws.onmessage = handleMessage;
    store.ws = ws;
    await reconnectWebSocket();
  }
};

const reconnectWebSocket = async () => {
  store.ws.onclose = async () => {
    await new Promise((resolve) => setTimeout(resolve, 2000));
    await initWebSocket();
  };
};

// Watchers
watch(route, async (to) => {
  await nextTick();
  if (to.path === '/') {
    scrollToBottom(store.highlighting, true);
  }
}, { immediate: true });


onMounted(async () => {
  await store.initialize();
  await initWebSocket();

  window.addEventListener('resize', () => {
    store.isMobile = (window.innerWidth <= 640);
    windowHeight.value = window.innerHeight;
  });
  document.addEventListener('mousedown', () => {
    store.highlighting = true;
  });
  document.addEventListener('mouseup', () => {
    store.highlighting = false;
    while (bufferedMessages.value.length > 0) {
      const bufferedEvent = bufferedMessages.value.shift();
      handleMessage(bufferedEvent);
    }
  });
  document.addEventListener('selectionchange', function (e) {
    var selected = window.getSelection().toString();
    if (selected.length < 1) {
      return;
    }
    navigator.clipboard.writeText(selected);
  });
});
</script>