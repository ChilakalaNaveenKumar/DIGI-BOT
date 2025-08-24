# Data Table Markdown Format Documentation v1

## Overview

This documentation describes how to create structured data tables using direct markdown syntax. The system automatically renders interactive data tables when tabular format enhances data comprehension and analysis.

## Core Philosophy

**Smart Tabulation**: Only create data tables when they genuinely improve data comprehension or provide detailed structured information. Use tables for complex multi-attribute data that benefits from tabular presentation.

**Data Focus**: Prioritize tables that help organize, compare, or present detailed information that would be difficult to understand in other formats.

**Direct Format**: Use simple markdown syntax that automatically renders as interactive data tables.

## Data Table Format

### Data Tables
**Use for**: Complex structured data, statistical measures, detailed comparisons, multi-attribute datasets, exact values, financial data, performance metrics

**Format**:
```
:::data-table
title: Product Performance Statistics
data: [
  {
    "Product": "Widget A",
    "Sales": "$125,000",
    "Units": "1,250",
    "Growth": "+15%",
    "Rating": "4.8/5"
  },
  {
    "Product": "Widget B",
    "Sales": "$98,000", 
    "Units": "980",
    "Growth": "+8%",
    "Rating": "4.6/5"
  },
  {
    "Product": "Widget C",
    "Sales": "$156,000",
    "Units": "1,560",
    "Growth": "+22%",
    "Rating": "4.9/5"
  }
]
:::
```

## Usage Guidelines for Data Tables

### Decision Matrix: When to Use Data Tables

| Data Type | Use Data Table | Reasoning |
|-----------|----------------|-----------|
| Multi-attribute Data | Yes | Detailed comparison requires exact values |
| Statistical Measures | Yes | Precision and calculations are important |
| Financial Reports | Yes | Exact numbers and multiple metrics needed |
| Performance Metrics | Yes | Multiple KPIs need structured presentation |
| Simple Lists | No | No tabular structure needed |
| Single Metric Comparisons | No | Charts are more visual |

### Best Practices for Data Tables

1. **Detailed Information**: Use tables when users need exact values and detailed comparisons
2. **Multiple Attributes**: Perfect for data with multiple columns/attributes
3. **Clear Headers**: Use descriptive column names that explain the data
4. **Consistent Formatting**: Maintain consistent data formatting within columns
5. **Appropriate Size**: Don't create overly large tables that become hard to read
6. **Direct Format**: Use the `:::data-table` syntax directly in responses

### Data Table Example Scenarios

#### ✅ Good Use Cases for Data Tables

**Query**: "Show me detailed performance metrics for our top products"
**Response**: Include data table with direct format:
```
:::data-table
title: Product Performance Metrics Q4 2024
data: [
  {
    "Product": "Premium Widget",
    "Revenue": "$245,000",
    "Units Sold": "2,450",
    "Profit Margin": "32%",
    "Customer Rating": "4.8/5",
    "Return Rate": "2.1%"
  },
  {
    "Product": "Standard Widget",
    "Revenue": "$189,000",
    "Units Sold": "3,780",
    "Profit Margin": "28%",
    "Customer Rating": "4.6/5",
    "Return Rate": "3.2%"
  }
]
:::
```
**Reasoning**: Multiple metrics require structured tabular presentation

**Query**: "Compare the financial performance of different departments"
**Response**: Include data table with direct format:
```
:::data-table
title: Department Financial Performance 2024
data: [
  {
    "Department": "Sales",
    "Budget": "$2.5M",
    "Actual Spend": "$2.3M",
    "Revenue Generated": "$12.8M",
    "ROI": "456%",
    "Headcount": "45"
  },
  {
    "Department": "Marketing",
    "Budget": "$1.8M",
    "Actual Spend": "$1.7M",
    "Revenue Generated": "$8.2M",
    "ROI": "382%",
    "Headcount": "28"
  }
]
:::
```
**Reasoning**: Financial data with multiple attributes needs tabular structure

