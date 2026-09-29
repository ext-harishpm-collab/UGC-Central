from decimal import Decimal
from datetime import datetime
from sqlalchemy import or_
from ..db.session import SessionLocal
from ..models import PaymentTransaction,ReconciliationEvent

FIXED_COLUMNS=["Payout Type","Book ID","User Bank Account","Amount Before Tax","Currency","Amount After Tax","Payout Status","UTR","TDS%","Transaction Date","Payout Id","Mode","Status Details"]
SUCCESS={"success","successful","processed","paid","completed"}; FAILED={"failed","failure"}; REVERSED={"reversed","reversal"}

def norm(v):
    x=(v or "").strip().lower()
    if x in SUCCESS:return "SUCCESS"
    if x in FAILED:return "FAILED"
    if x in REVERSED:return "REVERSED"
    return "UNMATCHED"

def to_decimal(v):
    try:return Decimal(str(v))
    except Exception:return None

def parse_uwt_rows(rows):
    out=[]
    for rownum,row in enumerate(rows,start=2):
        if not any(v not in (None,"") for v in row):continue
        vals=list(row)+[None]*len(FIXED_COLUMNS)
        out.append({"row_number":rownum,"payout_type":vals[0],"book_id":str(vals[1]).strip() if vals[1] not in (None,"") else None,
                    "bank_account":str(vals[2]).strip() if vals[2] not in (None,"") else None,
                    "amount_before_tax":to_decimal(vals[3]),"currency":str(vals[4]).strip() if vals[4] not in (None,"") else "INR",
                    "amount_after_tax":to_decimal(vals[5]),"raw_status":vals[6],"status":norm(vals[6]),
                    "utr":str(vals[7]).strip() if vals[7] not in (None,"") else None,
                    "tds":to_decimal(vals[8]),"transaction_date":vals[9],"payout_id":str(vals[10]).strip() if vals[10] not in (None,"") else None,
                    "mode":vals[11],"status_details":vals[12]})

def reconcile_uwt_row(item):
    db=SessionLocal()
    try:
        row=None;match_type="NONE"
        if item.get("payout_id"):
            row=db.query(PaymentTransaction).filter(PaymentTransaction.payout_id==item["payout_id"]).first();match_type="PAYOUT_ID" if row else match_type
        if not row and item.get("utr"):
            row=db.query(PaymentTransaction).filter(PaymentTransaction.utr==item["utr"]).first();match_type="UTR" if row else match_type
        if not row and item.get("book_id") and item.get("amount_after_tax") is not None:
            row=db.query(PaymentTransaction).filter(PaymentTransaction.book_id==item["book_id"],PaymentTransaction.amount_after_tax==item["amount_after_tax"]).first();match_type="BOOK_AMOUNT" if row else match_type
        if not row:return {"matched":False,"status":item["status"],"match_type":match_type,"reason":"No deterministic payout match"}
        row.status=item["status"];row.ledger_state="CLOSED" if item["status"]=="SUCCESS" else "RETRYABLE" if item["status"] in {"FAILED","REVERSED"} else "OPEN"
        if item.get("utr"):row.utr=item["utr"]
        if item.get("bank_account"):row.account_number=item["bank_account"]
        if item.get("transaction_date") is not None:
            try:row.transaction_date=item["transaction_date"]
            except Exception:pass
        db.add(ReconciliationEvent(payment_transaction_id=row.id,match_type=f"UWT_{match_type}",finance_status=item["status"],ledger_state=row.ledger_state,notes=item.get("status_details")))
        db.commit()
        return {"matched":True,"payment_transaction_id":row.id,"author_id":row.author_id,"book_id":row.book_id,"show_id":row.show_id,"status":item["status"],"ledger_state":row.ledger_state,"match_type":match_type,"payout_type":item.get("payout_type")}
    finally:db.close()

def uwt_summary(items):
    result={"total":len(items),"SUCCESS":0,"FAILED":0,"REVERSED":0,"UNMATCHED":0}
    for i in items:result[i["status"]]=result.get(i["status"],0)+1
    return result
