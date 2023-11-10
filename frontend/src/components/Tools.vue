<template>
    <div id="alt-window" class="font-mulish flex flex-col gap-3 max-w-full overflow-y-scroll">
        <div class="p-8 pt-[5.5rem] max-w-3xl">
            <div class="flex items-center justify-between">
                <SectionHeading section-name="Add Tools" @on-click="onBackButtonClick" />
                <Button @buttonClick="router.push('/setup')" buttonSize="small" buttonType="btn-outline-light"
                    class="flex items-center gap-1">
                    Manage Plugins
                </Button>
            </div>
            <div class="font-bold text-nearylight-200 mt-12">
                Available Tools
            </div>
            <div class="mt-6 space-y-4">
                <template v-for="tool in filteredTools" :key="tool.name">
                    <Card v-if="!tool.unconnected_integrations.length > 0">
                        <template v-slot:icon>
                            <div class="flex items-center justify-center h-9 w-9 rounded shadow bg-neutral-100 mt-0.5">
                                <Icon :icon="tool.plugin_icon ? tool.plugin_icon : 'mdi:function'"
                                    class="text-nearyyellow-200/90 w-5 h-5" />
                            </div>
                        </template>
                        <div class="leading-7">
                            <div class="text-field-default-foreground text-sm font-medium">{{ tool.display_name }}</div>
                            <div class="text-sm text-nearygray-400">{{ tool.description }}</div>
                        </div>
                        <template v-slot:button>
                            <Icon icon="heroicons:plus" @click="addTool(tool)"
                                class="cursor-pointer shrink-0 ml-4 mr-2 w-6 h-6" />
                        </template>
                    </Card>
                </template>
            </div>
            <div class="font-bold text-nearylight-200 mt-12">
                Disabled Tools
            </div>
            <div class="mt-6 space-y-4">
                <template v-for="tool in filteredTools" :key="tool.name">
                    <Card v-if="tool.unconnected_integrations.length > 0">
                        <template v-slot:icon>
                            <div class="flex items-center justify-center h-9 w-9 rounded shadow bg-neutral-100 mt-0.5">
                                <Icon :icon="tool.plugin_icon ? tool.plugin_icon : 'mdi:note-text-outline'"
                                    class="text-field-default-foreground w-5 h-5" />
                            </div>
                        </template>
                        <div class="leading-7">
                            <div class="text-field-default-foreground text-sm font-medium">{{ tool.display_name }}</div>
                            <div class="text-sm text-nearygray-400 font-normal">Requires <span @click="router.push('/setup')" class="cursor-pointer font-medium text-nearygray-300 underline">{{ tool.unconnected_integrations.join(', ') }}</span> integration</div>
                        </div>
                        <template v-slot:button>
                            <Icon icon="heroicons:exclamation-circle" class="text-nearygray-300 shrink-0 ml-4 mr-2 w-6 h-6" />
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
import Button from './common/Button.vue'
import { Icon } from '@iconify/vue';

const store = useAppStore();
const router = useRouter();

const filteredTools = computed(() => {
    if (store.selectedConversation && store.selectedConversation.plugins && store.availablePlugins) {
        let selectedTools = store.getEnabledFunctions('tool').map(func => func.name)

        let tools = [];

        store.availablePlugins.forEach(plugin => {
            if (plugin.is_enabled) {
                plugin.functions.forEach(func => {
                    if (func.type === 'tool' && !selectedTools.includes(func.name)) {
                        let unconnected_integrations = [];
                        if (func.integrations) {
                            func.integrations.forEach(integration => {
                                if (integration.instances.length == 0) {
                                    unconnected_integrations.push(integration.display_name);
                                }
                            });
                        }

                        tools.push({
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
        return tools;
    }
    return [];
});


const addTool = (tool) => {
    let functionData = {
        "function_name": tool.name,
        "plugin_name": tool.plugin_name
    }
    store.addConversationFunction(functionData, store.selectedConversation.id);
}

const onBackButtonClick = () => {
    router.go(-1);
};

</script>