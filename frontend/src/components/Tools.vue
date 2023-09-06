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
            Object.entries(plugin.functions).forEach(([name, details]) => {
                if (details.type === 'tool') {
                    selectedTools.push(name);
                }
            });
        });

        let tools = [];

        store.availablePlugins.forEach(plugin => {
            Object.entries(plugin.functions).forEach(([name, details]) => {
                if (details.type === 'tool' && !selectedTools.includes(name)) {
                    tools.push({
                        name: name,
                        display_name: details.display_name,
                        description: details.description
                    });
                }
            });
        });

        return tools;
    }
    return [];
});

const addTool = (toolName) => {
    const availablePlugin = store.availablePlugins.find(plugin => {
        return Object.keys(plugin.functions).includes(toolName);
    });

    if (availablePlugin) {
        const existingPlugin = store.selectedConversation.plugins.find(plugin => plugin.name === availablePlugin.name);

        if (existingPlugin) {
            existingPlugin.functions[toolName] = availablePlugin.functions[toolName];
        } else {
            const newPlugin = {
                id: null,
                name: availablePlugin.name,
                conversation_id: store.selectedConversation.id,
                data: null,
                functions: {
                    [toolName]: availablePlugin.functions[toolName]
                },
                metadata: availablePlugin.metadata
            };

            store.selectedConversation.plugins.push(newPlugin);
        }
        store.updateConversation(store.selectedConversation);
    }
};

const onBackButtonClick = () => {
    router.go(-1);
};

</script>