import { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2, Cpu, Download, Network, Radar, RefreshCw, Server, ShieldCheck, Terminal } from "lucide-react";

export default function NmapWorkspace() {
  const [status, setStatus] = useState(null);
  const [target, setTarget] = useState("");
  const [profile, setProfile] = useState("inventory");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [running, setRunning] = useState(false);

  useEffect(() => {
    fetch("/api/network-security/nmap/status")
      .then((response) => response.json())
      .then((data) => setStatus(data.nmap))
      .catch(() => setStatus({ available: false, reason: "Unable to check local Nmap availability.", profiles: [] }));
  }, []);

  async function scan(event) {
    event.preventDefault();
    if (!target.trim()) { setError("Enter a host or IP address you are authorized to scan."); return; }
    setRunning(true); setError(""); setResult(null);
    try {
      const response = await fetch("/api/network-security/nmap", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ target: target.trim(), profile }) });
      const data = await response.json();
      if (!response.ok || !data.success) throw new Error(data.error || "Nmap scan failed.");
      setResult(data);
    } catch (scanError) { setError(scanError.message); } finally { setRunning(false); }
  }

  const profiles = status?.profiles || [];
  const selected = profiles.find((item) => item.id === profile);
  const host = result?.hosts?.[0];
  const openPorts = host?.ports?.filter((port) => port.state === "OPEN") || [];

  return <section className="nmap-workspace">
    <header className="module-header network-module-header"><div className="module-heading"><div className="module-heading-icon"><Radar size={24} /></div><div><p className="eyebrow">NIGHT HUNTER · LOCAL NMAP</p><h2>Verified Nmap Workspace</h2><p className="subtitle">Named profiles · XML evidence · no simulated findings</p></div></div><div className={`module-state ${running ? "busy" : status?.available ? "success" : ""}`}><span />{running ? "SCANNING" : status?.available ? "NMAP READY" : "NMAP UNAVAILABLE"}</div></header>

    {!status?.available && status?.runtime === "cloud" && <section className="local-access-notice"><div className="local-access-icon"><Download size={22} /></div><div><span>COMPLETE LOCAL ACCESS</span><h3>Download Night Hunter for verified Nmap output</h3><p>The cloud edition intentionally does not run LAN-level Nmap scans. For full TCP/UDP profiles, OS fingerprint attempts, MAC/vendor discovery, and the complete local evidence report, use the Windows, Linux, or Termux edition on your own device.</p><div className="local-access-links"><a href="/downloads/night-hunter-windows.zip">Windows</a><a href="/downloads/night-hunter-linux.tar.gz">Linux</a><a href="/downloads/night-hunter-termux.zip">Termux</a></div></div></section>}
    <div className="network-caution-banner"><div className="caution-icon-box"><AlertTriangle size={18} /></div><div><strong>LOCAL ONLY:</strong> Full Nmap profiles run only on the Windows, Linux, or Termux installation. The hosted cloud app cannot scan from your LAN or provide reliable OS/MAC results. Use only with targets you own or are authorized to assess.</div></div>

    <form className="nmap-form" onSubmit={scan}>
      <label>AUTHORIZED TARGET<input value={target} onChange={(event) => setTarget(event.target.value)} disabled={running || !status?.available} placeholder="192.168.1.20 or host.local" /></label>
      <label>NMAP PROFILE<select value={profile} onChange={(event) => setProfile(event.target.value)} disabled={running || !status?.available}>{profiles.map((item) => <option key={item.id} value={item.id}>{item.label}</option>)}</select></label>
      <button className="advanced-network-run" disabled={running || !status?.available} type="submit">{running ? <RefreshCw className="spin-icon" size={17} /> : <Radar size={17} />}{running ? "RUNNING NMAP..." : "RUN LOCAL NMAP"}</button>
      {error && <p className="advanced-network-error"><AlertTriangle size={16} />{error}</p>}
      <p className="advanced-network-note"><ShieldCheck size={15} />{status?.reason || "Checking local Nmap…"}</p>
    </form>

    {selected && <section className="nmap-profile-note"><Terminal size={18} /><div><strong>{selected.label}</strong><p>{selected.description}</p>{selected.requires_admin && <small>OS or UDP features may require Administrator/root privileges.</small>}</div></section>}

    {result && <><section className="nmap-results-heading"><div><span>VERIFIED NMAP REPORT</span><h3>{host?.hostname || host?.addresses?.[0] || result.target}</h3><code>{result.engine} · {result.command}</code></div><Network size={22} /></section>
      <div className="advanced-network-metrics"><Metric icon={Server} label="HOST STATUS" value={host?.status?.toUpperCase() || "UNKNOWN"} tone="blue" /><Metric icon={Cpu} label="OS RESULT" value={host?.os || "INCONCLUSIVE"} tone="violet" /><Metric icon={Terminal} label="OPEN PORTS" value={openPorts.length} tone="green" /><Metric icon={Network} label="PROFILE" value={result.profile.label} tone="pink" /></div>
      <section className="network-result-card"><div className="result-card-heading"><div><span>MEASURED PORT RESULTS</span><h3>Open services ({openPorts.length})</h3></div><Server size={19} /></div>{openPorts.length ? <div className="advanced-port-list">{openPorts.map((port) => <article key={`${port.protocol}-${port.port}`}><b>{port.port}</b><div><strong>{port.service}</strong><span>{port.protocol} {port.product ? `· ${port.product} ${port.version}` : ""}</span></div><em>OPEN</em></article>)}</div> : <div className="result-empty"><CheckCircle2 size={21} /><p>No open ports were reported by this Nmap profile.</p></div>}</section>
      <p className="nmap-evidence-note">{result.warning}</p></>}
  </section>;
}

function Metric({ icon: Icon, label, value, tone }) { return <article className="network-metric-card"><div className={`network-metric-icon ${tone}`}><Icon size={19} /></div><div><span>{label}</span><strong>{value}</strong></div></article>; }
