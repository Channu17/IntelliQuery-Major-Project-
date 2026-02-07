# Visualization API Guide

## Overview
The visualization system uses Groq LLM to intelligently analyze query results and suggest appropriate charts, then generates Plotly visualizations that can be rendered in the frontend.

## API Endpoints

### 1. Get Visualization Suggestions
**POST** `/ai/visualize/suggest`

Analyzes your query results and suggests the best chart types using AI.

**Request:**
```json
{
  "results": [
    {"date": "2024-01-01", "product": "Laptop", "sales": 1200, "region": "North"},
    {"date": "2024-01-02", "product": "Mouse", "sales": 150, "region": "South"}
  ],
  "query_context": "Show me sales by product over time"
}
```

**Response:**
```json
{
  "success": true,
  "recommendations": [
    {
      "type": "line",
      "reason": "Time series data with dates - line chart shows trends",
      "x_axis": "date",
      "y_axis": "sales",
      "group_by": "product",
      "priority": 1
    },
    {
      "type": "bar",
      "reason": "Compare sales across products",
      "x_axis": "product",
      "y_axis": "sales",
      "group_by": "region",
      "priority": 2
    }
  ],
  "data_insights": "Dataset shows sales trends across multiple products and regions",
  "data_summary": {
    "rows": 2,
    "columns": 4,
    "numeric_cols": ["sales"],
    "categorical_cols": ["product", "region"],
    "datetime_cols": ["date"]
  }
}
```

### 2. Generate Visualization
**POST** `/ai/visualize/generate`

Creates a specific chart based on user selection or AI suggestion.

**Request:**
```json
{
  "results": [...],
  "chart_type": "bar",
  "x_axis": "product",
  "y_axis": "sales",
  "group_by": "region",
  "customization": {
    "title": "Sales by Product and Region",
    "theme": "plotly_dark",
    "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1"],
    "height": 600,
    "width": 900,
    "show_legend": true,
    "hovermode": "closest"
  }
}
```

**Response:**
```json
{
  "success": true,
  "chart_type": "bar",
  "chart_data": {
    "data": [...],
    "layout": {...}
  },
  "config": {
    "displayModeBar": true,
    "responsive": true
  }
}
```

## Supported Chart Types

| Chart Type | Best For | Required Fields |
|------------|----------|----------------|
| `line` | Time series, trends | x_axis, y_axis |
| `bar` | Categorical comparison | x_axis, y_axis |
| `horizontal_bar` | Long category names | x_axis, y_axis |
| `pie` | Distribution, proportions | x_axis (categories), y_axis (values) |
| `scatter` | Correlation between 2 variables | x_axis, y_axis |
| `histogram` | Distribution of single variable | x_axis |
| `box` | Statistical distribution | y_axis |
| `area` | Cumulative trends | x_axis, y_axis |
| `stacked_bar` | Part-to-whole comparison | x_axis, y_axis, group_by |
| `grouped_bar` | Multi-category comparison | x_axis, y_axis, group_by |
| `heatmap` | Correlation matrix | (auto-detects numeric columns) |
| `funnel` | Conversion/pipeline | x_axis, y_axis |
| `waterfall` | Incremental changes | x_axis, y_axis |

## Customization Options

### Colors
```json
{
  "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1"]
}
```
Or use Plotly palettes:
- `px.colors.qualitative.Plotly` (default)
- `px.colors.qualitative.Bold`
- `px.colors.qualitative.Vivid`
- Custom hex codes

### Themes
```json
{
  "theme": "plotly_dark"
}
```
Available: `plotly`, `plotly_white`, `plotly_dark`, `ggplot2`, `seaborn`, `simple_white`, `none`

### Layout
```json
{
  "height": 600,
  "width": 900,
  "show_legend": true,
  "hovermode": "closest"
}
```

## Frontend Integration

### Using Plotly.js
```html
<div id="chart"></div>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<script>
  const response = await fetch('/ai/visualize/generate', {...});
  const data = await response.json();
  Plotly.newPlot('chart', data.chart_data.data, data.chart_data.layout, data.config);
</script>
```

### Using React Plotly
```jsx
import Plot from 'react-plotly.js';

function Chart({ chartData }) {
  return (
    <Plot
      data={chartData.chart_data.data}
      layout={chartData.chart_data.layout}
      config={chartData.config}
    />
  );
}
```

## Workflow Example

1. **Execute Query:**
```bash
POST /ai/query
{
  "query": "show me monthly sales by product",
  "datasource_id": "ds_123"
}
```

2. **Get Suggestions:**
```bash
POST /ai/visualize/suggest
{
  "results": [...results from step 1...],
  "query_context": "show me monthly sales by product"
}
```

3. **User Selects Chart Type** (e.g., from recommendations)

4. **Generate Chart:**
```bash
POST /ai/visualize/generate
{
  "results": [...results from step 1...],
  "chart_type": "line",
  "x_axis": "month",
  "y_axis": "sales",
  "group_by": "product",
  "customization": {
    "title": "Monthly Sales Trend",
    "theme": "plotly_dark",
    "colors": ["#FF6B6B", "#4ECDC4"]
  }
}
```

5. **Render in Frontend** using Plotly

## Error Handling

All endpoints return proper error messages:

```json
{
  "success": false,
  "error": "No data provided for visualization",
  "chart_type": "bar"
}
```

Common errors:
- Empty results array
- Invalid chart type
- Missing required axis for chart type
- Invalid column names
- Data structure incompatible with chart type

## Testing

Run the test script:
```bash
cd backend
python test_visualization.py
```

This tests:
- ✅ Visualization suggestions with Groq LLM
- ✅ Chart generation for all types
- ✅ Customization options
- ✅ Error handling
