
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
from getpass import getpass

# Connect to MySQL
username = input("MySQL username (default root): ").strip() or "root"
password = getpass("MySQL password: ")

connection = mysql.connector.connect(
    host="localhost",
    user=username,
    password=password,
    database="social_media_analytics"
)

# Get total daily revenue across all campaigns
query = """
SELECT
    report_date,
    SUM(revenue) AS revenue
FROM campaign_performance
GROUP BY report_date
ORDER BY report_date;
"""

df = pd.read_sql(query, connection)
connection.close()

# Calculate robust Z-scores using median absolute deviation
median_revenue = df["revenue"].median()
absolute_deviation = (df["revenue"] - median_revenue).abs()
mad = absolute_deviation.median()

if mad == 0:
    raise ValueError(
        "Median absolute deviation is zero; cannot calculate robust Z-scores."
    )

df["robust_z_score"] = (
    0.6745 * (df["revenue"] - median_revenue) / mad
)

# Flag unusually high or low revenue days
df["is_anomaly"] = df["robust_z_score"].abs() > 3.5

df["anomaly_reason"] = df["robust_z_score"].apply(
    lambda score:
        "Unusually high revenue" if score > 3.5
        else "Unusually low revenue" if score < -3.5
        else "Normal"
)

# Display results
anomalies = df[df["is_anomaly"]].copy()

print("\nTotal dates analyzed:", len(df))
print("Anomalies detected:", len(anomalies))

if anomalies.empty:
    print("No unusual revenue days detected.")
else:
    print(anomalies[
        ["report_date", "revenue", "robust_z_score", "anomaly_reason"]
    ].to_string(index=False))

# Plot daily revenue and flagged dates
plt.figure(figsize=(12, 5))
plt.plot(df["report_date"], df["revenue"], label="Daily revenue")

if not anomalies.empty:
    plt.scatter(
        anomalies["report_date"],
        anomalies["revenue"],
        label="Detected anomalies",
        marker="o"
    )

plt.title("Daily Revenue Anomaly Detection")
plt.xlabel("Date")
plt.ylabel("Revenue")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(
    "insights/daily_revenue_anomalies.png",
    dpi=150,
    bbox_inches="tight"
)
plt.show()

# Export analysis results
df.to_csv("insights/daily_revenue_anomaly_results.csv", index=False)

print("\nSaved chart and results in the insights folder.")
  