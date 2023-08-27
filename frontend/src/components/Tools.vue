<template>
    <div id="alt-window" class="font-mulish flex flex-col gap-3 max-w-3xl overflow-y-scroll">
        <div class="p-8 pt-[5.5rem]">
            <SectionHeading section-name="Add Tools" @on-click="onBackButtonClick" />
            <div class="mt-6 space-y-4">
                <template v-for="tool in filteredTools" :key="tool.name">
                    <Card>
                        <template v-slot:icon>
                            <div class="flex items-center justify-center h-9 w-9 rounded shadow bg-neutral-100 mt-0.5">
                                <Icon icon="mdi:function" class="text-nearyyellow-200 w-5 h-5" />
                            </div>
                        </template>
                        <div class="leading-7">
                            <div class="text-field-default-foreground text-sm font-medium">{{ tool.display_name }}</div>
                            <div class="text-sm text-nearygray-400">{{ tool.description }}</div>
                        </div>
                        <template v-slot:button>
                            <Icon icon="heroicons:plus" @click="addTool(tool)"
                                class="cursor-pointer shrink-0 ml-4 w-5 h-5" />
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

const availableTools = ref([])

const filteredTools = computed(() => {
    if (store.selectedConversation && store.selectedConversation.plugins) {
        const activePluginNames = store.selectedConversation.plugins.map(plugin => plugin.name);
        return availableTools.value.filter(tool => !activePluginNames.includes(tool.name));
    }
    return []
});

const addTool = async (tool) => {
    store.selectedConversation.plugins.push(tool);
    await store.updateConversation(store.selectedConversation)
}

const onBackButtonClick = () => {
    router.go(-1);
};

watch(() => store.selectedConversationId, async (newId) => {
    if (newId) {
        availableTools.value = await api.getAvailableTools(newId);
    }
}, { immediate: true });

</script>