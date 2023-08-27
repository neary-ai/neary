<template>
    <TransitionRoot as="template" :show="isOpen">
        <Dialog as="div" class="relative z-10" @close="cancel">
            <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100"
                leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
                <div class="fixed inset-0 bg-nearyblue-100 bg-opacity-75 transition-opacity" />
            </TransitionChild>
            <div class="fixed inset-0 z-10 overflow-y-auto">
                <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
                    <TransitionChild as="template" enter="ease-out duration-300"
                        enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                        enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200"
                        leave-from="opacity-100 translate-y-0 sm:scale-100"
                        leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
                        <DialogPanel
                            class="relative transform overflow-hidden rounded-lg bg-nearyblue-300 px-8 py-8 text-left shadow-xl transition-all">
                            <div>
                                <div class="text-center">
                                    <DialogTitle as="h3" class="font-semibold text-lg text-field-default-foreground">{{ modalTitle
                                    }}</DialogTitle>
                                    <div class="mt-4 text-left">
                                            <label
                                                class="block text-sm font-medium leading-6 text-field-label">Space Name</label>
                                            <div class="mt-2">
                                                <input v-model="spaceName" type="text"
                                                    class="block w-full text-sm rounded-md border-0 py-2 text-nearyblue-300 bg-nearygray-100 shadow-sm placeholder:text-nearyblue-300/80 focus:border-transparent focus:ring-0 focus:outline-none"
                                                    placeholder="What should we call it?" />
                                            </div>
                                    </div>
                                </div>
                            </div>
                            <div class="flex gap-3 items-center justify-center mt-5">
                                <Button @buttonClick="save" button-type="btn-pink">Save</Button>
                                <Button @buttonClick="cancel" button-type="btn-outline-pink">Cancel</Button>
                            </div>
                        </DialogPanel>
                    </TransitionChild>
                </div>
            </div>
        </Dialog>
    </TransitionRoot>
</template>  
  
<script setup>
import { ref, watch } from 'vue';
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue';
import Button from './Button.vue';

const props = defineProps({
  isOpen: Boolean,
  modalTitle: String,
  space: Object,
});

const spaceName = ref('');

watch(() => props.space, function (newSpace) {
  if (newSpace) {
    spaceName.value = newSpace.name || '';
  } else {
    spaceName.value = '';
  }
}, { immediate: true });

const emit = defineEmits(['save', 'close']);

const save = () => {
  const updatedSpace = props.space ? { ...props.space, name: spaceName.value } : { name: spaceName.value };
  emit('save', updatedSpace);
};

const cancel = () => {
  emit('close');
};


</script>
