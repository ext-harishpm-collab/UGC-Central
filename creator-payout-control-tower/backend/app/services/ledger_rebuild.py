from collections import defaultdict

def rebuild_show_ledger(earning_rows,payment_rows):
    # Aggregate payout evidence only where a deterministic Book/Show lineage exists.
    by_key=defaultdict(lambda:{"gross":0.0,"net":0.0,"statuses":[],"utrs":[],"rewards":[]})
    for e in earning_rows:
        if not e.get("show_id"):continue
        key=(e.get("show_id"),e.get("book_id"),e.get("author_id"),e.get("payment_period"))
        by_key[key]["gross"]+=float(e.get("gross") or 0)
        by_key[key]["rewards"].append(e.get("id"))
    for p in payment_rows:
        if not p.get("show_id"):continue
        key=(p.get("show_id"),p.get("book_id"),p.get("author_id"),p.get("payment_period"))
        by_key[key]["net"]+=float(p.get("amount_after_tax") or 0)
        if p.get("status"):by_key[key]["statuses"].append(p["status"])
        if p.get("utr"):by_key[key]["utrs"].append(p["utr"])
    out=[]
    for (show,book,author,period),v in by_key.items():
        status="UNMATCHED"
        if "SUCCESS" in v["statuses"]:status="SUCCESS"
        elif "REVERSED" in v["statuses"]:status="REVERSED"
        elif "FAILED" in v["statuses"]:status="FAILED"
        out.append({"show_id":show,"book_id":book,"author_id":author,"payment_period":period,**v,"resolved_status":status,
                    "ledger_state":"CLOSED" if status=="SUCCESS" else "RETRYABLE" if status in {"FAILED","REVERSED"} else "OPEN"})
    return out
