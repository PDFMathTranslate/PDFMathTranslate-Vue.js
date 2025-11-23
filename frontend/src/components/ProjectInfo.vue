<script setup>
import { computed, ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { Github, Keyboard } from 'lucide-vue-next'
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
  },
  health: {
    type: Object,
    default: null
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
    case 'busy': return t('service.status.busy')
    case 'error': return t('service.status.error')
    case 'ready': return t('service.status.ready')
    default: return t('service.status.unknown')
  }
})

const cpuLoadColor = computed(() => {
  if (!props.health || props.health.cpu_percent === undefined) return 'text-muted-foreground'
  const cpu = props.health.cpu_percent
  if (cpu < 50) return 'text-green-500'
  if (cpu < 80) return 'text-yellow-500'
  return 'text-red-500'
})

const memoryColor = computed(() => {
  if (!props.health || props.health.memory_percent === undefined) return 'text-muted-foreground'
  const memory = props.health.memory_percent
  if (memory < 60) return 'text-green-500'
  if (memory < 85) return 'text-yellow-500'
  return 'text-red-500'
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

const showShortcuts = ref(false)
const shortcutsTriggerRef = ref(null)
const shortcutsPopupStyle = reactive({ bottom: '0px', left: '0px', transform: 'translateX(-50%)' })

const showShortcutsPopup = () => {
  if (shortcutsTriggerRef.value) {
    const rect = shortcutsTriggerRef.value.getBoundingClientRect()
    shortcutsPopupStyle.bottom = `${window.innerHeight - rect.top + 8}px`
    shortcutsPopupStyle.left = `${rect.left + rect.width / 2}px`
    shortcutsPopupStyle.transform = 'translateX(-50%)'
    showShortcuts.value = true
  }
}

const hideShortcutsPopup = () => {
  showShortcuts.value = false
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
            <TooltipContent side="top" class="max-w-xs">
              <div class="space-y-1.5">
                <p class="font-semibold">{{ statusTitle }}</p>
                <template v-if="health && !health.error">
                  <div class="text-xs space-y-1 border-t pt-1.5 mt-1.5">
                    <div class="flex justify-between items-center">
                      <span class="text-muted-foreground">{{ t('service.cpu') }}:</span>
                      <span :class="cpuLoadColor" class="font-mono">{{ health.cpu_percent }}%</span>
                    </div>
                    <div class="flex justify-between items-center">
                      <span class="text-muted-foreground">{{ t('service.memory') }}:</span>
                      <span :class="memoryColor" class="font-mono">
                        {{ health.memory_percent }}% ({{ health.memory_used_gb }}/{{ health.memory_total_gb }} GB)
                      </span>
                    </div>
                    <div v-if="health.active_tasks > 0" class="flex justify-between items-center">
                      <span class="text-muted-foreground">{{ t('service.activeTasks') }}:</span>
                      <span class="font-mono">{{ health.active_tasks }}</span>
                    </div>
                    <div v-if="health.pending_tasks > 0" class="flex justify-between items-center">
                      <span class="text-muted-foreground">{{ t('service.pendingTasks') }}:</span>
                      <span class="font-mono">{{ health.pending_tasks }}</span>
                    </div>
                  </div>
                </template>
                <p v-else-if="health && health.error" class="text-xs text-red-500">
                  {{ t('service.errorFetchingHealth') }}
                </p>
              </div>
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

      <div class="text-end md:flex-1 flex justify-end gap-2">
      <div
        ref="shortcutsTriggerRef"
        class="relative flex items-center"
        @mouseenter="showShortcutsPopup"
        @mouseleave="hideShortcutsPopup"
      >
        <Button variant="ghost" size="sm">
          <Keyboard class="w-4 h-4 mr-2" />
          {{ t('shortcuts.title') }}
        </Button>
        <Teleport to="body">
          <div
            v-if="showShortcuts"
            class="fixed bg-white dark:bg-black border rounded-lg shadow-lg p-4 pointer-events-none z-[2147483647]"
            :style="{
              bottom: shortcutsPopupStyle.bottom,
              left: shortcutsPopupStyle.left,
              transform: shortcutsPopupStyle.transform,
              width: 'max-content'
            }"
          >
            <div class="grid grid-cols-[auto,auto] gap-x-6 gap-y-2 text-sm items-center">
                <span class="text-muted-foreground">{{ t('shortcuts.new') }} / {{ t('shortcuts.stop') }}</span> 
                <span class="font-mono text-xs bg-muted px-1.5 py-0.5 rounded border">⌘/Ctrl + N / R</span>
                
                <span class="text-muted-foreground">{{ t('shortcuts.settings') }}</span> 
                <span class="font-mono text-xs bg-muted px-1.5 py-0.5 rounded border">⌘/Ctrl + P / ,</span>
                
                <span class="text-muted-foreground">{{ t('shortcuts.theme') }}</span> 
                <span class="font-mono text-xs bg-muted px-1.5 py-0.5 rounded border">⌘/Ctrl + D</span>
                
                <span class="text-muted-foreground">{{ t('shortcuts.language') }}</span> 
                <span class="font-mono text-xs bg-muted px-1.5 py-0.5 rounded border">⌘/Ctrl + L</span>

                <span class="text-muted-foreground">{{ t('shortcuts.closeSettings') }}</span> 
                <span class="font-mono text-xs bg-muted px-1.5 py-0.5 rounded border">Esc</span>
            </div>
          </div>
        </Teleport>
      </div>

      <a href="https://github.com/PDFMathTranslate/PDFMathTranslate" target="_blank" rel="noreferrer">
        <Button variant="ghost" size="sm">
          <Github class="w-4 h-4 mr-2" />
          GitHub
        </Button>
      </a>
      </div>
    </div>
  </footer>
</template>
