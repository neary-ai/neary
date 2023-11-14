<template>
  <div v-if="store.availablePresets" id="alt-window" class="font-mulish flex flex-col gap-3 w-full overflow-y-scroll">
    <div class="p-8 pt-[5.5rem] max-w-3xl">
      <div class="flex items-center justify-between">
        <SectionHeading section-name="Presets" @on-click="onBackButtonClick" />
        <div class="cursor-pointer flex text-nearylight-300 text-sm font-medium items-center justify-center"
          @click="$refs.fileInput.click()">
          <Icon icon="heroicons:arrow-down-on-square-20-solid" class="w-5 h-5 mr-1" />
          Import Preset
        </div>
        <input type="file" @change="importPreset" accept=".json" style="display: none" ref="fileInput" />
      </div>
      <div class="flex flex-col w-full gap-3 mt-6">
        <template v-for="preset in store.availablePresets" :key="preset.id">
          <Card class="cursor-pointer" @click="updatePreset(preset)" :active="isSelected(preset).value">
            <template v-slot:icon>
              <div class="flex items-center justify-center h-9 w-9 rounded shadow bg-nearycyan-500/80 mt-0.5">
                <Icon :icon="preset.icon ? preset.icon : 'heroicons:user-solid'" class="text-white w-6 h-6" />
              </div>
            </template>
            <div class="leading-7">
              <div class="text-field-default-foreground text-sm font-medium">
                {{ preset.name }}
              </div>
              <div class="text-sm text-nearygray-400">{{ preset.description }}</div>
            </div>
            <template v-slot:button>
              <Popover class="relative inline-block text-left">
                <PopoverButton
                  class="flex items-center group relative cursor-pointer px-2 py-0.5 hover:text-nearygray-100 focus:border-transparent focus:ring-0 focus:outline-none">
                  <Icon icon="heroicons:ellipsis-vertical" class="w-5 h-5" />
                </PopoverButton>
                <Transition as="div" enter="transition ease-out duration-200" enterFrom="opacity-0 translate-y-1"
                  enterTo="opacity-100 translate-y-0" leave="transition ease-in duration-150"
                  leaveFrom="opacity-100 translate-y-0" leaveTo="opacity-0 translate-y-1">
                  <PopoverPanel v-slot="{ close }"
                    class="absolute w-40 bottom-8 -right-0 origin-top-right ring-1 ring-nearygray-500  bg-nearygray-200 text-nearyblue-300 rounded-md focus:outline-none z-20">
                    <ul class="divide-y divide-nearygray-500">
                      <li v-if="preset.is_default"
                        class="text-nearygray-800 flex items-center rounded-t gap-2 px-3 py-2 text-sm">
                        <Icon icon="heroicons:check-20-solid" class="w-5 h-5" />
                        <div>Default Preset</div>
                      </li>
                      <li v-else @click.stop="setDefault(preset, close)"
                        class="cursor-pointer flex items-center rounded-t gap-2 px-3 py-2 text-sm hover:bg-nearygray-300">
                        <Icon icon="heroicons:cursor-arrow-rays-20-solid" class="w-5 h-5" />
                        <div>Set as Default</div>
                      </li>
                      <li @click.stop="router.push(`/preset/${preset.id}`);"
                        class="cursor-pointer flex items-center rounded-b gap-2 px-3 py-2 text-sm hover:bg-nearygray-300">
                        <Icon icon="heroicons:pencil" class="w-5 h-5" />
                        <div>Edit Preset</div>
                      </li>
                      <li @click.stop="store.deletePreset(preset, close)"
                        class="cursor-pointer flex items-center rounded-b gap-2 px-3 py-2 text-sm hover:bg-nearygray-300">
                        <Icon icon="heroicons:x-mark" class="w-5 h-5" />
                        <div>Delete Preset</div>
                      </li>
                      <li @click.stop="exportPreset(preset, close)"
                        class="cursor-pointer flex items-center rounded-b gap-2 px-3 py-2 text-sm hover:bg-nearygray-300">
                        <Icon icon="heroicons:arrow-up-on-square" class="w-5 h-5" />
                        <div>Export Preset</div>
                      </li>
                    </ul>
                  </PopoverPanel>
                </Transition>
              </Popover>
            </template>
          </Card>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { Icon } from '@iconify/vue';
import { useAppStore } from '@/store/index.js';
import { Popover, PopoverButton, PopoverPanel } from '@headlessui/vue';
import SectionHeading from './common/SectionHeading.vue'
import Card from './common/Card.vue';
import api from '../services/apiService';

const store = useAppStore();
const router = useRouter();

const isSelected = (preset) => computed(() => {
  return store.selectedConversation.preset_id === preset.id;
})

const updatePreset = async (preset) => {
  await store.updateConversationPreset(store.selectedConversation, preset);
}

const exportPreset = async (preset, close) => {
  close();

  const presetJSON = await api.exportPreset(preset);
  const presetString = JSON.stringify(presetJSON, null, 2);
  const fileData = new Blob([presetString], { type: "application/json" });
  const fileName = `preset_${preset.id}.json`;

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

const importPreset = async (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = async function (e) {
      try {
        const preset = JSON.parse(e.target.result);

        // Define required keys
        const requiredKeys = ["name", "description", "icon", "plugins", "settings"];

        // Check if all required keys exist in the preset
        const isValidPreset = requiredKeys.every(key => key in preset);

        // Check if a preset with the same name already exists
        const presetExists = store.availablePresets.some(existingPreset => existingPreset.name === preset.name);

        if (!isValidPreset) {
          store.newNotification("Invalid preset! Check the file format.");
          return;
        }

        if (presetExists) {
          store.newNotification("A preset with this name already exists");
          return;
        }
        let new_preset = await api.importPreset(preset);
        store.availablePresets.push(new_preset)
      } catch (err) {
        console.log(err)
        store.newNotification("Unable to import preset");
      }
    };
    reader.readAsText(file);
  }
};

const setDefault = async (preset) => {
  preset['is_default'] = true;
  await api.updatePreset(preset.id, preset);
}

const onBackButtonClick = () => {
  router.go(-1);
};

</script>