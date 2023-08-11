<template>
  <div class="fixed -bottom-0.5 w-full" :class="[(store.sidebarOpen && !store.isMobile) ? 'pl-44' : '']">
    <div class="relative">
      <div
        class="absolute left-1/2 z-10 transform -translate-x-1/2 -translate-y-1/2 gap-3 py-1 bg-neutral-100/90 border border-nearyblue-300 text-nearygray-200/80 shadow rounded-md">
        <ul class="flex items-center divide-x divide-nearygray-600/50">
          <li @click="toggleGrowMode()" class="px-2.5 py-0.5 hover:text-nearygray-100 cursor-pointer group relative">
            <template v-if="store.growMode">
              <Icon icon="heroicons:arrows-pointing-in-20-solid" class="w-[1.1rem] h-[1.1rem]" />
            </template>
            <template v-else>
              <Icon icon="heroicons:arrows-pointing-out-20-solid" class="w-[1.1rem] h-[1.1rem]" />
            </template>
          </li>
          <li @click="toggleArchivedMessages()"
            class="px-2.5 py-0.5 hover:text-nearygray-100 cursor-pointer group relative">
            <template v-if="store.selectedConversation && !store.selectedConversation.showArchivedMessages">
              <Icon icon="heroicons:eye-20-solid" class="w-[1.1rem] h-[1.1rem]" />
            </template>
            <template v-else>
              <Icon icon="heroicons:eye-slash-20-solid" class="w-[1.1rem] h-[1.1rem]" />
            </template>
          </li>
          <li v-if="store.conversationSettings.program && store.conversationSettings.program.value == 'DocumentChat'"
            @click="toggleDocuments()" class="px-2.5 py-0.5 hover:text-nearygray-100 cursor-pointer group relative">
            <Icon icon="heroicons:paper-clip-20-solid" class="w-[1.1rem] h-[1.1rem]" />
          </li>
          <li @click="toggleSettings()" class="px-2.5 py-0.5 hover:text-nearygray-100 cursor-pointer group relative">
            <Icon icon="heroicons:cog-6-tooth-20-solid" class="w-[1.1rem] h-[1.1rem]" />
          </li>
          <li class="flex items-center group relative">
            <Popover class="relative inline-block text-left">
              <PopoverButton
                class="flex items-center group relative cursor-pointer px-2 py-0.5 hover:text-nearygray-100 focus:border-transparent focus:ring-0 focus:outline-none">
                <Icon icon="heroicons-solid:dots-vertical" class="w-[1.1rem] h-[1.1rem]" />
              </PopoverButton>
              <Transition as="div" enter="transition ease-out duration-200" enterFrom="opacity-0 translate-y-1"
                enterTo="opacity-100 translate-y-0" leave="transition ease-in duration-150"
                leaveFrom="opacity-100 translate-y-0" leaveTo="opacity-0 translate-y-1">
                <PopoverPanel v-slot="{ close }"
                  class="absolute w-48 bottom-8 -right-0 origin-top-right border border-field-active  bg-field-default text-field-default-foreground rounded-md shadow ring-1 ring-black ring-opacity-10 focus:outline-none">
                  <ul class="divide-y divide-field-divide">
                    <li @click="toggleXRay(close)"
                      class="cursor-pointer flex rounded-t-md items-center gap-2 px-3 py-2 text-sm hover:bg-field-active hover:text-field-active-foreground">
                      <Icon icon="tabler:square-toggle" class="w-5 h-5" />
                      <div>Show X-Ray</div>
                    </li>
                    <li @click="archiveMessages(close)"
                      class="cursor-pointer flex rounded-t-md items-center gap-2 px-3 py-2 text-sm hover:bg-field-active hover:text-field-active-foreground">
                      <Icon icon="heroicons:archive-box-arrow-down-20-solid" class="w-5 h-5" />
                      <div>Archive Messages</div>
                    </li>
                    <li @click="deleteConversation(close)"
                      class="cursor-pointer flex rounded-b-md items-center gap-2 px-3 py-2 text-sm hover:bg-field-active hover:text-field-active-foreground">
                      <Icon icon="heroicons:x-mark-20-solid" class="w-5 h-5" />
                      <div>Delete Conversation</div>
                    </li>
                  </ul>
                </PopoverPanel>
              </Transition>
            </Popover>
          </li>
        </ul>
      </div>
      <div class="relative flex items-center bg-nearyblue-300">
        <textarea ref="chatBoxRef" v-model="currentMessage"
          @keydown.enter="!$event.shiftKey ? (sendMessage(), $event.preventDefault()) : ''" @input="resize"
          @focus="isFocused = true" @blur="isFocused = false" placeholder="What do you say?" spellcheck="false"
          class="bg-nearygray-200/5 resize-none rounded-lg mx-0 sm:mx-1 mb-0.5 sm:mb-1.5 w-full p-6 pt-7 text-slate-200 border border-nearyblue-300 shadow focus:border-nearygray-800/5 focus:ring-0 placeholder-slate-400/80"></textarea>
        <div @click="sendMessage()"
          class="absolute right-4 cursor-pointer text-slate-400 hover:text-slate-300 rounded-full h-9 w-9 flex items-center justify-center">
          <Icon icon="heroicons:paper-airplane-solid" class="w-5 h-5 ml-0.5" />
        </div>
      </div>
    </div>
    <!-- X-Ray! -->
    <div v-if="showXray"
      :class="[store.sidebarOpen && !store.isMobile ? 'left-44' : 'left-0', 'fixed top-12  right-0 bottom-28 flex items-center justify-center z-5']">
      <div class="bg-nearyblue-500/50 backdrop-blur-md w-full h-full rounded-lg relative p-12 overflow-y-scroll">
        <button @click="showXray = false" class="absolute top-4 right-4">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"
            class="text-nearygray-300 w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
        <template v-if="store.xray && store.xray.messages">
          <div class="text-nearygray-200 mb-2 w-4/5 leading-7 border-l-4 border-nearyblue-50 pl-4">Your last generation totaled <span class="font-bold">{{tokenSum}} tokens</span>. Here's the complete context passed to the model:</div>
          <ul role="list" class="divide-y divide-field-divide/50">
            <li v-for="(message, index) in store.xray.messages" :key="index" class="py-6">
              <div class="flex items-center justify-between pt-1">
                <span :class="{
                    'border-nearypink-300/50 bg-nearypink-300/20': message.role == 'assistant',
                    'border-nearycyan-300/50 bg-nearycyan-300/20': message.role == 'user',
                    'border-nearyblue-50 bg-nearyblue-50/50': message.role == 'system'
                  }"
                  class="border rounded-full px-2 py-[0.1rem] text-nearygray-100 text-xs tracking-wide">{{ message.role}}
                  </span>
                <span class="text-xs font-semibold text-nearygray-600">{{ index + 1 }} / {{ store.xray.messages.length }}</span>
              </div>
              <div class="text-sm text-nearygray-200 whitespace-pre-wrap [overflow-wrap:anywhere] leading-7 mt-4">
                {{ message.content }}
              </div>
            </li>
          </ul>
        </template>
        <div v-else class="text-nearygray-200 mb-2 w-4/5 leading-7 border-l-4 border-nearyblue-50 pl-4">Send a message, then check back here for the complete context sent to the chat model.</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, nextTick, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAppStore } from '@/store/index.js';
