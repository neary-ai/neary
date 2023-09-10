<template>
    <div class="font-bold text-nearylight-200 mt-12">
        Enabled Plugins
    </div>
    <div class="mt-6 space-y-4">
        <template v-for="plugin in store.availablePlugins">
            <Card v-if="plugin.is_enabled" :key="plugin.name" padding="p-6 sm:p-5" flex="items-start" outerFlex='flex-col items-start sm:flex-row sm:items-center justify-between gap-3'>
                <template v-slot:icon>
                    <div class="hidden sm:flex items-center justify-center h-9 w-9 rounded shadow bg-nearycyan-300/50 mt-0.5 mr-4">
                        <Icon :icon="plugin.icon ? plugin.icon : 'mdi:extension-outline'" class="text-white w-6 h-6" />
                    </div>
                </template>
                <div class="leading-7 pr-8">
                    <div class="text-field-default-foreground text-sm font-semibold">{{ plugin.display_name }}</div>
                    <div v-if="plugin.url" class="text-xs text-nearygray-500">By <a :href="plugin.url" class="underline"
                            target="_blank">{{ plugin.author }}</a></div>
                    <div v-else class="text-xs text-nearygray-300">By {{ plugin.author }}</div>
                    <div class="text-sm font-medium text-nearygray-300 mt-4">{{ plugin.description }}</div>
                </div>
                <template v-slot:button>
                    <Button @buttonClick="store.disablePlugin(plugin.id)" buttonType="btn-outline-light"
                        buttonSize="medium" class="mt-2 sm:mt-0">
                        <div class="flex items-center">
                            <Icon icon="heroicons:x-mark-20-solid" class="w-5 h-5 mr-1" />
                            <div>Disable</div>
                        </div>
                    </Button>
                </template>
            </Card>
        </template>
    </div>
    <div class="font-bold text-nearylight-200 mt-12">
        Available Plugins
    </div>
    <div class="mt-6 space-y-4">
        <template v-for="plugin in store.availablePlugins">
            <Card v-if="!plugin.is_enabled" :key="plugin.name" padding="px-6 py-6" flex="items-start" outerFlex='flex-col items-start sm:flex-row sm:items-center justify-between gap-3'>
                <template v-slot:icon>
                    <div class="hidden sm:flex items-center justify-center h-9 w-9 rounded shadow bg-nearycyan-300/50 mt-0.5 mr-4">
                        <Icon :icon="plugin.icon ? plugin.icon : 'mdi:extension-outline'" class="text-white w-6 h-6" />
                    </div>
                </template>
                <div class="leading-7 pr-8">
                    <div class="text-field-default-foreground text-sm font-semibold">{{ plugin.display_name }}</div>
                    <div v-if="plugin.url" class="text-xs text-nearygray-500">By <a :href="plugin.url" class="underline"
                            target="_blank">{{ plugin.author }}</a></div>
                    <div v-else class="text-xs text-nearygray-300">By {{ plugin.author }}</div>
                    <div class="text-sm font-medium text-nearygray-300 mt-4">{{ plugin.description }}</div>
                </div>
                <template v-slot:button>
                    <Button @buttonClick="store.enablePlugin(plugin.id)" buttonType="btn-light"
                        buttonSize="medium" class="mt-2 sm:mt-0">
                        <div class="flex items-center">
                            <Icon icon="heroicons:plus-20-solid" class="w-5 h-5 mr-1" />
                            <div>Enable</div>
                        </div>
                    </Button>
                </template>
            </Card>
        </template>
    </div>
</template>

<script setup>
import { useAppStore } from '@/store/index.js';
import Card from './common/Card.vue'
import Button from './common/Button.vue'
import { Icon } from '@iconify/vue';

const store = useAppStore();

</script>