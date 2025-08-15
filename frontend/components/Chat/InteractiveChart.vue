<template>
  <div class="interactive-chart-container">
    <!-- Chart Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center space-x-3">
        <div class="p-2 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg">
          <BarChart3 class="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            {{ chart.title }}
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ chart.type }} chart • {{ chart.data?.length || 0 }} data points
          </p>
        </div>
      </div>
      
      <div class="flex items-center space-x-2">
        <USelectMenu
          v-model="selectedChartType"
          :options="chartTypes"
          size="sm"
          @change="updateChartType"
        />
        <UButton 
          @click="exportChart" 
          size="sm" 
          variant="ghost"
          icon="i-lucide-download"
        />
      </div>
    </div>

    <!-- Chart Display -->
    <div class="chart-display bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
      <!-- Simple Chart Visualization -->
      <div class="space-y-4">
        <!-- Bar Chart -->
        <div v-if="currentChartType === 'bar'" class="space-y-3">
          <div 
            v-for="(item, index) in processedData" 
            :key="index"
            class="flex items-center space-x-4"
          >
            <div class="w-20 text-sm text-gray-700 dark:text-gray-300 truncate">
              {{ item.label }}
            </div>
            <div class="flex-1 relative">
              <div class="h-8 bg-gray-100 dark:bg-gray-700 rounded-lg overflow-hidden">
                <div 
                  class="h-full bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg transition-all duration-1000 ease-out"
                  :style="{ width: `${(item.value / maxValue) * 100}%` }"
                ></div>
              </div>
              <span class="absolute right-2 top-1 text-xs text-gray-600 dark:text-gray-400">
                {{ formatValue(item.value) }}
              </span>
            </div>
          </div>
        </div>

        <!-- Line Chart -->
        <div v-else-if="currentChartType === 'line'" class="relative h-64">
          <svg class="w-full h-full" viewBox="0 0 400 200">
            <!-- Grid lines -->
            <defs>
              <pattern id="grid" width="40" height="20" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 20" fill="none" stroke="#e5e7eb" stroke-width="1"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
            
            <!-- Data line -->
            <polyline
              :points="linePoints"
              fill="none"
              stroke="url(#lineGradient)"
              stroke-width="3"
              class="animate-draw-line"
            />
            
            <!-- Data points -->
            <circle
              v-for="(point, index) in linePointsArray"
              :key="index"
              :cx="point.x"
              :cy="point.y"
              r="4"
              fill="#6366f1"
              class="animate-fade-in-delayed"
              :style="{ animationDelay: `${index * 0.1}s` }"
            />
            
            <!-- Gradient definition -->
            <defs>
              <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style="stop-color:#6366f1;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#8b5cf6;stop-opacity:1" />
              </linearGradient>
            </defs>
          </svg>
        </div>

        <!-- Pie Chart -->
        <div v-else-if="currentChartType === 'pie'" class="flex items-center justify-center">
          <div class="relative w-64 h-64">
            <svg class="w-full h-full transform -rotate-90" viewBox="0 0 200 200">
              <circle
                v-for="(segment, index) in pieSegments"
                :key="index"
                :cx="100"
                :cy="100"
                :r="80"
                fill="none"
                :stroke="segment.color"
                :stroke-width="20"
                :stroke-dasharray="`${segment.length} ${circumference - segment.length}`"
                :stroke-dashoffset="segment.offset"
                class="transition-all duration-1000 ease-out"
              />
            </svg>
            
            <!-- Legend -->
            <div class="absolute -right-20 top-0 space-y-2">
              <div 
                v-for="(item, index) in processedData" 
                :key="index"
                class="flex items-center space-x-2 text-sm"
              >
                <div 
                  class="w-3 h-3 rounded-full"
                  :style="{ backgroundColor: pieSegments[index]?.color }"
                ></div>
                <span class="text-gray-700 dark:text-gray-300">{{ item.label }}</span>
                <span class="text-gray-500 dark:text-gray-400">({{ formatValue(item.value) }})</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Scatter Plot -->
        <div v-else-if="currentChartType === 'scatter'" class="relative h-64">
          <svg class="w-full h-full" viewBox="0 0 400 200">
            <!-- Grid -->
            <rect width="100%" height="100%" fill="url(#grid)" />
            
            <!-- Scatter points -->
            <circle
              v-for="(point, index) in scatterPoints"
              :key="index"
              :cx="point.x"
              :cy="point.y"
              :r="point.size || 5"
              :fill="point.color || '#6366f1'"
              class="animate-fade-in-delayed hover:r-8 transition-all cursor-pointer"
              :style="{ animationDelay: `${index * 0.05}s` }"
              @mouseenter="showTooltip(point, $event)"
              @mouseleave="hideTooltip"
            />
          </svg>
        </div>
      </div>

      <!-- Chart Info -->
      <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
        <div class="flex items-center justify-between text-sm">
          <div class="flex items-center space-x-4 text-gray-600 dark:text-gray-400">
            <span>{{ chart.xAxis || 'X-Axis' }}</span>
            <span>•</span>
            <span>{{ chart.yAxis || 'Y-Axis' }}</span>
          </div>
          <div class="flex items-center space-x-2 text-gray-500 dark:text-gray-400">
            <TrendingUp class="w-4 h-4" />
            <span>Interactive Chart</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { BarChart3, TrendingUp } from 'lucide-vue-next'

