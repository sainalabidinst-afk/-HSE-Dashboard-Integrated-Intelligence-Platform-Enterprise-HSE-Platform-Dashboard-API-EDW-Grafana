import csv
import random
from datetime import datetime, timedelta

# Configuration
start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 6, 30)
site_keys = ['SITE-A', 'SITE-A-C', 'SITE-A-O', 'SITE-B', 'SITE-B-C', 'SITE-C', 'SITE-C-U']
dept_keys = ['DEPT-MIN', 'DEPT-CON', 'DEPT-ICT', 'DEPT-MNT', 'DEPT-ENV', 'DEPT-EHS', 'DEPT-PROC', 'DEPT-MNT-B', 'DEPT-HSE', 'DEPT-SUB', 'DEPT-MIN-C', 'DEPT-HSE-C', 'DEPT-SAF']

employees = [f'EMP-{str(i).zfill(3)}' for i in range(1, 21)]
contractors = [f'CTR-{str(i).zfill(3)}' for i in range(1, 9)]
equipments = [f'EQ-DT-{str(i).zfill(3)}' for i in range(1, 3)] + [f'EQ-EX-{str(i).zfill(3)}' for i in range(1, 3)] + [f'EQ-CR-{str(i).zfill(3)}' for i in range(1, 2)] + [f'EQ-FK-{str(i).zfill(3)}' for i in range(1, 2)]

output_file = 'C:/Users/SAbidin/HSE Dashboard/dummy_data/fact_hse_sample.csv'

