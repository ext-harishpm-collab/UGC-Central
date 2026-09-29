from sqlalchemy import inspect,text
from .db.session import engine

def ensure_local_schema():
    inspector=inspect(engine)
    required={
        "payment_transactions":["account_number","ifsc","bank_name","payment_period","content_type","ledger_state"],
        "earnings":["payment_period","reward_type","author_id","book_id","show_id","content_type","pay_flag","exclusion_reason","gross","tds","net","product_rs","source_file","source_sheet","source_row"],
        "payout_batches":["id","payment_period","status","created_at","frozen_at","notes"],
        "payout_lines":["id","batch_id","payment_period","author_id","gross_incentive","gross_revenue_share","other_earnings","gross_payable","marketing","platform","cop","flat_deduction","recovery","adjustment","tds","net_payable","qc_status","freeze_status"],
        "payout_line_earnings":["id","payout_line_id","earning_id"],
        "qc_results":["id","period","entity_type","entity_id","rule_id","severity","message","detected_value","expected_value","status"],
        "exception_cases":["id","period","category","entity_type","entity_id","severity","status","reason","resolution"],
        "reconciliation_events":["id","payment_transaction_id","match_type","finance_status","ledger_state","notes","created_at"]
    }
    for table,cols in required.items():
        if not inspector.has_table(table):
            continue
        existing={c["name"] for c in inspector.get_columns(table)}
        for col in cols:
            if col in existing:
                continue
            sql_type="INTEGER" if col=="source_row" else "TEXT"
            with engine.begin() as conn:
                conn.execute(text(f'ALTER TABLE "{table}" ADD COLUMN "{col}" {sql_type}'))
