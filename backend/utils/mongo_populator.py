"""
MongoDB Data Populator for Voxalize Demo
Generates 5000 analysis-friendly records for sales/business intelligence demo
"""

import os
from datetime import datetime, timedelta
from faker import Faker
import random
from pymongo import MongoClient
from pymongo.database import Database


# Initialize Faker
fake = Faker()

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("POPULATOR_DB_NAME", "ecommerce")
COLLECTION_NAME = os.getenv("POPULATOR_COLLECTION", "sales_transactions")

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


def get_mongo_connection() -> Database:
    """Establish MongoDB connection"""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return client[DB_NAME]


def generate_transaction_record(index: int) -> dict:
    """Generate a single transaction record with realistic data"""
    
    # Select product
    product = random.choice(PRODUCTS)
    
    # Generate quantity (weighted towards lower quantities)
    quantity = random.choices([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 
                             weights=[30, 25, 15, 10, 8, 5, 3, 2, 1, 1])[0]
    
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
    transaction_date = fake.date_time_between(start_date="-18M", end_date="now")
    
    # Status weights (90% completed, 5% pending, 3% cancelled, 2% refunded)
    status = random.choices(ORDER_STATUS, weights=[90, 5, 3, 2])[0]
    
    # Generate customer info
    customer_segment = random.choice(CUSTOMER_SEGMENTS)
    
    # Payment method
    payment_method = random.choice(PAYMENT_METHODS)
    
    # Region
    region = random.choice(REGIONS)
    
    # Generate transaction record with 9 fields
    record = {
        "transaction_id": f"TXN{index:06d}",
        "transaction_date": transaction_date,
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
        "order_status": status,
        "created_at": datetime.utcnow()
    }
    
    return record


def populate_mongodb():
    """Main function to populate MongoDB with 5000 records"""
    
    print("=" * 60)
    print("MongoDB Data Populator for Voxalize Demo")
    print("=" * 60)
    
    try:
        # Connect to MongoDB
        print(f"\n[1/4] Connecting to MongoDB...")
        db = get_mongo_connection()
        collection = db[COLLECTION_NAME]
        
        # Test connection
        db.command("ping")
        print(f"✓ Connected to database: {DB_NAME}")
        
        # Drop existing collection for clean start
        print(f"\n[2/4] Preparing collection: {COLLECTION_NAME}")
        if COLLECTION_NAME in db.list_collection_names():
            collection.drop()
            print(f"✓ Dropped existing collection")
        
        # Generate records
        print(f"\n[3/4] Generating {NUM_RECORDS} transaction records...")
        records = []
        for i in range(1, NUM_RECORDS + 1):
            record = generate_transaction_record(i)
            records.append(record)
            
            # Progress indicator
            if i % 500 == 0:
                print(f"  Generated {i}/{NUM_RECORDS} records...")
        
        print(f"✓ Generated all {NUM_RECORDS} records")
        
        # Insert records
        print(f"\n[4/4] Inserting records into MongoDB...")
        result = collection.insert_many(records)
        print(f"✓ Inserted {len(result.inserted_ids)} records")
        
        # Create indexes for better query performance
        print(f"\n[5/5] Creating indexes...")
        collection.create_index("transaction_id")
        collection.create_index("transaction_date")
        collection.create_index("product_category")
        collection.create_index("region")
        collection.create_index("customer_segment")
        print(f"✓ Indexes created")
        
        # Display summary statistics
        print("\n" + "=" * 60)
        print("DATA POPULATION COMPLETE!")
        print("=" * 60)
        
        print(f"\nCollection: {COLLECTION_NAME}")
        print(f"Total Records: {collection.count_documents({})}")
        
        # Category distribution
        print("\n📊 Product Category Distribution:")
        pipeline = [
            {"$group": {"_id": "$product_category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        for doc in collection.aggregate(pipeline):
            print(f"  {doc['_id']}: {doc['count']} transactions")
        
        # Region distribution
        print("\n🌍 Region Distribution:")
        pipeline = [
            {"$group": {"_id": "$region", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        for doc in collection.aggregate(pipeline):
            print(f"  {doc['_id']}: {doc['count']} transactions")
        
        # Revenue by status
        print("\n💰 Revenue by Order Status:")
        pipeline = [
            {"$group": {
                "_id": "$order_status", 
                "total_revenue": {"$sum": "$total_amount"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"total_revenue": -1}}
        ]
        for doc in collection.aggregate(pipeline):
            print(f"  {doc['_id']}: ${doc['total_revenue']:,.2f} ({doc['count']} orders)")
        
        print("\n✅ Database is ready for Voxalize demo!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    populate_mongodb()
