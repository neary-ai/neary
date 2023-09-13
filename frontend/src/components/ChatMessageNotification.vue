<template>
    <div ref="messageContainer"
        class="flex justify-start items-start w-full prose prose-invert max-w-none leading-7 mr-auto text-gray-400 pt-6 pb-3.5 pl-6 pr-8 transition-all duration-50 delay-0"
        :class="message.is_archived ? 'pattern-diagonal-lines pattern-nearyblue-300 pattern-bg-nearyblue-400 pattern-size-6 pattern-opacity-80' : 'bg-nearyblue-400'">
        <div class="flex w-full items-start">
            <div class="py-3">
                <div
                    class="not-prose flex-shrink-0 font-bold rounded h-7 w-7 flex items-center justify-center mr-5 text-sm bg-nearypink-300/20 text-nearypink-200">
                    N
                </div>
            </div>
            <div
                class="overflow-x-scroll min-w-0 flex gap-3 max-w-full text-slate-300/80 bg-nearylight-400/20 border-nearylight-400/70 border rounded p-5 pr-10 mb-6">
                <InformationCircleIcon class="flex-shrink-0 text-nearylight-200 flex items-center justify-center w-5 h-5" />
                <div class="flex flex-col">
                    <div class="flex items-stretch justify-start mb-4">
                        <div class="flex items-center justify-between gap-4">
                            <div class="flex flex-col items-start justify-start">
                                <div class="text-white font-bold text-sm">
                                    Approval Needed
                                </div>
                                <div class="flex">
                                    <div class="mt-3 -mb-2 text-sm font-medium text-nearygray-100" v-html="renderMarkdown(content.content)"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div v-if="showArgs" class="prose prose-invert text-nearylight-100 w-full mb-8 " v-html="renderMarkdown(content.args)"></div>
                    <div class="text-sm font-medium text-nearygray-200 flex items-center">
                        <div v-if="!actionResponseLoading" class="flex gap-3">
                            <button v-for="(action, index) in message.actions" :key="index"
                                @click="handleActionButton(action, message.id)"
                                class="bg-nearylight-200 text-nearyblue-400 px-2 py-1.5 rounded text-sm font-semibold">
                                {{ action.label }}
                            </button>
                        </div>
                        <div v-if="content.args" class="flex ml-3.5">
                            <div v-if="!showArgs" @click="showToolArgs()"
                                class="cursor-pointer text-sm text-nearygray-100 font-medium flex">
                                <div>or <span class="font-semibold text-nearygray-50 inline-block ml-1">view details</span></div>
                                <ChevronDownIcon class="ml-0.5 w-5 h-5 font-semibold" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { Icon } from '@iconify/vue';
import { ref, computed } from 'vue';
import MarkdownIt from 'markdown-it';
import DOMPurify from 'dompurify';

import 'prismjs/components/prism-python';
import 'prismjs/themes/prism-tomorrow.css';
import { ChevronDownIcon, InformationCircleIcon, } from '@heroicons/vue/20/solid';
import { scrollToBottom } from '../services/scrollFunction.js';
import { useAppStore } from '@/store/index.js';
import api from '@/services/apiService';

const store = useAppStore();

const props = defineProps({
    message: Object,
});

let actionResponseLoading = ref(false);
let showArgs = ref(false);

const content = computed(() => {
    if (props.message) {
        const parsedContent = parseArguments(props.message.content);
        return parsedContent;
    }
})

const parseArguments = (content) => {
    const argsRegex = /<<args>>(.*?)<<\/args>>/gs;
    let match;
    let args = '';

    while ((match = argsRegex.exec(content)) !== null) {
        args += match[1];
        content = content.replace(match[0], '');
    }

    return { content, args };
}

const handleActionButton = async (action, messageId) => {
    if (action.type === 'link') {
        window.open(action.data.url, '_blank');
    } else {
        actionResponseLoading.value = true;
        try {
            const response = await api.postActionResponse(action, messageId);
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

const showToolArgs = () => {
    showArgs.value = true;
    scrollToBottom(store.highlighting, true);
}

</script>