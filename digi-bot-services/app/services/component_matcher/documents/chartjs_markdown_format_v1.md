# Chart.js Markdown Format Documentation v1

## Overview

This documentation describes how to create Chart.js visualizations using direct markdown syntax. The system automatically renders interactive Chart.js charts when the format enhances learning and understanding.

## Core Philosophy

**Smart Visualization**: Only create charts when they genuinely improve comprehension or learning experience. Avoid unnecessary visualizations for simple text-based queries.

**Educational Focus**: Prioritize visualizations that help explain concepts, show relationships, or make complex data more understandable.

**Direct Format**: Use simple markdown syntax that automatically renders as interactive Chart.js charts.

## Chart.js Formats

### 1. Pie Charts
**Use for**: Percentages, proportions, market share, demographics

**Format**:
```
:::pie-chart
title: Social Media Market Share 2024
data: [
  {"label": "Instagram", "value": 45},
  {"label": "TikTok", "value": 30},
  {"label": "Facebook", "value": 15},
  {"label": "Twitter", "value": 10}
]
:::
```

### 2. Bar Charts
**Use for**: Category comparisons, sales by region, survey results

**Format**:
```
:::bar-chart
title: Regional Sales Performance Q4 2024
data: [
  {"label": "North America", "value": 125000},
  {"label": "Europe", "value": 98000},
  {"label": "Asia Pacific", "value": 156000},
  {"label": "Latin America", "value": 67000}
]
:::
```

### 3. Line Charts
**Use for**: Trends over time, growth rates, performance metrics

**Format**:
```
:::line-chart
title: AI Adoption Growth 2020-2024
data: [
  {"label": "2020", "value": 15},
  {"label": "2021", "value": 28},
  {"label": "2022", "value": 45},
  {"label": "2023", "value": 67},
  {"label": "2024", "value": 82}
]
:::
```

### 4. Doughnut Charts
**Use for**: Similar to pie but with center space for additional info

**Format**:
```
:::doughnut-chart
title: Budget Allocation 2024
data: [
  {"label": "Marketing", "value": 35},
  {"label": "Development", "value": 40},
  {"label": "Operations", "value": 15},
  {"label": "Research", "value": 10}
]
:::
```

### 5. Scatter Plots
**Use for**: Correlation analysis, x-y relationships

**Format**:
```
:::scatter-chart
title: Price vs Performance Analysis
data: [
  {"x": 100, "y": 85},
  {"x": 150, "y": 92},
  {"x": 200, "y": 88},
  {"x": 250, "y": 95}
]
:::
```

## Usage Guidelines for Chart.js

### Decision Matrix: Chart Types

| Data Type | Chart Type | Reasoning |
|-----------|------------|-----------|
| Percentages/Proportions | Pie/Doughnut Chart | Visual proportions are easier to understand |
| Category Comparisons | Bar Chart | Height comparison shows differences clearly |
| Time Series | Line Chart | Trends are immediately visible |
| Correlations | Scatter Plot | Relationship patterns emerge visually |

### Best Practices for Chart.js

1. **Educational Value First**: Only create visualizations that genuinely enhance learning
2. **Appropriate Chart Types**: Match chart type to data characteristics
3. **Clear Titles**: Use descriptive titles that explain what the chart shows
4. **Simple Data Format**: Use straightforward JSON arrays with label/value pairs
5. **Context Awareness**: Consider whether the user's question benefits from visualization
6. **Direct Format**: Use the `:::chart-type` syntax directly in responses

### Chart.js Example Scenarios

#### ✅ Good Use Cases for Chart.js

**Query**: "What's the market share of social media platforms?"
**Response**: Include pie chart with direct format:
```
:::pie-chart
title: Social Media Market Share 2024
data: [{"label": "Instagram", "value": 45}, {"label": "TikTok", "value": 30}]
:::
```
**Reasoning**: Proportional data is best understood visually

