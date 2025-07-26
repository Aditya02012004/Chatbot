from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
from typing import List, Dict, Any

app = FastAPI(title="E-commerce Chatbot API", version="1.0.0")

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables to store loaded data
products_df = None
orders_df = None
order_items_df = None
inventory_df = None

@app.on_event("startup")
async def load_data():
    """Load CSV data on startup"""
    global products_df, orders_df, order_items_df, inventory_df
    
    data_path = "../docker/data"
    
    try:
        print("Loading CSV data...")
        products_df = pd.read_csv(os.path.join(data_path, "products.csv"))
        orders_df = pd.read_csv(os.path.join(data_path, "orders.csv"))
        order_items_df = pd.read_csv(os.path.join(data_path, "order_items.csv"))
        inventory_df = pd.read_csv(os.path.join(data_path, "inventory_items.csv"))
        print("Data loaded successfully!")
    except Exception as e:
        print(f"Error loading data: {e}")

@app.get("/")
def read_root():
    return {"message": "E-commerce Chatbot Backend is running."}

@app.get("/top-products")
def get_top_products(limit: int = 5) -> List[Dict[str, Any]]:
    """Get top selling products"""
    if order_items_df is None or products_df is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    # Count product sales
    product_sales = order_items_df.groupby('product_id').size().reset_index(name='sales_count')
    
    # Merge with product details
    top_products = product_sales.merge(products_df, left_on='product_id', right_on='id')
    top_products = top_products.sort_values('sales_count', ascending=False).head(limit)
    
    return top_products[['name', 'brand', 'category', 'sales_count']].to_dict('records')

@app.get("/order-status/{order_id}")
def get_order_status(order_id: int) -> Dict[str, Any]:
    """Get status of a specific order"""
    if orders_df is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    order = orders_df[orders_df['order_id'] == order_id]
    if order.empty:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    
    order_data = order.iloc[0].to_dict()
    return {
        "order_id": order_data['order_id'],
        "status": order_data['status'],
        "created_at": order_data['created_at'],
        "shipped_at": order_data['shipped_at'],
        "delivered_at": order_data['delivered_at'],
        "returned_at": order_data['returned_at']
    }

@app.get("/stock/{product_name}")
def get_product_stock(product_name: str) -> Dict[str, Any]:
    """Get stock count for a specific product"""
    if products_df is None or inventory_df is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    # Find product by name (case insensitive)
    product = products_df[products_df['name'].str.contains(product_name, case=False, na=False)]
    if product.empty:
        raise HTTPException(status_code=404, detail=f"Product '{product_name}' not found")
    
    product_id = product.iloc[0]['id']
    
    # Count inventory items for this product
    stock_count = len(inventory_df[inventory_df['product_id'] == product_id])
    
    return {
        "product_name": product.iloc[0]['name'],
        "brand": product.iloc[0]['brand'],
        "stock_count": stock_count
    }

@app.get("/chatbot/query")
def chatbot_query(query: str) -> Dict[str, Any]:
    """Process chatbot queries and return appropriate responses"""
    query_lower = query.lower()
    
    # Simple keyword matching for demo purposes
    if "top" in query_lower and ("product" in query_lower or "sold" in query_lower):
        products = get_top_products(5)
        return {
            "query": query,
            "response": f"Here are the top 5 most sold products:",
            "data": products
        }
    
    elif "order" in query_lower and "status" in query_lower:
        # Extract order ID from query (simple pattern matching)
        import re
        order_match = re.search(r'(\d+)', query)
        if order_match:
            order_id = int(order_match.group(1))
            try:
                order_status = get_order_status(order_id)
                return {
                    "query": query,
                    "response": f"Order {order_id} status: {order_status['status']}",
                    "data": order_status
                }
            except HTTPException as e:
                return {
                    "query": query,
                    "response": f"Order {order_id} not found.",
                    "data": None
                }
        else:
            return {
                "query": query,
                "response": "Please provide an order ID to check status.",
                "data": None
            }
    
    elif "stock" in query_lower or "left" in query_lower:
        # Extract product name from query
        import re
        # Simple extraction - look for words after "stock" or "left"
        words = query.split()
        for i, word in enumerate(words):
            if word.lower() in ["stock", "left", "inventory"] and i + 1 < len(words):
                product_name = words[i + 1]
                try:
                    stock_info = get_product_stock(product_name)
                    return {
                        "query": query,
                        "response": f"{stock_info['product_name']} has {stock_info['stock_count']} items in stock.",
                        "data": stock_info
                    }
                except HTTPException as e:
                    return {
                        "query": query,
                        "response": f"Product '{product_name}' not found.",
                        "data": None
                    }
        
        return {
            "query": query,
            "response": "Please specify which product you want to check stock for.",
            "data": None
        }
    
    else:
        return {
            "query": query,
            "response": "I can help you with:\n- Top selling products\n- Order status\n- Product stock levels\nPlease ask a specific question.",
            "data": None
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 