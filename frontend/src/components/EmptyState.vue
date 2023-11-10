<template>
  <div
    :class="[isTall ? 'justify-start' : 'justify-center', 'w-full h-screen flex flex-col items-center mt-12 px-8 pb-6']">
    <Icon icon="uil:tornado" class="w-14 h-14 text-nearypink-300 mb-6" />
    <div class="text-xl text-nearygray-50 font-semibold mb-2 text-center">Ready? Just start typing.</div>
    <div v-if="isTall && store.selectedConversation" class="w-full max-w-sm mt-8">
      <div class="flex flex-col gap-2.5 mb-6">
        <label class="text-sm text-field-label">Choose a title</label>
        <TextInputField class="w-full" @change="store.updateConversation(store.selectedConversation)"
          v-model="store.selectedConversation.title" />
      </div>
      <div class="flex flex-col gap-2.5 mb-6">
        <label class="text-sm text-field-label">Add to Space</label>
        <ListBoxBasic @change="store.updateConversation(store.selectedConversation)"
          v-model="store.selectedConversation.space_id" :options="store.spacesOptions" />
      </div>
      <div class="flex flex-col gap-2.5">
        <label class="text-sm text-field-label">Select Preset</label>
        <Card @click="router.push('/stack')" class="cursor-pointer" padding="px-3 py-2.5">
          <template v-slot:icon>
            <div class="flex items-center justify-center">
              <Icon
                :icon="store.conversationPreset(store.selectedConversation).icon ? store.conversationPreset(store.selectedConversation).icon : 'heroicons:user-solid'"
                class="text-nearygray-300 w-6 h-6" />
            </div>
          </template>
          <div class="font-medium text-sm py-0.5 -ml-1 text-field-default-foreground">
            {{ store.conversationPreset(store.selectedConversation).name }}</div>
          <template v-slot:button>
            <ChevronRightIcon class="w-5 h-5 shrink-0"></ChevronRightIcon>
          </template>
        </Card>
      </div>
    </div>
    <div v-else class="w-full max-w-xs">
      <div @click="router.push('/stack')"
        class="cursor-pointer flex items-center justify-center text-nearygray-400 text-sm mt-3">View chat stack
        &rarr;</div>
    </div>
  </div>
</template>

<script setup>
import { Icon } from '@iconify/vue';
import { ref, computed, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import ListBoxBasic from './common/ListBoxBasic.vue'
import TextInputField from './common/TextInputField.vue'
import { useAppStore } from '@/store/index.js';
import Card from './common/Card.vue';
import { ChevronRightIcon } from '@heroicons/vue/20/solid';

const store = useAppStore();
const route = useRoute();
const router = useRouter();

// Determine layout
const windowHeight = ref(window.innerHeight);

const updateHeight = () => {
  windowHeight.value = window.innerHeight;
};

window.addEventListener('resize', updateHeight);

onUnmounted(() => {
  window.removeEventListener('resize', updateHeight);
});

const isTall = computed(() => windowHeight.value > 680);


// Update space
const selectedSpaceValue = ref(null);

</script>