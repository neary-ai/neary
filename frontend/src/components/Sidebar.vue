<template>
  <!-- Sidebar -->
  <aside v-show="store.sidebarOpen"
    class="z-10 hidden fixed sm:flex sm:flex-col h-full pb-4 pt-[4.5rem] bg-nearyblue-300 border-r border-slate-400/10 shadow-lg w-44 items-center justify-between">
    <Spaces />
    <div class="flex gap-3 items-center justify-between text-slate-400/80">
      <Icon icon="heroicons:squares-2x2-solid" @click="toggleManageSpaces()" class="hover:text-slate-300/80 cursor-pointer w-5 h-5" />
      <Icon icon="heroicons:cog-6-tooth-solid" @click="toggleSetup()" class="hover:text-slate-300/80 cursor-pointer w-5 h-5" />
      <Icon icon="heroicons:user-solid" @click="toggleAccount()" class="hover:text-slate-300/80 cursor-pointer w-5 h-5" />
      <Icon icon="heroicons:bookmark-solid" @click="toggleBookmarks()" class="hover:text-slate-300/80 cursor-pointer w-5 h-5" />
    </div>
  </aside>
  <!-- Compact slide-over -->
  <TransitionRoot v-if="store.isMobile" class="block sm:hidden" as="template" :show="store.sidebarOpen">
    <Dialog as="div" class="fixed inset-0 overflow-hidden z-50" @close="toggleSidebar('close')">
      <div class="fixed inset-0 bg-nearyblue-400/50" aria-hidden="true" />
      <div class="absolute inset-0 overflow-hidden">
        <div class="absolute inset-0">
          <div class="fixed inset-y-0 left-0 flex max-w-full">
            <TransitionChild as="template" enter="transform transition ease-in-out duration-500 sm:duration-700"
              enter-from="-translate-x-full" enter-to="translate-x-0"
              leave="transform transition ease-in-out duration-500 sm:duration-700" leave-from="translate-x-0"
              leave-to="-translate-x-full">
              <DialogPanel class="w-60 bg-nearyblue-200 flex flex-col items-start justify-between shadow-xl">
                <div class="w-full">
                  <div class="w-full flex items-start justify-between p-6 px-4">
                    <img @click="router.push('/');" :src="logo" class="w-[5rem]" />
                    <button type="button"
                      class="rounded-md text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-0"
                      @click="toggleSidebar('close')">
                      <span class="sr-only">Close panel</span>
                      <Icon icon="heroicons:x-mark-20-solid" class="h-5 w-5 text-nearygray-400" aria-hidden="true" />
                    </button>
                  </div>
                  <Spaces />
                </div>
                <div class="flex gap-3 items-center justify-center text-slate-400/80 w-full pb-4">
                  <Icon icon="heroicons:squares-2x2-solid" @click="toggleManageSpaces()" class="cursor-pointer w-5 h-5" />
                  <Icon icon="heroicons:user-solid" @click="toggleSetup()" class="cursor-pointer w-5 h-5" />
                  <Icon icon="heroicons:cog-6-tooth-solid" @click="toggleAccount()" class="cursor-pointer w-5 h-5" />
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>
<script setup>
import Spaces from './Spaces.vue';
import logo from '@/assets/images/neary.svg';
import { Icon } from '@iconify/vue';
import { Dialog, DialogPanel, TransitionRoot, TransitionChild } from '@headlessui/vue';
import { useAppStore } from '@/store/index.js';
import { useRouter } from 'vue-router';

const store = useAppStore();
const router = useRouter();

const toggleSidebar = () => {
  store.toggleSidebar();
};

const toggleManageSpaces = () => {
  if (router.currentRoute.value.path.startsWith('/spaces')) {
    router.go(-1);
  } else {
    router.push(`/spaces`);
  }

  if (store.isMobile) {
    store.toggleSidebar();
  }
};

const toggleAccount = () => {
  if (router.currentRoute.value.path.startsWith('/account')) {
    router.go(-1);
  } else {
    router.push(`/account`);
  }

  if (store.isMobile) {
    store.toggleSidebar();
  }
};

const toggleSetup = () => {
  if (router.currentRoute.value.path.startsWith('/setup')) {
    router.go(-1);
  } else {
    router.push(`/setup`);
  }

  if (store.isMobile) {
    store.toggleSidebar();
  }
};

const toggleBookmarks = () => {
  if (router.currentRoute.value.path.startsWith('/bookmarks')) {
    router.go(-1);
  } else {
    router.push(`/bookmarks`);
  }

  if (store.isMobile) {
    store.toggleSidebar();
  }
};

</script>

<style scoped>
.custom-slideover {
  top: 20px;
  bottom: 20px;
}
</style>
