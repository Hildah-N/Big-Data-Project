-- ============================================================
--  Global Patent Intelligence Database (SQLite Version)
-- ============================================================

PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------
-- 1. PATENTS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS patents (
    patent_id       TEXT PRIMARY KEY,
    title           TEXT,
    abstract        TEXT,
    filing_date     TEXT,      -- SQLite stores DATE as TEXT
    year            INTEGER
);

-- ------------------------------------------------------------
-- 2. INVENTORS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS inventors (
    inventor_id     TEXT PRIMARY KEY,
    name            TEXT,
    country         TEXT
);

-- ------------------------------------------------------------
-- 3. COMPANIES
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS companies (
    company_id      TEXT PRIMARY KEY,
    name            TEXT
);

-- ------------------------------------------------------------
-- 4. RELATIONSHIPS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS relationships (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    patent_id       TEXT,
    inventor_id     TEXT,
    company_id      TEXT,
    FOREIGN KEY (patent_id)   REFERENCES patents(patent_id),
    FOREIGN KEY (inventor_id) REFERENCES inventors(inventor_id),
    FOREIGN KEY (company_id)  REFERENCES companies(company_id)
);

-- ------------------------------------------------------------
-- Indexes
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_year        ON patents(year);
CREATE INDEX IF NOT EXISTS idx_inv_country ON inventors(country);
CREATE INDEX IF NOT EXISTS idx_rel_patent  ON relationships(patent_id);
CREATE INDEX IF NOT EXISTS idx_rel_inv     ON relationships(inventor_id);
CREATE INDEX IF NOT EXISTS idx_rel_comp    ON relationships(company_id);