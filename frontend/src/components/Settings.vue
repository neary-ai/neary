<template>
  <div class="w-full overflow-y-scroll">
    <div v-if="store.selectedConversation && store.selectedConversation.settings && store.settingsOptions" id="alt-window"
      class="font-mulish flex flex-col gap-3 max-w-3xl">
      <div class="p-8 pt-[5.5rem]">
        <SectionHeading section-name="Settings" @on-click="onBackButtonClick" />
        <div class="divide-y divide-slate-400/20">
          <div class="grid grid-cols-1 sm:grid-cols-7 py-12">
            <div class="col-span-full sm:col-span-3 pr-12">
              <div class="flex flex-col mb-6 sm:mb-0">
                <div class="text-slate-300 font-semibold mb-2">Conversation Settings</div>
                <div class="text-sm text-nearygray-400">Customize your conversation</div>
              </div>
            </div>
            <div class="col-span-full sm:col-span-4 flex flex-col text-slate-400">
              <div class="flex flex-col items-start">
                <label class="text-sm font-semibold text-slate-300/90 w-full mb-1.5">Title</label>
                <TextInputField class="w-full mb-6" @change="store.updateConversation(store.selectedConversation)"
                  v-model="store.selectedConversation.title" />
              </div>
              <div class="flex flex-col items-start">
                <label class="text-sm font-semibold text-slate-300/90 w-full mb-1.5">Space</label>
                <ListBoxBasic class="w-full mb-6" @change="store.updateConversation(store.selectedConversation)"
                  v-model="store.selectedConversation.space_id" :options="store.spacesOptions" />
              </div>
            </div>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-7 py-12">
            <div class="col-span-full sm:col-span-3 pr-12">
              <div class="flex flex-col mb-6 sm:mb-0">
                <div class=" text-slate-300 font-semibold mb-2">AI Settings</div>
                <div class="text-sm text-nearygray-400">Configure the chat model to shape the AI's output and performance</div>
              </div>
            </div>
            <div class="col-span-full sm:col-span-4 flex flex-col text-slate-400">

              <div class="flex flex-col items-start">
                <label class="text-sm font-semibold text-slate-300 w-full mb-1.5">API Type</label>
                <ListBoxBasic @change="store.updateConversation(store.selectedConversation)" class="w-full mb-6"
                  v-model="store.selectedConversation.settings.llm.api_type"
                  :options="store.settingsOptions.llm.api_type" />
              </div>
              <div class="flex flex-col items-start">
                <label class="text-sm font-semibold text-slate-300 w-full mb-1.5">Model</label>
                <ListBoxBasic @change="store.updateConversation(store.selectedConversation)" class="w-full mb-6"
                  v-model="store.selectedConversation.settings.llm.model" :options="store.settingsOptions.llm.model" />
              </div>
              <div class="flex flex-col items-start">
                <label class="text-sm font-semibold text-slate-300 w-full mb-1.5">Temperature</label>
                <NumberInputField :step=".1" :minValue="0" :maxValue="1" @change="store.updateConversation(store.selectedConversation)" class="w-full mb-6"
                  v-model="store.selectedConversation.settings.llm.temperature" />
              </div>
              <div class="flex flex-col items-start">
                <label class="text-sm font-semibold text-slate-300 w-full mb-1.5">Input Tokens</label>
                <NumberInputField :step="100" :minValue="0" @change="store.updateConversation(store.selectedConversation)" class="w-full mb-6"
                  v-model="store.selectedConversation.settings.max_input_tokens" />
              </div>
              <div class="flex flex-col items-start">
                <label class="text-sm font-semibold text-slate-300 w-full mb-1.5">Max Tokens (0 = infinite)</label>
                <NumberInputField :step="100" :minValue="0" @change="store.updateConversation(store.selectedConversation)" class="w-full mb-6"
                  v-model="store.selectedConversation.settings.llm.max_tokens" />
              </div>
            </div>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-7 py-12">
            <div class="col-span-full sm:col-span-3 pr-4">
              <div class="flex flex-col mb-6 sm:mb-0">
                <div class=" text-slate-300 font-semibold mb-2">Export Data</div>
                <div class="text-sm text-slate-400">Save your messages locally</div>
              </div>
            </div>
            <div class="col-span-full sm:col-span-4 flex flex-col text-slate-400">
              <div class="flex flex-col items-start">
                <label class="text-sm font-semibold text-slate-300 w-full mb-1.5">Export Format</label>
                <ListBoxBasic class="w-full mb-6" :options="exportOptions" v-model="exportFormat"
                  @change="handleExportInput($event)" />
                <Button @buttonClick="downloadConversation()" button-type="btn-light">Download</Button>
              </div>
            </div>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-7 py-12">
            <div class="col-span-1 sm:col-span-3 pr-4">
              <div class="flex flex-col mb-6 sm:mb-0">
                <div class=" text-slate-300 font-semibold mb-2">Manage Conversation</div>
              </div>
            </div>
            <div class="col-span-1 sm:col-span-4 flex flex-col text-slate-400">
              <div class="flex items-center w-full gap-3">
                <Button class="shrink-0" @buttonClick="archiveMessages()" button-type="btn-light">Archive
                  Messages</Button>
                <Button class="shrink-0" @buttonClick="deleteConversation()" button-type="btn-outline-light">Delete
                  Conversation</Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAppStore } from '@/store/index.js';
