<template>
    <div class="mt-6">
        <div class="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between mb-6">
            <div class="flex items-center gap-3">
                <!-- Dropdown for Filters -->
                <Listbox v-slot={open} v-model="filterType" as="div">
                    <ListboxButton
                    :class="[open ? 'border-field-focused' : 'border-transparent', 'bg-field-default text-field-default-foreground border relative w-full cursor-default rounded-md py-1.5 pl-3 pr-10 text-left shadow-sm focus:outline-none text-sm leading-6']">
                        {{ filterType }}
                        <span
                            class="bg-neutral-100 text-field-default-foreground font-semibold ml-2 inline-flex items-center rounded-full px-1.5 text-xs py-0.5">
                            {{ getTabCount(filterType) }}
                        </span>
                        <span class="pointer-events-none absolute inset-y-0 right-0 ml-3 flex items-center pr-2">
                            <ChevronUpDownIcon class="h-5 w-5 text-field-default-foreground" aria-hidden="true" />
                        </span>
                    </ListboxButton>
                    <ListboxOptions as="ul"
                    class="border border-field-focused divide-y divide-field-divide absolute z-10 mt-1 max-h-60 overflow-auto rounded-md bg-field-default text-field-default-foreground py-1 text-base shadow-lg focus:outline-none sm:text-sm">
                        <ListboxOption v-for="tab in tabs" :key="tab.name" :value="tab.name" v-slot="{ active }" as="li">
                            <li
                                :class="[active ? 'bg-field-active text-field-active-foreground' : '', 'relative cursor-default select-none py-2 pl-2 pr-4']">
                                <div class="flex items-center justify-between gap-3 text-sm">
                                    <span :class="[selected ? 'font-semibold' : 'font-normal', 'ml-1 block truncate']">{{
                                        tab.name }}</span>
                                    <span v-if="tab.count"
                                        :class="[active ? '' : '', 'bg-neutral-100 text-field-default-foreground font-semibold ml-1 inline-flex items-center rounded-full px-1.5 text-xs py-0.5']">
                                        {{ tab.count }}
                                    </span>
                                </div>
                            </li>
                        </ListboxOption>
                    </ListboxOptions>
                </Listbox>

                <!-- Dropdown for Actions -->
                <Listbox v-slot="{open}" v-model="selectedAction" as="div">
                    <ListboxButton
                    :class="[open ? 'border-field-focused' : 'border-transparent', 'bg-field-default text-field-default-foreground border relative w-full cursor-default rounded-md py-1.5 pl-3 pr-10 text-left shadow-sm focus:outline-none text-sm leading-6']">
                        Actions
                        <span class="pointer-events-none absolute inset-y-0 right-0 ml-3 flex items-center pr-2">
                            <ChevronUpDownIcon class="h-5 w-5 text-field-default-foreground" aria-hidden="true" />
                        </span>
                    </ListboxButton>
                    <ListboxOptions as="ul"
                    class="border border-field-focused divide-y divide-field-divide absolute z-10 mt-1 max-h-60 overflow-auto rounded-md bg-field-default text-field-default-foreground py-1 text-sm shadow-lg focus:outline-none sm:text-sm">
                        <ListboxOption :disabled="!canAddToConversation" :value="'Add to Conversation'" as="li">
                            <div :class="[canAddToConversation ? 'hover:bg-field-active hover:text-field-active-foreground' : 'text-slate-600', 'px-4 py-2 cursor-pointer']">Add to Conversation</div>
                        </ListboxOption>
                        <ListboxOption :disabled="!canRemoveFromConversation" :value="'Remove from Conversation'" as="li">
                            <div :class="[canRemoveFromConversation ? 'hover:bg-field-active hover:text-field-active-foreground' : 'text-slate-600', 'px-4 py-2 cursor-pointer']">Remove from Conversation</div>
                        </ListboxOption>
                        <ListboxOption :disabled="!canDeleteDocument" :value="'Delete Document'" as="li">
                            <div :class="[canDeleteDocument ? 'hover:bg-field-active hover:text-field-active-foreground' : 'text-slate-600', 'px-4 py-2 cursor-pointer']">Delete Documents</div>
                        </ListboxOption>
                    </ListboxOptions>
                </Listbox>
            </div>
            <!-- Button to Add New Document -->
            <button @click="emit('toggledocs')"
                class="text-white flex items-center gap-1.5 bg-nearypink-300 rounded-md pr-3.5 pl-2 py-2 text-sm shadow-sm hover:bg-opacity-90">
                <PlusIcon class="w-5 h-5" />
                New Document
            </button>
        </div>
        <!-- Table -->
        <div class="overflow-x-auto">
            <table class="w-full divide-y divide-gray-700">
                <thead>
                    <tr>
                        <th scope="col"
                            class="px-4 py-4 w-8 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            <input type="checkbox" v-model="selectAll" @change="toggleAll"
                                class="text-field-active rounded focus:ring-0">
                        </th>
                        <th scope="col" class="px-6 py-3 text-left text-sm font-medium text-slate-300 tracking-wider">
                            Name
                        </th>
                        <th scope="col" class="w-12 px-6 py-3 text-left text-sm font-medium text-slate-300 tracking-wider">
                            Type
                        </th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-700">
                    <tr v-for="doc in filteredDocs" :key="doc.id">
                        <td class="px-4 py-4 text-sm">
                            <input type="checkbox" v-model="doc.selected" class="text-field-active rounded focus:ring-0">
                        </td>
                        <td class="px-6 py-4 text-sm max-w-0">
                            <div class="text-slate-400 truncate">
                                {{ doc.source }}
                            </div>
                        </td>
                        <td class="w-12 px-6 py-4 text-sm text-slate-500">
                            {{ doc.type }}
                        </td>
                    </tr>
                </tbody>
            </table>
            <div @click="emit('toggledocs')" v-if="filteredDocs.length === 0"
                class="cursor-pointer text-center py-5 text-nearypink-300 font-semibold border-t border-gray-700">
                + Add documents
            </div>
        </div>
    </div>
