import io,csv
from sqlalchemy import func
from ..db.session import SessionLocal
from ..models import PayoutBatch,PayoutLine,Earning,Author,BankAccount,PanRecord,ContractRecord,QCResult,RecoveryEvent,Adjustment

HEADERS=["Payment Period","Author ID","Author Name","PAN","PAN Status","TDS %","Bank Account Number","IFSC","Bank Name","Bank Validation Status",
         "Book/Novel IDs","Show/Series IDs","Content Type","N2A/A2A","Parent ID","Contract Type","Contractual RS %","Gross Incentive",
         "Gross Revenue Share","Other Earnings","Gross Payable","Marketing","Platform","COP","Flat Deduction","Recovery Applied","Manual Adjustment",
         "TDS Amount","Final Net Payable","Master Match Status","QC Status","Hold Reason","Payout Batch ID","Source References"]

def export_frozen_batch(batch_id):
    db=SessionLocal()
    try:
        batch=db.query(PayoutBatch).filter_by(id=batch_id).first()
        if not batch:return {"ok":False,"reason":"Batch not found"}
        if batch.status!="FROZEN":return {"ok":False,"reason":"Batch is not frozen"}
        lines=db.query(PayoutLine).filter_by(batch_id=batch_id).all()
        blocking=db.query(QCResult).filter(QCResult.period==batch.payment_period,QCResult.severity.in_([ "BLOCK","CRITICAL"]),QCResult.status=="OPEN").count()
        if blocking:return {"ok":False,"reason":"Open blocking QC exists","blocking_qc":blocking}
        out=[]
        for line in lines:
            author=db.query(Author).filter_by(author_id=line.author_id).first()
            banks=db.query(BankAccount).filter_by(author_id=line.author_id,is_current=True).all()
            pan=db.query(PanRecord).filter_by(author_id=line.author_id).order_by(PanRecord.validated_at.desc()).first()
            contracts=db.query(ContractRecord).filter_by(author_id=line.author_id).all()
            earns=db.query(Earning).filter(Earning.payment_period==batch.payment_period,Earning.author_id==line.author_id).all()
            refs=[f"{e.source_file}:{e.source_sheet}:R{e.source_row}" for e in earns]
            books=sorted({e.book_id for e in earns if e.book_id});shows=sorted({e.show_id for e in earns if e.show_id});types=sorted({e.content_type or "UNKNOWN" for e in earns})
            parent_ids=sorted({e.show_id for e in earns if e.content_type=="N2A/A2A" and e.show_id})
            bank=banks[0] if banks else None
            contract_rs=contracts[0].contract_rs if len(contracts)==1 else None
            out.append({
              "Payment Period":batch.payment_period,"Author ID":line.author_id,"Author Name":author.name if author else "",
              "PAN":pan.pan if pan else "","PAN Status":pan.pan_status if pan else "","TDS %":float(pan.validated_tds_rate) if pan and pan.validated_tds_rate is not None else "",
              "Bank Account Number":bank.account_number if bank else "","IFSC":bank.ifsc if bank else "","Bank Name":bank.bank_name if bank else "",
              "Bank Validation Status":bank.verification_status if bank else "MISSING","Book/Novel IDs":" | ".join(books),"Show/Series IDs":" | ".join(shows),
              "Content Type":" / ".join(types),"N2A/A2A":"YES" if "N2A/A2A" in types else "NO","Parent ID":" | ".join(parent_ids),
              "Contract Type":contracts[0].contract_type if len(contracts)==1 else "REVIEW","Contractual RS %":float(contract_rs) if contract_rs is not None else "",
              "Gross Incentive":float(line.gross_incentive),"Gross Revenue Share":float(line.gross_revenue_share),"Other Earnings":float(line.other_earnings),
              "Gross Payable":float(line.gross_payable),"Marketing":float(line.marketing),"Platform":float(line.platform),"COP":float(line.cop),"Flat Deduction":float(line.flat_deduction),
              "Recovery Applied":float(line.recovery),"Manual Adjustment":float(line.adjustment),"TDS Amount":float(line.tds),"Final Net Payable":float(line.net_payable),
              "Master Match Status":"MATCHED" if author else "MISSING","QC Status":line.qc_status,"Hold Reason":"" if line.qc_status=="PASS" else "QC BLOCK/REVIEW",
              "Payout Batch ID":batch.id,"Source References":" | ".join(refs)
            })
        b=io.StringIO();w=csv.DictWriter(b,fieldnames=HEADERS);w.writeheader();w.writerows(out)
        return {"ok":True,"csv":b.getvalue().encode("utf-8-sig"),"row_count":len(out),"headers":HEADERS}
    finally:db.close()
