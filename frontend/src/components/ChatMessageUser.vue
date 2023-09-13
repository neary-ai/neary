<template>
    <div class="flex w-full items-start prose prose-invert max-w-none leading-7 mr-auto py-9 pl-6 pr-8 md:pr-12 lg:pr-20" :class="message.is_archived ? 'pattern-diagonal-lines pattern-nearyblue-200 pattern-bg-nearyblue-300 pattern-size-6 pattern-opacity-80' : 'bg-nearyblue-300'">
      <div class="not-prose flex-shrink-0 font-bold rounded h-7 w-7 flex items-center justify-center mr-5 text-sm bg-nearyblue-50/90 text-nearygray-100">
        {{ firstLetterOfName }}
      </div>
      <div class="whitespace-pre-wrap [overflow-wrap:anywhere]" :class="[message.is_archived ? 'text-nearygray-100' : 'text-slate-300/80']">{{ message.content }}</div>
    </div>
  </template>
  
  <script setup>
  import { computed } from 'vue';
  import { useAppStore } from '@/store/index.js';
  
  const props = defineProps({
    message: Object,
  });
  
  const store = useAppStore();
  
  const firstLetterOfName = computed(() => {
    if (store.userProfile && store.userProfile.name) {
      const name = store.userProfile.name;
      return name ? name[0] : 'U';
    }
    return 'U';
  });
  </script>