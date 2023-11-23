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
                <div class="overflow-x-scroll min-w-0 max-w-full" :class="[message.is_archived ? 'text-nearygray-200' : 'text-slate-300/80']">
                    <div @click="downloadFile" class="cursor-pointer flex gap-3 items-center bg-nearylight-400/20 hover:bg-nearylight-400/10 border-nearylight-400/70 border rounded py-3 px-4 max-w-2xl mb-6">
                        <Icon icon="heroicons:document-text" class="flex-shrink-0 text-nearylight-200 flex items-center justify-center w-6 h-6" />
                        <div class="flex flex-col">
                            <div class="text-sm font-medium text-nearylight-100">{{ fileName }}</div>
                            <div class="text-xs text-nearylight-400">{{ fileSize }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
  
<script setup>
import { computed } from 'vue';
import { Icon } from '@iconify/vue';
import { useAppStore } from '@/store/index.js';

const store = useAppStore();

const props = defineProps({
    message: Object,
});

const fileName = computed(() => {
    if (props.message) {
        return props.message.content.filename;
    }
})

const fileUrl = computed(() => {
    if (props.message) {
        return props.message.content.file_url;
    }
})

const fileSize = computed(() => {
    if (props.message) {
        return props.message.content.filesize;
    }
})

const downloadFile = () => {
    const link = document.createElement('a');
    link.href = fileUrl.value;
    link.download = fileName.value;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};

</script>