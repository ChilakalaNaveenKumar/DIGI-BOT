<template>
  <div class="pie-chart-container">
    <div v-if="title" class="chart-title mb-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ title }}</h3>
    </div>
    <div class="chart-wrapper">
      <apexchart
        v-if="chartReady"
        :options="chartOptions"
        :series="series"
        type="pie"
        :height="height"
        class="apex-chart"
      />
      <div v-else class="chart-loading">
        <UiLoadingDots />
      </div>
    </div>
    <div v-if="showLegend && legendData.length" class="chart-legend mt-4">
      <div class="flex flex-wrap gap-2">
        <div
          v-for="(item, index) in legendData"
          :key="index"
          class="flex items-center gap-2 text-sm"
        >
          <div
            class="w-3 h-3 rounded-full"
            :style="{ backgroundColor: colors[index % colors.length] }"
          />
          <span class="text-gray-700 dark:text-gray-300">
            {{ item.label }}: {{ item.value }}{{ showPercentage ? '%' : '' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface PieChartData {
  label: string
  value: number
  percentage?: number
}

interface Props {
  data: PieChartData[]
  title?: string
  height?: string | number
  colors?: string[]
  showLegend?: boolean
  showPercentage?: boolean
  theme?: 'light' | 'dark' | 'auto'
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  height: 350,
  colors: () => [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
    '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
  ],
  showLegend: true,
  showPercentage: true,
  theme: 'auto'
})

const { $colorMode } = useNuxtApp() as { $colorMode?: { value: string } }

const chartReady = ref(false)

// Compute series data
const series = computed(() => props.data.map(item => item.value))

// Compute legend data
const legendData = computed(() => 
  props.data.map(item => ({
    label: item.label,
    value: item.percentage || item.value
  }))
)

// Chart theme based on color mode
const isDark = computed(() => {
  if (props.theme === 'auto') {
    return $colorMode?.value === 'dark'
  }
  return props.theme === 'dark'
})

// Chart options
const chartOptions = computed(() => ({
  chart: {
    id: `pie-chart-${Math.random().toString(36).substr(2, 9)}`,
    type: 'pie',
    background: 'transparent',
    fontFamily: 'Inter, system-ui, sans-serif',
    animations: {
      enabled: true,
      easing: 'easeinout',
      speed: 1200,
      animateGradually: {
        enabled: true,
        delay: 150
      },
      dynamicAnimation: {
        enabled: true,
        speed: 350
      }
    },
    // Fix blurriness issues
    pixelRatio: window.devicePixelRatio || 1,
    redrawOnParentResize: true,
    redrawOnWindowResize: true
  },
  labels: props.data.map(item => item.label),
  colors: props.colors,
  legend: {
    show: false // We'll use custom legend
  },
  dataLabels: {
    enabled: true,
    formatter: function(val: number) {
      return props.showPercentage ? `${val.toFixed(1)}%` : val.toString()
    },
    style: {
      fontSize: '14px',
      fontWeight: '700',
      fontFamily: 'Inter, system-ui, sans-serif',
      colors: ['#ffffff'],
      textShadow: '1px 1px 2px rgba(0,0,0,0.5)'
    },
    dropShadow: {
      enabled: true,
      top: 1,
      left: 1,
      blur: 1,
      opacity: 0.8
    }
  },
  states: {
    hover: {
      filter: {
        type: 'lighten',
        value: 0.15
      }
    },
    active: {
      allowMultipleDataPointsSelection: false,
      filter: {
        type: 'darken',
        value: 0.1
      }
    }
  },
  plotOptions: {
    pie: {
      expandOnClick: true,
      donut: {
        labels: {
          show: false
        }
      }
    }
  },
  tooltip: {
    theme: isDark.value ? 'dark' : 'light',
    style: {
      fontSize: '13px',
      fontFamily: 'Inter, system-ui, sans-serif'
    },
    y: {
      formatter: function(val: number) {
        return props.showPercentage ? `${val}%` : val.toString()
      }
    }
  },
  responsive: [{
    breakpoint: 480,
    options: {
      chart: {
        width: 300
      },
      legend: {
        position: 'bottom'
      }
    }
  }]
}))

onMounted(() => {
  // Ensure ApexCharts is ready
  nextTick(() => {
    chartReady.value = true
  })
})
</script>

<style scoped>
@reference "tailwindcss";
.pie-chart-container {
  width: 100%;
}

.chart-wrapper {
  position: relative;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  /* Fix blurriness and improve rendering */
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

.chart-loading {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-title h3 {
  text-align: center;
}

.chart-legend {
  @apply border-gray-200 dark:border-gray-700;
  border-top: 1px solid;
  padding-top: 1rem;
}

.chart-legend span {
  @apply text-gray-700 dark:text-gray-300;
}

.apex-chart {
  width: 100%;
}

/* Global ApexCharts improvements */
:deep(.apexcharts-canvas) {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

:deep(.apexcharts-datalabel-label) {
  font-family: 'Inter', system-ui, sans-serif !important;
  font-weight: 700 !important;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
}

:deep(.apexcharts-datalabel-value) {
  font-family: 'Inter', system-ui, sans-serif !important;
  font-weight: 700 !important;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
}

/* Dark mode specific fixes */
@media (prefers-color-scheme: dark) {
  :deep(.apexcharts-datalabel-label),
  :deep(.apexcharts-datalabel-value) {
    fill: #ffffff !important;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.8) !important;
  }
  
  :deep(.apexcharts-legend-text) {
    fill: #e5e7eb !important;
  }
}

:deep(.apexcharts-pie-slice) {
  cursor: pointer;
  transition: all 0.3s ease;
}

:deep(.apexcharts-pie-slice:hover) {
  transform: scale(1.05);
}
</style>
