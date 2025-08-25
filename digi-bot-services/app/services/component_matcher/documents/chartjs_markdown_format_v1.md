# Chart.js Markdown Format Documentation v2

## Overview

This documentation explains how to create **Chart.js visualizations** using direct markdown syntax.
Charts should only be generated when they **clarify, explain, or enhance** understanding of data.

## Core Principles

* **Purposeful Visualization**: Only use charts when they add real value.
* **Pattern Recognition**: Match queries to chart types by data shape, not keywords.
* **Educational Focus**: Prioritize visuals that make comparisons, proportions, or trends easier to grasp.
* **Direct Format**: Always output using `:::chart-type ... :::` blocks for automatic rendering.
* **Postiion**: Exact position to insert the charts after which character  without disturbing the text and flow of concept
* **action**: insert / update -> for this document its only insert

---

## Chart.js Formats

### Pie Chart

**Use for**: Proportions, market share, percentages, demographics.

```
:::pie-chart
title: Market Share 2024
position: <Exact position to insert the charts after which character without disturbing the text and flow of concept>
action: insert
data: [
  {"label": "Instagram", "value": 45},
  {"label": "TikTok", "value": 30},
  {"label": "Facebook", "value": 15},
  {"label": "Twitter", "value": 10}
]
:::
```

### Bar Chart

**Use for**: Comparing categories, regions, teams, or inventory.

```
:::bar-chart
title: Regional Sales Q4
position: 20
action: insert
data: [
  {"label": "North America", "value": 125000},
  {"label": "Europe", "value": 98000},
  {"label": "Asia Pacific", "value": 156000},
  {"label": "Latin America", "value": 67000}
]
:::
```

### Line Chart

**Use for**: Trends over time, growth, seasonality.

```
:::line-chart
title: AI Adoption 2020-2024
position: 40
action: insert
data: [
  {"label": "2020", "value": 15},
  {"label": "2021", "value": 28},
  {"label": "2022", "value": 45},
  {"label": "2023", "value": 67},
  {"label": "2024", "value": 82}
]
:::
```

### Doughnut Chart

**Use for**: Similar to pie but with a central space (budget, allocation).

```
:::doughnut-chart
title: Budget Allocation 2024
position: 50
action: insert
data: [
  {"label": "Marketing", "value": 35},
  {"label": "Development", "value": 40},
  {"label": "Operations", "value": 15},
  {"label": "Research", "value": 10}
]
:::
```

### Scatter Plot

**Use for**: Correlations, x-y relationships.

```
:::scatter-chart
title: Price vs Performance
position: 100
action: insert
data: [
  {"x": 100, "y": 85},
  {"x": 150, "y": 92},
  {"x": 200, "y": 88},
  {"x": 250, "y": 95}
]
:::
```

---

## Decision Rules (Pattern → Chart Type)

| Query Pattern                                 | Chart Type             | Reason                         |
| --------------------------------------------- | ---------------------- | ------------------------------ |
| Percentages sum ≈ 100%                        | Pie/Doughnut           | Shows proportions clearly      |
| Categorical values (teams, regions, products) | Bar                    | Easy comparison of heights     |
| Time series (dates, months, years)            | Line                   | Shows growth/decline over time |
| Paired variables (x,y)                        | Scatter                | Reveals relationships          |
| Multi-attribute per entity                    | Data Table (not chart) | Structure > visualization      |

---

## Best Practices

1. **Clear Title**: Always describe what the chart shows.
2. **Consistent Values**: Use same unit (%, \$, count).
3. **Few Categories**: Max 5–8 for readability.
4. **Fallback**: If no clear chart type applies, return `"NO_MATCH"`.
5. **Semantic Mapping**: Treat *regions, teams, categories* all as bar-chart candidates.

---

## Example Scenarios

### ✅ Good Matches

**Query**: "Compare team productivity: Frontend 45 tasks, Backend 38, QA 29"

```
:::bar-chart
title: Team Productivity
position: 1120
action: insert
data: [
  {"label": "Frontend", "value": 45},
  {"label": "Backend", "value": 38},
  {"label": "QA", "value": 29}
]
:::
```

**Query**: "Show me last 6 months of revenue growth"

```
:::line-chart
title: Revenue Growth 2024
position: 25
action: insert
data: [
  {"label": "Jan", "value": 12000},
  {"label": "Feb", "value": 15000},
  {"label": "Mar", "value": 18000},
  {"label": "Apr", "value": 20000},
  {"label": "May", "value": 22500},
  {"label": "Jun", "value": 25000}
]
:::
```

**Query**: "What’s the salary distribution?"

```
:::doughnut-chart
title: Salary Distribution
position: 200
action: insert
data: [
  {"label": "Managers", "value": 40},
  {"label": "Developers", "value": 35},
  {"label": "Designers", "value": 15},
  {"label": "QA", "value": 10}
]
:::
```

### ❌ Poor Matches

* **Query**: "Explain quantum computing" → Use text only.
* **Query**: "Benefits of daily exercise" → Use bullet list.
* **Query**: "Departmental financials with budget, spend, ROI" → Use `:::data-table`, not chart.

---

## Quick Reference

**Available Chart Types**:

* `:::pie-chart` — Proportions
* `:::bar-chart` — Category comparisons
* `:::line-chart` — Trends over time
* `:::doughnut-chart` — Proportions + center info
* `:::scatter-chart` — Correlations

**When NOT to use**:

* Multi-metric structured data → Data Table
* Pure explanations → Text
* Step-by-step processes → List

---

## Key Principle

👉 Use charts for **visual clarity** (proportions, trends, comparisons, relationships).
👉 Use tables for **structured detail**.
👉 Use text for **concepts**.