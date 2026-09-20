import { useState } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  CircleDotDashed,
  Globe,
  Network,
  Radar,
  Radio,
  RefreshCw,
  Router,
  Server,
  ShieldCheck,
  Terminal,
  Wifi,
  XCircle,
} from "lucide-react";

function Metric({ icon: Icon, label, value, tone }) {
  return <article className={`advanced-network-metric ${tone}`}><div><Icon size={19} /></div><section><span>{label}</span><strong>{value}</strong></section></article>;
}

export default function AdvancedNetworkSecurity() {
  const [target, setTarget] = useState("");
  const [status, setStatus] = useState("READY");
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [progress, setProgress] = useState([]);
  const [completedPorts, setCompletedPorts] = useState(0);
  const [totalPorts, setTotalPorts] = useState(40);

  async function runNetworkCheck(event) {
    event.preventDefault();
    const host = target.trim();
    if (!host) { setStatus("TARGET REQUIRED"); setError("Enter a hostname or IP address."); return; }

    setScanning(true); setStatus("SCANNING"); setError(""); setResult(null);
    setProgress([{ type: "system", message: `Preparing advanced scan for ${host}` }]);
    setCompletedPorts(0);
    try {
      const response = await fetch("/api/network-security/stream", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ target: host }) });
      const contentType = response.headers.get("content-type") || "";

      if (!response.ok || !response.body || !contentType.includes("text/event-stream")) {
        const rawResponse = await response.text();
        let message = "Advanced network scan failed.";

        try {
          message = JSON.parse(rawResponse).error || message;
        } catch {
          if (rawResponse.toLowerCase().includes("<!doctype")) {
            message = "Night Hunter Server is out of date. Close its terminal and launch start_night_hunter.bat again.";
          }
        }

        throw new Error(message);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let pending = "";

      while (true) {
        const { value, done } = await reader.read();
        pending += decoder.decode(value || new Uint8Array(), { stream: !done });
        const messages = pending.split("\n\n");
        pending = messages.pop();

        for (const message of messages) {
          const dataLine = message.split("\n").find((line) => line.startsWith("data: "));
          if (!dataLine) continue;
          const update = JSON.parse(dataLine.slice(6));

          if (update.type === "started") {
            setTotalPorts(update.total_ports);
            setProgress((current) => [...current, { type: "system", message: `Scanning ${update.total_ports} common TCP ports` }]);
          } else if (update.type === "resolution") {
            const state = update.resolution.resolved ? "resolved" : "failed";
            setProgress((current) => [...current, { type: "system", message: `DNS ${state}: ${update.resolution.host}` }]);
          } else if (update.type === "port") {
            setCompletedPorts(update.completed);
            setProgress((current) => [...current, { type: "port", result: update.port_result }]);
          } else if (update.type === "banner") {
            setProgress((current) => [...current, { type: "system", message: `Collected banner from port ${update.banner.port}` }]);
          } else if (update.type === "error") {
            throw new Error(update.message || "Network scan failed.");
          } else if (update.type === "complete") {
            setResult(update.result); setStatus("COMPLETE");
            setProgress((current) => [...current, { type: "system", message: "Advanced scan complete" }]);
          }
        }

        if (done) break;
      }
    } catch (requestError) {
      setError(requestError.message || "Unable to reach the Night Hunter API."); setStatus("API ERROR");
    } finally { setScanning(false); }
  }

  function reset() { setTarget(""); setStatus("READY"); setResult(null); setError(""); setProgress([]); setCompletedPorts(0); }

  const resolution = result?.resolution || {};
  const addresses = resolution.addresses || [];
  const openPorts = result?.open_ports || [];
  const services = result?.open_services || [];
  const banners = result?.service_banners || [];
  const hostStatus = result?.host_check?.reachable ? "REACHABLE" : result ? "UNREACHABLE" : "AWAITING";

  return <section className="advanced-network-page">
    <header className="module-header network-module-header">
      <div className="module-heading"><div className="module-heading-icon"><Network size={24} /></div><div><p className="eyebrow">NIGHT HUNTER · NETWORK SECURITY</p><h2>Network Recon</h2><p className="subtitle">Resolve · Discover · Identify</p></div></div>
      <div className={`module-state ${scanning ? "busy" : status === "COMPLETE" ? "success" : ""}`}><span />{status}</div>
    </header>

    <div className="network-scan-layout">
      <form className="advanced-network-scan-card" onSubmit={runNetworkCheck}>
        <div className="advanced-network-card-heading"><div><span>AUTHORIZED TARGET</span><h3>Advanced Service Scan</h3></div><Radar size={20} /></div>
        <label className="advanced-network-input"><Globe size={18} /><input value={target} onChange={(event) => setTarget(event.target.value)} placeholder="hostname, IP address, or https://hostname" disabled={scanning} /></label>
        <div className="advanced-network-actions"><button className="advanced-network-run" type="submit" disabled={scanning}>{scanning ? <RefreshCw className="spin-icon" size={17} /> : <Radar size={17} />}{scanning ? "RUNNING ADVANCED SCAN" : "START ADVANCED SCAN"}</button>{target && !scanning && <button className="advanced-network-reset" onClick={reset} type="button">Clear</button>}</div>
        {error && <p className="advanced-network-error"><AlertTriangle size={16} />{error}</p>}
        <p className="advanced-network-note"><ShieldCheck size={15} />Use only on systems and networks you own or are authorized to test.</p>
      </form>
      <aside className="network-profile-card"><CircleDotDashed size={24} /><span>ADVANCED PROFILE</span><h3>Common-service reconnaissance</h3><ul><li><i /> DNS resolution and host reachability</li><li><i /> 40 common TCP service ports</li><li><i /> Service identification and response time</li><li><i /> Safe HTTP banner collection when available</li></ul></aside>
    </div>

    <div className="advanced-network-metrics"><Metric icon={Server} label="HOST STATUS" value={hostStatus} tone="blue" /><Metric icon={Radio} label="OPEN PORTS" value={result ? result.total_open_ports : "—"} tone="violet" /><Metric icon={Globe} label="IP ADDRESSES" value={result ? addresses.length : "—"} tone="pink" /><Metric icon={Activity} label="SERVICES" value={result ? services.length : "—"} tone="green" /></div>

    {!result ? scanning ? <section className="network-live-progress"><div className="network-live-heading"><div><span>LIVE SCAN PROGRESS</span><h3>Port discovery in progress</h3></div><b>{completedPorts} / {totalPorts}</b></div><div className="network-progress-bar"><i style={{ width: `${(completedPorts / totalPorts) * 100}%` }} /></div><div className="network-event-feed">{progress.slice(-12).reverse().map((entry, index) => entry.type === "port" ? <article className="network-port-event" key={`${entry.result.port}-${index}`}><span>PORT {entry.result.port}</span><b>{entry.result.service}</b><em className={entry.result.state.toLowerCase()}>{entry.result.state}</em><small>{entry.result.response_time === null ? "—" : `${entry.result.response_time} ms`}</small></article> : <p key={`${entry.message}-${index}`}><i />{entry.message}</p>)}</div></section> : <section className="network-readiness-card"><div className="network-radar"><Wifi size={28} /><i /><i /><i /></div><div><span>NETWORK ENGINE</span><h3>Ready for an advanced scan</h3><p>The advanced profile checks 40 common TCP ports and sends each finished result to this panel live.</p></div></section> : <>
      <div className="advanced-network-results-grid"><section className="network-result-card"><div className="result-card-heading"><div><span>HOST INTELLIGENCE</span><h3>Resolution</h3></div><Router size={19} /></div><div className="resolution-rows"><p><b>Target</b><code>{result.target}</code></p><p><b>DNS status</b>{resolution.resolved ? <em className="positive"><CheckCircle2 size={15} />Resolved</em> : <em className="negative"><XCircle size={15} />Failed</em>}</p><div className="address-pills">{addresses.length ? addresses.map((address) => <code key={address}>{address}</code>) : <span>No addresses returned.</span>}</div></div></section>
        <section className="network-result-card"><div className="result-card-heading"><div><span>SERVICE DISCOVERY</span><h3>Open Ports</h3></div><Terminal size={19} /></div>{openPorts.length ? <div className="advanced-port-list">{openPorts.map((port) => <article key={port.port}><b>{port.port}</b><div><strong>{port.service}</strong><span>TCP · {port.response_time ?? "—"} ms</span></div><em>OPEN</em></article>)}</div> : <div className="result-empty"><CheckCircle2 size={21} /><p>No open common ports found.</p></div>}</section></div>
      {banners.length > 0 && <section className="banner-result-card"><div className="result-card-heading"><div><span>SERVICE DETAILS</span><h3>HTTP Banners</h3></div><Wifi size={19} /></div>{banners.map((banner) => <article key={banner.port}><b>PORT {banner.port}</b><code>{banner.banner || banner.error || "No banner returned."}</code></article>)}</section>}
    </>}
  </section>;
}
