<template>
    <div ref="messageContainer" v-if="convertedContent != ''"
        class="flex justify-start items-start w-full prose prose-invert max-w-none leading-7 mr-auto text-gray-400 pt-6 pb-3.5 pl-6 pr-8 md:pr-12 lg:pr-20 transition-all duration-50 delay-0" :class="message.is_archived ? 'pattern-diagonal-lines pattern-nearyblue-300 pattern-bg-nearyblue-400 pattern-size-6 pattern-opacity-80' : 'bg-nearyblue-400'">
        <div class="flex w-full items-start">
            <div class="py-3">
                <div class="not-prose flex-shrink-0 font-bold rounded h-7 w-7 flex items-center justify-center mr-5 text-sm bg-nearypink-300/20 text-nearypink-200">
                    N
                </div>
            </div>
            <div class="flex flex-col min-w-0 pt-[0.75rem]">
                <div class="overflow-x-scroll min-w-0 max-w-full"
                    :class="[message.is_archived ? 'text-nearygray-200' : 'text-slate-300/80']"
                    v-html="convertedContent"></div>
                <div v-if="uniqueSources && uniqueSources.length > 0"
                    class="text-slate-400/80 text-sm py-4 mt-4 border-t border-slate-700">
                    Sources: {{ uniqueSources.join(', ') }}
                </div>
                <div v-if="message.status != 'incomplete'" class="flex gap-2.5 mb-2 -mt-1.5">
                    <Icon 
                        v-if="message.status != 'incomplete'"
                        icon="octicon:paste-16"
                        class="cursor-pointer hover:opacity-80 w-4 h-4 text-nearygray-800"
                        @click="copyToClipboard"
                    />
                    <Icon 
                        v-if="message.status != 'incomplete'"
                        :icon="isBookmarked ? 'octicon:bookmark-slash-16' : 'octicon:bookmark-16'"
                        class="cursor-pointer hover:opacity-80 w-4 h-4 text-nearygray-800"
                        @click="toggleBookmark"
                    />
                </div>
            </div>
        </div>
    </div>
</template>
  
<script setup>
import { onMounted, ref, watch, nextTick, computed } from 'vue';
import MarkdownIt from 'markdown-it';
import mditTexmath from 'markdown-it-texmath';
import DOMPurify from 'dompurify';
import ClipboardJS from 'clipboard';
import Prism from 'prismjs';
import katex from 'katex';
import { Icon } from '@iconify/vue';
import 'prismjs/components/prism-python';
import 'prismjs/themes/prism-tomorrow.css';
import 'katex/dist/katex.min.css';
import 'markdown-it-texmath/css/texmath.css';

import { useAppStore } from '@/store/index.js';

const store = useAppStore();

const props = defineProps({
    message: Object,
    chatWindowHeight: Number,
});

let chatWindowHeight = ref(props.chatWindowHeight);
let messageContainer = ref(null);
let isExpanded = ref(false);

const isBookmarked = computed(() => {
  return store.bookmarks.some(bookmark => bookmark.message_id === props.message.id)
})

const toggleBookmark = async () => {
    try {
        if (isBookmarked.value) {
            store.removeBookmark(props.message.id)
        } else {
            store.addBookmark(props.message.id)
            store.newNotification('Bookmark added!');
        }
    } catch (error) {
        console.error('Error toggling bookmark:', error);
    }
};

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
    if (props.message.content.text) {
        return renderMarkdown(props.message.content.text);
    }
    else {
        return ""
    }
});

const renderMarkdown = (markdownText) => {
    if (markdownText == '') {
        return markdownText
    }
    const copyButton = '<button class="copy-button absolute right-0 mr-2 mt-2 top-0 text-xs bg-gray-800 opacity-75 text-white py-1 px-2 rounded hover:bg-gray-700">Copy</button>';

    const md = new MarkdownIt({
        html: true,
        linkify: true,
        typographer: true,
        highlight: function (str, lang) {
            let highlightedCode = str;
            let langClass = '';

            if (lang && Prism.languages[lang]) {
                try {
                    highlightedCode = Prism.highlight(str, Prism.languages[lang], lang);
                    langClass = `language-${lang}`;
                } catch (error) {
                    console.error('Prism syntax highlighting error:', error);
                }
            }

            const tailwindClasses = 'p-4 rounded cursor-pointer relative';
            return `<pre class="${tailwindClasses}">${copyButton}<code class="${langClass}">${highlightedCode}</code></pre>`;
        }
    })
    .use(mditTexmath, { engine: katex, delimiters:'brackets' });

    console.log('Rendering text: ', markdownText)

    let html = md.render(markdownText);
    html = html.replace(/^<p>|<\/p>$/g, '');
    const sanitizedHtml = DOMPurify.sanitize(html);
    return sanitizedHtml;
}

const copyToClipboard = async () => {
    try {
        await navigator.clipboard.writeText(props.message.content.text);
        store.newNotification('Message copied!');
    } catch (err) {
        console.error('Failed to copy text: ', err);
    }
};

const initCopyButtons = async (copyData) => {
    await nextTick();
    const clipboard = new ClipboardJS('.copy-button', {
        text: function (trigger) {
            if (copyData) {
                return copyData;
            } else {
                return trigger.nextElementSibling.textContent;
            }
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