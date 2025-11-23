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
import { Moon, Sun, Laptop } from 'lucide-vue-next'

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

// Service Configuration Mapping
const serviceFields = {
  OpenAI: [
    { name: 'openai_api_key', label: 'API Key', type: 'password' },
    { name: 'openai_model', label: 'Model', type: 'text', placeholder: 'gpt-4o-mini' },
    { name: 'openai_base_url', label: 'Base URL', type: 'text', placeholder: 'https://api.openai.com/v1' },
  ],
  AzureOpenAI: [
    { name: 'azure_openai_api_key', label: 'API Key', type: 'password' },
    { name: 'azure_openai_base_url', label: 'Base URL', type: 'text' },
    { name: 'azure_openai_model', label: 'Model', type: 'text', placeholder: 'gpt-4o-mini' },
    { name: 'azure_openai_api_version', label: 'API Version', type: 'text', placeholder: '2024-06-01' },
  ],
  DeepSeek: [
    { name: 'deepseek_api_key', label: 'API Key', type: 'password' },
    { name: 'deepseek_model', label: 'Model', type: 'text', placeholder: 'deepseek-chat' },
  ],
  Ollama: [
    { name: 'ollama_host', label: 'Host', type: 'text', placeholder: 'http://localhost:11434' },
    { name: 'ollama_model', label: 'Model', type: 'text', placeholder: 'gemma2' },
  ],
  Xinference: [
    { name: 'xinference_host', label: 'Host', type: 'text' },
    { name: 'xinference_model', label: 'Model', type: 'text', placeholder: 'gemma-2-it' },
  ],
  ModelScope: [
    { name: 'modelscope_api_key', label: 'API Key', type: 'password' },
    { name: 'modelscope_model', label: 'Model', type: 'text', placeholder: 'Qwen/Qwen2.5-32B-Instruct' },
  ],
  Zhipu: [
    { name: 'zhipu_api_key', label: 'API Key', type: 'password' },
    { name: 'zhipu_model', label: 'Model', type: 'text', placeholder: 'glm-4-flash' },
  ],
  SiliconFlow: [
    { name: 'siliconflow_api_key', label: 'API Key', type: 'password' },
    { name: 'siliconflow_model', label: 'Model', type: 'text', placeholder: 'Qwen/Qwen2.5-7B-Instruct' },
    { name: 'siliconflow_base_url', label: 'Base URL', type: 'text', placeholder: 'https://api.siliconflow.cn/v1' },
  ],
  TencentMechineTranslation: [
    { name: 'tencentcloud_secret_id', label: 'Secret ID', type: 'password' },
    { name: 'tencentcloud_secret_key', label: 'Secret Key', type: 'password' },
  ],
  Gemini: [
    { name: 'gemini_api_key', label: 'API Key', type: 'password' },
    { name: 'gemini_model', label: 'Model', type: 'text', placeholder: 'gemini-1.5-flash' },
  ],
  Azure: [
    { name: 'azure_api_key', label: 'API Key', type: 'password' },
    { name: 'azure_endpoint', label: 'Endpoint', type: 'text', placeholder: 'https://api.translator.azure.cn' },
  ],
  AnythingLLM: [
    { name: 'anythingllm_apikey', label: 'API Key', type: 'password' },
    { name: 'anythingllm_url', label: 'URL', type: 'text' },
  ],
  Dify: [
    { name: 'dify_apikey', label: 'API Key', type: 'password' },
    { name: 'dify_url', label: 'URL', type: 'text' },
  ],
  Grok: [
    { name: 'grok_api_key', label: 'API Key', type: 'password' },
    { name: 'grok_model', label: 'Model', type: 'text', placeholder: 'grok-2-1212' },
  ],
  Groq: [
    { name: 'groq_api_key', label: 'API Key', type: 'password' },
    { name: 'groq_model', label: 'Model', type: 'text', placeholder: 'llama-3-3-70b-versatile' },
  ],
  QwenMt: [
    { name: 'qwenmt_api_key', label: 'API Key', type: 'password' },
    { name: 'qwenmt_model', label: 'Model', type: 'text', placeholder: 'qwen-mt-plus' },
    { name: 'qwenmt_base_url', label: 'Base URL', type: 'text', placeholder: 'https://dashscope.aliyuncs.com/compatible-mode/v1' },
  ],
  OpenAICompatible: [
    { name: 'openai_compatible_api_key', label: 'API Key', type: 'password' },
    { name: 'openai_compatible_base_url', label: 'Base URL', type: 'text', placeholder: 'https://api.openai.com/v1' },
    { name: 'openai_compatible_model', label: 'Model', type: 'text', placeholder: 'gpt-4o-mini' },
  ],
  AliyunDashScope: [
    { name: 'aliyun_dashscope_api_key', label: 'API Key', type: 'password' },
    { name: 'aliyun_dashscope_model', label: 'Model', type: 'text', placeholder: 'qwen-plus-latest' },
    { name: 'aliyun_dashscope_base_url', label: 'Base URL', type: 'text', placeholder: 'https://dashscope.aliyuncs.com/compatible-mode/v1' },
  ],
  DeepL: [
    { name: 'deepl_auth_key', label: 'Auth Key', type: 'password' },
  ],
  ClaudeCode: [
    { name: 'claude_code_path', label: 'CLI Path', type: 'text', placeholder: 'claude' },
    { name: 'claude_code_model', label: 'Model', type: 'text', placeholder: 'sonnet' },
  ],
  SiliconFlowFree: [],
  Google: [],
  Bing: []
}