**Query**: "Compare sales performance across different regions"
**Response**: Include bar chart with direct format:
```
:::bar-chart
title: Regional Sales Comparison
data: [{"label": "North America", "value": 125000}, {"label": "Europe", "value": 98000}]
:::
```
**Reasoning**: Comparison data benefits from visual height differences

**Query**: "Show me the trend of AI adoption over the past 5 years"
**Response**: Include line chart with direct format:
```
:::line-chart
title: AI Adoption Trend 2020-2024
data: [{"label": "2020", "value": 15}, {"label": "2024", "value": 82}]
:::
```
**Reasoning**: Trends are immediately visible in line charts

#### ❌ Poor Use Cases for Chart.js

**Query**: "What is artificial intelligence?"
**Response**: Text explanation only
**Reasoning**: Conceptual explanation doesn't need visualization

**Query**: "List the benefits of exercise"
**Response**: Text list only
**Reasoning**: Simple enumeration doesn't benefit from charts

**Query**: "How do I cook pasta?"
**Response**: Text instructions only
**Reasoning**: Process instructions are better as text

## Technical Implementation for Chart.js

### Direct Format Flow

1. **Query Analysis**: Determine if Chart.js visualization would enhance understanding
2. **Data Extraction**: Identify numerical/categorical data in content
3. **Chart Type Selection**: Choose most appropriate Chart.js visualization
4. **Direct Format**: Use `:::chart-type` syntax directly in response
5. **Auto-Rendering**: Frontend automatically renders interactive Chart.js charts

### Chart.js Data Format Examples

**Pie Chart Data**:
```json
[
  {"label": "Instagram", "value": 45},
  {"label": "TikTok", "value": 30},
  {"label": "Facebook", "value": 15},
  {"label": "Twitter", "value": 10}
]
```

**Bar Chart Data**:
```json
[
  {"label": "Q1 2024", "value": 125000},
  {"label": "Q2 2024", "value": 145000},
  {"label": "Q3 2024", "value": 162000},
  {"label": "Q4 2024", "value": 178000}
]
```

**Scatter Plot Data**:
```json
[
  {"x": 10, "y": 20},
  {"x": 15, "y": 35},
  {"x": 20, "y": 45},
  {"x": 25, "y": 55}
]
```

## Integration with AI Models for Chart.js

### Reasoning Mode Considerations

When using reasoning models (o1-preview, o1-mini):
- Carefully analyze whether Chart.js visualization adds educational value
- Consider multiple chart types before selecting optimal one
- Evaluate if the user's learning objective benefits from visual representation
- Use direct `:::chart-type` format when charts enhance understanding
- Avoid over-visualization of simple concepts

### Direct Format Guidelines for AI

**When to Use Chart.js Format**:
- User asks about numerical data, comparisons, or trends
- Visualization would genuinely enhance understanding
- Data is suitable for Chart.js representation
- Educational value is clear

**How to Use**:
- Include the `:::chart-type` block directly in your response
- Choose appropriate Chart.js chart type for the data
- Use clear, descriptive titles
- Format data as simple JSON arrays

## Conclusion

The Chart.js markdown format system provides intelligent, context-aware data visualization that enhances learning and understanding. By using simple `:::chart-type` syntax directly in responses, it creates meaningful educational experiences while avoiding unnecessary complexity.

The key principle is **purposeful Chart.js visualization**: every chart should serve a clear educational or analytical purpose, making complex information more accessible and understandable for users.

### Quick Reference for Chart.js

**Available Chart.js Types**:
- `:::pie-chart` - For percentages and proportions
- `:::bar-chart` - For category comparisons  
- `:::line-chart` - For trends over time
- `:::doughnut-chart` - For proportions with center space
- `:::scatter-chart` - For correlations and x-y relationships

**Remember**: Only use Chart.js charts when they genuinely enhance understanding. Simple text explanations are often better than unnecessary visualizations.

