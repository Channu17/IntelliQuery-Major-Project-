# MongoDB Demo Data Guide

## Overview
This guide explains the MongoDB data population script created for the Voxalize demo.

## Data Structure

### Collection: `sales_transactions`
**Total Records:** 5,000 business transactions

### Schema (16 Fields)

| Field | Type | Description | Example Values |
|-------|------|-------------|----------------|
| `transaction_id` | String | Unique transaction identifier | "TXN000001" |
| `transaction_date` | DateTime | When transaction occurred | 2024-08-15 14:23:10 |
| `customer_name` | String | Full name of customer | "John Smith" |
| `customer_email` | String | Customer email address | "john.smith@email.com" |
| `customer_segment` | String | Business segment | Enterprise, SMB, Individual, Retail |
| `region` | String | Geographic region | North, South, East, West, Central |
| `product_name` | String | Product purchased | "Laptop Pro X1", "Office Chair" |
| `product_category` | String | Product category | Electronics, Furniture, Appliances, Stationery, Accessories |
| `quantity` | Integer | Units purchased | 1-10 (weighted towards lower values) |
| `unit_price` | Float | Price per unit | Varies by product with ±15% variance |
| `discount_percent` | Integer | Discount applied | 0, 5, 10, 15, 20, 25 |
| `discount_amount` | Float | Dollar amount discounted | Calculated value |
| `total_amount` | Float | Final transaction amount | Calculated value |
| `payment_method` | String | Payment method used | Credit Card, Debit Card, UPI, Net Banking, Cash on Delivery |
| `order_status` | String | Current order status | Completed (90%), Pending (5%), Cancelled (3%), Refunded (2%) |
| `created_at` | DateTime | Record creation timestamp | System timestamp |

## Usage

### 1. Activate Virtual Environment
```bash
cd f:\IntelliQuery\backend
source intelenv/Scripts/activate  # On Windows Git Bash
# or
.\intelenv\Scripts\activate.bat   # On Windows CMD
# or
.\intelenv\Scripts\Activate.ps1   # On Windows PowerShell
```

### 2. Ensure Dependencies
```bash
pip install pymongo faker
```

### 3. Set Environment Variables (Optional)
```bash
export MONGO_URI="mongodb://localhost:27017"
export MONGO_DB_NAME="intelliquery"
```

### 4. Run the Population Script
```bash
cd f:\IntelliQuery\backend
python -m utils.mongo_populator
```

## Sample Queries for Demo

### Basic Queries

1. **Total revenue by category**
   - "What is the total revenue by product category?"
   - "Show me sales breakdown by category"

2. **Regional performance**
   - "Which region has the highest sales?"
   - "Compare revenue across all regions"

3. **Top products**
   - "What are the top 5 products by revenue?"
   - "Show me best selling products"

4. **Customer segment analysis**
   - "What's the total revenue from Enterprise customers?"
   - "Compare sales across customer segments"

5. **Time-based analysis**
   - "Show monthly revenue for the last 6 months"
   - "What were the sales in December 2024?"

6. **Discount impact**
   - "What's the average discount percentage by category?"
   - "How much revenue was lost to discounts?"

7. **Payment preferences**
   - "What's the most popular payment method?"
   - "Show transaction count by payment method"

8. **Order status tracking**
   - "How many orders are pending?"
   - "What percentage of orders were cancelled?"

### Advanced Queries

1. **Multi-dimensional analysis**
   - "Show me revenue by region and category"
   - "Which customer segment buys the most electronics?"

2. **Aggregations**
   - "What's the average order value?"
   - "Calculate total quantity sold per product"

3. **Filtering**
   - "Show all transactions above $1000"
   - "List all cancelled orders in the North region"

4. **Date ranges**
   - "Show sales between January and March 2025"
   - "Compare Q1 vs Q2 revenue"

## Data Characteristics

### Analysis-Friendly Features

1. **Multiple Dimensions**: Region, Category, Segment, Status for multi-dimensional analysis
2. **Time Series Data**: 18 months of historical data for trend analysis
3. **Numerical Metrics**: Revenue, quantity, discounts for aggregations
4. **Realistic Distribution**: Weighted probabilities for realistic business patterns
5. **Categorical Data**: Multiple categorical fields for grouping and filtering

### Business Intelligence Use Cases

- Sales performance dashboards
- Regional market analysis
- Product category insights
- Customer segment profiling
- Discount effectiveness analysis
- Payment method trends
- Order fulfillment tracking
- Revenue forecasting

## Data Volume

- **5,000 transactions**
- **15 unique products** across 5 categories
- **5 regions** for geographic analysis
- **4 customer segments** for market segmentation
- **5 payment methods**
- **18 months** of historical data

## Indexes Created

For optimal query performance, the following indexes are automatically created:
- `transaction_id` - Unique transaction lookup
- `transaction_date` - Time-based queries
- `product_category` - Category filtering
- `region` - Regional analysis
- `customer_segment` - Segment filtering

## Maintenance

### Regenerate Data
To regenerate with fresh data:
```bash
python -m utils.mongo_populator
```
The script automatically drops and recreates the collection.

### Verify Data
```python
from utils.db import get_db
db = get_db()
collection = db.sales_transactions
print(f"Total records: {collection.count_documents({})}")
```

## Integration with Voxalize

This data is designed to work seamlessly with Voxalize's:
- Natural language query processing
- MongoDB agent for NoSQL queries
- Visualization generation
- Voice-to-query conversion

Users can ask questions naturally and get meaningful insights from this rich dataset.
