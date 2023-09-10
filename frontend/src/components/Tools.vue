<template>
    <div id="alt-window" class="font-mulish flex flex-col gap-3 w-full overflow-y-scroll">
        <div class="p-8 pt-[5.5rem] max-w-3xl">
            <SectionHeading section-name="Add Tools" @on-click="onBackButtonClick" />
            <div class="mt-6 space-y-4">
                <template v-for="tool in filteredTools" :key="tool.name">
                    <Card>
                        <template v-slot:icon>
                            <div class="flex items-center justify-center h-9 w-9 rounded shadow bg-neutral-100 mt-0.5">
                                <Icon icon="mdi:function" class="text-nearyyellow-100 w-5 h-5" />
                            </div>
                        </template>
                        <div class="leading-7">
                            <div class="text-field-default-foreground text-sm font-medium">{{ tool.display_name }}</div>
                            <div class="text-sm text-nearygray-400">{{ tool.description }}</div>
                        </div>
                        <template v-slot:button>
                            <Icon icon="heroicons:plus" @click="addTool(tool.name)"
                            class="cursor-pointer shrink-0 ml-4 mr-2 w-5 h-5" />
                        </template>
                    </Card>
                </template>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAppStore } from '@/store/index.js';
import SectionHeading from './common/SectionHeading.vue'
import Card from './common/Card.vue'
import api from '../services/apiService';
import { Icon } from '@iconify/vue';

const store = useAppStore();
const router = useRouter();

const filteredTools = computed(() => {
    if (store.selectedConversation && store.selectedConversation.plugins && store.availablePlugins) {
        let selectedTools = [];

        store.selectedConversation.plugins.forEach(plugin => {
            if (plugin.functions.tools) {
                Object.entries(plugin.functions.tools).forEach(([name, details]) => {
                    selectedTools.push(name);
                });
            }
        });

        let tools = [];

        store.availablePlugins.forEach(plugin => {
            if (plugin.is_enabled && plugin.functions.tools) {
                Object.entries(plugin.functions.tools).forEach(([name, details]) => {
                    if (!selectedTools.includes(name)) {
                        tools.push({
                            name: name,
                            display_name: details.display_name,
                            description: details.description
                        });
                    }
                });
            }
        });

        return tools;
    }
    return [];
});

const addTool = (toolName) => {
    const availablePlugin = store.availablePlugins.find(plugin => {
        return plugin.functions.tools && Object.keys(plugin.functions.tools).includes(toolName);
    });

    if (availablePlugin) {
        const pluginInstance = store.selectedConversation.plugins.find(plugin => plugin.name === availablePlugin.name);

        if (pluginInstance) {
            pluginInstance.functions['tools'][toolName] = availablePlugin.functions['tools'][toolName];
        }
        store.updateConversation(store.selectedConversation);
    }
};
const onBackButtonClick = () => {
    router.go(-1);
};

</script>