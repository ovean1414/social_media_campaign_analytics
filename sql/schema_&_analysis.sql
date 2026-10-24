
CREATE DATABASE IF NOT EXISTS social_media_analytics;

USE social_media_analytics;

CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id INT PRIMARY KEY,
    campaign_name VARCHAR(150) NOT NULL,
    platform VARCHAR(30) NOT NULL,
    campaign_type VARCHAR(40) NOT NULL,
    target_audience VARCHAR(120),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_budget DECIMAL(12,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS campaign_performance (
    performance_id INT PRIMARY KEY,
    campaign_id INT NOT NULL,
    report_date DATE NOT NULL,
    impressions INT NOT NULL,
    clicks INT NOT NULL,
    likes INT NOT NULL,
    comments INT NOT NULL,
    shares INT NOT NULL,
    conversions INT NOT NULL,
    ad_spend DECIMAL(12,2) NOT NULL,
    revenue DECIMAL(14,2) NOT NULL,

    CONSTRAINT fk_campaign
        FOREIGN KEY (campaign_id)
        REFERENCES campaigns(campaign_id),

    CONSTRAINT uq_campaign_date
        UNIQUE (campaign_id, report_date),

    INDEX idx_report_date (report_date)
);

CREATE TABLE IF NOT EXISTS forecast_results (
    forecast_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    forecast_date DATE NOT NULL,
    metric VARCHAR(30) NOT NULL,
    forecast_value DECIMAL(16,2) NOT NULL,
    model_name VARCHAR(80) NOT NULL,
    forecast_type VARCHAR(20) NOT NULL,
    actual_value DECIMAL(16,2) NULL
);

CREATE TABLE IF NOT EXISTS anomaly_results (
    anomaly_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    report_date DATE NOT NULL UNIQUE,
    revenue DECIMAL(14,2) NOT NULL,
    robust_z_score DECIMAL(10,3) NULL,
    is_anomaly BOOLEAN NOT NULL,
    anomaly_reason VARCHAR(150) NOT NULL
);

show tables;

SELECT COUNT(*) AS total_campaigns
FROM campaigns;

SELECT COUNT(*) AS total_performance_records
FROM campaign_performance;

SELECT MIN(report_date) AS first_date,
       MAX(report_date) AS last_date
FROM campaign_performance;

SELECT
    COUNT(*) AS total_records,
    SUM(impressions) AS total_impressions,
    SUM(clicks) AS total_clicks,
    SUM(conversions) AS total_conversions,
    ROUND(SUM(ad_spend), 2) AS total_ad_spend,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM campaign_performance;

SELECT
    c.platform,
    SUM(p.impressions) AS total_impressions,
    SUM(p.clicks) AS total_clicks,
    SUM(p.conversions) AS total_conversions,
    ROUND(SUM(p.ad_spend), 2) AS total_ad_spend,
    ROUND(SUM(p.revenue), 2) AS total_revenue,
    ROUND(
        100.0 * SUM(p.clicks) / NULLIF(SUM(p.impressions), 0),
        2
    ) AS ctr_percent,
    ROUND(
        100.0 * SUM(p.conversions) / NULLIF(SUM(p.clicks), 0),
        2
    ) AS conversion_rate_percent,
    ROUND(
        SUM(p.revenue) / NULLIF(SUM(p.ad_spend), 0),
        2
    ) AS roas
FROM campaigns c
JOIN campaign_performance p
    ON c.campaign_id = p.campaign_id
GROUP BY c.platform
ORDER BY roas DESC;

-- Rank campaigns by ROAS--

SELECT
    c.campaign_id,
    c.campaign_name,
    c.platform,
    ROUND(SUM(p.ad_spend), 2) AS total_ad_spend,
    ROUND(SUM(p.revenue), 2) AS total_revenue,
    ROUND(
        SUM(p.revenue) / NULLIF(SUM(p.ad_spend), 0),
        2
    ) AS roas
FROM campaigns c
JOIN campaign_performance p
    ON c.campaign_id = p.campaign_id
GROUP BY
    c.campaign_id,
    c.campaign_name,
    c.platform
ORDER BY roas DESC;

-- Find the monthly revenue trend--

SELECT
    DATE_FORMAT(report_date, '%Y-%m') AS report_month,
    ROUND(SUM(ad_spend), 2) AS monthly_ad_spend,
    ROUND(SUM(revenue), 2) AS monthly_revenue,
    SUM(conversions) AS monthly_conversions,
    ROUND(
        SUM(revenue) / NULLIF(SUM(ad_spend), 0),
        2
    ) AS monthly_roas
FROM campaign_performance
GROUP BY DATE_FORMAT(report_date, '%Y-%m')
ORDER BY report_month;

-- Identify the best campaign for conversions--

SELECT
    c.campaign_name,
    c.platform,
    SUM(p.clicks) AS total_clicks,
    SUM(p.conversions) AS total_conversions,
    ROUND(
        100.0 * SUM(p.conversions) / NULLIF(SUM(p.clicks), 0),
        2
    ) AS conversion_rate_percent
FROM campaigns c
JOIN campaign_performance p
    ON c.campaign_id = p.campaign_id
GROUP BY c.campaign_id, c.campaign_name, c.platform
ORDER BY conversion_rate_percent DESC;

-- Verfiy the monthly trend--
WITH monthly_revenue AS (
    SELECT
        DATE_FORMAT(report_date, '%Y-%m') AS report_month,
        SUM(revenue) AS revenue
    FROM campaign_performance
    GROUP BY DATE_FORMAT(report_date, '%Y-%m')
),
revenue_comparison AS (
    SELECT
        report_month,
        revenue,
        LAG(revenue) OVER (
            ORDER BY report_month
        ) AS previous_month_revenue
    FROM monthly_revenue
)
SELECT
    report_month,
    ROUND(revenue, 2) AS revenue,
    ROUND(previous_month_revenue, 2) AS previous_month_revenue,
    ROUND(
        100.0 * (revenue - previous_month_revenue)
        / NULLIF(previous_month_revenue, 0),
        2
    ) AS month_over_month_change_percent
FROM revenue_comparison
ORDER BY report_month;

