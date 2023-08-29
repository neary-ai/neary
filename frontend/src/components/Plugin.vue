<template>
    <div id="alt-window" class="font-mulish flex flex-col gap-3 w-full overflow-y-scroll">
        <div class="p-8 pt-[5.5rem] max-w-3xl">
            <div class="flex items-center justify-between">
                <SectionHeading section-name="Plugin Settings" @on-click="onBackButtonClick" />
            </div>
            <div v-if="plugin" class="divide-y divide-slate-400/20">
                <div class="grid grid-cols-1 sm:grid-cols-7 py-12">
                    <div class="col-span-full sm:col-span-3 pr-12">
                        <div class="flex flex-col mb-6 sm:mb-0">
                            <div class="text-slate-300 font-semibold mb-2">Plugin Info</div>
                            <div class="text-sm text-nearygray-400">About this plugin</div>
                        </div>
                    </div>
                    <div class="col-span-full sm:col-span-4 flex gap-6 flex-col text-slate-400 text-sm">
                        <div class="flex flex-col items-start">
                            <label class="text-sm font-semibold text-slate-300/90 w-full mb-1.5">Name</label>
                            <div>{{ plugin.registry.metadata.display_name }}</div>
                        </div>
                        <div class="flex flex-col items-start">
                            <label class="text-sm font-semibold text-slate-300/90 w-full mb-1.5">Author</label>
                            <div>{{ plugin.registry.metadata.author }}</div>
                        </div>
                        <div class="flex flex-col items-start">
                            <label class="text-sm font-semibold text-slate-300/90 w-full mb-1.5">Version</label>
                            <div>{{ plugin.registry.metadata.version }}</div>
                        </div>
                        <div class="flex flex-col items-start">
                            <label class="text-sm font-semibold text-slate-300/90 w-full mb-1.5">Description</label>
                            <div>{{ plugin.registry.metadata.description }}</div>
                        </div>
                        <div v-if="plugin.registry.metadata.integrations" class="flex flex-col items-start">
                            <label class="text-sm font-semibold text-slate-300/90 w-full mb-1.5">Required
                                Integrations</label>
                            <div>{{ plugin.registry.metadata.integrations.map(name => formatName(name)).join(', ') }}</div>
                        </div>
                    </div>
                </div>
                <div v-if="currentSettings" class="grid grid-cols-1 sm:grid-cols-7 py-12">
                    <div class="col-span-full sm:col-span-3 pr-12">
                        <div class="flex flex-col mb-6 sm:mb-0">
                            <div class="text-slate-300 font-semibold mb-2">Settings</div>
                            <div class="text-sm text-nearygray-400">Tweak the settings or use the provided defaults</div>
                        </div>
                    </div>
                    <div class="col-span-full sm:col-span-4 flex flex-col text-slate-400">
                        <template v-for="(setting, key) in currentSettings" :key="key">
                            <div class="flex flex-col items-start mb-8">
                                <div v-if="setting.type === 'boolean'" class="flex w-full items-start justify-start gap-2">
                                    <CheckboxField v-model="setting.value" class="grow-0 shrink-0" />
                                    <div class="flex flex-col flex-grow">
                                        <label class="text-sm font-bold text-slate-300/90 w-full mb-0.5">{{ formatName(key)
                                        }}</label>
                                        <div v-if="setting.description" class="text-sm">{{ setting.description }}</div>
                                    </div>
                                </div>
                                <div v-else class="w-full">
                                    <label class="text-sm font-bold text-slate-300/90 w-full mb-0.5">{{ formatName(key)
                                    }}</label>
                                    <div v-if="setting.description" class="text-sm">{{ setting.description }}</div>
                                    <NumberInputField v-if="setting.type === 'integer'" v-model="setting.value" class="w-full mt-3" />
                                    <TextInputField v-else v-model="setting.value" class="w-full mt-3" />
                                </div>
                            </div>
                        </template>
                        <div class="flex items-center w-full mt-8">
                            <Button class="shrink-0" button-type="btn-light" @click="saveSettings">Save Settings</Button>
                        </div>
                    </div>
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-7 py-12">
                    <div class="col-span-full sm:col-span-3 pr-12">
                        <div class="flex flex-col mb-6 sm:mb-0">
                            <div class="text-slate-300 font-semibold mb-2">Actions</div>
                            <div class="text-sm text-nearygray-400"></div>
                        </div>
                    </div>
                    <div class="col-span-1 sm:col-span-4 flex flex-col text-slate-400">
                        <div class="flex items-center w-full gap-3">
                            <Button class="shrink-0" @buttonClick="deleteConversation()"
                                button-type="btn-outline-light">Clear Plugin Data</Button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
  
<script setup>
import { ref, watch, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { Icon } from '@iconify/vue';
import { useAppStore } from '@/store/index.js';
import SectionHeading from './common/SectionHeading.vue'
import TextInputField from './common/TextInputField.vue';
import NumberInputField from './common/NumberInputField.vue';
import CheckboxField from './common/CheckboxField.vue';
import Button from './common/Button.vue';
import api from '../services/apiService';

const store = useAppStore();
const router = useRouter();

const plugin = ref(null);

const onBackButtonClick = () => {
    router.go(-1);
};

const currentSettings = computed(() => {
    // Check if plugin.value exists
    if (plugin.value && plugin.value.registry.default_settings) {
        // Get the default settings
        let defaultSettings = plugin.value.registry.default_settings
        let editableSettings = Object.fromEntries(Object.entries(defaultSettings).filter(([key, value]) => value.editable));

        // Get user-defined settings
        let userSettings = plugin.value.settings

        // If userSettings is not null, merge it with defaultSettings
        if (userSettings) {
            Object.keys(editableSettings).forEach(key => {
                if (key in userSettings) {
                    editableSettings[key].value = userSettings[key]
                }
            })
        }

        return editableSettings
    }
    return {}
})

const saveSettings = async () => {
    let updatedSettings = {};
    for (let key in currentSettings.value) {
        updatedSettings[key] = currentSettings.value[key].value;
    }
    await api.updatePluginSettings(plugin.value.id, updatedSettings);
    store.newNotification('Plugin updated!')
}


function formatName(name) {
    return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

onMounted(async () => {
    let pluginId = Number(router.currentRoute.value.params.id);
    plugin.value = await api.getPlugin(pluginId);
})
</script>