-- Supabase PostgreSQL Schema for Body Evolution Wellness System
-- Run these commands in Supabase SQL Editor

-- ============================================================
-- 1. PATIENTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    age INTEGER NOT NULL CHECK (age >= 1 AND age <= 150),
    gender VARCHAR(20) NOT NULL,
    height DECIMAL(5, 2) NOT NULL CHECK (height >= 50 AND height <= 250),
    mobile VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255),
    area VARCHAR(255) NOT NULL,
    address TEXT,
    notes TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on patient_id for faster searches
CREATE INDEX idx_patients_patient_id ON patients(patient_id);
CREATE INDEX idx_patients_mobile ON patients(mobile);
CREATE INDEX idx_patients_name ON patients(name);
CREATE INDEX idx_patients_is_active ON patients(is_active);

-- ============================================================
-- 2. HEALTH RECORDS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS health_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id VARCHAR(10) NOT NULL,
    weight DECIMAL(5, 2) NOT NULL CHECK (weight >= 20 AND weight <= 300),
    bmi DECIMAL(5, 2) NOT NULL CHECK (bmi >= 10 AND bmi <= 50),
    bmr INTEGER NOT NULL CHECK (bmr >= 800 AND bmr <= 3000),
    body_fat DECIMAL(5, 2) NOT NULL CHECK (body_fat >= 5 AND body_fat <= 60),
    visceral_fat DECIMAL(5, 2) NOT NULL CHECK (visceral_fat >= 1 AND visceral_fat <= 30),
    body_age INTEGER NOT NULL CHECK (body_age >= 1 AND body_age <= 150),
    tsf DECIMAL(5, 2) NOT NULL,
    muscle_mass DECIMAL(5, 2) NOT NULL CHECK (muscle_mass >= 10 AND muscle_mass <= 60),
    wellness_score DECIMAL(3, 1) DEFAULT 5.0 CHECK (wellness_score >= 0 AND wellness_score <= 10),
    ai_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    CONSTRAINT valid_metrics CHECK (
        weight > 0 AND
        bmi > 0 AND
        bmr > 0 AND
        body_fat > 0 AND
        visceral_fat > 0 AND
        body_age > 0 AND
        tsf >= 0 AND
        muscle_mass > 0
    )
);

-- Create indexes for health records
CREATE INDEX idx_health_records_patient_id ON health_records(patient_id);
CREATE INDEX idx_health_records_created_at ON health_records(created_at);
CREATE INDEX idx_health_records_wellness_score ON health_records(wellness_score);

-- ============================================================
-- 3. AUDIT LOG TABLE (for tracking changes)
-- ============================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id UUID,
    patient_id VARCHAR(10),
    changes JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_ip VARCHAR(45)
);

CREATE INDEX idx_audit_logs_patient_id ON audit_logs(patient_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- ============================================================
-- 4. RLS (Row Level Security) Policies
-- ============================================================
-- Enable RLS
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE health_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Allow all authenticated users to read patients
CREATE POLICY "Allow authenticated users to read patients" ON patients
    FOR SELECT USING (auth.role() = 'authenticated');

-- Allow all authenticated users to create patients
CREATE POLICY "Allow authenticated users to create patients" ON patients
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Allow users to update their own records
CREATE POLICY "Allow users to update patients" ON patients
    FOR UPDATE USING (auth.role() = 'authenticated');

-- Similar policies for health_records
CREATE POLICY "Allow authenticated users to read health records" ON health_records
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users to create health records" ON health_records
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- ============================================================
-- 5. VIEW for Dashboard Statistics
-- ============================================================
CREATE VIEW dashboard_stats AS
SELECT 
    (SELECT COUNT(*) FROM patients WHERE is_active = true) as total_active_patients,
    (SELECT COUNT(*) FROM health_records) as total_evaluations,
    (SELECT COUNT(DISTINCT patient_id) FROM health_records WHERE wellness_score > 6) as high_risk_patients,
    (SELECT COUNT(*) FROM health_records WHERE created_at > CURRENT_DATE - INTERVAL '30 days') as recent_evaluations;

-- ============================================================
-- 6. FUNCTIONS FOR AUTOMATED AUDIT LOGGING
-- ============================================================
CREATE OR REPLACE FUNCTION audit_patient_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (action, table_name, record_id, patient_id, changes)
        VALUES ('UPDATE', 'patients', NEW.id, NEW.patient_id, 
                jsonb_build_object('old', row_to_json(OLD), 'new', row_to_json(NEW)));
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (action, table_name, record_id, patient_id, changes)
        VALUES ('DELETE', 'patients', OLD.id, OLD.patient_id, row_to_json(OLD));
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (action, table_name, record_id, patient_id, changes)
        VALUES ('INSERT', 'patients', NEW.id, NEW.patient_id, row_to_json(NEW));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER patient_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON patients
FOR EACH ROW EXECUTE FUNCTION audit_patient_changes();

-- Similar trigger for health_records
CREATE OR REPLACE FUNCTION audit_health_record_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (action, table_name, record_id, patient_id, changes)
        VALUES ('INSERT', 'health_records', NEW.id, NEW.patient_id, row_to_json(NEW));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER health_record_audit_trigger
AFTER INSERT ON health_records
FOR EACH ROW EXECUTE FUNCTION audit_health_record_changes();

-- ============================================================
-- 7. SAMPLE DATA (Optional - for testing)
-- ============================================================
-- Uncomment to add sample data
/*
INSERT INTO patients (patient_id, name, age, gender, height, mobile, email, area, address, notes)
VALUES 
    ('P0001', 'John Doe', 35, 'Male', 175.5, '9876543210', 'john@example.com', 'New York', '123 Main St', 'No known allergies'),
    ('P0002', 'Jane Smith', 28, 'Female', 162.3, '9876543211', 'jane@example.com', 'Los Angeles', '456 Oak Ave', 'Regular exercise routine'),
    ('P0003', 'Robert Brown', 45, 'Male', 180.2, '9876543212', 'robert@example.com', 'Chicago', '789 Elm St', 'Diabetic');

INSERT INTO health_records (patient_id, weight, bmi, bmr, body_fat, visceral_fat, body_age, tsf, muscle_mass, wellness_score)
VALUES 
    ('P0001', 75.5, 24.5, 1800, 22.5, 8, 35, 12.5, 38, 3.5),
    ('P0002', 58.2, 22.1, 1400, 25, 6, 26, 15, 35, 2.8),
    ('P0003', 92.3, 28.4, 1950, 32, 14, 52, 18, 30, 7.2);
*/

-- ============================================================
-- NOTES FOR SETUP
-- ============================================================
/*
1. Copy the SQL above to Supabase SQL Editor and run
2. The tables include:
   - patients: Main patient records
   - health_records: Health evaluation metrics
   - audit_logs: Automatic audit trail
   
3. Indexes are created for performance
4. RLS policies control data access
5. Views provide analytics
6. Triggers automatically log changes
7. Constraints ensure data integrity

8. Update your .env file with:
   SUPABASE_URL=your_project_url.supabase.co
   SUPABASE_KEY=your_anon_key
*/
