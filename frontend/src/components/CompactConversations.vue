<template>
  <!-- Compact view -->
  <div class="flex items-center justify-start w-full ml-5">
    <Listbox v-if="store.selectedConversation" as="div" v-model="selectedOptionId" class="flex-grow">
      <div class="relative">
        <ListboxButton
          class="relative w-full cursor-default py-1.5 pl-3 pr-10 text-left text-field-active-foreground border border-field-default-foreground/60 rounded-md focus:outline-none focus:ring-0">
          <span class="flex items-center">
            <span class="flex items-center justify-start max-w-[14rem]">
              <Icon :icon="store.selectedConversation.preset.icon ? store.selectedConversation.preset.icon : 'heroicons:user-solid'" class="h-5 w-5 mr-2 opacity-70" />
              <div class="truncate">{{ store.selectedConversation && store.selectedConversation.title }}</div>
            </span>
          </span>
          <span class="pointer-events-none absolute inset-y-0 right-0 ml-3 flex items-center pr-2">
            <ChevronUpDownIcon class="h-5 w-5 text-field-active-foreground" aria-hidden="true" />
          </span>
        </ListboxButton>
        <transition leave-active-class="transition ease-in duration-100" leave-from-class="opacity-100"
          leave-to-class="opacity-0">
          <ListboxOptions
            class="absolute z-10 mt-1 max-h-80 w-full overflow-auto rounded-md bg-field-default border border-field-active py-1 shadow-lg ring-1 ring-black ring-opacity-10 focus:outline-none divide-y divide-field-divide">
            <h2 v-if="spaceConversations.length > 0" class="my-4 px-3 text-xs font-semibold text-field-focused-foreground">In {{ store.selectedSpace.name }}</h2>
            <ListboxOption as="template" v-for="conversation in spaceConversations" :key="conversation.id"
              :value="conversation.id" v-slot="{ active, selected }">
              <li
                :class="[active ? 'bg-field-active text-field-active-foreground' : 'text-field-focused-foreground', 'relative cursor-default select-none py-2 pl-3 pr-9']">
                <div class="flex items-center text-sm">
                  <Icon :icon="conversation.preset.icon ? conversation.preset.icon : 'heroicons:user-solid'" class="mt-0.5 h-5 w-5 mr-2 opacity-70" />
                  <div class="flex flex-col items-start justify-center">
                    <span :class="[selected ? 'font-semibold' : 'font-semibold', 'block truncate w-[13rem]']">{{
                      conversation.title }}</span>
                    <div :class="['opacity-70 truncate w-[13rem]']">{{ conversation.excerpt ? conversation.excerpt : 'No messages, yet!' }}</div>
                  </div>
                </div>
                <span v-if="selected"
                  :class="[active ? 'text-white' : 'text-nearypink-300', 'absolute inset-y-0 right-0 flex items-center pr-4']">
                  <CheckIcon class="h-5 w-5" aria-hidden="true" />
                </span>
              </li>
            </ListboxOption>
            <h2 class="py-4 px-3 text-xs font-semibold text-field-focused-foreground">All Conversations</h2>
            <ListboxOption as="template" v-for="conversation in nonSpaceConversations" :key="conversation.id"
              :value="conversation.id" v-slot="{ active, selected }">
              <li
                :class="[active ? 'bg-field-active text-field-active-foreground' : 'text-field-focused-foreground', 'relative cursor-default select-none py-2 pl-3 pr-9']">
                <div class="flex items-start text-sm">
                  <Icon :icon="conversation.preset.icon ? conversation.preset.icon : 'heroicons:user-solid'" class="mt-0.5 h-5 w-5 mr-2 opacity-70" />
                  <div class="flex flex-col items-start justify-center">
                    <span :class="[selected ? 'font-semibold' : 'font-semibold', 'block truncate w-[13rem]']">{{
                      conversation.title }}</span>
                    <div :class="[active ? 'text-field-active-foreground' : '', 'opacity-70 truncate w-[13rem]']">{{ conversation.excerpt ? conversation.excerpt : 'No messages, yet!' }}</div>
                  </div>
                </div>
                <span v-if="selected"
                  :class="[active ? 'text-white' : 'text-nearypink-300', 'absolute inset-y-0 right-0 flex items-center pr-4']">
                  <CheckIcon class="h-5 w-5" aria-hidden="true" />
                </span>
              </li>
            </ListboxOption>
          </ListboxOptions>
        </transition>
      </div>
    </Listbox>
    <div @click="store.createConversation(store.selectedSpaceId)"
      class="cursor-pointer flex items-center justify-center text-slate-300 hover:text-slate-100 px-3">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"
        class="-mr-3.5 w-7 h-7 sm:w-6 sm:h-6">
        <path
          d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z" />
      </svg>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useAppStore } from '@/store/index.js';
import { Icon } from '@iconify/vue';
import {
  Listbox,
  ListboxButton,
  ListboxOptions,
  ListboxOption,
} from '@headlessui/vue';
import {
  CheckIcon,
  ChevronUpDownIcon,
} from '@heroicons/vue/24/solid';

const store = useAppStore();

const selectedOptionId = ref(null);

const spaceConversations = computed(() => {
  let convs;
  if (store.selectedSpace) {
    convs = store.selectedSpace.conversations.map(id => store.conversations[id]);
  } else {
    convs = [];
  }

  return convs.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
});

const nonSpaceConversations = computed(() => {
  let convs;
  if (store.selectedSpace) {
    convs = Object.values(store.conversations)
      .filter(conversation => !store.selectedSpace.conversations.includes(conversation.id));
  } else {
    convs = Object.values(store.conversations);
  }

  return convs.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
});


watch(
  () => selectedOptionId.value,
  (newValue,) => {
    store.loadConversation(newValue);
  }
);
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}

.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}</style>