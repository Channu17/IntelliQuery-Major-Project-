import os
import logging
from typing import Optional
from groq import Groq, APIError

logger = logging.getLogger(__name__)

# Primary Groq LLM model
GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


def get_groq_client() -> Optional[Groq]:
    """Get Groq client with API key from environment."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.error("GROQ_API_KEY not set in environment")
        return None
    return Groq(api_key=api_key)


async def generate_with_groq(
    prompt: str,
    query_type: str,
    schema_context: str
) -> Optional[str]:
    """
    Generate query using Groq LLM.
    
    Args:
        prompt: The user's natural language query
        query_type: One of 'sql', 'mongo', 'pandas'
        schema_context: Schema information for the datasource
        
    Returns:
        Generated query string or None if failed
    """
    client = get_groq_client()
    if not client:
        return None
    
    system_prompts = {
        "sql": """You are an expert SQL query generator. Given a natural language question and database schema, 
generate ONLY a valid SELECT SQL query. Do not include any explanations, just the raw SQL query.
IMPORTANT: Only generate READ-ONLY queries (SELECT). Never generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, or any other modifying queries.
Return ONLY the SQL query, nothing else.""",
        
        "mongo": """You are an expert MongoDB query generator. Given a natural language question and collection schema,
generate a valid MongoDB query in JSON format.

IMPORTANT:
- Only generate READ-ONLY queries (find, aggregate, count, distinct)
- Never generate insert, update, delete, drop, or any modifying operations
- Return pure JSON only, no explanation

SUPPORTED FORMATS:
For aggregate: {"aggregate": [{"$group": {...}}, {"$sort": {...}}]}
For find: {"find": {...}, "projection": {...}, "sort": {...}, "limit": 10}
For count: {"count": {...}}
For distinct: {"distinct": "field_name", "filter": {...}}

Return ONLY the MongoDB query as a JSON object.""",
        
        "pandas": """You are an expert Pandas code generator. Given a natural language question and DataFrame columns,
generate ONLY valid Pandas code to query the data. Assume the DataFrame is named 'df'.
IMPORTANT: Only generate READ-ONLY operations. Never generate operations that modify the original DataFrame.
Return ONLY the Pandas code, nothing else. The code should return a DataFrame or Series."""
    }
    
    system_prompt = system_prompts.get(query_type, system_prompts["sql"])
    
    user_message = f"""Schema/Columns:
{schema_context}

Natural Language Query: {prompt}

Generate the {query_type.upper()} query:"""

    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.1,
            max_completion_tokens=1024,
            top_p=0.9,
            stream=False
        )
        
        if completion.choices and len(completion.choices) > 0:
            return completion.choices[0].message.content.strip()
        return None
        
    except APIError as e:
        logger.error(f"Groq API error: {e}")
        return None
    except Exception as e:
        logger.error(f"Groq request failed: {e}")
        return None


async def generate_with_groq_streaming(
    prompt: str,
    query_type: str,
    schema_context: str
):
    """
    Generate query using Groq with streaming (for future use).
    
    Yields chunks of the response as they come in.
    """
    client = get_groq_client()
    if not client:
        return
    
    system_prompts = {
        "sql": "You are an expert SQL query generator. Generate ONLY valid SELECT queries.",
        "mongo": "You are an expert MongoDB query generator. Generate ONLY valid read queries.",
        "pandas": "You are an expert Pandas code generator. Generate ONLY read operations."
    }
    
    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompts.get(query_type, "")},
                {"role": "user", "content": f"Schema: {schema_context}\n\nQuery: {prompt}"}
            ],
            temperature=0.1,
            max_completion_tokens=1024,
            top_p=0.9,
            stream=True
        )
        
        for chunk in completion:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
                
    except Exception as e:
        logger.error(f"Groq streaming failed: {e}")


async def get_groq_completion(prompt: str, temperature: float = 0.3) -> str:
    """
    Get a general completion from Groq LLM.
    Used for tasks like visualization suggestions and data analysis.
    
    Args:
        prompt: The prompt to send to Groq
        temperature: Sampling temperature (0-1)
        
    Returns:
        Completion text from Groq
    """
    client = get_groq_client()
    if not client:
        raise Exception("Groq client not available. Check GROQ_API_KEY environment variable.")
    
    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_completion_tokens=2048,
            top_p=0.95,
            stream=False
        )
        
        if completion.choices and len(completion.choices) > 0:
            return completion.choices[0].message.content.strip()
        
        raise Exception("No response from Groq")
        
    except APIError as e:
        logger.error(f"Groq API error: {e}")
        raise Exception(f"Groq API error: {str(e)}")
    except Exception as e:
        logger.error(f"Groq request failed: {e}")
        raise Exception(f"Failed to get Groq completion: {str(e)}")
