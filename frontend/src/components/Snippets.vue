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
                            <Icon icon="heroicons:plus" @click="addSnippet(snippet)"
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
        let selectedSnippets = store.getEnabledFunctions('snippet').map(func => func.name)

        let snippets = [];

        store.availablePlugins.forEach(plugin => {
            if (plugin.is_enabled) {
                plugin.functions.forEach(func => {
                    if (func.type === 'snippet' && !selectedSnippets.includes(func.name)) {
                        let unconnected_integrations = [];
                        if (func.integrations) {
                            func.integrations.forEach(integration => {
                                if (integration.instances.length == 0) {
                                    unconnected_integrations.push(integration.display_name);
                                }
                            });
                        }

                        snippets.push({
                            name: func.name,
                            display_name: func.display_name,
                            description: func.description,
                            plugin_name: plugin.name,
                            plugin_display_name: plugin.display_name,
                            plugin_icon: plugin.icon,
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

const addSnippet = (snippet) => {
    let functionData = {
        "function_name": snippet.name,
        "plugin_name": snippet.plugin_name
    }
    store.addConversationFunction(functionData, store.selectedConversation.id);
}

const onBackButtonClick = () => {
    router.go(-1);
};

</script>