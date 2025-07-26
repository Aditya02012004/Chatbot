import pandas as pd
import os

# Path to data files
data_path = "../docker/data"

# Explore each CSV file
files = ['products.csv', 'orders.csv', 'order_items.csv', 'inventory_items.csv', 'users.csv', 'distribution_centers.csv']

for file in files:
    file_path = os.path.join(data_path, file)
    print(f"\n=== {file} ===")
    
    try:
        # Read first few rows to understand structure
        df = pd.read_csv(file_path, nrows=5)
        print(f"Columns: {list(df.columns)}")
        print(f"Shape: {df.shape}")
        print("First few rows:")
        print(df.head())
        print("-" * 50)
    except Exception as e:
        print(f"Error reading {file}: {e}")

# Check file sizes
print("\n=== File Sizes ===")
for file in files:
    file_path = os.path.join(data_path, file)
    if os.path.exists(file_path):
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        print(f"{file}: {size_mb:.1f} MB") 