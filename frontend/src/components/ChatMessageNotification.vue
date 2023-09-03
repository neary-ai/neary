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
            <div class="flex flex-col min-w-0 pt-[0.75rem]">
                <div class="overflow-x-scroll min-w-0 max-w-full text-slate-300/80">
                    <div
                        class="flex flex-col bg-nearylight-400/20 border-nearylight-400/70 border rounded p-5 max-w-2xl mb-6">
                        <div class="flex items-start justify-between gap-8">
                            <div class="flex items-start justify-start gap-3.5">
                                <InformationCircleIcon
                                    class="flex-shrink-0 text-nearylight-200 flex items-center justify-center w-5 h-5" />
                                <div class="flex flex-col items-start justify-start">
                                    <div class="text-white font-bold text-sm">
                                        Approval Needed
                                    </div>
                                    <div class="flex">
                                    <div class="mt-2.5 text-sm font-medium text-nearygray-100"
                                        v-html="renderMarkdown(content.content)"></div>
                                    </div>
                                    <div v-if="content.args" class="flex items-center text-sm mb-4 bg-slate-200 py-1.5 px-3 rounded text-nearyblue-100">
                                        <div v-if="!showArgs" @click="showToolArgs()" class="flex items-center">
                                            <div>Show details</div> <ChevronDownIcon class="ml-0.5 w-5 h-5" />
                                        </div>
                                        <div v-else class="prose-base prose-slate text-nearyblue-100 p-1" v-html="renderMarkdown(content.args)"></div>
                                    </div>
                                    <div
                                        class="text-sm font-medium text-nearygray-200 flex items-center justify-between w-full mt-2">
                                        <div class="flex gap-3">
                                            <div v-if="!actionResponseLoading" class="flex gap-3 items-center">
                                                <button v-for="(action, index) in message.actions" :key="index"
                                                    @click="handleActionButton(action, message.id)"
                                                    class="text-nearyblue-300 bg-nearylight-200 rounded-md px-2.5 py-1.5 text-sm font-semibold shadow hover:bg-opacity-80">
                                                    {{ action.label }}
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
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