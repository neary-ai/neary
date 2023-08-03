<template>
  <div id="documents-window" class="flex flex-col gap-3 max-w-3xl overflow-y-scroll">
    <div class="p-8 pt-[5.5rem]">
      <SectionHeading section-name="Documents" @on-click="onBackButtonClick" />
      <ManageDocuments v-if="!showAddDocuments" @toggledocs="toggleAddDocs"></ManageDocuments>
      <AddDocument v-if="showAddDocuments"></AddDocument>
    </div>
  </div>
</template>
  
<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import AddDocument from './AddDocument.vue';
import ManageDocuments from './ManageDocuments.vue';
import SectionHeading from './common/SectionHeading.vue';
import { useAppStore } from '@/store/index.js';

const store = useAppStore();
const router = useRouter();

const showAddDocuments = ref(false);

const toggleAddDocs = () => {
  showAddDocuments.value = !showAddDocuments.value;
};

const onBackButtonClick = () => {
  if (showAddDocuments.value) {
    toggleAddDocs();
  } else {
    router.go(-1);
  }
};

</script>
  