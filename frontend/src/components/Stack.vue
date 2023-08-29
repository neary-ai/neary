<template>
    <div class="w-full overflow-y-scroll">
        <div v-if="store.selectedConversation && store.selectedConversation.settings && store.settingsOptions"
            id="alt-window" class="font-mulish flex flex-col gap-3 max-w-3xl">
            <div class="p-8 pt-[5.5rem]">
                <SectionHeading section-name="Chat Stack" @on-click="onBackButtonClick" />
                <div class="divide-y divide-slate-400/20">
                    <div class="grid grid-cols-1 sm:grid-cols-7 py-12">
                        <div class="col-span-full sm:col-span-3 pr-12">
                            <div class="flex flex-col mb-6 sm:mb-0">
                                <div class="text-slate-300 font-semibold mb-2">Preset</div>
                                <div class="text-sm text-nearygray-400">Start your stack with a ready-made conversation
                                    recipe.
                                </div>
                            </div>
                        </div>
                        <div class="col-span-full sm:col-span-4 flex flex-col text-slate-400">
                            <Card @click="router.push('/presets')" class="cursor-pointer" padding="px-3 py-3">
                                <template v-slot:icon>
                                    <div class="flex items-center justify-center">
                                        <Icon
                                            :icon="store.selectedConversation.preset.icon ? store.selectedConversation.preset.icon : 'heroicons:user-solid'"
                                            class="text-nearylight-200 w-6 h-6" />
                                    </div>
                                </template>
                                <div class="text-nearygray-100 text-sm font-bold py-0.5 -ml-1">
                                    {{ store.selectedConversation.preset.name }}</div>
                                <template v-slot:button>
                                    <ChevronRightIcon class="w-5 h-5 shrink-0"></ChevronRightIcon>
                                </template>
                            </Card>
                        </div>
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-7 py-12">
                        <div class="col-span-1 sm:col-span-3 pr-12">
                            <div class="flex flex-col mb-6 sm:mb-0">
                                <div class=" text-slate-300 font-semibold mb-2">Instructions</div>
                                <div class="text-sm text-nearygray-400">Customize these instructions (or system message) to
                                    tell the AI how it should behave.</div>
                            </div>
                        </div>
                        <div class="col-span-full sm:col-span-4 flex flex-col text-slate-400">
                            <div class="flex flex-col items-start">
                                <TextareaField @change="store.updateConversation(store.selectedConversation)"
                                    class="w-full mb-6" v-model="store.selectedConversation.settings.llm.system_message" />
                            </div>
                        </div>
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-7 py-12">
                        <div class="col-span-1 sm:col-span-3 pr-12">
                            <div class="flex flex-col mb-6 sm:mb-0">
                                <div class=" text-slate-300 font-semibold mb-2">Snippets</div>
                                <div class="text-sm text-nearygray-400">Automatically insert pieces of context into the
                                    conversation, so Neary is always in the know.</div>
                            </div>
                        </div>
                        <div class="col-span-full sm:col-span-4 flex flex-col text-slate-400">
                            <div class="flex flex-col gap-3 items-start">
                                <template v-for="snippet in enabledSnippets" :key="snippet.id">
                                    <Card>
                                        <template v-slot:icon>
                                            <div
                                                class="flex items-center justify-center h-9 w-9 rounded shadow bg-neutral-100 mt-0.5">
                                                <Icon icon="mdi:note-text-outline" class="text-nearycyan-300 w-5 h-5" />
                                            </div>
                                        </template>
                                        <div class="text-field-default-foreground text-sm font-medium">{{
                                            snippet.registry.metadata.display_name }}</div>
                                        <div class="text-sm font-normal text-nearygray-400">{{
                                            snippet.registry.metadata.description }}</div>
                                        <template v-slot:button>
                                            <Popover class="relative inline-block text-left">
                                                <PopoverButton
                                                    class="flex items-center group relative cursor-pointer px-2 py-0.5 hover:text-nearygray-100 focus:border-transparent focus:ring-0 focus:outline-none">
                                                    <Icon icon="heroicons:ellipsis-vertical" class="w-5 h-5" />
                                                </PopoverButton>
                                                <Transition as="div" enter="transition ease-out duration-200"
                                                    enterFrom="opacity-0 translate-y-1" enterTo="opacity-100 translate-y-0"
                                                    leave="transition ease-in duration-150"
                                                    leaveFrom="opacity-100 translate-y-0" leaveTo="opacity-0 translate-y-1">
                                                    <PopoverPanel v-slot="{ close }"
                                                        class="absolute w-32 bottom-8 -right-0 origin-top-right ring-1 ring-nearygray-500  bg-nearygray-200 text-nearyblue-300 rounded-md focus:outline-none">
                                                        <ul class="divide-y divide-nearygray-500">
                                                            <li @click.stop="pluginSettings(snippet, close)"
                                                                class="cursor-pointer flex items-center rounded-t gap-2 px-3 py-2 text-sm hover:bg-nearygray-300">
                                                                <Icon icon="heroicons:adjustments-horizontal"
                                                                    class="w-5 h-5" />
                                                                <div>Settings</div>
                                                            </li>
                                                            <li @click.stop="disablePlugin(snippet, close)"
                                                                class="cursor-pointer flex items-center rounded-b gap-2 px-3 py-2 text-sm hover:bg-nearygray-300">
                                                                <Icon icon="heroicons:x-mark" class="w-5 h-5" />
                                                                <div>Remove</div>
                                                            </li>
                                                        </ul>
                                                    </PopoverPanel>
                                                </Transition>
                                            </Popover>
                                        </template>
                                    </Card>
                                </template>
                                <button @click="router.push(`/settings/${store.selectedConversationId}/snippets`)"
                                    type="button"
                                    class="mt-2 text-sm font-semibold leading-6 text-nearylight-100 hover:text-nearylight-100/80"><span
                                        aria-hidden="true">+</span> Add more snippets</button>
                            </div>
                        </div>
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-7 py-12">
                        <div class="col-span-1 sm:col-span-3 pr-12">
                            <div class="flex flex-col mb-6 sm:mb-0">
                                <div class=" text-slate-300 font-semibold mb-2">Tools</div>
                                <div class="text-sm text-nearygray-400">Choose which tools, or actions, the AI can take on
                                    your behalf
                                </div>
                            </div>
                        </div>
                        <div class="col-span-1 sm:col-span-4 flex flex-col text-slate-400">
                            <div class="flex flex-col gap-3 items-start">
                                <template v-for="tool in enabledTools" :key="tool.id">
                                    <Card>
                                        <template v-slot:icon>
                                            <div
                                                class="flex items-center justify-center h-9 w-9 rounded shadow bg-neutral-100 mt-0.5">
                                                <Icon icon="mdi:function" class="text-nearyyellow-100 w-5 h-5" />
                                            </div>
                                        </template>
                                        <div class="leading-7">
                                            <div class="text-field-default-foreground text-sm font-medium">{{
                                                tool.registry.metadata.display_name }}</div>
                                            <div class="text-sm font-normal text-nearygray-400">{{
                                                tool.registry.metadata.description }}</div>
                                        </div>
                                        <template v-slot:button>
                                            <Popover class="relative inline-block text-left">
                                                <PopoverButton
                                                    class="flex items-center group relative cursor-pointer px-2 py-0.5 hover:text-nearygray-100 focus:border-transparent focus:ring-0 focus:outline-none">
                                                    <Icon icon="heroicons:ellipsis-vertical" class="w-5 h-5" />
                                                </PopoverButton>
                                                <Transition as="div" enter="transition ease-out duration-200"
                                                    enterFrom="opacity-0 translate-y-1" enterTo="opacity-100 translate-y-0"
                                                    leave="transition ease-in duration-150"
                                                    leaveFrom="opacity-100 translate-y-0" leaveTo="opacity-0 translate-y-1">
                                                    <PopoverPanel v-slot="{ close }"
                                                        class="absolute w-32 bottom-8 -right-0 origin-top-right ring-1 ring-nearygray-500  bg-nearygray-200 text-nearyblue-300 rounded-md focus:outline-none">
                                                        <ul class="divide-y divide-nearygray-500">
                                                            <li @click.stop="pluginSettings(tool, close)"
                                                                class="cursor-pointer flex items-center rounded-t gap-2 px-3 py-2 text-sm hover:bg-nearygray-300">
                                                                <Icon icon="heroicons:adjustments-horizontal"
                                                                    class="w-5 h-5" />
                                                                <div>Settings</div>
                                                            </li>
                                                            <li @click.stop="disablePlugin(tool, close)"
                                                                class="cursor-pointer flex items-center rounded-b gap-2 px-3 py-2 text-sm hover:bg-nearygray-300">
                                                                <Icon icon="heroicons:x-mark" class="w-5 h-5" />
                                                                <div>Remove</div>
                                                            </li>
                                                        </ul>
                                                    </PopoverPanel>
                                                </Transition>
                                            </Popover>
                                        </template>
                                    </Card>
                                </template>
                                <button @click="router.push(`/settings/${store.selectedConversationId}/tools`)"
                                    type="button"
                                    class="mt-2 text-sm font-semibold leading-6 text-nearylight-100 hover:text-nearylight-100/80"><span
                                        aria-hidden="true">+</span> Add more tools</button>
                            </div>
                        </div>
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-7 py-12">
                        <div class="col-span-1 sm:col-span-3 pr-12">
                            <div class="flex flex-col mb-6 sm:mb-0">
                                <div class=" text-slate-300 font-semibold mb-2">Save Settings</div>
                                <div class="text-sm text-nearygray-400">Use these settings for new conversations</div>
                            </div>
                        </div>
                        <div class="col-span-1 sm:col-span-4 flex flex-col text-slate-400">
                            <div class="flex flex-col items-start w-full">
                                <Button class="shrink-0" @buttonClick="isOpen = true;" button-type="btn-light">Save New Preset</Button>
                            </div>
                        </div>
                        <Modal :isOpen="isOpen" @keyup.enter="save" @save="save" @close="close">
                            <template v-slot:title>
                                Create Preset
                            </template>
                            <div class="flex-grow w-full my-5">
                                <div class="flex flex-col mb-6">
                                    <label class="text-sm font-semibold text-slate-300 w-full mb-2">Preset Name</label>
                                    <TextInputField v-model="createPresetName" class="w-full"
                                        placeholderText="Enter a name for your preset" />
                                </div>
                                <div class="flex flex-col mb-6">
                                    <label class="text-sm font-semibold text-slate-300 w-full mb-2">Description</label>
                                    <TextInputField v-model="createPresetDescription" class="w-full"
                                        placeholderText="Enter a short description" />
                                </div>
                            </div>
                            <template v-slot:buttons>
                                <Button @buttonClick="save" button-type="btn-light" class="w-full">Save Preset</Button>
                                <Button @buttonClick="close" button-type="btn-outline-light" class="w-full">Cancel</Button>
                            </template>
                        </Modal>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAppStore } from '@/store/index.js';
