-- Create database
CREATE DATABASE financial_db;

-- Create user
CREATE USER user WITH PASSWORD 'password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE financial_db TO user;

-- Connect to the database
\c financial_db;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables
-- Tables will be created automatically by SQLAlchemy based on the models