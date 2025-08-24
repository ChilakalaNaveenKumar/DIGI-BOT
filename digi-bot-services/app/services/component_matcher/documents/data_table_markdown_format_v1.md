# Data Table Markdown Format Documentation v2

## Overview

This documentation defines how to create **structured data tables** in markdown for interactive rendering.
Use data tables when **multi-attribute precision** is required, or when comparisons are too detailed for charts alone.

## Core Principles

* **Purposeful Tabulation**: Create tables only when they improve comprehension.
* **Multi-Attribute First**: Use when there are multiple metrics, KPIs, or attributes for each entity.
* **Exactness Over Visualization**: Favor tables when numbers and details matter more than trends or proportions.
* **Direct Format**: Always output in `:::data-table ... :::` blocks for automatic rendering.

---

## Data Table Format

```
:::data-table
title: <Descriptive Title>
data: [
  {
    "Column A": "Value A1",
    "Column B": "Value B1",
    "Column C": "Value C1"
  },
  {
    "Column A": "Value A2",
    "Column B": "Value B2",
    "Column C": "Value C2"
  }
]
:::
```

---

## Decision Rules

| Data Type / Pattern                                             | Use Table?                | Reasoning                                          |
| --------------------------------------------------------------- | ------------------------- | -------------------------------------------------- |
| **Multi-metric entities** (products, teams, departments)        | ✅ Yes                     | Multiple attributes need structured comparison     |
| **Financial / budget data**                                     | ✅ Yes                     | Requires precision and multiple numbers            |
| **Performance KPIs** (load time, conversion, bounce rate, etc.) | ✅ Yes                     | Several metrics side-by-side                       |
| **Survey / poll results**                                       | ✅ Yes                     | Rows for questions, columns for answer percentages |
| **A/B test results**                                            | ✅ Yes                     | Side-by-side statistical outcomes                  |
| **Simple proportions** (just percentages)                       | ❌ No → Pie/Doughnut chart | Visual proportions easier                          |
| **Trends over time**                                            | ❌ No → Line chart         | Trend visualization better                         |
| **Category comparison (single metric)**                         | ❌ No → Bar chart          | Easier to compare with bars                        |

---

## Best Practices

1. **Clear Headers**: Column names should be explicit (Revenue, ROI, Conversions).
2. **Consistent Values**: Format currency, percentages, units consistently.
3. **Readable Size**: Keep 2–8 columns, avoid overly wide tables.
4. **Match Context**: Only include metrics relevant to the user’s query.
5. **Fallback**: If attributes are missing, but a tabular structure is obvious, use placeholders like `<value_X>`.

---

## Example Scenarios

### ✅ Good Use Cases

**1. Product Performance**

```
:::data-table
title: Product Performance Statistics
data: [
  {"Product": "Widget A", "Revenue": "$125,000", "Units": "1,250", "Growth": "+15%", "Rating": "4.8/5"},
  {"Product": "Widget B", "Revenue": "$98,000", "Units": "980", "Growth": "+8%", "Rating": "4.6/5"},
  {"Product": "Widget C", "Revenue": "$156,000", "Units": "1,560", "Growth": "+22%", "Rating": "4.9/5"}
]
:::
```

**2. Department Financials**

```
:::data-table
title: Department Financial Performance 2024
data: [
  {"Department": "Sales", "Budget": "$2.5M", "Actual Spend": "$2.3M", "Revenue": "$12.8M", "ROI": "456%", "Headcount": "45"},
  {"Department": "Marketing", "Budget": "$1.8M", "Actual Spend": "$1.7M", "Revenue": "$8.2M", "ROI": "382%", "Headcount": "28"}
]
:::
```

**3. A/B Test Results**

```
:::data-table
title: Homepage Redesign - A/B Test
data: [
  {"Variant": "Control", "Visitors": "10,250", "Conversions": "1,435", "Rate": "14.0%", "Bounce": "42.3%"},
  {"Variant": "New Design", "Visitors": "10,180", "Conversions": "1,672", "Rate": "16.4%", "Bounce": "38.1%"}
]
:::
```

**4. HR / Salary Comparison**

```
:::data-table
title: Employee Salary Overview
data: [
  {"Name": "John", "Role": "Manager", "Salary": "$80,000"},
  {"Name": "Sarah", "Role": "Developer", "Salary": "$70,000"},
  {"Name": "Mike", "Role": "Designer", "Salary": "$65,000"}
]
:::
```

**5. Survey Results**

```
:::data-table
title: Customer Satisfaction Survey
data: [
  {"Question": "Overall Satisfaction", "Very Satisfied": "45%", "Satisfied": "32%", "Neutral": "15%", "Dissatisfied": "8%"},
  {"Question": "Product Quality", "Very Satisfied": "52%", "Satisfied": "28%", "Neutral": "12%", "Dissatisfied": "8%"}
]
:::
```

---

### ❌ Poor Use Cases

* **Query**: “What’s the market share of platforms?”
  → Use **Pie Chart**
* **Query**: “Show sales over 6 months.”
  → Use **Line Chart**
* **Query**: “List the benefits of exercise.”
  → Use **Bulleted text**

---

## Technical Workflow

1. **Analyze Query**: Look for multiple attributes per entity.
2. **Extract Entities**: Products, teams, departments, variants.
3. **Identify Metrics**: Revenue, Growth, ROI, KPIs, survey percentages.
4. **Build Table**: Map entities → rows, metrics → columns.
5. **Format Output**: Use `:::data-table ... :::`.

---

## Quick Reference

**Available Table Type**:

* `:::data-table` — For structured, multi-attribute data

**Best Fits**:

* Financial data
* Multi-metric performance
* Survey or poll breakdowns
* A/B tests
* HR / salaries / inventory

**Avoid**:

* Pure proportions (Pie/Doughnut)
* Time series trends (Line)
* Single-metric comparisons (Bar)

---

## Key Principle

👉 **Only use a data table when precision, structure, and multi-attribute detail matter.**
Charts are for trends and visuals. Tables are for structured comparisons.
