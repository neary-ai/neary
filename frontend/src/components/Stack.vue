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
                                    recipe
                                </div>
                            </div>
                        </div>
                        <div class="col-span-full sm:col-span-4 flex flex-col text-slate-400">
                            <Card @click="router.push('/presets')" class="cursor-pointer" padding="px-3 py-2.5">
                                <template v-slot:icon>
                                    <div class="flex items-center justify-center">
                                        <Icon
                                            :icon="store.selectedConversation.preset.icon ? store.selectedConversation.preset.icon : 'heroicons:user-solid'"
                                            class="text-nearygray-300 w-6 h-6" />
                                    </div>
                                </template>
                                <div class="font-medium text-sm py-0.5 -ml-1 text-field-default-foreground">
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
                                <div class="text-sm text-nearygray-400">Custom instructions tell the AI how it should behave
                                </div>
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
                                    conversation</div>
                            </div>
                        </div>
                        <div class="col-span-full sm:col-span-4 flex flex-col text-slate-400">
                            <div class="flex flex-col gap-3 items-start">
                                <template v-for="snippet in enabledSnippets" :key="snippet.name">
                                    <Card>
                                        <template v-slot:icon>
                                            <div
                                                class="flex items-center justify-center h-9 w-9 rounded shadow bg-neutral-100 mt-0.5">
                                                <Icon icon="mdi:note-text-outline" class="text-nearycyan-400 w-5 h-5" />
                                            </div>
                                        </template>
                                        <div class="text-field-default-foreground text-sm font-medium leading-6">{{
                                            snippet.display_name }}</div>
                                        <template v-slot:button>
                                            <Popover class="relative inline-block text-left">
                                                <PopoverButton
                                                    class="flex items-center group relative cursor-pointer pl-2 py-0.5 hover:text-nearygray-100 focus:border-transparent focus:ring-0 focus:outline-none">
                                                    <Icon icon="heroicons:ellipsis-vertical" class="w-5 h-5" />
                                                </PopoverButton>
                                                <Transition as="div" enter="transition ease-out duration-200"
                                                    enterFrom="opacity-0 translate-y-1" enterTo="opacity-100 translate-y-0"
                                                    leave="transition ease-in duration-150"
                                                    leaveFrom="opacity-100 translate-y-0" leaveTo="opacity-0 translate-y-1">
                                                    <PopoverPanel v-slot="{ close }"
                                                        class="absolute w-32 bottom-8 -right-0 origin-top-right ring-1 ring-nearygray-500  bg-nearygray-200 text-nearyblue-300 rounded-md focus:outline-none">
                                                        <ul class="divide-y divide-nearygray-500">
                                                            <li @click.stop="router.push(`/plugins/${snippet.plugin}`)"
                                                                class="cursor-pointer flex items-center rounded-t gap-2 px-3 py-2 text-sm hover:bg-nearygray-300">
                                                                <Icon icon="heroicons:adjustments-horizontal"
                                                                    class="w-5 h-5" />
                                                                <div>Settings</div>
                                                            </li>
                                                            <li @click.stop="removeFunction(snippet.name, 'snippets', close)"
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
                                <div class="text-sm text-nearygray-400">Tools are actions the AI can take on
                                    your behalf
                                </div>
                            </div>
                        </div>
                        <div class="col-span-1 sm:col-span-4 flex flex-col text-slate-400">
                            <div class="flex flex-col gap-3 items-start">
                                <template v-for="tool in enabledTools" :key="tool.name">
                                    <Card>
                                        <template v-slot:icon>
                                            <div
                                                class="flex items-center justify-center h-9 w-9 rounded shadow bg-neutral-100 mt-0.5">
                                                <Icon icon="mdi:function" class="text-nearyyellow-100 w-5 h-5" />
                                            </div>
                                        </template>
                                        <div class="text-field-default-foreground text-sm font-medium leading-6">{{
                                            tool.display_name }}</div>
                                        <template v-slot:button>
                                            <Popover class="relative inline-block text-left">
                                                <PopoverButton
                                                    class="flex items-center group relative cursor-pointer pl-2 py-0.5 hover:text-nearygray-100 focus:border-transparent focus:ring-0 focus:outline-none">
                                                    <Icon icon="heroicons:ellipsis-vertical" class="w-5 h-5" />
                                                </PopoverButton>
                                                <Transition as="div" enter="transition ease-out duration-200"
                                                    enterFrom="opacity-0 translate-y-1" enterTo="opacity-100 translate-y-0"
                                                    leave="transition ease-in duration-150"
                                                    leaveFrom="opacity-100 translate-y-0" leaveTo="opacity-0 translate-y-1">
                                                    <PopoverPanel v-slot="{ close }"
                                                        class="absolute w-32 bottom-8 -right-0 origin-top-right ring-1 ring-nearygray-500  bg-nearygray-200 text-nearyblue-300 rounded-md focus:outline-none">
                                                        <ul class="divide-y divide-nearygray-500">
                                                            <li @click.stop="router.push(`/plugins/${tool.plugin}`)"
                                                                class="cursor-pointer flex items-center rounded-t gap-2 px-3 py-2 text-sm hover:bg-nearygray-300">
                                                                <Icon icon="heroicons:adjustments-horizontal"
                                                                    class="w-5 h-5" />
                                                                <div>Settings</div>
                                                            </li>
                                                            <li @click.stop="removeFunction(tool.name, 'tools', close)"
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
                                <div class="text-sm text-nearygray-400">Save your stack as a preset for easy reuse</div>
                            </div>
                        </div>
                        <div class="col-span-1 sm:col-span-4 flex flex-col text-slate-400">
                            <div class="flex items-start w-full gap-3">
                                <Button class="shrink-0" @buttonClick="router.push('/preset')" button-type="btn-light">Save
                                    New
                                    Preset</Button>
                                <Button class="shrink-0"
                                    @buttonClick="updateSelectedPreset(store.selectedConversation.preset)"
                                    button-type="btn-outline-light">Update Current Preset</Button>
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


