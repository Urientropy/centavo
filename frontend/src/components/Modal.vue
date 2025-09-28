<template>
  <TransitionRoot appear :show="show" as="template">
    <Dialog as="div" @close="closeModal" class="relative z-50">
      <TransitionChild
        as="template"
        enter="duration-300 ease-out"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="duration-200 ease-in"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black/40 backdrop-blur-sm" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4 text-center">
          <TransitionChild
            as="template"
            enter="duration-300 ease-out"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="duration-200 ease-in"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel
              class="w-full transform overflow-hidden rounded-xl bg-white p-6 text-left align-middle transition-all border-2 border-gray-graphite"
              :class="[
                { 'shadow-[8px_8px_0px_#4F46E5]': color === 'indigo' },
                { 'shadow-[8px_8px_0px_#EC4899]': color === 'magenta' },
                { 'shadow-[8px_8px_0px_#1F2937]': color === 'gris_grafito' },
                { 'max-w-md': size === 'md' },
                { 'max-w-xl': size === 'xl' },
                { 'max-w-2xl': size === '2xl' },
                { 'max-w-4xl': size === '4xl' },
                { 'max-w-5xl': size === '5xl' }, // <-- NUEVA LÍNEA
              ]"
            >
              <DialogTitle as="h3" class="text-2xl font-display font-bold leading-6 text-gray-graphite flex justify-between items-center">
                <span>{{ title }}</span>
                <button @click="closeModal" class="p-1 rounded-full hover:bg-gray-graphite/10 transition-colors">
                  <XMarkIcon class="h-6 w-6" />
                </button>
              </DialogTitle>
              <div class="mt-4">
                <slot />
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup>
import {
  TransitionRoot,
  TransitionChild,
  Dialog,
  DialogPanel,
  DialogTitle,
} from '@headlessui/vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  show: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: 'Modal Title',
  },
  color: {
    type: String,
    default: 'gris_grafito' // 'indigo' o 'magenta' o 'gris_grafito'
  },
  size: {
    type: String,
    default: '2xl' // md, xl, 2xl, 4xl, 5xl
  }
})

const emit = defineEmits(['close'])

function closeModal() {
  emit('close')
}
</script>