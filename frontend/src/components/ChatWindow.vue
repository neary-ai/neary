<template>
  <div ref="chatWindow" id="chat-window" v-touch:swipe="swipeToConversation" class="flex flex-col overflow-y-auto">
    <div class="pt-12 bg-nearyblue-300"></div>
    <div v-if="!emptyState" class="flex flex-col items-start divide-y divide-neutral-500/60 px-0">
      <div v-if="showArchivedMessages" class="divide-y divide-neutral-500/60">
        <component :is="selectMessageComponent(message)" :chatWindowHeight="chatWindowHeight"
          v-for="(message, index) in archivedMessages" :key="'archived-' + index" :message="message" />
        <div class="relative py-4">
          <div class="absolute inset-0 flex items-center" aria-hidden="true">
          </div>
          <div class="relative">
            <div class="absolute inset-0 flex items-center" aria-hidden="true">
              <div class="w-full border-t border-slate-500" />
            </div>
            <div class="relative flex justify-center bg-gray-400">
              <span class="bg-nearyblue-300 px-2 py-2 text-sm text-slate-400">Archived messages</span>
            </div>
          </div>
        </div>
      </div>
      <component :is="selectMessageComponent(message)" :chatWindowHeight="chatWindowHeight"
        v-for="(message, index) in nonArchivedMessages" :key="'non-archived-' + index" :message="message" />
    </div>
    <EmptyState v-if="emptyState && (store.currentMessage == '')" />
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted, onUnmounted } from "vue";
import { useAppStore } from "@/store/index.js";
import ChatMessageUser from "./ChatMessageUser.vue";
import ChatMessageAssistant from "./ChatMessageAssistant.vue";
import ChatMessageNotification from "./ChatMessageNotification.vue";
import EmptyState from "./EmptyState.vue";
import { scrollToBottom } from '../services/scrollFunction.js';

const store = useAppStore();

const chatWindow = ref(null);
const chatWindowHeight = ref(0);

const swipeToConversation = (event) => {
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini|Mobi/i.test(navigator.userAgent);

  if (isMobile) {
    let direction = event;
    const conversations = store.selectedSpace.conversations;
    const currentIndex = conversations.findIndex(id => id === store.selectedConversationId);

    if (direction === 'left' && currentIndex > 0) {
      store.loadConversation(conversations[currentIndex - 1]);
    } else if (direction === 'right' && currentIndex < conversations.length - 1) {
      store.loadConversation(conversations[currentIndex + 1]);
    }
  }
}

const showArchivedMessages = computed(() => {
  if (store.selectedConversation) {
    return store.selectedConversation.showArchivedMessages;
  }
})

const messages = computed(() => {
  if (store.selectedConversation && Object.keys(store.messages).length > 0) {
    return store.selectedConversation.messages.map(id => {
      const message = store.messages[id];
      return message;
    });
  }
  return [];
});

const archivedMessages = computed(() => {
  if (store.selectedConversation) {
    return messages.value.filter(message => message.is_archived)
  }
  return [];
});

const nonArchivedMessages = computed(() => {
  if (store.selectedConversation) {
    return messages.value.filter(message => !message.is_archived)
  }
  return [];
});

const selectMessageComponent = (message) => {
  switch (message.role) {
    case 'user':
      return ChatMessageUser;
    case 'assistant':
      return ChatMessageAssistant;
    case 'notification':
      return ChatMessageNotification;
    default:
      return null;
  }
};


const emptyState = computed(() => {
  return !store.messagesLoading && (showArchivedMessages.value && messages.value.length == 0) | (!showArchivedMessages.value && nonArchivedMessages.value.length == 0)
})

const updateHeight = () => {
  if (chatWindow.value) {
    chatWindowHeight.value = chatWindow.value.clientHeight;
  }
};

watch(nonArchivedMessages, () => {
  scrollToBottom(store.highlighting);
})

watch(() => store.selectedConversation?.showArchivedMessages, (newValue) => {
  if (newValue !== undefined) {
    scrollToBottom(store.highlighting, true);
  }
})

onMounted(() => {
  window.addEventListener('resize', updateHeight);
  setTimeout(updateHeight, 1000);
});

onUnmounted(() => {
  window.removeEventListener('resize', updateHeight);
});

</script>

<style>
.tab {
  padding: 1em;
  border: 1px solid #ddd;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
}
</style>