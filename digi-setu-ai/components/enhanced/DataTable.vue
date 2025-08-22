<template>
  <div class="w-full p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
    <h3 v-if="title" class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">{{ title }}</h3>
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr>
            <th v-for="header in headers" :key="header" class="px-3 py-2 text-left font-medium text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
              {{ header }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in paginatedData" :key="index" class="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700">
            <td v-for="(value, key) in row" :key="key" class="px-3 py-2 text-gray-900 dark:text-gray-100">
              {{ formatValue(value) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-center gap-4 mt-4">
      <button 
        @click="currentPage--" 
        :disabled="currentPage === 1"
        class="px-3 py-1 bg-blue-500 text-white rounded disabled:bg-gray-300 disabled:cursor-not-allowed hover:bg-blue-600"
      >
        ←
      </button>
      <span class="text-sm text-gray-600 dark:text-gray-400">{{ currentPage }} / {{ totalPages }}</span>
      <button 
        @click="currentPage++" 
        :disabled="currentPage === totalPages"
        class="px-3 py-1 bg-blue-500 text-white rounded disabled:bg-gray-300 disabled:cursor-not-allowed hover:bg-blue-600"
      >
        →
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  data: any[]
  title?: string
  headers?: string[]
  pageSize?: number
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  headers: () => [],
  pageSize: 10
})

const currentPage = ref(1)

// Auto-detect headers
const headers = computed(() => {
  if (props.headers.length) return props.headers
  if (props.data.length) return Object.keys(props.data[0])
  return []
})

const totalPages = computed(() => Math.ceil(props.data.length / props.pageSize))

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * props.pageSize
  return props.data.slice(start, start + props.pageSize)
})

function formatValue(value: any): string {
  if (typeof value === 'number') return value.toLocaleString()
  if (value === null || value === undefined) return '-'
  return String(value)
}
</script>


