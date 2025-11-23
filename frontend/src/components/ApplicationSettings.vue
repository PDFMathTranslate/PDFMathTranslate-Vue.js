<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Switch } from '@/components/ui/switch'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

const { t } = useI18n()

const model = defineModel({ required: true })

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
</script>

<template>
  <!-- <div class="mt-2">
    <p class="text-sm text-gray-500"> Settings will be automatically saved. </p>
  </div> -->
  <div class="space-y-6">
    <Accordion type="single" collapsible class="w-full" defaultValue="output-preference">
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

          <div class="flex items-center justify-between pt-2" v-if="bilingual">
            <Label for="dual-translate-first">{{ t('settings.dualTranslateFirst') }}</Label>
            <Switch id="dual-translate-first" v-model="dualTranslateFirst" />
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
        </AccordionContent>
      </AccordionItem>
    </Accordion>

  </div>
</template>
