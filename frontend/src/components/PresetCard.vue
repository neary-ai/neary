<template>
  <div v-if="store.selectedConversation" @click="router.push('/presets')"
    class="cursor-pointer flex items-center justify-between gap-3 py-4 px-4 text-sm bg-field-default rounded-lg text-field-default-foreground">
    <div class="flex flex-col pl-4">
      <div class="mb-1 text-field-default-foreground font-semibold">{{ store.selectedConversation.preset.name }}</div>
      <div class="text-field-default-foreground/80">{{ store.selectedConversation.preset.description }}</div>
    </div>
    <ChevronRightIcon class="w-5 h-5 shrink-0"></ChevronRightIcon>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { ChevronRightIcon } from '@heroicons/vue/20/solid';
import { useAppStore } from '@/store/index.js';

const store = useAppStore();
const router = useRouter();

</script>