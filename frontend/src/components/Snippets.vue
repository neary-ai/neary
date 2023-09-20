<template>
    <div id="alt-window" class="font-mulish flex flex-col gap-3 max-w-full overflow-y-scroll">
        <div class="p-8 pt-[5.5rem] max-w-3xl">
            <div class="flex items-center justify-between">
                <SectionHeading section-name="Add Snippets" @on-click="onBackButtonClick" />
                <Button @buttonClick="router.push('/setup')" buttonSize="small" buttonType="btn-outline-light"
                    class="flex items-center gap-1">
                    Manage Plugins
                </Button>
            </div>
            <div class="font-bold text-nearylight-200 mt-12">
                Available Snippets
            </div>
            <div class="mt-6 space-y-4">
                <template v-for="snippet in filteredSnippets" :key="snippet.name">
                    <Card v-if="!snippet.unconnected_integrations.length > 0">
                        <template v-slot:icon>
                            <div class="flex items-center justify-center h-9 w-9 rounded shadow bg-neutral-100 mt-0.5">
                                <Icon :icon="snippet.plugin_icon ? snippet.plugin_icon : 'mdi:note-text-outline'"
                                    class="text-nearycyan-400 w-5 h-5" />
                            </div>
                        </template>
                        <div class="leading-7">
                            <div class="text-field-default-foreground text-sm font-medium">{{ snippet.display_name }}</div>
                            <div class="text-sm text-nearygray-400">{{ snippet.description }}</div>
                        </div>
                        <template v-slot:button>
                            <Icon icon="heroicons:plus" @click="addSnippet(snippet.name)"
                                class="cursor-pointer shrink-0 ml-4 mr-2 w-6 h-6" />
                        </template>
                    </Card>
                </template>
            </div>
            <div class="font-bold text-nearylight-200 mt-12">
                Disabled Snippets
            </div>
            <div class="mt-6 space-y-4">
                <template v-for="snippet in filteredSnippets" :key="snippet.name">
                    <Card v-if="snippet.unconnected_integrations.length > 0">
                        <template v-slot:icon>
                            <div class="flex items-center justify-center h-9 w-9 rounded shadow bg-neutral-100 mt-0.5">
                                <Icon :icon="snippet.plugin_icon ? snippet.plugin_icon : 'mdi:note-text-outline'"
                                    class="text-field-default-foreground w-5 h-5" />
                            </div>
                        </template>
                        <div class="leading-7">
                            <div class="text-field-default-foreground text-sm font-medium">{{ snippet.display_name }}</div>
                            <div class="text-sm text-nearygray-400 font-normal">Requires <span @click="router.push('/setup')" class="cursor-pointer font-medium text-nearygray-300 underline">{{ snippet.unconnected_integrations.join(', ')
                                    }}</span> integration</div>
                        </div>
                        <template v-slot:button>
                            <Icon icon="heroicons:exclamation-circle"
                                class="text-nearygray-300 shrink-0 ml-4 mr-2 w-6 h-6" />
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
import { useAppStore } from '@/store/index.js';
import SectionHeading from './common/SectionHeading.vue'
import Button from './common/Button.vue'
import Card from './common/Card.vue'
import { Icon } from '@iconify/vue';

const store = useAppStore();
const router = useRouter();

const filteredSnippets = computed(() => {
    if (store.selectedConversation && store.selectedConversation.plugins && store.availablePlugins) {
        let selectedSnippets = [];

        store.selectedConversation.plugins.forEach(plugin => {
            plugin.functions.forEach(func => {
                if (func.type === 'snippet') {
                    selectedSnippets.push(func.name);
                }
            });
        });

        let snippets = [];

        store.availablePlugins.forEach(plugin => {
            if (plugin.is_enabled) {
                plugin.functions.forEach(func => {
                    if (func.type === 'snippet' && !selectedSnippets.includes(func.name)) {
                        let unconnected_integrations = [];
                        // Iterate over the integrations array
                        if (func.integrations) {
                            func.integrations.forEach(integration => {
                                // If connected is false, push the name to the unconnected_integrations array
                                if (!integration.connected) {
                                    unconnected_integrations.push(integration.name);
                                }
                            });
                        }

                        snippets.push({
                            name: func.name,
                            plugin_name: plugin.display_name,
                            plugin_icon: plugin.icon,
                            display_name: func.metadata.display_name,
                            description: func.metadata.description,
                            unconnected_integrations: unconnected_integrations
                        });
                    }
                });
            }
        });
        return snippets;
    }
    return [];
});

const addSnippet = (snippetName) => {
    let availablePlugin;
    let availableFunction;

    store.availablePlugins.forEach(plugin => {
        plugin.functions.forEach(func => {
            if (func.type === 'snippet' && func.name === snippetName) {
                availablePlugin = plugin;
                availableFunction = func;
            }
        });
    });

    if (availablePlugin && availableFunction) {
        let pluginInstance = store.selectedConversation.plugins.find(plugin => plugin.name === availablePlugin.name);

        if (!pluginInstance) {
            pluginInstance = {
                "plugin_id": availablePlugin.id,
                "conversation_id": store.selectedConversation.id,
                "name": availablePlugin.name,
                "display_name": availablePlugin.display_name,
                "description": availablePlugin.description,
                "icon": availablePlugin.icon,
                "author": availablePlugin.author,
                "url": availablePlugin.url,
                "version": availablePlugin.version,
                "data": null,
                "settings": availablePlugin.settings,
                "functions": [],
                "is_enabled": true
            };
            store.selectedConversation.plugins.push(pluginInstance);
        }

        const functionExists = pluginInstance.functions.find(func => func.name === availableFunction.name);
        
        if (!functionExists) {
            pluginInstance.functions.push(availableFunction);
        }

        store.updateConversation(store.selectedConversation);
    }
}

const onBackButtonClick = () => {
    router.go(-1);
};

</script>