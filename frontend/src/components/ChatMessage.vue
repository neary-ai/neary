<template>
  <div class="w-full">
    <div v-if="isPrevMessageSameRole" class="w-full border-b border-neutral-100"></div>
    <div v-if="isUser" class="flex items-start prose prose-invert max-w-none leading-7 mr-auto bg-nearyblue-300 px-6 py-3.5"
      :class="message.is_archived ? 'pattern-diagonal-lines pattern-nearyblue-200 pattern-bg-nearyblue-300 pattern-size-6 pattern-opacity-80' : ''">
      <div class="py-3">
        <div class="not-prose flex-shrink-0 font-bold rounded h-8 w-8 flex items-center justify-center mr-5"
          :class="message.is_archived ? 'bg-slate-700 text-slate-400' : 'bg-nearyblue-50/90 text-nearygray-100'">
          {{ firstLetterOfName }}
        </div>
      </div>
      <div class="text-slate-300/80 whitespace-pre-wrap py-4 [overflow-wrap:anywhere]">{{ message.content }}</div>
    </div>
    <div ref="messageContainer" v-if="isAssistant && convertedContent.text != ''"
      class="flex justify-start items-start prose prose-invert max-w-none leading-7 mr-auto bg-nearyblue-400 text-gray-400 pt-3.5 pb-2.5 px-6 transition-all duration-50 delay-0"
      :class="{ 'pattern-diagonal-lines pattern-nearyblue-300 pattern-bg-nearyblue-400 pattern-size-6 pattern-opacity-80': message.is_archived }">
      <div class="flex w-full items-start">
        <div class="py-3">
          <div class="not-prose flex-shrink-0 font-bold rounded h-8 w-8 flex items-center justify-center mr-5"
            :class="message.is_archived ? 'bg-slate-700 text-slate-400' : 'bg-nearypink-300/20 text-nearypink-200'">
            N
          </div>
        </div>
        <div class="flex flex-col min-w-0 pt-[1rem]">
          <div class="overflow-x-scroll text-slate-300/80 min-w-0 max-w-full" v-html="convertedContent.text"></div>
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
    <div v-if="isNotification"
      class="flex justify-start items-start prose prose-invert max-w-none leading-7 pl-8 pr-6 py-4 shadow bg-nearyblue-50/30 border border-neutral-300 m-4 rounded-lg">
      <div class="flex w-full gap-6 items-start">
        <InformationCircleIcon class="flex-shrink-0 text-nearygray-200 flex items-center justify-center w-7 h-7 mt-4" />
        <div class="flex flex-col min-w-0 pr-8">
          <div class="flex items-center">
            <div class="flex items-center overflow-x-scroll text-nearygray-200 min-w-0 max-w-full">
              <div class="pt-4" v-html="convertedContent.text"></div>
            </div>
          </div>
          <div v-if="!actionResponseLoading" class="flex gap-3 items-center">
            <div v-if="isActionCompleted"
              class="text-sm text-nearyblue-100 bg-slate-400 shadow px-4 py-1.5 mb-4 rounded-full font-medium flex items-center">
              {{ isActionCompleted }}
            </div>
            <button v-else v-for="(action, index) in message.actions" :key="index"
              @click="handleActionButton(action, message.id)"
              :disabled="actionCompleted[action.data.request_id] || actionResponseLoading"
              class="text-nearyblue-100 bg-slate-400 rounded-md px-3.5 py-2.5 mb-4 mt-2 text-sm shadow hover:bg-opacity-80"
              :class="[actionCompleted[action.data.request_id] ? 'text-slate-600' : 'text-nearyblue-500', actionResponseLoading ? '' : '']">
              {{ action.label }}
            </button>
          </div>
          <Loading v-if="actionResponseLoading" textColor="text-nearygray-100" />
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
import { InformationCircleIcon, } from '@heroicons/vue/24/outline';
import { useAppStore } from '@/store/index.js';
import api from '@/services/apiService';
import Loading from '@/components/common/Loading.vue';

const store = useAppStore();

const props = defineProps({
  message: Object,
  chatWindowHeight: Number,
});

let actionCompleted = ref({});
let chatWindowHeight = ref(props.chatWindowHeight);
let messageContainer = ref(null);
let isExpanded = ref(false);
let actionResponseLoading = ref(false);

let isActionCompleted = computed(() => {
  const completedAction = Object.values(actionCompleted.value).find(status => status !== 'error');
  return completedAction || '';
});

let isPrevMessageSameRole = computed(() => {
  if (store.selectedConversation) {
    let currentIndex = store.selectedConversation.messages.indexOf(props.message.id);
    if (currentIndex > 0) {
      let prevMessageId = store.selectedConversation.messages[currentIndex - 1];
      let prevMessage = store.messages[prevMessageId];
      return prevMessage && prevMessage.role === props.message.role;
    }
    return false;
  }
});

const firstLetterOfName = computed(() => {
  if (store.userProfile && store.userProfile.name) {
    const name = store.userProfile.name;
    return name ? name[0] : '?';
  }
  return '?';
});

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

const isUser = computed(() => props.message.role === 'user');
const isAssistant = computed(() => props.message.role === 'assistant');
const isNotification = computed(() => props.message.role === 'notification');
const convertedContent = computed(() => {
  const { finalText, toolName } = processToolRequest(props.message.content);
  return { "text": renderMarkdown(finalText), "toolName": toolName };
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