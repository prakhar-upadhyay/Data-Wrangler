# Legacy Data Wrangler

[![Docker Build CI](https://github.com/prakhar-upadhyay/Data-Wrangler/actions/workflows/docker-build.yml/badge.svg)](https://github.com/prakhar-upadhyay/Data-Wrangler/actions/workflows/docker-build.yml)

## Overview
The Legacy Data Wrangler is a robust, containerized ETL (Extract, Transform, Load) pipeline built in Python. It is designed to ingest highly nested, poorly formatted JSON data from legacy systems, normalize the schema, handle inconsistencies (such as missing values and mixed data types), and output a clean, standardized CSV ready for modern accounting software integration.

## Architecture & Technologies
* **Language:** Python 3.x
* **Data Manipulation:** `pandas` for high-performance JSON flattening and dataframe transformations.
* **Containerization:** Docker (ensuring environment parity across all client deployments).
* **CI/CD:** GitHub Actions for automated Docker builds.

## Key Features
* **Dynamic Normalization:** Automatically flattens deeply nested JSON dictionaries into a flat, tabular format.
* **Data Imputation:** Gracefully handles missing keys (e.g., dynamically assigning 'Unassigned' to null roles).
* **Production Logging:** Generates standardized timestamped server logs detailing extraction stages, input/output sources, and error tracking.
* **Health Reporting:** Outputs a dedicated `cleaning_report.json` containing metrics on processed records and missing data points.

---

## Prerequisites
To run this pipeline, you do not need Python installed on your host machine. You only need:
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/](https://github.com/)[YOUR_GITHUB_USERNAME]/[YOUR_REPO_NAME].git
   cd [YOUR_REPO_NAME]
   ```

2. **Build the Docker container:**
   ```bash
   docker build -t data-wrangler-app .
   ```

## Usage
The pipeline is designed to be executed via a simple Docker command. By default, the container will look for a `data.json` file in the working directory and execute the wrangling script.

**Run the pipeline:**
```bash
docker run -v "$(pwd):/app" data-wrangler-app
```
*(Note: The `-v "$(pwd):/app"` flag mounts your current directory to the container, allowing the script to read your local `data.json` and write the final CSV back to your machine.)*

## Expected Outputs

Upon successful execution, the pipeline generates the following in your directory:

1.  **`cleaned_data.csv`**: The fully flattened and standardized data file, ready for downstream use.
2.  **`cleaning_report.json`**: A diagnostic file containing metrics such as total rows processed and counts of missing identifiers.
3.  **Terminal Logs**: Standardized `INFO` logs tracking the job's lifecycle in real-time.

```text
2026-05-02 12:00:00,000 | INFO | data_wrangler | Starting data wrangling job
2026-05-02 12:00:00,005 | INFO | data_wrangler | Input: data.json
2026-05-02 12:00:00,010 | INFO | data_wrangler | Output: cleaned_data.csv
2026-05-02 12:00:00,500 | INFO | data_wrangler | Data wrangling completed successfully.
```
