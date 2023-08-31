<template>
    <div id="alt-window" class="font-mulish flex flex-col gap-3 w-full overflow-y-scroll">
        <div class="p-8 pt-[5.5rem] max-w-3xl">
            <div class="flex items-center justify-between">
                <SectionHeading section-name="Plugin Settings" @on-click="onBackButtonClick" />
            </div>
            <div v-if="settings" class="divide-y divide-slate-400/20">
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
                            <div>{{ settings.parentPluginMetadata.display_name }}</div>
                        </div>
                        <div class="flex flex-col items-start">
                            <label class="text-sm font-semibold text-slate-300/90 w-full mb-1.5">Author</label>
                            <div>{{ settings.parentPluginMetadata.author }}</div>
                        </div>
                        <div class="flex flex-col items-start">
                            <label class="text-sm font-semibold text-slate-300/90 w-full mb-1.5">Version</label>
                            <div>{{ settings.parentPluginMetadata.version }}</div>
                        </div>
                        <div class="flex flex-col items-start">
                            <label class="text-sm font-semibold text-slate-300/90 w-full mb-1.5">Description</label>
                            <div>{{ settings.parentPluginMetadata.description }}</div>
                        </div>
                        <div v-if="settings.parentPluginMetadata.integrations" class="flex flex-col items-start">
                            <label class="text-sm font-semibold text-slate-300/90 w-full mb-1.5">Required
                                Integrations</label>
                            <div>{{ settings.parentPluginMetadata.integrations.map(name => formatName(name)).join(', ') }}
                            </div>
                        </div>
                    </div>
                </div>
                <template v-for="functionSettings in settings.functionSettingsArray" :key="functionSettings.functionName">
                    <div class="grid grid-cols-1 sm:grid-cols-7 py-12">
                        <div class="col-span-full sm:col-span-3 pr-12">
                            <div class="flex flex-col mb-6 sm:mb-0">
                                <div class="flex items-center text-slate-300 font-semibold mb-2">{{ functionSettings.displayName
                                }} <span :class="[functionSettings.type == 'snippet' ? 'bg-nearycyan-300/10 text-nearycyan-300 ring-nearycyan-300/20' : 'bg-nearyyellow-200/10 text-nearyyellow-200 ring-nearyyellow-200/20', 'inline-flex ml-1.5 items-center px-2 py-0.5 rounded-full text-xs font-medium  ring-1 ring-inset']">{{ formatName(functionSettings.type) }}</span>
                                </div>
                                <div class="text-sm text-nearygray-400">{{ functionSettings.description }}
                                </div>
                            </div>
                        </div>
                        <div class="col-span-full sm:col-span-4 flex flex-col text-slate-400">
                            <template v-if="Object.keys(functionSettings.functionSettings).length > 0"
                                v-for="(setting, key) in functionSettings.functionSettings" :key="key">
                                <div class="flex flex-col items-start mb-8">
                                    <div v-if="setting.type === 'boolean'"
                                        class="flex w-full items-start justify-start gap-2">
                                        <CheckboxField v-model="setting.value" class="grow-0 shrink-0" />
                                        <div class="flex flex-col flex-grow">
                                            <label class="text-sm font-bold text-slate-300/90 w-full mb-0.5">{{
                                                formatName(key) }}</label>
                                            <div v-if="setting.description" class="text-sm">{{ setting.description }}</div>
                                        </div>
                                    </div>
                                    <div v-else class="w-full">
                                        <label class="text-sm font-bold text-slate-300/90 w-full mb-0.5">{{ formatName(key)
                                        }}</label>
                                        <div v-if="setting.description" class="text-sm">{{ setting.description }}</div>
                                        <NumberInputField v-if="setting.type === 'integer'" v-model="setting.value"
                                            class="w-full mt-3" />
                                        <TextInputField v-else v-model="setting.value" class="w-full mt-3" />
                                    </div>
                                </div>
                            </template>
                            <div v-else class="text-sm font-semibold">This {{ functionSettings.type }} has no settings.
                            </div>
                        </div>
                    </div>
                </template>
                <div class="grid grid-cols-1 sm:grid-cols-7 py-12">
                    <div class="col-span-full sm:col-span-3 pr-12">
                        <div class="flex flex-col mb-6 sm:mb-0">
                            <div class="text-slate-300 font-semibold mb-2">Actions</div>
                            <div class="text-sm text-nearygray-400"></div>
                        </div>
                    </div>
                    <div class="col-span-1 sm:col-span-4 flex flex-col text-slate-400">
                        <div class="flex items-center w-full gap-3">
                            <Button class="shrink-0" button-type="btn-light" @click="saveSettings">Save Settings</Button>
                            <Button class="shrink-0" @buttonClick="clearPluginData()"
                                button-type="btn-outline-light">Clear Plugin Data</Button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
  
<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAppStore } from '@/store/index.js';
import SectionHeading from './common/SectionHeading.vue'
import TextInputField from './common/TextInputField.vue';
import NumberInputField from './common/NumberInputField.vue';
import CheckboxField from './common/CheckboxField.vue';
import Button from './common/Button.vue';
import api from '../services/apiService';

const store = useAppStore();
const router = useRouter();

const onBackButtonClick = () => {
    router.go(-1);
};

const settings = computed(() => {
    if (store.selectedConversation && store.selectedConversation.plugins) {
        const pluginName = router.currentRoute.value.params.name

        // Find the parent plugin from selectedConversation
        const parentPlugin = store.selectedConversation.plugins.find(
            (plugin) => plugin.name === pluginName
        );

        if (parentPlugin) {
            const functionSettingsArray = [];

            for (const functionName in parentPlugin.functions) {
                // Get the function settings from the parent plugin
                const functionSettings = parentPlugin.functions[functionName].settings;

                // Add the function settings, metadata, display name and description to the array
                functionSettingsArray.push({
                    functionName,
                    displayName: parentPlugin.functions[functionName].display_name,
                    description: parentPlugin.functions[functionName].description,
                    type: parentPlugin.functions[functionName].type,
                    functionSettings: functionSettings,
                });
            }

            return {
                parentPluginMetadata: parentPlugin.metadata,
                functionSettingsArray,
            };
        }
    }
});


const saveSettings = async () => {
    const updatedSettings = {};

    for (const functionSettings of settings.value.functionSettingsArray) {
        // Gather the updated settings values
        updatedSettings[functionSettings.functionName] = {};
        for (const key in functionSettings.functionSettings) {
            updatedSettings[functionSettings.functionName][key] = functionSettings.functionSettings[key].value;
        }
    }

    const pluginName = router.currentRoute.value.params.name

    try {
        await api.updatePluginSettings(pluginName, store.selectedConversationId, updatedSettings);
        store.newNotification('Plugin setting saved!');
    } catch (error) {
        console.error('Failed to update plugin settings:', error);
    }
};

const clearPluginData = async () => {
    const pluginName = router.currentRoute.value.params.name
    await api.clearPluginData(pluginName, store.selectedConversationId);
    store.newNotification('Plugin data cleared');
}

function formatName(name) {
    return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}
</script>