const currentServiceFields = computed(() => {
  return serviceFields[service.value] || []
})
</script>

<template>
  <!-- <div class="mt-2">
    <p class="text-sm text-gray-500"> Settings will be automatically saved. </p>
  </div> -->
  <div class="space-y-6">
    <Accordion type="single" collapsible class="w-full" v-model="accordionValue">
      
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
      <AccordionItem value="output-preference">
        <AccordionTrigger>{{ t('settings.outputPreference') }}</AccordionTrigger>
        <AccordionContent class="space-y-4 pt-2">
          <div class="grid grid-cols-3 gap-4">
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

            <div 
              class="border rounded-lg p-4 cursor-pointer flex flex-col items-center gap-2 hover:bg-accent transition-colors"
              :class="{ 'bg-accent border-primary': alternatingPages }"
              @click="() => { alternatingPages = true; bilingual = false }"
            >
              <img src="@/assets/icons/compare-vert.png" class="w-12" />
              <span class="text-sm font-medium">{{ t('settings.alternatingPages') }}</span>
            </div>
          </div>

          <div class="overflow-hidden">
            <div class="flex items-center justify-between pt-2" v-if="bilingual">
              <Label for="dual-translate-first">{{ t('settings.dualTranslateFirst') }}</Label>
              <Switch id="dual-translate-first" v-model="dualTranslateFirst" />
            </div>
          </div>
        </AccordionContent>
      </AccordionItem>

      <AccordionItem value="service">
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
                  {{ t('translation.noServicesAvailable') || 'No services available' }}
                </div>
              </SelectContent>
            </Select>
          </div>

          <!-- Dynamic Service Fields -->
          <div v-if="currentServiceFields.length > 0" class="space-y-4 pt-2 border-t mt-4">
            <div v-for="field in currentServiceFields" :key="field.name" class="space-y-2">
              <Label :for="field.name">{{ field.label }}</Label>
              <Input 
                :id="field.name" 
                v-model="model[field.name]" 
                :type="field.type" 
                :placeholder="field.placeholder"
              />
            </div>
          </div>
        </AccordionContent>
      </AccordionItem>

      <AccordionItem value="pdf-processing">
        <AccordionTrigger>{{ t('settings.pdfProcessing') }}</AccordionTrigger>
        <AccordionContent class="space-y-4 pt-2">
          <div class="space-y-2">
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
          <div class="space-y-2">
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
          <div class="space-y-2">
            <Label for="min-text-length">{{ t('settings.minTextLength') }}</Label>
            <Input 
              id="min-text-length" 
              v-model="minTextLength" 
              type="number" 
              :placeholder="t('settings.minTextLengthPlaceholder')"
            />
          </div>
          <div class="space-y-2">
            <Label for="custom-system-prompt">{{ t('settings.customSystemPrompt') }}</Label>
            <Input 
              id="custom-system-prompt" 
              v-model="customSystemPrompt" 
              :placeholder="t('settings.customSystemPromptPlaceholder')"
            />
          </div>
        </AccordionContent>
      </AccordionItem>

      <AccordionItem value="rate-limiting">
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
      <AccordionItem value="appearance">
        <AccordionTrigger>{{ t('settings.appearance') }}</AccordionTrigger>
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

      <AccordionItem value="advanced">
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
    </Accordion>

  </div>
</template>

<style scoped>
</style>