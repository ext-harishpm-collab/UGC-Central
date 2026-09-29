-- Creator Payout Control Tower - Phase 2 local schema
CREATE TABLE IF NOT EXISTS import_batches (
  id TEXT PRIMARY KEY,
  filename TEXT NOT NULL,
  payment_period TEXT,
  checksum TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL DEFAULT 'IMPORTED',
  imported_at TEXT NOT NULL,
  total_rows INTEGER NOT NULL DEFAULT 0,
  payment_event_rows INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS raw_import_rows (
  id TEXT PRIMARY KEY,
  batch_id TEXT NOT NULL,
  source_sheet TEXT NOT NULL,
  source_row INTEGER NOT NULL,
  sheet_kind TEXT NOT NULL,
  payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS authors (
  id TEXT PRIMARY KEY,
  author_id TEXT NOT NULL UNIQUE,
  name TEXT,
  status TEXT
);
CREATE TABLE IF NOT EXISTS author_bank_accounts (
  id TEXT PRIMARY KEY,
  author_id TEXT NOT NULL,
  account_number TEXT NOT NULL,
  ifsc TEXT,
  bank_name TEXT,
  verification_status TEXT,
  successful_payment_count INTEGER NOT NULL DEFAULT 0,
  last_successful_payment TEXT,
  is_current INTEGER NOT NULL DEFAULT 0,
  UNIQUE(author_id,account_number,ifsc)
);
CREATE TABLE IF NOT EXISTS content_items (
  id TEXT PRIMARY KEY,
  book_id TEXT,
  show_id TEXT,
  author_id TEXT,
  content_type TEXT NOT NULL,
  language TEXT
);
CREATE TABLE IF NOT EXISTS payment_transactions (
  id TEXT PRIMARY KEY,
  author_id TEXT,
  book_id TEXT,
  show_id TEXT,
  payment_type TEXT,
  amount_before_tax NUMERIC,
  amount_after_tax NUMERIC,
  currency TEXT,
  status TEXT NOT NULL,
  utr TEXT,
  transaction_date TEXT,
  payout_id TEXT,
  original_status TEXT,
  source_file TEXT,
  source_sheet TEXT,
  source_row INTEGER
);
CREATE TABLE IF NOT EXISTS rule_configs (
  id TEXT PRIMARY KEY,
  rule_key TEXT NOT NULL,
  scope_type TEXT NOT NULL,
  scope_value TEXT,
  value_numeric NUMERIC,
  value_text TEXT,
  effective_from TEXT,
  effective_to TEXT,
  is_active INTEGER NOT NULL DEFAULT 1,
  approved_by TEXT,
  reason TEXT
);
