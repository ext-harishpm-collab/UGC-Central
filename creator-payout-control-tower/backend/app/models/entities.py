from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Text, Integer, Boolean, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from ..db.session import Base

class Author(Base):
    __tablename__="authors"
    id:Mapped[str]=mapped_column(String(64),primary_key=True)
    author_id:Mapped[str]=mapped_column(String(128),unique=True,index=True)
    name:Mapped[str|None]=mapped_column(String(255)); status:Mapped[str|None]=mapped_column(String(64))
    first_seen:Mapped[datetime|None]=mapped_column(DateTime); last_seen:Mapped[datetime|None]=mapped_column(DateTime)

class BankAccount(Base):
    __tablename__="author_bank_accounts"
    id:Mapped[str]=mapped_column(String(64),primary_key=True); author_id:Mapped[str]=mapped_column(String(128),index=True)
    account_number:Mapped[str]=mapped_column(String(128),index=True); ifsc:Mapped[str|None]=mapped_column(String(32)); bank_name:Mapped[str|None]=mapped_column(String(255))
    verification_status:Mapped[str|None]=mapped_column(String(64)); successful_payment_count:Mapped[int]=mapped_column(Integer,default=0)
    first_successful_payment:Mapped[datetime|None]=mapped_column(DateTime); last_successful_payment:Mapped[datetime|None]=mapped_column(DateTime)
    is_current:Mapped[bool]=mapped_column(Boolean,default=False); source_month:Mapped[str|None]=mapped_column(String(64))

class ContentItem(Base):
    __tablename__="content_items"
    id:Mapped[str]=mapped_column(String(64),primary_key=True); book_id:Mapped[str|None]=mapped_column(String(128),index=True); show_id:Mapped[str|None]=mapped_column(String(128),index=True)
    author_id:Mapped[str|None]=mapped_column(String(128),index=True); content_type:Mapped[str|None]=mapped_column(String(32),index=True); content_subtype:Mapped[str|None]=mapped_column(String(32))
    language:Mapped[str|None]=mapped_column(String(64)); parent_book_id:Mapped[str|None]=mapped_column(String(128)); parent_show_id:Mapped[str|None]=mapped_column(String(128)); relationship_type:Mapped[str|None]=mapped_column(String(64))

class ImportBatch(Base):
    __tablename__="import_batches"
    id:Mapped[str]=mapped_column(String(64),primary_key=True); filename:Mapped[str]=mapped_column(String(255)); payment_period:Mapped[str|None]=mapped_column(String(64)); checksum:Mapped[str]=mapped_column(String(64),unique=True)
    status:Mapped[str]=mapped_column(String(32),default="IMPORTED"); imported_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    total_rows:Mapped[int]=mapped_column(Integer,default=0); payment_event_rows:Mapped[int]=mapped_column(Integer,default=0)

class RawImportRow(Base):
    __tablename__="raw_import_rows"
    id:Mapped[str]=mapped_column(String(64),primary_key=True); batch_id:Mapped[str]=mapped_column(String(64),index=True); source_sheet:Mapped[str]=mapped_column(String(255)); source_row:Mapped[int]=mapped_column(Integer); sheet_kind:Mapped[str]=mapped_column(String(64)); payload:Mapped[str]=mapped_column(Text)

class PaymentTransaction(Base):
    __tablename__="payment_transactions"
    id:Mapped[str]=mapped_column(String(64),primary_key=True); author_id:Mapped[str|None]=mapped_column(String(128),index=True); book_id:Mapped[str|None]=mapped_column(String(128),index=True); show_id:Mapped[str|None]=mapped_column(String(128),index=True)
    payment_type:Mapped[str|None]=mapped_column(String(64)); amount_before_tax:Mapped[Decimal|None]=mapped_column(Numeric(18,4)); amount_after_tax:Mapped[Decimal|None]=mapped_column(Numeric(18,4)); currency:Mapped[str|None]=mapped_column(String(16))
    status:Mapped[str]=mapped_column(String(32),index=True); utr:Mapped[str|None]=mapped_column(String(128),index=True); transaction_date:Mapped[datetime|None]=mapped_column(DateTime); payout_id:Mapped[str|None]=mapped_column(String(128),index=True)
    original_status:Mapped[str|None]=mapped_column(String(128)); source_file:Mapped[str|None]=mapped_column(String(255)); source_sheet:Mapped[str|None]=mapped_column(String(255)); source_row:Mapped[int|None]=mapped_column(Integer)
    payment_period:Mapped[str|None]=mapped_column(String(64),index=True); content_type:Mapped[str|None]=mapped_column(String(32),index=True); ledger_state:Mapped[str]=mapped_column(String(32),default="OPEN",index=True)
    account_number:Mapped[str|None]=mapped_column(String(128)); ifsc:Mapped[str|None]=mapped_column(String(32)); bank_name:Mapped[str|None]=mapped_column(String(255))

class Earning(Base):
    __tablename__="earnings"
    id:Mapped[str]=mapped_column(String(64),primary_key=True); payment_period:Mapped[str|None]=mapped_column(String(64),index=True); reward_type:Mapped[str]=mapped_column(String(64),index=True)
    author_id:Mapped[str|None]=mapped_column(String(128),index=True); book_id:Mapped[str|None]=mapped_column(String(128),index=True); show_id:Mapped[str|None]=mapped_column(String(128),index=True)
    content_type:Mapped[str|None]=mapped_column(String(32),index=True); pay_flag:Mapped[str|None]=mapped_column(String(64)); exclusion_reason:Mapped[str|None]=mapped_column(Text)
    gross:Mapped[Decimal|None]=mapped_column(Numeric(18,4)); tds:Mapped[Decimal|None]=mapped_column(Numeric(18,4)); net:Mapped[Decimal|None]=mapped_column(Numeric(18,4)); product_rs:Mapped[Decimal|None]=mapped_column(Numeric(12,4))
    source_file:Mapped[str|None]=mapped_column(String(255)); source_sheet:Mapped[str|None]=mapped_column(String(255)); source_row:Mapped[int|None]=mapped_column(Integer)

