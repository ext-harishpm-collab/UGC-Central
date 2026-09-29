from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Text, Integer, Boolean, Numeric, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from ..db.session import Base

class Author(Base):
    __tablename__="authors"
    id:Mapped[str]=mapped_column(String(64),primary_key=True)
    author_id:Mapped[str]=mapped_column(String(128),unique=True,index=True)
    name:Mapped[str|None]=mapped_column(String(255))
    status:Mapped[str|None]=mapped_column(String(64))
    first_seen:Mapped[datetime|None]=mapped_column(DateTime)
    last_seen:Mapped[datetime|None]=mapped_column(DateTime)

class BankAccount(Base):
    __tablename__="author_bank_accounts"
    id:Mapped[str]=mapped_column(String(64),primary_key=True)
    author_id:Mapped[str]=mapped_column(String(128),index=True)
    account_number:Mapped[str]=mapped_column(String(128),index=True)
    ifsc:Mapped[str|None]=mapped_column(String(32))
    bank_name:Mapped[str|None]=mapped_column(String(255))
    verification_status:Mapped[str|None]=mapped_column(String(64))
    successful_payment_count:Mapped[int]=mapped_column(Integer,default=0)
    first_successful_payment:Mapped[datetime|None]=mapped_column(DateTime)
    last_successful_payment:Mapped[datetime|None]=mapped_column(DateTime)
    is_current:Mapped[bool]=mapped_column(Boolean,default=False)
    source_month:Mapped[str|None]=mapped_column(String(64))
    __table_args__=(UniqueConstraint("author_id","account_number","ifsc",name="uq_author_bank"),)

class ContentItem(Base):
    __tablename__="content_items"
    id:Mapped[str]=mapped_column(String(64),primary_key=True)
    book_id:Mapped[str|None]=mapped_column(String(128),index=True)
    show_id:Mapped[str|None]=mapped_column(String(128),index=True)
    author_id:Mapped[str|None]=mapped_column(String(128),index=True)
    content_type:Mapped[str|None]=mapped_column(String(32),index=True)
    content_subtype:Mapped[str|None]=mapped_column(String(32))
    language:Mapped[str|None]=mapped_column(String(64))
    parent_book_id:Mapped[str|None]=mapped_column(String(128))
    parent_show_id:Mapped[str|None]=mapped_column(String(128))
    relationship_type:Mapped[str|None]=mapped_column(String(64))

class ImportBatch(Base):
    __tablename__="import_batches"
    id:Mapped[str]=mapped_column(String(64),primary_key=True)
    filename:Mapped[str]=mapped_column(String(255))
    payment_period:Mapped[str|None]=mapped_column(String(64))
    checksum:Mapped[str]=mapped_column(String(64),unique=True)
    status:Mapped[str]=mapped_column(String(32),default="IMPORTED")
    imported_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    total_rows:Mapped[int]=mapped_column(Integer,default=0)
    payment_event_rows:Mapped[int]=mapped_column(Integer,default=0)

class RawImportRow(Base):
    __tablename__="raw_import_rows"
    id:Mapped[str]=mapped_column(String(64),primary_key=True)
    batch_id:Mapped[str]=mapped_column(String(64),index=True)
    source_sheet:Mapped[str]=mapped_column(String(255))
    source_row:Mapped[int]=mapped_column(Integer)
    sheet_kind:Mapped[str]=mapped_column(String(64))
    payload:Mapped[str]=mapped_column(Text)

class PaymentTransaction(Base):
    __tablename__="payment_transactions"
    id:Mapped[str]=mapped_column(String(64),primary_key=True)
    author_id:Mapped[str|None]=mapped_column(String(128),index=True)
    book_id:Mapped[str|None]=mapped_column(String(128),index=True)
    show_id:Mapped[str|None]=mapped_column(String(128),index=True)
    payment_type:Mapped[str|None]=mapped_column(String(64))
    amount_before_tax:Mapped[Decimal|None]=mapped_column(Numeric(18,4))
    amount_after_tax:Mapped[Decimal|None]=mapped_column(Numeric(18,4))
    currency:Mapped[str|None]=mapped_column(String(16))
    status:Mapped[str]=mapped_column(String(32),index=True)
    utr:Mapped[str|None]=mapped_column(String(128),index=True)
    transaction_date:Mapped[datetime|None]=mapped_column(DateTime)
    payout_id:Mapped[str|None]=mapped_column(String(128),index=True)
    original_status:Mapped[str|None]=mapped_column(String(128))
    source_file:Mapped[str|None]=mapped_column(String(255))
    source_sheet:Mapped[str|None]=mapped_column(String(255))
    source_row:Mapped[int|None]=mapped_column(Integer)
    payment_period:Mapped[str|None]=mapped_column(String(64),index=True)
    content_type:Mapped[str|None]=mapped_column(String(32),index=True)
    ledger_state:Mapped[str]=mapped_column(String(32),default="OPEN",index=True)
    account_number:Mapped[str|None]=mapped_column(String(128))
    ifsc:Mapped[str|None]=mapped_column(String(32))
    bank_name:Mapped[str|None]=mapped_column(String(255))

class RuleConfig(Base):
    __tablename__="rule_configs"
    id:Mapped[str]=mapped_column(String(64),primary_key=True)
    rule_key:Mapped[str]=mapped_column(String(128),index=True)
    scope_type:Mapped[str]=mapped_column(String(64))
    scope_value:Mapped[str|None]=mapped_column(String(128))
    value_numeric:Mapped[Decimal|None]=mapped_column(Numeric(18,6))
    value_text:Mapped[str|None]=mapped_column(String(255))
    effective_from:Mapped[datetime|None]=mapped_column(DateTime)
    effective_to:Mapped[datetime|None]=mapped_column(DateTime)
    is_active:Mapped[bool]=mapped_column(Boolean,default=True)
    approved_by:Mapped[str|None]=mapped_column(String(128))
    reason:Mapped[str|None]=mapped_column(Text)