import { Icon } from '@iconify/vue';
import { Popover, PopoverButton, PopoverPanel } from '@headlessui/vue';
import { scrollToBottom } from '../services/scrollFunction.js';

const store = useAppStore();
const router = useRouter();
const route = useRoute();

const currentMessage = ref("");
const chatBoxRef = ref(null);
const isFocused = ref(false);
const showXray = ref(false);

const tokenSum = computed(() => {
  if (store.xray.messages) {
    return store.xray.messages.reduce((total, message) => total + message.tokens, 0);
  }
  return 0
});

const resize = () => {
  let element = chatBoxRef.value;
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
    chatBoxRef.value.blur();
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

  if (!('title' in conversation) || conversation.title == null || conversation.title == 'New conversation') {
    let title = message.content.slice(0, 50);
    let update = { 'conversation': [{ 'name': 'title', 'value': title }] };
    await store.updateConversationSettings(conversation.id, update);
  }

  if (store.ws.readyState === WebSocket.OPEN) {
    store.ws.send(JSON.stringify(message));
    await store.addMessage(message, conversation.id);
    currentMessage.value = "";
    await nextTick();
    resize();

    store.messageTimeout = setTimeout(() => {
      store.notification = { 'type': 'error', 'message': 'Connecting to server. Wait a moment and try again.' };
    }, 8000);

  } else {
    store.notification = { 'type': 'error', 'message': 'Connecting to server. Wait a moment and try again.'};
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
    await store.updateConversationSettings(store.selectedConversationId, { 'title': title });
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


const toggleArchivedMessages = () => {
  if (store.selectedConversation.showArchivedMessages) {
    store.selectedConversation.showArchivedMessages = false;
    store.notification = { 'message': 'Hiding archived messages' }
  }
  else {
    store.selectedConversation.showArchivedMessages = true;
    store.notification = { 'message': 'Showing archived messages' }
  }
}
const toggleGrowMode = () => {
  if (store.growMode) {
    store.growMode = false;
    store.notification = { 'message': 'Messages grow normally' }
  }
  else {
    store.growMode = true;
    store.notification = { 'message': 'Messages have room to grow' }
  }
}

const toggleSettings = () => {
  if (route.path.startsWith('/settings')) {
    router.push('/');
  } else {
    router.push(`/settings/${store.selectedConversationId}`);
  }
}

const toggleDocuments = () => {
  if (router.currentRoute.value.path.startsWith('/documents')) {
    router.go(-1);
  } else {
    router.push(`/documents/${store.selectedConversationId}`);
  }
};

const toggleXRay = async (close) => {
  showXray.value = !showXray.value
  close();
};

const archiveMessages = async (close) => {
  await store.archiveMessages(store.selectedConversationId);
  close();
  store.notification = { 'message': 'Messages archived' }
};

const deleteConversation = async (close = null) => {
  await store.deleteConversation(store.selectedConversationId);
  if (close) {
    close();
  }
};

const focusTextInput = async () => {
  await nextTick();
  if (chatBoxRef.value && !store.isMobile) {
    chatBoxRef.value.focus();
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

watch(() => store.growMode, async (newVal, oldVal) => {
  if (oldVal != newVal) {
    store.saveState();
  }
});

onMounted(() => {
  nextTick(() => {
    resize()
  })
})

onUnmounted(() => {
  store.textInputHeight = 0;
})

</script>

<style>
.v-enter-active,
.v-leave-active {
  transition: opacity 0.3s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}
</style>