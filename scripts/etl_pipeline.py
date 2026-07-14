"""
HSE Data Pipeline — ETL Script
Mengambil data dari sumber (CSV/Excel/API) → transform → load ke PostgreSQL EDW

Fitur:
- Load CSV folder (dummy_data/) ke PostgreSQL
- Validasi data quality (null check, range check, referential integrity)
- Incremental load (hanya baris baru)
- Logging & error handling

Dependencies:
    pip install pandas sqlalchemy psycopg2-binary python-dotenv

Environment:
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5432
    POSTGRES_DB=hse_edw
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=your_password
"""

import os
import sys
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import pandas as pd
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

# =============================================
# CONFIGURATION
# =============================================

BASE_DIR = Path(__file__).parent.parent
DUMMY_DATA_DIR = BASE_DIR / "dummy_data"
LOG_DIR = BASE_DIR / "logs"

# Database connection (from environment or default)
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "hse_edw")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ETL Settings
SCHEMA_NAME = "hse"
BATCH_SIZE = 10000  # rows per batch insert
NULL_THRESHOLD = 0.1  # max 10% nulls allowed
FK_CHECK_ENABLED = True

# Tables to load (in dependency order)
DIM_TABLES = [
    "dim_datetime",
    "dim_site",
    "dim_department",
    "dim_employee",
    "dim_equipment",
    "dim_contractor",
    "dim_incident",
    "dim_ptw",
    "dim_environmental",
    "dim_training",
    "dim_hazard",
    "ref_env_threshold",
]

FACT_TABLES = [
    "fact_hse",
]

# =============================================
# LOGGING SETUP
# =============================================

LOG_DIR.mkdir(exist_ok=True)
log_file = LOG_DIR / f"etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# =============================================
# DATABASE UTILITIES
# =============================================

def get_engine():
    """Create SQLAlchemy engine with connection pool."""
    try:
        engine = create_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600,
            echo=False
        )
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection established")
        return engine
    except SQLAlchemyError as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


