-- Create mlflow database
CREATE DATABASE mlflow;
-- Create airflow database
CREATE DATABASE airflow;
-- Enable pgvector on main DB
\c factorymind;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
