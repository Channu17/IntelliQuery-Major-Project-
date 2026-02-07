"""
Test script for visualization agent functionality.
Run this to verify visualization endpoints work correctly.
"""
import asyncio
import json

# Sample test data
sample_sales_data = [
    {"date": "2024-01-01", "product": "Laptop", "sales": 1200, "quantity": 5, "region": "North"},
    {"date": "2024-01-02", "product": "Mouse", "sales": 150, "quantity": 30, "region": "South"},
    {"date": "2024-01-03", "product": "Keyboard", "sales": 300, "quantity": 15, "region": "North"},
    {"date": "2024-01-04", "product": "Laptop", "sales": 2400, "quantity": 10, "region": "East"},
    {"date": "2024-01-05", "product": "Monitor", "sales": 800, "quantity": 8, "region": "West"},
    {"date": "2024-01-06", "product": "Mouse", "sales": 200, "quantity": 40, "region": "North"},
    {"date": "2024-01-07", "product": "Keyboard", "sales": 450, "quantity": 22, "region": "South"},
    {"date": "2024-01-08", "product": "Laptop", "sales": 3600, "quantity": 15, "region": "North"},
    {"date": "2024-01-09", "product": "Monitor", "sales": 1600, "quantity": 16, "region": "East"},
    {"date": "2024-01-10", "product": "Mouse", "sales": 250, "quantity": 50, "region": "West"},
]

sample_customer_data = [
    {"customer_id": 1, "name": "John Doe", "age": 35, "country": "USA", "total_purchases": 5},
    {"customer_id": 2, "name": "Jane Smith", "age": 28, "country": "UK", "total_purchases": 3},
    {"customer_id": 3, "name": "Bob Johnson", "age": 45, "country": "Canada", "total_purchases": 8},
    {"customer_id": 4, "name": "Alice Brown", "age": 32, "country": "USA", "total_purchases": 12},
    {"customer_id": 5, "name": "Charlie Wilson", "age": 51, "country": "Australia", "total_purchases": 6},
]


async def test_suggestions():
    """Test visualization suggestions."""
    from ai.agents.visualization_agent import visualization_agent
    
    print("=" * 60)
    print("Testing Visualization Suggestions")
    print("=" * 60)
    
    suggestions = await visualization_agent.suggest_visualizations(
        results=sample_sales_data,
        query_context="Show sales data by product and region over time"
    )
    
    print("\n✓ Success:", suggestions.get("success"))
    print("\n📊 Recommendations:")
    for i, rec in enumerate(suggestions.get("recommendations", []), 1):
        print(f"\n{i}. Chart Type: {rec.get('type')}")
        print(f"   Reason: {rec.get('reason')}")
        print(f"   X-axis: {rec.get('x_axis')}")
        print(f"   Y-axis: {rec.get('y_axis')}")
        print(f"   Group by: {rec.get('group_by', 'N/A')}")
        print(f"   Priority: {rec.get('priority')}")
    
    print("\n💡 Insights:", suggestions.get("data_insights"))
    print("\n📈 Data Summary:", json.dumps(suggestions.get("data_summary"), indent=2))
    
    return suggestions


async def test_chart_generation(chart_type="bar"):
    """Test chart generation."""
    from ai.agents.visualization_agent import visualization_agent
    
    print("\n" + "=" * 60)
    print(f"Testing {chart_type.upper()} Chart Generation")
    print("=" * 60)
    
    customization = {
        "title": f"Sales Analysis - {chart_type.title()} Chart",
        "theme": "plotly_dark",
        "height": 600,
        "width": 900,
        "show_legend": True
    }
    
    chart = await visualization_agent.generate_visualization(
        results=sample_sales_data,
        chart_type=chart_type,
        x_axis="product" if chart_type in ["bar", "pie"] else "date",
        y_axis="sales",
        group_by="region" if chart_type != "pie" else None,
        customization=customization
    )
    
    print("\n✓ Success:", chart.get("success"))
    print("📊 Chart Type:", chart.get("chart_type"))
    
    if chart.get("success"):
        print("✅ Chart data generated successfully!")
        print(f"   Data size: {len(json.dumps(chart.get('chart_data', {})))} bytes")
    else:
        print("❌ Error:", chart.get("error"))
    
    return chart


async def test_all_chart_types():
    """Test all supported chart types."""
    from ai.agents.visualization_agent import visualization_agent
    
    print("\n" + "=" * 60)
    print("Testing All Chart Types")
    print("=" * 60)
    
    chart_tests = [
        ("line", "date", "sales", "region"),
        ("bar", "product", "sales", "region"),
        ("horizontal_bar", "product", "quantity", None),
        ("pie", "product", "sales", None),
        ("scatter", "quantity", "sales", "product"),
        ("area", "date", "sales", None),
    ]
    
    results = {}
    
    for chart_type, x, y, group in chart_tests:
        try:
            chart = await visualization_agent.generate_visualization(
                results=sample_sales_data,
                chart_type=chart_type,
                x_axis=x,
                y_axis=y,
                group_by=group,
                customization={"title": f"{chart_type.title()} Chart"}
            )
            status = "✅ PASS" if chart.get("success") else f"❌ FAIL: {chart.get('error')}"
            results[chart_type] = status
        except Exception as e:
            results[chart_type] = f"❌ ERROR: {str(e)}"
    
    print("\n" + "=" * 60)
    print("Chart Generation Results:")
    print("=" * 60)
    for chart_type, status in results.items():
        print(f"{chart_type:20s} : {status}")
    
    return results


async def main():
    """Run all tests."""
    print("\n🚀 Starting Visualization Agent Tests\n")
    
    try:
        # Test 1: Suggestions
        await test_suggestions()
        
        # Test 2: Single chart generation
        await test_chart_generation("bar")
        
        # Test 3: All chart types
        await test_all_chart_types()
        
        print("\n" + "=" * 60)
        print("✅ All Tests Completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
