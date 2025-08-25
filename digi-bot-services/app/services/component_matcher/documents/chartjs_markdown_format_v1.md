# Chart.js Markdown Format Documentation v3 (Generic)

## Overview

This documentation defines how to create **Chart.js visualizations** using direct markdown syntax.
Charts should only be generated when they **clarify, explain, or enhance** understanding of data.

## Core Principles

* **Purposeful Visualization**: Only use charts when they add clarity.
* **Pattern Recognition**: Match query intent (proportions, categories, time trends, x-y pairs).
* **Generic Placeholders**: Always use `<label>`, `<value>`, `<x>`, `<y>`, `<position>` if real data is not provided.
* **No Fabrication**: Never invent sample data or categories. Use placeholders when missing.

---

## Chart.js Formats

### Pie Chart

**Use for**: Proportions, percentages, demographics.

```
:::pie-chart
title: <Descriptive Title>
data: [
  {"label": "<label_1>", "value": <value_1>},
  {"label": "<label_2>", "value": <value_2>}
]
:::
```

### Bar Chart

**Use for**: Comparing categories, teams, or regions.

```
:::bar-chart
title: <Descriptive Title>
data: [
  {"label": "<label_1>", "value": <value_1>},
  {"label": "<label_2>", "value": <value_2>}
]
:::
```

### Line Chart

**Use for**: Trends over time (months, years, etc.).

```
:::line-chart
title: <Descriptive Title>
data: [
  {"label": "<time_1>", "value": <value_1>},
  {"label": "<time_2>", "value": <value_2>}
]
:::
```

### Doughnut Chart

**Use for**: Proportions with central space (e.g., allocation).

```
:::doughnut-chart
title: <Descriptive Title>
data: [
  {"label": "<label_1>", "value": <value_1>},
  {"label": "<label_2>", "value": <value_2>}
]
:::
```

### Scatter Plot

**Use for**: Correlations, x–y relationships.

```
:::scatter-chart
title: <Descriptive Title>
data: [
  {"x": <x_value_1>, "y": <y_value_1>},
  {"x": <x_value_2>, "y": <y_value_2>}
]
:::
```

---

## Decision Rules (Pattern → Chart Type)

| Query Pattern                    | Chart Type   | Reason                          |
| -------------------------------- | ------------ | ------------------------------- |
| Percentages (sum ≈ 100%)         | Pie/Doughnut | Clear proportions               |
| Single metric across categories  | Bar          | Compare category heights        |
| Time series (dates/months/years) | Line         | Show growth or decline          |
| Paired numeric variables (x,y)   | Scatter      | Show correlation                |
| Multi-attribute per entity       | Data Table   | Better for structure than chart |
| No clear fit                     | NO\_MATCH    | Avoid forced charting           |

---

## Best Practices

1. **Clear Titles**: Always describe what the chart represents.
2. **Consistent Units**: Ensure same unit type within a chart.
3. **Use Placeholders**: If no real data is provided, output `<label>`, `<value>`.
4. **Few Categories**: Keep ≤ 8 for readability.
5. **Return NO\_MATCH** if no chart type applies.

---

## Example Blocks (Generic)

**Query**: "Compare departments"

```
:::bar-chart
title: Department Comparison
data: [
  {"label": "<label_1>", "value": <value_1>},
  {"label": "<label_2>", "value": <value_2>}
]
:::
```

**Query**: "Show revenue growth over months"

```
:::line-chart
title: Revenue Growth
data: [
  {"label": "<time_1>", "value": <value_1>},
  {"label": "<time_2>", "value": <value_2>}
]
:::
```

**Query**: "Give me allocation breakdown"

```
:::doughnut-chart
title: Allocation Breakdown
data: [
  {"label": "<label_1>", "value": <value_1>},
  {"label": "<label_2>", "value": <value_2>}
]
:::
```

---

## Quick Reference

* **Pie/Doughnut** → Proportions (\~100%).
* **Bar** → Category comparisons.
* **Line** → Time trends.
* **Scatter** → Correlations.
* **Data Table** → Multi-attribute structured data.
* **Text/List** → Pure explanations or qualitative info.

---

## Key Principle

👉 Use **charts for visual clarity** (proportions, trends, comparisons, relationships).
👉 Use **tables for multi-attribute detail**.
👉 Use **text for concepts/explanations**.