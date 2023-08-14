<template>
    <div :class="[store.sidebarOpen && !store.isMobile ? 'left-44' : 'left-0', 'fixed top-12  right-0 bottom-28 flex items-center justify-center z-5']">
      <div class="bg-nearyblue-500/50 backdrop-blur-md w-full h-full rounded-lg relative p-12 overflow-y-scroll">
        <button @click="store.showXray = false" class="absolute top-4 right-4">
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
        <div v-else class="text-nearygray-200 mb-2 w-4/5 leading-7 border-l-4 border-nearyblue-50 pl-4">Send a message, then check back here for details about your most recent request.</div>
      </div>
    </div>
</template>

<script setup>
import { computed } from 'vue';
import { useAppStore } from '@/store/index.js';

const store = useAppStore();

const tokenSum = computed(() => {
  if (store.xray.messages) {
    return store.xray.messages.reduce((total, message) => total + message.tokens, 0);
  }
  return 0
});
</script>