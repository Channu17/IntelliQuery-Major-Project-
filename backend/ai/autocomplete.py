"""
Autocomplete and Query Suggestion Engine
Provides real-time query suggestions as users type, similar to Google search.
Uses Groq LLM for intelligent, context-aware suggestions.
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional
from functools import lru_cache
import json

from ai.llm.groq import get_groq_completion, get_groq_client
from datasources.store import get_datasource_by_id

logger = logging.getLogger(__name__)


class QueryAutocomplete:
    """
    Fast autocomplete engine for natural language queries.
    """
    
    def __init__(self):
        self.schema_cache = {}
        self.suggestion_cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def get_suggestions(
        self,
        partial_query: str,
        datasource_id: str,
        user_id: str,
        limit: int = 5
    ) -> List[str]:
        """
        Generate query suggestions based on partial input.
        
        Args:
            partial_query: User's partial input (e.g., "show me all")
            datasource_id: ID of selected datasource
            user_id: Current user ID
            limit: Maximum number of suggestions (default 5)
            
        Returns:
            List of suggested query completions
        """
        try:
            # Quick validation
            if not partial_query or len(partial_query.strip()) < 2:
                return self._get_starter_suggestions(datasource_id)
            
            # Check cache first
            cache_key = f"{datasource_id}:{partial_query.lower().strip()}"
            if cache_key in self.suggestion_cache:
                cached = self.suggestion_cache[cache_key]
                return cached[:limit]
            
            # Get datasource info
            datasource = get_datasource_by_id(datasource_id)
            if not datasource or str(datasource.get("user_id")) != user_id:
                return []
            
            # Get schema context (cached)
            schema_summary = await self._get_schema_summary(datasource)
            
            # Generate suggestions using Groq
            suggestions = await self._generate_suggestions(
                partial_query,
                schema_summary,
                datasource.get("type"),
                limit
            )
            
            # Cache results
            self.suggestion_cache[cache_key] = suggestions
            
            # Cleanup old cache entries (simple LRU)
            if len(self.suggestion_cache) > 1000:
                # Remove oldest 200 entries
                keys_to_remove = list(self.suggestion_cache.keys())[:200]
                for key in keys_to_remove:
                    del self.suggestion_cache[key]
            
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return self._get_fallback_suggestions(partial_query)
    
    async def _get_schema_summary(self, datasource: Dict[str, Any]) -> str:
        """Get compact schema summary for prompt (with caching)."""
        ds_id = str(datasource.get("_id", datasource.get("id")))
        
        if ds_id in self.schema_cache:
            return self.schema_cache[ds_id]
        
        ds_type = datasource.get("type", "")
        details = datasource.get("details", {})
        
        try:
            if ds_type in ["mysql", "psql", "sql"]:
                summary = await self._get_sql_schema_summary(datasource)
            elif ds_type in ["mongo", "mongodb"]:
                summary = await self._get_mongo_schema_summary(datasource)
            elif ds_type in ["pandas", "csv", "excel"]:
                summary = await self._get_pandas_schema_summary(datasource)
            else:
                summary = "Unknown datasource type"
            
            self.schema_cache[ds_id] = summary
            return summary
            
        except Exception as e:
            logger.error(f"Error getting schema summary: {e}")
            return "Schema unavailable"
    
    async def _get_sql_schema_summary(self, datasource: Dict[str, Any]) -> str:
        """Get compact SQL schema summary."""
        try:
            from ai.agents.sql_agent import SQLAgent
            agent = SQLAgent()
            tables_info = await agent.get_tables_info(datasource)
            
            # Create compact summary
            summary_parts = []
            for table in tables_info[:10]:  # Limit to 10 tables
                cols = [c["name"] for c in table.get("columns", [])[:10]]  # First 10 columns
                summary_parts.append(f"{table['name']}({', '.join(cols)})")
            
            return f"Tables: {'; '.join(summary_parts)}"
            
        except Exception as e:
            logger.error(f"SQL schema error: {e}")
            return "SQL database"
    
    async def _get_mongo_schema_summary(self, datasource: Dict[str, Any]) -> str:
        """Get compact MongoDB schema summary."""
        try:
            from ai.agents.mongo_agent import MongoAgent
            agent = MongoAgent()
            collections_info = await agent.get_collections_info(datasource)
            
            summary_parts = []
            for coll in collections_info[:10]:
                fields = coll.get("fields", [])[:10]
                summary_parts.append(f"{coll['name']}({', '.join(fields)})")
            
            return f"Collections: {'; '.join(summary_parts)}"
            
        except Exception as e:
            logger.error(f"Mongo schema error: {e}")
            return "MongoDB database"
    
    async def _get_pandas_schema_summary(self, datasource: Dict[str, Any]) -> str:
        """Get compact Pandas schema summary."""
        try:
            details = datasource.get("details", {})
            columns = details.get("columns", [])[:20]  # First 20 columns
            return f"Columns: {', '.join(columns)}"
            
        except Exception as e:
            logger.error(f"Pandas schema error: {e}")
            return "CSV/Excel file"
    
    async def _generate_suggestions(
        self,
        partial_query: str,
        schema_summary: str,
        datasource_type: str,
        limit: int
    ) -> List[str]:
        """Generate suggestions using Groq LLM."""
        
        # Optimized prompt for speed
        prompt = f"""Complete this database query with {limit} natural language suggestions.

