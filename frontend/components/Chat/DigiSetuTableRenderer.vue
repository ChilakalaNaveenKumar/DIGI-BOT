<template>
  <div class="ds-table-renderer">
    <div class="ds-table-wrapper">
      <table class="ds-table">
        <thead v-if="headers.length">
          <tr>
            <th v-for="(header, index) in headers" :key="index">
              {{ header }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, rowIndex) in rows" :key="rowIndex">
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
import { computed } from 'vue'

const props = defineProps({
  content: {
    type: String,
    required: true
  },
  isStreaming: {
    type: Boolean,
    default: false
  }
})

// Parse markdown table
const parsedTable = computed(() => {
  const lines = props.content.split('\n').filter(line => line.trim())
  
  if (lines.length < 2) return { headers: [], rows: [] }
  
  // First line is headers
  const headerLine = lines[0]
  const headers = headerLine.split('|').map(h => h.trim()).filter(h => h)
  
  // Skip separator line (---)
  const dataLines = lines.slice(2)
  
  // Parse data rows
  const rows = dataLines.map(line => {
    return line.split('|').map(cell => cell.trim()).filter(cell => cell)
  })
  
  return { headers, rows }
})

const headers = computed(() => parsedTable.value.headers)
const rows = computed(() => parsedTable.value.rows)
</script>

<style scoped>
.ds-table-renderer {
  margin: 1rem 0;
  overflow-x: auto;
}

.ds-table-wrapper {
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.ds-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.ds-table th {
  background: #f9fafb;
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  border-bottom: 1px solid #e5e7eb;
}

.ds-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #f3f4f6;
}

.ds-table tr:last-child td {
  border-bottom: none;
}

.ds-table tr:hover {
  background: #f9fafb;
}
</style>
