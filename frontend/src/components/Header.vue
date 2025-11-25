<script setup>
import { ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Moon, Sun, Languages, Settings, X, Zap } from 'lucide-vue-next'
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
  showSettings: {
    type: Boolean,
    default: false
  },
  isWco: {
    type: Boolean,
    default: false
  },
  devMode: {
    type: Boolean,
    default: false
  },
  isTranslating: {
    type: Boolean,
    default: false
  }
})

const { locale, t } = useI18n()
const colorMode = useColorMode({
  disableTransition: false
})
const emit = defineEmits(['toggle-settings', 'change-language', 'toggle-dev-mode', 'go-home'])

// Dev mode activation via 4 rapid clicks
const clickCount = ref(0)
const clickTimeout = ref(null)
const DEV_MODE_CLICKS = 4
const CLICK_TIMEOUT_MS = 3000

const handleSettingsClick = () => {
  clickCount.value++
  
  // Clear existing timeout
  if (clickTimeout.value) {
    clearTimeout(clickTimeout.value)
  }
  
  // Check if we've reached the required clicks
  if (clickCount.value >= DEV_MODE_CLICKS) {
    emit('toggle-dev-mode')
    clickCount.value = 0
    return
  }
  
  // Reset click count after timeout
  clickTimeout.value = setTimeout(() => {
    clickCount.value = 0
  }, CLICK_TIMEOUT_MS)
  
  // Toggle settings on single click
  emit('toggle-settings')
}

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
  emit('change-language', langCode)
}

const toggleTheme = () => {
  colorMode.value = colorMode.value === 'dark' ? 'light' : 'dark'
}
</script>

<template>
  <header 
    class="sticky top-0 z-50 flex items-center justify-between px-6 pb-4 pt-[calc(1rem_+_env(safe-area-inset-top,0px))] border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
    :class="{ 'wco-header': isWco }"
  >
    <div class="flex items-center gap-2">
      <h1 
        v-if="!isWco" 
        class="text-xl font-bold tracking-tight text-primary cursor-pointer hover:opacity-80 transition-opacity select-none"
        @click="emit('go-home')"
      >
        {{ t('app.title') }}
      </h1>
    </div>
    <div class="flex items-center gap-2" :class="{ 'app-no-drag': isWco }">
      <PWAInstallButton />
      
      <DropdownMenu>
        <DropdownMenuTrigger as-child>
          <Button variant="ghost" size="icon" id="language-menu-trigger" :disabled="isTranslating">
            <div class="relative w-5 h-5 flex items-center justify-center">
              <Transition name="rotate-fade" mode="out-in">
                <Languages :key="locale" class="absolute h-5 w-5" />
              </Transition>
            </div>
            <span class="sr-only">{{ t('language.select') }}</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" class="z-[100]">
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

      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger as-child>
            <Button variant="ghost" size="icon" @click="toggleTheme">
              <div class="relative w-5 h-5 flex items-center justify-center">
                <Transition name="rotate-fade">
                  <Sun v-if="colorMode === 'light'" class="absolute h-5 w-5 theme-icon-sun" />
                  <Moon v-else class="absolute h-5 w-5 theme-icon-moon" />
                </Transition>
              </div>
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>{{ t('shortcuts.theme') }} (⌘/Ctrl + D)</p>
          </TooltipContent>
        </Tooltip>

        <Tooltip>
          <TooltipTrigger as-child>
            <Button 
              variant="ghost" 
              size="icon" 
              @click="handleSettingsClick"
              :class="{ 'text-amber-500': devMode }"
              :disabled="isTranslating"
            >
              <div class="relative w-5 h-5 flex items-center justify-center">
                <Transition name="rotate-fade">
                  <Zap v-if="devMode && !showSettings" class="absolute h-5 w-5 settings-icon text-amber-500" />
                  <Settings v-else-if="!showSettings" class="absolute h-5 w-5 settings-icon" />
                  <X v-else class="absolute h-5 w-5 close-icon" />
                </Transition>
              </div>
              <span class="sr-only">{{ showSettings ? t('common.close') : t('settings.title') }}</span>
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>{{ showSettings ? t('shortcuts.closeSettings') + ' (Esc)' : t('shortcuts.settings') + ' (⌘/Ctrl + ,)' }}</p>
            <p v-if="devMode" class="text-amber-500 text-xs mt-1">{{ t('devMode.enabled') }}</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    </div>
  </header>
</template>

<style scoped>
/* stylelint-disable property-no-unknown */
.rotate-fade-enter-active,
.rotate-fade-leave-active {
  transition: all 0.2s ease;
}

/* Settings Icon: Rotate between 0 and 90 */
.rotate-fade-enter-from.settings-icon,
.rotate-fade-leave-to.settings-icon {
  opacity: 0;
  transform: rotate(90deg);
}

/* Close Icon: Rotate between 0 and -90 */
.rotate-fade-enter-from.close-icon,
.rotate-fade-leave-to.close-icon {
  opacity: 0;
  transform: rotate(-90deg);
}

/* Theme Icons */
/* Sun (Light Mode) enters/leaves */
.rotate-fade-enter-from.theme-icon-sun,
.rotate-fade-leave-to.theme-icon-sun {
  opacity: 0;
  transform: rotate(90deg);
}

/* Moon (Dark Mode) enters/leaves */
.rotate-fade-enter-from.theme-icon-moon,
.rotate-fade-leave-to.theme-icon-moon {
  opacity: 0;
  transform: rotate(-90deg);
}

/* Language Icon: Simple fade and scale */
.rotate-fade-enter-from:not(.settings-icon):not(.close-icon):not(.theme-icon-sun):not(.theme-icon-moon),
.rotate-fade-leave-to:not(.settings-icon):not(.close-icon):not(.theme-icon-sun):not(.theme-icon-moon) {
  opacity: 0;
  transform: scale(0.8);
}

.wco-header {
  position: fixed;
  top: 0;
  left: env(titlebar-area-x, 0);
  width: env(titlebar-area-width, 100%);
  height: env(titlebar-area-height, 3rem);
  padding: 0 1rem;
  background: hsl(var(--background) / 0.95);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid hsl(var(--border));
  -webkit-app-region: drag;
  /* Reset standard header styles */
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}

.wco-header :deep(button),
.wco-header :deep([role="menu"]),
.wco-header :deep([data-reka-dropdown-menu-content]) {
  -webkit-app-region: no-drag;
}

.app-no-drag,
.app-no-drag * {
  -webkit-app-region: no-drag;
}

@supports not (height: env(titlebar-area-height)) {
  .wco-header {
    position: sticky;
    height: auto;
    min-height: 3rem;
  }
}

/* stylelint-enable property-no-unknown */
</style>
