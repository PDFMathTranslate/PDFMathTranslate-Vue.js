<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Code, Settings2, Wrench, FileJson } from 'lucide-vue-next'

const { t } = useI18n()

const props = defineProps({
  modelValue: { type: Object, required: true },
  config: { type: Object, default: () => ({ all_params: {} }) },
})

const emit = defineEmits(['update:modelValue'])

const model = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// Group params by category
const groupedParams = computed(() => {
  const params = props.config?.all_params || {}
  const groups = {}
  
  for (const [key, param] of Object.entries(params)) {
    const category = param.category || 'other'
    if (!groups[category]) {
      groups[category] = []
    }
    groups[category].push({ key, ...param })
  }
  
  return groups
})

const categoryNames = computed(() => Object.keys(groupedParams.value).sort())

const getCategoryIcon = (category) => {
  if (category.startsWith('engine_')) return Wrench
  if (category === 'translation') return FileJson
  if (category === 'pdf') return Settings2
  return Code
}

const getCategoryTitle = (category) => {
  if (category.startsWith('engine_')) {
    return category.replace('engine_', 'Engine: ')
  }
  return category.charAt(0).toUpperCase() + category.slice(1)
}

const getParamValue = (key, param) => {
  // Try to get from model, fallback to default
  const parts = key.split('.')
  let value = model.value
  for (const part of parts.slice(1)) { // skip category prefix
    if (value && typeof value === 'object') {
      value = value[part]
    } else {
      value = undefined
      break
    }
  }
  return value !== undefined ? value : param.default
}

const setParamValue = (key, param, value) => {
  const fieldName = param.name
  if (fieldName) {
    model.value[fieldName] = value
  }
}

const getInputType = (typeStr) => {
  if (!typeStr) return 'text'
  if (typeStr.includes('bool')) return 'switch'
  if (typeStr.includes('int') || typeStr.includes('float')) return 'number'
  return 'text'
}

const accordionValue = ref('translation')
</script>

<template>
  <Card class="dev-settings-card border-dashed border-violet-500/50 bg-violet-500/5">
    <CardHeader class="pb-3">
      <CardTitle class="flex items-center gap-2 text-violet-600 dark:text-violet-400">
        <Code class="h-5 w-5" />
        {{ t('devMode.advancedSettingsTitle') }}
      </CardTitle>
      <CardDescription class="text-violet-600/70 dark:text-violet-400/70">
        {{ t('devMode.advancedSettingsDescription') }}
      </CardDescription>
    </CardHeader>
    <CardContent>
      <Accordion type="single" collapsible class="w-full" v-model="accordionValue">
        <AccordionItem v-for="category in categoryNames" :key="category" :value="category">
          <AccordionTrigger class="text-sm">
            <div class="flex items-center gap-2">
              <component :is="getCategoryIcon(category)" class="h-4 w-4" />
              {{ getCategoryTitle(category) }}
              <Badge variant="secondary" class="ml-2 text-xs">
                {{ groupedParams[category].length }}
              </Badge>
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <div class="space-y-4 pt-2">
              <div 
                v-for="param in groupedParams[category]" 
                :key="param.key"
                class="p-3 rounded-lg bg-background/50 border space-y-2"
              >
                <div class="flex items-center justify-between">
                  <div class="space-y-1">
                    <Label :for="param.key" class="font-mono text-sm">
                      {{ param.name }}
                    </Label>
                    <p v-if="param.description" class="text-xs text-muted-foreground">
                      {{ param.description }}
                    </p>
                    <Badge variant="outline" class="text-xs font-mono">
                      {{ param.type }}
                    </Badge>
                  </div>
                  
                  <!-- Switch for boolean -->
                  <Switch 
                    v-if="getInputType(param.type) === 'switch'"
                    :id="param.key"
                    :checked="getParamValue(param.key, param)"
                    @update:checked="setParamValue(param.key, param, $event)"
                  />
                </div>
                
                <!-- Input for non-boolean -->
                <Input 
                  v-if="getInputType(param.type) !== 'switch'"
                  :id="param.key"
                  :type="getInputType(param.type)"
                  :value="getParamValue(param.key, param)"
                  :placeholder="param.default !== null ? String(param.default) : 'Not set'"
                  @input="setParamValue(param.key, param, $event.target.value)"
                  class="font-mono text-sm"
                />
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>
      
      <!-- Raw JSON View -->
      <div class="mt-4 pt-4 border-t">
        <Label class="text-sm font-medium mb-2 block">Current Model State (JSON)</Label>
        <pre class="p-3 rounded-lg bg-muted/50 border overflow-auto max-h-40 text-xs font-mono">{{ JSON.stringify(model, null, 2) }}</pre>
      </div>
    </CardContent>
  </Card>
</template>

<style scoped>
.dev-settings-card {
  animation: pulse-border-violet 2s ease-in-out infinite;
}

@keyframes pulse-border-violet {
  0%, 100% {
    border-color: rgba(139, 92, 246, 0.3);
  }
  50% {
    border-color: rgba(139, 92, 246, 0.6);
  }
}
</style>

