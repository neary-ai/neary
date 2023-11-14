<template>
    <div class="w-full overflow-y-scroll">
        <div v-if="store.selectedConversation && store.selectedConversation.settings && store.settingsOptions"
            id="alt-window" class="font-mulish flex flex-col gap-3 max-w-3xl">
            <div class="p-8 pt-[5.5rem]">
                <SectionHeading :section-name="pageTitle" @on-click="onBackButtonClick" />
                <div class="divide-y divide-slate-400/20">
                    <div class="grid grid-cols-1 sm:grid-cols-7 py-12">
                        <div class="col-span-full sm:col-span-3 pr-12">
                            <div class="flex flex-col mb-6 sm:mb-0">
                                <div class="text-slate-300 font-semibold mb-2">Preset Info</div>
                                <div class="text-sm text-nearygray-400">To add an icon, find one you like on <a
                                        href="https://icon-sets.iconify.design/" target="_blank"
                                        class="font-semibold text-nearygray-200">Iconify</a> and add the shortcode</div>
                            </div>
                        </div>
                        <div class="col-span-full sm:col-span-4 flex flex-col text-slate-400">
                            <div class="flex flex-col items-start">
                                <label class="text-sm font-semibold text-slate-300/90 w-full mb-1.5">Name</label>
                                <TextInputField class="w-full mb-6" v-model="preset.name"
                                    placeholderText="Enter a preset name" />
                            </div>
                            <div class="flex flex-col items-start">
                                <label class="text-sm font-semibold text-slate-300/90 w-full mb-1.5">Description</label>
                                <TextInputField class="w-full mb-6" v-model="preset.description"
                                    placeholderText="Enter an optional description" />
                            </div>
                            <div class="flex flex-col items-start">
                                <label class="text-sm font-semibold text-slate-300/90 w-full mb-1.5">Icon Shortcode</label>
                                <TextInputField class="w-full mb-6" v-model="preset.icon"
                                    placeholderText="some-collection:some-icon" />
                            </div>
                            <div class="flex flex-col items-start mt-2">
                                <Button class="shrink-0" @buttonClick="savePreset()" button-type="btn-light">Save Preset</Button>
                            </div>
                        </div>
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-7 py-12">
                        <div class="col-span-1 sm:col-span-3 pr-12">
                            <div class="flex flex-col mb-6 sm:mb-0">
                                <div class="text-slate-300 font-semibold mb-2">Actions</div>
                                <div class="text-sm text-nearygray-400">Exported presets include custom settings, but no user data</div>
                            </div>
                        </div>
                        <div class="col-span-1 sm:col-span-4 flex flex-col text-slate-400">
                            <div class="flex items-start w-full gap-3">
                                <Button class="shrink-0"
                                    @buttonClick="exportPreset(preset)"
                                    button-type="btn-light">Export Preset</Button>
                                <Button class="shrink-0"
                                    @buttonClick="deletePreset(preset)"
                                    button-type="btn-outline-light">Delete Preset</Button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAppStore } from '@/store/index.js';
import Button from './common/Button.vue';
import TextInputField from './common/TextInputField.vue';
import SectionHeading from './common/SectionHeading.vue'
import api from '../services/apiService';

const store = useAppStore();
const router = useRouter();

const pageTitle = ref('Create Preset');

const preset = ref({
    name: '',
    description: '',
    icon: ''
});

const savePreset = async () => {
    const id = Number(router.currentRoute.value.params.id);
    if (id !== 0) {
        await api.updatePreset(id, preset.value);
        store.newNotification("Preset updated");
    }
    else {
        let new_preset = await api.createPresetFromConversation(store.selectedConversationId, preset.value);
        store.availablePresets.push(new_preset)
        console.log("Avail: ", store.availablePresets)
        await store.updateConversationPreset(store.selectedConversation, new_preset);
        store.newNotification("New preset saved");
    }
};

const exportPreset = async (preset) => {
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

const onBackButtonClick = () => {
    router.go(-1);
};

const deletePreset = async (preset) => {
  store.availablePresets = await api.deletePreset(preset);
  store.newNotification('Preset deleted');
  router.go(-1);
}

onMounted(() => {
    const id = Number(router.currentRoute.value.params.id);
    if (id !== 0) {
        pageTitle.value = "Edit Preset Info";
        const foundPreset = store.availablePresets.find(p => p.id === id);
        if (foundPreset) {
            preset.value = foundPreset;
        }
    }
});

</script>