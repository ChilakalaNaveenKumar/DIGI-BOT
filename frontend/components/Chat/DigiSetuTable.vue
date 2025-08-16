<template>
  <div class="ds-table-container">
    <div v-if="searchable" class="ds-table-search">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search table..."
        class="ds-search-input"
      />
    </div>
    <div class="ds-table-wrapper">
      <table class="ds-table">
        <thead>
          <tr>
            <th
              v-for="(header, index) in tableHeaders"
              :key="index"
              :class="{ 'ds-sortable': sortable }"
              @click="sortable ? sortBy(index) : null"
            >
              {{ header }}
              <ChevronUp v-if="sortable && sortColumn === index && sortDirection === 'asc'" class="w-4 h-4 inline ml-1" />
              <ChevronDown v-if="sortable && sortColumn === index && sortDirection === 'desc'" class="w-4 h-4 inline ml-1" />
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, rowIndex) in filteredRows" :key="rowIndex">
            <td v-for="(cell, cellIndex) in row" :key="cellIndex">
              {{ cell }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ChevronUp, ChevronDown } from 'lucide-vue-next'

const props = defineProps({
  data: {
    type: [Object, Array],
    required: true
  },
  headers: {
    type: Array,
    default: null
  },
  sortable: {
    type: Boolean,
    default: true
  },
  searchable: {
    type: Boolean,
    default: true
  }
})

const searchQuery = ref('')
const sortColumn = ref(null)
const sortDirection = ref('asc')

// Parse table data
const tableData = computed(() => {
  if (Array.isArray(props.data)) {
    return props.data
  }
  
  if (props.data.headers && props.data.rows) {
    return {
      headers: props.data.headers,
      rows: props.data.rows
    }
  }
  
  // Try to convert object to table format
  const keys = Object.keys(props.data)
  const headers = ['Key', 'Value']
  const rows = keys.map(key => [key, props.data[key]])
  
  return { headers, rows }
})

const tableHeaders = computed(() => {
  return props.headers || tableData.value.headers || []
})

const tableRows = computed(() => {
  if (Array.isArray(tableData.value)) {
    return tableData.value
  }
  return tableData.value.rows || []
})

// Filtering
const filteredRows = computed(() => {
  let rows = [...tableRows.value]
  
  // Apply search filter
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    rows = rows.filter(row => 
      row.some(cell => 
        String(cell).toLowerCase().includes(query)
      )
    )
  }
  
  // Apply sorting
  if (sortColumn.value !== null) {
    rows.sort((a, b) => {
      const aVal = String(a[sortColumn.value] || '')
      const bVal = String(b[sortColumn.value] || '')
      
      const comparison = aVal.localeCompare(bVal, undefined, { numeric: true })
      return sortDirection.value === 'asc' ? comparison : -comparison
    })
  }
  
  return rows
})

const sortBy = (columnIndex) => {
  if (sortColumn.value === columnIndex) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value = columnIndex
    sortDirection.value = 'asc'
  }
}
</script>

<style scoped>
.ds-table-container {
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-lg);
  overflow: hidden;
}

.ds-table-search {
  padding: var(--ds-space-3);
  border-bottom: 1px solid var(--ds-border-primary);
  background: var(--ds-surface-secondary);
}

.ds-search-input {
  width: 100%;
  padding: var(--ds-space-2) var(--ds-space-3);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-md);
  background: var(--ds-surface-primary);
  color: var(--ds-text-primary);
  font-size: var(--ds-text-sm);
}

.ds-search-input:focus {
  outline: none;
  border-color: var(--ds-primary);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--ds-primary) 10%, transparent);
}

.ds-table-wrapper {
  overflow-x: auto;
  max-height: 400px;
  overflow-y: auto;
}

.ds-table {
  width: 100%;
  border-collapse: collapse;
}

.ds-table th {
  background: var(--ds-surface-secondary);
  color: var(--ds-text-primary);
  font-weight: var(--ds-font-medium);
  padding: var(--ds-space-3);
  text-align: left;
  border-bottom: 1px solid var(--ds-border-primary);
  position: sticky;
  top: 0;
  z-index: 1;
}

.ds-table th.ds-sortable {
  cursor: pointer;
  user-select: none;
  transition: background-color var(--ds-transition-fast);
}

.ds-table th.ds-sortable:hover {
  background: var(--ds-surface-tertiary);
}

.ds-table td {
  padding: var(--ds-space-3);
  border-bottom: 1px solid var(--ds-border-secondary);
  color: var(--ds-text-primary);
  vertical-align: top;
}

.ds-table tbody tr:hover {
  background: var(--ds-surface-secondary);
}

.ds-table tbody tr:last-child td {
  border-bottom: none;
}

/* Scrollbar styling */
.ds-table-wrapper::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.ds-table-wrapper::-webkit-scrollbar-track {
  background: var(--ds-surface-primary);
}

.ds-table-wrapper::-webkit-scrollbar-thumb {
  background: var(--ds-border-primary);
  border-radius: 3px;
}

.ds-table-wrapper::-webkit-scrollbar-thumb:hover {
  background: var(--ds-text-muted);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .ds-table th,
  .ds-table td {
    padding: var(--ds-space-2);
    font-size: var(--ds-text-sm);
  }
  
  .ds-table-wrapper {
    max-height: 300px;
  }
}
</style>
