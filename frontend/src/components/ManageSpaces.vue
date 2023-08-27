<template>
  <div id="spaces-window" class="flex flex-col gap-3 max-w-3xl overflow-y-scroll">
    <div class="p-8 pt-[5.5rem]">
      <div class="flex items-center justify-between">
        <SectionHeading section-name="Spaces" @on-click="onBackButtonClick" />
        <Button v-if="hasSpaces" @buttonClick="newSpace" button-type="btn-pink">
          <div class="flex items-center gap-1 pr-1.5">
            <PlusIcon class="w-5 h-5" />
            New Space
          </div>
        </Button>
      </div>
      <ul v-if="hasSpaces" class="divide-y divide-slate-700 text-slate-400 mt-6">
        <template v-for="space in Object.values(store.spaces)">
          <li v-if="space.id != -1" :key="space.id" class="flex items-center justify-between px-6 py-4">
            <div @click="store.loadSpace(space.id)" class="leading-7 cursor-pointer">
              <div class="font-semibold text-nearygray-50">{{ space.name }}</div>
              <div class="text-nearygray-50/70 text-sm">{{ space.conversations.length }} conversations</div>
            </div>
            <div class="cursor-pointer text-nearygray-50 flex items-center gap-3">
              <PencilSquareIcon @click="editSpace(space.id)" class="w-6 h-6" />
              <XMarkIcon @click="store.deleteSpace(space.id)" class="w-6 h-6" />
            </div>
          </li>
        </template>
      </ul>
      <div v-else class="flex items-center justify-center max-w-lg">
        <div class="text-center py-12 px-14 mt-12 rounded-lg border-2 border-dashed border-neutral-100">
          <Square3Stack3DIcon class="mx-auto h-12 w-12 text-nearygray-200 mb-4" />
          <h3 class="mt-2 text-sm font-semibold text-nearygray-50">Organize your conversations</h3>
          <p class="mt-1 text-sm text-nearygray-300">Create your first space</p>
          <div class="mt-6">
            <Button @buttonClick="newSpace" button-type="btn-pink">
              <div class="flex items-center gap-1 pr-1.5">
                <PlusIcon class="w-5 h-5" />
                New Space
              </div>
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
  <Modal :isOpen="isOpen" @save="save" @close="close">
    <template v-slot:title>
      <h3 class="font-semibold text-lg text-field-default-foreground">{{ modalTitle }}</h3>
    </template>
    <div class="flex-grow w-full my-5">
      <div>
        <input v-model="spaceName" type="text" placeholder="What should we call it?"
          class="focus:ring-0 focus:border-nearyblue-300 border border-transparent rounded-md bg-nearygray-100 text-sm w-full px-3 py-2" />
      </div>
    </div>
    <template v-slot:buttons>
      <Button @buttonClick="save" button-type="btn-light">Save</Button>
      <Button @buttonClick="close" button-type="btn-light">Cancel</Button>
    </template>
  </Modal>
</template>
  
<script setup>
import { ref, computed } from 'vue';
import Button from './common/Button.vue';
import Modal from './common/Modal.vue';
import SectionHeading from './common/SectionHeading.vue';
import api from '@/services/apiService';
import { useAppStore } from '@/store/index.js';
import { useRouter } from 'vue-router';
import { PlusIcon } from '@heroicons/vue/20/solid';
import { Square3Stack3DIcon, PencilSquareIcon, XMarkIcon } from '@heroicons/vue/24/outline';

const store = useAppStore();
const router = useRouter();

const hasSpaces = computed(() => {
  return Object.keys(store.spaces).length > 1;
})

// Create / edit space Modal

const modalTitle = ref(null)
const space = ref(null)
const spaceName = ref(null)
const isOpen = ref(false)

const editSpace = (index) => {
  modalTitle.value = 'Edit Space';
  space.value = store.spaces[index];
  spaceName.value = space.value.name;
  isOpen.value = true;
};

const newSpace = () => {
  modalTitle.value = 'New Space';
  space.value = null;
  spaceName.value = null;
  isOpen.value = true;
};

const save = async () => {
  isOpen.value = false;
  try {
    if (!space.value) {
      const newSpace = await api.createSpace(spaceName.value);
      store.spaces[newSpace.id] = newSpace
      store.loadSpace(newSpace.id);
    } else {
      await store.updateSpace(space.id, space.name);
    }
  } catch (error) {
    console.error('Error updating space:', error);
  }
};

const close = () => {
  isOpen.value = false;
};

// Methods
const onBackButtonClick = () => {
  router.go(-1);
};

</script>