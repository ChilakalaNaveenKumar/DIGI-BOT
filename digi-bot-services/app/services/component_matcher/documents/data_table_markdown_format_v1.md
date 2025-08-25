# Data Table Markdown Format Documentation v3 (Generic)

## Overview

This documentation defines how to create **structured data tables** in markdown for interactive rendering.
Use data tables when **multi-attribute precision** is required, or when comparisons are too detailed for charts.

## Core Principles

* **Purposeful Tabulation**: Only use tables when they improve comprehension.
* **Multi-Attribute First**: Choose tables when multiple metrics, KPIs, or attributes need side-by-side comparison.
* **Exactness Over Visualization**: Prefer tables when raw numbers/details matter more than trends.
* **Generic Placeholders**: Always use `<column_X>`, `<value_X>`, `<position>` if real data is missing.
* **No Fabrication**: Never invent rows, metrics, or numbers. Use placeholders when actual values are absent.

---

## Data Table Format

```
:::data-table
title: <Descriptive Title>
data: [
  {"<column_1>": "<value_1>", "<column_2>": "<value_2>"},
  {"<column_1>": "<value_3>", "<column_2>": "<value_4>"}
]
:::
```

---

## Decision Rules

| Data Type / Pattern                               | Use Table? | Reason                                      |
| ------------------------------------------------- | ---------- | ------------------------------------------- |
| Multi-metric entities (products, teams, depts.)   | ✅ Yes      | Multiple attributes → structured comparison |
| Financial / budget data                           | ✅ Yes      | Precision across multiple numbers           |
| Performance KPIs (load, conversion, bounce, etc.) | ✅ Yes      | Several metrics side-by-side                |
| Survey / poll results                             | ✅ Yes      | Rows = questions, columns = answer %        |
| A/B test results                                  | ✅ Yes      | Side-by-side statistical outcomes           |
| Simple proportions only                           | ❌ No       | Use Pie/Doughnut chart                      |
| Trends over time                                  | ❌ No       | Use Line chart                              |
| Single-metric categorical comparison              | ❌ No       | Use Bar chart                               |

---

## Best Practices

1. **Clear Headers**: Column names should be explicit (`<column_1>`, `<column_2>`).
2. **Consistent Values**: Keep units consistent (%, \$, counts).
3. **Readable Size**: 2–8 columns max.
4. **Use Placeholders**: If missing, output `<column_X>`, `<value_X>`.
5. **Fallback**: If no table pattern fits, return `NO_MATCH`.

---

## Example Blocks (Generic)

**Query**: "Compare product performance"

```
:::data-table
title: Product Performance
data: [
  {"<column_1>": "<value_1>", "<column_2>": "<value_2>", "<column_3>": "<value_3>"},
  {"<column_1>": "<value_4>", "<column_2>": "<value_5>", "<column_3>": "<value_6>"}
]
:::
```

**Query**: "Show A/B test results"

```
:::data-table
title: A/B Test Results
data: [
  {"<variant>": "<value_1>", "<metric_1>": "<value_2>", "<metric_2>": "<value_3>"},
  {"<variant>": "<value_4>", "<metric_1>": "<value_5>", "<metric_2>": "<value_6>"}
]
:::
```

**Query**: "Provide survey breakdown"

```
:::data-table
title: Survey Results
data: [
  {"<question>": "<value_1>", "<answer_1>": "<value_2>", "<answer_2>": "<value_3>"},
  {"<question>": "<value_4>", "<answer_1>": "<value_5>", "<answer_2>": "<value_6>"}
]
:::
```

---

## Quick Reference

* **Use**: Multi-attribute structured data (finance, KPIs, surveys, A/B tests).
* **Avoid**: Pure proportions (Pie/Doughnut), time series (Line), single-metric comparisons (Bar).
* **Always**: Placeholders if missing data, never fabricate.
* **Output**: Exact block or `NO_MATCH`.

---

## Key Principle

👉 Use **data tables** when detail, structure, and multiple attributes matter.
👉 Use **charts** for visual clarity (trends, comparisons, proportions).
👉 Use **text** for explanations and concepts.