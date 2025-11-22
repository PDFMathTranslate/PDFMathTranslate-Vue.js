<script setup>
import { ref, computed, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Moon, Sun, Languages, Settings } from 'lucide-vue-next'
import { useColorMode } from '@vueuse/core'
import PWAInstallButton from '@/components/PWAInstallButton.vue'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
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

const { locale, t } = useI18n()
const colorMode = useColorMode()
const showPreview = ref(false)
const triggerRef = ref(null)
const popupStyle = reactive({ top: '0px', right: '0px' })

const showPopup = () => {
  if (triggerRef.value) {
    const rect = triggerRef.value.getBoundingClientRect()
    popupStyle.top = `${rect.bottom + 8}px`
    // Calculate right position relative to viewport edge
    // we want the popup's right edge to align with the trigger's right edge roughly,
    // or just position it near the trigger.
    // Given the design, right-aligned to the trigger seems best.
    popupStyle.right = `${window.innerWidth - rect.right}px`
    showPreview.value = true
  }
}

const hidePopup = () => {
  showPreview.value = false
}

const emit = defineEmits(['toggle-settings'])

const supportedLocales = [
  { code: 'en', label: 'English', native: 'English' },
  { code: 'zh', label: '简体中文', native: '简体中文' },
  { code: 'zh-TW', label: '繁體中文', native: '繁體中文' },
  { code: 'ja', label: '日本語', native: '日本語' },
  { code: 'ko', label: '한국어', native: '한국어' },
  { code: 'fr', label: 'Français', native: 'Français' },
  { code: 'de', label: 'Deutsch', native: 'Deutsch' },
  { code: 'es', label: 'Español', native: 'Español' },
  { code: 'ru', label: 'Русский', native: 'Русский' },
  { code: 'it', label: 'Italiano', native: 'Italiano' },
  { code: 'pt', label: 'Português', native: 'Português' },
]

const changeLanguage = (langCode) => {
  locale.value = langCode
  localStorage.setItem('locale', langCode)
}

const toggleTheme = () => {
  colorMode.value = colorMode.value === 'dark' ? 'light' : 'dark'
}
</script>

<template>
  <header class="relative z-50 flex items-center justify-between px-6 py-4 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
    <div class="flex items-center gap-2">
      <h1 class="text-xl font-bold tracking-tight text-primary">{{ t('app.title') }}</h1>
      <!-- <span class="text-xs text-muted-foreground">{{ t('app.subtitle') }}</span> -->

      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger as-child>
            <div 
              :class="['w-3 h-3 rounded-full transition-all duration-300 mr-1 cursor-help', statusColor]" 
              tabindex="0"
            ></div>
          </TooltipTrigger>
          <TooltipContent side="bottom">
            <p>{{ statusTitle }}</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    </div>
    <div class="flex items-center gap-2">
      <div
        ref="triggerRef"
        class="relative"
        @mouseenter="showPopup"
        @mouseleave="hidePopup"
      >
        <p class="cursor-pointer text-sm text-muted-foreground hover:text-foreground transition-colors">

          {{ t('header.howDoesItWork') }}
        </p>
        <Teleport to="body">
          <div
            v-if="showPreview"
            class="fixed z-[15000] bg-white dark:bg-black border rounded-lg shadow-lg p-2 pointer-events-none"
            :style="{
              top: popupStyle.top,
              right: popupStyle.right,
              maxWidth: '40vw',
              width: '600px'
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
      <PWAInstallButton />
      <DropdownMenu>
        <DropdownMenuTrigger as-child>
          <Button variant="ghost" size="icon">
            <Languages class="h-5 w-5" />
            <span class="sr-only">{{ t('language.select') }}</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem
            v-for="lang in supportedLocales"
            :key="lang.code"
            :class="{ 'bg-accent': locale === lang.code }"
            @click="changeLanguage(lang.code)"
          >
            {{ lang.native }}
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
      <Button variant="ghost" size="icon" @click="toggleTheme">
        <Sun class="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
        <Moon class="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
      </Button>
      <Button variant="ghost" size="icon" @click="emit('toggle-settings')">
        <Settings class="h-5 w-5" />
        <span class="sr-only">{{ t('settings.title') }}</span>
      </Button>
    </div>
  </header>
</template>
