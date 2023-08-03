<template>
  <div class="flex items-center justify-center w-full overflow-x-scroll no-scrollbar" :class="store.sidebarOpen ? 'ml-[3.5rem]' : 'ml-2'">
    <div v-show="arrowsVisible" class="flex items-center justify-center h-9 cursor-pointer text-nearygray-100 hover:text-white">
      <ChevronLeftIcon @click="switchTab('previous')" class="w-5 h-5" />
    </div>
    <div ref="tabContainerRef" class="flex flex-1 gap-2.5 justify-start items-center overflow-x-scroll no-scrollbar"
      :class="arrowsVisible ? 'mx-2' : 'mx-3'">
      <div v-for="element in openTabConversations" :key="element.id" :ref="el => (tabItemRefs[element.id] = el)" @click="store.loadConversation(element.id)" :class="element.id === store.selectedConversationId ? 'border-nearyyellow-200/90' : 'border-slate-400'" class="flex min-w-[8rem] max-w-[12rem] bg-nearyblue-300 shadow-lg cursor-pointer items-center rounded pb-1.5 pt-2 px-0.5 text-sm border-b-2 text-nearygray-50 font-semibold">
        <div class="flex items-center flex-shrink-0">
          <div v-if="element.isLoading" id="loading-indicator" class="mx-2">
            <img :src="loadingIcon" class="w-4 h-4">
          </div>
          <div v-else class="mx-2">
            <component :is="iconComponents[element.program.metadata.icon]"
              class="text-slate-400/80 h-[1.1rem] w-[1.1rem]" />
          </div>
          <div v-if="element.unreadMessages == true" class="flex items-center justify-center mr-2">
            <div class="h-2 w-2 rounded-full bg-ncyan"></div>
          </div>
        </div>
        <div class="flex-grow min-w-0 truncate text-clip">
          {{ element.title }}
        </div>
        <div @click.stop="closeTab(element.id);" class="flex-shrink-0 hover:text-slate-100 ml-1.5 mr-1.5">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
            <path
              d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
          </svg>
        </div>
      </div>
    </div>
    <div v-if="arrowsVisible"
      class="flex items-center justify-center h-8 cursor-pointer text-nearygray-100 hover:text-white">
      <ChevronRightIcon @click="switchTab('next')" class="w-5 h-5" />
    </div>
    <div @click="store.createConversation(store.selectedSpace ? store.selectedSpace.id : null)"
      class="cursor-pointer flex items-center justify-center text-nearygray-100 hover:text-white"
      :class="arrowsVisible ? 'ml-3' : 'ml-2'">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
        <path
          d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z" />
      </svg>
    </div>
  </div>
  <Popover class="hidden sm:flex relative items-center gap-2 text-sm font-semibold flex-shrink ml-6 mr-2">
    <PopoverButton class="flex items-center cursor-pointer focus:outline-none focus:ring-0">
      <ChevronDownIcon class="w-5 h-5 text-nearygray-100 hover:text-white" />
    </PopoverButton>
    <PopoverPanel
      v-slot="{ close }"
      class="absolute right-0 top-10 rounded-md border-field-active border bg-field-default text-field-default-foreground py-1 shadow-xl ring-1 ring-black ring-opacity-10 focus:outline-none w-96 z-20">
      <div class="px-5 pb-1 relative border-b border-field-divide">
        <MagnifyingGlassIcon class="pointer-events-none absolute left-3 top-2 h-5 w-5"
          aria-hidden="true" />
        <input type="text" v-model="query" placeholder="Search..."
          class="text-sm w-full px-6 py-2 border-0 bg-transparent focus:ring-0 placeholder:text-field-default-foreground/70">
      </div>
      <div class="overflow-y-auto max-h-80 scroll-py-2">
        <h2 v-if="filteredConversations.spaceConversations.length > 0"
          class="mb-2 mt-4 px-3 text-xs font-semibold">In {{ store.selectedSpace.name }}</h2>
        <ul class="divide-y divide-field-divide">
          <li v-for="conversation in filteredConversations.spaceConversations" :key="conversation.id"
            class="group flex cursor-pointer select-none items-center pl-2 pr-4 py-2.5 hover:bg-field-active hover:text-field-active-foreground"
            @click="store.loadConversation(conversation.id, close)">
            <div>
              <component :is="iconComponents[conversation.program.metadata.icon]"
                class="h-5 w-5 mr-3 ml-2 opacity-70" />
            </div>
            <div class="flex flex-col items-start w-80 pr-2">
              <div class="font-medium truncate w-full pb-0.5">{{
                conversation.title
              }}</div>
              <div class="font-light truncate w-full opacity-70">{{ conversation.snippet ? conversation.snippet : 'No messages, yet!' }}
              </div>
            </div>
          </li>
        </ul>
        <h2 v-if="filteredConversations.nonSpaceConversations.length > 0"
          class="mb-2 mt-4 px-3 text-xs font-semibold text-field-default-foreground">All Conversations</h2>
        <ul class="divide-y divide-field-divide">
          <li v-for="conversation in filteredConversations.nonSpaceConversations" :key="conversation.id"
            class="group flex cursor-pointer select-none items-center pl-2 pr-4 py-2.5 hover:bg-field-active hover:text-field-active-foreground"
            @click="store.loadConversation(conversation.id, close)">
            <div>
              <component :is="iconComponents[conversation.program.metadata.icon]"
                class="h-5 w-5 mr-3 ml-2 opacity-70" />
            </div>
            <div class="flex flex-col items-start w-80 pr-2">
              <div class="font-medium truncate w-full pb-0.5">{{
                conversation.title
              }}</div>
              <div class="font-light truncate w-full opacity-70">{{ conversation.snippet ? conversation.snippet : 'No messages, yet!' }}</div>
            </div>
          </li>
        </ul>
      </div>
      <div
        v-if="filteredConversations.spaceConversations.length === 0 && filteredConversations.nonSpaceConversations.length === 0"
        class="px-6 py-14 text-center text-sm font-normal">No other conversations!</div>
    </PopoverPanel>
  </Popover>
