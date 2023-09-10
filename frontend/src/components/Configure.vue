<template>
    <div id="alt-window" class="font-mulish flex flex-col gap-3 w-full overflow-y-scroll">
        <div class="p-8 pt-[5.5rem] max-w-3xl">
            <SectionHeading section-name="Settings" @on-click="onBackButtonClick" />
            <div class="mt-3">
                <div class="block">
                    <div class="border-b border-field-divide">
                        <nav class="-mb-px flex space-x-8" aria-label="Tabs">
                            <a href="#" @click="activeTab = 'plugins'" :class="[activeTab == 'plugins' ? 'border-nearycyan-300 text-nearycyan-400 font-semibold' : 'text-nearylight-200 border-transparent font-medium', 'whitespace-nowrap border-b-2 py-4 px-1 text-sm']">Plugins</a>
                            <a href="#" @click="activeTab = 'integrations'" :class="[activeTab == 'integrations' ? 'border-nearycyan-300 text-nearycyan-400 font-semibold' : 'text-nearylight-200 border-transparent font-medium', 'whitespace-nowrap border-b-2 py-4 px-1 text-sm']">Integrations</a>
                        </nav>
                    </div>
                </div>
                <Plugins v-if="activeTab == 'plugins'" />
                <Integrations v-if="activeTab == 'integrations'" />
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAppStore } from '@/store/index.js';
import SectionHeading from './common/SectionHeading.vue'
import api from '../services/apiService';
import { Icon } from '@iconify/vue';
import Integrations from './Integrations.vue';
import Plugins from './Plugins.vue';

const store = useAppStore();
const router = useRouter();

const activeTab = ref('plugins')

const onBackButtonClick = () => {
    router.go(-1);
};

</script>