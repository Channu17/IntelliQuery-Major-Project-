"""
Excel/CSV Data Populator for Voxalize Demo (Pandas Agent)
Generates 5000 analysis-friendly records for sales/business intelligence demo
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker
import random


# Initialize Faker
fake = Faker()

# File Configuration
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_FILE = "sales_data_demo.csv"

# Data Generation Parameters
NUM_RECORDS = 5000

# Business Data Constants
PRODUCTS = [
    {"name": "Laptop Pro X1", "category": "Electronics", "base_price": 1200},
    {"name": "Wireless Mouse", "category": "Electronics", "base_price": 25},
    {"name": "Mechanical Keyboard", "category": "Electronics", "base_price": 89},
    {"name": "4K Monitor", "category": "Electronics", "base_price": 450},
    {"name": "USB-C Hub", "category": "Electronics", "base_price": 45},
    {"name": "Office Chair", "category": "Furniture", "base_price": 299},
    {"name": "Standing Desk", "category": "Furniture", "base_price": 599},
    {"name": "Desk Lamp", "category": "Furniture", "base_price": 35},
    {"name": "Coffee Maker", "category": "Appliances", "base_price": 89},
    {"name": "Water Purifier", "category": "Appliances", "base_price": 199},
    {"name": "Air Purifier", "category": "Appliances", "base_price": 249},
    {"name": "Notebook Set", "category": "Stationery", "base_price": 12},
    {"name": "Pen Collection", "category": "Stationery", "base_price": 8},
    {"name": "Phone Case", "category": "Accessories", "base_price": 15},
    {"name": "Laptop Bag", "category": "Accessories", "base_price": 49},
]

REGIONS = ["North", "South", "East", "West", "Central"]
PAYMENT_METHODS = ["Credit Card", "Debit Card", "UPI", "Net Banking", "Cash on Delivery"]
ORDER_STATUS = ["Completed", "Pending", "Cancelled", "Refunded"]
CUSTOMER_SEGMENTS = ["Enterprise", "SMB", "Individual", "Retail"]


def generate_sales_data(num_records: int) -> pd.DataFrame:
    """Generate sales data with realistic patterns"""
    
    records = []
    
    print(f"Generating {num_records} records...")
    
    for i in range(1, num_records + 1):
        # Select product
        product = random.choice(PRODUCTS)
        
        # Generate quantity (weighted towards lower quantities)
        quantity = random.choices(
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            weights=[30, 25, 15, 10, 8, 5, 3, 2, 1, 1]
        )[0]
        
        # Calculate price with some variance
        unit_price = round(product["base_price"] * random.uniform(0.9, 1.15), 2)
        
        # Apply discount (20% chance of discount)
        discount_percent = 0
        if random.random() < 0.2:
            discount_percent = random.choice([5, 10, 15, 20, 25])
        
        subtotal = round(unit_price * quantity, 2)
        discount_amount = round(subtotal * discount_percent / 100, 2)
        total_amount = round(subtotal - discount_amount, 2)
        
        # Generate date (last 18 months)
        start_date = datetime.now() - timedelta(days=540)
        days_offset = random.randint(0, 540)
        transaction_date = start_date + timedelta(days=days_offset)
        
        # Status weights (90% completed, 5% pending, 3% cancelled, 2% refunded)
        status = random.choices(ORDER_STATUS, weights=[90, 5, 3, 2])[0]
        
        # Generate customer info
        customer_segment = random.choice(CUSTOMER_SEGMENTS)
        
        # Payment method
        payment_method = random.choice(PAYMENT_METHODS)
        
        # Region
        region = random.choice(REGIONS)
        
        # Create record
        record = {
            "transaction_id": f"TXN{i:06d}",
            "transaction_date": transaction_date.strftime("%Y-%m-%d"),
            "customer_name": fake.name(),
            "customer_email": fake.email(),
            "customer_segment": customer_segment,
            "region": region,
            "product_name": product["name"],
            "product_category": product["category"],
            "quantity": quantity,
            "unit_price": unit_price,
            "discount_percent": discount_percent,
            "discount_amount": discount_amount,
            "total_amount": total_amount,
            "payment_method": payment_method,
            "order_status": status
        }
        
        records.append(record)
        
        # Progress indicator
        if i % 500 == 0:
            print(f"  Generated {i}/{num_records} records...")
    
    # Create DataFrame
    df = pd.DataFrame(records)
    
    return df


def display_statistics(df: pd.DataFrame):
    """Display summary statistics"""
    
    print("\n" + "=" * 60)
    print("DATA STATISTICS")
    print("=" * 60)
    
    print(f"\n📊 Dataset Overview:")
    print(f"  Total Records: {len(df)}")
    print(f"  Columns: {len(df.columns)}")
    print(f"  Date Range: {df['transaction_date'].min()} to {df['transaction_date'].max()}")
    
    print(f"\n💰 Financial Summary:")
    print(f"  Total Revenue: ${df[df['order_status'] == 'Completed']['total_amount'].sum():,.2f}")
    print(f"  Average Order Value: ${df['total_amount'].mean():.2f}")
    print(f"  Median Order Value: ${df['total_amount'].median():.2f}")
    print(f"  Total Discount Given: ${df['discount_amount'].sum():,.2f}")
    
    print(f"\n📦 Product Category Distribution:")
    category_counts = df['product_category'].value_counts()
    for category, count in category_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {category}: {count} ({percentage:.1f}%)")
    
    print(f"\n🌍 Regional Distribution:")
    region_counts = df['region'].value_counts()
    for region, count in region_counts.items():
        revenue = df[df['region'] == region]['total_amount'].sum()
        print(f"  {region}: {count} transactions - ${revenue:,.2f} revenue")
    
    print(f"\n👥 Customer Segment Analysis:")
    segment_stats = df.groupby('customer_segment').agg({
        'total_amount': ['sum', 'mean', 'count']
    }).round(2)
    for segment in df['customer_segment'].unique():
        segment_data = df[df['customer_segment'] == segment]
        total_rev = segment_data['total_amount'].sum()
        avg_order = segment_data['total_amount'].mean()
        count = len(segment_data)
        print(f"  {segment}: {count} orders, ${total_rev:,.2f} total, ${avg_order:.2f} avg")
    
    print(f"\n📈 Order Status Breakdown:")
    status_stats = df.groupby('order_status').agg({
        'total_amount': ['sum', 'count']
    })
    for status in df['order_status'].unique():
        status_data = df[df['order_status'] == status]
        count = len(status_data)
        revenue = status_data['total_amount'].sum()
        percentage = (count / len(df)) * 100
        print(f"  {status}: {count} ({percentage:.1f}%) - ${revenue:,.2f}")
    
    print(f"\n💳 Payment Method Distribution:")
    payment_counts = df['payment_method'].value_counts()
    for method, count in payment_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {method}: {count} ({percentage:.1f}%)")
    
    print(f"\n🔝 Top 5 Products by Revenue:")
    product_revenue = df[df['order_status'] == 'Completed'].groupby('product_name')['total_amount'].sum().sort_values(ascending=False).head(5)
    for i, (product, revenue) in enumerate(product_revenue.items(), 1):
        print(f"  {i}. {product}: ${revenue:,.2f}")


def populate_excel():
    """Main function to generate and save Excel/CSV data"""
    
    print("=" * 60)
    print("Excel/CSV Data Populator for Voxalize Demo")
    print("=" * 60)
    
    try:
        # Generate data
        print(f"\n[1/3] Generating {NUM_RECORDS} sales records...")
        df = generate_sales_data(NUM_RECORDS)
        print(f"✓ Generated {len(df)} records")
        
        # Create output directory if it doesn't exist
        print(f"\n[2/3] Preparing output directory...")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
        print(f"✓ Output path: {output_path}")
        
        # Save to CSV
        print(f"\n[3/3] Saving to CSV file...")
        df.to_csv(output_path, index=False)
        print(f"✓ Saved to: {output_path}")
        
        # Display statistics
        display_statistics(df)
        
        # Column info
        print("\n" + "=" * 60)
        print("COLUMN INFORMATION")
        print("=" * 60)
        print(f"\nColumns ({len(df.columns)}):")
        for i, col in enumerate(df.columns, 1):
            dtype = df[col].dtype
            print(f"  {i}. {col} ({dtype})")
        
        print("\n" + "=" * 60)
        print("DATA POPULATION COMPLETE!")
        print("=" * 60)
        print(f"\n✅ CSV file ready at: {output_path}")
        print(f"✅ Total records: {len(df)}")
        print(f"✅ Ready for Pandas agent queries!")
        print("=" * 60)
        
        return output_path
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    populate_excel()
