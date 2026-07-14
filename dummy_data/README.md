# HSE Dashboard — Dummy Dataset Directory

## Files Overview

| File | Description | Records | Used For |
|---|---|---|---|
| `dim_site.csv` | Site master data | 7 sites | Filter, location |
| `dim_department.csv` | Department/organization | 13 depts | Drill-through |
| `dim_employee.csv` | Employee & contractor master | 20 rows | Manpower, accountability |
| `dim_equipment.csv` | Equipment register | 10 units | Equipment safety |
| `dim_incident.csv` | Incident categories & master | 10 samples | Incident analysis |
| `dim_contractor.csv` | Contractor master | 8 contractors | Contractor dashboard |
| `dim_ptw.csv` | Permit to Work register | 10 permits | PTW dashboard |
| `dim_environmental.csv` | Environmental parameters | 16 params | Environmental dashboard |
| `dim_training.csv` | Training programs | 20 programs | Training dashboard |
| `dim_datetime_sample.csv` | Calendar (sample) | 10 days | Time intelligence |
| `ref_env_threshold.csv` | Location-specific limits | 19 rows | Dynamic thresholding |
| `fact_hse_sample.csv` | Daily HSE metrics (generated) | Script-generated | Main fact table |
| `generate_dummy_hse.py` | Python generator script | N/A | Regenerate fact_hse |

## Loading Sequence (Python / Power BI / SQL)

1. Load all `dim_*` tables first
2. Load `ref_env_threshold.csv`
3. Load `dim_datetime_sample.csv` (or generate full year via script)
4. Generate `fact_hse_sample.csv` using `generate_dummy_hse.py`
5. Verify foreign key integrity (sample check)

## Sample Data Characteristics

- **Period:** January - June 2025 (6 months)
- **Sites:** Kutai (mining), Balikpapan (oil & gas), Samarinda (mining)
- **Seasons:** Rainy (Jan-Mar, Nov-Dec), Dry (Apr-Oct)
- **Incident probability:** Higher during rainy season (+20%)
- **Weekend:** Reduced man-hours (30%), fewer incidents
- **Department coverage:** Mining, Construction, ICT, Maintenance, Environmental, HSE, Process, Support
- **Contractor mix:** 30-70% of workforce depending on site

## Regenerate Data

```python
# Run from directory: C:\Users\SAbidin\HSE Dashboard
python scripts/generate_dummy_hse.py
```

Output: `dummy_data/fact_hse_sample.csv`

## Note

Data is synthetic and for demonstration purposes only. All names, sites, and values are fictional.
In production, replace with real EDW data via ETL pipeline.
