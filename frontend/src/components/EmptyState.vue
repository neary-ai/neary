<template>
  <div class="w-full h-screen flex flex-col items-center justify-start mt-12 px-8 pb-6">
    <Icon icon="uil:tornado" class="w-14 h-14 text-nearypink-300/70 mb-6" />
    <div class="text-xl text-slate-300 font-semibold mb-2 text-center">Ready? Just start typing.</div>
    <div class="w-full max-w-sm mt-8">
      <div class="flex flex-col gap-2.5">
        <label class="text-sm text-field-label">Choose a title</label>
        <input type="text" placeholder="Enter your title" v-model="conversationTitle" @blur="saveConversationSettings"
          class="py-2 pl-3 placeholder:text-field-default-foreground/60 rounded-lg text-field-default-foreground text-sm bg-field-default border border-transparent focus:border-field-focused focus:ring-0">
      </div>
      <div class="flex flex-col gap-2.5 my-8">
        <label class="text-sm text-field-label">Add to Space</label>
        <ListBoxBasic :options="store.spacesOptions" :value="selectedSpace" @updateInput="handleSpaceUpdate" />
      </div>
      <div class="flex flex-col gap-2.5 mt-8">
        <label class="text-sm text-field-label">Select Program</label>
        <ProgramCard />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, } from 'vue';
import { Icon } from '@iconify/vue';
import ListBoxBasic from './common/ListBoxBasic.vue'
import { useAppStore } from '@/store/index.js';
import ProgramCard from './ProgramCard.vue';

const store = useAppStore();

const conversationTitle = ref(null);
const selectedSpaceValue = ref(null);

const selectedSpace = computed(() => {
  if (store.conversationSettings.space && store.conversationSettings.space.value) {
      return store.conversationSettings.space.value
  }
});

const handleSpaceUpdate = async (selected) => {
  selectedSpaceValue.value = selected;
  await saveConversationSettings();
}

const saveConversationSettings = async () => {
  let settings = { 'title': conversationTitle.value, 'space': selectedSpaceValue.value }
  await store.updateConversationSettings(store.selectedConversationId, settings);
};

watch(
  () => store.conversationSettings,
  (newVal) => {
    if (newVal) {
      if (newVal && newVal.title) {
        conversationTitle.value = newVal.title.value;
      }
      if (newVal && newVal.space) {
        selectedSpaceValue.value = newVal.space.value;
      }
    }
  },
  { immediate: true }
);

</script>