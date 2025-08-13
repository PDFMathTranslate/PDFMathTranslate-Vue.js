<template>
  <section class="card">
    <div class="grid sm:grid-cols-2 lg:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm text-accent-500 font-bold mb-1">Translate from</label>
        <select :value="langIn" @change="onChangeLangIn" class="w-full rounded-lg border-slate-100 dark:border-slate-600 bg-white dark:bg-slate-900 text-accent-500 ">
          <option v-for="(code, name) in langOptions" :key="name" :value="code">{{ name }}</option>
        </select>
      </div>
      <div>
        <label class="block text-sm font-medium font-bold mb-1" text-accent-500 >To</label>
        <select :value="langOut" @change="onChangeLangOut" class="w-full rounded-lg  border-slate-100 dark:border-slate-600 bg-white dark:bg-slate-900">
          <option v-for="(code, name) in langOptions" :key="name" :value="code">{{ name }}</option>
        </select>
      </div>
      <div class="sm:col-span-2 flex items-end gap-3">
        <div
          class="group relative w-full border-2 border-dashed rounded-lg p-4 cursor-pointer bg-slate-100 text-sm text-slate-600 dark:text-slate-300 hover:border-accent-500 hover:bg-slate-300dark:hover:border-accent-500"
          :class="{ 'border-accent-500 bg-accent-50/40 dark:bg-accent-900/20': isDragOver }"
          @click="openChooser"
          @dragenter.prevent="onDragEnter"
          @dragover.prevent="onDragOver"
          @dragleave.prevent="onDragLeave"
          @drop.prevent="onDrop"
        >
          <div class="flex items-center justify-center min-h-[16rem]">
            <span class="pointer-events-none transition-opacity duration-150 group-hover:opacity-0 text-slate-300 ">Click or drop PDF(s) here</span>
          </div>
          <div class="pointer-events-none absolute inset-0 hidden items-center justify-center group-hover:flex bg-slate-200 ">
            <span class=" text-slate-500 ">Only .pdf files are accepted</span>
          </div>
          <input ref="fileInput" class="sr-only" type="file" accept="application/pdf" multiple @change="onInputChange" />
        </div>
        <!-- <button class="btn btn-primary" :disabled="!hasFiles || !hasPending" @click="$emit('start-all')">Start</button>
        <button class="btn btn-outline" :disabled="!isWorking" @click="$emit('cancel-all')">Cancel</button> -->
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { defineProps, defineEmits, ref } from 'vue'
import type { LanguageOptions } from '../types'

const props = defineProps<{
  langIn: string
  langOut: string
  langOptions: LanguageOptions
  hasPending: boolean
  isWorking: boolean
  hasFiles: boolean
}>()

const emit = defineEmits<{
  (e: 'update:langIn', value: string): void
  (e: 'update:langOut', value: string): void
  (e: 'files-selected', files: File[]): void
  (e: 'start-all'): void
  (e: 'cancel-all'): void
}>()

function onChangeLangIn(e: Event) {
  const target = e.target as HTMLSelectElement
  emit('update:langIn', target.value)
}

function onChangeLangOut(e: Event) {
  const target = e.target as HTMLSelectElement
  emit('update:langOut', target.value)
}

const fileInput = ref<HTMLInputElement | null>(null)
const isDragOver = ref(false)

function openChooser() {
  fileInput.value?.click()
}

function onInputChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (!input.files) return
  const files = Array.from(input.files).filter(isPdf)
  if (files.length) emit('files-selected', files)
  input.value = ''
}

function onDragEnter() {
  isDragOver.value = true
}

function onDragOver() {
  isDragOver.value = true
}

function onDragLeave() {
  isDragOver.value = false
}

function onDrop(e: DragEvent) {
  isDragOver.value = false
  if (!e.dataTransfer) return
  const files = Array.from(e.dataTransfer.files).filter(isPdf)
  if (files.length) emit('files-selected', files)
}

function isPdf(f: File) {
  return f && (f.type === 'application/pdf' || /\.pdf$/i.test(f.name))
}
</script>


