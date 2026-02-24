import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import awswrangler as wr
import pandas as pd
import boto3

# --- AWS CONFIGURATION ---
BUCKET_NAME = "datalake-online-retail-2026"
GLUE_DATABASE = "retail-db"
GLUE_TABLE = "clean-processed"
S3_OUTPUT = f"s3://{BUCKET_NAME}/athena-results/"

boto3.setup_default_session(region_name="af-south-1")

# --- INITIALIZE APP (TAILWIND CDN) ---
external_scripts = ['https://cdn.tailwindcss.com']
app = dash.Dash(__name__, external_scripts=external_scripts)
app.title = "Online Retail Dashboard"

# --- PLOTLY CHART COLORS ---
DARK_BLUE = "#1976d2"      # tailwind blue-700
LIGHT_BLUE = "#3b82f6"     # tailwind blue-500
ORANGE_ORANGE = "#f97316"  # tailwind orange-500
DARK_ORANGE = "#c2410c"    # tailwind orange-700

# --- HELPER FUNCTION ---
def run_query(query):
    try:
        df = wr.athena.read_sql_query(
            sql=query,
            database=GLUE_DATABASE,
            s3_output=S3_OUTPUT,
            ctas_approach=False
        )
        return df
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()

# --- LAYOUT ---
# min-h-screen ensures the background covers the whole page, bg-sky-50 is the pale blue
app.layout = html.Div(className="min-h-screen bg-sky-50 p-4 md:p-8 font-sans text-slate-800", children=[
    
    # 1. Header
    html.Div(className="bg-white rounded-xl shadow-md p-8 mb-8 border-b-4 border-blue-500", children=[
        html.H1("Global Retail Analytics Dashboard", className="text-4xl font-extrabold text-blue-900 mb-2"),
        html.P("Real-time insights from Serverless Data Lake (S3 + Athena)", className="text-lg text-orange-500 font-medium"),
    ]),

    # 2. Global Filters
    html.Div(className="mb-8 max-w-sm", children=[
        html.Label("Filter by Country:", className="block text-sm font-bold text-blue-900 mb-2"),
        dcc.Dropdown(
            id='country-dropdown',
            options=[
                {'label': 'United Kingdom', 'value': 'United Kingdom'},
                {'label': 'France', 'value': 'France'},
                {'label': 'Germany', 'value': 'Germany'},
                {'label': 'EIRE', 'value': 'EIRE'},
                {'label': 'Norway', 'value': 'Norway'}
            ],
            value='United Kingdom',
            clearable=False,
            className="text-slate-700"
        ),
    ]),

    # 3. KPI Row (CSS Grid: 1 column on mobile, 4 on desktop)
    html.Div(className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8", children=[
        html.Div(className="bg-white rounded-xl shadow-md p-6 border border-slate-100 flex flex-col items-center justify-center", children=[
            html.H3(id='kpi-revenue', className="text-3xl font-bold text-blue-500 mb-1"),
            html.P("Total Revenue", className="text-sm font-semibold text-slate-500 uppercase tracking-wider")
        ]),

        html.Div(className="bg-white rounded-xl shadow-md p-6 border border-slate-100 flex flex-col items-center justify-center", children=[
            html.H3(id='kpi-orders', className="text-3xl font-bold text-orange-500 mb-1"),
            html.P("Total Orders", className="text-sm font-semibold text-slate-500 uppercase tracking-wider")
        ]),

        html.Div(className="bg-white rounded-xl shadow-md p-6 border border-slate-100 flex flex-col items-center justify-center", children=[
            html.H3(id='kpi-aov', className="text-3xl font-bold text-blue-900 mb-1"),
            html.P("Avg Order Value", className="text-sm font-semibold text-slate-500 uppercase tracking-wider")
        ]),

        html.Div(className="bg-white rounded-xl shadow-md p-6 border border-slate-100 flex flex-col items-center justify-center", children=[
            html.H3(id='kpi-customers', className="text-3xl font-bold text-orange-700 mb-1"),
            html.P("Active Customers", className="text-sm font-semibold text-slate-500 uppercase tracking-wider")
        ]),
    ]),

    # 4. Charts Row 1
    html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8", children=[
        html.Div(className="bg-white rounded-xl shadow-md p-4 border border-slate-100", children=[
            dcc.Graph(id='product-bar-chart')
        ]),
        
        html.Div(className="bg-white rounded-xl shadow-md p-4 border border-slate-100", children=[
            dcc.Graph(id='hourly-trend-chart')
        ]),
    ]),

    # 5. Charts Row 2
    html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-6 pb-12", children=[
        html.Div(className="bg-white rounded-xl shadow-md p-4 border border-slate-100", children=[
            dcc.Graph(id='country-revenue-chart')
        ]),

        html.Div(className="bg-white rounded-xl shadow-md p-4 border border-slate-100", children=[
             dcc.Graph(id='monthly-trend-chart')
        ]),
    ])
])

