<template>
    <div
        :class="['flex w-full text-sm rounded-md text-field-default-foreground', outerFlex, active ? 'ring-2 ring-nearycyan-500' : '', bgColor, padding]">
        <div :class="['flex', flex]">
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
        default: "py-3 px-3"
    },
    flex: {
        type: String,
        default: "items-center gap-4"
    },
    outerFlex: {
        type: String,
        default: "items-center justify-between gap-3"
    },
    active: {
        type: Boolean,
        default: false
    },
});

</script>