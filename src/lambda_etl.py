import boto3
import pandas as pd
import awswrangler as wr

def lambda_handler(event, context):
    # CONFIGURATION
    BUCKET_NAME = "datalake-online-retail-2026" 
    INPUT_KEY = "raw/online_retail.csv"
    OUTPUT_PATH = f"s3://{BUCKET_NAME}/processed/"
    
    print("Starting ETL Job...")
    
    try:
        # 1. READ: Load CSV from S3 (using ISO-8859-1 for special chars)
        df = wr.s3.read_csv(f"s3://{BUCKET_NAME}/{INPUT_KEY}", encoding="ISO-8859-1")
        print(f"Read {len(df)} rows from Raw.")

        # 2. TRANSFORM: Cleaning Data
        # Drop rows with missing CustomerID
        df = df.dropna(subset=['CustomerID'])
        
        # Remove Returns (Negative Quantity) & Adjustments (Negative Price)
        df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
        
        # Fix Date Format
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
        
        # Add Business Metric: TotalAmount
        df['TotalAmount'] = df['Quantity'] * df['UnitPrice']
        
        # Clean CustomerID (Float -> Integer)
        df['CustomerID'] = df['CustomerID'].astype(int)
        
        print(f"Data Cleaned. {len(df)} rows remain.")
        
        # 3. LOAD: Write to Parquet (Partitioned by Country)
        wr.s3.to_parquet(
            df=df,
            path=OUTPUT_PATH,
            dataset=True,
            mode="overwrite",
            partition_cols=["Country"]  # Optimizes Athena costs
        )
        
        print(f"Success! Data written to {OUTPUT_PATH}")
        return {'statusCode': 200, 'body': 'ETL Complete'}
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {'statusCode': 500, 'body': str(e)}