import api from '@/services/apiService';
import Button from './common/Button.vue';
import { Popover, PopoverButton, PopoverPanel } from '@headlessui/vue';
import TextareaField from './common/TextareaField.vue';
import TextInputField from './common/TextInputField.vue';
import SectionHeading from './common/SectionHeading.vue'
import Card from './common/Card.vue';
import Modal from './common/Modal.vue';
import { Icon } from '@iconify/vue';
import { ChevronRightIcon } from '@heroicons/vue/20/solid';

const store = useAppStore();
const router = useRouter();


const enabledSnippets = computed(() => {
    if (store.selectedConversation) {
        return store.selectedConversation.plugins.filter(plugin => plugin.registry.metadata.plugin_type === 'snippet');
    }
    return []
});

const enabledTools = computed(() => {
    if (store.selectedConversation) {
        return store.selectedConversation.plugins.filter(plugin => plugin.registry.metadata.plugin_type === 'tool');
    }
    return []
});

const pluginSettings = (plugin) => {
    store.pluginSettings = plugin;
    router.push(`/plugins/${plugin.id}`);
    return
}

const disablePlugin = async (plugin) => {
    store.selectedConversation.plugins = store.selectedConversation.plugins.filter(p => p !== plugin);
    await store.updateConversation(store.selectedConversation);
}

// Create new preset
const isOpen = ref(false)

const createPresetName = ref('')
const createPresetDescription = ref('')

const save = async () => {
    isOpen.value = false;

    try {
        await api.createPreset(createPresetName.value, createPresetDescription.value, store.selectedConversationId)
        store.newNotification("Preset saved!");
    }
    catch {
        store.newNotification("Couldn't save preset");
    }

}

const close = () => {
  isOpen.value = false;
};

const onBackButtonClick = () => {
    router.go(-1);
};

watch(() => store.selectedConversationId, async (newId) => {
    if (newId) {
        store.settingsOptions = await api.getAvailableSettings();
    }
}, { immediate: true });

</script>