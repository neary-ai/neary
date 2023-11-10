<template>
  <div class="flex flex-1 flex-col overflow-y-scroll w-full truncate">
    <ul role="list" class="space-y-3">
      <li>
        <div @click="loadSpace(null)"
          :class="[!store.selectedSpaceId ? 'bg-nearyblue-50 text-slate-100' : 'text-nearygray-200 hover:bg-nearygray-200/10', 'cursor-pointer group flex gap-x-3 rounded-r-full mr-4 py-1.5 pr-2 pl-4 text-sm leading-6']">
          All
          <span
            class="ml-auto w-8 min-w-max whitespace-nowrap rounded-full px-2 py-0.5 text-center text-xs font-medium leading-5 bg-nearygray-50/10"
            aria-hidden="true">{{ Object.keys(store.conversations).length }}</span>
        </div>
      </li>
      <template v-for="space in Object.values(store.spaces)">
        <li v-if="space.id != -1" :key="space.id">
          <div @click="loadSpace(space.id)"
            :class="[space.id === store.selectedSpaceId ? 'bg-nearyblue-50 text-slate-100' : 'text-nearygray-200 hover:bg-nearygray-200/10', 'cursor-pointer group flex gap-x-3 rounded-r-full mr-4 py-1.5 pr-2 pl-4 text-sm leading-6']">
            <span class="truncate">{{ space.name }}</span>
            <span
              class="shrink-0 ml-auto w-8 min-w-max whitespace-nowrap rounded-full px-2 py-0.5 text-center text-xs font-medium leading-5 bg-nearygray-50/10"
              aria-hidden="true">{{ space.conversation_ids.length }}</span>
          </div>
        </li>
      </template>
    </ul>
  </div>
</template>

<script setup>
import { useAppStore } from '@/store/index.js';

const store = useAppStore();

const loadSpace = (spaceId) => {
  store.loadSpace(spaceId);
  if (store.isMobile) {
    store.toggleSidebar();
  }
}

</script>