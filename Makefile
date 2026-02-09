.PHONY: help bootstrap terraform-init terraform-plan terraform-apply \
       deploy-functions deploy-dashboard run-local backfill lint test

PROJECT_ID := jobs-dashboard
REGION := us-central1

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'

bootstrap: ## One-time GCP project setup
	bash scripts/bootstrap.sh

terraform-init: ## Initialize Terraform
	cd terraform && terraform init

terraform-plan: ## Preview infrastructure changes
	cd terraform && terraform plan

terraform-apply: ## Apply infrastructure changes
	cd terraform && terraform apply

deploy-functions: ## Deploy Cloud Functions
	gcloud functions deploy ingest-fred \
		--gen2 --runtime=python312 --region=$(REGION) \
		--source=functions/ingest_fred --entry-point=ingest \
		--trigger-http --memory=512Mi --timeout=300s
	gcloud functions deploy transform-analytics \
		--gen2 --runtime=python312 --region=$(REGION) \
		--source=functions/transform --entry-point=transform \
		--trigger-http --memory=512Mi --timeout=300s

deploy-dashboard: ## Build and deploy dashboard to Cloud Run
	gcloud builds submit --config=cloudbuild.yaml .

run-local: ## Run Streamlit dashboard locally
	cd dashboard && streamlit run app.py --server.port=8501

backfill: ## Trigger historical data backfill
	bash scripts/backfill.sh

lint: ## Run linters
	cd functions/ingest_fred && python -m py_compile main.py
	cd functions/transform && python -m py_compile main.py
	cd dashboard && python -m py_compile app.py

test: ## Run tests
	python -m pytest tests/ -v
	python -m pytest functions/ingest_fred/ -v
	python -m pytest functions/transform/ -v
