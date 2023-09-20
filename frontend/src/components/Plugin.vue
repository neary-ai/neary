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
                            <div>{{ settings.plugin.display_name }}</div>
                        </div>
                        <div class="flex flex-col items-start">
                            <label class="text-sm font-semibold text-slate-300/90 w-full mb-1.5">Author</label>
                            <div>{{ settings.plugin.author }}</div>
                        </div>
                        <div class="flex flex-col items-start">
                            <label class="text-sm font-semibold text-slate-300/90 w-full mb-1.5">Version</label>
                            <div>{{ settings.plugin.version }}</div>
                        </div>
                        <div class="flex flex-col items-start">
                            <label class="text-sm font-semibold text-slate-300/90 w-full mb-1.5">Description</label>
                            <div>{{ settings.plugin.description }}</div>
                        </div>
                        <div v-if="settings.plugin.integrations" class="flex flex-col items-start">
                            <label class="text-sm font-semibold text-slate-300/90 w-full mb-1.5">Required
                                Integrations</label>
                            <div>{{ settings.plugin.integrations.map(name => formatName(name)).join(', ') }}
                            </div>
                        </div>
                    </div>
                </div>
                <template v-for="functionSettings in settings.functions" :key="functionSettings.functionName">
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
                            <template v-if="functionSettings.functionSettings && Object.keys(functionSettings.functionSettings).length > 0"
                                v-for="(setting, key) in functionSettings.functionSettings" :key="key">
                                <div class="flex flex-col items-start mb-8">
                                    <div v-if="setting.type === 'boolean'"
                                        class="flex w-full items-start justify-start gap-2">
                                        <CheckboxField @change="saveSettings()" v-model="setting.value" class="grow-0 shrink-0" />
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
                                        <NumberInputField v-if="setting.type === 'integer'" v-model="setting.value" @change="saveSettings()" class="w-full mt-3" />
                                        <TextInputField v-else v-model="setting.value" @change="saveSettings()" class="w-full mt-3" />
                                    </div>
                                </div>
                            </template>
                            <div v-else class="text-sm font-semibold">This {{ functionSettings.type }} has no settings.</div>
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
                            <Button class="shrink-0" @buttonClick="clearPluginData()" button-type="btn-outline-light">Clear Plugin Data</Button>
                            <Button v-if="settings.plugin.is_enabled" class="shrink-0" @buttonClick="store.disablePlugin(settings.plugin.plugin_id)" button-type="btn-outline-light">Disable Plugin</Button>
                            <Button v-else class="shrink-0" @buttonClick="store.enablePlugin(settings.plugin.plugin_id)" button-type="btn-outline-light">Disable Plugin</Button>
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
        const pluginId = Number(router.currentRoute.value.params.id)

        // Find the parent plugin from selectedConversation
        const selectedPlugin = store.selectedConversation.plugins.find(
            (plugin) => plugin.id === pluginId
        );

        if (selectedPlugin) {
            const functions = [];

            // Iterate over functions array
            selectedPlugin.functions.forEach(functionItem => {
                // Add the function name, metadata, display name, and description to the array
                functions.push({
                    functionName: functionItem.name,
                    displayName: functionItem.metadata.display_name,
                    description: functionItem.metadata.description,
                    type: functionItem.type === 'snippet' ? 'snippet' : 'tool',
                    functionSettings: functionItem.settings,
                });
            });

            return {
                plugin: selectedPlugin,
                functions,
            };
        }
    }
});

const saveSettings = async () => {
    const updatedSettings = {};

    for (const functionSettings of settings.value.functions) {
        // Gather the updated settings values
        updatedSettings[functionSettings.functionName] = {};
        for (const key in functionSettings.functionSettings) {
            updatedSettings[functionSettings.functionName][key] = functionSettings.functionSettings[key].value;
        }
    }

    const pluginId = Number(router.currentRoute.value.params.id)

    try {
        await api.updatePluginSettings(pluginId, updatedSettings);
    } catch (error) {
        console.error('Failed to update plugin settings:', error);
    }
};

const clearPluginData = async () => {
    const pluginId = Number(router.currentRoute.value.params.id);
    await api.clearPluginData(pluginId);
    store.newNotification('Plugin data cleared');
}

function formatName(name) {
    return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}
</script>