# --- CALLBACKS ---
@app.callback(
    [Output('kpi-revenue', 'children'),
     Output('kpi-orders', 'children'),
     Output('kpi-aov', 'children'),
     Output('kpi-customers', 'children'),
     Output('product-bar-chart', 'figure'),
     Output('hourly-trend-chart', 'figure'),
     Output('country-revenue-chart', 'figure'),
     Output('monthly-trend-chart', 'figure')],
    [Input('country-dropdown', 'value')]
)
def update_dashboard(selected_country):
    print(f"Fetching data for {selected_country}...")

    # --- 1. KPI Query ---
    kpi_sql = f"""
        SELECT 
            SUM(totalamount) as total_rev,
            COUNT(DISTINCT "ï»¿invoiceno") as total_orders,
            COUNT(DISTINCT customerid) as total_customers,
            AVG(totalamount) as avg_order
        FROM "{GLUE_TABLE}"
        WHERE country = '{selected_country}'
    """
    df_kpi = run_query(kpi_sql)
    
    if not df_kpi.empty:
        rev = f"£{df_kpi['total_rev'][0]:,.0f}"
        orders = f"{df_kpi['total_orders'][0]:,}"
        aov = f"£{df_kpi['total_rev'][0] / df_kpi['total_orders'][0]:,.2f}"
        cust = f"{df_kpi['total_customers'][0]:,}"
    else:
        rev, orders, aov, cust = "£0", "0", "0", "0"

    # --- 2. Top Products (Bar Chart - Styled Blue) ---
    prod_sql = f"""
        SELECT description, SUM(quantity) as quantity
        FROM "{GLUE_TABLE}"
        WHERE country = '{selected_country}'
        GROUP BY description
        ORDER BY quantity DESC
        LIMIT 10
    """
    df_prod = run_query(prod_sql)
    fig_prod = px.bar(df_prod, x='quantity', y='description', orientation='h', 
                      title=f"Top 10 Products in {selected_country}", 
                      color_discrete_sequence=[LIGHT_BLUE])
    fig_prod.update_layout(yaxis={'categoryorder':'total ascending'}, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=50, l=10, r=10, b=10))

    # --- 3. Hourly Trend (Line Chart - Styled Orange) ---
    hour_sql = f"""
        SELECT extract(hour from invoicedate) as hour, count(distinct "ï»¿invoiceno") as orders
        FROM "{GLUE_TABLE}"
        WHERE country = '{selected_country}'
        GROUP BY 1
        ORDER BY 1
    """
    df_hour = run_query(hour_sql)
    fig_hour = px.line(df_hour, x='hour', y='orders', markers=True, 
                       title=f"Peak Shopping Hours in {selected_country}",
                       color_discrete_sequence=[ORANGE_ORANGE])
    fig_hour.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=50, l=10, r=10, b=10))

    # --- 4. Global Country Comparison (Pie Chart - Mixed Blue/Orange) ---
    country_sql = f"""
        SELECT country, SUM(totalamount) as revenue
        FROM "{GLUE_TABLE}"
        GROUP BY country
        ORDER BY revenue DESC
        LIMIT 10
    """
    df_country = run_query(country_sql)
    pie_colors = [DARK_BLUE, ORANGE_ORANGE, LIGHT_BLUE, DARK_ORANGE, '#60a5fa', '#fb923c', '#2563eb', '#ea580c', '#93c5fd', '#9a3412']
    
    fig_country = px.pie(df_country, names='country', values='revenue', 
                         title="Global Revenue Share (Top 10 Markets)", hole=0.4,
                         color_discrete_sequence=pie_colors)
    fig_country.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=50, l=10, r=10, b=10))

    # --- 5. Monthly Trend (Area Chart - Styled Light Blue) ---
    date_sql = f"""
        SELECT date_trunc('month', invoicedate) as month, SUM(totalamount) as revenue
        FROM "{GLUE_TABLE}"
        WHERE country = '{selected_country}'
        GROUP BY 1
        ORDER BY 1
    """
    df_date = run_query(date_sql)
    fig_date = px.area(df_date, x='month', y='revenue', 
                       title=f"Monthly Revenue Growth in {selected_country}",
                       color_discrete_sequence=[LIGHT_BLUE])
    fig_date.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=50, l=10, r=10, b=10))

    return rev, orders, aov, cust, fig_prod, fig_hour, fig_country, fig_date

# --- RUN ---
if __name__ == '__main__':
    app.run(debug=True, port=8050)