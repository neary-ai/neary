<template>
    <Listbox as="div" v-slot={open} v-model="selected">
        <div class="relative">
            <ListboxButton
                :class="[open ? 'border-field-focused' : 'border-transparent', 'bg-field-default text-field-default-foreground border relative w-full cursor-default rounded-md py-1.5 pl-3 pr-10 text-left shadow-sm focus:outline-none text-sm leading-6']">
                <span class="block truncate">{{ selected.option }}</span>
                <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
                    <ChevronUpDownIcon class="h-5 w-5 text-field-default-foreground" aria-hidden="true" />
                </span>
            </ListboxButton>

            <transition leave-active-class="transition ease-in duration-100" leave-from-class="opacity-100"
                leave-to-class="opacity-0">
                <ListboxOptions
                    class="border border-field-focused divide-y divide-field-divide absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-field-default text-field-default-foreground py-1 text-base shadow-lg focus:outline-none sm:text-sm">
                    <ListboxOption as="template" v-for="item in options" :key="item.value" :value="item"
                        v-slot="{ active, selected }">
                        <li
                            :class="[active ? 'bg-field-active text-field-active-foreground font-medium' : '', 'relative cursor-default select-none py-2 pl-3 pr-9']">
                            <span :class="['block truncate']">{{ item.option}}</span>
                        </li>
                    </ListboxOption>
                </ListboxOptions>
            </transition>
        </div>
    </Listbox>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { Listbox, ListboxButton, ListboxOption, ListboxOptions } from '@headlessui/vue'
import { ChevronUpDownIcon } from '@heroicons/vue/20/solid'

const props = defineProps({
  options: {
    type: Array,
    default: [{'option': null, 'value': null}],
  },
  value: {
    type: [String, Number],
    default: '',
  },
});

let selected = ref({'option': null, 'value': null})
const emit = defineEmits(['updateInput'])

watch(() => props.value, (newVal) => {
  selected.value = props.options.find(option => option.value === newVal) || {'option': '', 'value': ''}
})

watch(selected, (newVal, oldVal) => {
  if (oldVal && oldVal.value && oldVal.value != newVal.value) {
    emit('updateInput', newVal.value)
  }
}, { immediate: true })

onMounted(() => {
  selected.value = props.options.find(option => option.value === props.value) || {'option': '', 'value': ''}
})
</script>