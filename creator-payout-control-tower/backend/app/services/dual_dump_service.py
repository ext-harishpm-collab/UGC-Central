import io,csv,uuid
from collections import defaultdict
from decimal import Decimal
from openpyxl import load_workbook
from ..db.session import SessionLocal
from ..models import Earning,MonthlyRun,QCResult,ExceptionCase,ContentItem

PAYABLE_FLAGS={"yes","eligible","paid","true"}
def s(v):return str(v).strip() if v not in (None,"") else ""
def d(v):
    try:return Decimal(str(v))
    except Exception:return Decimal("0")
def ix(hs,*terms):
    for i,h in enumerate(hs):
        x=(h or "").strip().lower()
        if any(t.lower() in x for t in terms):return i
    return None
def classify(ip,db,book,show):
    x=(ip or "").upper()
    if "N2A" in x or "A2A" in x:return "N2A/A2A","SOURCE"
    c=None
    if book:c=db.query(ContentItem).filter(ContentItem.book_id==book).first()
    if not c and show:c=db.query(ContentItem).filter(ContentItem.show_id==show).first()
    if c and c.content_type:return c.content_type,"MASTER"
    if "SERIES" in x:return "SERIES","SOURCE"
    if "NOVEL" in x:return "NOVEL","SOURCE"
    return "UNKNOWN","UNRESOLVED"

def read_dump(path,kind,db):
    wb=load_workbook(path,read_only=True,data_only=True);rows=[]
    for ws in wb.worksheets:
        header_row=None;hs=None
        for rn,r in enumerate(ws.iter_rows(min_row=1,max_row=min(12,ws.max_row or 1),values_only=True),1):
            vals=[s(v) for v in r]
            hits=sum(1 for x in vals if x.lower() in {"book id","show id","author id","author uid","pay?","ip type","gross","net amount"})
            if hits>=2:header_row=rn;hs=vals;break
        if not hs:continue
        for rn,r in enumerate(ws.iter_rows(min_row=header_row+1,values_only=True),header_row+1):
            if not any(v not in (None,"") for v in r):continue
            def get(*terms):
                j=ix(hs,*terms);return r[j] if j is not None and j<len(r) else None
            book=s(get("book id"));show=s(get("show id"));author=s(get("author id","author uid"))
            if not author:
                c=(db.query(ContentItem).filter(ContentItem.book_id==book).first() if book else None)
                author=c.author_id if c else None
            ctype,ctype_source=classify(s(get("ip type")),db,book,show)
            pay=s(get("pay?","pay"));gross=d(get("gross"));tds=d(get("tds amount","processed tds","tds"));net=d(get("net amount","processed net"))
            if net==0 and gross:net=gross-tds
            rows.append({"source_kind":kind,"source_file":path.rsplit("/",1)[-1],"source_sheet":ws.title,"source_row":rn,"author_id":author or None,
                         "book_id":book or None,"show_id":show or None,"content_type":ctype,"content_type_source":ctype_source,
                         "pay_flag":pay or None,"gross":gross,"tds":tds,"net":net})
    return rows

