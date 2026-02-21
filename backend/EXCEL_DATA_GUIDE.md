# Excel/CSV Demo Data Guide

## Overview
This guide explains the Excel/CSV data population script created for the Voxalize Pandas agent demo.

## Data Structure

### File: `sales_data_demo.csv`
**Location:** `backend/data/sales_data_demo.csv`
**Total Records:** 5,000 business transactions

### Schema (15 Columns)

| Column | Type | Description | Example Values |
|--------|------|-------------|----------------|
| `transaction_id` | String | Unique transaction identifier | "TXN000001" |
| `transaction_date` | Date | When transaction occurred | "2024-08-15" |
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
pip install pandas faker
```

### 3. Run the Population Script
```bash
cd f:\IntelliQuery\backend
python -m utils.excel_populator
```

### 4. Verify the Data
```bash
python test_excel_data.py
```

## Sample Queries for Demo

### Basic Queries

1. **Revenue by category**
   - "What is the total revenue by product category?"
   - "Show me sales by category"
   - "Which category has the highest revenue?"

2. **Regional analysis**
   - "What is the average order value by region?"
   - "Show me total sales by region"
   - "Which region has the most orders?"

3. **Top performers**
   - "Show me the top 10 customers by spending"
   - "What are the top 5 products by revenue?"
   - "List customers who spent more than $5000"

4. **Time-based analysis**
   - "Show monthly revenue trend"
   - "What was the total revenue in the last quarter?"
   - "Compare sales month over month"

5. **Customer insights**
   - "What's the total revenue from Enterprise customers?"
   - "How many orders did each customer segment make?"
   - "What's the average order value by customer segment?"

6. **Discount analysis**
   - "How many orders had discounts?"
   - "What's the total discount amount given?"
   - "What's the average discount percentage?"

7. **Product performance**
   - "Which products sold the most units?"
   - "Show revenue per product"
   - "What's the transaction count per product?"

8. **Order status**
   - "How many orders were cancelled?"
   - "What percentage of orders are completed?"
   - "Show order count by status"

### Advanced Pandas Queries

1. **Aggregations**
   ```
   "Calculate the average, median, and total revenue"
   "Show sum of quantities by category"
   "What's the standard deviation of order values?"
   ```

2. **Filtering & Conditions**
   ```
   "Show all orders above $1000"
   "List cancelled orders in the North region"
   "Find orders with more than 20% discount"
   ```

3. **Grouping & Pivoting**
   ```
   "Group by region and category, show total revenue"
   "Create a pivot table of revenue by region and segment"
   "Show counts grouped by status and payment method"
   ```

4. **Date-based Analysis**
   ```
   "Show daily/weekly/monthly revenue"
   "Find orders in Q4 2024"
   "Compare revenue year over year"
   ```

5. **Statistical Analysis**
   ```
   "Calculate correlation between quantity and total amount"
   "Show percentile distribution of order values"
   "Find outliers in the dataset"
   ```

6. **Complex Filters**
   ```
   "Show completed orders from Enterprise customers in Electronics"
   "List high-value customers (>$5000) from the North region"
   "Find products with average order value above $500"
   ```

## Data Characteristics

### Analysis-Friendly Features

1. **Multiple Dimensions**: 
   - Geographic (5 regions)
   - Product (5 categories, 15 products)
   - Customer (4 segments)
   - Time (18 months of data)

2. **Numerical Metrics**: 
   - Revenue, quantity, discounts, prices
   - Perfect for aggregations and statistics

3. **Categorical Data**: 
   - Multiple categorical fields for grouping
   - Status, payment methods, segments

4. **Realistic Distribution**: 
   - Weighted probabilities for realistic patterns
   - 90% completion rate, 20% discount rate

5. **Time Series**: 
   - 18 months of historical data
   - Suitable for trend analysis

## Business Intelligence Use Cases

- **Sales Dashboards**: Track revenue, orders, and performance
- **Regional Analysis**: Compare performance across geographies
- **Product Analytics**: Best sellers, revenue per product
- **Customer Segmentation**: Understand spending patterns
- **Discount ROI**: Analyze discount effectiveness
- **Trend Analysis**: Month-over-month, seasonal patterns
- **Payment Insights**: Preferred payment methods
- **Order Management**: Track fulfillment and cancellations

## File Operations

### Load Data in Python/Pandas
```python
import pandas as pd

# Load the CSV
df = pd.read_csv('backend/data/sales_data_demo.csv')

# Convert date column
df['transaction_date'] = pd.to_datetime(df['transaction_date'])

# Basic analysis
print(df.describe())
print(df['product_category'].value_counts())
```

### Upload to Voxalize
1. Navigate to the Query Page
2. Connect to Pandas/Excel data source
3. Upload `sales_data_demo.csv`
4. Start querying with natural language

## Data Volume

- **5,000 transactions**
- **15 unique products** across 5 categories
- **5 regions** for geographic analysis
- **4 customer segments** for market segmentation
- **5 payment methods**
- **18 months** of historical data
- **15 columns** for comprehensive analysis

## Maintenance

### Regenerate Data
To regenerate with fresh data:
```bash
python -m utils.excel_populator
```
This will overwrite the existing CSV file.

### Verify Data Quality
```bash
python test_excel_data.py
```
This runs comprehensive checks and sample queries.

### Update Record Count
Edit `excel_populator.py`:
```python
NUM_RECORDS = 10000  # Change to desired number
```

## Integration with Voxalize

This CSV is designed to work seamlessly with:
- **Pandas Agent**: Natural language to Pandas queries
- **Visualization**: Automatic chart generation
- **Voice Queries**: Voice-to-query conversion
- **Excel Upload**: Direct file upload support

## Comparison with MongoDB Version

| Feature | MongoDB | Excel/CSV |
|---------|---------|-----------|
| Records | 5,000 | 5,000 |
| Fields/Columns | 16 | 15 |
| Data Source | NoSQL Database | File-based |
| Query Language | MongoDB queries | Pandas/SQL-like |
| Use Case | Database demos | File analysis demos |

Both datasets contain the same business logic and can be used interchangeably for demos.
