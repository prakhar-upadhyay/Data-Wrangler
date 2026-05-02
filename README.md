# Legacy Data Wrangler

[![Docker Build CI](https://github.com/[YOUR_GITHUB_USERNAME]/[YOUR_REPO_NAME]/actions/workflows/docker-build.yml/badge.svg)](https://github.com/[YOUR_GITHUB_USERNAME]/[YOUR_REPO_NAME]/actions/workflows/docker-build.yml)

## Overview
The Legacy Data Wrangler is a robust, containerized ETL (Extract, Transform, Load) pipeline built in Python. It is designed to ingest highly nested, poorly formatted JSON data from legacy systems, normalize the schema, and export a clean, standardized CSV ready for modern accounting software integration. 

Built with defensive programming principles, the pipeline gracefully handles schema inconsistencies, missing critical fields, and variable data types without crashing.

## Architecture & Technologies
* **Language:** Python 3.12 (with Type Hints and Docstrings)
* **Data Manipulation:** `pandas` for high-performance JSON flattening.
* **Containerization:** Docker (`python:3.12-slim` base image) for environment parity.
* **CI/CD:** GitHub Actions for automated Docker builds.
* **Design Pattern:** Modular pipeline with a thin orchestration `main()` function and distinct functional stages (`load_payload`, `normalize_employee`, `build_dataframe`, `write_outputs`).

## Key Features
* **Defensive Data Parsing:** Implements case-insensitive key lookups (e.g., `details` vs `Details`) and fallback mapping for renamed keys (e.g., mapping both `id` and `employee_id` to `id`).
* **Smart Type Coercion & Cleansing:**
  * **Roles:** Extracts the first element from unexpected lists, trims whitespace, and assigns "Unassigned" to null/missing values.
  * **Salaries:** Strips commas from strings and coerces invalid or negative values to null.
  * **Dates:** Enforces strict coercion to `YYYY-MM-DD` format, safely nulling out unparseable dates.
* **Dynamic Normalization:** Automatically flattens deeply nested JSON dictionaries into a flat, stable tabular format.
* **Production Logging:** Utilizes Python's structured `logging` module to generate timestamped server logs tracking extraction stages, input/output sources, and fatal error aborts.
* **Health Reporting:** Outputs a dedicated `cleaning_report.json` containing metrics on processed records, duplicate IDs, and missing data points.

---

## Prerequisites
To run this pipeline, you do not need Python installed on your host machine. You only need:
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/](https://github.com/)[YOUR_GITHUB_USERNAME]/[YOUR_REPO_NAME].git
   cd [YOUR_REPO_NAME]

2. **Build the Docker container:**
   ```bash
   docker build -t data-wrangler .


## Usage
The pipeline is designed to be executed via a simple Docker command. By default, the container will look for a data.json file in the working directory and execute the wrangling script.

Run the pipeline:

```bash
docker run -v "$(pwd):/app" data-wrangler-app
(Note: The -v "$(pwd):/app" flag mounts your current directory to the container, allowing the script to read your local data.json and write the final CSV back to your machine.)

## Expected Outputs

1. Upon successful execution, the pipeline generates the following in your directory:

2. cleaned_data.csv: The fully flattened and standardized data file, ready for downstream use.

3. cleaning_report.json: A diagnostic file containing metrics such as total rows processed and counts of missing identifiers.

Terminal Logs: Standardized INFO logs tracking the job's lifecycle in real-time.
