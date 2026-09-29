import { useEffect, useState } from "react";

type Status = "SUCCESS" | "FAILED" | "REVERSED";

const sample = [
  { show: "SHOW-10021", book: "BOOK-20021", author: "AUTH-30021", type: "NOVEL", amount: 18425.5, status: "SUCCESS" as Status },
  { show: "SHOW-10022", book: "BOOK-20022", author: "AUTH-30022", type: "SERIES", amount: 12840, status: "FAILED" as Status },
  { show: "SHOW-10023", book: "BOOK-20023", author: "AUTH-30023", type: "N2A/A2A", amount: 9210.25, status: "REVERSED" as Status }
];

export default function App() {
  const [month, setMonth] = useState("August 2026");
  const [view, setView] = useState("All");
  const [api, setApi] = useState("checking...");
  const rows = view === "All" ? sample : sample.filter(r => r.type === view);

  useEffect(() => {
    fetch("/api/health").then(r => r.json()).then(d => setApi(d.status)).catch(() => setApi("backend offline"));
  }, []);

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">Creator Payout<br/>Control Tower</div>
        {["Dashboard","Monthly Cycle","Author","Book","Show","Novel","Series","N2A/A2A","UWT","Ledger","Exceptions","Rules"].map(x =>
          <div className={x==="Dashboard" ? "nav active" : "nav"} key={x}>{x}</div>
        )}
      </aside>
      <main className="main">
        <header>
          <div><div className="eyebrow">PHASE 1 LOCAL PREVIEW</div><h1>Payment Operations</h1><p>Historical foundation, UWT processing and ledger controls.</p></div>
          <div className="controls">
            <select value={month} onChange={e => setMonth(e.target.value)}><option>August 2026</option><option>July 2026</option><option>June 2026</option><option>May 2026</option></select>
            <select value={view} onChange={e => setView(e.target.value)}><option>All</option><option>NOVEL</option><option>SERIES</option><option>N2A/A2A</option></select>
          </div>
        </header>
        <section className="cards">
          {[
            ["Ready for Payout","2,341"],["On Hold","145"],["Gross","₹52.44M"],["Net Payable","₹21.18M"],["Success","2,301"],["Retry Pool","40"]
          ].map(([label,value]) => <div className="card" key={label}><span>{label}</span><strong>{value}</strong></div>)}
        </section>
        <section className="panel">
          <div className="panelHead"><div><h2>Show-Level Payment Ledger</h2><p>{month} · {view}</p></div><span className="health">API {api}</span></div>
          <table><thead><tr><th>Show ID</th><th>Book ID</th><th>Author ID</th><th>Type</th><th>Net</th><th>Status</th></tr></thead>
          <tbody>{rows.map(r => <tr key={r.show}><td>{r.show}</td><td>{r.book}</td><td>{r.author}</td><td>{r.type}</td><td>₹{r.amount.toLocaleString("en-IN",{minimumFractionDigits:2})}</td><td><span className={"pill "+r.status.toLowerCase()}>{r.status}</span></td></tr>)}</tbody></table>
        </section>
        <section className="grid2">
          <div className="panel"><h2>QC Gate</h2><div className="checks">{["Identity mapping","Contract / RS %","N2A incentive exclusion","Bank string integrity","PAN / TDS","Duplicate payment","Recovery","Deduction cap"].map(x => <div key={x}>✓ {x}</div>)}</div></div>
          <div className="panel"><h2>Configurable Caps</h2><label>Marketing Cap<input defaultValue="30%" /></label><label>COP Cap<input defaultValue="30%" /></label><label>Payment Threshold<input defaultValue="₹100" /></label><button>Simulation Mode</button></div>
        </section>
      </main>
    </div>
  );
}
