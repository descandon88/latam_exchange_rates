-- Runs once when the postgres container's data volume is first created.
-- Phase 1 doesn't write to this table yet, but the schema needs to exist
-- for docker-compose's volume mount of this file to succeed.
CREATE SCHEMA IF NOT EXISTS exchange_rates;

CREATE TABLE IF NOT EXISTS exchange_rates.rates (
    id BIGSERIAL PRIMARY KEY,
    source VARCHAR(10) NOT NULL,       -- 'BCP' | 'BCU'
    country VARCHAR(2) NOT NULL,       -- 'PY' | 'UY'
    currency VARCHAR(10) NOT NULL,     -- 'USD'
    rate_date DATE NOT NULL,
    rate_buy NUMERIC(14, 4) NOT NULL,
    rate_sell NUMERIC(14, 4) NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_rates_source_currency_date UNIQUE (source, currency, rate_date)
);

CREATE INDEX IF NOT EXISTS idx_rates_country_date ON exchange_rates.rates (country, rate_date);
