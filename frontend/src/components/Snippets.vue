<template>
    <div id="alt-window" class="font-mulish flex flex-col gap-3 max-w-full overflow-y-scroll">
        <div class="p-8 pt-[5.5rem] max-w-3xl">
            <SectionHeading section-name="Add Snippets" @on-click="onBackButtonClick" />
            <div class="mt-6 space-y-4">
                <template v-for="snippet in filteredSnippets" :key="snippet.name">
                    <Card>
                        <template v-slot:icon>
                            <div class="flex items-center justify-center h-9 w-9 rounded shadow bg-neutral-100 mt-0.5">
                                <Icon icon="mdi:note-text-outline" class="text-nearycyan-300 w-5 h-5" />
                            </div>
                        </template>
                        <div class="leading-7">
                            <div class="text-field-default-foreground text-sm font-medium">{{ snippet.display_name }}</div>
                            <div class="text-sm text-nearygray-400">{{ snippet.description }}</div>
                        </div>
                        <template v-slot:button>
                            <Icon icon="heroicons:plus" @click="addSnippet(snippet.name)"
                                class="cursor-pointer shrink-0 ml-4 mr-2 w-5 h-5" />
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
import Card from './common/Card.vue'
import { Icon } from '@iconify/vue';

const store = useAppStore();
const router = useRouter();

const filteredSnippets = computed(() => {
    if (store.selectedConversation && store.selectedConversation.plugins && store.availablePlugins) {
        let selectedSnippets = [];

        store.selectedConversation.plugins.forEach(plugin => {
            if (plugin.functions.snippets) {
                Object.entries(plugin.functions.snippets).forEach(([name, details]) => {
                    selectedSnippets.push(name);
                });
            }
        });

        let snippets = [];

        store.availablePlugins.forEach(plugin => {
            if (plugin.is_enabled && plugin.functions.snippets) {
                Object.entries(plugin.functions.snippets).forEach(([name, details]) => {
                    if (!selectedSnippets.includes(name)) {
                        snippets.push({
                            name: name,
                            plugin_name: plugin.display_name,
                            display_name: details.display_name,
                            description: details.description
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
    const availablePlugin = store.availablePlugins.find(plugin => {
        return plugin.functions.snippets && Object.keys(plugin.functions.snippets).includes(snippetName);
    });

    if (availablePlugin) {
        let pluginInstance = store.selectedConversation.plugins.find(plugin => plugin.name === availablePlugin.name);

        if (!pluginInstance) {
            pluginInstance = {
                "plugin_id": availablePlugin.id,
                "conversation_id": store.selectedConversation.id,
                "name": availablePlugin.name,
                "display_name": availablePlugin.display_name,
                "description": availablePlugin.description,
                "author": availablePlugin.author,
                "url": availablePlugin.url,
                "version": availablePlugin.version,
                "data": null,
                "settings": availablePlugin.settings,
                "functions": {"snippets": {}},
                "is_enabled": true
            };
            store.selectedConversation.plugins.push(pluginInstance);
        }
        pluginInstance.functions['snippets'][snippetName] = availablePlugin.functions['snippets'][snippetName];
        store.updateConversation(store.selectedConversation);
    }
}

const onBackButtonClick = () => {
    router.go(-1);
};

</script>