**Query**: "Show me the detailed statistics for our A/B test results"
**Response**: Include data table with direct format:
```
:::data-table
title: A/B Test Results - Homepage Redesign
data: [
  {
    "Variant": "Control (Original)",
    "Visitors": "10,250",
    "Conversions": "1,435",
    "Conversion Rate": "14.0%",
    "Avg. Session Time": "3:24",
    "Bounce Rate": "42.3%"
  },
  {
    "Variant": "Test (New Design)",
    "Visitors": "10,180",
    "Conversions": "1,672",
    "Conversion Rate": "16.4%",
    "Avg. Session Time": "4:12",
    "Bounce Rate": "38.1%"
  }
]
:::
```
**Reasoning**: Statistical comparison requires exact values in structured format

#### ❌ Poor Use Cases for Data Tables

**Query**: "What's the market share of social media platforms?"
**Response**: Use pie chart instead
**Reasoning**: Proportional data is better visualized than tabulated

**Query**: "Show me the sales trend over the last 6 months"
**Response**: Use line chart instead
**Reasoning**: Trends are better shown visually than in tables

**Query**: "What are the benefits of exercise?"
**Response**: Text list only
**Reasoning**: Simple enumeration doesn't need tabular structure

## Technical Implementation for Data Tables

### Direct Format Flow

1. **Query Analysis**: Determine if structured tabular data would enhance understanding
2. **Data Structure**: Identify multi-attribute data that benefits from tabular presentation
3. **Column Selection**: Choose appropriate columns/attributes for comparison
4. **Direct Format**: Use `:::data-table` syntax directly in response
5. **Auto-Rendering**: Frontend automatically renders interactive data tables

### Data Table Format Examples

**Financial Data Table**:
```json
[
  {
    "Company": "TechCorp",
    "Revenue": "$2.5B",
    "Profit": "$450M",
    "Employees": "12,500",
    "Market Cap": "$15.2B"
  },
  {
    "Company": "InnovateCo",
    "Revenue": "$1.8B",
    "Profit": "$320M",
    "Employees": "8,900",
    "Market Cap": "$11.7B"
  }
]
```

**Performance Metrics Table**:
```json
[
  {
    "Metric": "Page Load Time",
    "Current": "2.3s",
    "Target": "2.0s",
    "Status": "Needs Improvement",
    "Priority": "High"
  },
  {
    "Metric": "Conversion Rate",
    "Current": "14.2%",
    "Target": "15.0%",
    "Status": "On Track",
    "Priority": "Medium"
  }
]
```

**Survey Results Table**:
```json
[
  {
    "Question": "Overall Satisfaction",
    "Very Satisfied": "45%",
    "Satisfied": "32%",
    "Neutral": "15%",
    "Dissatisfied": "8%"
  },
  {
    "Question": "Product Quality",
    "Very Satisfied": "52%",
    "Satisfied": "28%",
    "Neutral": "12%",
    "Dissatisfied": "8%"
  }
]
```

## Integration with AI Models for Data Tables

### Reasoning Mode Considerations

When using reasoning models (o1-preview, o1-mini):
- Carefully analyze whether tabular presentation adds value over other formats
- Consider if the data has multiple attributes that benefit from structured comparison
- Evaluate if users need exact values rather than visual trends
- Use direct `:::data-table` format when structured data enhances understanding
- Avoid creating tables for simple data that could be better visualized

### Direct Format Guidelines for AI

**When to Use Data Table Format**:
- User asks about detailed comparisons with multiple attributes
- Data contains exact values that need precision
- Information is structured and benefits from tabular presentation
- Multiple metrics or KPIs need to be compared
- Financial, statistical, or performance data is involved

**How to Use**:
- Include the `:::data-table` block directly in your response
- Use clear, descriptive column headers
- Ensure consistent data formatting within columns
- Format data as JSON array of objects

## Conclusion

The data table markdown format system provides structured, detailed data presentation that enhances information comprehension and analysis. By using simple `:::data-table` syntax directly in responses, it creates organized data experiences for complex information.

The key principle is **purposeful tabulation**: every data table should serve a clear informational purpose, making complex structured data more accessible and comparable for users.

### Quick Reference for Data Tables

**Available Data Table Type**:
- `:::data-table` - For complex structured data, multi-attribute comparisons, exact values, financial data, performance metrics

**Remember**: Only use data tables when structured tabular presentation genuinely enhances data comprehension. Simple comparisons might be better as charts, and basic information might be better as text.

