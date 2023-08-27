<template>
    <TransitionRoot as="template" :show="isOpen">
        <Dialog as="div" class="relative z-10" @close="cancel">
            <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100"
                leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
                <div class="fixed inset-0 bg-nearyblue-300 bg-opacity-75 transition-opacity" />
            </TransitionChild>
            <div class="fixed inset-0 z-10 overflow-y-auto">
                <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
                    <TransitionChild as="template" enter="ease-out duration-300"
                        enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                        enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200"
                        leave-from="opacity-100 translate-y-0 sm:scale-100"
                        leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
                        <DialogPanel
                            class="relative transform overflow-hidden rounded-lg bg-nearyblue-50 w-72 px-8 py-8 text-left shadow-xl transition-all">
                            <div>
                                <div class="text-center">
                                    <!-- Named slot for the title -->
                                    <slot name="title">
                                        <DialogTitle as="h3" class="font-semibold text-lg text-field-default-foreground">{{ modalTitle }}</DialogTitle>
                                    </slot>
                                    <!-- Default slot for the content -->
                                    <slot></slot>
                                </div>
                            </div>
                            <div class="flex gap-3 items-center justify-center mt-5">
                                <!-- Named slot for the buttons -->
                                <slot name="buttons"></slot>
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
});

const emit = defineEmits(['close']);

const cancel = () => {
    emit('close');
};
</script>