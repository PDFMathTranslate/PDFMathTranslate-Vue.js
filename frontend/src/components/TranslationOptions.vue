<script setup>
import { computed, watch, ref, nextTick, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { ArrowRightLeft } from 'lucide-vue-next'
import FileSelector from '@/components/FileSelector.vue'

const { t } = useI18n()

const props = defineProps({
  config: {
    type: Object,
    default: () => null
  }
})

const model = defineModel()

const emit = defineEmits(['file-selected'])

// Computed properties for languages to ensure stable order if needed
const languages = computed(() => {
  if (!props.config?.languages) {
    console.debug('[TranslationOptions] No languages in config:', props.config)
    return []
  }
  const langKeys = Object.keys(props.config.languages)
  console.debug('[TranslationOptions] Languages loaded:', langKeys.length, langKeys)
  return langKeys
})

const services = computed(() => {
  if (!props.config?.services) {
    console.debug('[TranslationOptions] No services in config:', props.config)
    return []
  }
  const svcs = Array.isArray(props.config.services) ? props.config.services : []
  console.debug('[TranslationOptions] Services loaded:', svcs.length, svcs)
  return svcs
})

// Debug: Log model values
watch(() => model.value, (newModel) => {
  console.debug('[TranslationOptions] Model updated:', {
    langFrom: newModel?.langFrom,
    langTo: newModel?.langTo,
    service: newModel?.service,
    source: newModel?.source
  })
}, { deep: true, immediate: true })

// Ensure default values are valid when config loads
watch(() => props.config, (newConfig, oldConfig) => {
  // Only process if config actually changed
  if (newConfig === oldConfig) return
  
  console.debug('[TranslationOptions] Config changed:', {
    hasLanguages: !!newConfig?.languages,
    hasServices: !!newConfig?.services,
    languagesCount: newConfig?.languages ? Object.keys(newConfig.languages).length : 0,
    servicesCount: Array.isArray(newConfig?.services) ? newConfig.services.length : 0
  })
  
  // Initialize languages
  if (newConfig && newConfig.languages && typeof newConfig.languages === 'object') {
    const langKeys = Object.keys(newConfig.languages)
    if (langKeys.length > 0) {
      // Ensure model.value exists
      if (!model.value) {
        console.warn('[TranslationOptions] Model value is null/undefined, initializing')
        return // Will be handled by parent component
      }
      
      // Set default langFrom if not set or invalid
      const currentLangFrom = model.value.langFrom
      if (!currentLangFrom || typeof currentLangFrom !== 'string' || !langKeys.includes(currentLangFrom)) {
        const newLangFrom = langKeys[0]
        console.debug('[TranslationOptions] Setting langFrom:', currentLangFrom, '->', newLangFrom)
        model.value.langFrom = newLangFrom
      } else {
        console.debug('[TranslationOptions] langFrom is valid:', currentLangFrom)
      }
      
      // Set default langTo if not set or invalid
      const currentLangTo = model.value.langTo
      if (!currentLangTo || typeof currentLangTo !== 'string' || !langKeys.includes(currentLangTo)) {
        const chineseLang = langKeys.find(l => l.includes('Chinese'))
        const newLangTo = chineseLang || langKeys[0]
        console.debug('[TranslationOptions] Setting langTo:', currentLangTo, '->', newLangTo)
        model.value.langTo = newLangTo
      } else {
        console.debug('[TranslationOptions] langTo is valid:', currentLangTo)
      }
    } else {
      console.warn('[TranslationOptions] No languages available in config')
    }
  } else if (newConfig && !newConfig.languages) {
    console.warn('[TranslationOptions] Config loaded but no languages property')
  }
  
  // Initialize services
  if (newConfig && newConfig.services) {
    if (!Array.isArray(newConfig.services)) {
      console.warn('[TranslationOptions] Services is not an array:', typeof newConfig.services)
      return
    }
    
    if (newConfig.services.length > 0) {
      // Ensure model.value exists
      if (!model.value) {
        console.warn('[TranslationOptions] Model value is null/undefined, initializing')
        return
      }
      
      // Set default service if not set or invalid
      const currentService = model.value.service
      if (!currentService || typeof currentService !== 'string' || !newConfig.services.includes(currentService)) {
        const newService = newConfig.services[0]
        console.debug('[TranslationOptions] Setting service:', currentService, '->', newService)
        model.value.service = newService
      } else {
        console.debug('[TranslationOptions] service is valid:', currentService)
      }
    } else {
      console.warn('[TranslationOptions] Services array is empty')
    }
  } else if (newConfig && !newConfig.services) {
    console.warn('[TranslationOptions] Config loaded but no services property')
  }
}, { immediate: true, deep: true })

const handleFileSelected = (file) => {
  emit('file-selected', file)
}

const rotation = ref(0)

const swapLanguages = () => {
  rotation.value += 180
  const temp = model.value.langFrom
  model.value.langFrom = model.value.langTo
  model.value.langTo = temp
}

// Ref for the link input container to enable auto-focus
const linkInputContainerRef = ref(null)

// Watch for tab changes to auto-focus the input when Link tab is selected
watch(() => model.value.source, async (newSource) => {
  if (newSource === 'Link') {
    // Wait for the tab content to be rendered and visible
    await nextTick()
    // Add a small delay to ensure the TabsContent is fully visible
    setTimeout(() => {
      if (linkInputContainerRef.value) {
        // Find the input element within the container
        const inputElement = linkInputContainerRef.value.querySelector('input')
        if (inputElement && typeof inputElement.focus === 'function') {
          inputElement.focus()
        }
      }
    }, 100)
  }
})

// Create computed properties for two-way binding with validation
const langFrom = computed({
  get: () => {
    const value = model.value.langFrom
    // Validate value exists in languages array
    if (value && languages.value.length > 0 && !languages.value.includes(value)) {
      console.warn('[TranslationOptions] langFrom value not in languages:', value, 'Available:', languages.value)
    }
    return value
  },
  set: (val) => {
    console.debug('[TranslationOptions] langFrom changed:', model.value.langFrom, '->', val)
    if (languages.value.includes(val)) {
      model.value.langFrom = val
    } else {
      console.warn('[TranslationOptions] Invalid langFrom value:', val)
    }
  }
})

const langTo = computed({
  get: () => {
    const value = model.value.langTo
    // Validate value exists in languages array
    if (value && languages.value.length > 0 && !languages.value.includes(value)) {
      console.warn('[TranslationOptions] langTo value not in languages:', value, 'Available:', languages.value)
    }
    return value
  },
  set: (val) => {
    console.debug('[TranslationOptions] langTo changed:', model.value.langTo, '->', val)
    if (languages.value.includes(val)) {
      model.value.langTo = val
    } else {
      console.warn('[TranslationOptions] Invalid langTo value:', val)
    }
  }
})

const service = computed({
  get: () => {
    const value = model.value.service
    // Validate value exists in services array
    if (value && services.value.length > 0 && !services.value.includes(value)) {
      console.warn('[TranslationOptions] service value not in services:', value, 'Available:', services.value)
    }
    return value
  },
  set: (val) => {
    console.debug('[TranslationOptions] service changed:', model.value.service, '->', val)
    if (services.value.includes(val)) {
      model.value.service = val
    } else {
      console.warn('[TranslationOptions] Invalid service value:', val)
    }
  }
})

// Log initial state on mount
onMounted(() => {
  console.debug('[TranslationOptions] Component mounted', {
    config: props.config,
    model: model.value,
    languages: languages.value,
    services: services.value
  })
})
</script>

<template>
  <div class="space-y-6">
    <Tabs v-model="model.source" class="w-full">
      <TabsList class="grid w-full grid-cols-2">
        <TabsTrigger value="File">{{ t('translation.file') }}</TabsTrigger>
        <TabsTrigger value="Link">{{ t('translation.link') }}</TabsTrigger>
      </TabsList>
      <TabsContent value="File" class="mt-2">
        <FileSelector @file-selected="handleFileSelected" />
      </TabsContent>
      <TabsContent value="Link" class="mt-2">
        <div ref="linkInputContainerRef" class="space-y-2">
          <Label>{{ t('translation.pdfLink') }}</Label>
          <Input 
            v-model="model.url" 
            :placeholder="t('translation.pdfLinkPlaceholder')" 
          />
        </div>
      </TabsContent>
    </Tabs>

    <div class="flex items-end gap-2">
      <div class="flex-1 space-y-2">
        <Label>{{ t('translation.from') }}</Label>
        <Select :model-value="langFrom" @update:model-value="(val) => langFrom = val">
          <SelectTrigger>
            <SelectValue :placeholder="t('translation.selectLanguage')">
              <span v-if="langFrom">{{ langFrom }}</span>
              <span v-else class="text-muted-foreground">{{ t('translation.selectLanguage') }}</span>
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            <SelectItem 
              v-for="lang in languages" 
              :key="`from-${lang}`" 
              :value="lang"
            >
              {{ lang }}
            </SelectItem>
            <div v-if="languages.length === 0" class="px-2 py-1.5 text-sm text-muted-foreground">
              {{ t('translation.noLanguagesAvailable') || 'No languages available' }}
            </div>
          </SelectContent>
        </Select>
      </div>

      <Button 
        variant="ghost" 
        size="icon" 
        class="mb-0.5 shrink-0" 
        @click="swapLanguages"
        :title="t('translation.swapLanguages')"
      >
        <ArrowRightLeft 
          class="h-4 w-4 transition-transform duration-300"
          :style="{ transform: `rotate(${rotation}deg)` }"
        />
      </Button>

      <div class="flex-1 space-y-2">
        <Label>{{ t('translation.to') }}</Label>
        <Select :model-value="langTo" @update:model-value="(val) => langTo = val">
          <SelectTrigger>
            <SelectValue :placeholder="t('translation.selectLanguage')">
              <span v-if="langTo">{{ langTo }}</span>
              <span v-else class="text-muted-foreground">{{ t('translation.selectLanguage') }}</span>
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            <SelectItem 
              v-for="lang in languages" 
              :key="`to-${lang}`" 
              :value="lang"
            >
              {{ lang }}
            </SelectItem>
            <div v-if="languages.length === 0" class="px-2 py-1.5 text-sm text-muted-foreground">
              {{ t('translation.noLanguagesAvailable') || 'No languages available' }}
            </div>
          </SelectContent>
        </Select>
      </div>
    </div>

    
    <!-- Advanced Options Accordion or Toggle could go here -->
  </div>
</template>
