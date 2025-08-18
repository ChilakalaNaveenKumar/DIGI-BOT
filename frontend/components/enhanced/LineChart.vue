<template>
  <div class="line-chart-container">
    <div v-if="title" class="chart-title mb-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ title }}</h3>
    </div>
    <div class="chart-wrapper">
      <apexchart
        v-if="chartReady"
        :options="chartOptions"
        :series="series"
        type="line"
        :height="height"
        class="apex-chart"
      />
      <div v-else class="chart-loading">
        <UiLoadingDots />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface LineChartDataPoint {
  x: string | number
  y: number
}

interface LineChartSeries {
  name: string
  data: LineChartDataPoint[]
  color?: string
}

interface Props {
  data: LineChartSeries[]
  title?: string
  height?: string | number
  colors?: string[]
  smooth?: boolean
  showPoints?: boolean
  showGrid?: boolean
  theme?: 'light' | 'dark' | 'auto'
  xAxisTitle?: string
  yAxisTitle?: string
  xAxisType?: 'category' | 'datetime' | 'numeric'
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  height: 350,
  colors: () => [
    '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
    '#06B6D4', '#84CC16', '#F97316', '#EC4899', '#6B7280'
  ],
  smooth: true,
  showPoints: true,
  showGrid: true,
  theme: 'auto',
  xAxisTitle: '',
  yAxisTitle: '',
  xAxisType: 'category'
})

const { $colorMode } = useNuxtApp() as { $colorMode?: { value: string } }

const chartReady = ref(false)

// Compute series data
const series = computed(() => 
  props.data.map((series, index) => ({
    name: series.name,
    data: series.data,
    color: series.color || props.colors[index % props.colors.length]
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
    id: `line-chart-${Math.random().toString(36).substr(2, 9)}`,
    type: 'line',
    background: 'transparent',
    fontFamily: 'Inter, system-ui, sans-serif',
    // Fix blurriness issues
    pixelRatio: window.devicePixelRatio || 1,
    redrawOnParentResize: true,
    redrawOnWindowResize: true,
    toolbar: {
      show: true,
      tools: {
        download: true,
        selection: false,
        zoom: true,
        zoomin: true,
        zoomout: true,
        pan: true,
        reset: true
      }
    },
    animations: {
      enabled: true,
      easing: 'easeinout',
      speed: 800
    }
  },
  colors: props.colors,
  stroke: {
    curve: props.smooth ? 'smooth' : 'straight',
    width: 3
  },
  markers: {
    size: props.showPoints ? 6 : 0,
    hover: {
      size: 8
    }
  },
  dataLabels: {
    enabled: false
  },
  xaxis: {
    type: props.xAxisType,
    title: {
      text: props.xAxisTitle || '',
      style: {
        color: isDark.value ? '#9CA3AF' : '#6B7280',
        fontSize: '12px',
        fontWeight: '600'
      }
    },
    labels: {
      style: {
        colors: isDark.value ? '#9CA3AF' : '#6B7280',
        fontSize: '12px'
      }
    },
    axisBorder: {
      show: true,
      color: isDark.value ? '#374151' : '#E5E7EB'
    },
    axisTicks: {
      show: true,
      color: isDark.value ? '#374151' : '#E5E7EB'
    }
  },
  yaxis: {
    title: {
      text: props.yAxisTitle || '',
      style: {
        color: isDark.value ? '#9CA3AF' : '#6B7280',
        fontSize: '12px',
        fontWeight: '600'
      }
    },
    labels: {
      style: {
        colors: isDark.value ? '#9CA3AF' : '#6B7280',
        fontSize: '12px'
      }
    }
  },
  grid: {
    show: props.showGrid,
    borderColor: isDark.value ? '#374151' : '#E5E7EB',
    strokeDashArray: 3,
    xaxis: {
      lines: {
        show: props.showGrid
      }
    },
    yaxis: {
      lines: {
        show: props.showGrid
      }
    }
  },
  tooltip: {
    theme: isDark.value ? 'dark' : 'light',
    shared: true,
    intersect: false,
    x: {
      show: true
    },
    y: {
          formatter: function(val: number | string) {
      return String(val)
    }
    }
  },
  legend: {
    show: props.data.length > 1,
    position: 'top',
    horizontalAlign: 'right',
    labels: {
      colors: isDark.value ? '#9CA3AF' : '#6B7280'
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
.line-chart-container {
  width: 100%;
}

.chart-wrapper {
  position: relative;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
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

.apex-chart {
  width: 100%;
}
</style>
