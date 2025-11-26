<script setup>
import { ref, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { Upload, FileText, Link as LinkIcon } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const { t } = useI18n()

const props = defineProps({
  source: {
    type: String,
    required: true
  },
  url: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['file-selected', 'update:source', 'update:url'])

const isDragging = ref(false)
const file = ref(null)
const fileInput = ref(null)
const urlInput = ref(null)

watch(() => props.source, async (val) => {
  if (val === 'Link') {
    await nextTick()
    if (urlInput.value?.$el) {
      urlInput.value.$el.focus()
    }
  }
})

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
    <div v-if="source === 'File'">
      <div
        class="file-dropbox relative group flex flex-col items-center justify-center w-full h-96 border-2 border-dashed rounded-lg cursor-pointer transition-all duration-300"
        :class="[
          isDragging ? 'border-primary bg-primary/5' : 'border-muted-foreground/25 hover:border-primary/50 hover:bg-muted/50',
          file ? 'border-primary bg-primary/5' : ''
        ]"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop.prevent="handleDrop"
        @click="fileInput?.click()"
      >
        <input
          ref="fileInput"
          type="file"
          class="hidden"
          accept=".pdf"
          @change="handleFileSelect"
        />
        
        <Transition name="fade" mode="out-in">
          <div v-if="!file" class="flex flex-col items-center justify-center pt-5 pb-6 text-center">
            <div class="p-3 mb-3 rounded-full bg-primary/10 transition-colors duration-300">
              <Upload class="w-6 h-6 text-primary" />
            </div>
            <p class="mb-1 text-sm font-medium text-foreground">
              <span class="font-semibold">{{ t('fileSelector.clickToUpload') }}</span>
            </p>
            <p class="text-xs text-muted-foreground">{{ t('fileSelector.dragAndDrop') }}</p>
          </div>

          <div v-else class="flex flex-col items-center justify-center pt-5 pb-6 text-center">
            <div class="p-3 mb-3 rounded-full bg-primary/10 transition-colors duration-300">
              <FileText class="w-6 h-6 text-primary" />
            </div>
            <p class="mb-1 text-sm font-medium text-foreground">
              {{ file.name }}
            </p>
            <p class="text-xs text-muted-foreground">
              {{ (file.size / 1024 / 1024).toFixed(2) }} MB
            </p>
          </div>
        </Transition>
      </div>
    </div>

    <div v-else class="space-y-4 py-4">
      <div class="space-y-2">
        <Label>{{ t('translation.pdfLink') }}</Label>
        <Input 
          ref="urlInput"
          :model-value="url"  
          @update:model-value="emit('update:url', $event)"
          :placeholder="t('translation.pdfLinkPlaceholder')" 
          autofocus
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Elegant floating animation for file dropbox */
.file-dropbox {
  animation: subtle-breathe 4s cubic-bezier(0.37, 0, 0.63, 1) infinite;
  transition: transform 0.5s cubic-bezier(0.22, 1, 0.36, 1), 
              box-shadow 0.5s cubic-bezier(0.22, 1, 0.36, 1),
              border-color 0.3s ease,
              background-color 0.3s ease;
}

.file-dropbox:hover {
  animation: levitate 3s cubic-bezier(0.37, 0, 0.63, 1) infinite;
  transform: translateY(-6px) scale(1.01);
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.12), 
              0 8px 16px -8px rgba(0, 0, 0, 0.08),
              0 0 0 1px rgba(0, 0, 0, 0.02);
}

:global(.dark) .file-dropbox:hover {
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.5), 
              0 8px 16px -8px rgba(0, 0, 0, 0.3),
              0 0 0 1px rgba(255, 255, 255, 0.02);
}

/* Subtle resting animation - gentle breathing effect */
@keyframes subtle-breathe {
  0%, 100% {
    transform: translateY(0) scale(1);
  }
  50% {
    transform: translateY(-2px) scale(1.002);
  }
}

/* Hover state - more pronounced organic floating */
@keyframes levitate {
  0% {
    transform: translateY(-6px) scale(1.01) rotate(0deg);
  }
  25% {
    transform: translateY(-9px) scale(1.012) rotate(0.2deg);
  }
  50% {
    transform: translateY(-6px) scale(1.01) rotate(0deg);
  }
  75% {
    transform: translateY(-9px) scale(1.012) rotate(-0.2deg);
  }
  100% {
    transform: translateY(-6px) scale(1.01) rotate(0deg);
  }
}

/* Elegant icon animation on hover */
.file-dropbox:hover :deep(.p-3) {
  animation: icon-float 2s cubic-bezier(0.37, 0, 0.63, 1) infinite;
}

@keyframes icon-float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  25% {
    transform: translateY(-4px) rotate(2deg);
  }
  75% {
    transform: translateY(-4px) rotate(-2deg);
  }
}

/* Smooth border glow on hover */
.file-dropbox::before {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: inherit;
  padding: 1px;
  background: linear-gradient(135deg, transparent 0%, transparent 100%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0;
  transition: opacity 0.5s cubic-bezier(0.22, 1, 0.36, 1);
}

.file-dropbox:hover::before {
  background: linear-gradient(135deg, hsl(var(--primary) / 0.3) 0%, hsl(var(--primary) / 0.1) 100%);
  opacity: 1;
}

/* Reduce motion for users who prefer it */
@media (prefers-reduced-motion: reduce) {
  .file-dropbox {
    animation: none;
  }
  .file-dropbox:hover {
    animation: none;
    transform: translateY(-2px);
  }
  .file-dropbox:hover :deep(.p-3) {
    animation: none;
  }
}
</style>
