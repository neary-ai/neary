<template>
  <Transition>
    <div v-if="store.notification" class="absolute left-0 right-0 bottom-[3rem] flex justify-center">
      <div
        class="flex flex-shrink-0 items-center justify-between bg-nearypink-300 text-sm text-white px-4 py-2 rounded-full shadow ring-1 ring-nearyblue-300 max-w-sm">
        <div>{{ message }}</div>
        <XMarkIcon v-if="sticky" @click="store.notification = null;"
          class="flex-shrink-0 cursor-pointer ml-1.5 w-4 h-4 text-white/60" />
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { computed } from 'vue';
import { useAppStore } from '@/store/index.js';
import { XMarkIcon } from '@heroicons/vue/20/solid';

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