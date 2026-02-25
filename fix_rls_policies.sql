-- ============================================================
-- FIX: RLS Policies for Custom Auth (Non-Supabase Auth)
-- Run this in Supabase SQL Editor to fix the permission error
-- ============================================================

-- Drop existing restrictive policies
DROP POLICY IF EXISTS "Allow authenticated users to read patients" ON patients;
DROP POLICY IF EXISTS "Allow authenticated users to create patients" ON patients;
DROP POLICY IF EXISTS "Allow users to update patients" ON patients;
DROP POLICY IF EXISTS "Allow authenticated users to read health records" ON health_records;
DROP POLICY IF EXISTS "Allow authenticated users to create health records" ON health_records;

-- ============================================================
-- Allow anon role full access (app uses its own auth system)
-- ============================================================

-- PATIENTS table policies
CREATE POLICY "Allow anon read patients" ON patients
    FOR SELECT USING (true);

CREATE POLICY "Allow anon insert patients" ON patients
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow anon update patients" ON patients
    FOR UPDATE USING (true);

CREATE POLICY "Allow anon delete patients" ON patients
    FOR DELETE USING (true);

-- HEALTH RECORDS table policies
CREATE POLICY "Allow anon read health records" ON health_records
    FOR SELECT USING (true);

CREATE POLICY "Allow anon insert health records" ON health_records
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow anon update health records" ON health_records
    FOR UPDATE USING (true);

CREATE POLICY "Allow anon delete health records" ON health_records
    FOR DELETE USING (true);

-- AUDIT LOGS table policies
CREATE POLICY "Allow anon read audit logs" ON audit_logs
    FOR SELECT USING (true);

CREATE POLICY "Allow anon insert audit logs" ON audit_logs
    FOR INSERT WITH CHECK (true);