with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        'date_key', 'site_key', 'dept_key', 'emp_key', 'contractor_key', 'equip_key',
        'ptw_key', 'hazard_key', 'incident_key',
        'man_hours_worked', 'lti_count', 'mti_count', 'fai_count', 'near_miss_count',
        'fatality_count', 'first_aid_count', 'property_dmg_count', 'env_incident_count',
        'inspection_count', 'observation_count', 'observation_safe', 'observation_unsafe',
        'ptw_issued_count', 'ptw_closed_count', 'ptw_open_count', 'ptw_violation_count',
        'gas_clearance_count', 'training_passed_count', 'training_failed_count', 'training_pending_count',
        'equipment_insp_pass_count', 'equipment_insp_fail_count', 'equipment_down_count',
        'metric_value', 'metric_type', 'severity_level', 'risk_level',
        'audit_score', 'audit_findings', 'audit_critical', 'audit_major', 'audit_minor',
        'env_reading_value', 'env_limit_value', 'env_exceeded', 'env_sample_id',
        'headcount_present', 'headcount_leave', 'headcount_contractor',
        'weather_condition', 'shift_name'
    ])
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        
        for site in site_keys:
            for dept in dept_keys:
                # Filter realistic combinations
                if site == 'SITE-A-O' and dept != 'DEPT-ICT':
                    continue
                if site == 'SITE-B' and dept not in ['DEPT-PROC', 'DEPT-MNT-B', 'DEPT-HSE']:
                    continue
                if site == 'SITE-B-C' and dept != 'DEPT-SUB':
                    continue
                if site == 'SITE-C-U' and dept != 'DEPT-MIN-C':
                    continue
                
                # Determine base working hours by department type
                if dept == 'DEPT-ICT':
                    base_hours = random.randint(200, 300)
                    base_contractor_hours = 0
                elif 'MIN' in dept or 'PROC' in dept:
                    base_hours = random.randint(1200, 1800)
                    base_contractor_hours = random.randint(400, 700)
                else:
                    base_hours = random.randint(300, 600)
                    base_contractor_hours = random.randint(100, 300)
                
                man_hours = base_hours + base_contractor_hours
                
                # Weekend check (lower hours)
                weekday = current_date.weekday()
                if weekday >= 5:
                    man_hours = int(man_hours * 0.3)
                    base_hours = int(base_hours * 0.3)
                    base_contractor_hours = int(base_contractor_hours * 0.3)
                
                # Generate incidents based on probability (seasonal adjustment for rainy season)
                is_rainy = current_date.month in [1, 2, 3, 11, 12]
                incident_multiplier = 1.2 if is_rainy else 1.0
                
                lti = 1 if random.random() < 0.02 * incident_multiplier else 0
                mti = random.randint(0, int(2 * incident_multiplier))
                fai = random.randint(0, int(3 * incident_multiplier))
                near_miss = random.randint(0, int(5 * incident_multiplier))
                fatality = 1 if random.random() < 0.005 else 0
                
                # PTW
                ptw_issued = random.randint(0, 8) if random.random() > 0.2 else 0
                ptw_closed = ptw_issued - random.randint(0, min(2, ptw_issued))
                ptw_open = ptw_issued - ptw_closed
                ptw_violation = random.randint(0, int(ptw_issued * 0.15))
                
                # Observations (higher during dry season)
                obs_target = 150 if dept in ['DEPT-MIN', 'DEPT-MNT', 'DEPT-MIN-C', 'DEPT-MNT-B'] else 50
                observation_count = random.randint(int(obs_target * 0.5), int(obs_target * 1.5))
                observation_safe = random.randint(int(observation_count * 0.4), observation_count)
                observation_unsafe = observation_count - observation_safe
                
                # Inspections
                inspection_count = random.randint(1, 8) if weekday < 5 else 0
                
                # Training
                training_passed = random.randint(0, 5) if random.random() > 0.6 else 0
                training_failed = random.randint(0, 1) if training_passed > 0 else 0
                training_pending = random.randint(0, 10)
                
                # Equipment
                equip_insp_pass = random.randint(0, 5)
                equip_insp_fail = random.randint(0, 1)
                equip_down = random.randint(0, 2) if weekday < 5 else 0
                
                # Audit (less frequent)
                audit_score = round(random.uniform(75, 98), 1) if random.random() > 0.95 else None
                audit_findings = random.randint(0, 12) if audit_score else 0
                audit_critical = random.randint(0, 2) if audit_score else 0
                audit_major = random.randint(0, 4) if audit_score else 0
                audit_minor = audit_findings - audit_critical - audit_major
                
                # Environmental
                env_reading = round(random.uniform(5, 80), 1) if random.random() > 0.3 else None
                env_limit = 50 if site == 'SITE-A' else 35
                env_exceeded = 1 if env_reading and env_reading > env_limit else 0
                env_sample_id = f'ENV-{random.randint(1, 16):03d}' if env_reading else None
                
                # Headcount
                if dept == 'DEPT-ICT':
                    present = random.randint(8, 15)
                    leave = random.randint(0, 2)
                    contractor_present = random.randint(2, 5)
                elif 'MIN' in dept or 'PROC' in dept:
                    present = random.randint(100, 250) if weekday < 5 else random.randint(30, 60)
                    leave = random.randint(10, 30)
                    contractor_present = random.randint(50, 150)
                else:
                    present = random.randint(15, 50)
                    leave = random.randint(0, 5)
                    contractor_present = random.randint(5, 20)
                
                # Metric value for KPI calculation
                metric_value = round(random.uniform(0.1, 5.0), 2) if random.random() > 0.3 else None
                metric_types = ['LTIFR', 'TRIR', 'SEVERITY', 'NEAR_MISS_RATE']
                metric_type = random.choice(metric_types) if metric_value else None
                
                # Risk level
                risk_levels = ['Low', 'Medium', 'High', 'Very High']
                risk_probs = [0.4, 0.35, 0.2, 0.05]
                risk_level = random.choices(risk_levels, weights=risk_probs, k=1)[0]
                
                # Headcount
                headcount_present = present
                headcount_leave = leave
                headcount_contractor = contractor_present
                
                # Gas clearance
                gas_clearance = random.randint(0, 5) if ptw_issued > 0 else 0
                
                writer.writerow([
                    date_str, site, dept, random.choice(employees) if random.random() > 0.3 else '',
                    random.choice(contractors) if random.random() > 0.5 else '',
                    random.choice(equipments) if random.random() > 0.5 else '',
                    '', '', '',
                    man_hours, lti, mti, fai, near_miss, fatality, 0, 0,
                    inspection_count, observation_count, observation_safe, observation_unsafe,
                    ptw_issued, ptw_closed, ptw_open, ptw_violation,
                    gas_clearance, training_passed, training_failed, training_pending,
                    equip_insp_pass, equip_insp_fail, equip_down,
                    metric_value, metric_type, random.choice(['FATAL', 'SERIOUS', 'MODERATE', 'MINOR']), risk_level,
                    audit_score, audit_findings, audit_critical, audit_major, audit_minor,
                    env_reading, env_limit, env_exceeded, env_sample_id,
                    headcount_present, headcount_leave, headcount_contractor,
                    random.choice(['Sunny', 'Cloudy', 'Rainy', 'Storm']), 'Morning'
                ])
        
        current_date += timedelta(days=1)

print(f'Generated fact_hse sample: {output_file}')
