<template>
  <div class="chart-container">
    <h3 v-if="title" class="chart-title">{{ title }}</h3>
    <div class="relative h-80">
      <canvas 
        :ref="canvasId"
        :id="canvasId"
        class="w-full h-full"
      ></canvas>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick, onBeforeUnmount } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

interface Props {
  type: string
  title?: string
  data: any
  options?: any
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  options: () => ({})
})

const canvasId = `chart-${Math.random().toString(36).substr(2, 9)}`
let chartInstance: Chart | null = null

// Micro color palette
const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4', '#84CC16', '#F97316', '#EC4899', '#6B7280']

const createChart = async () => {
  await nextTick()
  
  const canvas = document.getElementById(canvasId) as HTMLCanvasElement
  if (!canvas || !props.data) return

  // Destroy existing
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }

  // Auto-format data based on type
  let chartData = props.data
  
  // Smart data formatting
  if (Array.isArray(props.data)) {
    if (props.type === 'pie' || props.type === 'doughnut') {
      chartData = {
        labels: props.data.map(d => d.label || d.name),
        datasets: [{
          data: props.data.map(d => d.value || d.y),
          backgroundColor: COLORS
        }]
      }
    } else if (props.type === 'bar' || props.type === 'line') {
      chartData = {
        labels: props.data.map(d => d.label || d.name || d.x),
        datasets: [{
          label: props.title || 'Data',
          data: props.data.map(d => d.value || d.y),
          backgroundColor: props.type === 'line' ? 'transparent' : COLORS[0],
          borderColor: COLORS[0],
          tension: props.type === 'line' ? 0.4 : 0
        }]
      }
    } else if (props.type === 'scatter' || props.type === 'bubble') {
      chartData = {
        datasets: [{
          label: props.title || 'Data',
          data: props.data.map(d => ({ x: d.x, y: d.y, r: d.r || 5 })),
          backgroundColor: COLORS[0],
          borderColor: COLORS[0]
        }]
      }
    }
  }

  // Default options
  const defaultOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: props.type !== 'bar' && props.type !== 'line' }
    }
  }

  try {
    chartInstance = new Chart(canvas, {
      type: props.type as any,
      data: chartData,
      options: { ...defaultOptions, ...props.options }
    })
  } catch (error) {
    console.error('Chart creation failed:', error)
  }
}

watch([() => props.data, () => props.type], createChart, { deep: true })
onMounted(createChart)
onBeforeUnmount(() => chartInstance?.destroy())
</script>

<style scoped>
.chart-container {
  width: 100%;
  padding: 1rem;
  background: var(--bg-primary);
  border-radius: 0.5rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-primary);
}

.chart-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.relative {
  position: relative;
}

.h-80 {
  height: 20rem;
}

.w-full {
  width: 100%;
}

.h-full {
  height: 100%;
}
</style>
