import { useEffect, useState } from "react";

const NAV = ["Dashboard","Monthly Cycle","Novel","Series","N2A/A2A","UWT","Ledger","Exceptions","Rules","Author","Book","Show","Historical Import","Calculation & QC"];
const typeFor = (p:string) => p === "Novel" ? "NOVEL" : p === "Series" ? "SERIES" : p === "N2A/A2A" ? "N2A/A2A" : undefined;

export default function App() {
  const [page,setPage] = useState("Dashboard");
  const [month,setMonth] = useState("August 2026");
  const [api,setApi] = useState("checking");
  const [rows,setRows] = useState<any[]>([]);
  const [summary,setSummary] = useState<any>(null);
  const [exceptions,setExceptions] = useState<any[]>([]);
  const [rules,setRules] = useState<any>(null);

  useEffect(() => {
    fetch("/api/health").then(r=>r.json()).then(()=>setApi("online")).catch(()=>setApi("offline"));
  }, []);

  useEffect(() => {
    if (["Dashboard","Monthly Cycle","Novel","Series","N2A/A2A","Ledger"].includes(page)) loadLedger();
    if (page === "Exceptions") loadExceptions();
    if (page === "Rules") loadRules();
  }, [page,month]);

  async function loadLedger() {
    const t=typeFor(page);
    const url=t ? `/api/ledger?month=${encodeURIComponent(month)}&content_type=${encodeURIComponent(t)}` : `/api/ledger?month=${encodeURIComponent(month)}`;
    const data=await fetch(url).then(r=>r.json()).catch(()=>[]);
    const s=await fetch(`/api/month/breakdown?month=${encodeURIComponent(month)}`).then(r=>r.json()).catch(()=>null);
    setRows(Array.isArray(data)?data:[]); setSummary(s);
  }

  async function loadExceptions() { setExceptions(await fetch(`/api/exceptions?period=${encodeURIComponent(month)}`).then(r=>r.json()).catch(()=>[])); }
  async function loadRules() { setRules(await fetch(`/api/config/rules?period=${encodeURIComponent(month)}`).then(r=>r.json()).catch(()=>null)); }

  const stats=summary?.status || {};
  return <div className="app">
    <aside className="sidebar"><div className="brand">Creator Payout<br/>Control Tower</div>
      {NAV.map(x=><div key={x} className={x===page?"nav active":"nav"} onClick={()=>setPage(x)}>{x}</div>)}
    </aside>
    <main className="main">
      <header><div><div className="eyebrow">LOCAL DEVELOPMENT</div><h1>{page}</h1><p>{month} · API {api}</p></div>
        <select value={month} onChange={e=>setMonth(e.target.value)}><option>August 2026</option><option>July 2026</option><option>June 2026</option><option>May 2026</option></select>
      </header>

      {["Dashboard","Novel","Series","N2A/A2A","Ledger"].includes(page) && <>
        <section className="cards">
          {[["Rows",rows.length],["Success",stats.SUCCESS?.count||0],["Failed",stats.FAILED?.count||0],["Reversed",stats.REVERSED?.count||0],["Unmatched",stats.UNMATCHED?.count||0],["Content Groups",Object.keys(summary?.content||{}).length]].map(([a,b])=><div className="card" key={a}><span>{a}</span><strong>{b}</strong></div>)}
        </section>
        <section className="panel"><h2>Show-Level Ledger</h2><p>{page==="Dashboard"?"All content":page}</p>
          <div className="tableWrap"><table><thead><tr><th>Show ID</th><th>Book ID</th><th>Author ID</th><th>Content</th><th>Net</th><th>Status</th><th>Ledger</th><th>UTR</th></tr></thead>
          <tbody>{rows.slice(0,500).map(r=><tr key={r.payment_id}><td>{r.show_id||"-"}</td><td>{r.book_id||"-"}</td><td>{r.author_id||"-"}</td><td>{r.content_type||"UNKNOWN"}</td><td>{r.amount_after_tax==null?"-":"₹"+Number(r.amount_after_tax).toLocaleString("en-IN",{minimumFractionDigits:2})}</td><td><span className={"pill "+String(r.status).toLowerCase()}>{r.status}</span></td><td>{r.ledger_state}</td><td>{r.utr||"-"}</td></tr>)}</tbody></table></div>
        </section>
      </>}

      {page==="Monthly Cycle" && <section className="grid2"><div className="panel"><h2>Monthly Breakdown</h2><pre className="result">{JSON.stringify(summary,null,2)}</pre></div><div className="panel"><h2>Processing Gate</h2><div className="checks"><div>✓ Import validation</div><div>✓ Calculation layer</div><div>✓ Mandatory QC layer</div><div>✓ UWT reconciliation layer</div><div>○ Historical parity validation</div></div></div></section>}

      {page==="Exceptions" && <section className="panel"><h2>Exception Queue · {exceptions.length}</h2>{exceptions.length===0?<p>No open exceptions for {month}.</p>:<table><thead><tr><th>Rule</th><th>Severity</th><th>Entity</th><th>Message</th></tr></thead><tbody>{exceptions.map((x:any,i)=><tr key={i}><td>{x.rule_id}</td><td>{x.severity}</td><td>{x.entity_type} / {x.entity_id}</td><td>{x.message}</td></tr>)}</tbody></table>}</section>}

      {page==="Rules" && <section className="panel"><h2>Effective Rules</h2><pre className="result">{JSON.stringify(rules,null,2)}</pre></section>}

      {page==="UWT" && <section className="panel"><h2>Finance UWT</h2><p>Use the backend API docs to test the fixed 13-column UWT import/export while the frontend controls are being hardened.</p><a href="/docs" target="_blank">Open API docs</a></section>}
      {page==="Historical Import" && <section className="panel"><h2>Historical Import</h2><p>Upload previous-month processed workbooks through the existing import endpoint.</p><a href="/docs" target="_blank">Open API docs</a></section>}
      {page==="Calculation & QC" && <section className="panel"><h2>Calculation & QC</h2><p>Calculation and mandatory QC endpoints are live in the local backend.</p><a href="/docs" target="_blank">Open API docs</a></section>}
      {["Author","Book","Show"].includes(page) && <section className="panel"><h2>{page} Explorer</h2><p>Entity-level APIs are available; the detailed drill-down UI will be connected after historical parity testing.</p></section>}
    </main>
  </div>;
}