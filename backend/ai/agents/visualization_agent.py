import logging
import base64
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple
import json

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from ai.llm.groq import get_groq_completion

logger = logging.getLogger(__name__)


class VisualizationAgent:
    """
    Visualization Agent that analyzes query results and generates appropriate graphs.
    Uses Groq LLM to intelligently select graph types based on data structure.
    """
    
    SUPPORTED_CHART_TYPES = [
        "line",
        "bar", 
        "horizontal_bar",
        "pie",
        "scatter",
        "histogram",
        "box",
        "area",
        "stacked_bar",
        "grouped_bar",
        "heatmap",
        "funnel",
        "waterfall"
    ]
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def _prepare_dataframe(self, results: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert query results to pandas DataFrame."""
        try:
            if not results:
                raise ValueError("No data provided for visualization")
            
            df = pd.DataFrame(results)
            
            # Convert string dates to datetime if possible
            for col in df.columns:
                if df[col].dtype == 'object':
                    try:
                        # Try parsing as datetime
                        df[col] = pd.to_datetime(df[col])
                    except (ValueError, TypeError):
                        pass
            
            return df
        except Exception as e:
            logger.error(f"Error preparing dataframe: {e}")
            raise ValueError(f"Failed to prepare data: {str(e)}")
    
    def _analyze_data_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze DataFrame structure for graph suggestions."""
        analysis = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": {},
            "numeric_columns": [],
            "categorical_columns": [],
            "datetime_columns": [],
            "has_nulls": df.isnull().any().any()
        }
        
        for col in df.columns:
            dtype = str(df[col].dtype)
            unique_count = df[col].nunique()
            null_count = df[col].isnull().sum()
            
            col_info = {
                "dtype": dtype,
                "unique_count": unique_count,
                "null_count": null_count,
                "sample_values": df[col].dropna().head(3).tolist()
            }
            
            analysis["columns"][col] = col_info
            
            # Categorize columns
            if pd.api.types.is_numeric_dtype(df[col]):
                analysis["numeric_columns"].append(col)
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                analysis["datetime_columns"].append(col)
            else:
                # Categorical if unique count is less than 50% of total or < 20
                if unique_count < len(df) * 0.5 or unique_count < 20:
                    analysis["categorical_columns"].append(col)
        
        return analysis
    
    async def suggest_visualizations(
        self, 
        results: List[Dict[str, Any]],
        query_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Use Groq LLM to analyze data and suggest appropriate visualizations.
        """
        try:
            df = self._prepare_dataframe(results)
            analysis = self._analyze_data_structure(df)
            
            # Build prompt for LLM
            prompt = f"""You are a data visualization expert. Analyze this dataset and suggest the most appropriate chart types.

Dataset Information:
- Rows: {analysis['row_count']}
- Columns: {analysis['column_count']}
- Numeric columns: {', '.join(analysis['numeric_columns']) if analysis['numeric_columns'] else 'None'}
- Categorical columns: {', '.join(analysis['categorical_columns']) if analysis['categorical_columns'] else 'None'}
- Datetime columns: {', '.join(analysis['datetime_columns']) if analysis['datetime_columns'] else 'None'}

Column Details:
{json.dumps(analysis['columns'], indent=2, default=str)[:1000]}

User Query Context: {query_context or 'Not provided'}

Available Chart Types:
{', '.join(self.SUPPORTED_CHART_TYPES)}

Respond ONLY with a JSON object in this exact format:
{{
  "recommended_charts": [
    {{
      "type": "chart_type",
      "reason": "why this chart is suitable",
      "x_axis": "column_name",
      "y_axis": "column_name",
      "group_by": "column_name (optional)",
      "priority": 1-5
    }}
  ],
  "data_insights": "brief insights about the data"
}}

Provide 3-5 chart recommendations ranked by priority (1=highest)."""

            # Get LLM response
            llm_response = await get_groq_completion(prompt)
            
            # Parse JSON response
            try:
                # Extract JSON from response
                json_match = llm_response.strip()
                if "```json" in json_match:
                    json_match = json_match.split("```json")[1].split("```")[0].strip()
                elif "```" in json_match:
                    json_match = json_match.split("```")[1].split("```")[0].strip()
                
                suggestions = json.loads(json_match)
                
                # Validate and filter recommendations
                valid_recommendations = []
                for rec in suggestions.get("recommended_charts", []):
                    if rec.get("type") in self.SUPPORTED_CHART_TYPES:
                        valid_recommendations.append(rec)
                
                return {
                    "success": True,
                    "recommendations": valid_recommendations,
                    "data_insights": suggestions.get("data_insights", ""),
                    "data_summary": {
                        "rows": analysis["row_count"],
                        "columns": analysis["column_count"],
                        "numeric_cols": analysis["numeric_columns"],
                        "categorical_cols": analysis["categorical_columns"],
                        "datetime_cols": analysis["datetime_columns"]
                    }
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {llm_response[:200]}")
                # Fallback to rule-based suggestions
                return self._fallback_suggestions(analysis)
                
        except Exception as e:
            logger.error(f"Error suggesting visualizations: {e}")
            return {
                "success": False,
                "error": str(e),
                "recommendations": []
            }
    
    def _fallback_suggestions(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based fallback for chart suggestions."""
        recommendations = []
        
        numeric_cols = analysis["numeric_columns"]
        categorical_cols = analysis["categorical_columns"]
        datetime_cols = analysis["datetime_columns"]
        
        # Time series: line chart
        if datetime_cols and numeric_cols:
            recommendations.append({
                "type": "line",
                "reason": "Time series data detected",
                "x_axis": datetime_cols[0],
                "y_axis": numeric_cols[0],
                "priority": 1
            })
        
        # Categorical + Numeric: bar chart
        if categorical_cols and numeric_cols:
            recommendations.append({
                "type": "bar",
                "reason": "Categorical data with numeric values",
                "x_axis": categorical_cols[0],
                "y_axis": numeric_cols[0],
                "priority": 2
            })
        
        # Categorical distribution: pie chart
        if categorical_cols and len(categorical_cols) > 0:
            recommendations.append({
                "type": "pie",
                "reason": "Show distribution of categories",
                "x_axis": categorical_cols[0],
                "priority": 3
            })
        
        # Multiple numeric: scatter
        if len(numeric_cols) >= 2:
            recommendations.append({
                "type": "scatter",
                "reason": "Compare two numeric variables",
                "x_axis": numeric_cols[0],
                "y_axis": numeric_cols[1],
                "priority": 4
            })
        
        return {
            "success": True,
            "recommendations": recommendations,
            "data_insights": "Auto-generated suggestions based on data structure",
            "data_summary": {
                "rows": analysis["row_count"],
                "columns": analysis["column_count"],
                "numeric_cols": numeric_cols,
                "categorical_cols": categorical_cols,
                "datetime_cols": datetime_cols
            }
        }
    
    async def generate_visualization(
        self,
        results: List[Dict[str, Any]],
        chart_type: str,
        x_axis: Optional[str] = None,
        y_axis: Optional[str] = None,
        group_by: Optional[str] = None,
        customization: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a specific visualization based on parameters.
        Returns Plotly JSON for frontend rendering.
        """
        try:
            df = self._prepare_dataframe(results)
            
            # Default customization
            custom = customization or {}
            colors = custom.get("colors", px.colors.qualitative.Plotly)
            title = custom.get("title", f"{chart_type.replace('_', ' ').title()} Chart")
            theme = custom.get("theme", "plotly")
            height = custom.get("height", 500)
            width = custom.get("width", 800)
            
            # Generate chart based on type
            fig = None
            
            if chart_type == "line":
                fig = self._create_line_chart(df, x_axis, y_axis, group_by, colors, title)
            
            elif chart_type == "bar":
                fig = self._create_bar_chart(df, x_axis, y_axis, group_by, colors, title)
            
            elif chart_type == "horizontal_bar":
                fig = self._create_horizontal_bar_chart(df, x_axis, y_axis, group_by, colors, title)
            
            elif chart_type == "pie":
                fig = self._create_pie_chart(df, x_axis, y_axis, colors, title)
            
            elif chart_type == "scatter":
                fig = self._create_scatter_chart(df, x_axis, y_axis, group_by, colors, title)
            
            elif chart_type == "histogram":
                fig = self._create_histogram(df, x_axis, colors, title)
            
            elif chart_type == "box":
                fig = self._create_box_plot(df, x_axis, y_axis, group_by, colors, title)
            
            elif chart_type == "area":
                fig = self._create_area_chart(df, x_axis, y_axis, group_by, colors, title)
            
            elif chart_type == "stacked_bar":
                fig = self._create_stacked_bar(df, x_axis, y_axis, group_by, colors, title)
            
            elif chart_type == "grouped_bar":
                fig = self._create_grouped_bar(df, x_axis, y_axis, group_by, colors, title)
            
            elif chart_type == "heatmap":
                fig = self._create_heatmap(df, colors, title)
            
            elif chart_type == "funnel":
                fig = self._create_funnel_chart(df, x_axis, y_axis, colors, title)
            
            elif chart_type == "waterfall":
                fig = self._create_waterfall_chart(df, x_axis, y_axis, title)
            
            else:
                raise ValueError(f"Unsupported chart type: {chart_type}")
            
            # Apply common styling
            fig.update_layout(
                template=theme,
                height=height,
                width=width,
                showlegend=custom.get("show_legend", True),
                hovermode=custom.get("hovermode", "closest")
            )
            
            # Convert to JSON
            chart_json = fig.to_json()
            
            return {
                "success": True,
                "chart_type": chart_type,
                "chart_data": json.loads(chart_json),
                "config": {
                    "displayModeBar": True,
                    "responsive": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating visualization: {e}")
            return {
                "success": False,
                "error": str(e),
                "chart_type": chart_type
            }
    
    # Chart generation methods
    
    def _create_line_chart(self, df, x, y, group_by, colors, title):
        """Create line chart."""
        if not x or not y:
            # Auto-detect
            x = x or df.select_dtypes(include=['datetime64', 'object']).columns[0]
            y = y or df.select_dtypes(include=['number']).columns[0]
        
        if group_by and group_by in df.columns:
            fig = px.line(df, x=x, y=y, color=group_by, title=title, color_discrete_sequence=colors)
        else:
            fig = px.line(df, x=x, y=y, title=title, color_discrete_sequence=colors)
        
        return fig
    
    def _create_bar_chart(self, df, x, y, group_by, colors, title):
        """Create vertical bar chart."""
        if not x or not y:
            cat_cols = df.select_dtypes(include=['object', 'category']).columns
            num_cols = df.select_dtypes(include=['number']).columns
            x = x or (cat_cols[0] if len(cat_cols) > 0 else df.columns[0])
            y = y or (num_cols[0] if len(num_cols) > 0 else df.columns[1] if len(df.columns) > 1 else df.columns[0])
        
        if group_by and group_by in df.columns:
            fig = px.bar(df, x=x, y=y, color=group_by, title=title, color_discrete_sequence=colors)
        else:
            fig = px.bar(df, x=x, y=y, title=title, color_discrete_sequence=colors)
        
        return fig
    
    def _create_horizontal_bar_chart(self, df, x, y, group_by, colors, title):
        """Create horizontal bar chart."""
        if not x or not y:
            cat_cols = df.select_dtypes(include=['object', 'category']).columns
            num_cols = df.select_dtypes(include=['number']).columns
            x = x or (num_cols[0] if len(num_cols) > 0 else df.columns[0])
            y = y or (cat_cols[0] if len(cat_cols) > 0 else df.columns[1] if len(df.columns) > 1 else df.columns[0])
        
        if group_by and group_by in df.columns:
            fig = px.bar(df, x=x, y=y, color=group_by, orientation='h', title=title, color_discrete_sequence=colors)
        else:
            fig = px.bar(df, x=x, y=y, orientation='h', title=title, color_discrete_sequence=colors)
        
        return fig
    
    def _create_pie_chart(self, df, x, y, colors, title):
        """Create pie chart."""
        if not x:
            x = df.select_dtypes(include=['object', 'category']).columns[0]
        
        # Aggregate data if y is provided, otherwise count
        if y and y in df.columns:
            pie_data = df.groupby(x)[y].sum().reset_index()
            fig = px.pie(pie_data, names=x, values=y, title=title, color_discrete_sequence=colors)
        else:
            pie_data = df[x].value_counts().reset_index()
            pie_data.columns = [x, 'count']
            fig = px.pie(pie_data, names=x, values='count', title=title, color_discrete_sequence=colors)
        
        return fig
    
    def _create_scatter_chart(self, df, x, y, group_by, colors, title):
        """Create scatter plot."""
        num_cols = df.select_dtypes(include=['number']).columns
        if not x or not y:
            x = x or (num_cols[0] if len(num_cols) > 0 else df.columns[0])
            y = y or (num_cols[1] if len(num_cols) > 1 else num_cols[0] if len(num_cols) > 0 else df.columns[1])
        
        if group_by and group_by in df.columns:
            fig = px.scatter(df, x=x, y=y, color=group_by, title=title, color_discrete_sequence=colors)
        else:
            fig = px.scatter(df, x=x, y=y, title=title, color_discrete_sequence=colors)
        
        return fig
    
    def _create_histogram(self, df, x, colors, title):
        """Create histogram."""
        if not x:
            x = df.select_dtypes(include=['number']).columns[0]
        
        fig = px.histogram(df, x=x, title=title, color_discrete_sequence=colors)
        return fig
    
    def _create_box_plot(self, df, x, y, group_by, colors, title):
        """Create box plot."""
        num_cols = df.select_dtypes(include=['number']).columns
        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        
        if not y:
            y = num_cols[0] if len(num_cols) > 0 else df.columns[0]
        
        if x and x in df.columns:
            fig = px.box(df, x=x, y=y, title=title, color_discrete_sequence=colors)
        else:
            fig = px.box(df, y=y, title=title, color_discrete_sequence=colors)
        
        return fig
    
    def _create_area_chart(self, df, x, y, group_by, colors, title):
        """Create area chart."""
        if not x or not y:
            x = x or df.columns[0]
            y = y or df.select_dtypes(include=['number']).columns[0]
        
        if group_by and group_by in df.columns:
            fig = px.area(df, x=x, y=y, color=group_by, title=title, color_discrete_sequence=colors)
        else:
            fig = px.area(df, x=x, y=y, title=title, color_discrete_sequence=colors)
        
        return fig
    
    def _create_stacked_bar(self, df, x, y, group_by, colors, title):
        """Create stacked bar chart."""
        if not x or not y or not group_by:
            raise ValueError("Stacked bar requires x, y, and group_by parameters")
        
        fig = px.bar(df, x=x, y=y, color=group_by, title=title, 
                     color_discrete_sequence=colors, barmode='stack')
        return fig
    
    def _create_grouped_bar(self, df, x, y, group_by, colors, title):
        """Create grouped bar chart."""
        if not x or not y or not group_by:
            raise ValueError("Grouped bar requires x, y, and group_by parameters")
        
        fig = px.bar(df, x=x, y=y, color=group_by, title=title,
                     color_discrete_sequence=colors, barmode='group')
        return fig
    
    def _create_heatmap(self, df, colors, title):
        """Create heatmap from correlation matrix or pivot table."""
        # Use only numeric columns
        numeric_df = df.select_dtypes(include=['number'])
        
        if len(numeric_df.columns) < 2:
            raise ValueError("Heatmap requires at least 2 numeric columns")
        
        # Create correlation matrix
        corr_matrix = numeric_df.corr()
        
        fig = px.imshow(corr_matrix, 
                       text_auto=True,
                       title=title,
                       color_continuous_scale=colors if isinstance(colors, str) else 'RdBu_r',
                       aspect='auto')
        return fig
    
    def _create_funnel_chart(self, df, x, y, colors, title):
        """Create funnel chart."""
        if not x or not y:
            cat_cols = df.select_dtypes(include=['object', 'category']).columns
            num_cols = df.select_dtypes(include=['number']).columns
            x = x or (cat_cols[0] if len(cat_cols) > 0 else df.columns[0])
            y = y or (num_cols[0] if len(num_cols) > 0 else df.columns[1])
        
        fig = px.funnel(df, x=y, y=x, title=title, color_discrete_sequence=colors)
        return fig
    
    def _create_waterfall_chart(self, df, x, y, title):
        """Create waterfall chart."""
        if not x or not y:
            x = x or df.columns[0]
            y = y or df.select_dtypes(include=['number']).columns[0]
        
        fig = go.Figure(go.Waterfall(
            name="",
            orientation="v",
            x=df[x].tolist(),
            y=df[y].tolist(),
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))
        
        fig.update_layout(title=title)
        return fig


# Singleton instance
visualization_agent = VisualizationAgent()
