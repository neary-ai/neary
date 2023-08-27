<template>
  <div id="alt-window" class="font-mulish flex flex-col gap-3 max-w-3xl overflow-y-scroll">
    <div class="p-8 pt-[5.5rem]">
      <SectionHeading section-name="Conversations" @on-click="router.go(-1);" />
      <div v-if="conversations && conversations.length > 0" class="text-xs font-bold text-nearygray-100 mt-7">
        <template v-if="store.selectedSpace">In {{ store.selectedSpace.name }}</template>
        <template v-else>In All Spaces</template>
      </div>
      <ul v-if="conversations && conversations.length > 0" role="list"
        class="divide-y divide-neutral-500/80 flex flex-col max-w-3xl mt-2">
        <li @click="store.loadConversation(conversation.id)" v-for="conversation in conversations" :key="conversation.id"
          class="flex-grow group w-full cursor-pointer text-nearygray-300 flex items-center justify-start py-5">
          <div class="flex items-center justify-center mr-3 flex-grow h-full">
            <Icon :icon="conversation.preset.icon" class="w-6 h-6 text-nearygray-500" />
          </div>
          <div class="w-full truncate">
            <div class="font-bold text-sm text-nearygray-100 mb-0.5">{{ conversation.title }}</div>
            <div class="text-sm font-light text-nearygray-300 truncate overflow-hidden">{{ conversation.excerpt ?
              conversation.excerpt : 'No messages, yet!' }}</div>
          </div>
          <div class="self-end ml-4">
            <div class="flex items-center justify-center w-6 h-6 bg-neutral-500 rounded-full text-xs font-medium">{{ conversation.messages.length }}</div>
          </div>
        </li>
      </ul>
      <div v-else class="flex items-center justify-center max-w-lg">
        <div class="text-center py-12 px-14 mt-12 rounded-lg border-2 border-dashed border-neutral-100">
          <h3 class="mt-2 text-sm font-semibold text-nearygray-50">That's an empty space</h3>
          <p class="mt-1 text-sm text-nearygray-300">Start your first conversation</p>
          <div class="mt-6">
            <Button @buttonClick="store.createConversation(store.selectedSpace.id)" button-type="btn-pink">
              <div class="flex items-center gap-1 pr-1.5">
                <PlusIcon class="w-5 h-5" />
                New Conversation
              </div>
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import SectionHeading from './common/SectionHeading.vue'
import { useAppStore } from '@/store/index.js';
import { PlusIcon } from '@heroicons/vue/20/solid';
import Button from './common/Button.vue';
import { Icon } from '@iconify/vue';

const store = useAppStore();
const router = useRouter();

const conversations = computed(() => {
  let convs;
  if (store.selectedSpace) {
    convs = store.selectedSpace.conversations.map(id => store.conversations[id]);
  } else {
    convs = Object.values(store.conversations);
  }

  return convs.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
});
</script>