<template>
    <div ref="messageContainer" v-if="convertedContent.text != ''"
        class="flex justify-start items-start w-full prose prose-invert max-w-none leading-7 mr-auto bg-nearyblue-400 text-gray-400 pt-6 pb-3.5 pl-6 pr-8 transition-all duration-50 delay-0">
        <div class="flex w-full items-start">
            <div class="py-3">
                <div class="not-prose flex-shrink-0 font-bold text-base rounded h-7 w-7 flex items-center justify-center mr-5 text-sm"
                    :class="message.is_archived ? 'bg-slate-700 text-slate-400' : 'bg-nearypink-300/20 text-nearypink-200'">
                    N
                </div>
            </div>
            <div class="flex flex-col min-w-0 pt-[0.75rem]">
                <div class="overflow-x-scroll min-w-0 max-w-full"
                    :class="[message.is_archived ? 'text-slate-300/60' : 'text-slate-300/80']"
                    v-html="convertedContent.text"></div>
                <div v-if="convertedContent.toolName != ''" class="text-sm w-full">
                    <div class="flex items-center justify-start w-full flex-grow pb-3">
                        <div class="inline-flex gap-1 text-nearycyan-300">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
                                <path fill-rule="evenodd"
                                    d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z"
                                    clip-rule="evenodd" />
                            </svg>
                            {{ convertedContent.toolName }}
                        </div>
                    </div>
                </div>
                <div v-if="uniqueSources && uniqueSources.length > 0"
                    class="text-slate-400/80 text-sm py-4 mt-4 border-t border-slate-700">
                    Sources: {{ uniqueSources.join(', ') }}
                </div>
            </div>
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
import { useAppStore } from '@/store/index.js';

const store = useAppStore();

const props = defineProps({
    message: Object,
    chatWindowHeight: Number,
});

let chatWindowHeight = ref(props.chatWindowHeight);
let messageContainer = ref(null);
let isExpanded = ref(false);

const uniqueSources = computed(() => {
    if (props.message.metadata) {
        let documentsObject = props.message.metadata.find(item => item.documents);
        if (documentsObject) {
            let sources = documentsObject.documents.map(doc => doc.source);
            let uniqueSources = [...new Set(sources)];
            return uniqueSources
        }
    }
});

watch(() => props.message.content, () => {
    if (!props.message.status || !store.growMode || !messageContainer.value) return;
    else if (props.message.status === 'incomplete') {
        if (isExpanded.value == false) {
            messageContainer.value.style.height = (chatWindowHeight.value) + 'px';
            messageContainer.value.style.paddingTop = '56px';
            isExpanded.value = true;
        } else {
            nextTick(() => {
                const messageContainerHeight = messageContainer.value.scrollHeight;
                if (messageContainerHeight > chatWindowHeight.value) {
                    chatWindowHeight.value = messageContainerHeight;
                    messageContainer.value.style.height = (chatWindowHeight.value) + 'px';
                    messageContainer.value.style.paddingTop = '60px';
                }
            });
        }
    }
});

watch(() => props.message.status, () => {
    if (!props.message.status || !store.growMode || !messageContainer.value) return;
    else if (props.message.status === 'complete' && isExpanded.value == true) {
        messageContainer.value.style.height = 'auto';
        messageContainer.value.style.paddingTop = '20px';
        isExpanded.value = false;
    }
});

watch(() => props.chatWindowHeight, (newVal) => {
    chatWindowHeight.value = newVal;
});

const convertedContent = computed(() => {
    const { finalText, toolName } = processToolRequest(props.message.content);
    return { "text": renderMarkdown(finalText), "toolName": toolName };
});

const formatToolName = (slug) => {
    return slug
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

const processToolRequest = (text) => {
    const toolRequestRegex = /<<tool:([\w]+)\(([^)]*)\)>>/g;
    const partialToolRequestRegex = /(.*?)(<<[^>]*$)/;

    let toolName = '';

    const replacedText = text.replace(toolRequestRegex, (match, name) => {
        toolName = formatToolName(name);
        return '';
    });

    const finalText = replacedText.replace(partialToolRequestRegex, (match, before, partial) => {
        if (partial.startsWith('<<tool:')) {
            return before;
        }
        return match;
    });

    return { finalText, toolName };
}

const renderMarkdown = (markdownText) => {
    if (markdownText == '') {
        return markdownText
    }
    const copyButton = '<button class="copy-button absolute right-0 mr-2 mt-2 top-0 text-xs bg-gray-800 opacity-75 text-white py-1 px-2 rounded hover:bg-gray-700">Copy</button>';

    const md = new MarkdownIt({
        highlight: function (str, lang) {
            if (lang && Prism.languages[lang]) {
                try {
                    const highlightedCode = Prism.highlight(str, Prism.languages[lang], lang);
                    const langClass = `language-${lang}`;
                    const tailwindClasses = 'p-4 rounded cursor-pointer relative';
                    return `<pre class="${tailwindClasses}">${copyButton}<code class="${langClass}">${highlightedCode}</code></pre>`;
                } catch (error) {
                    console.error('Prism syntax highlighting error:', error);
                }
            }
            return '';
        },
    });

    let html = md.render(markdownText);
    html = html.replace(/^<p>|<\/p>$/g, '');
    const sanitizedHtml = DOMPurify.sanitize(html);
    return sanitizedHtml;
}

const initCopyButtons = async () => {
    await nextTick();
    const clipboard = new ClipboardJS('.copy-button', {
        target: function (trigger) {
            return trigger.nextElementSibling;
        },
    });

    clipboard.on('success', function (e) {
        e.clearSelection();
        e.trigger.textContent = 'Copied!';
        setTimeout(() => {
            e.trigger.textContent = 'Copy';
        }, 2000);
    });

    clipboard.on('error', function (e) {
        e.trigger.textContent = 'Error!';
        setTimeout(() => {
            e.trigger.textContent = 'Copy';
        }, 2000);
    });
}

onMounted(() => {
    initCopyButtons();
});
</script>