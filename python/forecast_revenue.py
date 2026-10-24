
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
from getpass import getpass
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Connect to MySQL
username = input("MySQL username (default root): ").strip() or "root"
password = getpass("MySQL password: ")

connection = mysql.connector.connect(
    host="localhost",
    user=username,
    password=password,
    database="social_media_analytics"
)

# Read daily revenue from MySQL
query = """
SELECT report_date, revenue
FROM campaign_performance
ORDER BY report_date;
"""

df = pd.read_sql(query, connection)
connection.close()

# Convert daily data into monthly revenue
df["report_date"] = pd.to_datetime(df["report_date"])

monthly = (
    df.set_index("report_date")["revenue"]
    .resample("MS")
    .sum()
)

print("\nMonthly revenue:")
print(monthly.round(2))

# Plot historical revenue
plt.figure(figsize=(10, 5))
plt.plot(monthly.index, monthly.values, marker="o")
plt.title("Monthly Social Media Campaign Revenue")
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.grid(True)
plt.tight_layout()
plt.show()

# Forecast the next three months
model = ExponentialSmoothing(
    monthly,
    trend="add",
    seasonal=None,
    initialization_method="estimated"
)

fitted_model = model.fit()
forecast = fitted_model.forecast(3)

print("\nRevenue forecast for the next three months:")
print(forecast.round(2))

# Plot forecast
plt.figure(figsize=(10, 5))
plt.plot(monthly.index, monthly.values, marker="o", label="Historical revenue")
plt.plot(forecast.index, forecast.values, marker="o", linestyle="--",
         label="Forecast revenue")
plt.title("Monthly Revenue Forecast")
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
