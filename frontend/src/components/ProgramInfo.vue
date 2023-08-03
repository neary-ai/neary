<template>
    <div id="alt-window" class="font-mulish flex flex-col gap-3 max-w-3xl overflow-y-scroll">
        <div class="p-8 pt-[5.5rem]">
            <SectionHeading section-name="prop.programName" @on-click="onBackButtonClick" />
            <div class="mt-6">
                <div v-if="programData" class="space-y-4">
                    <template v-for="program in programData.options" :key="program.value">
                        <div class='relative cursor-pointer rounded-lg border border-transparent bg-neutral-500 px-6 py-4 shadow-sm focus:outline-none max-w-xl'>
                            <span class="flex items-center justify-between">
                                <span class="flex items-center justify-start text-sm">
                                    <component :is="iconComponents[program.icon]"
                                        class="h-6 w-6 mr-4 text-nearygray-200/80" />
                                    <div class="flex flex-col">
                                        <span class="font-medium text-nearygray-50 mb-0.5">{{ program.option }}</span>
                                        <span class="text-nearygray-400">{{program.description }}</span>
                                    </div>
                                </span>
                                <button @click="updateProgram(program.value)" type="button" :class="[selectedProgram && selectedProgram.value === program.value ? 'bg-nearypink-300/80 text-white' : 'bg-nearyblue-50 text-nearygray-200', 'w-24 shrink-0 px-3 py-2 ml-4 text-sm rounded']">
                                    <span v-if="selectedProgram && selectedProgram.value === program.value">Deactivate</span>
                                    <span v-else>Activate</span>
                                </button>
                            </span>
                        </div>
                    </template>
                </div>
            </div>
        </div>
    </div>
</template>


<script setup>
// Holding place for individual program descriptions
import { onMounted, ref, watch, nextTick, computed } from 'vue';
import { useAppStore } from '@/store/index.js';

const store = useAppStore();

const props = defineProps({
    message: Object,
    chatWindowHeight: Number,
  });

<template>
    <div v-if="store.currentMessage" class="text-slate-400 w-full h-screen flex flex-col items-center start mt-14 px-8">
        <div class="w-12 h-12 rounded-full flex items-center justify-center bg-slate-500/80">
            <component v-if="iconComponents" :is="iconComponents[selectedProgram.icon]"
                class="h-7 w-7 text-nearyblue-300" />
        </div>
        <div class="text-xl mt-4 text-slate-400">{{ selectedProgram.option }}</div>
        <div class="max-w-sm text-slate-500 mt-6">
            Upload documents in the Documents section, then ask Neary questions about them. Quick tips:
            <ul class="list-disc pl-8 mt-5 space-y-2">
                <li class="font-medium">Keep conversations thematically similar</li>
                <li class="font-medium">Fewer, denser documents perform better</li>
                <li class="font-medium">Use descriptive questions</li>
            </ul>
        </div>
    </div>
</template>