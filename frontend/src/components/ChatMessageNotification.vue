<template>
    <div class="flex self-center gap-6 items-start leading-7 px-8 py-4 bg-nearyblue-50 m-4 rounded-lg">
        <InformationCircleIcon class="flex-shrink-0 text-nearygray-50 flex items-center justify-center w-7 h-7 mt-4" />
        <div class="flex flex-col min-w-0 pr-8">
            <div class="flex items-center">
                <div class="flex items-center overflow-x-scroll text-nearygray-50 min-w-0">
                    <div class="pt-4 prose prose-invert" v-html="renderMarkdown(message.content)"></div>
                </div>
            </div>
            <div v-if="!actionResponseLoading" class="flex gap-3 items-center">
                <div v-if="isActionCompleted"
                    class="text-sm text-nearyblue-100 bg-slate-400 shadow px-4 py-1.5 mb-4 mt-8 rounded-full font-medium flex items-center">
                    {{ isActionCompleted }}
                </div>
                <button v-else v-for="(action, index) in message.actions" :key="index"
                    @click="handleActionButton(action, message.id)"
                    :disabled="actionCompleted[action.data.request_id] || actionResponseLoading"
                    class="text-nearyblue-100 bg-slate-400 rounded-md px-3.5 py-2 mb-4 mt-8 text-sm shadow hover:bg-opacity-80"
                    :class="[actionCompleted[action.data.request_id] ? 'text-slate-600' : 'text-nearyblue-500', actionResponseLoading ? '' : '']">
                    {{ action.label }}
                </button>
            </div>
            <Loading v-if="actionResponseLoading" textColor="text-nearygray-300" class="my-4 -ml-1" />
        </div>
    </div>
</template>
  
<script setup>
import { onMounted, ref, watch, nextTick, computed } from 'vue';
import MarkdownIt from 'markdown-it';
import DOMPurify from 'dompurify';
import ClipboardJS from 'clipboard';
import Prism from 'prismjs';
import 'prismjs/components/prism-python';
import 'prismjs/themes/prism-tomorrow.css';
import { InformationCircleIcon, } from '@heroicons/vue/24/outline';
import { useAppStore } from '@/store/index.js';
import api from '@/services/apiService';
import Loading from '@/components/common/Loading.vue';

const store = useAppStore();

const props = defineProps({
    message: Object,
});

let actionCompleted = ref({});
let actionResponseLoading = ref(false);

let isActionCompleted = computed(() => {
    const completedAction = Object.values(actionCompleted.value).find(status => status !== 'error');
    return completedAction || '';
});

const handleActionButton = async (action, messageId) => {
    if (action.type === 'link') {
        window.open(action.data.url, '_blank');
    } else {
        actionResponseLoading.value = true;
        try {
            const response = await api.postActionResponse(action, messageId);
            if (response.data.detail !== 'error') {
                actionCompleted.value = { ...actionCompleted.value, [action.data.request_id]: response.data.detail };
            }
        } catch (error) {
            console.error('Error sending action response:', error);
        }
        actionResponseLoading.value = false;
    }
};

const renderMarkdown = (markdownText) => {
    if (markdownText == '') {
        return markdownText
    }

    const md = new MarkdownIt();

    let html = md.render(markdownText);
    html = html.replace(/^<p>|<\/p>$/g, '');
    const sanitizedHtml = DOMPurify.sanitize(html);
    return sanitizedHtml;
}

</script>