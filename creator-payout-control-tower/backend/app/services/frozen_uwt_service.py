from collections import defaultdict
from decimal import Decimal
from ..db.session import SessionLocal
from ..models import PayoutBatch,PayoutLine,PayoutLineEarning,Earning

UWT_COLUMNS=["Payout Type","Book ID","User Bank Account","Amount Before Tax","Currency","Amount After Tax","Payout Status","UTR","TDS%","Transaction Date","Payout Id","Mode","Status Details"]

def build_frozen_rows(batch_id):
    db=SessionLocal()
    try:
        batch=db.query(PayoutBatch).filter_by(id=batch_id).first()
        if not batch:return {"ok":False,"reason":"Batch not found"}
        if batch.status!="FROZEN":return {"ok":False,"reason":"Batch is not frozen"}
        lines=db.query(PayoutLine).filter_by(batch_id=batch_id,qc_status="PASS").all()
        groups=defaultdict(lambda:{"gross":Decimal("0"),"tds":Decimal("0"),"net":Decimal("0"),"author_ids":set(),"earning_ids":[]})
        for line in lines:
            links=db.query(PayoutLineEarning).filter_by(payout_line_id=line.id).all()
            for link in links:
                e=db.query(Earning).filter_by(id=link.earning_id).first()
                if not e or not e.book_id:continue
                payout_type="INCENTIVE" if e.reward_type=="INCENTIVE" else "REVENUE_SHARE"
                key=(payout_type,e.book_id)
                g=groups[key];g["author_ids"].add(line.author_id);g["earning_ids"].append(e.id)
                g["gross"]+=e.gross or 0;g["tds"]+=e.tds or 0;g["net"]+= (e.gross or 0)-(e.tds or 0)
        rows=[]
        for (ptype,book),g in sorted(groups.items()):
            rows.append({"Payout Type":ptype,"Book ID":book,"User Bank Account":"","Amount Before Tax":float(g["gross"]),"Currency":"INR",
                         "Amount After Tax":float(g["net"]),"Payout Status":"READY","UTR":"","TDS%":float(g["tds"]/g["gross"]) if g["gross"] else "",
                         "Transaction Date":"","Payout Id":batch.id,"Mode":"","Status Details":""})
        return {"ok":True,"batch_id":batch_id,"rows":rows}
    finally:db.close()