def process_two_dumps(inc_path,rs_path,period):
    db=SessionLocal()
    try:
        inc=read_dump(inc_path,"INCENTIVE_DUMP",db);rs=read_dump(rs_path,"REVENUE_SHARE_DUMP",db);all_rows=inc+rs
        qc=[];grouped=defaultdict(lambda:{"inc":Decimal("0"),"rs":Decimal("0"),"rows":[]})
        for r in all_rows:
            eligible=r["pay_flag"].lower() in PAYABLE_FLAGS or r["pay_flag"]==""
            reason=None;severity="REVIEW"
            if not r["author_id"] or not r["book_id"]:reason="Missing Author ID or Book ID"
            elif r["content_type"]=="UNKNOWN":reason="Novel/Series classification unresolved"
            elif not eligible:reason=f"Pay flag not eligible: {r['pay_flag']}"
            elif r["source_kind"]=="INCENTIVE_DUMP" and r["content_type"]=="N2A/A2A":reason="N2A/A2A incentive excluded";severity="BLOCK"
            key=(r["author_id"],r["book_id"],r["show_id"])
            grouped[key]["rows"].append(r)
            if reason:
                qc.append({"severity":severity,"rule_id":"ELG-002" if "N2A" in reason else "SOURCE-001","message":reason,
                           "author_id":r["author_id"],"book_id":r["book_id"],"show_id":r["show_id"],
                           "source_file":r["source_file"],"source_sheet":r["source_sheet"],"source_row":r["source_row"]})
                continue
            grouped[key]["inc" if r["source_kind"]=="INCENTIVE_DUMP" else "rs"]+=r["gross"]
        author=defaultdict(lambda:{"inc":Decimal("0"),"rs":Decimal("0"),"refs":[],"count":0,"types":set()});show_rows=[]
        for (aid,bid,sid),g in grouped.items():
            refs=[]
            for r in g["rows"]:
                refs.append(f'{r["source_kind"]}:{r["source_file"]}:{r["source_sheet"]}:R{r["source_row"]}')
                if r not in g["rows"]:continue
                if r["pay_flag"].lower() not in PAYABLE_FLAGS and r["pay_flag"]!="":continue
                if r["source_kind"]=="INCENTIVE_DUMP" and r["content_type"]=="N2A/A2A":continue
                if aid:
                    author[aid]["inc"]+=r["gross"] if r["source_kind"]=="INCENTIVE_DUMP" else 0
                    author[aid]["rs"]+=r["gross"] if r["source_kind"]=="REVENUE_SHARE" else 0
                    author[aid]["refs"].append(refs[-1]);author[aid]["count"]+=1;author[aid]["types"].add(r["content_type"])
            show_rows.append({"period":period,"author_id":aid,"book_id":bid,"show_id":sid,"content_type":" / ".join(sorted(g["rows"][0:1][0:1] and {r["content_type"] for r in g["rows"]} or {"UNKNOWN"})),
                              "incentive_gross":float(g["inc"]),"revenue_share_gross":float(g["rs"]),"gross":float(g["inc"]+g["rs"]),"sources":" | ".join(refs)})
        author_rows=[{"period":period,"author_id":aid,"incentive_gross":float(v["inc"]),"revenue_share_gross":float(v["rs"]),"gross":float(v["inc"]+v["rs"]),
                      "source_row_count":v["count"],"source_references":" | ".join(v["refs"]),"content_types":" / ".join(sorted(v["types"])) or "UNKNOWN"} for aid,v in author.items()]
        # Persist source rows and QC evidence. Existing rows for this period are replaced by the newly uploaded pair.
        db.query(Earning).filter(Earning.payment_period==period).delete(synchronize_session=False)
        db.query(QCResult).filter(QCResult.period==period).delete(synchronize_session=False)
        db.query(ExceptionCase).filter(ExceptionCase.period==period).delete(synchronize_session=False)
        run=MonthlyRun(id=uuid.uuid4().hex,period=period,incentive_file=inc_path.rsplit("/",1)[-1],revenue_share_file=rs_path.rsplit("/",1)[-1],
                       status="QC_REQUIRED",input_rows=len(all_rows),output_author_rows=len(author_rows),
                       qc_blocked=sum(x["severity"]=="BLOCK" for x in qc),qc_review=sum(x["severity"]=="REVIEW" for x in qc))
        db.add(run)
        for r in all_rows:
            reason=None
            if not r["author_id"] or not r["book_id"]:reason="Missing Author ID or Book ID"
            elif r["content_type"]=="UNKNOWN":reason="Novel/Series classification unresolved"
            elif r["pay_flag"].lower() not in PAYABLE_FLAGS:reason=f"Pay flag not eligible: {r['pay_flag']}"
            elif r["source_kind"]=="INCENTIVE_DUMP" and r["content_type"]=="N2A/A2A":reason="N2A/A2A incentive exclusion"
            db.add(Earning(id=uuid.uuid4().hex,payment_period=period,reward_type="INCENTIVE" if r["source_kind"]=="INCENTIVE_DUMP" else "REVENUE_SHARE",
                           author_id=r["author_id"],book_id=r["book_id"],show_id=r["show_id"],content_type=r["content_type"],
                           pay_flag=r["pay_flag"],exclusion_reason=reason,gross=r["gross"],tds=r["tds"],net=r["net"],
                           source_file=r["source_file"],source_sheet=r["source_sheet"],source_row=r["source_row"]))
        for q in qc:
            eid=f'{q["source_file"]}:{q["source_sheet"]}:R{q["source_row"]}'
            db.add(QCResult(id=uuid.uuid4().hex,period=period,entity_type="SOURCE_ROW",entity_id=eid,rule_id=q["rule_id"],severity=q["severity"],message=q["message"],detected_value=eid,status="OPEN"))
            if q["severity"]=="BLOCK":
                db.add(ExceptionCase(id=uuid.uuid4().hex,period=period,category=q["rule_id"],entity_type="SOURCE_ROW",entity_id=eid,severity="BLOCK",status="OPEN",reason=q["message"]))
        run.completed_at=__import__("datetime").datetime.utcnow();run.status="QC_BLOCKED" if run.qc_blocked else "QC_REVIEW" if run.qc_review else "QC_PASS"
        db.commit()
        return {"period":period,"run_status":run.status,"input_summary":{"incentive_rows":len(inc),"revenue_share_rows":len(rs),"total_source_rows":len(all_rows)},
                "author_level_rows":author_rows,"show_level_rows":show_rows,"qc_rows":qc,
                "qc_summary":{"BLOCK":sum(x["severity"]=="BLOCK" for x in qc),"REVIEW":sum(x["severity"]=="REVIEW" for x in qc),
                              "PASS":max(0,len(all_rows)-len(qc))}}
    finally:db.close()

def csv_bytes(rows,headers):
    b=io.StringIO();w=csv.DictWriter(b,fieldnames=headers,extrasaction="ignore");w.writeheader();w.writerows(rows);return b.getvalue().encode("utf-8-sig")
