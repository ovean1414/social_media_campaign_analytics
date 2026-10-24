
import pandas as pd
import mysql.connector
from pathlib import Path
from getpass import getpass

# Find project folders
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

# Read CSV files
campaigns = pd.read_csv(
    RAW / "campaigns.csv",
    parse_dates=["start_date", "end_date"]
)

performance = pd.read_csv(
    RAW / "campaign_performance.csv",
    parse_dates=["report_date"]
)

# Connect to MySQL
username = input("MySQL username (press Enter for root): ").strip()
if not username:
    username = "root"

password = getpass("Enter your MySQL password: ")

connection = None

try:
    connection = mysql.connector.connect(
        host="localhost",
        user=username,
        password=password,
        database="social_media_analytics"
    )
    print("Connected server:", connection.server_host)
    print("Connected port:", connection.server_port)
    print("Connected database:", connection.database)
    cursor = connection.cursor()

    # Prepare campaign records
    campaign_rows = [
        (
            int(row.campaign_id),
            row.campaign_name,
            row.platform,
            row.campaign_type,
            row.target_audience,
            row.start_date.date(),
            row.end_date.date(),
            float(row.total_budget)
        )
        for row in campaigns.itertuples(index=False)
    ]

    # Prepare daily performance records
    performance_rows = [
        (
            int(row.performance_id),
            int(row.campaign_id),
            row.report_date.date(),
            int(row.impressions),
            int(row.clicks),
            int(row.likes),
            int(row.comments),
            int(row.shares),
            int(row.conversions),
            float(row.ad_spend),
            float(row.revenue)
        )
        for row in performance.itertuples(index=False)
    ]

    # Replace existing rows in these project tables.
    # Delete performance first because it references campaigns.
    cursor.execute("DELETE FROM campaign_performance")
    cursor.execute("DELETE FROM campaigns")

    campaign_sql = """
        INSERT INTO campaigns (
            campaign_id, campaign_name, platform, campaign_type,
            target_audience, start_date, end_date, total_budget
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    performance_sql = """
        INSERT INTO campaign_performance (
            performance_id, campaign_id, report_date, impressions,
            clicks, likes, comments, shares, conversions,
            ad_spend, revenue
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.executemany(campaign_sql, campaign_rows)
    cursor.executemany(performance_sql, performance_rows)

    connection.commit()

    print("\nData loaded successfully!")
    print("Campaigns loaded:", len(campaign_rows))
    print("Performance records loaded:", len(performance_rows))

except Exception as error:
    if connection and connection.is_connected():
        connection.rollback()
    print("\nSomething went wrong:", error)

finally:
    if connection and connection.is_connected():
        cursor.close()
        connection.close()