</template>

  
<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAppStore } from '@/store/index.js';
import api from '@/services/apiService';
import { Listbox, ListboxButton, ListboxOption, ListboxOptions } from '@headlessui/vue';
import { ChevronUpDownIcon } from '@heroicons/vue/24/outline';
import { PlusIcon } from '@heroicons/vue/20/solid';

const store = useAppStore();
const router = useRouter();

const emit = defineEmits(['toggledocs']);

const docs = ref([]);
const selectAll = ref(false);
const selectedAction = ref('Actions')
const tabs = [
    {
        name: 'In Conversation',
        href: '#',
        count: computed(() => docs.value.filter(doc => doc.conversation_ids.includes(store.selectedConversationId)).length),
        current: computed(() => filterType.value === 'In Conversation')
    },
    {
        name: 'Not in Conversation',
        href: '#',
        count: computed(() => docs.value.filter(doc => !doc.conversation_ids.includes(store.selectedConversationId)).length),
        current: computed(() => filterType.value === 'Not in Conversation')
    },
    {
        name: 'All Documents',
        href: '#',
        count: computed(() => docs.value.length),
        current: computed(() => filterType.value === 'All Documents')
    },
]

const filterType = ref(tabs[0].name);

const canAddToConversation = computed(() => {
    return selectedDocs.value.some(doc => !doc.conversation_ids.includes(store.selectedConversationId));
});

const canRemoveFromConversation = computed(() => {
    return selectedDocs.value.some(doc => doc.conversation_ids.includes(store.selectedConversationId));
});

const canDeleteDocument = computed(() => {
    return selectedDocs.value.length > 0;
});

const getTabCount = (tabName) => {
    let tab = tabs.find(t => t.name === tabName);
    return tab ? tab.count.value : 0;
}

const filteredDocs = computed(() => {
    if (filterType.value === 'All Documents') {
        return docs.value;
    } else if (filterType.value === 'In Conversation') {
        return docs.value.filter(doc => doc.conversation_ids.includes(store.selectedConversationId));
    } else if (filterType.value === 'Not in Conversation') {
        return docs.value.filter(doc => !doc.conversation_ids.includes(store.selectedConversationId));
    }
});


const selectedDocs = computed(() => {
    return filteredDocs.value.filter(doc => doc.selected);
});

const addSelectedDocsToConversation = async () => {
    for (const doc of selectedDocs.value) {
        await api.addDocumentToConversation(doc.document_key, store.selectedConversationId);
    }
    docs.value = await api.getDocuments(store.selectedConversationId);
};

const removeSelectedDocsFromConversation = async () => {
    for (const doc of selectedDocs.value) {
        await api.removeDocumentFromConversation(doc.document_key, store.selectedConversationId);
    }
    docs.value = await api.getDocuments(store.selectedConversationId);
};

const deleteSelectedDocs = async () => {
    for (const doc of selectedDocs.value) {
        await api.deleteDocument(doc.document_key);
    }
    docs.value = await api.getDocuments(store.selectedConversationId);
};

const toggleAll = () => {
  if (selectAll.value) {
    filteredDocs.value.forEach(doc => doc.selected = true);
  } else {
    filteredDocs.value.forEach(doc => doc.selected = false);
  }
};

watch(selectedAction, async (newAction) => {
    switch (newAction) {
        case 'Add to Conversation':
            await addSelectedDocsToConversation();
            break;
        case 'Remove from Conversation':
            await removeSelectedDocsFromConversation();
            break;
        case 'Delete Document':
            await deleteSelectedDocs();
            break;
        default:
            break;
    }
    selectedAction.value = 'Actions';
});

onMounted(async () => {
    let id = router.currentRoute.value.params.id
    docs.value = await api.getDocuments(id);
});
</script>