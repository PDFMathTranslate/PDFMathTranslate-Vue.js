<script setup>
import { computed, ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { Github, Keyboard, Quote, Copy, Check } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

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

// Citation popup logic
const showCitation = ref(false)
const citationTriggerRef = ref(null)
const citationPopupStyle = reactive({ bottom: '0px', left: '0px', transform: 'translateX(-50%)', width: '420px' })
let citationHideTimeout = null
const selectedCitationStyle = ref('')
const bibtexCopied = ref(false)
const citationCopied = ref(false)
const isDropdownOpen = ref(false)

const bibtexContent = `@inproceedings{ouyang-etal-2025-pdfmathtranslate,
    title = "{PDFM}ath{T}ranslate: Scientific Document Translation Preserving Layouts",
    author = "Ouyang, Rongxin  and
      Chu, Chang  and
      Xin, Zhikuang  and
      Ma, Xiangyao",
    editor = {Habernal, Ivan  and
      Schulam, Peter  and
      Tiedemann, J{\\"o}rg},
    booktitle = "Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing: System Demonstrations",
    month = nov,
    year = "2025",
    address = "Suzhou, China",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2025.emnlp-demos.71/",
    pages = "918--924",
    ISBN = "979-8-89176-334-0",
    abstract = "Language barriers in scientific documents hinder the diffusion and development of science and technologies. However, prior efforts in translating such documents largely overlooked the information in layouts. To bridge the gap, we introduce PDFMathTranslate, the world{'}s first open-source software for translating scientific documents while preserving layouts. Leveraging the most recent advances in large language models and precise layout detection, we contribute to the community with key improvements in precision, flexibility, and efficiency. The work is open-sourced at https://github.com/byaidu/pdfmathtranslate with more than 222k downloads."
}`

const citationStyles = [
  { value: 'apa', label: 'APA (7th Edition)' },
  { value: 'chicago', label: 'Chicago (17th Edition)' },
  { value: 'mla', label: 'MLA (9th Edition)' },
  { value: 'ieee', label: 'IEEE' },
  { value: 'harvard', label: 'Harvard' },
  { value: 'acl', label: 'ACL' }
]

const getFormattedCitation = computed(() => {
  const style = selectedCitationStyle.value
  
  const authors = {
    full: 'Rongxin Ouyang, Chang Chu, Zhikuang Xin, and Xiangyao Ma',
    apa: 'Ouyang, R., Chu, C., Xin, Z., & Ma, X.',
    mla: 'Ouyang, Rongxin, et al.',
    chicago: 'Ouyang, Rongxin, Chang Chu, Zhikuang Xin, and Xiangyao Ma',
    ieee: 'R. Ouyang, C. Chu, Z. Xin, and X. Ma',
    harvard: 'Ouyang, R., Chu, C., Xin, Z. and Ma, X.',
    acl: 'Rongxin Ouyang, Chang Chu, Zhikuang Xin, and Xiangyao Ma'
  }
  
  const title = 'PDFMathTranslate: Scientific Document Translation Preserving Layouts'
  const booktitle = 'Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing: System Demonstrations'
  const year = '2025'
  const pages = '918–924'
  const url = 'https://aclanthology.org/2025.emnlp-demos.71/'
  
  switch (style) {
    case 'apa':
      return {
        html: `<p>${authors.apa} (${year}). ${title}. In I. Habernal, P. Schulam, & J. Tiedemann (Eds.), <em>${booktitle}</em> (pp. ${pages}). Association for Computational Linguistics. <a href="${url}" target="_blank" class="text-primary hover:underline">${url}</a></p>`,
        text: `${authors.apa} (${year}). ${title}. In I. Habernal, P. Schulam, & J. Tiedemann (Eds.), ${booktitle} (pp. ${pages}). Association for Computational Linguistics. ${url}`
      }
    case 'chicago':
      return {
        html: `<p>${authors.chicago}. "${title}." In <em>${booktitle}</em>, edited by Ivan Habernal, Peter Schulam, and Jörg Tiedemann, ${pages}. Suzhou, China: Association for Computational Linguistics, ${year}. <a href="${url}" target="_blank" class="text-primary hover:underline">${url}</a>.</p>`,
        text: `${authors.chicago}. "${title}." In ${booktitle}, edited by Ivan Habernal, Peter Schulam, and Jörg Tiedemann, ${pages}. Suzhou, China: Association for Computational Linguistics, ${year}. ${url}.`
      }
    case 'mla':
      return {
        html: `<p>${authors.mla} "${title}." <em>${booktitle}</em>, edited by Ivan Habernal et al., Association for Computational Linguistics, ${year}, pp. ${pages}. <a href="${url}" target="_blank" class="text-primary hover:underline">${url}</a>.</p>`,
        text: `${authors.mla} "${title}." ${booktitle}, edited by Ivan Habernal et al., Association for Computational Linguistics, ${year}, pp. ${pages}. ${url}.`
      }
    case 'ieee':
      return {
        html: `<p>${authors.ieee}, "${title}," in <em>${booktitle}</em>, Suzhou, China, Nov. ${year}, pp. ${pages}. [Online]. Available: <a href="${url}" target="_blank" class="text-primary hover:underline">${url}</a></p>`,
        text: `${authors.ieee}, "${title}," in ${booktitle}, Suzhou, China, Nov. ${year}, pp. ${pages}. [Online]. Available: ${url}`
      }
    case 'harvard':
      return {
        html: `<p>${authors.harvard} (${year}) '${title}', in Habernal, I., Schulam, P. and Tiedemann, J. (eds.) <em>${booktitle}</em>. Suzhou, China: Association for Computational Linguistics, pp. ${pages}. Available at: <a href="${url}" target="_blank" class="text-primary hover:underline">${url}</a>.</p>`,
        text: `${authors.harvard} (${year}) '${title}', in Habernal, I., Schulam, P. and Tiedemann, J. (eds.) ${booktitle}. Suzhou, China: Association for Computational Linguistics, pp. ${pages}. Available at: ${url}.`
      }
    case 'acl':
      return {
        html: `<p>${authors.acl}. ${year}. <a href="${url}" target="_blank" class="text-primary hover:underline">${title}</a>. In <em>${booktitle}</em>, pages ${pages}, Suzhou, China. Association for Computational Linguistics.</p>`,
        text: `${authors.acl}. ${year}. ${title}. In ${booktitle}, pages ${pages}, Suzhou, China. Association for Computational Linguistics.`
      }
    default:
      return null
  }
})

const showCitationPopup = () => {
  if (citationHideTimeout) {
    clearTimeout(citationHideTimeout)
    citationHideTimeout = null
  }
  
  if (citationTriggerRef.value) {
    const rect = citationTriggerRef.value.getBoundingClientRect()
    const popupWidth = Math.min(420, window.innerWidth * 0.9) // Use 420px or 90vw, whichever is smaller
    const margin = 16 // Minimum margin from window edge
    
    // Position to the left of center (shift left by 80px)
    let leftPosition = rect.left + rect.width / 2 - 80
    
    // Ensure it doesn't go off the left edge
    if (leftPosition - popupWidth / 2 < margin) {
      leftPosition = margin + popupWidth / 2
    }
    
    // Ensure it doesn't go off the right edge
    if (leftPosition + popupWidth / 2 > window.innerWidth - margin) {
      leftPosition = window.innerWidth - margin - popupWidth / 2
    }
    
    citationPopupStyle.width = `${popupWidth}px`
    citationPopupStyle.bottom = `${window.innerHeight - rect.top + 8}px`
    citationPopupStyle.left = `${leftPosition}px`
    citationPopupStyle.transform = 'translateX(-50%)'
    showCitation.value = true
  }
}

const scheduleCitationHide = () => {
  // Don't hide if dropdown is open
  if (isDropdownOpen.value) return
  
  citationHideTimeout = setTimeout(() => {
    showCitation.value = false
  }, 300)
}

const cancelCitationHide = () => {
  if (citationHideTimeout) {
    clearTimeout(citationHideTimeout)
    citationHideTimeout = null
  }
}

const copyBibtex = async () => {
  try {
    await navigator.clipboard.writeText(bibtexContent)
    bibtexCopied.value = true
    setTimeout(() => {
      bibtexCopied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy BibTeX:', err)
  }
}

const copyCitation = async () => {
  if (!getFormattedCitation.value) return
  try {
    await navigator.clipboard.writeText(getFormattedCitation.value.text)
    citationCopied.value = true
    setTimeout(() => {
      citationCopied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy citation:', err)
  }
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
            <TooltipContent side="top" :side-offset="12" :align-offset="8" align="start" class="max-w-xs">
              <div class="space-y-1.5">
                <p class="font-semibold">{{ statusTitle }}</p>
                <template v-if="health && !health.error">
                  <div class="flex justify-between items-center">
                    <span class="text-muted-foreground">{{ t('service.currentTasks') }}:</span>
                    <span class="font-mono">{{ (health.active_tasks || 0) + (health.pending_tasks || 0) }}</span>
                  </div>
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
                <template v-else-if="health && health.error">
                  <p class="text-xs text-red-500">
                    {{ t('service.errorFetchingHealth') }}
                  </p>
                </template>
                <template v-else>
                  <div class="flex justify-between items-center">
                    <span class="text-muted-foreground">{{ t('service.currentTasks') }}:</span>
                    <span class="font-mono">0</span>
                  </div>
                </template>
              </div>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
        <p class="text-xs text-muted-foreground">{{ t('app.subtitle') }}</p>
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
      <!-- Shortcuts Button -->
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

      <!-- Citation Button -->
      <div
        ref="citationTriggerRef"
        class="relative flex items-center"
        @mouseenter="showCitationPopup"
        @mouseleave="scheduleCitationHide"
      >
        <Button variant="ghost" size="sm">
          <Quote class="w-4 h-4 mr-2" />
          {{ t('citation.title') }}
        </Button>
        <Teleport to="body">
          <Transition name="citation-fade">
            <div
              v-if="showCitation"
              class="fixed bg-white dark:bg-zinc-950 border rounded-xl shadow-2xl p-5 z-[2147483647]"
              :style="{
                bottom: citationPopupStyle.bottom,
                left: citationPopupStyle.left,
                transform: citationPopupStyle.transform,
                width: citationPopupStyle.width,
                maxHeight: '85vh',
                overflowY: 'auto'
              }"
              @mouseenter="cancelCitationHide"
              @mouseleave="scheduleCitationHide"
            >
              <div class="space-y-4">
                <!-- Header -->
                <div class="flex items-center justify-between">
                  <h3 class="font-semibold text-sm text-foreground">{{ t('citation.citeThisWork') }}</h3>
                </div>
                
                <!-- BibTeX Section -->
                <div class="space-y-2">
                  <div class="flex items-center justify-between">
                    <span class="text-xs font-medium text-muted-foreground uppercase tracking-wide">BibTeX</span>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      class="h-7 px-2 text-xs"
                      @click="copyBibtex"
                    >
                      <Check v-if="bibtexCopied" class="w-3 h-3 mr-1.5 text-green-500" />
                      <Copy v-else class="w-3 h-3 mr-1.5" />
                      {{ bibtexCopied ? t('citation.copied') : t('citation.copyBibtex') }}
                    </Button>
                  </div>
                  <div class="bg-muted/50 rounded-lg p-3 overflow-x-auto">
                    <pre class="text-xs font-mono text-muted-foreground whitespace-pre-wrap break-all leading-relaxed">@inproceedings{ouyang-etal-2025-pdfmathtranslate,
  title = "PDFMathTranslate: Scientific Document
           Translation Preserving Layouts",
  author = "Ouyang, Rongxin and Chu, Chang
            and Xin, Zhikuang and Ma, Xiangyao",
  booktitle = "EMNLP 2025 System Demonstrations",
  year = "2025",
  pages = "918--924"
}</pre>
                  </div>
                </div>

                <!-- Divider -->
                <div class="border-t border-border"></div>

                <!-- Citation Style Selector -->
                <div class="space-y-2">
                  <span class="text-xs font-medium text-muted-foreground uppercase tracking-wide">{{ t('citation.formattedCitation') }}</span>
                  <Select 
                    v-model="selectedCitationStyle"
                    @update:open="isDropdownOpen = $event"
                  >
                    <SelectTrigger class="w-full h-9">
                      <SelectValue :placeholder="t('citation.selectStyle')" />
                    </SelectTrigger>
                    <SelectContent class="z-[2147483648]">
                      <SelectItem 
                        v-for="style in citationStyles" 
                        :key="style.value" 
                        :value="style.value"
                      >
                        {{ style.label }}
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <!-- Rendered Citation -->
                <Transition name="citation-content">
                  <div v-if="getFormattedCitation" class="space-y-2">
                    <div class="flex items-center justify-between">
                      <span class="text-xs text-muted-foreground">{{ citationStyles.find(s => s.value === selectedCitationStyle)?.label }}</span>
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        class="h-7 px-2 text-xs"
                        @click="copyCitation"
                      >
                        <Check v-if="citationCopied" class="w-3 h-3 mr-1.5 text-green-500" />
                        <Copy v-else class="w-3 h-3 mr-1.5" />
                        {{ citationCopied ? t('citation.copied') : t('citation.copy') }}
                      </Button>
                    </div>
                    <div 
                      class="bg-muted/30 rounded-lg p-4 text-sm leading-relaxed border-l-4 border-primary/40 break-words overflow-wrap-anywhere"
                      v-html="getFormattedCitation.html"
                    ></div>
                  </div>
                </Transition>
              </div>
            </div>
          </Transition>
        </Teleport>
      </div>

      <!-- GitHub Button with Tooltip -->
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger as-child>
            <a href="https://github.com/PDFMathTranslate/PDFMathTranslate" target="_blank" rel="noreferrer">
              <Button variant="ghost" size="sm">
                <Github class="w-4 h-4 mr-2" />
                GitHub
              </Button>
            </a>
          </TooltipTrigger>
          <TooltipContent side="top" class="max-w-xs">
            <p class="whitespace-pre-line text-xs">
              Give us a ✨ if you like this tool.
              Made with love by Rongxin, Byaidu, awwaawwa, hellofinch
            </p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.citation-fade-enter-active,
.citation-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.citation-fade-enter-from,
.citation-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(8px);
}

.citation-content-enter-active,
.citation-content-leave-active {
  transition: opacity 0.15s ease, max-height 0.2s ease;
  overflow: hidden;
}

.citation-content-enter-from,
.citation-content-leave-to {
  opacity: 0;
  max-height: 0;
}

.citation-content-enter-to,
.citation-content-leave-from {
  max-height: 300px;
}
</style>
