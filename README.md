# U.S. Labor Market Dashboard

A GCP-based data pipeline and public web dashboard that ingests labor market data from the [FRED API](https://fred.stlouisfed.org/) (Bureau of Labor Statistics series), stores it in BigQuery, and visualizes key employment metrics via a Streamlit app on Cloud Run.

## Architecture

```
Cloud Scheduler ──▶ Cloud Functions (ingest) ──▶ BigQuery (raw)
       │                                              │
       └──▶ Cloud Functions (transform) ◀─────────────┘
                      │
                      ▼
               BigQuery (analytics)
                      │
                      ▼
               Cloud Run (Streamlit)  ◀── Cloud Build (CI/CD on push)
```

### Components

| Component | Service | Purpose |
|-----------|---------|---------|
| **Data Ingestion** | Cloud Functions (2nd gen) | Fetches observations from FRED API, upserts into BigQuery |
| **Analytics Transform** | Cloud Functions (2nd gen) | Computes MoM/YoY changes, moving averages, z-scores |
| **Data Warehouse** | BigQuery | Raw observations + analytics tables, partitioned by date |
| **Dashboard** | Cloud Run (Streamlit) | Public-facing interactive charts and KPI scorecards |
| **Scheduling** | Cloud Scheduler | Monthly (after BLS release) + weekly (jobless claims) |
| **CI/CD** | Cloud Build | Auto-deploy dashboard and functions on push to `main` |
| **Container Registry** | Artifact Registry | Docker images for the dashboard |
| **Secrets** | Secret Manager | FRED API key storage |
| **IaC** | Terraform | All infrastructure defined as code |

## Tracked Series

| Series ID | Indicator | Frequency | Source |
|-----------|-----------|-----------|--------|
| `PAYEMS` | Total Nonfarm Payrolls | Monthly | BLS/CES |
| `UNRATE` | Unemployment Rate (U-3) | Monthly | BLS/CPS |
| `CIVPART` | Labor Force Participation Rate | Monthly | BLS/CPS |
| `CES0500000003` | Average Hourly Earnings (Private) | Monthly | BLS/CES |
| `JTSJOL` | Job Openings (JOLTS) | Monthly | BLS/JOLTS |
| `ICSA` | Initial Jobless Claims | Weekly | DOL/ETA |
| `U6RATE` | U-6 Underemployment Rate | Monthly | BLS/CPS |
| `EMRATIO` | Employment-Population Ratio | Monthly | BLS/CPS |

## Dashboard Pages

1. **Overview** — KPI scorecard for all indicators + z-score pulse chart
2. **Employment** — Nonfarm payrolls (level + monthly change), participation rate, emp-pop ratio
3. **Unemployment** — U-3 rate, U-3 vs U-6 comparison, spread analysis
4. **Wages** — Average hourly earnings level and year-over-year growth
5. **Job Openings** — JOLTS openings trend and Beveridge curve (openings vs unemployment)
6. **Claims** — Weekly initial claims with 4-week moving average, year-over-year overlay

## Setup

### Prerequisites

- GCP project with billing enabled
- `gcloud` CLI authenticated
- Terraform >= 1.5
- A free [FRED API key](https://fred.stlouisfed.org/docs/api/api_key.html)

### 1. Bootstrap the GCP project

```bash
# Enable APIs and create Terraform state bucket
bash scripts/bootstrap.sh
```

### 2. Store the FRED API key

```bash
echo -n 'YOUR_FRED_API_KEY' | gcloud secrets versions add fred-api-key --data-file=-
```

### 3. Deploy infrastructure

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars  # edit if needed
terraform init
terraform apply
```

### 4. Initial data backfill

```bash
bash scripts/backfill.sh
```

### 5. Connect GitHub for CI/CD

In the GCP Console, connect your GitHub repository to Cloud Build via **Cloud Build > Triggers**. The Terraform-defined triggers will auto-deploy:
- **Dashboard** on changes to `dashboard/` or `cloudbuild.yaml`
- **Functions** on changes to `functions/` or `cloudbuild-functions.yaml`

## Local Development

```bash
# Run the Streamlit dashboard locally (requires BQ credentials)
make run-local

# Lint function code
make lint
```

## Refresh Schedule

| Trigger | Schedule (ET) | Target |
|---------|--------------|--------|
| Monthly ingestion | Saturday 6 AM, week after first Friday | All 8 series |
| Weekly ingestion | Thursday 12 PM | ICSA (jobless claims) |
| Monthly transform | Saturday 6:30 AM, week after first Friday | Analytics rebuild |
| Weekly transform | Thursday 12:30 PM | Analytics rebuild |

## Project Structure

```
├── cloudbuild.yaml              # CI/CD: dashboard build + deploy
├── cloudbuild-functions.yaml    # CI/CD: Cloud Functions deploy
├── Makefile                     # Dev convenience targets
├── dashboard/                   # Streamlit app (Cloud Run)
│   ├── Dockerfile
│   ├── app.py                   # Entry point
│   ├── pages/                   # Dashboard pages (01-06)
│   ├── components/              # Charts, metrics, data loader, filters
│   └── utils/                   # BQ client, constants, formatting
├── functions/                   # Cloud Functions
│   ├── ingest_fred/             # FRED API → BigQuery raw
│   └── transform/               # Raw → analytics (SQL transforms)
├── sql/                         # Reference DDL and seed data
│   ├── schema/
│   └── seed/
├── scripts/                     # Bootstrap and backfill helpers
└── terraform/                   # All GCP infrastructure as code
```

## Cost Estimate

At low traffic volumes, this project fits well within GCP free tiers:

- **Cloud Functions**: ~10 invocations/month (free tier: 2M/month)
- **Cloud Scheduler**: 4 jobs (free tier: 3 per account + minimal cost)
- **BigQuery**: < 1 GB storage, minimal queries (~$0/month)
- **Cloud Run**: Scale-to-zero; charges only during active requests ($0-2/month)
- **Estimated total**: **$0-5/month**

## License

GPL-3.0 — see [LICENSE](LICENSE).
