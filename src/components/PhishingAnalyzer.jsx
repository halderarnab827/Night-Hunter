import { useState } from "react";
import { AlertTriangle, CheckCircle2, CircleGauge, Link, RefreshCw, Search, ShieldAlert, ShieldCheck } from "lucide-react";

function Metric({ label, value, tone }) {
  return <article className={`phishing-metric ${tone}`}><span>{label}</span><strong>{value}</strong></article>;
}

export default function PhishingAnalyzer() {
  const [target, setTarget] = useState("");
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function analyze(event) {
    event.preventDefault();
    if (!target.trim()) { setError("Enter a URL to analyze."); return; }
    setLoading(true); setError(""); setReport(null);
    try {
      const response = await fetch("/api/phishing", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ target: target.trim() }) });
      const data = await response.json();
      if (!response.ok || !data.success) throw new Error(data.error || "Analysis failed.");
      setReport(data.report);
    } catch (requestError) { setError(requestError.message); }
    finally { setLoading(false); }
  }

  const metrics = report?.metrics || {};
  const findings = report?.findings || [];

  return <section className="phishing-page">
    <header className="module-header phishing-header"><div className="module-heading"><div className="module-heading-icon"><ShieldAlert size={24} /></div><div><p className="eyebrow">NIGHT HUNTER · PHISHING ANALYSIS</p><h2>Link Inspector</h2><p className="subtitle">Detect · Verify · Analyze</p></div></div><div className={`module-state ${loading ? "busy" : ""}`}><span />{loading ? "ANALYZING" : "READY"}</div></header>

    <div className="phishing-workspace">
      <form className="phishing-scan-card" onSubmit={analyze}><div className="phishing-card-heading"><div><span>SUSPICIOUS LINK</span><h3>Inspect a URL</h3></div><Link size={19} /></div><label className="phishing-input"><Link size={18} /><input value={target} onChange={(event) => setTarget(event.target.value)} placeholder="https://example.com/login" disabled={loading} /></label><button className="phishing-run-button" type="submit" disabled={loading}>{loading ? <RefreshCw className="spin-icon" size={17} /> : <Search size={17} />}{loading ? "ANALYZING LINK" : "ANALYZE URL"}</button>{error && <p className="phishing-error"><AlertTriangle size={16} />{error}</p>}<p className="phishing-note">Passive URL analysis only: the hosted analyzer does not open the destination page or follow redirects.</p></form>
      <aside className="phishing-check-card"><CircleGauge size={24} /><span>PASSIVE INSPECTION</span><h3>Signals we check</h3><ul><li><i /> URL structure and encoding</li><li><i /> Suspicious words and TLDs</li><li><i /> Brand impersonation signals</li><li><i /> Hostname and URL indicators only</li></ul></aside>
    </div>

    {report ? <><div className="phishing-metrics"><Metric label="RISK SCORE" value={`${report.risk_score}/100`} tone="violet" /><Metric label="RISK LEVEL" value={report.risk_level} tone="pink" /><Metric label="FINDINGS" value={metrics.total_findings || 0} tone="blue" /><Metric label="REDIRECTS" value={report.redirect_chain?.length || 0} tone="green" /></div><section className="phishing-results"><div className="phishing-results-heading"><div><p className="eyebrow">ANALYSIS RESULTS</p><h3>Risk Indicators</h3><span>{report.normalized_url}</span></div><ShieldCheck size={21} /></div>{findings.length ? <div className="phishing-findings">{findings.map((finding, index) => <article className="phishing-finding" key={`${finding.title}-${index}`}><div><AlertTriangle size={19} /></div><section><header><strong>{finding.title}</strong><b className={finding.severity?.toLowerCase()}>{finding.severity}</b></header><p>{finding.description}</p><small>{finding.recommendation || finding.category}</small></section></article>)}</div> : <div className="phishing-safe"><CheckCircle2 size={23} /><div><strong>No suspicious indicators found</strong><p>The URL checks completed without flagging an indicator.</p></div></div>}</section></> : <section className="phishing-standby"><ShieldCheck size={22} /><div><strong>Analysis is ready</strong><p>Paste a link above to see its risk score and URL indicators.</p></div></section>}
  </section>;
}
