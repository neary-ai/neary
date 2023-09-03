<template>
  <Transition>
    <div v-if="store.notification" class="absolute left-0 right-0 bottom-[3rem] flex justify-center">
      <div :class="[store.notification.message.length >= 45 ? 'rounded-lg px-4 py-3' : 'rounded-full px-4 py-2', 'flex flex-shrink-0 items-center justify-between text-sm shadow ring-1 ring-nearyblue-300 max-w-sm', store.notification.type == 'tool_start' || store.notification.type == 'tool_success' ? 'bg-nearycyan-400 font-semibold' : 'bg-nearypink-300 text-white']">
        <Icon icon="line-md:loading-twotone-loop" v-if="type == 'tool_start'" class="flex-shrink-0 cursor-pointer mr-1 w-5 h-5" />
        <Icon icon="line-md:confirm-circle" v-else-if="type == 'tool_success'" class="flex-shrink-0 cursor-pointer mr-1 w-5 h-5" />
        <Icon icon="line-md:remove" v-else-if="type == 'tool_error'" class="flex-shrink-0 cursor-pointer mr-1 w-5 h-5" />
        <div>{{ message }}</div>
        <Icon icon="heroicons:x-mark-20-solid" v-if="sticky" @click="store.notification = null;"
          class="flex-shrink-0 cursor-pointer ml-1.5 w-4 h-4 text-white/60" />
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { computed } from 'vue';
import { Icon } from '@iconify/vue';
import { useAppStore } from '@/store/index.js';

const store = useAppStore();

const type = computed(() => {
  if (store.notification) {
    return store.notification.type
  }
  else return null;
})

const message = computed(() => {
  if (store.notification) {
    return store.notification.message
  }
  else return null;
})

const sticky = computed(() => {
  if (store.notification) {
    return store.notification.sticky
  }
  else return null;
})
</script>

<style>
.v-enter-active,
.v-leave-active {
  transition: opacity 0.3s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}
</style>