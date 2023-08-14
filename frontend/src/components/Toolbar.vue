<template>
    <div
        class="absolute left-1/2 z-10 transform -translate-x-1/2 -translate-y-1/2 gap-3 py-1 bg-neutral-100/90 border border-nearyblue-300 text-nearygray-200/80 shadow rounded-md">
        <ul class="flex items-center divide-x divide-nearygray-600/50">
            <li @click="toggleGrowMode()" class="px-2.5 py-0.5 hover:text-nearygray-100 cursor-pointer group relative">
                <template v-if="store.growMode">
                    <Icon icon="heroicons:arrows-pointing-in-20-solid" class="w-[1.1rem] h-[1.1rem]" />
                </template>
                <template v-else>
                    <Icon icon="heroicons:arrows-pointing-out-20-solid" class="w-[1.1rem] h-[1.1rem]" />
                </template>
            </li>
            <li @click="toggleArchivedMessages()"
                class="px-2.5 py-0.5 hover:text-nearygray-100 cursor-pointer group relative">
                <template v-if="store.selectedConversation && !store.selectedConversation.showArchivedMessages">
                    <Icon icon="heroicons:eye-20-solid" class="w-[1.1rem] h-[1.1rem]" />
                </template>
                <template v-else>
                    <Icon icon="heroicons:eye-slash-20-solid" class="w-[1.1rem] h-[1.1rem]" />
                </template>
            </li>
            <li v-if="store.conversationSettings.program && store.conversationSettings.program.value == 'DocumentChat'"
                @click="toggleDocuments()" class="px-2.5 py-0.5 hover:text-nearygray-100 cursor-pointer group relative">
                <Icon icon="heroicons:paper-clip-20-solid" class="w-[1.1rem] h-[1.1rem]" />
            </li>
            <li @click="toggleSettings()" class="px-2.5 py-0.5 hover:text-nearygray-100 cursor-pointer group relative">
                <Icon icon="heroicons:cog-6-tooth-20-solid" class="w-[1.1rem] h-[1.1rem]" />
            </li>
            <li class="flex items-center group relative">
                <Popover class="relative inline-block text-left">
                    <PopoverButton
                        class="flex items-center group relative cursor-pointer px-2 py-0.5 hover:text-nearygray-100 focus:border-transparent focus:ring-0 focus:outline-none">
                        <Icon icon="heroicons-solid:dots-vertical" class="w-[1.1rem] h-[1.1rem]" />
                    </PopoverButton>
                    <Transition as="div" enter="transition ease-out duration-200" enterFrom="opacity-0 translate-y-1"
                        enterTo="opacity-100 translate-y-0" leave="transition ease-in duration-150"
                        leaveFrom="opacity-100 translate-y-0" leaveTo="opacity-0 translate-y-1">
                        <PopoverPanel v-slot="{ close }"
                            class="absolute w-48 bottom-8 -right-0 origin-top-right border border-field-active  bg-field-default text-field-default-foreground rounded-md shadow ring-1 ring-black ring-opacity-10 focus:outline-none">
                            <ul class="divide-y divide-field-divide">
                                <li @click="toggleXRay(close)"
                                    class="cursor-pointer flex rounded-t-md items-center gap-2 px-3 py-2 text-sm hover:bg-field-active hover:text-field-active-foreground">
                                    <Icon icon="tabler:square-toggle" class="w-5 h-5" />
                                    <div>Show X-Ray</div>
                                </li>
                                <li @click="archiveMessages(close)"
                                    class="cursor-pointer flex rounded-t-md items-center gap-2 px-3 py-2 text-sm hover:bg-field-active hover:text-field-active-foreground">
                                    <Icon icon="heroicons:archive-box-arrow-down-20-solid" class="w-5 h-5" />
                                    <div>Archive Messages</div>
                                </li>
                                <li @click="deleteConversation(close)"
                                    class="cursor-pointer flex rounded-b-md items-center gap-2 px-3 py-2 text-sm hover:bg-field-active hover:text-field-active-foreground">
                                    <Icon icon="heroicons:x-mark-20-solid" class="w-5 h-5" />
                                    <div>Delete Conversation</div>
                                </li>
                            </ul>
                        </PopoverPanel>
                    </Transition>
                </Popover>
            </li>
        </ul>
    </div>
</template>

<script setup>
import { watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Icon } from '@iconify/vue';
import { Popover, PopoverButton, PopoverPanel } from '@headlessui/vue';
import { useAppStore } from '@/store/index.js';

const store = useAppStore();
const route = useRoute();
const router = useRouter();

const toggleArchivedMessages = () => {
    if (store.selectedConversation.showArchivedMessages) {
        store.selectedConversation.showArchivedMessages = false;
        store.notification = { 'message': 'Hiding archived messages' }
    }
    else {
        store.selectedConversation.showArchivedMessages = true;
        store.notification = { 'message': 'Showing archived messages' }
    }
}
const toggleGrowMode = () => {
    if (store.growMode) {
        store.growMode = false;
        store.notification = { 'message': 'Messages grow normally' }
    }
    else {
        store.growMode = true;
        store.notification = { 'message': 'Messages have room to grow' }
    }
}

const toggleSettings = () => {
    if (route.path.startsWith('/settings')) {
        router.push('/');
    } else {
        router.push(`/settings/${store.selectedConversationId}`);
    }
}

const toggleDocuments = () => {
    if (router.currentRoute.value.path.startsWith('/documents')) {
        router.go(-1);
    } else {
        router.push(`/documents/${store.selectedConversationId}`);
    }
};

const toggleXRay = async (close) => {
    store.showXray = !store.showXray
    close();
};

const archiveMessages = async (close) => {
    await store.archiveMessages(store.selectedConversationId);
    close();
    store.notification = { 'message': 'Messages archived' }
};

const deleteConversation = async (close = null) => {
    await store.deleteConversation(store.selectedConversationId);
    if (close) {
        close();
    }
};

watch(() => store.growMode, async (newVal, oldVal) => {
  if (oldVal != newVal) {
    store.saveState();
  }
});
</script>