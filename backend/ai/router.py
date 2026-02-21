from typing import Dict, Any
import logging
from fastapi import APIRouter, HTTPException, Depends, status

from auth.dependencies import require_user
from ai.schemas import (
    QueryRequest, 
    QueryResponse,
    VisualizationSuggestRequest,
    VisualizationSuggestResponse,
    VisualizationGenerateRequest,
    VisualizationGenerateResponse,
    AutocompleteRequest,
    AutocompleteResponse
)
from ai.ai_router import ai_router
from ai.agents.visualization_agent import visualization_agent
from ai.autocomplete import autocomplete

router = APIRouter(prefix="/ai", tags=["ai"])
logger = logging.getLogger(__name__)


@router.post("/query", response_model=QueryResponse)
async def execute_query(
    request: QueryRequest,
    user: dict = Depends(require_user)
) -> QueryResponse:
    """
    Execute a natural language query against a datasource.
    
    The AI router will:
    1. Determine the datasource type (SQL, MongoDB, Pandas)
    2. Route to the appropriate agent
    3. Generate the query using Groq LLM
    4. Validate the query is read-only
    5. Execute and return results
    """
    response = await ai_router.route_query(
        natural_query=request.query,
        datasource_id=request.datasource_id,
        user_id=str(user["id"])
    )
    
    return response


@router.get("/schema/{datasource_id}")
async def get_datasource_schema(
    datasource_id: str,
    user: dict = Depends(require_user)
) -> Dict[str, Any]:
    """
    Get schema information for a datasource.
    
    Returns:
    - For SQL: List of tables with columns
    - For MongoDB: List of collections with fields
    - For Pandas: DataFrame columns and stats
    """
    schema_info = await ai_router.get_schema_info(
        datasource_id=datasource_id,
        user_id=str(user["id"])
    )
    
    if "error" in schema_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=schema_info["error"]
        )
    
    return schema_info


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Check health of AI services (Groq).
    """
    from ai.llm.groq import get_groq_client, GROQ_MODEL
    
    groq_available = get_groq_client() is not None
    
    return {
        "groq": {
            "available": groq_available,
            "model": GROQ_MODEL
        },
        "status": "healthy" if groq_available else "degraded"
    }


@router.post("/visualize/suggest", response_model=VisualizationSuggestResponse)
async def suggest_visualizations(
    request: VisualizationSuggestRequest,
    user: dict = Depends(require_user)
) -> VisualizationSuggestResponse:
    """
    Analyze query results and suggest appropriate visualizations using Groq LLM.
    
    This endpoint:
    1. Analyzes the data structure (columns, types, distributions)
    2. Uses Groq LLM to intelligently suggest chart types
    3. Returns ranked recommendations with reasons
    
    Returns:
    - List of recommended chart types with configuration
    - Data insights and summary
    """
    try:
        suggestions = await visualization_agent.suggest_visualizations(
            results=request.results,
            query_context=request.query_context
        )
        
        return VisualizationSuggestResponse(**suggestions)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate visualization suggestions: {str(e)}"
        )


@router.post("/visualize/generate", response_model=VisualizationGenerateResponse)
async def generate_visualization(
    request: VisualizationGenerateRequest,
    user: dict = Depends(require_user)
) -> VisualizationGenerateResponse:
    """
    Generate a specific visualization chart based on user selection.
    
    Parameters:
    - results: Query results to visualize
    - chart_type: Type of chart (line, bar, pie, scatter, etc.)
    - x_axis: Column name for X axis (optional, auto-detected)
    - y_axis: Column name for Y axis (optional, auto-detected)
    - group_by: Column for grouping/coloring (optional)
    - customization: Dict with colors, theme, height, width, etc.
    
    Customization options:
    - colors: List of color codes or Plotly color palette
    - title: Chart title
    - theme: plotly, plotly_white, plotly_dark, ggplot2, seaborn, simple_white
    - height: Chart height in pixels (default 500)
    - width: Chart width in pixels (default 800)
    - show_legend: Boolean (default True)
    - hovermode: closest, x, y, x unified, y unified
    
    Returns Plotly JSON that can be rendered using Plotly.js or plotly-react
    """
    try:
        chart = await visualization_agent.generate_visualization(
            results=request.results,
            chart_type=request.chart_type,
            x_axis=request.x_axis,
            y_axis=request.y_axis,
            group_by=request.group_by,
            customization=request.customization
        )
        
        return VisualizationGenerateResponse(**chart)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate visualization: {str(e)}"
        )


@router.post("/autocomplete", response_model=AutocompleteResponse)
async def query_autocomplete(
    request: AutocompleteRequest,
    user: dict = Depends(require_user)
) -> AutocompleteResponse:
    """
    Get real-time query suggestions as user types (Google-style autocomplete).
    
    Features:
    - Fast, sub-second response using Groq LLM
    - Context-aware suggestions based on datasource schema
    - Intelligent caching for performance
    - Fallback suggestions if LLM is unavailable
    
    Parameters:
    - partial_query: User's current input (e.g., "show me all")
    - datasource_id: Selected datasource ID
    - limit: Max suggestions to return (default 5, max 10)
    
    Returns:
    - List of natural language query suggestions
    - Optimized for real-time typing experience
    
    Usage:
    - Call on every keystroke (debounced on frontend)
    - Minimum 2 characters required
    - Results cached for 5 minutes per datasource
    
    Example:
    Input: "show me"
    Output: [
        "show me all records",
        "show me top 10 items",
        "show me records from today",
        "show me unique values",
        "show me summary statistics"
    ]
    """
    try:
        # Validate limit
        limit = min(request.limit or 5, 10)  # Max 10 suggestions
        
        # Get suggestions
        suggestions = await autocomplete.get_suggestions(
            partial_query=request.partial_query,
            datasource_id=request.datasource_id,
            user_id=str(user["id"]),
            limit=limit
        )
        
        return AutocompleteResponse(
            success=True,
            suggestions=suggestions,
            partial_query=request.partial_query
        )
        
    except Exception as e:
        logger.error(f"Autocomplete error: {e}")
        # Return fallback on error
        return AutocompleteResponse(
            success=False,
            suggestions=[],
            partial_query=request.partial_query,
            error=str(e)
        )


@router.delete("/autocomplete/cache/{datasource_id}")
async def clear_autocomplete_cache(
    datasource_id: str,
    user: dict = Depends(require_user)
) -> Dict[str, Any]:
    """
    Clear autocomplete cache for a specific datasource.
    
    Use this when:
    - Datasource schema has changed
    - You want fresh suggestions
    - Testing autocomplete behavior
    """
    try:
        autocomplete.clear_cache(datasource_id)
        return {
            "success": True,
            "message": f"Cache cleared for datasource {datasource_id}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to clear cache: {str(e)}"
        )