Database: {datasource_type}
Schema: {schema_summary}
User typing: "{partial_query}"

Generate {limit} COMPLETE query suggestions that:
1. Start with or include the user's partial input
2. Are natural language questions (not SQL/code)
3. Are realistic questions someone would ask this database
4. Are diverse and cover different query types

Respond ONLY with a JSON array of strings, nothing else:
["suggestion 1", "suggestion 2", "suggestion 3"]

Examples:
- "show me all users"
- "what are the top 10 products by sales"
- "count how many orders were placed today"
- "find customers from California"

Your {limit} suggestions:"""

        try:
            # Use Groq with aggressive timeout for speed
            client = get_groq_client()
            if not client:
                return self._get_fallback_suggestions(partial_query)
            
            # Fast, low-temperature completion
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Fastest Groq model
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_completion_tokens=200,  # Keep it short
                top_p=0.9,
                stream=False
            )
            
            if completion.choices and len(completion.choices) > 0:
                response_text = completion.choices[0].message.content.strip()
                
                # Parse JSON array
                try:
                    # Extract JSON array
                    if "```" in response_text:
                        response_text = response_text.split("```")[1]
                        if response_text.startswith("json"):
                            response_text = response_text[4:]
                    
                    suggestions = json.loads(response_text.strip())
                    
                    if isinstance(suggestions, list):
                        # Clean and validate suggestions
                        clean_suggestions = []
                        for s in suggestions:
                            if isinstance(s, str) and len(s.strip()) > 0:
                                clean_suggestions.append(s.strip())
                        
                        return clean_suggestions[:limit]
                    
                except json.JSONDecodeError:
                    # Try line-by-line parsing
                    lines = [l.strip(' "[],-') for l in response_text.split('\n')]
                    suggestions = [l for l in lines if len(l) > 5 and not l.startswith('[')]
                    return suggestions[:limit]
            
            return self._get_fallback_suggestions(partial_query)
            
        except Exception as e:
            logger.error(f"Groq suggestion error: {e}")
            return self._get_fallback_suggestions(partial_query)
    
    def _get_starter_suggestions(self, datasource_id: str) -> List[str]:
        """Get starter suggestions when query is empty or too short."""
        return [
            "show me all records",
            "count total number of rows",
            "what are the top 10 items",
            "find records from last month",
            "summarize the data"
        ]
    
    def _get_fallback_suggestions(self, partial_query: str) -> List[str]:
        """Fallback suggestions when LLM fails."""
        partial = partial_query.lower().strip()
        
        fallback_map = {
            "show": [
                "show me all records",
                "show me the top 10 items",
                "show me records from today",
                "show me unique values",
                "show me summary statistics"
            ],
            "count": [
                "count total records",
                "count unique values",
                "count by category",
                "count records by date",
                "count non-null values"
            ],
            "find": [
                "find records where value equals",
                "find top items",
                "find records between dates",
                "find duplicates",
                "find null values"
            ],
            "get": [
                "get all records",
                "get top 10 results",
                "get records from specific date",
                "get summary",
                "get unique values"
            ],
            "what": [
                "what are the top items",
                "what is the total count",
                "what is the average value",
                "what is the maximum value",
                "what are the unique categories"
            ],
            "list": [
                "list all records",
                "list unique values",
                "list records sorted by",
                "list top 10 items",
                "list records from date range"
            ]
        }
        
        # Find matching suggestions
        for keyword, suggestions in fallback_map.items():
            if partial.startswith(keyword):
                return suggestions
        
        # Default fallbacks
        return [
            f"{partial} all records",
            f"{partial} top 10 items",
            f"{partial} records from today",
            f"{partial} by category",
            f"{partial} with filters"
        ]
    
    def clear_cache(self, datasource_id: Optional[str] = None):
        """Clear suggestion cache for a datasource or all."""
        if datasource_id:
            # Clear specific datasource
            keys_to_remove = [k for k in self.suggestion_cache.keys() if k.startswith(f"{datasource_id}:")]
            for key in keys_to_remove:
                del self.suggestion_cache[key]
            
            if datasource_id in self.schema_cache:
                del self.schema_cache[datasource_id]
        else:
            # Clear all
            self.suggestion_cache.clear()
            self.schema_cache.clear()


# Singleton instance
autocomplete = QueryAutocomplete()
