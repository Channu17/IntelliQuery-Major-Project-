"""
Test script to verify Excel/CSV data and run sample Pandas queries
"""

import os
import pandas as pd
import numpy as np


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DATA_FILE = "sales_data_demo.csv"


def test_file_exists():
    """Check if the CSV file exists"""
    file_path = os.path.join(DATA_DIR, DATA_FILE)
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        print("⚠️  Please run excel_populator.py first!")
        return None
    
    print(f"✓ File found: {file_path}")
    return file_path


def load_and_verify_data(file_path: str) -> pd.DataFrame:
    """Load CSV and verify basic structure"""
    try:
        df = pd.read_csv(file_path)
        print(f"✓ Successfully loaded data")
        print(f"  Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        return df
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return None


def display_sample_data(df: pd.DataFrame):
    """Display sample records"""
    print("\n" + "=" * 60)
    print("SAMPLE DATA")
    print("=" * 60)
    
    print("\n📝 First 3 Records:")
    print(df.head(3).to_string())
    
    print("\n\n📊 Data Types:")
    print(df.dtypes)
    
    print("\n\n📈 Basic Statistics:")
    print(df.describe())


def run_sample_queries(df: pd.DataFrame):
    """Run sample Pandas queries to demonstrate capabilities"""
    
    print("\n" + "=" * 60)
    print("SAMPLE PANDAS QUERIES")
    print("=" * 60)
    
    # Query 1: Total revenue by category
    print("\n1️⃣  Total Revenue by Category:")
    category_revenue = df[df['order_status'] == 'Completed'].groupby('product_category')['total_amount'].sum().sort_values(ascending=False)
    for category, revenue in category_revenue.items():
        print(f"   {category}: ${revenue:,.2f}")
    
    # Query 2: Monthly revenue trend
    print("\n2️⃣  Monthly Revenue Trend (Last 6 Months):")
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    df_completed = df[df['order_status'] == 'Completed'].copy()
    df_completed['month'] = df_completed['transaction_date'].dt.to_period('M')
    monthly_revenue = df_completed.groupby('month')['total_amount'].sum().tail(6)
    for month, revenue in monthly_revenue.items():
        print(f"   {month}: ${revenue:,.2f}")
    
    # Query 3: Top 10 customers by spending
    print("\n3️⃣  Top 10 Customers by Total Spending:")
    top_customers = df[df['order_status'] == 'Completed'].groupby('customer_name').agg({
        'total_amount': 'sum',
        'transaction_id': 'count'
    }).sort_values('total_amount', ascending=False).head(10)
    top_customers.columns = ['Total Spent', 'Orders']
    for i, (customer, row) in enumerate(top_customers.iterrows(), 1):
        print(f"   {i}. {customer}: ${row['Total Spent']:,.2f} ({row['Orders']} orders)")
    
    # Query 4: Average order value by region
    print("\n4️⃣  Average Order Value by Region:")
    region_avg = df.groupby('region')['total_amount'].agg(['mean', 'count']).sort_values('mean', ascending=False)
    region_avg.columns = ['Avg Order Value', 'Total Orders']
    for region, row in region_avg.iterrows():
        print(f"   {region}: ${row['Avg Order Value']:.2f} ({row['Total Orders']} orders)")
    
    # Query 5: Discount analysis
    print("\n5️⃣  Discount Impact Analysis:")
    df_with_discount = df[df['discount_percent'] > 0]
    df_no_discount = df[df['discount_percent'] == 0]
    print(f"   Orders with Discount: {len(df_with_discount)} ({len(df_with_discount)/len(df)*100:.1f}%)")
    print(f"   Orders without Discount: {len(df_no_discount)} ({len(df_no_discount)/len(df)*100:.1f}%)")
    print(f"   Average Discount: {df['discount_percent'].mean():.2f}%")
    print(f"   Total Discount Amount: ${df['discount_amount'].sum():,.2f}")
    
    # Query 6: Product performance
    print("\n6️⃣  Product Performance Analysis:")
    product_stats = df[df['order_status'] == 'Completed'].groupby('product_name').agg({
        'total_amount': 'sum',
        'quantity': 'sum',
        'transaction_id': 'count'
    }).sort_values('total_amount', ascending=False)
    product_stats.columns = ['Revenue', 'Units Sold', 'Transactions']
    print("\n   Top 5 Products:")
    for i, (product, row) in enumerate(product_stats.head(5).iterrows(), 1):
        print(f"   {i}. {product}")
        print(f"      Revenue: ${row['Revenue']:,.2f} | Units: {row['Units Sold']} | Orders: {row['Transactions']}")
    
    # Query 7: Customer segment profitability
    print("\n7️⃣  Customer Segment Profitability:")
    segment_stats = df[df['order_status'] == 'Completed'].groupby('customer_segment').agg({
        'total_amount': ['sum', 'mean', 'count']
    }).round(2)
    segment_stats.columns = ['Total Revenue', 'Avg Order', 'Order Count']
    segment_stats = segment_stats.sort_values('Total Revenue', ascending=False)
    for segment, row in segment_stats.iterrows():
        print(f"   {segment}: ${row['Total Revenue']:,.2f} | Avg: ${row['Avg Order']:.2f} | Orders: {int(row['Order Count'])}")
    
    # Query 8: Payment method preferences
    print("\n8️⃣  Payment Method Analysis:")
    payment_stats = df.groupby('payment_method').agg({
        'transaction_id': 'count',
        'total_amount': 'sum'
    }).sort_values('transaction_id', ascending=False)
    payment_stats.columns = ['Transactions', 'Total Value']
    for method, row in payment_stats.iterrows():
        percentage = (row['Transactions'] / len(df)) * 100
        print(f"   {method}: {row['Transactions']} ({percentage:.1f}%) - ${row['Total Value']:,.2f}")
    
    # Query 9: High-value transactions
    print("\n9️⃣  High-Value Transaction Analysis:")
    high_value_threshold = df['total_amount'].quantile(0.95)
    high_value_orders = df[df['total_amount'] >= high_value_threshold]
    print(f"   Threshold (95th percentile): ${high_value_threshold:.2f}")
    print(f"   High-value orders: {len(high_value_orders)} ({len(high_value_orders)/len(df)*100:.1f}%)")
    print(f"   Total value: ${high_value_orders['total_amount'].sum():,.2f}")
    
    # Query 10: Cancellation analysis
    print("\n🔟 Order Status & Cancellation Analysis:")
    status_stats = df.groupby('order_status').agg({
        'transaction_id': 'count',
        'total_amount': 'sum'
    })
    status_stats.columns = ['Count', 'Value']
    for status, row in status_stats.iterrows():
        percentage = (row['Count'] / len(df)) * 100
        print(f"   {status}: {row['Count']} ({percentage:.1f}%) - ${row['Value']:,.2f}")


def main():
    """Main test function"""
    print("=" * 60)
    print("Excel/CSV Data Verification & Query Test")
    print("=" * 60)
    
    # Check file
    file_path = test_file_exists()
    if not file_path:
        return
    
    # Load data
    print("\n" + "=" * 60)
    print("LOADING DATA")
    print("=" * 60 + "\n")
    df = load_and_verify_data(file_path)
    if df is None:
        return
    
    # Display sample
    display_sample_data(df)
    
    # Run queries
    run_sample_queries(df)
    
    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
    print("=" * 60)
    print(f"\n📁 Your CSV file is ready at: {file_path}")
    print("🚀 Ready for Voxalize Pandas agent queries!")
    print("\nExample queries you can try:")
    print("  • 'What is the total revenue by category?'")
    print("  • 'Show me the top 5 customers by spending'")
    print("  • 'What's the average order value by region?'")
    print("  • 'How many cancelled orders do we have?'")
    print("  • 'Show monthly revenue trend'")


if __name__ == "__main__":
    main()
