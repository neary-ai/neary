<template>
  <div class="text-nearygray-100 py-5 text-sm">
    To add new documents, enter a URL or upload a text file using the form below.
  </div>
  <div class="container mx-auto pb-4 pt-2 text-sm">
    <form @submit.prevent="uploadDocument" class="text-field-label">
      <div class="mb-4">
        <label for="url" class="block mb-2 font-semibold">Enter URL:</label>
        <input type="url" id="url" name="url" placeholder="https://www.example.com/article"
          class="text-field-default-foreground text-sm placeholder:text-field-default-foreground/60 bg-field-default w-full px-3 py-2 border border-nearyblue-100 rounded-md focus:outline-none focus:border-field-active focus:ring-0"
          v-model="url" @input="clearFile">
      </div>
      <p class="text-center font-semibold">- OR -</p>
      <div class="mb-8">
        <label for="file" class="block mb-2 font-semibold">Drag and drop a file:</label>
        <div id="dragArea"
          class="bg-field-default rounded-md border border-nearyblue-100 text-field-default-foreground w-full h-40 flex items-center justify-center text-center drag-area"
          @click="triggerFileInput" @dragover.prevent="handleDragOver" @dragleave="handleDragLeave"
          @drop.prevent="handleDrop">
          <div v-if="!fileName">
            <div>Drop your file here or click to select a file</div>
            <div class="text-sm text-field-default-foreground/60 mt-2">Supported formats: text, pdf</div>
          </div>
          <span v-else>{{ fileName }}</span>
          <input type="file" id="file" name="file" class="hidden" ref="fileInput" @change="handleFileInputChange"
            accept=".txt, .pdf, text/plain, application/pdf">
        </div>
      </div>
      <div class="flex items-center gap-3">
        <Button button-type="btn-light" :disabled="isUploading">Add Document</Button>
        <alert ref="alertComponent" v-model="alertData" />
        <Loading v-if="isUploading" />
      </div>
    </form>
  </div>
</template>
  
<script setup>
import { ref } from 'vue';
import { useAppStore } from '@/store/index.js';
import api from '../services/apiService';
import Button from './common/Button.vue';
import Alert from "./common/Alert.vue";
import Loading from "./common/Loading.vue";

const store = useAppStore();

const fileName = ref('');
const fileInput = ref(null);
const url = ref('');

const alertData = ref({});
const alertComponent = ref(null);
const isUploading = ref(false);

const triggerFileInput = () => fileInput.value.click();

const handleDrop = (e) => {
  fileInput.value.files = e.dataTransfer.files;
  fileName.value = e.dataTransfer.files[0].name;
};

const handleFileInputChange = (e) => {
  fileName.value = e.target.files[0].name;
  clearUrl();
};

const clearUrl = () => url.value = '';

const clearFile = () => {
  fileInput.value.value = null;
  fileName.value = '';
};

const uploadDocument = async () => {
  isUploading.value = true;
  try {
    if (url.value) {
      await api.createDocumentFromURL(store.selectedConversationId, url.value);
      alertData.value = { alertType: "success", alertMessage: "Document added!" };
    } else if (fileInput.value.files.length > 0) {
      await api.createDocumentFromFile(store.selectedConversationId, fileInput.value.files[0])
      alertData.value = { alertType: "success", alertMessage: "Document added!" };
    } else {
      console.error("No file or URL provided for upload");
      alertData.value = { alertType: "error", alertMessage: "Nothing to add!" };
    }
  } catch (error) {
    alertData.value = { alertType: "error", alertMessage: error.data.detail };
  } finally {
    clearUrl();
    clearFile();
    isUploading.value = false;
  }
};

</script>