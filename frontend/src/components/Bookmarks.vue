<template>
    <div id="alt-window" class="font-mulish flex flex-col gap-3 w-full overflow-y-scroll">
        <div class="p-8 pt-[5.5rem] max-w-3xl">
            <SectionHeading section-name="Bookmarks" @on-click="onBackButtonClick" />
            <div class="flex flex-col divide-y divide-neutral-500 mt-2">
                <div v-for="bookmark in store.bookmarks" :key="bookmark.message_id" class="text-sm py-6">
                    <div class="text-sm text-nearylight-100 font-bold mb-1">{{ bookmark.conversation_title }}</div>
                    <div class="text-xs text-nearylight-300">
                        {{ formatDate(bookmark.created_at) }}
                    </div>
                    <div class="mt-3 mb-5 text-nearylight-200">
                        {{ truncateText(bookmark.message_content.text, 200) }}
                    </div>
                    <div>
                        <ul class="flex gap-4">
                            <li @click="showContext(bookmark)" class="text-sm text-nearycyan-400 hover:text-nearycyan-500 cursor-pointer">View</li>
                            <li @click="store.removeBookmark(bookmark.message_id)" class="text-sm text-nearycyan-400 hover:text-nearycyan-500 cursor-pointer">Remove</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useAppStore } from '@/store/index.js';
import SectionHeading from './common/SectionHeading.vue'

const store = useAppStore();
const router = useRouter();

const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return new Date(dateString).toLocaleDateString('en-US', options);
};

const truncateText = (text, maxLength) => {
  if (text.length > maxLength) {
    return text.substring(0, maxLength).trim() + '...';
  }
  return text;
};

const showContext = (bookmark) => {
    store.loadConversation(bookmark.conversation_id);
    store.scrollToMessage = bookmark.message_id;
}

const onBackButtonClick = () => {
    router.go(-1);
};

</script>