function getEnabledFunctions(functionType) {
    return computed(() => {
        const selectedPlugins = store.selectedConversation.plugins;
        let functions = [];

        selectedPlugins.forEach(plugin => {
            if (plugin.is_enabled && plugin['functions'][functionType]) {
                Object.entries(plugin['functions'][functionType]).forEach(([name, details]) => {
                    functions.push({
                        name: name,
                        display_name: details.display_name,
                        description: details.description,
                        plugin: plugin.name,
                        plugin_display_name: plugin.display_name,
                    });
                });
            }
        });
        return functions;
    });
}

const enabledSnippets = getEnabledFunctions('snippets');
const enabledTools = getEnabledFunctions('tools');

const removeFunction = (functionName, functionType, close) => {
    close();
    if (store.selectedConversation && store.selectedConversation.plugins) {
        store.selectedConversation.plugins.forEach(plugin => {
            if (plugin.functions[functionType] && plugin.functions[functionType][functionName]) {
                delete plugin.functions[functionType][functionName];

                // If there are no functions left in the plugin, remove the plugin
                if (Object.keys(plugin.functions[functionType]).length === 0) {
                    delete plugin.functions[functionType];

                    if (Object.keys(plugin.functions).length === 0) {
                        const index = store.selectedConversation.plugins.indexOf(plugin);
                        if (index > -1) {
                            store.selectedConversation.plugins.splice(index, 1);
                        }
                    }
                }
            }
        });
        store.updateConversation(store.selectedConversation);
    }
};

// Create new preset
const isOpen = ref(false)

const createPresetName = ref('')
const createPresetDescription = ref('')

const save = async () => {
    isOpen.value = false;

    try {
        await api.createPreset(createPresetName.value, createPresetDescription.value, store.selectedConversationId)
        store.newNotification("New preset saved");
    }
    catch {
        store.newNotification("Couldn't save preset");
    }

}

const updateSelectedPreset = async (preset) => {
    try {
        preset['rebuild_from_conversation'] = store.selectedConversationId;
        await api.updatePreset(preset);
        store.newNotification("Preset updated");
    }
    catch {
        store.newNotification("Couldn't update preset");
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