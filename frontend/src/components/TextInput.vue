<template>
  <div class="relative flex items-center bg-nearyblue-300">
    <textarea ref="textInputRef" v-model="currentMessage"
      @keydown.enter="!$event.shiftKey ? (sendMessage(), $event.preventDefault()) : ''" @input="resize"
      @focus="isFocused = true" @blur="isFocused = false" placeholder="What do you say?" spellcheck="false"
      :disabled="!store.isWebSocketActive && !initializing"
      :class="store.isWebSocketActive || initializing ? ' border-nearyblue-300' : 'border-2 border-nearypink-300/50'"
      class="border bg-nearygray-200/5 resize-none rounded-lg mx-0 sm:mx-1 mb-0.5 sm:mb-1.5 w-full p-6 pt-7 text-slate-200 shadow focus:border-nearygray-800/5 focus:ring-0 placeholder-slate-400/80"></textarea>
    <div @click="sendMessage()"
      class="absolute right-4 cursor-pointer text-slate-400 hover:text-slate-300 rounded-full h-9 w-9 flex items-center justify-center">
      <Icon icon="heroicons:paper-airplane-solid" class="w-5 h-5 ml-0.5" />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAppStore } from '@/store/index.js';
import { Icon } from '@iconify/vue';
import useWebSocket from '@/composables/websocket.js';
import { scrollToBottom } from '../services/scrollFunction.js';

const store = useAppStore();
const router = useRouter();
const route = useRoute();
const { sendMessageThroughWebSocket } = useWebSocket();

const currentMessage = ref("");
const textInputRef = ref(null);
const isFocused = ref(false);

const resize = () => {
  let element = textInputRef.value;
  let oldHeight = element.style.height;
  let newHeight = 0;
  let maxHeight;

  if (store.isMobile) {
    element.style.height = '104px';
    maxHeight = 150;
  }
  else {
    element.style.height = '104px';
    maxHeight = 174;
  }

  if (element.scrollHeight > maxHeight) {
    newHeight = maxHeight;
    element.style.overflowY = 'auto';
  } else {
    newHeight = element.scrollHeight + 2;
  }
  element.style.height = `${newHeight}px`;
  store.textInputHeight = newHeight;

  if (element.style.height !== oldHeight) {
    scrollToBottom(store.highlighting, true);
  }
}

const sendMessage = async () => {
  scrollToBottom(store.highlighting, true);

  if (store.isMobile) {
    textInputRef.value.blur();
  }

  if (currentMessage.value == "") {
    return;
  }

  if (currentMessage.value.startsWith('/')) {
    let result = await handleCommand(currentMessage.value.slice(1));
    if (result == true) {
      currentMessage.value = "";
      await nextTick();
      resize();
      return;
    }
  }

  store.notification = null;
  clearTimeout(store.messageTimeout);

  const message = {
    role: "user",
    content: currentMessage.value,
    conversation_id: store.selectedConversationId
  }

  const conversation = store.selectedConversation;

  if (!('title' in conversation) || conversation.title == null || conversation.title == 'New Conversation') {
    let title = message.content.slice(0, 50);
    store.selectedConversation.title = title
    await store.updateConversation(store.selectedConversation);
  }

  try {
    sendMessageThroughWebSocket(message);
    await store.addMessage(message, conversation.id);
    currentMessage.value = "";
    await nextTick();
    resize();

    store.messageTimeout = setTimeout(() => {
      store.newNotification('Waiting for response from chat server..');
    }, 8000);
  } catch (error) {
    store.newNotification('Connecting to server. Wait a moment and try again.');
  }
};

const handleCommand = async (input) => {
  const trimmedInput = input.trim();
  const [command, ...args] = trimmedInput.split(' ');
  const commandArgs = args.join(' ');

  if (command === 'new') {
    store.createConversation(store.selectedSpaceId);
    return true;
  }

  if (command === 'archive') {
    store.archiveMessages(store.selectedConversationId);
    return true;
  }

  if (command === 'delete') {
    deleteConversation();
    return true;
  }

  if (command === 'title') {
    const title = commandArgs;
    store.selectedConversation.title = title;
    await store.updateConversation(store.selectedConversation);
    return true;
  }

  if (command === 'settings') {
    toggleSettings();
    return true;
  }

  else {
    return false;
  }
};

const toggleSettings = () => {
  if (route.path.startsWith('/settings')) {
    router.push('/');
  } else {
    router.push(`/settings/${store.selectedConversationId}`);
  }
}

const deleteConversation = async (close = null) => {
  await store.deleteConversation(store.selectedConversationId);
  if (close) {
    close();
  }
};

const focusTextInput = async () => {
  await nextTick();
  if (textInputRef.value && !store.isMobile) {
    textInputRef.value.focus();
  }
};

watch(currentMessage, (newMessage) => {
  store.currentMessage = newMessage;
});

watch(() => store.selectedConversationId, async () => {
  if (store.selectedConversation) {
    store.selectedConversation.unreadMessages = false;
    focusTextInput();
  }
});

let initializing = ref(true);

onMounted(() => {
  nextTick(() => {
    resize();
  })
  setTimeout(() => {
    initializing.value = false;
  }, 2000); // delay of 2 seconds
})

onUnmounted(() => {
  store.textInputHeight = 0;
})

</script>