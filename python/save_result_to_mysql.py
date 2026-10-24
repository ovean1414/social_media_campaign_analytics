
import pandas as pd
import mysql.connector
from pathlib import Path
from getpass import getpass

ROOT = Path(__file__).resolve().parents[1]
INSIGHTS = ROOT / "insights"

# Read the anomaly analysis
anomalies = pd.read_csv(
    INSIGHTS / "daily_revenue_anomaly_results.csv",
    parse_dates=["report_date"]
)

# Connect to MySQL
username = input("MySQL username (default root): ").strip() or "root"
password = getpass("MySQL password: ")

connection = mysql.connector.connect(
    host="localhost",
    user=username,
    password=password,
    database="social_media_analytics"
)

cursor = connection.cursor()

try:
    # Save forecast values from the model again
    # so the database contains the same three-month forecast.
    # We will regenerate these values from the historical monthly data.
    cursor.execute("""
        DELETE FROM forecast_results
        WHERE metric = 'revenue'
          AND model_name = 'ExponentialSmoothing'
          AND forecast_type = 'forecast'
    """)

    # Rebuild the same monthly forecast
    from statsmodels.tsa.holtwinters import ExponentialSmoothing

    historical = pd.read_sql("""
        SELECT report_date, SUM(revenue) AS revenue
        FROM campaign_performance
        GROUP BY report_date
        ORDER BY report_date
    """, connection)

    historical["report_date"] = pd.to_datetime(
        historical["report_date"]
    )

    monthly = (
        historical.set_index("report_date")["revenue"]
        .resample("MS")
        .sum()
    )

    model = ExponentialSmoothing(
        monthly,
        trend="add",
        seasonal=None,
        initialization_method="estimated"
    ).fit()

    forecast = model.forecast(3)

    forecast_rows = [
        (
            forecast_date.date(),
            "revenue",
            round(float(value), 2),
            "ExponentialSmoothing",
            "forecast",
            None
        )
        for forecast_date, value in forecast.items()
    ]

    cursor.executemany("""
        INSERT INTO forecast_results
        (forecast_date, metric, forecast_value,
         model_name, forecast_type, actual_value)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, forecast_rows)

    # Replace the anomaly results with the latest analysis
    cursor.execute("DELETE FROM anomaly_results")

    anomaly_rows = [
        (
            row.report_date.date(),
            round(float(row.revenue), 2),
            round(float(row.robust_z_score), 3),
            bool(row.is_anomaly),
            row.anomaly_reason
        )
        for row in anomalies.itertuples(index=False)
    ]

    cursor.executemany("""
        INSERT INTO anomaly_results
        (report_date, revenue, robust_z_score,
         is_anomaly, anomaly_reason)
        VALUES (%s, %s, %s, %s, %s)
    """, anomaly_rows)

    connection.commit()

    print("Forecast and anomaly results saved successfully!")
    print("Forecast rows:", len(forecast_rows))
    print("Anomaly-analysis rows:", len(anomaly_rows))

except Exception as error:
    connection.rollback()
    print("Error:", error)

finally:
    cursor.close()
    connection.close()
