-- Analytics monthly table (managed by Terraform, this file is for reference).
CREATE TABLE IF NOT EXISTS `jobs-dashboard.labor_market.analytics_monthly` (
    series_id        STRING    NOT NULL,
    observation_date DATE      NOT NULL,
    value            FLOAT64,
    mom_change       FLOAT64,
    mom_pct_change   FLOAT64,
    yoy_change       FLOAT64,
    yoy_pct_change   FLOAT64,
    ma_3m            FLOAT64,
    ma_12m           FLOAT64,
    z_score_5y       FLOAT64
)
PARTITION BY DATE_TRUNC(observation_date, MONTH)
CLUSTER BY series_id;
