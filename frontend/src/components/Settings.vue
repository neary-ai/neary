<template>
  <div id="alt-window" class="font-mulish flex flex-col gap-3 max-w-3xl overflow-y-scroll">
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
          <div v-if="store.conversationSettings && store.conversationSettings.title" class="col-span-full sm:col-span-4 flex flex-col text-slate-400">
            <div class="flex flex-col items-start">
              <label class="text-sm font-semibold text-slate-300/90 w-full mb-1.5">Title</label>
              <TextInputField class="w-full mb-6" :value="store.conversationSettings.title.value" @updateInput="handleSettingsInput('conversation', 'title', $event)" />
            </div>
            <div class="flex flex-col items-start">
              <label class="text-sm font-semibold text-slate-300/90 w-full mb-1.5">Space</label>
              <ListBoxBasic class="w-full mb-6" :value="selectedSpace" :options="store.spacesOptions" @updateInput="handleSettingsInput('conversation', 'space', $event)" />
            </div>
            <label class="text-sm font-semibold text-slate-300/90 w-full mb-1.5">Program</label>
            <ProgramCard />
          </div>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-7 py-12">
          <div class="col-span-full sm:col-span-3 pr-12">
            <div v-if="store.conversationSettings.program && store.conversationSettings.program.value=='DefaultProgram'" class="flex flex-col mb-6 sm:mb-0">
              <div class=" text-slate-300 font-semibold mb-2">AI Settings</div>
              <div class="text-sm text-nearygray-400">The default settings work well for most conversations. If in doubt, leave them as is. </div>
            </div>
            <div v-else class="flex flex-col mb-6 sm:mb-0">
              <div class=" text-slate-300 font-semibold mb-2">Program Settings</div>
              <div class="text-sm text-nearygray-400">Tweak these to change the way your program behaves.</div>
            </div>
          </div>
          <div class="col-span-full sm:col-span-4 flex flex-col text-slate-400">
            <template v-for="(setting, key) in store.programSettings" :key="key">
              <div class="flex flex-col items-start">
                <label v-if="setting.field !== null" class="text-sm font-semibold text-slate-300 w-full mb-1.5">{{
                  setting.display_name
                }}</label>
                <component class="w-full mb-6" :is="resolveDynamicComponent(setting.field)" v-if="setting.field !== null"
                  :inputName="key" :value="setting.value" :options="setting.options"
                  @updateInput="handleSettingsInput('program', key, $event)" />
              </div>
            </template>
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
              <ListBoxBasic class="w-full mb-6" :options="exportOptions" :value="'plain'" @updateInput="handleExportInput($event)" />
              <Button @buttonClick="downloadConversation()" button-type="btn-pink">Download</Button>
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
              <Button class="shrink-0" @buttonClick="archiveMessages()" button-type="btn-pink">Archive Messages</Button>
              <Button class="shrink-0" @buttonClick="deleteConversation()" button-type="btn-outline-pink">Delete Conversation</Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAppStore } from '@/store/index.js';
import api from '@/services/apiService';
import Button from './common/Button.vue';
import TextInputField from './common/TextInputField.vue';
import NumberInputField from './common/NumberInputField.vue';
import TextareaField from './common/TextareaField.vue';
import CheckboxField from './common/CheckboxField.vue';
import SectionHeading from './common/SectionHeading.vue'
import ProgramCard from './ProgramCard.vue';
import ListBoxBasic from './common/ListBoxBasic.vue';

const store = useAppStore();
const router = useRouter();
const exportFormat = ref("plain")

const exportOptions = [
  { value: 'plain', option: 'Plain Text' },
  { value: 'json', option: 'JSON' }
]

let debounce;

const selectedSpace = computed(() => {
  if (store.conversationSettings.space && store.conversationSettings.space.value > 0) return store.conversationSettings.space.value
  else return -1
})

const handleSettingsInput = async (section, setting, value) => {
  clearTimeout(debounce)
  debounce = setTimeout(async () => {
    if (section == 'conversation') {
      await store.updateConversationSettings(store.selectedConversationId, {[setting]: value});
    }
    else if (section == 'program') {
      await store.updateProgramSettings(store.selectedConversationId, {[setting]: value});
    }
  }, 500);
};

const handleExportInput = (event) => {
  exportFormat.value = event;
}

const archiveMessages = async () => {
  await store.archiveMessages(store.selectedConversationId);
  router.push('/');
  store.notification = { "type": "success", "message": "Messages archived!" }
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

const resolveDynamicComponent = (fieldType) => {
  switch (fieldType) {
    case 'TextInput':
      return TextInputField;
    case 'NumberInput':
      return NumberInputField;
    case 'Select':
      return ListBoxBasic;
    case 'Textarea':
      return TextareaField;
    case 'Checkbox':
      return CheckboxField;
  }
};
</script>