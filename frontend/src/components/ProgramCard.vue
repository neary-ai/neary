<template>
    <div @click="router.push('/programs')"
        class="cursor-pointer flex items-center justify-between gap-3 py-4 px-4 text-sm bg-field-default rounded-lg text-field-default-foreground">
        <div v-if="selectedProgram" class="flex items-center">
        <component v-if="iconComponents" :is="iconComponents[selectedProgram.icon]" class="w-8 h-8 text-field-default-foreground" />
        <div class="flex flex-col pl-4">
            <div class="mb-1 text-field-default-foreground font-semibold">{{selectedProgram.option}}</div>
            <div class="text-field-default-foreground/80">{{selectedProgram.description}}</div>
        </div>
        </div>
        <div v-else class="flex items-center gap-4">
        <div class="flex-1">
            <CursorArrowRaysIcon class="w-7 h-7 text-nearygray-500" />
        </div>
        <div class="text-nearygray-400 font-semibold">Enhance your conversation with special capabilities by activating a program.</div>
        </div>
        <ChevronRightIcon class="w-5 h-5 shrink-0"></ChevronRightIcon>
    </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { ChevronRightIcon } from '@heroicons/vue/20/solid';
import { LifebuoyIcon, XMarkIcon, CalendarDaysIcon, DocumentMagnifyingGlassIcon, ChatBubbleLeftRightIcon, MapPinIcon, BuildingStorefrontIcon, HeartIcon, InformationCircleIcon, CursorArrowRaysIcon } from '@heroicons/vue/24/outline';
import { useAppStore } from '@/store/index.js';

const store = useAppStore();
const router = useRouter();

const iconComponents = computed(() => ({
  CalendarDaysIcon,
  DocumentMagnifyingGlassIcon,
  MapPinIcon,
  ChatBubbleLeftRightIcon,
  BuildingStorefrontIcon,
  InformationCircleIcon,
  HeartIcon,
  XMarkIcon,
  LifebuoyIcon
}));

const selectedProgram = computed(() => {
  if (store.conversationSettings && store.conversationSettings.program) {
    let currentProgram = store.conversationSettings.program.options.find(item => item.value === store.conversationSettings.program.value);
    return currentProgram;
  }
});

</script>