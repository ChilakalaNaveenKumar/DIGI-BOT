# Enhanced Component Capabilities for AI Analysis

This document describes the available enhanced components that can be dynamically generated based on content analysis.

## Available Components

### 1. PieChart Component
**Purpose**: Display percentage-based data as circular segments  
**Best for**: Market share analysis, demographics, survey results, categorical percentages  
**Data Structure**:
```typescript
interface PieChartData {
  label: string
  value: number
  percentage?: number
}
```

**Markdown Syntax**: `:::pie-chart`

**Example Usage**:
```markdown
:::pie-chart
title: Social Media Usage Distribution
data:
  - { label: "Instagram", value: 45, percentage: 45 }
  - { label: "Facebook", value: 30, percentage: 30 }
  - { label: "Twitter", value: 25, percentage: 25 }
:::
```

**When to Generate**:
- Content mentions percentages or proportions
- Data represents parts of a whole
- Categories with percentage distribution
- Survey results with options

---

### 2. BarChart Component
**Purpose**: Compare quantities across different categories  
**Best for**: Performance metrics, comparisons, rankings, time-based comparisons  
**Data Structure**:
```typescript
interface BarChartData {
  label: string
  value: number
  color?: string
}
```

**Markdown Syntax**: `:::bar-chart`

**Example Usage**:
```markdown
:::bar-chart
title: Quarterly Sales Performance
data:
  - { label: "Q1 2024", value: 100000 }
  - { label: "Q2 2024", value: 150000 }
  - { label: "Q3 2024", value: 200000 }
  - { label: "Q4 2024", value: 175000 }
horizontal: false
showValues: true
:::
```

**When to Generate**:
- Comparative data between categories
- Performance metrics over time
- Rankings or leaderboards
- Quantity comparisons

---

### 3. LineChart Component
**Purpose**: Show trends and changes over time  
**Best for**: Time series data, growth trends, performance tracking, progression analysis  
**Data Structure**:
```typescript
interface LineChartSeries {
  name: string
  data: { x: string | number, y: number }[]
  color?: string
}
```

**Markdown Syntax**: `:::line-chart`

**Example Usage**:
```markdown
:::line-chart
title: Website Traffic Growth
data:
  - name: "Visitors"
    data:
      - { x: "Jan", y: 1200 }
      - { x: "Feb", y: 1500 }
      - { x: "Mar", y: 1800 }
      - { x: "Apr", y: 2100 }
smooth: true
showPoints: true
:::
```

**When to Generate**:
- Time-based data progression
- Trend analysis
- Growth or decline patterns
- Multiple data series comparisons

---

### 4. DataTable Component
**Purpose**: Present structured data with sorting, filtering, and pagination  
**Best for**: Detailed datasets, comparison tables, lists with multiple attributes  
**Data Structure**:
```typescript
interface TableHeader {
  key: string
  label: string
  type?: 'text' | 'number' | 'badge' | 'link'
}
```

**Markdown Syntax**: `:::data-table`

**Example Usage**:
```markdown
:::data-table
title: Product Comparison
headers:
  - { key: "name", label: "Product Name", type: "text" }
  - { key: "price", label: "Price", type: "number" }
  - { key: "rating", label: "Rating", type: "number" }
  - { key: "status", label: "Status", type: "badge" }
data:
  - { name: "iPhone 15", price: 999, rating: 4.5, status: "active" }
  - { name: "Samsung S24", price: 899, rating: 4.3, status: "active" }
  - { name: "Pixel 8", price: 699, rating: 4.2, status: "active" }
searchable: true
sortable: true
:::
```

**When to Generate**:
- Structured data with multiple columns
- Comparison information
- Lists with detailed attributes
- Data requiring search/filter capabilities

---

## AI Decision Framework

### Content Analysis Triggers

**Generate PieChart when content contains**:
- Percentage distributions (e.g., "30% of users prefer...", "Market share: 45% Apple, 35% Samsung")
- Categorical breakdowns with proportions
- Survey results with multiple choice answers
- Demographic data with percentages

**Generate BarChart when content contains**:
- Comparative quantities (e.g., "Sales in Q1: $100K, Q2: $150K")
- Rankings or leaderboards
- Performance metrics across categories
- Before/after comparisons

**Generate LineChart when content contains**:
- Time-series data (e.g., "Growth from January to December")
- Trend descriptions (e.g., "increasing over time", "steady decline")
- Progressive data points
- Multiple trend comparisons

**Generate DataTable when content contains**:
- Structured lists with multiple attributes
- Comparison data with various properties
- Detailed specifications or features
- Data requiring organization and search

### Decision Logic

1. **Analyze content for data patterns**
2. **Identify data relationships** (categorical, temporal, comparative)
3. **Determine best visualization method**
4. **Extract and structure data**
5. **Generate appropriate component markdown**

### Response Format

```json
{
  "decision": "GENERATE_NOW" | "NO_COMPONENT",
  "component_type": "pie-chart" | "bar-chart" | "line-chart" | "data-table",
  "confidence": 0.8,
  "reasoning": "Content contains percentage distribution data suitable for pie chart visualization",
  "markdown": ":::pie-chart\ntitle: Market Share Analysis\ndata:\n  - { label: \"Company A\", value: 45, percentage: 45 }\n:::"
}
```

## Integration Notes

- Components are auto-imported with `Enhanced` prefix
- All components support dark/light theme switching
- Responsive design for mobile compatibility
- ApexCharts library provides interactive features
- Components integrate with existing Tailwind CSS styling
