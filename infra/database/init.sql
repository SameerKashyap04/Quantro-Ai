-- ============================================================
-- Quantro Personal AI — Database Initialization
-- ============================================================
-- This runs first on fresh database creation.
-- Creates extensions and sets timezone.
-- ============================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Set timezone
SET timezone = 'Asia/Kolkata';

-- Create application schema
CREATE SCHEMA IF NOT EXISTS quantro;
