-- Raw FRED observations table (managed by Terraform, this file is for reference).
CREATE TABLE IF NOT EXISTS `jobs-dashboard.labor_market.raw_fred_observations` (
    series_id        STRING    NOT NULL,
    observation_date DATE      NOT NULL,
    value            FLOAT64,
    realtime_start   DATE,
    realtime_end     DATE,
    ingested_at      TIMESTAMP NOT NULL
)
PARTITION BY DATE_TRUNC(observation_date, MONTH)
CLUSTER BY series_id;
