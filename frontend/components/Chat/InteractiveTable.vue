<template>
  <div class="interactive-table-container">
    <!-- Table Header -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center space-x-3">
        <div class="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
          <Table2 class="w-5 h-5 text-blue-600 dark:text-blue-400" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            {{ data.title }}
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ data.rows?.length || 0 }} rows • {{ data.headers?.length || 0 }} columns
          </p>
        </div>
      </div>
      
      <div class="flex items-center space-x-2">
        <UButton 
          v-if="data.searchable" 
          @click="showSearch = !showSearch"
          size="sm" 
          variant="ghost"
          :icon="showSearch ? 'i-lucide-search-x' : 'i-lucide-search'"
        />
        <UButton 
          @click="exportTable" 
          size="sm" 
          variant="ghost"
          icon="i-lucide-download"
        />
      </div>
    </div>

    <!-- Search Bar -->
    <div v-if="showSearch && data.searchable" class="mb-4">
      <UInput
        v-model="searchQuery"
        placeholder="Search table data..."
        icon="i-lucide-search"
        size="sm"
        class="max-w-sm"
      />
    </div>

    <!-- Interactive Table -->
    <div class="overflow-hidden rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
      <UTable
        :columns="tableColumns"
        :rows="filteredRows"
        :loading="false"
        class="w-full"
      >
        <!-- Custom header -->
        <template #header="{ column }">
          <div class="flex items-center space-x-2">
            <span class="font-semibold">{{ column.label }}</span>
            <button 
              v-if="data.sortable"
              @click="toggleSort(column.key)"
              class="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
            >
              <ArrowUpDown class="w-3 h-3 text-gray-400" />
            </button>
          </div>
        </template>

        <!-- Custom cell rendering -->
        <template #[`${column.key}-data`]="{ row }" v-for="column in tableColumns" :key="column.key">
          <div class="py-2">
            <!-- Handle different data types -->
            <UBadge 
              v-if="isUrl(row[column.key])"
              color="blue" 
              variant="soft" 
              size="sm"
              class="cursor-pointer"
              @click="openUrl(row[column.key])"
            >
              {{ formatUrl(row[column.key]) }}
            </UBadge>
            <UBadge 
              v-else-if="isNumber(row[column.key])"
              color="green" 
              variant="soft" 
              size="sm"
            >
              {{ formatNumber(row[column.key]) }}
            </UBadge>
            <span v-else class="text-gray-900 dark:text-gray-100">
              {{ row[column.key] }}
            </span>
          </div>
        </template>
      </UTable>
    </div>

    <!-- Table Stats -->
    <div class="mt-4 flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
      <div class="flex items-center space-x-4">
        <span>{{ filteredRows.length }} of {{ data.rows?.length || 0 }} rows</span>
        <span v-if="searchQuery">• Filtered by: "{{ searchQuery }}"</span>
      </div>
      <div class="flex items-center space-x-2">
        <BarChart3 class="w-4 h-4" />
        <span>Interactive Data Table</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Table2, ArrowUpDown, BarChart3 } from 'lucide-vue-next'

const props = defineProps({
  data: {
    type: Object,
    required: true,
    default: () => ({
      title: 'Data Table',
      headers: [],
      rows: [],
      sortable: true,
      searchable: true
    })
  }
})

// State
const showSearch = ref(false)
const searchQuery = ref('')
const sortColumn = ref('')
const sortDirection = ref('asc')

// Table configuration
const tableColumns = computed(() => {
  if (!props.data.headers) return []
  
  return props.data.headers.map(header => ({
    key: header.toLowerCase().replace(/\s+/g, '_'),
    label: header,
    sortable: props.data.sortable
  }))
})

// Processed table data
const tableRows = computed(() => {
  if (!props.data.rows) return []
  
  return props.data.rows.map((row, index) => {
    const rowObj = { id: index }
    
    if (Array.isArray(row)) {
      // Handle array format
      props.data.headers.forEach((header, headerIndex) => {
        const key = header.toLowerCase().replace(/\s+/g, '_')
        rowObj[key] = row[headerIndex] || ''
      })
    } else if (typeof row === 'object') {
      // Handle object format
      Object.assign(rowObj, row)
    }
    
    return rowObj
  })
})

// Filtered and sorted data
const filteredRows = computed(() => {
  let rows = [...tableRows.value]
  
  // Apply search filter
  if (searchQuery.value && props.data.searchable) {
    const query = searchQuery.value.toLowerCase()
    rows = rows.filter(row => 
      Object.values(row).some(value => 
        String(value).toLowerCase().includes(query)
      )
    )
  }
  
  // Apply sorting
  if (sortColumn.value && props.data.sortable) {
    rows.sort((a, b) => {
      const aVal = a[sortColumn.value]
      const bVal = b[sortColumn.value]
      
      // Handle different data types
      if (isNumber(aVal) && isNumber(bVal)) {
        return sortDirection.value === 'asc' 
          ? Number(aVal) - Number(bVal)
          : Number(bVal) - Number(aVal)
      }
      
      const aStr = String(aVal).toLowerCase()
      const bStr = String(bVal).toLowerCase()
      
      if (sortDirection.value === 'asc') {
        return aStr.localeCompare(bStr)
      } else {
        return bStr.localeCompare(aStr)
      }
    })
  }
  
  return rows
})

// Utility functions
const isUrl = (value) => {
  if (typeof value !== 'string') return false
  return value.startsWith('http://') || value.startsWith('https://')
}

const isNumber = (value) => {
  return !isNaN(Number(value)) && !isNaN(parseFloat(value))
}

const formatUrl = (url) => {
  try {
    const urlObj = new URL(url)
    return urlObj.hostname
  } catch {
    return url
  }
}

const formatNumber = (value) => {
  const num = Number(value)
  if (num > 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num > 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toLocaleString()
}

const openUrl = (url) => {
  window.open(url, '_blank', 'noopener,noreferrer')
}

// Sorting
const toggleSort = (column) => {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value = column
    sortDirection.value = 'asc'
  }
}

// Export functionality
const exportTable = () => {
  const csv = [
    props.data.headers.join(','),
    ...filteredRows.value.map(row => 
      props.data.headers.map(header => {
        const key = header.toLowerCase().replace(/\s+/g, '_')
        return `"${String(row[key] || '').replace(/"/g, '""')}"`
      }).join(',')
    )
  ].join('\n')
  
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${props.data.title.toLowerCase().replace(/\s+/g, '-')}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

// Auto-expand for small tables
const isExpanded = ref(props.data.rows?.length <= 5)
</script>

<style scoped>
.interactive-table-container {
  background-color: white;
  border-radius: 1rem;
  border: 1px solid #e5e7eb;
  padding: 1.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s;
}

.interactive-table-container:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.dark .interactive-table-container {
  background-color: #1f2937;
  border-color: #374151;
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
