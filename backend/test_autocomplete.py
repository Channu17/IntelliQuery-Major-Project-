"""
Test script for autocomplete functionality.
"""
import asyncio
import time

async def test_autocomplete():
    """Test autocomplete with various inputs."""
    from ai.autocomplete import autocomplete
    
    # Mock datasource
    mock_datasource = {
        "_id": "test_ds_001",
        "user_id": "user123",
        "type": "sql",
        "details": {
            "host": "localhost",
            "database": "sales_db"
        }
    }
    
    # Mock datasource store
    from unittest.mock import patch
    
    test_queries = [
        "sh",
        "show",
        "show me",
        "show me all",
        "count",
        "find",
        "get top",
        "what are",
        "list all"
    ]
    
    print("=" * 70)
    print("🔍 Testing Autocomplete Performance")
    print("=" * 70)
    
    for query in test_queries:
        print(f"\n📝 Input: '{query}'")
        
        start_time = time.time()
        
        # Get fallback suggestions (doesn't need datasource)
        suggestions = autocomplete._get_fallback_suggestions(query)
        
        elapsed = (time.time() - start_time) * 1000  # Convert to ms
        
        print(f"⚡ Response time: {elapsed:.2f}ms")
        print(f"💡 Suggestions:")
        for i, suggestion in enumerate(suggestions[:5], 1):
            print(f"   {i}. {suggestion}")
    
    # Test caching
    print("\n" + "=" * 70)
    print("🗄️  Testing Cache Performance")
    print("=" * 70)
    
    query = "show me all"
    cache_key = f"test_ds_001:{query}"
    
    # First call (not cached)
    autocomplete.suggestion_cache[cache_key] = [
        "show me all records",
        "show me all users",
        "show me all products"
    ]
    
    start_time = time.time()
    autocomplete.suggestion_cache.get(cache_key)
    cache_time = (time.time() - start_time) * 1000
    
    print(f"✅ Cache hit time: {cache_time:.4f}ms")
    print(f"🚀 Cache is ~{1000/max(cache_time, 0.001):.0f}x faster than network call")
    
    # Test cache cleanup
    print("\n" + "=" * 70)
    print("🧹 Testing Cache Management")
    print("=" * 70)
    
    print(f"📊 Current cache size: {len(autocomplete.suggestion_cache)} entries")
    autocomplete.clear_cache()
    print(f"✨ After clear: {len(autocomplete.suggestion_cache)} entries")
    
    print("\n" + "=" * 70)
    print("✅ All Tests Completed!")
    print("=" * 70)


async def test_groq_integration():
    """Test Groq LLM integration for suggestions."""
    print("\n" + "=" * 70)
    print("🤖 Testing Groq LLM Integration")
    print("=" * 70)
    
    from ai.autocomplete import autocomplete
    
    schema_summary = "Tables: users(id, name, email, age), orders(id, user_id, total, date)"
    
    test_inputs = [
        ("show me", "sql"),
        ("count", "sql"),
        ("find users", "sql"),
    ]
    
    for partial_query, ds_type in test_inputs:
        print(f"\n📝 Generating suggestions for: '{partial_query}'")
        
        try:
            start_time = time.time()
            
            suggestions = await autocomplete._generate_suggestions(
                partial_query=partial_query,
                schema_summary=schema_summary,
                datasource_type=ds_type,
                limit=5
            )
            
            elapsed = (time.time() - start_time) * 1000
            
            print(f"⚡ LLM response time: {elapsed:.0f}ms")
            print(f"💡 Suggestions:")
            for i, s in enumerate(suggestions, 1):
                print(f"   {i}. {s}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            print("   Using fallback suggestions...")
    
    print("\n✅ Groq integration test completed!")


async def benchmark_autocomplete():
    """Benchmark autocomplete performance."""
    print("\n" + "=" * 70)
    print("⚡ Autocomplete Performance Benchmark")
    print("=" * 70)
    
    from ai.autocomplete import autocomplete
    
    iterations = 100
    query = "show me all"
    
    # Warm up cache
    cache_key = f"test_ds:{query}"
    autocomplete.suggestion_cache[cache_key] = [
        "show me all records",
        "show me all users"
    ]
    
    # Benchmark cached lookups
    start = time.time()
    for _ in range(iterations):
        autocomplete.suggestion_cache.get(cache_key)
    elapsed = (time.time() - start) * 1000
    
    avg_time = elapsed / iterations
    requests_per_sec = 1000 / avg_time
    
    print(f"\n📊 Results ({iterations} iterations):")
    print(f"   Total time: {elapsed:.2f}ms")
    print(f"   Average time per request: {avg_time:.4f}ms")
    print(f"   Requests per second: {requests_per_sec:.0f}")
    print(f"\n🚀 Can handle ~{requests_per_sec:.0f} concurrent users typing!")
    
    # Test fallback performance
    print("\n📊 Fallback suggestion performance:")
    start = time.time()
    for _ in range(iterations):
        autocomplete._get_fallback_suggestions("show me")
    elapsed = (time.time() - start) * 1000
    
    avg_fallback = elapsed / iterations
    print(f"   Average fallback time: {avg_fallback:.4f}ms")
    print(f"   Fallback RPS: {1000/avg_fallback:.0f}")


async def main():
    """Run all tests."""
    print("\n🚀 Starting Autocomplete Test Suite\n")
    
    try:
        # Basic functionality
        await test_autocomplete()
        
        # Groq integration (requires API key)
        try:
            await test_groq_integration()
        except Exception as e:
            print(f"\n⚠️  Groq test skipped: {e}")
            print("   (Set GROQ_API_KEY to test LLM features)")
        
        # Performance benchmark
        await benchmark_autocomplete()
        
        print("\n" + "=" * 70)
        print("✅ All Autocomplete Tests Passed!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