const props = defineProps({
  chart: {
    type: Object,
    required: true,
    default: () => ({
      title: 'Interactive Chart',
      type: 'bar',
      data: [],
      xAxis: 'X-Axis',
      yAxis: 'Y-Axis'
    })
  }
})

// Chart state
const selectedChartType = ref(props.chart.type || 'bar')

const chartTypes = [
  { value: 'bar', label: 'Bar Chart' },
  { value: 'line', label: 'Line Chart' },
  { value: 'pie', label: 'Pie Chart' },
  { value: 'scatter', label: 'Scatter Plot' }
]

const currentChartType = computed(() => selectedChartType.value)

// Data processing
const processedData = computed(() => {
  if (!props.chart.data) return []
  
  return props.chart.data.map((item, index) => {
    if (typeof item === 'object') {
      return {
        label: item.label || item.name || `Item ${index + 1}`,
        value: Number(item.value || item.y || item.count || 0)
      }
    } else {
      return {
        label: `Item ${index + 1}`,
        value: Number(item) || 0
      }
    }
  })
})

const maxValue = computed(() => {
  return Math.max(...processedData.value.map(item => item.value), 1)
})

// Line chart calculations
const linePoints = computed(() => {
  if (processedData.value.length === 0) return ''
  
  const width = 400
  const height = 200
  const padding = 20
  
  return processedData.value.map((item, index) => {
    const x = padding + (index / (processedData.value.length - 1)) * (width - 2 * padding)
    const y = height - padding - ((item.value / maxValue.value) * (height - 2 * padding))
    return `${x},${y}`
  }).join(' ')
})

const linePointsArray = computed(() => {
  if (processedData.value.length === 0) return []
  
  const width = 400
  const height = 200
  const padding = 20
  
  return processedData.value.map((item, index) => ({
    x: padding + (index / (processedData.value.length - 1)) * (width - 2 * padding),
    y: height - padding - ((item.value / maxValue.value) * (height - 2 * padding))
  }))
})

// Pie chart calculations
const circumference = 2 * Math.PI * 80
const totalValue = computed(() => {
  return processedData.value.reduce((sum, item) => sum + item.value, 0)
})

const pieSegments = computed(() => {
  let currentOffset = 0
  const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#ef4444']
  
  return processedData.value.map((item, index) => {
    const percentage = item.value / totalValue.value
    const length = percentage * circumference
    const segment = {
      length,
      offset: -currentOffset,
      color: colors[index % colors.length]
    }
    currentOffset += length
    return segment
  })
})

// Scatter plot calculations
const scatterPoints = computed(() => {
  if (processedData.value.length === 0) return []
  
  const width = 400
  const height = 200
  const padding = 20
  const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981']
  
  return processedData.value.map((item, index) => ({
    x: padding + Math.random() * (width - 2 * padding),
    y: height - padding - ((item.value / maxValue.value) * (height - 2 * padding)),
    size: Math.max(4, Math.min(12, item.value / maxValue.value * 10)),
    color: colors[index % colors.length],
    label: item.label,
    value: item.value
  }))
})

// Chart actions
const updateChartType = (newType) => {
  selectedChartType.value = newType
}

const exportChart = () => {
  const exportData = {
    title: props.chart.title,
    type: currentChartType.value,
    data: processedData.value,
    xAxis: props.chart.xAxis,
    yAxis: props.chart.yAxis,
    timestamp: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `chart-${props.chart.title.toLowerCase().replace(/\s+/g, '-')}.json`
  a.click()
  URL.revokeObjectURL(url)
}

// Utility functions
const formatValue = (value) => {
  if (value > 1000000) return (value / 1000000).toFixed(1) + 'M'
  if (value > 1000) return (value / 1000).toFixed(1) + 'K'
  return value.toLocaleString()
}

const showTooltip = (point, event) => {
  // Simple tooltip implementation
  console.log('Chart point:', point)
}

const hideTooltip = () => {
  // Hide tooltip
}
</script>

<style scoped>
.interactive-chart-container {
  background-color: white;
  border-radius: 1rem;
  border: 1px solid #e5e7eb;
  padding: 1.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s;
}

.interactive-chart-container:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.dark .interactive-chart-container {
  background-color: #1f2937;
  border-color: #374151;
}

.chart-display {
  min-height: 300px;
}

.animate-draw-line {
  stroke-dasharray: 1000;
  stroke-dashoffset: 1000;
  animation: drawLine 2s ease-out forwards;
}

.animate-fade-in-delayed {
  opacity: 0;
  animation: fadeInDelayed 0.5s ease-out forwards;
}

@keyframes drawLine {
  to {
    stroke-dashoffset: 0;
  }
}

@keyframes fadeInDelayed {
  to {
    opacity: 1;
  }
}
</style>
