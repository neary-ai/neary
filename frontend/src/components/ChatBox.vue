<template>
  <div class="fixed -bottom-0.5 w-full" :class="[(store.sidebarOpen && !store.isMobile) ? 'pl-44' : '']">
    <div class="relative">
        <Toolbar />
        <TextInput />
    </div>
        <Xray v-if="store.showXray" />
  </div>
</template>

<script setup>
import { useAppStore } from '@/store/index.js';
import TextInput from './TextInput.vue';
import Toolbar from './Toolbar.vue';
import Xray from './Xray.vue';

const store = useAppStore();
</script>