</template>
  
<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { useAppStore } from '@/store/index.js';
import {
  Popover,
  PopoverButton,
  PopoverPanel,
} from '@headlessui/vue';

import {
  ChevronLeftIcon,
  ChevronRightIcon,
  ChevronDownIcon,
} from '@heroicons/vue/24/solid';
import { LifebuoyIcon, InformationCircleIcon, CalendarDaysIcon, DocumentMagnifyingGlassIcon, ChatBubbleLeftRightIcon, BuildingStorefrontIcon, HeartIcon, MagnifyingGlassIcon } from '@heroicons/vue/20/solid';
import loadingIcon from '@/assets/images/three-dots.svg';

const store = useAppStore();
const arrowsVisible = ref(false);
const tabContainerRef = ref(null);

const iconComponents = computed(() => ({
  CalendarDaysIcon,
  DocumentMagnifyingGlassIcon,
  ChatBubbleLeftRightIcon,
  BuildingStorefrontIcon,
  InformationCircleIcon,
  HeartIcon,
  LifebuoyIcon
}));

const openTabConversations = computed(() => {
  if (store.openTabs) {
    if (store.selectedSpaceId) {
      return store.openTabs
        .filter(id => store.selectedSpace.conversations.includes(id))
        .map(id => store.conversations[id])
        .filter(Boolean);
    }
    return store.openTabs
      .map(id => store.conversations[id])
      .filter(Boolean);
  }
  return [];
});

const tabItemRefs = reactive(
  openTabConversations.value.reduce((acc, conversation) => {
    acc[conversation.id] = null;
    return acc;
  }, {})
);

const query = ref('')

const spaceConversations = computed(() => {
  if (store.selectedSpace) {
    return store.selectedSpace.conversations.map(id => store.conversations[id]);
  }
  return [];
});

const nonSpaceConversations = computed(() => {
  if (store.selectedSpace) {
    return Object.values(store.conversations)
      .filter(conversation => !store.selectedSpace.conversations.includes(conversation.id));
  }
  return Object.values(store.conversations);
});

const filteredConversations = computed(() => {
  let spaceConvs = spaceConversations.value;
  let nonSpaceConvs = nonSpaceConversations.value;

  if (query.value) {
    const lowerCaseQuery = query.value.toLowerCase();
    spaceConvs = spaceConvs.filter(conversation =>
      conversation.title.toLowerCase().includes(lowerCaseQuery)
    );

    nonSpaceConvs = nonSpaceConvs.filter(conversation =>
      conversation.title.toLowerCase().includes(lowerCaseQuery)
    );
  }

  spaceConvs.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
  nonSpaceConvs.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));

  return {
    spaceConversations: spaceConvs,
    nonSpaceConversations: nonSpaceConvs
  };
});

const closeTab = (Id) => {
  store.closeTab(Id);
  checkArrowsVisibility();
}

const switchTab = (direction) => {
  const currentIndex = openTabConversations.value.findIndex(
    (conversation) => conversation.id === store.selectedConversationId
  );
  const newIndex =
    direction === 'next'
      ? (currentIndex + 1) % openTabConversations.value.length
      : (currentIndex - 1 + openTabConversations.value.length) %
      openTabConversations.value.length;

  if (newIndex >= 0 && newIndex < openTabConversations.value.length) {
    store.loadConversation(openTabConversations.value[newIndex].id);
  }
}

const scrollToSelectedTab = (conversationId) => {
  const selectedTab = tabItemRefs[conversationId];
  if (selectedTab) {
    selectedTab.scrollIntoView({
      behavior: 'smooth',
      inline: 'nearest',
      block: 'nearest',
    });
  }
};

const checkArrowsVisibility = async () => {
  if (!tabContainerRef.value) {
    return;
  }
  const tabContainer = tabContainerRef.value;
  const totalTabsWidth = openTabConversations.value.reduce((acc, conversation) => {
    const tabItem = tabItemRefs[conversation.id];
    return acc + (tabItem ? tabItem.clientWidth : 0);
  }, 0);

  arrowsVisible.value = totalTabsWidth > tabContainer.clientWidth;
};

watch(
  () => store.sidebarOpen,
  async () => {
    setTimeout(checkArrowsVisibility, 10)
  },
);

watch(
  () => store.selectedConversationId,
  async (newValue, oldValue) => {
    if (newValue !== oldValue) {
      scrollToSelectedTab(newValue);
    }
  }
);

watch(
  () => store.selectedSpaceId,
  async () => {
    checkArrowsVisibility();
  }
);

onMounted(async () => {
  window.addEventListener('resize', checkArrowsVisibility);
  setTimeout(checkArrowsVisibility, 50)
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', checkArrowsVisibility);
});
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}

.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>