<template>
    <div class="fixed w-full z-10 flex-shrink-0 h-12 flex items-center justify-center backdrop-blur-lg bg-nearygray-100/10 px-2">
        <div class="flex shrink-0 pt-1 sm:ml-1 items-center justify-center">
            <svg @click="store.toggleSidebar()" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                stroke-width="2" stroke="currentColor" class="-mt-1 w-7 h-7 sm:w-6 sm:h-6 cursor-pointer" :class="[(store.isMobile || !store.sidebarOpen) ? 'text-slate-300' : 'text-slate-400']">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25H12" />
            </svg>
            <img @click="router.push('/');" :src="logo" v-if="!store.isMobile && store.sidebarOpen" class="w-[4.5rem] ml-3.5" />
        </div>
        <CompactConversations v-if="store.isMobile" />
        <TabConversations v-else />
    </div>
</template>

<script setup>
import TabConversations from './TabConversations.vue';
import CompactConversations from './CompactConversations.vue';
import logo from '@/assets/images/neary.svg';
import { useAppStore } from '@/store/index.js';
import { useRouter } from 'vue-router';

const store = useAppStore();
const router = useRouter();

</script>