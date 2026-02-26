# 🛍️ Serverless Retail Data Lake & Executive Dashboard
This project is an end-to-end, serverless Data Lake built on AWS, designed to process and analyze global retail transaction data. Engineered with a business-first mindset, the architecture focuses on resource optimization, automated data quality checks, and delivering actionable executive insights. 

Raw CSV sales data is automatically ingested, cleaned, partitioned by country, and converted to a cost-effective columnar format (Parquet). The data is then queried using serverless SQL and visualized in a custom-built, interactive Python web application.

**🔴 Live Deployment:** <a href="https://data-lake-dashboard.onrender.com">Data Lake Dashboard</a>

## 🔗 Table of Contents
- [Architecture](#architecture)
- [Key Features & Business Impact](#key-features--business-impact)
- [Dashboard](#dashboard)
- [Tech Stack](#tech-stack)
- [How to Run Locally](#how-to-run-locally)

## ☁️ Architecture
<img src="architecture/aws serverless data lake architecture.png" alt="architecture diagram" width="820">


**The Pipeline:**
1. **Ingestion:** Raw CSV files are uploaded to an **Amazon S3** Raw Bucket.
2. **ETL Processing:** An **AWS Lambda** function (Python/Pandas) is triggered automatically to drop nulls, handle encoding anomalies (UTF-8 BOM), and convert the data.
3. **Storage:** The cleaned data is written to an **Amazon S3** Processed Bucket in Parquet format, partitioned by country.
4. **Data Cataloging:** **AWS Glue Crawler** infers the schema and updates the Glue Data Catalog.
5. **Analytics:** **Amazon Athena** executes standard SQL queries directly against the S3 data layer.
6. **Visualization:** A **Plotly Dash** application fetches live data via Boto3/AWS Wrangler to display business KPIs.


## 💡 Key Features & Business Impact
* **Cost Optimization:** Reduced Athena query scanning costs by implementing AWS best practices (Parquet columnar storage and S3 folder partitioning).
* **Automated Data Quality:** Lambda ETL script automatically cleans dirty data, while specific SQL validation queries ensure the pipeline's logic health (e.g., catching impossible negative sales values).
* **Real-World Problem Solving:** Successfully identified and resolved a hidden UTF-8 Byte Order Mark (BOM) encoding issue during the ingestion phase that was causing schema mismatch errors in Athena.
* **Executive Visibility:** Built an interactive Dash application that calculates and visualizes Total Revenue, Average Order Value (AOV), and Peak Shopping Hours by region.


## 📊 Dashboard
Here is a live view of the executive dashboard visualizing the data from Athena:
<img src="images/dashboard 1.png" alt="dashboard" width="820">
<img src="images/dashboard 2.png" alt="dashboard graphs" width="820">
<img src="images/dashboard 3.png" alt="dashboard graphs" width="820">

## 🛠️ Tech Stack
* **Cloud Infrastructure:** AWS (S3, Lambda, Glue, Athena, IAM)
* **Data Engineering:** Python, Pandas, ETL Pipelines, Parquet, Data Partitioning
* **Database & Analytics:** SQL, Time-Series Analysis, Unit Economics (AOV, CLV)
* **Frontend/Visualization:** Plotly Dash, HTML/CSS (Tailwind)
* **Deployment:** Render


## 🚀 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/luyandazuma/aws-online-retail-datalake.git]
   cd aws-online-retail-datalake 
   python src/dashboard.py