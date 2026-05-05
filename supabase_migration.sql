-- PhotoWall — Supabase database migration
-- Run this in Supabase SQL Editor before deploying

CREATE TABLE IF NOT EXISTS photos (
    id          SERIAL PRIMARY KEY,
    object_key  TEXT NOT NULL,
    url         TEXT NOT NULL,
    date        TEXT NOT NULL DEFAULT '',
    note        TEXT NOT NULL DEFAULT '',
    deleted     BOOLEAN NOT NULL DEFAULT false,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Index for listing photos ordered by date
CREATE INDEX IF NOT EXISTS idx_photos_date ON photos (date ASC)
    WHERE deleted = false;

-- Enable Row-Level Security (optional, skip if using service_role key)
-- ALTER TABLE photos ENABLE ROW LEVEL SECURITY;
