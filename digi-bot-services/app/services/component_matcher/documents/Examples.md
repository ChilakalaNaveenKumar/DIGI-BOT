# Component Matcher Examples

This document contains generic examples for component matching with placeholder values only.

## Generic Chart Examples

### Bar Chart Example
```
:::bar-chart
title: <Descriptive Title>
data: [
  {"label": "<label_1>", "value": <value_1>},
  {"label": "<label_2>", "value": <value_2>},
  {"label": "<label_3>", "value": <value_3>}
]
:::
```

### Line Chart Example
```
:::line-chart
title: <Descriptive Title>
data: [
  {"label": "<time_1>", "value": <value_1>},
  {"label": "<time_2>", "value": <value_2>},
  {"label": "<time_3>", "value": <value_3>}
]
:::
```

### Pie Chart Example
```
:::pie-chart
title: <Descriptive Title>
data: [
  {"label": "<category_1>", "value": <percentage_1>},
  {"label": "<category_2>", "value": <percentage_2>},
  {"label": "<category_3>", "value": <percentage_3>}
]
:::
```

### Doughnut Chart Example
```
:::doughnut-chart
title: <Descriptive Title>
data: [
  {"label": "<segment_1>", "value": <percentage_1>},
  {"label": "<segment_2>", "value": <percentage_2>},
  {"label": "<segment_3>", "value": <percentage_3>}
]
:::
```

### Scatter Plot Example
```
:::scatter-plot
title: <Descriptive Title>
data: [
  {"x": <x_value_1>, "y": <y_value_1>, "label": "<point_1>"},
  {"x": <x_value_2>, "y": <y_value_2>, "label": "<point_2>"},
  {"x": <x_value_3>, "y": <y_value_3>, "label": "<point_3>"}
]
:::
```

### Area Chart Example
```
:::area-chart
title: <Descriptive Title>
data: [
  {"label": "<period_1>", "value": <value_1>},
  {"label": "<period_2>", "value": <value_2>},
  {"label": "<period_3>", "value": <value_3>}
]
:::
```

## Generic Data Table Examples

### Simple Data Table Example
```
:::data-table
title: <Descriptive Title>
data: [
  {"<column_1>": "<value_1>", "<column_2>": "<value_2>", "<column_3>": "<value_3>"},
  {"<column_1>": "<value_4>", "<column_2>": "<value_5>", "<column_3>": "<value_6>"},
  {"<column_1>": "<value_7>", "<column_2>": "<value_8>", "<column_3>": "<value_9>"}
]
:::
```

### Multi-Attribute Data Table Example
```
:::data-table
title: <Descriptive Title>
data: [
  {"<attribute_1>": "<value_1>", "<attribute_2>": <numeric_value_1>, "<attribute_3>": "<status_1>"},
  {"<attribute_1>": "<value_2>", "<attribute_2>": <numeric_value_2>, "<attribute_3>": "<status_2>"},
  {"<attribute_1>": "<value_3>", "<attribute_2>": <numeric_value_3>, "<attribute_3>": "<status_3>"}
]
:::
```

## NO_MATCH Examples

The following types of queries should return NO_MATCH:

### Conceptual Questions
- "Explain quantum computing principles"
- "What is machine learning?"
- "How does blockchain work?"
- "Define artificial intelligence"

### Ambiguous Data Requests
- "Show me some data" (no specific data provided)
- "Create a visualization" (no data or context)
- "Make a chart" (no data specified)

### Non-Data Content
- "Write a story about data"
- "Create a poem about statistics"
- "Generate marketing copy"
- "Write documentation"

### Incomplete Specifications
- "Data distribution" (without actual data)
- "Performance metrics" (without specific metrics)
- "Comparison analysis" (without items to compare)

## Position Anchors

If the caller provides an anchor string and character offset, compute the exact character index from the document context. Otherwise, always emit `<position>` as a placeholder. Never guess numeric positions.

## Validation Checklist

Use this checklist to determine the appropriate component:

- **Multi-attribute data with rows/columns** → `:::data-table`
- **Single metric across categories** → `:::bar-chart`
- **Time series or sequential data** → `:::line-chart`
- **Proportions that sum to ~100%** → `:::pie-chart` or `:::doughnut-chart`
- **Two-dimensional relationships** → `:::scatter-plot`
- **Cumulative or filled area data** → `:::area-chart`
- **Conceptual questions or no data** → `NO_MATCH`

**Data Integrity Rules:**
- Never fabricate numbers, labels, or statistics
- Use placeholders when values are missing
- Only use data explicitly present in the query or documentation
- Position should be `<position>` unless exact offset is known
