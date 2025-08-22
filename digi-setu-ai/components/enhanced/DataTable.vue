<template>
  <div class="data-table-container">
    <h3 v-if="title" class="data-table-title">{{ title }}</h3>
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr>
            <th v-for="header in headers" :key="header" class="table-header">
              {{ header }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in paginatedData" :key="index" class="table-row">
            <td v-for="(value, key) in row" :key="key" class="table-cell">
              {{ formatValue(value) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination">
      <button 
        @click="currentPage--" 
        :disabled="currentPage === 1"
        class="pagination-btn"
      >
        ←
      </button>
      <span class="pagination-info">{{ currentPage }} / {{ totalPages }}</span>
      <button 
        @click="currentPage++" 
        :disabled="currentPage === totalPages"
        class="pagination-btn"
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

<style scoped>
.data-table-container {
  width: 100%;
  padding: 1rem;
  background: var(--bg-primary);
  border-radius: 0.5rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-primary);
}

.data-table-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.overflow-x-auto {
  overflow-x: auto;
}

.w-full {
  width: 100%;
}

.text-sm {
  font-size: 0.875rem;
}

.table-header {
  padding: 0.5rem 0.75rem;
  text-align: left;
  font-weight: 500;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-primary);
}

.table-row {
  border-bottom: 1px solid var(--border-primary);
  transition: background-color 0.2s ease;
}

.table-row:hover {
  background: var(--bg-hover);
}

.table-cell {
  padding: 0.5rem 0.75rem;
  color: var(--text-primary);
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 1rem;
}

.pagination-btn {
  padding: 0.25rem 0.75rem;
  background: var(--accent-primary);
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: var(--accent-hover);
}

.pagination-btn:disabled {
  background: var(--bg-tertiary);
  color: var(--text-muted);
  cursor: not-allowed;
}

.pagination-info {
  font-size: 0.875rem;
  color: var(--text-secondary);
}
</style>

