<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Upload, FileText } from 'lucide-vue-next'
import { Card } from '@/components/ui/card'

const { t } = useI18n()
const emit = defineEmits(['file-selected'])
const isDragging = ref(false)
const file = ref(null)

const handleDrop = (e) => {
  isDragging.value = false
  e.preventDefault()
  const droppedFile = e.dataTransfer.files[0]
  if (droppedFile) {
    // Check if it's a PDF by extension or MIME type
    const isPdf = droppedFile.type === 'application/pdf' || 
                  droppedFile.name.toLowerCase().endsWith('.pdf')
    if (isPdf) {
      file.value = droppedFile
      emit('file-selected', droppedFile)
    }
  }
}

const handleDragOver = (e) => {
  e.preventDefault()
  isDragging.value = true
}

const handleDragLeave = () => {
  isDragging.value = false
}

const handleFileSelect = (e) => {
  const selectedFile = e.target.files[0]
  if (selectedFile) {
    // Check if it's a PDF by extension or MIME type (accept attribute should filter, but double-check)
    const isPdf = selectedFile.type === 'application/pdf' || 
                  selectedFile.name.toLowerCase().endsWith('.pdf')
    if (isPdf) {
      file.value = selectedFile
      emit('file-selected', selectedFile)
    }
  }
}
</script>

<template>
  <div class="w-full mt-2">
    <div
      class="relative flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-lg cursor-pointer transition-colors"
      :class="[
        isDragging ? 'border-primary bg-primary/5' : 'border-muted-foreground/25 hover:border-primary/50 hover:bg-muted/50',
        file ? 'border-primary bg-primary/5' : ''
      ]"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @drop.prevent="handleDrop"
      @click="$refs.fileInput.click()"
    >
      <input
        ref="fileInput"
        type="file"
        class="hidden"
        accept=".pdf"
        @change="handleFileSelect"
      />
      
      <div v-if="!file" class="flex flex-col items-center justify-center pt-5 pb-6 text-center">
        <div class="p-4 mb-4 rounded-full bg-primary/10">
          <Upload class="w-8 h-8 text-primary" />
        </div>
        <p class="mb-2 text-sm font-medium text-foreground">
          <span class="font-semibold">{{ t('fileSelector.clickToUpload') }}</span> {{ t('fileSelector.dragAndDrop') }}
        </p>
        <p class="text-xs text-muted-foreground">{{ t('fileSelector.subtitle') }}</p>
      </div>

      <div v-else class="flex flex-col items-center justify-center pt-5 pb-6 text-center">
        <div class="p-4 mb-4 rounded-full bg-primary/10">
          <FileText class="w-8 h-8 text-primary" />
        </div>
        <p class="mb-2 text-sm font-medium text-foreground">
          {{ file.name }}
        </p>
        <p class="text-xs text-muted-foreground">
          {{ (file.size / 1024 / 1024).toFixed(2) }} MB
        </p>
      </div>
    </div>
  </div>
</template>
