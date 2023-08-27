<template>
    <div
        :class="['flex w-full items-center justify-between gap-3 text-sm rounded-lg text-field-default-foreground', active ? 'ring-2 ring-nearycyan-500' : '', bgColor, padding]">
        <div class="flex items-start gap-4">
            <div class="flex-1 text-nearygray-500">
                <slot name="icon"></slot>
            </div>
            <div class="text-nearygray-400 font-semibold">
                <slot></slot>
            </div>
        </div>
        <div class="shrink-0">
            <slot name="button"></slot>
        </div>
    </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useAppStore } from '@/store/index.js';

const store = useAppStore();
const router = useRouter();

const props = defineProps({
    bgColor: {
        type: String,
        default: "bg-field-default"
    },
    padding: {
        type: String,
        default: "py-4 px-4"
    },
    active: {
        type: Boolean,
        default: false
    },
});

</script>