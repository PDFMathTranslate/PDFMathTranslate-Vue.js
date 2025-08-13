<!--
 * @Author: Rongxin rongxin@u.nus.edu
 * @Date: 2025-08-13 13:58:31
 * @LastEditors: Rongxin rongxin@u.nus.edu
 * @LastEditTime: 2025-08-13 18:54:17
 * @FilePath: /PDFMathTranslate-Vue.js/gui-vue/src/components/PdfViewer.vue
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
-->
<template>
  <div ref="wrapper" class="relative w-full h-[420px] overflow-auto rounded border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900">
    <canvas ref="canvas" class="block mx-auto" />
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { GlobalWorkerOptions, getDocument } from 'pdfjs-dist'
import PdfWorker from 'pdfjs-dist/build/pdf.worker.min.mjs?worker'

GlobalWorkerOptions.workerPort = new PdfWorker()

const props = defineProps<{ src: string; page?: number }>()

const wrapper = ref<HTMLElement | null>(null)
const canvas = ref<HTMLCanvasElement | null>(null)
let resizeObserver: ResizeObserver | null = null

async function renderPdf() {
  if (!props.src || !canvas.value) return
  try {
    const loadingTask = getDocument(props.src)
    const pdf = await loadingTask.promise
    const page = await pdf.getPage(props.page || 1)

    const baseViewport = page.getViewport({ scale: 1 })
    const targetWidth = Math.max(100, (wrapper.value?.clientWidth ?? 2400))
    const scale = targetWidth / baseViewport.width
    const viewport = page.getViewport({ scale })

    const ctx = canvas.value.getContext('2d')
    if (!ctx) return
    canvas.value.width = viewport.width
    canvas.value.height = viewport.height

    await page.render({ canvasContext: ctx, viewport }).promise
    pdf.destroy()
  } catch (e) {
    // swallow render errors for preview purposes
  }
}

watch(() => props.src, () => renderPdf())
watch(() => props.page, () => renderPdf())
onMounted(() => {
  renderPdf()
  if ('ResizeObserver' in window) {
    resizeObserver = new ResizeObserver(() => {
      renderPdf()
    })
    if (wrapper.value) resizeObserver.observe(wrapper.value)
  } else {
    window.addEventListener('resize', renderPdf)
  }
})

onBeforeUnmount(() => {
  if (resizeObserver && wrapper.value) {
    resizeObserver.unobserve(wrapper.value)
    resizeObserver.disconnect()
    resizeObserver = null
  } else {
    window.removeEventListener('resize', renderPdf)
  }
})
</script>


