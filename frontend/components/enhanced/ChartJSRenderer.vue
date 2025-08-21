<template>
  <div class="chartjs-container">
    <div v-if="title" class="chart-title mb-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ title }}</h3>
    </div>
    
    <div class="chart-wrapper">
      <canvas 
        :ref="canvasRef"
        :id="chartId"
        class="chart-canvas"
        :style="{ display: chartReady ? 'block' : 'none' }"
      ></canvas>
      
      <div v-if="!chartReady" class="chart-loading">
        <UiLoadingDots />
      </div>
    </div>
    
    <!-- Chart Info -->
    <div v-if="showInfo" class="chart-info mt-4 text-sm text-gray-600 dark:text-gray-400">
      <p>{{ dataPoints }} data points • {{ chartType }} chart</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick, onBeforeUnmount } from 'vue'
import { Chart, registerables } from 'chart.js'

// Register all Chart.js components
Chart.register(...registerables)

interface Props {
  type: 'pie' | 'bar' | 'line' | 'doughnut' | 'scatter'
  title?: string
  data: any[]
  options?: Record<string, any>
  height?: number
  showInfo?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  height: 400,
  showInfo: true,
  options: () => ({})
})

const chartId = ref(`chart-${Math.random().toString(36).substr(2, 9)}`)
const canvasRef = ref(`canvas-${chartId.value}`)
const chartInstance = ref<Chart | null>(null)
const chartReady = ref(false)

// Chart.js color palette - professional colors
const CHART_COLORS = [
  '#3B82F6', // Blue
  '#10B981', // Emerald  
  '#F59E0B', // Amber
  '#EF4444', // Red
  '#8B5CF6', // Violet
  '#F97316', // Orange
  '#06B6D4', // Cyan
  '#84CC16', // Lime
  '#EC4899', // Pink
  '#6B7280'  // Gray
]

const dataPoints = computed(() => {
  if (props.type === 'line' && Array.isArray(props.data)) {
    return props.data.reduce((total, series) => total + (series.data?.length || 0), 0)
  }
  return Array.isArray(props.data) ? props.data.length : 0
})

const chartType = computed(() => props.type.charAt(0).toUpperCase() + props.type.slice(1))

const createChartConfig = () => {
  const baseConfig = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: false, // We handle title in template
      },
      legend: {
        display: true,
        position: 'bottom' as const,
        labels: {
          padding: 20,
          usePointStyle: true,
          font: {
            size: 12
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1
      }
    }
  }

  switch (props.type) {
    case 'pie':
    case 'doughnut':
      return {
        type: props.type,
        data: {
          labels: props.data.map((item: any) => item.label),
          datasets: [{
            data: props.data.map((item: any) => item.value || item.percentage),
            backgroundColor: CHART_COLORS.slice(0, props.data.length),
            borderWidth: 2,
            borderColor: '#fff',
            hoverBorderWidth: 3
          }]
        },
        options: {
          ...baseConfig,
          cutout: props.type === 'doughnut' ? '50%' : '0%',
          ...props.options
        }
      }

    case 'bar':
      return {
        type: 'bar',
        data: {
          labels: props.data.map((item: any) => item.label),
          datasets: [{
            label: props.title || 'Data',
            data: props.data.map((item: any) => item.value),
            backgroundColor: CHART_COLORS[0] + '80', // Add transparency
            borderColor: CHART_COLORS[0],
            borderWidth: 2,
            borderRadius: 4,
            borderSkipped: false,
          }]
        },
        options: {
          ...baseConfig,
          scales: {
            y: {
              beginAtZero: true,
              grid: {
                color: 'rgba(0, 0, 0, 0.1)'
              }
            },
            x: {
              grid: {
                display: false
              }
            }
          },
          ...props.options
        }
      }

    case 'line':
      // Handle both single series and multi-series data
      const datasets = Array.isArray(props.data) && props.data[0]?.data 
        ? props.data.map((series: any, index: number) => ({
            label: series.name || `Series ${index + 1}`,
            data: series.data?.map((point: any) => point.y) || [],
            borderColor: CHART_COLORS[index % CHART_COLORS.length],
            backgroundColor: CHART_COLORS[index % CHART_COLORS.length] + '20',
            tension: 0.4,
            fill: false,
            pointBackgroundColor: CHART_COLORS[index % CHART_COLORS.length],
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 6
          }))
        : [{
            label: props.title || 'Data',
            data: props.data.map((item: any) => item.value),
            borderColor: CHART_COLORS[0],
            backgroundColor: CHART_COLORS[0] + '20',
            tension: 0.4,
            fill: false
          }]

      const labels = Array.isArray(props.data) && props.data[0]?.data
        ? props.data[0].data.map((point: any) => point.x)
        : props.data.map((item: any) => item.label)

      return {
        type: 'line',
        data: {
          labels,
          datasets
        },
        options: {
          ...baseConfig,
          scales: {
            y: {
              beginAtZero: true,
              grid: {
                color: 'rgba(0, 0, 0, 0.1)'
              }
            },
            x: {
              grid: {
                color: 'rgba(0, 0, 0, 0.05)'
              }
            }
          },
          interaction: {
            intersect: false,
            mode: 'index' as const
          },
          ...props.options
        }
      }

    default:
      return null
  }
}

const renderChart = async () => {
  console.log('ChartJSRenderer - renderChart called with data:', props.data)
  console.log('ChartJSRenderer - Chart type:', props.type)
  
  if (!props.data || props.data.length === 0) {
    console.log('ChartJSRenderer - No data or empty data, setting chartReady to false')
    chartReady.value = false
    return
  }
  
  await nextTick()
  
  const canvas = document.getElementById(chartId.value) as HTMLCanvasElement
  if (!canvas) {
    console.log('ChartJSRenderer - Canvas element not found:', chartId.value)
    return
  }
  
  console.log('ChartJSRenderer - Canvas found, proceeding with chart creation')

  // Destroy existing chart
  if (chartInstance.value) {
    chartInstance.value.destroy()
    chartInstance.value = null
  }

  // Create new chart
  const config = createChartConfig()
  console.log('ChartJSRenderer - Chart config created:', config)
  
  if (config) {
    try {
      console.log('ChartJSRenderer - Creating Chart.js instance')
      chartInstance.value = new Chart(canvas, config)
      chartReady.value = true
      console.log('ChartJSRenderer - Chart created successfully, chartReady set to true')
    } catch (error) {
      console.error('ChartJSRenderer - Error creating chart:', error)
      chartReady.value = false
    }
  } else {
    console.log('ChartJSRenderer - No config returned, chart not created')
    chartReady.value = false
  }
}

// Watch for data changes and re-render
watch([() => props.data, () => props.type, () => props.title], renderChart, { deep: true })

onMounted(() => {
  renderChart()
})

onBeforeUnmount(() => {
  if (chartInstance.value) {
    chartInstance.value.destroy()
  }
})
</script>

<style scoped>
.chartjs-container {
  width: 100%;
  margin: 20px 0;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.dark .chartjs-container {
  background: #1f2937;
  border-color: rgba(255, 255, 255, 0.1);
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3);
}

.chart-wrapper {
  position: relative;
  height: 400px;
  width: 100%;
}

.chart-canvas {
  max-width: 100%;
  height: 100%;
}

.chart-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #6b7280;
}

.chart-title h3 {
  text-align: center;
  margin: 0;
}

.chart-info {
  text-align: center;
  font-size: 0.875rem;
}
</style>
