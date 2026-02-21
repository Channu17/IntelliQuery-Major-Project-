"""
Test script to verify MongoDB population and run sample queries
"""

from utils.db import get_db
from pymongo.database import Database


def test_mongo_connection():
    """Test MongoDB connection"""
    try:
        db = get_db()
        db.command("ping")
        print("✓ MongoDB connection successful")
        return True
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        return False


def verify_data_population():
    """Verify data has been populated correctly"""
    db = get_db()
    collection = db.sales_transactions
    
    print("\n" + "=" * 60)
    print("DATA VERIFICATION")
    print("=" * 60)
    
    # Check record count
    total_records = collection.count_documents({})
    print(f"\nTotal Records: {total_records}")
    
    if total_records == 0:
        print("⚠️  No data found. Please run mongo_populator.py first!")
        return False
    
    # Sample record
    print("\n📝 Sample Record:")
    sample = collection.find_one()
    if sample:
        print(f"  Transaction ID: {sample.get('transaction_id')}")
        print(f"  Date: {sample.get('transaction_date')}")
        print(f"  Customer: {sample.get('customer_name')}")
        print(f"  Product: {sample.get('product_name')}")
        print(f"  Category: {sample.get('product_category')}")
        print(f"  Quantity: {sample.get('quantity')}")
        print(f"  Total Amount: ${sample.get('total_amount')}")
        print(f"  Region: {sample.get('region')}")
        print(f"  Status: {sample.get('order_status')}")
    
    return True


def run_sample_queries():
    """Run sample analytical queries"""
    db = get_db()
    collection = db.sales_transactions
    
    print("\n" + "=" * 60)
    print("SAMPLE ANALYTICAL QUERIES")
    print("=" * 60)
    
    # Query 1: Total revenue
    print("\n1️⃣  Total Revenue:")
    pipeline = [
        {"$match": {"order_status": "Completed"}},
        {"$group": {"_id": None, "total_revenue": {"$sum": "$total_amount"}}}
    ]
    result = list(collection.aggregate(pipeline))
    if result:
        print(f"   ${result[0]['total_revenue']:,.2f}")
    
    # Query 2: Revenue by category
    print("\n2️⃣  Revenue by Product Category:")
    pipeline = [
        {"$match": {"order_status": "Completed"}},
        {"$group": {
            "_id": "$product_category",
            "revenue": {"$sum": "$total_amount"},
            "orders": {"$sum": 1}
        }},
        {"$sort": {"revenue": -1}}
    ]
    for doc in collection.aggregate(pipeline):
        print(f"   {doc['_id']}: ${doc['revenue']:,.2f} ({doc['orders']} orders)")
    
    # Query 3: Top 5 customers by spending
    print("\n3️⃣  Top 5 Customers by Total Spending:")
    pipeline = [
        {"$match": {"order_status": "Completed"}},
        {"$group": {
            "_id": "$customer_email",
            "customer_name": {"$first": "$customer_name"},
            "total_spent": {"$sum": "$total_amount"},
            "orders": {"$sum": 1}
        }},
        {"$sort": {"total_spent": -1}},
        {"$limit": 5}
    ]
    for i, doc in enumerate(collection.aggregate(pipeline), 1):
        print(f"   {i}. {doc['customer_name']}: ${doc['total_spent']:,.2f} ({doc['orders']} orders)")
    
    # Query 4: Regional analysis
    print("\n4️⃣  Revenue by Region:")
    pipeline = [
        {"$match": {"order_status": "Completed"}},
        {"$group": {
            "_id": "$region",
            "revenue": {"$sum": "$total_amount"},
            "avg_order_value": {"$avg": "$total_amount"}
        }},
        {"$sort": {"revenue": -1}}
    ]
    for doc in collection.aggregate(pipeline):
        print(f"   {doc['_id']}: ${doc['revenue']:,.2f} (Avg: ${doc['avg_order_value']:.2f})")
    
    # Query 5: Payment method distribution
    print("\n5️⃣  Payment Method Distribution:")
    pipeline = [
        {"$group": {
            "_id": "$payment_method",
            "count": {"$sum": 1},
            "percentage": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]
    total = collection.count_documents({})
    for doc in collection.aggregate(pipeline):
        percentage = (doc['count'] / total) * 100
        print(f"   {doc['_id']}: {doc['count']} ({percentage:.1f}%)")
    
    # Query 6: Orders by status
    print("\n6️⃣  Order Status Summary:")
    pipeline = [
        {"$group": {
            "_id": "$order_status",
            "count": {"$sum": 1},
            "total_value": {"$sum": "$total_amount"}
        }},
        {"$sort": {"count": -1}}
    ]
    for doc in collection.aggregate(pipeline):
        print(f"   {doc['_id']}: {doc['count']} orders (${doc['total_value']:,.2f})")
    
    # Query 7: Average metrics
    print("\n7️⃣  Average Metrics:")
    pipeline = [
        {"$group": {
            "_id": None,
            "avg_order_value": {"$avg": "$total_amount"},
            "avg_quantity": {"$avg": "$quantity"},
            "avg_discount": {"$avg": "$discount_percent"}
        }}
    ]
    result = list(collection.aggregate(pipeline))
    if result:
        doc = result[0]
        print(f"   Average Order Value: ${doc['avg_order_value']:.2f}")
        print(f"   Average Quantity per Order: {doc['avg_quantity']:.2f}")
        print(f"   Average Discount: {doc['avg_discount']:.2f}%")
    
    # Query 8: Customer segments
    print("\n8️⃣  Revenue by Customer Segment:")
    pipeline = [
        {"$match": {"order_status": "Completed"}},
        {"$group": {
            "_id": "$customer_segment",
            "revenue": {"$sum": "$total_amount"},
            "customers": {"$addToSet": "$customer_email"}
        }},
        {"$project": {
            "_id": 1,
            "revenue": 1,
            "customer_count": {"$size": "$customers"}
        }},
        {"$sort": {"revenue": -1}}
    ]
    for doc in collection.aggregate(pipeline):
        print(f"   {doc['_id']}: ${doc['revenue']:,.2f} ({doc['customer_count']} unique customers)")


def main():
    """Main test function"""
    print("=" * 60)
    print("MongoDB Data Population Test")
    print("=" * 60)
    
    # Test connection
    if not test_mongo_connection():
        return
    
    # Verify data
    if not verify_data_population():
        return
    
    # Run sample queries
    run_sample_queries()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
    print("=" * 60)
    print("\nYour MongoDB database is ready for Voxalize demo queries!")


if __name__ == "__main__":
    main()
