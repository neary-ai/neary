<template>
    <div id="alt-window" class="font-mulish flex flex-col gap-3 max-w-3xl overflow-y-scroll">
        <div class="p-8 pt-[5.5rem]">
            <SectionHeading section-name="Programs" @on-click="onBackButtonClick" />
            <div class="mt-6">
                <div v-if="programData" class="space-y-4">
                    <template v-for="program in programData.options" :key="program.value">
                        <div class='relative cursor-pointer rounded-lg border border-transparent bg-neutral-500 px-6 py-4 shadow-sm focus:outline-none max-w-xl'>
                            <span class="flex flex-col sm:flex-row gap-4 items-center justify-between">
                                <span class="w-full flex items-center justify-start text-sm">
                                    <component :is="iconComponents[program.icon]"
                                        class="hidden sm:inline-block h-6 w-6 mr-4 text-nearygray-200/80 shrink-0" />
                                    <div class="flex flex-col">
                                        <span class="font-medium text-nearygray-50 mb-0.5">{{ program.option }}</span>
                                        <span class="text-nearygray-400">{{program.description }}</span>
                                    </div>
                                </span>
                                <button @click="updateProgram(program.value)" type="button" :class="[selectedProgram && selectedProgram.value === program.value ? 'bg-nearypink-300/80 text-white' : 'bg-nearyblue-50 text-nearygray-200', 'w-full sm:w-24 shrink-0 px-3 py-2 text-sm rounded']">
                                    <span v-if="selectedProgram && selectedProgram.value === program.value">Deactivate</span>
                                    <span v-else>Activate</span>
                                </button>
                            </span>
                        </div>
                    </template>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAppStore } from '@/store/index.js';
import SectionHeading from './common/SectionHeading.vue'
import { LifebuoyIcon, CalendarDaysIcon, DocumentMagnifyingGlassIcon, ChatBubbleLeftRightIcon, XMarkIcon, BuildingStorefrontIcon, HeartIcon, InformationCircleIcon } from '@heroicons/vue/24/outline';

const store = useAppStore();
const router = useRouter();
const selectedProgramValue = ref(null);

const programData = computed(() => {
  if (store.conversationSettings && store.conversationSettings.program) {
    return store.conversationSettings.program;
  }
});

const selectedProgram = computed(() => {
  if (programData.value) {
    let currentProgram = programData.value.options.find(item => item.value === selectedProgramValue.value);
    return currentProgram;
  }
});

const updateProgram = async (program) => {
  if (program == selectedProgramValue.value) {
    selectedProgramValue.value = 'DefaultProgram'
    
  }
  else {
    selectedProgramValue.value = program
  }
  await store.updateConversationSettings(store.selectedConversationId, {'program': selectedProgramValue.value});
}

const iconComponents = computed(() => ({
    CalendarDaysIcon,
    DocumentMagnifyingGlassIcon,
    ChatBubbleLeftRightIcon,
    BuildingStorefrontIcon,
    InformationCircleIcon,
    HeartIcon,
    XMarkIcon,
    LifebuoyIcon
}));


const onBackButtonClick = () => {
    router.go(-1);
};

watch(
  () => store.conversationSettings,
  (newVal) => {
    if (newVal) {
      if (newVal && newVal.program) {
        selectedProgramValue.value = newVal.program.value;
      }
    }
  },
  { immediate: true }
);

</script>