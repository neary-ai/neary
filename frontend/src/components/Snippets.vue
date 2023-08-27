<template>
    <div id="alt-window" class="font-mulish flex flex-col gap-3 max-w-3xl overflow-y-scroll">
        <div class="p-8 pt-[5.5rem]">
            <SectionHeading section-name="Add Snippets" @on-click="onBackButtonClick" />
            <div class="mt-6 space-y-4">
                <template v-for="snippet in filteredSnippets" :key="snippet.name">
                    <Card>
                        <template v-slot:icon>
                            <div class="flex items-center justify-center h-9 w-9 rounded shadow bg-neutral-100 mt-0.5">
                                <Icon icon="mdi:note-text-outline" class="text-nearylight-300 w-5 h-5" />
                            </div>
                        </template>
                        <div class="leading-7">
                            <div class="text-field-default-foreground text-sm font-medium">{{ snippet.display_name }}</div>
                            <div class="text-sm text-nearygray-400">{{ snippet.description }}</div>
                        </div>
                        <template v-slot:button>
                            <Icon icon="heroicons:plus" @click="addSnippet(snippet)"
                                class="cursor-pointer shrink-0 ml-4 w-5 h-5" />
                        </template>
                    </Card>
                </template>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAppStore } from '@/store/index.js';
import SectionHeading from './common/SectionHeading.vue'
import Card from './common/Card.vue'
import api from '../services/apiService';
import { Icon } from '@iconify/vue';

const store = useAppStore();
const router = useRouter();

const availableSnippets = ref([])

const filteredSnippets = computed(() => {
    if (store.selectedConversation && store.selectedConversation.plugins) {
        const activePluginNames = store.selectedConversation.plugins.map(plugin => plugin.name);
        return availableSnippets.value.filter(snippet => !activePluginNames.includes(snippet.name));
    }
    return []
});

const addSnippet = async (snippet) => {
    store.selectedConversation.plugins.push(snippet);
    await store.updateConversation(store.selectedConversation)
}

const onBackButtonClick = () => {
    router.go(-1);
};


watch(() => store.selectedConversationId, async (newId) => {
    if (newId) {
        availableSnippets.value = await api.getAvailableSnippets(newId);
    }
}, { immediate: true });

</script>