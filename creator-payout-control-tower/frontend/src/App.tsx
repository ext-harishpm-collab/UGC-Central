import { useEffect, useState } from "react";

type Status = "SUCCESS" | "FAILED" | "REVERSED" | "UNMATCHED";
type Page = "Dashboard" | "Historical Import";

const sample = [
  { show:"SHOW-10021", book:"BOOK-20021", author:"AUTH-30021", type:"NOVEL", amount:18425.5, status:"SUCCESS" as Status },
  { show:"SHOW-10022", book:"BOOK-20022", author:"AUTH-30022", type:"SERIES", amount:12840, status:"FAILED" as Status },
  { show:"SHOW-10023", book:"BOOK-20023", author:"AUTH-30023", type:"N2A/A2A", amount:9210.25, status:"REVERSED" as Status }
];

export default function App(){
 const [month,setMonth]=useState("August 2026"),[view,setView]=useState("All"),[api,setApi]=useState("checking...");
 const [page,setPage]=useState<Page>("Dashboard"),[file,setFile]=useState<File|null>(null),[busy,setBusy]=useState(false),[result,setResult]=useState<any>(null);
 const rows=view==="All"?sample:sample.filter(r=>r.type===view);
 useEffect(()=>{fetch("/api/health").then(r=>r.json()).then(d=>setApi(d.status)).catch(()=>setApi("offline"))},[]);
 async function upload(){if(!file)return;setBusy(true);setResult(null);const fd=new FormData();fd.append("file",file);try{const r=await fetch("/api/import/upload",{method:"POST",body:fd});const d=await r.json();setResult(r.ok?d:{error:d.detail||"Import failed"});}catch{setResult({error:"Backend offline"});}finally{setBusy(false)}}
 const nav=["Dashboard","Monthly Cycle","Author","Book","Show","Novel","Series","N2A/A2A","UWT","Ledger","Exceptions","Rules","Historical Import"];
 return <div className="app"><aside className="sidebar"><div className="brand">Creator Payout<br/>Control Tower</div>{nav.map(x=><div key={x} onClick={()=>{if(x==="Dashboard"||x==="Historical Import")setPage(x as Page)}} className={x===page?"nav active":"nav"}>{x}</div>)}</aside>
 <main className="main">{page==="Dashboard"?<>
  <header><div><div className="eyebrow">PHASE 2 LOCAL PREVIEW</div><h1>Payment Operations</h1><p>Historical import, UWT processing and ledger controls.</p></div><div className="controls"><select value={month} onChange={e=>setMonth(e.target.value)}><option>August 2026</option><option>July 2026</option><option>June 2026</option><option>May 2026</option></select><select value={view} onChange={e=>setView(e.target.value)}><option>All</option><option>NOVEL</option><option>SERIES</option><option>N2A/A2A</option></select></div></header>
  <section className="cards">{[["Ready for Payout","2,341"],["On Hold","145"],["Gross","₹52.44M"],["Net Payable","₹21.18M"],["Success","2,301"],["Retry Pool","40"]].map(([a,b])=><div className="card" key={a}><span>{a}</span><strong>{b}</strong></div>)}</section>
  <section className="panel"><div className="panelHead"><div><h2>Show-Level Payment Ledger</h2><p>{month} · {view}</p></div><span className="health">API {api}</span></div><table><thead><tr><th>Show ID</th><th>Book ID</th><th>Author ID</th><th>Type</th><th>Net</th><th>Status</th></tr></thead><tbody>{rows.map(r=><tr key={r.show}><td>{r.show}</td><td>{r.book}</td><td>{r.author}</td><td>{r.type}</td><td>₹{r.amount.toLocaleString("en-IN",{minimumFractionDigits:2})}</td><td><span className={"pill "+r.status.toLowerCase()}>{r.status}</span></td></tr>)}</tbody></table></section>
  <section className="grid2"><div className="panel"><h2>QC Gate</h2><div className="checks">{["Identity mapping","Contract / RS %","N2A incentive exclusion","Bank string integrity","PAN / TDS","Duplicate payment","Recovery","Deduction cap"].map(x=><div key={x}>✓ {x}</div>)}</div></div><div className="panel"><h2>Configurable Caps</h2><label>Marketing Cap<input defaultValue="30%" /></label><label>COP Cap<input defaultValue="30%" /></label><label>Payment Threshold<input defaultValue="₹100" /></label><button>Simulation Mode</button></div></section>
 </>:<>
  <header><div><div className="eyebrow">PHASE 2</div><h1>Historical Import Center</h1><p>Import the previously processed monthly workbooks without altering the originals.</p></div></header>
  <section className="panel importCard"><h2>Upload processed workbook</h2><p className="muted">The importer fingerprints the file, detects sheets, maps headers, preserves raw rows and creates normalized payment events.</p><input type="file" accept=".xlsx,.xlsm" onChange={e=>setFile(e.target.files?.[0]??null)}/><div className="uploadRow"><span>{file?file.name:"No file selected"}</span><button disabled={!file||busy} onClick={upload}>{busy?"Importing...":"Import Historical File"}</button></div>{result&&<pre className="result">{JSON.stringify(result,null,2)}</pre>}</section>
  <section className="panel"><h2>What Phase 2 does</h2><div className="flow">{["Checksum duplicate guard","Sheet classification","Header mapping","Raw immutable row storage","Payment event normalization","Next: historical master enrichment"].map((x,i)=><div className="flowItem" key={x}><b>{i+1}</b><span>{x}</span></div>)}</div></section>
 </>}</main></div>
}
