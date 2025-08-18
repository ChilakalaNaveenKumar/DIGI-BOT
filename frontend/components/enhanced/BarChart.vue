<template>
  <div class="bar-chart-container">
    <div v-if="title" class="chart-title mb-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ title }}</h3>
    </div>
    <div class="chart-wrapper">
      <apexchart
        v-if="chartReady"
        :options="chartOptions"
        :series="series"
        type="bar"
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
interface BarChartData {
  label: string
  value: number
  color?: string
}

interface Props {
  data: BarChartData[]
  title?: string
  height?: string | number
  colors?: string[]
  horizontal?: boolean
  showValues?: boolean
  theme?: 'light' | 'dark' | 'auto'
  xAxisTitle?: string
  yAxisTitle?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  height: 350,
  colors: () => [
    '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
    '#06B6D4', '#84CC16', '#F97316', '#EC4899', '#6B7280'
  ],
  horizontal: false,
  showValues: true,
  theme: 'auto',
  xAxisTitle: '',
  yAxisTitle: ''
})

const { $colorMode } = useNuxtApp() as { $colorMode?: { value: string } }

const chartReady = ref(false)

// Compute series data for ApexCharts
const series = computed(() => [{
  name: props.yAxisTitle || 'Values',
  data: props.data.map(item => ({
    x: item.label,
    y: item.value,
    fillColor: item.color || props.colors[0]
  }))
}])

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
    id: `bar-chart-${Math.random().toString(36).substr(2, 9)}`,
    type: 'bar',
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
        zoom: false,
        zoomin: false,
        zoomout: false,
        pan: false,
        reset: false
      }
    },
    animations: {
      enabled: true,
      easing: 'easeinout',
      speed: 800
    }
  },
  plotOptions: {
    bar: {
      horizontal: props.horizontal,
      borderRadius: 4,
      dataLabels: {
        position: 'top'
      },
      distributed: true // This allows individual colors for each bar
    }
  },
  colors: props.colors,
  dataLabels: {
    enabled: props.showValues,
    formatter: function(val: number | string) {
      return String(val)
    },
    offsetY: props.horizontal ? 0 : -20,
    offsetX: props.horizontal ? 10 : 0,
    style: {
      fontSize: '12px',
      fontWeight: '600',
      colors: [isDark.value ? '#ffffff' : '#374151']
    }
  },
  xaxis: {
    type: 'category',
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
    borderColor: isDark.value ? '#374151' : '#E5E7EB',
    strokeDashArray: 3
  },
  tooltip: {
    theme: isDark.value ? 'dark' : 'light',
    y: {
      formatter: function(val: number) {
        return val.toString()
      }
    }
  },
  legend: {
    show: false // Hide legend for bar charts by default
  },
  responsive: [{
    breakpoint: 480,
    options: {
      chart: {
        width: 300
      },
      plotOptions: {
        bar: {
          horizontal: true
        }
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
.bar-chart-container {
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
