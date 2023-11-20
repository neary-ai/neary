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
import { useAppStore } from '@/store/index.js';
import useWebSocket from '@/composables/websocket.js';
import Sidebar from '@/components/Sidebar.vue';
import NavBar from '@/components/NavBar.vue';
import ToolbarAlert from '@/components/common/ToolbarAlert.vue';
import ChatBox from '../components/ChatBox.vue';

const store = useAppStore();
const route = useRoute();
const { initWebSocket, handleMessage } = useWebSocket();

const windowHeight = ref(window.innerHeight);

const inChatWindow = computed(() => {
  return route.path === '/'
});


// Watchers
watch(route, async (to) => {
  await nextTick();
  if (to.path === '/') {
    store.scrollChatWindow(true)
  }
}, { immediate: true });

watch(
  () => store.selectedConversation,
  (newVal, oldVal) => {
    if (newVal && oldVal && newVal.id === oldVal.id) {
      newVal.message_ids.forEach((newId, index) => {
        let oldId = oldVal.message_ids[index];
        if ((typeof oldId === 'string' || oldId === null) && typeof newId === 'number') {
          // Update temporary message ID with permanent ID
          store.messages[newId] = store.messages[oldId];
          delete store.messages[oldId];
        }
      });
    }
  },
  { deep: true }
);

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
    while (store.bufferedMessages.length > 0) {
      const bufferedEvent = store.bufferedMessages.shift();
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