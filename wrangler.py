import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

import pandas as pd

OUTPUT_COLUMNS = ["id", "name", "role", "salary", "hire_date", "company", "department"]
SALARY_WITH_COMMAS_RE = re.compile(r"[+-]?\d{1,3}(,\d{3})+(\.\d+)?$")
SALARY_PLAIN_RE = re.compile(r"[+-]?\d+(\.\d+)?$")

logger = logging.getLogger("data_wrangler")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean and normalize legacy employee JSON data.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).resolve().parent / "data.json",
        help="Path to source JSON file (default: data.json next to script).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "cleaned_data.csv",
        help="Path to cleaned CSV output (default: cleaned_data.csv next to script).",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path(__file__).resolve().parent / "cleaning_report.json",
        help="Path to quality report JSON output.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging verbosity level.",
    )
    return parser.parse_args()


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def get_ci(mapping: dict[str, Any], key: str, default: Any = None) -> Any:
    """Case-insensitive key lookup for dict-like legacy payloads."""
    if not isinstance(mapping, dict):
        return default
    if key in mapping:
        return mapping[key]
    key_lower = key.lower()
    for existing_key, value in mapping.items():
        if str(existing_key).lower() == key_lower:
            return value
    return default


def clean_text(value: Any) -> Any:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped else None
    return value


def parse_salary(value: Any) -> Any:
    """Parse salary strictly; reject malformed comma groupings like 9,,000."""
    if value is None:
        return pd.NA

    if isinstance(value, str):
        text = value.strip()
        if not text:
            return pd.NA
        if not (SALARY_WITH_COMMAS_RE.fullmatch(text) or SALARY_PLAIN_RE.fullmatch(text)):
            return pd.NA
        value = text.replace(",", "")

    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric) or numeric < 0:
        return pd.NA
    return float(numeric)


def parse_hire_date(value: Any) -> Any:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.notna(parsed):
        return parsed.date().isoformat()
    return pd.NA


def load_payload(input_path: Path) -> dict[str, Any]:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")
    with input_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise ValueError("Input JSON root must be an object.")
    return payload


def normalize_employee(employee: dict[str, Any]) -> dict[str, Any]:
    details = get_ci(employee, "details", {}) or {}
    if not isinstance(details, dict):
        details = {}

    role_value = get_ci(details, "role")
    if isinstance(role_value, list):
        role_value = role_value[0] if role_value else None

    return {
        "id": clean_text(get_ci(employee, "id", get_ci(employee, "employee_id"))),
        "name": clean_text(get_ci(employee, "name", get_ci(employee, "full_name"))),
        "role": clean_text(role_value),
        "salary": parse_salary(get_ci(details, "salary")),
        "hire_date": parse_hire_date(get_ci(details, "hire_date")),
    }


def build_dataframe(payload: dict[str, Any]) -> pd.DataFrame:
    employees = payload.get("employees", [])
    if not isinstance(employees, list):
        raise ValueError("`employees` must be a list in the input payload.")

    rows = [normalize_employee(emp) for emp in employees if isinstance(emp, dict)]
    df = pd.DataFrame(rows)

    if df.empty:
        df = pd.DataFrame(columns=OUTPUT_COLUMNS)
    else:
        for col in OUTPUT_COLUMNS:
            if col not in df.columns:
                df[col] = pd.NA

    df["company"] = clean_text(payload.get("company"))
    df["department"] = clean_text(payload.get("department"))
    df["role"] = df["role"].fillna("Unassigned")
    return df[OUTPUT_COLUMNS]


def build_quality_report(df: pd.DataFrame, source_records: int) -> dict[str, Any]:
    duplicate_id_count = int(df["id"].duplicated(keep=False).sum()) if not df.empty else 0
    report = {
        "source_records": int(source_records),
        "processed_records": int(len(df)),
        "rows_missing_id": int(df["id"].isna().sum()),
        "rows_missing_name": int(df["name"].isna().sum()),
        "rows_unassigned_role": int((df["role"] == "Unassigned").sum()),
        "rows_missing_salary": int(df["salary"].isna().sum()),
        "rows_missing_hire_date": int(df["hire_date"].isna().sum()),
        "rows_with_duplicate_id": duplicate_id_count,
    }
    return report


def write_outputs(df: pd.DataFrame, output_path: Path, report_path: Path, report: dict[str, Any]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    with report_path.open("w", encoding="utf-8") as report_file:
        json.dump(report, report_file, indent=2)


def main() -> int:
    args = parse_args()
    setup_logging(args.log_level)

    logger.info("Starting data wrangling job")
    logger.info("Input: %s", args.input)
    logger.info("Output: %s", args.output)
    logger.info("Report: %s", args.report)

    try:
        payload = load_payload(args.input)
        employees = payload.get("employees", [])
        source_records = len(employees) if isinstance(employees, list) else 0
        df = build_dataframe(payload)
        report = build_quality_report(df, source_records)
        write_outputs(df, args.output, args.report, report)
    except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError) as exc:
        logger.error("Data wrangling failed: %s", exc)
        return 1

    logger.info("Data wrangling completed successfully.")
    logger.info("Processed %s records", len(df))
    logger.info("Rows with missing id: %s", report["rows_missing_id"])
    logger.info("Rows with missing name: %s", report["rows_missing_name"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())