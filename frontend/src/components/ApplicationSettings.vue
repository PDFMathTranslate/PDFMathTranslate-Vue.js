<script setup>
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useColorMode } from '@vueuse/core'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Switch } from '@/components/ui/switch'
import { Button } from '@/components/ui/button'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { Moon, Sun, Laptop, FlaskConical, ShieldCheck } from 'lucide-vue-next'
import ServiceComparisonCard from './ServiceComparisonCard.vue'

const { t, locale } = useI18n()
const colorMode = useColorMode({
  disableTransition: false
})

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

const props = defineProps({
  modelValue: { type: Object, required: true },
  config: { type: Object, default: () => ({ services: [] }) },
  openAccordion: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue'])

const accordionValue = ref('output-preference')

// Watch for external accordion open requests
watch(() => props.openAccordion, (newValue) => {
  if (newValue) {
    accordionValue.value = newValue
  }
}, { immediate: true })

const model = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// Translation backend mode: 'stable' (pdf2zh) or 'experimental' (pdf2zh_next)
const translationBackend = computed({
  get: () => model.value?.translationBackend || 'stable',
  set: (val) => { 
    if (!model.value) model.value = {}
    model.value.translationBackend = val 
  }
})

// Backend availability from config
const backends = computed(() => props.config?.backends || {})
const isStableAvailable = computed(() => backends.value?.stable?.available ?? false)
const stableInstallHint = computed(() => backends.value?.stable?.install_hint || 'pip install pdf2zh-next[stable]')

const services = computed(() => {
  return props.config?.services || []
})

const service = computed({
  get: () => model.value?.service,
  set: (val) => { 
    if (!model.value) model.value = {}
    model.value.service = val
  }
})

// Output preferences
// "Bilingual" means enable dual/bilingual output, so noDual should be false when ON
// When OFF, mono-only mode is enabled (noDual = true)
const bilingual = computed({
  get: () => {
    if (!model.value) return true // Default to bilingual enabled
    return model.value.noDual !== true
  },
  set: (val) => { 
    if (!model.value) model.value = {}
    model.value.noDual = !val
    // If bilingual is disabled (mono-only mode), ensure mono is not disabled
    if (!val) {
      model.value.noMono = false
    }
  }
})

const dualTranslateFirst = computed({
  get: () => model.value?.dualTranslateFirst || false,
  set: (val) => { 
    if (!model.value) model.value = {}
    model.value.dualTranslateFirst = val 
  }
})

const alternatingPages = computed({
  get: () => model.value?.useAlternatingPagesDual || false,
  set: (val) => { 
    if (!model.value) model.value = {}
    model.value.useAlternatingPagesDual = val 
  }
})

// Rate limiting
const qps = computed({
  get: () => model.value?.qps || '',
  set: (val) => { 
    if (!model.value) model.value = {}
    model.value.qps = val ? Number(val) : undefined
  }
})

const poolMaxWorkers = computed({
  get: () => model.value?.poolMaxWorkers || '',
  set: (val) => { 
    if (!model.value) model.value = {}
    model.value.poolMaxWorkers = val ? Number(val) : undefined
  }
})

const termQps = computed({
  get: () => model.value?.termQps || '',
  set: (val) => { 
    if (!model.value) model.value = {}
    model.value.termQps = val ? Number(val) : undefined
  }
})

const termPoolMaxWorkers = computed({
  get: () => model.value?.termPoolMaxWorkers || '',
  set: (val) => { 
    if (!model.value) model.value = {}
    model.value.termPoolMaxWorkers = val ? Number(val) : undefined
  }
})

// PDF processing
const pages = computed({
  get: () => model.value?.pages || '',
  set: (val) => { 
    if (!model.value) model.value = {}
    model.value.pages = val || undefined
  }
})

const watermarkOutputMode = computed({
  get: () => model.value?.watermarkOutputMode || 'no_watermark',
  set: (val) => { 
    if (!model.value) model.value = {}
    model.value.watermarkOutputMode = val 
  }
})

const maxPagesPerPart = computed({
  get: () => model.value?.maxPagesPerPart || '',
  set: (val) => { 
    if (!model.value) model.value = {}
    model.value.maxPagesPerPart = val ? Number(val) : undefined
  }
})

// Translation options
const minTextLength = computed({
  get: () => model.value?.minTextLength || '',
  set: (val) => { 
    if (!model.value) model.value = {}
    model.value.minTextLength = val ? Number(val) : undefined
  }
})

const ignoreCache = computed({
  get: () => model.value?.ignoreCache || false,
  set: (val) => { 
    if (!model.value) model.value = {}
    model.value.ignoreCache = val 
  }
})

const customSystemPrompt = computed({
  get: () => model.value?.customSystemPrompt || '',
  set: (val) => { 
    if (!model.value) model.value = {}
    model.value.customSystemPrompt = val || undefined
  }
})

// Advanced options
const translateTableText = computed({
  get: () => model.value?.translateTableText || false,
  set: (val) => { 
    if (!model.value) model.value = {}
    model.value.translateTableText = val 
  }
})

const skipScannedDetection = computed({
  get: () => model.value?.skipScannedDetection || false,
  set: (val) => { 
    if (!model.value) model.value = {}
    model.value.skipScannedDetection = val 
  }
})

const ocrWorkaround = computed({
  get: () => model.value?.ocrWorkaround || false,
  set: (val) => { 
    if (!model.value) model.value = {}
    model.value.ocrWorkaround = val 
  }
})

const autoEnableOcrWorkaround = computed({
  get: () => model.value?.autoEnableOcrWorkaround || false,
  set: (val) => { 
    if (!model.value) model.value = {}
    model.value.autoEnableOcrWorkaround = val 
  }
})

// Appearance
const accentColor = computed({
  get: () => model.value?.accentColor || 'black',
  set: (val) => { 
    if (!model.value) model.value = {}
    model.value.accentColor = val 
  }
})

const resetSettings = () => {
  localStorage.clear()
  window.location.reload()
}

import { serviceFields } from '@/constants/services'

const currentServiceFields = computed(() => {
  return serviceFields[service.value] || []
})

// Version info from config
const stableVersion = computed(() => props.config?.versions?.stable || 'unknown')
const experimentalVersion = computed(() => props.config?.versions?.experimental || 'unknown')

// Check if we're using stable backend
const isStableBackend = computed(() => translationBackend.value === 'stable')
const isExperimentalBackend = computed(() => translationBackend.value === 'experimental')
</script>

<template>
  <!-- <div class="mt-2">
    <p class="text-sm text-gray-500"> Settings will be automatically saved. </p>
  </div> -->
  <div class="space-y-6">
    <!-- Backend Mode Switcher - Placed at the top right of settings -->
    <div class="flex items-center justify-between pb-4 border-b">
      <div class="space-y-1">
        <Label class="text-base font-medium">{{ t('settings.backendMode') }}</Label>
        <p class="text-sm text-muted-foreground">{{ t('settings.backendModeDescription') }}</p>
      </div>
      <div class="flex items-center gap-1 p-1 bg-muted/50 rounded-lg transition-colors duration-300">
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger as-child>
              <Button 
                variant="ghost" 
                size="sm" 
                @click="isStableAvailable && (translationBackend = 'stable')" 
                class="transition-all duration-300 rounded-md gap-1.5 h-8 px-3"
                :class="[
                  translationBackend === 'stable' 
                    ? 'bg-background shadow-sm text-primary font-medium' 
                    : 'text-muted-foreground hover:text-primary hover:bg-background/50',
                  !isStableAvailable && 'opacity-50 cursor-not-allowed hover:bg-transparent hover:text-muted-foreground'
                ]"
                :disabled="!isStableAvailable"
              >
                <ShieldCheck class="w-4 h-4" />
                {{ t('settings.stable') }}
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom" class="max-w-xs">
              <template v-if="isStableAvailable">
                <p class="font-medium">{{ t('settings.stableTooltip') }}</p>
                <p class="text-xs text-muted-foreground mt-1">pdf2zh v{{ stableVersion }}</p>
              </template>
              <template v-else>
                <p class="font-medium text-amber-600 dark:text-amber-400">{{ t('settings.stableNotAvailable') }}</p>
                <p class="text-xs text-muted-foreground mt-1">{{ t('settings.installWith') }}: <code class="bg-muted px-1 rounded">{{ stableInstallHint }}</code></p>
              </template>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger as-child>
              <Button 
                variant="ghost" 
                size="sm" 
                @click="translationBackend = 'experimental'" 
                class="transition-all duration-300 rounded-md gap-1.5 h-8 px-3"
                :class="translationBackend === 'experimental' 
                  ? 'bg-background shadow-sm text-primary font-medium' 
                  : 'text-muted-foreground hover:text-primary hover:bg-background/50'"
              >
                <FlaskConical class="w-4 h-4" />
                {{ t('settings.experimental') }}
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom" class="max-w-xs">
              <p class="font-medium">{{ t('settings.experimentalTooltip') }}</p>
              <p class="text-xs text-muted-foreground mt-1">pdf2zh_next v{{ experimentalVersion }}</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>
    </div>

    <Accordion type="single" collapsible class="w-full" v-model="accordionValue">
      
      <AccordionItem value="output-preference">
        <AccordionTrigger>{{ t('settings.outputPreference') }}</AccordionTrigger>
        <AccordionContent class="space-y-4 pt-2">
          <div :class="isExperimentalBackend ? 'grid grid-cols-3 gap-4' : 'grid grid-cols-2 gap-4'">
            <div 
              class="border rounded-lg p-4 cursor-pointer flex flex-col items-center gap-2 hover:bg-accent transition-colors"
              :class="{ 'bg-accent border-primary': !bilingual && !alternatingPages }"
              @click="() => { bilingual = false; alternatingPages = false }"
            >
              <img src="@/assets/icons/trans-only.png" class="w-12" />
              <span class="text-sm font-medium">{{ t('settings.monoOnly') }}</span>
            </div>

            <div 
              class="border rounded-lg p-4 cursor-pointer flex flex-col items-center gap-2 hover:bg-accent transition-colors"
              :class="{ 'bg-accent border-primary': bilingual && !alternatingPages }"
              @click="() => { bilingual = true; alternatingPages = false }"
            >
              <img src="@/assets/icons/compare-hor.png" class="w-12" />
              <span class="text-sm font-medium">{{ t('settings.bilingual') }}</span>
            </div>

            <!-- Alternating pages only available in experimental backend -->
            <div 
              v-if="isExperimentalBackend"
              class="border rounded-lg p-4 cursor-pointer flex flex-col items-center gap-2 hover:bg-accent transition-colors"
              :class="{ 'bg-accent border-primary': alternatingPages }"
              @click="() => { alternatingPages = true; bilingual = false }"
            >
              <img src="@/assets/icons/compare-vert.png" class="w-12" />
              <span class="text-sm font-medium">{{ t('settings.alternatingPages') }}</span>
            </div>
          </div>

          <div class="overflow-hidden">
            <!-- Only show dualTranslateFirst and alternatingPages for experimental backend -->
            <div class="flex items-center justify-between pt-2" v-if="bilingual && isExperimentalBackend">
              <Label for="dual-translate-first">{{ t('settings.dualTranslateFirst') }}</Label>
              <Switch id="dual-translate-first" v-model="dualTranslateFirst" />
            </div>
          </div>
        </AccordionContent>
      </AccordionItem>
      <!-- <AccordionItem value="general">
        <AccordionTrigger>{{ t('settings.general') || 'General' }}</AccordionTrigger>
        <AccordionContent class="space-y-4 pt-2">
          <div class="space-y-2">
             <Label>{{ t('language.select') }}</Label>
             <Select :model-value="locale" @update:model-value="changeLanguage">
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="lang in supportedLocales" :key="lang.code" :value="lang.code">
                  {{ lang.native }}
                </SelectItem>
              </SelectContent>
             </Select>
          </div>

          <div class="space-y-2">
            <Label>{{ t('settings.appearance') }}</Label>
            <div class="grid grid-cols-3 gap-4">
               <div 
                class="border rounded-lg p-4 cursor-pointer flex flex-col items-center gap-2 hover:bg-accent transition-colors"
                :class="{ 'bg-accent border-primary': colorMode === 'light' }"
                @click="colorMode = 'light'"
               >
                 <Sun class="w-6 h-6" />
                 <span class="text-sm font-medium">{{ t('settings.light') || 'Light' }}</span>
               </div>
               <div 
                class="border rounded-lg p-4 cursor-pointer flex flex-col items-center gap-2 hover:bg-accent transition-colors"
                :class="{ 'bg-accent border-primary': colorMode === 'dark' }"
                @click="colorMode = 'dark'"
               >
                 <Moon class="w-6 h-6" />
                 <span class="text-sm font-medium">{{ t('settings.dark') || 'Dark' }}</span>
               </div>
               <div 
                class="border rounded-lg p-4 cursor-pointer flex flex-col items-center gap-2 hover:bg-accent transition-colors"
                :class="{ 'bg-accent border-primary': colorMode === 'auto' }"
                @click="colorMode = 'auto'"
               >
                 <Laptop class="w-6 h-6" />
                 <span class="text-sm font-medium">{{ t('settings.auto') || 'Auto' }}</span>
               </div>
            </div>
          </div> -->
        <!-- </AccordionContent>
      </AccordionItem> --> 

      <!-- New Service Settings Accordion Item -->

      <!-- <AccordionItem value="service">
        <AccordionTrigger>{{ t('settings.service') }}</AccordionTrigger>
        <AccordionContent class="space-y-4 pt-2">
          <div class="space-y-2">
            <Label>{{ t('translation.selectService') }}</Label>
            <Select v-model="service">
              <SelectTrigger>
                <SelectValue :placeholder="t('translation.selectService')">
                  <span v-if="service">{{ service }}</span>
                  <span v-else class="text-muted-foreground">{{ t('translation.selectService') }}</span>
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                <SelectItem 
                  v-for="srv in services" 
                  :key="`service-${srv}`" 
                  :value="srv"
                >
                  {{ srv }}
                </SelectItem>
                <div v-if="services.length === 0" class="px-2 py-1.5 text-sm text-muted-foreground">
                  {{ t('translation.noServicesAvailable') }}
                </div>
              </SelectContent>
            </Select>
          </div> -->

          <!-- Dynamic Service Fields -->
          <!-- <div v-if="currentServiceFields.length > 0" class="space-y-4 pt-2 border-t mt-4">
            <div v-for="field in currentServiceFields" :key="field.name" class="space-y-2">
              <Label :for="field.name">{{ t(field.label) }}</Label>
              <Input 
                :id="field.name" 
                v-model="model[field.name]" 
                :type="field.type" 
                :placeholder="field.placeholder"
              />
            </div> -->

          <!-- Service Comparison Card -->
          <!-- <ServiceComparisonCard 
            :current-service="service" 
            :services="services"
            @update:current-service="service = $event"
          />
          </div>
        </AccordionContent>
      </AccordionItem> -->

      <AccordionItem value="pdf-processing">
        <AccordionTrigger>{{ t('settings.pdfProcessing') }}</AccordionTrigger>
        <AccordionContent class="space-y-4 pt-2">
          <!-- Watermark output mode only for experimental backend -->
          <div class="space-y-2" v-if="isExperimentalBackend">
            <Label for="watermark-output-mode">{{ t('settings.watermarkOutputMode') }}</Label>
            <Select v-model="watermarkOutputMode">
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="watermarked">{{ t('settings.watermarked') }}</SelectItem>
                <SelectItem value="no_watermark">{{ t('settings.noWatermark') }}</SelectItem>
                <SelectItem value="both">{{ t('settings.both') }}</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div class="space-y-2">
            <Label for="pages">{{ t('settings.pages') }}</Label>
            <Input 
              id="pages" 
              v-model="pages" 
              :placeholder="t('settings.pagesPlaceholder')"
            />
          </div>
          <!-- Max pages per part only for experimental backend -->
          <div class="space-y-2" v-if="isExperimentalBackend">
            <Label for="max-pages-per-part">{{ t('settings.maxPagesPerPart') }}</Label>
            <Input 
              id="max-pages-per-part" 
              v-model="maxPagesPerPart" 
              type="number" 
              :placeholder="t('settings.maxPagesPerPartPlaceholder')"
            />
          </div>
        </AccordionContent>
      </AccordionItem>

      <AccordionItem value="translation">
        <AccordionTrigger>{{ t('settings.translationOptions') }}</AccordionTrigger>
        <AccordionContent class="space-y-4 pt-2">
          <div class="flex items-center justify-between">
            <Label for="ignore-cache">{{ t('settings.ignoreCache') }}</Label>
            <Switch id="ignore-cache" v-model="ignoreCache" />
          </div>
          <!-- Min text length only for experimental backend -->
          <div class="space-y-2" v-if="isExperimentalBackend">
            <Label for="min-text-length">{{ t('settings.minTextLength') }}</Label>
            <Input 
              id="min-text-length" 
              v-model="minTextLength" 
              type="number" 
              :placeholder="t('settings.minTextLengthPlaceholder')"
            />
          </div>
          <!-- Custom system prompt only for experimental backend -->
          <div class="space-y-2" v-if="isExperimentalBackend">
            <Label for="custom-system-prompt">{{ t('settings.customSystemPrompt') }}</Label>
            <Input 
              id="custom-system-prompt" 
              v-model="customSystemPrompt" 
              :placeholder="t('settings.customSystemPromptPlaceholder')"
            />
          </div>
        </AccordionContent>
      </AccordionItem>

      <!-- Rate limiting only for experimental backend -->
      <AccordionItem value="rate-limiting" v-if="isExperimentalBackend">
        <AccordionTrigger>{{ t('settings.rateLimiting') }}</AccordionTrigger>
        <AccordionContent class="space-y-4 pt-2">
          <div class="space-y-2">
            <Label for="pool-max-workers">{{ t('settings.poolMaxWorkers') }}</Label>
            <Input 
              id="pool-max-workers" 
              v-model="poolMaxWorkers" 
              type="number" 
              :placeholder="t('settings.poolMaxWorkersPlaceholder')"
            />
          </div>
          <div class="space-y-2">
            <Label for="qps">{{ t('settings.qps') }}</Label>
            <Input 
              id="qps" 
              v-model="qps" 
              type="number" 
              :placeholder="t('settings.qpsPlaceholder')"
            />
          </div>
          <div class="space-y-2">
            <Label for="term-qps">{{ t('settings.termQps') }}</Label>
            <Input 
              id="term-qps" 
              v-model="termQps" 
              type="number" 
              :placeholder="t('settings.termQpsPlaceholder')"
            />
          </div>
          <div class="space-y-2">
            <Label for="term-pool-max-workers">{{ t('settings.termPoolMaxWorkers') }}</Label>
            <Input 
              id="term-pool-max-workers" 
              v-model="termPoolMaxWorkers" 
              type="number" 
              :placeholder="t('settings.termPoolMaxWorkersPlaceholder')"
            />
          </div>
        </AccordionContent>
      </AccordionItem>

      <!-- Advanced options only for experimental backend -->
      <AccordionItem value="advanced" v-if="isExperimentalBackend">
        <AccordionTrigger>{{ t('settings.advanced') }}</AccordionTrigger>
        <AccordionContent class="space-y-4 pt-2">
          <div class="flex items-center justify-between">
            <Label for="translate-table-text">{{ t('settings.translateTableText') }}</Label>
            <Switch id="translate-table-text" v-model="translateTableText" />
          </div>
          <div class="flex items-center justify-between">
            <Label for="skip-scanned-detection">{{ t('settings.skipScannedDetection') }}</Label>
            <Switch id="skip-scanned-detection" v-model="skipScannedDetection" />
          </div>
          <div class="flex items-center justify-between">
            <Label for="ocr-workaround">{{ t('settings.ocrWorkaround') }}</Label>
            <Switch id="ocr-workaround" v-model="ocrWorkaround" />
          </div>
          <div class="flex items-center justify-between">
            <Label for="auto-enable-ocr-workaround">{{ t('settings.autoEnableOcrWorkaround') }}</Label>
            <Switch id="auto-enable-ocr-workaround" v-model="autoEnableOcrWorkaround" />
          </div>
          <div class="pt-2">
            <Button variant="destructive" class="w-full" @click="resetSettings">
              {{ t('settings.resetSettings') }}
            </Button>
          </div>
        </AccordionContent>
      </AccordionItem>
      
      <AccordionItem value="appearance">
        <AccordionTrigger>{{ t('settings.appearance') || 'Appearance' }}</AccordionTrigger>
        <AccordionContent class="space-y-4 pt-2">
          <div class="space-y-2">
            <Label>{{ t('settings.accentColor') }}</Label>
            <div class="grid grid-cols-5 gap-3">
              <div 
                v-for="color in ['black', 'sky', 'lime', 'orange', 'pink']" 
                :key="color"
                class="border-2 rounded-lg p-3 cursor-pointer flex flex-col items-center gap-2 hover:bg-accent transition-all"
                :class="{ 'border-primary ring-2 ring-primary/20': accentColor === color, 'border-border': accentColor !== color }"
                @click="accentColor = color"
              >
                <div 
                  class="w-8 h-8 rounded-full"
                  :class="{
                    'bg-black dark:bg-white': color === 'black',
                    'bg-sky-800': color === 'sky',
                    'bg-lime-800': color === 'lime',
                    'bg-orange-800': color === 'orange',
                    'bg-pink-800': color === 'pink'
                  }"
                />
                <span class="text-xs font-medium">{{ t(`settings.accentColors.${color}`) }}</span>
              </div>
            </div>
          </div>
        </AccordionContent>
      </AccordionItem>
      
      <!-- Reset settings button for stable backend (without advanced options) -->
      <div v-if="isStableBackend" class="pt-4">
        <Button variant="destructive" class="w-full" @click="resetSettings">
          {{ t('settings.resetSettings') }}
        </Button>
      </div>
    </Accordion>
  </div>
</template>

<style scoped>
</style>