<template>
    <div class="flex w-full items-start prose prose-invert max-w-none leading-7 mr-auto bg-nearyblue-300 py-9 pl-6 pr-8">
      <div class="not-prose flex-shrink-0 font-bold rounded h-7 w-7 flex items-center justify-center mr-5 text-sm"
        :class="message.is_archived ? 'bg-slate-700 text-slate-400' : 'bg-nearyblue-50/90 text-nearygray-100'">
        {{ firstLetterOfName }}
      </div>
      <div class="text-slate-300/80 whitespace-pre-wrap [overflow-wrap:anywhere]" :class="[message.is_archived ? 'text-slate-300/60' : 'text-slate-300/80']">{{ message.content }}</div>
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
      return name ? name[0] : '?';
    }
    return '?';
  });
  </script>