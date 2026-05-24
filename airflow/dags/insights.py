import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# -----------------------------
# 1. LOAD DATA
# -----------------------------
DB_URI = "postgresql+psycopg2://airflow_user:airflow_pass@postgres:5432/airflow_db"

engine = create_engine(DB_URI)

df = pd.read_sql("SELECT * FROM mart.fact_economic", engine)

print("Data Loaded:", df.shape)


# -----------------------------
# 2. BASIC CLEANING
# -----------------------------
df = df.dropna(subset=['gdp_growth', 'inflation', 'unemployment'])



# -----------------------------
# 3. CORRELATION ANALYSIS
# -----------------------------
print("\n=== Correlation ===")
corr = df[['gdp_growth', 'inflation', 'unemployment']].corr()
print(corr)

sns.heatmap(corr, annot=True)
plt.title("Correlation Matrix")
plt.show()


# -----------------------------
# 4. INFLATION vs GROWTH
# -----------------------------
print("\n=== Inflation Impact ===")
inflation_impact = df.groupby('inflation_category')['gdp_growth'].mean()
print(inflation_impact)

inflation_impact.plot(kind='bar', title="GDP Growth by Inflation Category")
plt.show()


# -----------------------------
# 5. UNEMPLOYMENT IMPACT
# -----------------------------
print("\n=== Labor Market Impact ===")
labor_impact = df.groupby('labor_market_status')['gdp_growth'].mean()
print(labor_impact)

labor_impact.plot(kind='bar', title="GDP Growth by Labor Market Status")
plt.show()


# -----------------------------
# 6. STAGFLATION DETECTION
# -----------------------------
print("\n=== Stagflation Periods ===")
stagflation = df[
    (df['inflation_category'] == 'High') &
    (df['unemployment_category'] == 'High')
]

print(stagflation[['country', 'year', 'inflation', 'unemployment']])


# -----------------------------
# 7. GDP vs GDP PER CAPITA
# -----------------------------
print("\n=== Wealth Analysis ===")
top_gdp = df.sort_values('gdp', ascending=False).head(5)
top_per_capita = df.sort_values('gdp_per_capita', ascending=False).head(5)

print("\nTop by GDP:\n", top_gdp[['country', 'year', 'gdp']])
print("\nTop by Per Capita:\n", top_per_capita[['country', 'year', 'gdp_per_capita']])


# -----------------------------
# 8. POPULATION IMPACT
# -----------------------------
print("\n=== Population Impact ===")
pop_corr = df[['population', 'gdp_per_capita']].corr()
print(pop_corr)


# -----------------------------
# 9. ECONOMIC CONDITION DISTRIBUTION
# -----------------------------
print("\n=== Economic Condition ===")
condition_counts = df['economic_condition'].value_counts()
print(condition_counts)

condition_counts.plot(kind='bar', title="Economic Conditions Distribution")
plt.show()


# -----------------------------
# 10. BEST & WORST YEARS
# -----------------------------
print("\n=== Best Years ===")
print(df.sort_values('gdp_growth', ascending=False).head(5)[
    ['country', 'year', 'gdp_growth']
])

print("\n=== Worst Years ===")
print(df.sort_values('gdp_growth').head(5)[
    ['country', 'year', 'gdp_growth']
])