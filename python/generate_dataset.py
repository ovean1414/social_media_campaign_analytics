
import pandas as pd
import numpy as np
from pathlib import Path

# Project folders
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

np.random.seed(42)

# Campaign details
campaigns = pd.DataFrame([
    [101, "Summer Style Awareness", "Instagram", "Awareness", 32000],
    [102, "B2B Lead Generation", "LinkedIn", "Lead Generation", 48000],
    [103, "Weekend Food Offers", "Facebook", "Conversions", 36000],
    [104, "Product Launch Buzz", "X", "Engagement", 26000],
    [105, "Website Visitor Retargeting", "Instagram", "Conversions", 42000],
    [106, "Small Business Solutions", "LinkedIn", "Traffic", 39000],
    [107, "Loyalty Rewards", "Facebook", "Retention", 30000],
    [108, "Brand Conversation", "X", "Awareness", 22000]
], columns=[
    "campaign_id", "campaign_name", "platform",
    "campaign_type", "total_budget"
])

campaigns["target_audience"] = [
    "Young adults 18-30",
    "Business decision-makers",
    "Food lovers 21-45",
    "Technology enthusiasts",
    "Recent website visitors",
    "Small business owners",
    "Existing customers",
    "Social media followers"
]

campaigns["start_date"] = "2025-01-01"
campaigns["end_date"] = "2025-12-31"

campaigns = campaigns[
    ["campaign_id", "campaign_name", "platform",
     "campaign_type", "target_audience", "start_date",
     "end_date", "total_budget"]
]

campaigns.to_csv(RAW / "campaigns.csv", index=False)

# Daily performance data
dates = pd.date_range("2025-01-01", "2025-12-31")
platform_ctr = {
    "Instagram": 0.034,
    "LinkedIn": 0.022,
    "Facebook": 0.029,
    "X": 0.025
}
platform_cvr = {
    "Instagram": 0.047,
    "LinkedIn": 0.061,
    "Facebook": 0.043,
    "X": 0.028
}

records = []
performance_id = 1

for campaign in campaigns.itertuples(index=False):
    for day in dates:
        weekend_factor = 1.15 if day.dayofweek >= 5 else 0.95
        seasonal_factor = (
            1 + 0.12 * np.sin(2 * np.pi * day.dayofyear / 365)
        )

        spend = max(
            15,
            (campaign.total_budget / 365)
            * weekend_factor
            * np.random.uniform(0.8, 1.2)
        )

        impressions = int(
            spend * np.random.uniform(95, 145)
            * seasonal_factor
        )

        clicks = min(
            impressions,
            int(impressions * platform_ctr[campaign.platform]
                * np.random.uniform(0.8, 1.2))
        )

        engagements = int(
            impressions * np.random.uniform(0.03, 0.08)
        )
        likes = int(engagements * 0.78)
        comments = int(engagements * 0.10)
        shares = max(0, engagements - likes - comments)

        conversions = int(
            clicks * platform_cvr[campaign.platform]
            * np.random.uniform(0.8, 1.2)
        )

        revenue_per_conversion = {
            "Instagram": 82,
            "LinkedIn": 155,
            "Facebook": 68,
            "X": 55
        }[campaign.platform]

        revenue = round(
            conversions * revenue_per_conversion
            * np.random.uniform(0.8, 1.2), 2
        )

        records.append([
            performance_id,
            campaign.campaign_id,
            day.date(),
            impressions,
            clicks,
            likes,
            comments,
            shares,
            conversions,
            round(spend, 2),
            revenue
        ])

        performance_id += 1

performance = pd.DataFrame(records, columns=[
    "performance_id", "campaign_id", "report_date",
    "impressions", "clicks", "likes", "comments",
    "shares", "conversions", "ad_spend", "revenue"
])

performance.to_csv(
    RAW / "campaign_performance.csv", index=False
)

print("Dataset created successfully!")
print("Campaigns:", len(campaigns))
print("Daily performance records:", len(performance))
print("Files saved in:", RAW)