import api from '@/services/apiService';
import Button from './common/Button.vue';
import TextInputField from './common/TextInputField.vue';
import NumberInputField from './common/NumberInputField.vue';
import TextareaField from './common/TextareaField.vue';
import SectionHeading from './common/SectionHeading.vue'
import Card from './common/Card.vue';
import { Icon } from '@iconify/vue';
import ListBoxBasic from './common/ListBoxBasic.vue';
import { XMarkIcon, ChevronRightIcon } from '@heroicons/vue/20/solid';

const store = useAppStore();
const router = useRouter();
const exportFormat = ref("plain")

const exportOptions = [
  { value: 'plain', option: 'Plain Text' },
  { value: 'json', option: 'JSON' }
]

const enabledSnippets = computed(() => {
  if (store.selectedConversation) {
    return store.selectedConversation.plugins.filter(plugin => plugin.type === 'snippet');
  }
  return []
});

const enabledTools = computed(() => {
  if (store.selectedConversation) {
    return store.selectedConversation.plugins.filter(plugin => plugin.type === 'tool');
  }
  return []
});

const disablePlugin = async (plugin) => {
  store.selectedConversation.plugins = store.selectedConversation.plugins.filter(p => p !== plugin);
  await store.updateConversation(store.selectedConversation);
}

// Create new preset
const createPresetName = ref('')
const createPresetDescription = ref('')

const createPreset = async () => {
  console.log('creating preset with: ', createPresetName.value)
  try {
    await api.createPreset(createPresetName.value, createPresetDescription.value, store.selectedConversationId)
    store.newNotification("Preset saved!");
  }
  catch {
    store.newNotification("Couldn't save preset");
  }

}

const handleExportInput = (event) => {
  exportFormat.value = event;
}

const archiveMessages = async () => {
  await store.archiveMessages(store.selectedConversationId);
  router.push('/');
  store.newNotification("Messages archived!");
};

const deleteConversation = async () => {
  await store.deleteConversation(store.selectedConversationId);
};

const downloadConversation = async () => {
  const conversationId = Number(router.currentRoute.value.params.id);
  const fileData = await api.exportConversation(conversationId, exportFormat.value);
  const fileExtension = exportFormat.value === "plain" ? ".txt" : ".json";
  const fileName = `conversation_${conversationId}${fileExtension}`;

  const downloadLink = document.createElement("a");
  downloadLink.href = URL.createObjectURL(fileData);
  downloadLink.download = fileName;
  downloadLink.style.display = "none";
  document.body.appendChild(downloadLink);
  downloadLink.click();

  setTimeout(() => {
    URL.revokeObjectURL(downloadLink.href);
    document.body.removeChild(downloadLink);
  }, 100);
};

const onBackButtonClick = () => {
  router.go(-1);
};

watch(() => store.selectedConversationId, async (newId) => {
  if (newId) {
    store.settingsOptions = await api.getAvailableSettings();
  }
}, { immediate: true });

</script>