resource "google_bigquery_dataset" "labor_market" {
  dataset_id  = "labor_market"
  description = "Labor market data sourced from FRED / BLS"
  location    = var.bq_location
  project     = var.project_id

  depends_on = [google_project_service.apis["bigquery.googleapis.com"]]
}

resource "google_bigquery_table" "raw_fred_observations" {
  dataset_id          = google_bigquery_dataset.labor_market.dataset_id
  table_id            = "raw_fred_observations"
  project             = var.project_id
  deletion_protection = false

  time_partitioning {
    type  = "MONTH"
    field = "observation_date"
  }

  clustering = ["series_id"]

  schema = jsonencode([
    { name = "series_id", type = "STRING", mode = "REQUIRED", description = "FRED series identifier" },
    { name = "observation_date", type = "DATE", mode = "REQUIRED", description = "Date of observation" },
    { name = "value", type = "FLOAT64", mode = "NULLABLE", description = "Observed value" },
    { name = "realtime_start", type = "DATE", mode = "NULLABLE", description = "FRED real-time period start" },
    { name = "realtime_end", type = "DATE", mode = "NULLABLE", description = "FRED real-time period end" },
    { name = "ingested_at", type = "TIMESTAMP", mode = "REQUIRED", description = "Ingestion timestamp" },
  ])
}

resource "google_bigquery_table" "analytics_monthly" {
  dataset_id          = google_bigquery_dataset.labor_market.dataset_id
  table_id            = "analytics_monthly"
  project             = var.project_id
  deletion_protection = false

  time_partitioning {
    type  = "MONTH"
    field = "observation_date"
  }

  clustering = ["series_id"]

  schema = jsonencode([
    { name = "series_id", type = "STRING", mode = "REQUIRED" },
    { name = "observation_date", type = "DATE", mode = "REQUIRED" },
    { name = "value", type = "FLOAT64", mode = "NULLABLE" },
    { name = "mom_change", type = "FLOAT64", mode = "NULLABLE", description = "Month-over-month change" },
    { name = "mom_pct_change", type = "FLOAT64", mode = "NULLABLE", description = "Month-over-month % change" },
    { name = "yoy_change", type = "FLOAT64", mode = "NULLABLE", description = "Year-over-year change" },
    { name = "yoy_pct_change", type = "FLOAT64", mode = "NULLABLE", description = "Year-over-year % change" },
    { name = "ma_3m", type = "FLOAT64", mode = "NULLABLE", description = "3-month moving average" },
    { name = "ma_12m", type = "FLOAT64", mode = "NULLABLE", description = "12-month moving average" },
    { name = "z_score_5y", type = "FLOAT64", mode = "NULLABLE", description = "Z-score vs trailing 5-year window" },
  ])
}

resource "google_bigquery_table" "series_metadata" {
  dataset_id          = google_bigquery_dataset.labor_market.dataset_id
  table_id            = "series_metadata"
  project             = var.project_id
  deletion_protection = false

  schema = jsonencode([
    { name = "series_id", type = "STRING", mode = "REQUIRED" },
    { name = "display_name", type = "STRING", mode = "REQUIRED" },
    { name = "description", type = "STRING", mode = "NULLABLE" },
    { name = "source", type = "STRING", mode = "NULLABLE" },
    { name = "frequency", type = "STRING", mode = "NULLABLE" },
    { name = "units", type = "STRING", mode = "NULLABLE" },
    { name = "category", type = "STRING", mode = "NULLABLE" },
  ])
}
