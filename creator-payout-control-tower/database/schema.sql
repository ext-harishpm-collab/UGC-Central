-- Phase 13 schema additions
CREATE TABLE IF NOT EXISTS recovery_events(id TEXT PRIMARY KEY,payment_period TEXT,author_id TEXT,opening_outstanding NUMERIC,applied NUMERIC,closing_outstanding NUMERIC,source_file TEXT,source_sheet TEXT,source_row INTEGER);
CREATE TABLE IF NOT EXISTS adjustments(id TEXT PRIMARY KEY,payment_period TEXT,author_id TEXT,book_id TEXT,show_id TEXT,amount NUMERIC,reason TEXT,currency TEXT,reward_type TEXT,approved_by TEXT,status TEXT DEFAULT 'PENDING');
