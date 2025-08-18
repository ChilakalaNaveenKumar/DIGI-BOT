<template>
  <div class="data-table-container">
    <div v-if="title" class="table-title mb-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ title }}</h3>
    </div>
    
    <!-- Search and Filter Bar -->
    <div v-if="searchable || filterable" class="table-controls mb-4 flex gap-4">
      <div v-if="searchable" class="search-control flex-1">
        <UiInput
          v-model="searchTerm"
          placeholder="Search table..."
          class="w-full"
        />
      </div>
      <div v-if="filterable && filterOptions.length" class="filter-control">
        <select
          v-model="selectedFilter"
          class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
        >
          <option value="">All</option>
          <option
            v-for="option in filterOptions"
            :key="option.value"
            :value="option.value"
          >
            {{ option.label }}
          </option>
        </select>
      </div>
    </div>

    <!-- Table -->
    <div class="table-wrapper overflow-x-auto border border-gray-200 dark:border-gray-700 rounded-lg">
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <!-- Table Header -->
        <thead class="bg-gray-50 dark:bg-gray-800">
          <tr>
            <th
              v-for="(header, index) in headers"
              :key="index"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
              @click="sortBy(header.key)"
            >
              <div class="flex items-center gap-2">
                <span>{{ header.label }}</span>
                <div v-if="sortable" class="sort-indicators flex flex-col">
                  <Icon
                    name="lucide:chevron-up"
                    class="w-3 h-3 -mb-1"
                    :class="{
                      'text-blue-600': sortKey === header.key && sortDirection === 'asc',
                      'text-gray-400': !(sortKey === header.key && sortDirection === 'asc')
                    }"
                  />
                  <Icon
                    name="lucide:chevron-down"
                    class="w-3 h-3"
                    :class="{
                      'text-blue-600': sortKey === header.key && sortDirection === 'desc',
                      'text-gray-400': !(sortKey === header.key && sortDirection === 'desc')
                    }"
                  />
                </div>
              </div>
            </th>
          </tr>
        </thead>

        <!-- Table Body -->
        <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
          <tr
            v-for="(row, rowIndex) in paginatedData"
            :key="rowIndex"
            class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            <td
              v-for="(header, colIndex) in headers"
              :key="colIndex"
              class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100"
            >
              <div v-if="header.type === 'badge'" class="inline-flex">
                <UiBadge :variant="getBadgeVariant(String(row[header.key] || ''))">
                  {{ row[header.key] }}
                </UiBadge>
              </div>
              <div v-else-if="header.type === 'link'" class="text-blue-600 hover:text-blue-800 cursor-pointer">
                {{ row[header.key] }}
              </div>
              <div v-else-if="header.type === 'number'" class="font-mono text-right">
                {{ formatNumber(row[header.key]) }}
              </div>
              <div v-else>
                {{ row[header.key] }}
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-if="filteredData.length === 0" class="text-center py-8">
        <Icon name="lucide:search" class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p class="text-gray-500 dark:text-gray-400">No data found</p>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="paginated && totalPages > 1" class="pagination mt-4 flex items-center justify-between">
      <div class="text-sm text-gray-700 dark:text-gray-300">
        Showing {{ startIndex + 1 }} to {{ Math.min(endIndex, filteredData.length) }} of {{ filteredData.length }} results
      </div>
      <div class="flex gap-2">
        <UiButton
          variant="outline"
          size="sm"
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          Previous
        </UiButton>
        <span class="px-3 py-1 text-sm text-gray-700 dark:text-gray-300">
          Page {{ currentPage }} of {{ totalPages }}
        </span>
        <UiButton
          variant="outline"
          size="sm"
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          Next
        </UiButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface TableHeader {
  key: string
  label: string
  type?: 'text' | 'number' | 'badge' | 'link'
  sortable?: boolean
}

interface FilterOption {
  value: string
  label: string
}

interface Props {
  data: Record<string, unknown>[]
  headers: TableHeader[]
  title?: string
  searchable?: boolean
  sortable?: boolean
  filterable?: boolean
  paginated?: boolean
  pageSize?: number
  filterOptions?: FilterOption[]
  filterKey?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  searchable: true,
  sortable: true,
  filterable: false,
  paginated: true,
  pageSize: 10,
  filterOptions: () => [],
  filterKey: ''
})

// Reactive state
const searchTerm = ref('')
const selectedFilter = ref('')
const sortKey = ref('')
const sortDirection = ref<'asc' | 'desc'>('asc')
const currentPage = ref(1)

// Computed properties
const filteredData = computed(() => {
  let filtered = [...props.data]

  // Apply search filter
  if (searchTerm.value) {
    const search = searchTerm.value.toLowerCase()
    filtered = filtered.filter(row =>
      Object.values(row).some(value =>
        String(value).toLowerCase().includes(search)
      )
    )
  }

  // Apply column filter
  if (selectedFilter.value && props.filterKey) {
    filtered = filtered.filter(row => row[props.filterKey!] === selectedFilter.value)
  }

  // Apply sorting
  if (sortKey.value) {
    filtered.sort((a, b) => {
      const aVal = a[sortKey.value]
      const bVal = b[sortKey.value]
      
      let comparison = 0
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        comparison = aVal.localeCompare(bVal)
      } else if (typeof aVal === 'number' && typeof bVal === 'number') {
        comparison = aVal - bVal
      } else {
        // Convert to string for comparison
        const aStr = String(aVal || '')
        const bStr = String(bVal || '')
        comparison = aStr.localeCompare(bStr)
      }
      
      return sortDirection.value === 'desc' ? -comparison : comparison
    })
  }

  return filtered
})

const totalPages = computed(() => 
  props.paginated ? Math.ceil(filteredData.value.length / props.pageSize) : 1
)

const startIndex = computed(() => 
  props.paginated ? (currentPage.value - 1) * props.pageSize : 0
)

const endIndex = computed(() => 
  props.paginated ? startIndex.value + props.pageSize : filteredData.value.length
)

const paginatedData = computed(() => 
  props.paginated 
    ? filteredData.value.slice(startIndex.value, endIndex.value)
    : filteredData.value
)

// Methods
const sortBy = (key: string) => {
  if (!props.sortable) return
  
  if (sortKey.value === key) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDirection.value = 'asc'
  }
}

const getBadgeVariant = (value: string): 'default' | 'secondary' | 'success' | 'warning' | 'error' => {
  // Simple mapping for badge variants
  const variants: Record<string, 'default' | 'secondary' | 'success' | 'warning' | 'error'> = {
    'active': 'success',
    'inactive': 'secondary', 
    'pending': 'warning',
    'error': 'error',
    'success': 'success'
  }
  return variants[value.toLowerCase()] || 'secondary'
}

const formatNumber = (value: unknown) => {
  if (typeof value === 'number') {
    return value.toLocaleString()
  }
  return value
}

// Watch for filter changes to reset pagination
watch([searchTerm, selectedFilter], () => {
  currentPage.value = 1
})
</script>

<style scoped>
@reference "tailwindcss";
.data-table-container {
  width: 100%;
}

.table-wrapper {
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
}

.sort-indicators {
  opacity: 0.6;
  transition-property: opacity;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

.sort-indicators:hover {
  opacity: 1;
}

.pagination {
  user-select: none;
}
</style>
