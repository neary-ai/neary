<template>
    <TransitionRoot as="template" :show="isOpen">
        <Dialog as="div" class="relative z-10" @close="cancel">
            <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100"
                leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
                <div class="fixed inset-0 bg-nearyblue-300 bg-opacity-80 transition-opacity" />
            </TransitionChild>
            <div class="fixed inset-0 z-10 overflow-y-auto">
                <div class="flex min-h-full items-center justify-center p-4 text-center sm:p-0">
                    <TransitionChild as="template" enter="ease-out duration-300"
                        enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                        enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200"
                        leave-from="opacity-100 translate-y-0 sm:scale-100"
                        leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
                        <DialogPanel
                            class="relative transform flex flex-col overflow-hidden rounded-lg border border-neutral-200 bg-neutral-400 w-72 px-8 py-6 text-left shadow-xl transition-all">
                            <div class="flex items-center justify-between text-base font-semibold text-field-default-foreground mb-2">
                                <slot name="title">
                                    <DialogTitle>{{ modalTitle }}</DialogTitle>
                                </slot>
                                <Icon @click="cancel" icon="heroicons:x-mark" class="cursor-pointer w-5 h-5 -mr-1" />
                            </div>
                            <div>
                                <slot>

                                </slot>
                            </div>
                            <div class="flex gap-2 items-center justify-start mt-2 w-full">
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
import { Icon } from '@iconify/vue';
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