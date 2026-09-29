def run_qc(data):
    flags=[]
    if not data.get("author_id"): flags.append({"rule_id":"ELG-001","severity":"BLOCK","message":"Missing Author ID"})
    if data.get("content_type") in {"N2A","A2A","N2A/A2A"} and float(data.get("incentive",0)) != 0:
        flags.append({"rule_id":"ELG-002","severity":"BLOCK","message":"N2A/A2A incentive detected","detected":str(data.get("incentive")),"expected":"0"})
    if data.get("previously_paid"): flags.append({"rule_id":"DUP-001","severity":"CRITICAL","message":"Previously paid reward appears again"})
    if data.get("contract_rs") is not None and data.get("product_rs") is not None and abs(float(data["contract_rs"])-float(data["product_rs"]))>1e-9:
        flags.append({"rule_id":"CON-001","severity":"BLOCK","message":"Revenue Share % differs from contract","detected":str(data["product_rs"]),"expected":str(data["contract_rs"])})
    if not data.get("bank_ok"): flags.append({"rule_id":"BANK-001","severity":"BLOCK","message":"Bank validation required"})
    if not data.get("pan_ok"): flags.append({"rule_id":"TAX-001","severity":"BLOCK","message":"PAN/TDS validation required"})
    if data.get("recovery_double"): flags.append({"rule_id":"REC-001","severity":"BLOCK","message":"Recovery appears to be applied twice"})
    if not data.get("adjustment_reason",True): flags.append({"rule_id":"ADJ-001","severity":"BLOCK","message":"Adjustment lacks reason/approval"})
    if float(data.get("final_net",0)) < float(data.get("payment_threshold",100)):
        flags.append({"rule_id":"PAY-001","severity":"REVIEW","message":"Net payable is below configured threshold"})
    blocking=any(x["severity"] in {"BLOCK","CRITICAL"} for x in flags)
    return {"status":"BLOCK" if blocking else "PASS","flags":flags}