class PayoutBatch(Base):
    __tablename__="payout_batches"
    id:Mapped[str]=mapped_column(String(64),primary_key=True); payment_period:Mapped[str]=mapped_column(String(64),index=True)
    status:Mapped[str]=mapped_column(String(32),default="DRAFT"); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    frozen_at:Mapped[datetime|None]=mapped_column(DateTime); notes:Mapped[str|None]=mapped_column(Text)

class PayoutLine(Base):
    __tablename__="payout_lines"
    id:Mapped[str]=mapped_column(String(64),primary_key=True); batch_id:Mapped[str|None]=mapped_column(String(64),index=True); payment_period:Mapped[str]=mapped_column(String(64),index=True)
    author_id:Mapped[str]=mapped_column(String(128),index=True); gross_incentive:Mapped[Decimal]=mapped_column(Numeric(18,4),default=0); gross_revenue_share:Mapped[Decimal]=mapped_column(Numeric(18,4),default=0)
    other_earnings:Mapped[Decimal]=mapped_column(Numeric(18,4),default=0); gross_payable:Mapped[Decimal]=mapped_column(Numeric(18,4),default=0); marketing:Mapped[Decimal]=mapped_column(Numeric(18,4),default=0)
    platform:Mapped[Decimal]=mapped_column(Numeric(18,4),default=0); cop:Mapped[Decimal]=mapped_column(Numeric(18,4),default=0); flat_deduction:Mapped[Decimal]=mapped_column(Numeric(18,4),default=0)
    recovery:Mapped[Decimal]=mapped_column(Numeric(18,4),default=0); adjustment:Mapped[Decimal]=mapped_column(Numeric(18,4),default=0); tds:Mapped[Decimal]=mapped_column(Numeric(18,4),default=0)
    net_payable:Mapped[Decimal]=mapped_column(Numeric(18,4),default=0); qc_status:Mapped[str]=mapped_column(String(32),default="NOT_RUN"); freeze_status:Mapped[str]=mapped_column(String(32),default="OPEN")

class PayoutLineEarning(Base):
    __tablename__="payout_line_earnings"
    id:Mapped[str]=mapped_column(String(64),primary_key=True); payout_line_id:Mapped[str]=mapped_column(String(64),index=True); earning_id:Mapped[str]=mapped_column(String(64),index=True)

class QCResult(Base):
    __tablename__="qc_results"
    id:Mapped[str]=mapped_column(String(64),primary_key=True); period:Mapped[str|None]=mapped_column(String(64),index=True); entity_type:Mapped[str]=mapped_column(String(64)); entity_id:Mapped[str]=mapped_column(String(128),index=True)
    rule_id:Mapped[str]=mapped_column(String(64),index=True); severity:Mapped[str]=mapped_column(String(32)); message:Mapped[str]=mapped_column(Text); detected_value:Mapped[str|None]=mapped_column(Text); expected_value:Mapped[str|None]=mapped_column(Text); status:Mapped[str]=mapped_column(String(32),default="OPEN")

class ExceptionCase(Base):
    __tablename__="exception_cases"
    id:Mapped[str]=mapped_column(String(64),primary_key=True); period:Mapped[str|None]=mapped_column(String(64),index=True); category:Mapped[str]=mapped_column(String(64),index=True); entity_type:Mapped[str]=mapped_column(String(64)); entity_id:Mapped[str]=mapped_column(String(128),index=True)
    severity:Mapped[str]=mapped_column(String(32)); status:Mapped[str]=mapped_column(String(32),default="OPEN",index=True); reason:Mapped[str]=mapped_column(Text); resolution:Mapped[str|None]=mapped_column(Text)

class ReconciliationEvent(Base):
    __tablename__="reconciliation_events"
    id:Mapped[str]=mapped_column(String(64),primary_key=True); payment_transaction_id:Mapped[str|None]=mapped_column(String(64),index=True); match_type:Mapped[str]=mapped_column(String(64)); finance_status:Mapped[str]=mapped_column(String(32)); ledger_state:Mapped[str]=mapped_column(String(32)); notes:Mapped[str|None]=mapped_column(Text); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)

class RuleConfig(Base):
    __tablename__="rule_configs"
    id:Mapped[str]=mapped_column(String(64),primary_key=True); rule_key:Mapped[str]=mapped_column(String(128),index=True); scope_type:Mapped[str]=mapped_column(String(64)); scope_value:Mapped[str|None]=mapped_column(String(128)); value_numeric:Mapped[Decimal|None]=mapped_column(Numeric(18,6)); value_text:Mapped[str|None]=mapped_column(String(255))
    effective_from:Mapped[datetime|None]=mapped_column(DateTime); effective_to:Mapped[datetime|None]=mapped_column(DateTime); is_active:Mapped[bool]=mapped_column(Boolean,default=True); approved_by:Mapped[str|None]=mapped_column(String(128)); reason:Mapped[str|None]=mapped_column(Text)
