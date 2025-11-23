<script setup>
import { computed, ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { Github } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'

const props = defineProps({
  status: {
    type: String,
    default: 'ready'
  }
})

const { t } = useI18n()

const statusColor = computed(() => {
  switch (props.status) {
    case 'busy': return 'bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.6)]'
    case 'error': return 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]'
    case 'ready': return 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]'
    default: return 'bg-gray-500'
  }
})

const statusTitle = computed(() => {
  switch (props.status) {
    case 'busy': return 'Busy / Translating'
    case 'error': return 'Error'
    case 'ready': return 'Service found & communicatable'
    default: return 'Unknown Status'
  }
})

const showPreview = ref(false)
const triggerRef = ref(null)
const popupStyle = reactive({ bottom: '0px', left: '50%', transform: 'translateX(-50%)' })

const showPopup = () => {
  if (triggerRef.value) {
    const rect = triggerRef.value.getBoundingClientRect()
    // Position above the footer
    popupStyle.bottom = `${window.innerHeight - rect.top + 8}px`
    // Centered horizontally
    popupStyle.left = '50%'
    popupStyle.transform = 'translateX(-50%)'
    showPreview.value = true
  }
}

const hidePopup = () => {
  showPreview.value = false
}
</script>

<template>
  <footer class="py-2 border-t mx-6">
    <div class="flex flex-col justify-between gap-3 md:flex-row items-center text-xs text-muted-foreground">
      <div class="text-start flex items-center gap-2 md:flex-1">
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger as-child>
              <div 
                :class="['w-3 h-3 rounded-full transition-all duration-300 cursor-help', statusColor]" 
                tabindex="0"
              ></div>
            </TooltipTrigger>
            <TooltipContent side="top">
              <p>{{ statusTitle }}</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
        {{ t('app.subtitle') }}
      </div>
      
      <div
        ref="triggerRef"
        class="relative"
        @mouseenter="showPopup"
        @mouseleave="hidePopup"
      >
        <p class="cursor-pointer hover:text-foreground transition-colors">
          {{ t('header.howDoesItWork') }}
        </p>
        <Teleport to="body">
          <div
            v-if="showPreview"
            class="fixed bg-white dark:bg-black border rounded-lg shadow-lg p-2 pointer-events-none"
            :style="{
              zIndex: 2147483647,
              bottom: popupStyle.bottom,
              left: popupStyle.left,
              transform: popupStyle.transform,
              maxWidth: '40vw',
              width: '100%'
            }"
          >
            <img
              src="/preview.gif"
              alt="How it works preview"
              class="rounded-md"
              style="width: 100%; height: auto;"
            />
          </div>
        </Teleport>
      </div>

      <div class="text-end md:flex-1 flex justify-end">
      <a href="https://github.com/PDFMathTranslate/PDFMathTranslate" target="_blank" rel="noreferrer">
        <Button variant="ghost" size="sm">
          <Github />
          GitHub
        </Button>
      </a>
      </div>
    </div>
  </footer>
</template>
