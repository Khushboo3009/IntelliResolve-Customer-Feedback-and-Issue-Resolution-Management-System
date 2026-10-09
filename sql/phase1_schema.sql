CREATE DATABASE IF NOT EXISTS intelliresolve
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE intelliresolve;

-- SQLAlchemy creates the authoritative application schema.
-- This file documents the core Phase 1 entities.

CREATE TABLE IF NOT EXISTS roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS departments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255),
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(120) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    role_id INT NOT NULL,
    department_id INT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

CREATE TABLE IF NOT EXISTS datasets (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    industry VARCHAR(100),
    row_count INT NOT NULL DEFAULT 0,
    schema_json JSON,
    status VARCHAR(30) NOT NULL DEFAULT 'REGISTERED',
    created_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS feedback (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    external_id VARCHAR(255),
    dataset_id INT NOT NULL,
    feedback_text LONGTEXT NOT NULL,
    rating DECIMAL(6,2),
    feedback_date DATETIME,
    processing_status VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    processed_at DATETIME NULL,
    analysis_version VARCHAR(50),
    INDEX idx_feedback_dataset (dataset_id),
    INDEX idx_feedback_status (processing_status),
    FOREIGN KEY (dataset_id) REFERENCES datasets(id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(80),
    entity_id VARCHAR(80),
    details LONGTEXT,
    created_at DATETIME NOT NULL,
    INDEX idx_audit_created (created_at),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