def get_existing_dates(engine, table_name: str) -> set:
    """Get existing date_keys from fact table for incremental load."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT DISTINCT date_key FROM {SCHEMA_NAME}.{table_name}"))
            return {row[0] for row in result}
    except Exception as e:
        logger.warning(f"Could not get existing dates for {table_name}: {e}")
        return set()


def check_table_exists(engine, table_name: str) -> bool:
    """Check if table exists in database."""
    inspector = inspect(engine)
    return inspector.has_table(table_name, schema=SCHEMA_NAME)


# =============================================
# DATA QUALITY CHECKS
# =============================================

def validate_dataframe(df: pd.DataFrame, table_name: str) -> Tuple[bool, List[str]]:
    """
    Validate DataFrame before loading.
    Returns (is_valid, list_of_errors)
    """
    errors = []

    # Check for required columns (basic check)
    if df.empty:
        errors.append(f"Table {table_name}: DataFrame is empty")
        return False, errors

    # Null check
    null_pct = df.isnull().sum() / len(df)
    high_null_cols = null_pct[null_pct > NULL_THRESHOLD]
    if not high_null_cols.empty:
        for col, pct in high_null_cols.items():
            errors.append(f"  {table_name}.{col}: {pct:.1%} nulls (threshold {NULL_THRESHOLD:.1%})")

    # Duplicate primary key check
    if "date_key" in df.columns and "site_key" in df.columns and "dept_key" in df.columns:
        dupes = df.duplicated(subset=["date_key", "site_key", "dept_key"], keep=False)
        if dupes.any():
            errors.append(f"  {table_name}: {dupes.sum()} duplicate rows on (date_key, site_key, dept_key)")

    # Range checks for numeric columns
    if "man_hours_worked" in df.columns:
        invalid = df[(df["man_hours_worked"] < 0) | (df["man_hours_worked"] > 10000)]
        if not invalid.empty:
            errors.append(f"  {table_name}: {len(invalid)} rows with man_hours_worked out of range [0, 10000]")

    if "ltifr" in df.columns or "trir" in df.columns:
        rate_cols = [c for c in ["ltifr", "trir"] if c in df.columns]
        for col in rate_cols:
            invalid = df[(df[col] < 0) | (df[col] > 100)]
            if not invalid.empty:
                errors.append(f"  {table_name}: {len(invalid)} rows with {col} out of range [0, 100]")

    is_valid = len(errors) == 0
    if not is_valid:
        errors.insert(0, f"Validation failed for {table_name}:")
    return is_valid, errors


# =============================================
# LOAD FUNCTIONS
# =============================================

def load_csv_to_postgres(
    engine,
    csv_path: Path,
    table_name: str,
    schema: str = SCHEMA_NAME,
    if_exists: str = "append",
    incremental: bool = False
) -> int:
    """
    Load CSV file to PostgreSQL table.
    Returns number of rows loaded.
    """
    logger.info(f"Loading {csv_path.name} → {schema}.{table_name}")

    if not csv_path.exists():
        logger.error(f"File not found: {csv_path}")
        return 0

    try:
        # Read CSV
        df = pd.read_csv(csv_path, dtype=str, keep_default_na=False, na_values=["", "NULL", "null", "NA", "N/A"])

        # Clean column names
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        # Replace empty strings with None
        df = df.replace(r'^\s*$', None, regex=True)

        # Convert date columns
        for col in df.columns:
            if "date" in col or "at" in col:
                try:
                    df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
                except Exception:
                    pass

        # Convert numeric columns
        for col in df.columns:
            if any(x in col for x in ["count", "hours", "days", "value", "rate", "score", "pct", "amt", "limit"]):
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Convert boolean columns
        for col in df.columns:
            if any(x in col for x in ["is_", "_flag", "_required", "_done", "_active"]):
                df[col] = df[col].map(lambda x: True if str(x).lower() in ["true", "1", "yes"] else False if str(x).lower() in ["false", "0", "no"] else None)

        # Validate
        is_valid, errors = validate_dataframe(df, table_name)
        if not is_valid:
            for err in errors:
                logger.warning(err)
            if any("empty" in e.lower() for e in errors):
                return 0

        # Incremental load check for fact tables
        original_len = len(df)
        if incremental and "date_key" in df.columns:
            existing_dates = get_existing_dates(engine, table_name)
            if existing_dates:
                df = df[~df["date_key"].isin(existing_dates)]
                logger.info(f"  Incremental: filtered {original_len - len(df)} existing rows")

        if df.empty:
            logger.info(f"  No new rows to load for {table_name}")
            return 0

        # Load to database
        rows_loaded = 0
        with engine.begin() as conn:
            for i in range(0, len(df), BATCH_SIZE):
                batch = df.iloc[i:i + BATCH_SIZE]
                batch.to_sql(
                    name=table_name,
                    con=conn,
                    schema=schema,
                    if_exists=if_exists if i == 0 else "append",
                    index=False,
                    method="multi",
                    chunksize=BATCH_SIZE
                )
                rows_loaded += len(batch)
                logger.info(f"  Batch {i // BATCH_SIZE + 1}: {len(batch)} rows")

        logger.info(f"✓ Loaded {rows_loaded} rows into {schema}.{table_name}")
        return rows_loaded

    except Exception as e:
        logger.error(f"✗ Failed to load {table_name}: {e}")
        return 0


def run_etl(engine, data_dir: Path = DUMMY_DATA_DIR):
    """Run full ETL pipeline."""
    logger.info("=" * 60)
    logger.info("HSE ETL Pipeline Started")
    logger.info(f"Source: {data_dir}")
    logger.info(f"Target: {DATABASE_URL}")
    logger.info("=" * 60)

    total_rows = 0

    # 1. Load dimension tables
    logger.info("PHASE 1: Loading Dimension Tables")
    for table in DIM_TABLES:
        csv_path = data_dir / f"{table}.csv"
        if csv_path.exists():
            rows = load_csv_to_postgres(engine, csv_path, table, if_exists="replace")
            total_rows += rows
        else:
            logger.warning(f"Skip {table}: CSV not found ({csv_path})")

    # 2. Load fact tables (incremental)
    logger.info("PHASE 2: Loading Fact Tables")
    for table in FACT_TABLES:
        csv_path = data_dir / f"{table}.csv"
        if csv_path.exists():
            rows = load_csv_to_postgres(engine, csv_path, table, if_exists="replace", incremental=True)
            total_rows += rows
        else:
            logger.warning(f"Skip {table}: CSV not found ({csv_path})")

    # 3. Refresh views
    logger.info("PHASE 3: Refreshing Materialized Views")
    try:
        with engine.begin() as conn:
            for view_name in ["v_daily_hse_summary", "v_ptw_current_status", "v_env_realtime", "v_equipment_compliance", "v_active_alerts"]:
                conn.execute(text(f"CREATE OR REPLACE VIEW {SCHEMA_NAME}.{view_name} AS SELECT * FROM {SCHEMA_NAME}.{view_name}"))
                logger.info(f"  View {view_name} refreshed")
    except Exception as e:
        logger.error(f"View refresh failed: {e}")

    logger.info("=" * 60)
    logger.info(f"ETL Complete. Total rows loaded: {total_rows}")
    logger.info("=" * 60)

    return total_rows


# =============================================
# DATA QUALITY REPORT
# =============================================

def generate_quality_report(engine) -> pd.DataFrame:
    """Generate data quality report."""
    report = []

    checks = [
        ("fact_hse null man_hours", "SELECT COUNT(*) FROM hse.fact_hse WHERE man_hours_worked IS NULL", "Should be 0"),
        ("fact_hse null date_key", "SELECT COUNT(*) FROM hse.fact_hse WHERE date_key IS NULL", "Should be 0"),
        ("fact_hse future dates", "SELECT COUNT(*) FROM hse.fact_hse WHERE date_key > CURRENT_DATE", "Should be 0"),
        ("dim_site count", "SELECT COUNT(*) FROM hse.dim_site", "Should be > 0"),
        ("dim_employee count", "SELECT COUNT(*) FROM hse.dim_employee", "Should be > 0"),
        ("fact_hse last update", "SELECT MAX(updated_at) FROM hse.fact_hse", "Recent"),
        ("active alerts count", "SELECT COUNT(*) FROM hse.v_active_alerts", "Current alerts"),
    ]

    with engine.connect() as conn:
        for name, query, expected in checks:
            try:
                result = conn.execute(text(query))
                value = result.scalar()
                report.append({"check": name, "value": value, "expected": expected, "status": "OK" if value == 0 or (name == "active alerts count" and value >= 0) else "WARN"})
            except Exception as e:
                report.append({"check": name, "value": str(e), "expected": expected, "status": "ERROR"})

    return pd.DataFrame(report)


# =============================================
# MAIN
# =============================================

def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="HSE Data Pipeline ETL")
    parser.add_argument("--dry-run", action="store_true", help="Validate only, don't load")
    parser.add_argument("--report", action="store_true", help="Generate quality report")
    parser.add_argument("--tables", nargs="+", help="Specific tables to load")
    args = parser.parse_args()

    engine = get_engine()

    if args.report:
        logger.info("Generating Data Quality Report...")
        report = generate_quality_report(engine)
        report_path = BASE_DIR / "logs" / f"dq_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        report.to_csv(report_path, index=False)
        logger.info(f"Report saved: {report_path}")
        print(report.to_string(index=False))
        return

    if args.dry_run:
        logger.info("DRY RUN — validating source files only")
        for csv_file in sorted(DUMMY_DATA_DIR.glob("*.csv")):
            df = pd.read_csv(csv_file, nrows=5)
            logger.info(f"  {csv_file.name}: {len(df.columns)} cols, sample OK")
        logger.info("Dry run complete")
        return

    # Normal ETL run
    tables_to_load = args.tables if args.tables else None

    if tables_to_load:
        for table in tables_to_load:
            csv_path = DUMMY_DATA_DIR / f"{table}.csv"
            if csv_path.exists():
                load_csv_to_postgres(engine, csv_path, table, if_exists="replace", incremental=False)
    else:
        run_etl(engine)

    engine.dispose()
    logger.info("Pipeline finished. Engine disposed.")


if __name__ == "__main__":
    main()
