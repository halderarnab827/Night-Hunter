import { useState } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  CircleDotDashed,
  Cpu,
  Globe,
  Network,
  Radar,
  Radio,
  RefreshCw,
  Router,
  Server,
  ShieldAlert,
  ShieldCheck,
  Terminal,
  Wifi,
  XCircle,
} from "lucide-react";

function Metric({ icon: Icon, label, value, tone }) {
  return (
    <article className={`advanced-network-metric ${tone}`}>
      <div>
        <Icon size={19} />
      </div>
      <section>
        <span>{label}</span>
        <strong>{value}</strong>
      </section>
    </article>
  );
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
    if (!host) {
      setStatus("TARGET REQUIRED");
      setError("Enter a hostname or IP address.");
      return;
    }

    setScanning(true);
    setStatus("SCANNING");
    setError("");
    setResult(null);
    setProgress([{ type: "system", message: `Preparing Nmap device recon for ${host}` }]);
    setCompletedPorts(0);

    try {
      const response = await fetch("/api/network-security/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target: host }),
      });
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
            setProgress((current) => [
              ...current,
              { type: "system", message: `Scanning ports & identifying device OS` },
            ]);
          } else if (update.type === "resolution") {
            const state = update.resolution.resolved ? "resolved" : "failed";
            setProgress((current) => [
              ...current,
              { type: "system", message: `DNS ${state}: ${update.resolution.host}` },
            ]);
          } else if (update.type === "device_info") {
            const dev = update.device || {};
            setProgress((current) => [
              ...current,
              {
                type: "system",
                message: `Device: ${dev.device_name || "Host"} | OS: ${dev.os_model || "Detected"}`,
              },
            ]);
          } else if (update.type === "port") {
            setCompletedPorts(update.completed);
            setProgress((current) => [...current, { type: "port", result: update.port_result }]);
          } else if (update.type === "banner") {
            setProgress((current) => [
              ...current,
              { type: "system", message: `Collected banner from port ${update.banner.port}` },
            ]);
          } else if (update.type === "error") {
            throw new Error(update.message || "Network scan failed.");
          } else if (update.type === "complete") {
            setResult(update.result);
            setStatus("COMPLETE");
            setProgress((current) => [
              ...current,
              { type: "system", message: "Device recon & port scan complete" },
            ]);
          }
        }

        if (done) break;
      }
    } catch (requestError) {
      setError(requestError.message || "Unable to reach the Night Hunter API.");
      setStatus("API ERROR");
    } finally {
      setScanning(false);
    }
  }

  function reset() {
    setTarget("");
    setStatus("READY");
    setResult(null);
    setError("");
    setProgress([]);
    setCompletedPorts(0);
  }

  const resolution = result?.resolution || {};
  const addresses = resolution.addresses || [];
  const openPorts = result?.open_ports || [];
  const udpPorts = result?.udp_ports || [];
  const services = result?.open_services || [];
  const banners = result?.service_banners || [];
  const hostStatus = result?.host_check?.reachable
    ? "REACHABLE"
    : result
    ? "UNREACHABLE"
    : "AWAITING";

  return (
    <section className="advanced-network-page">
      <header className="module-header network-module-header">
        <div className="module-heading">
          <div className="module-heading-icon">
            <Network size={24} />
          </div>
          <div>
            <p className="eyebrow">NIGHT HUNTER · NETWORK SECURITY</p>
            <h2>Target Device Intelligence & Nmap Recon</h2>
            <p className="subtitle">Discover · Fingerprint OS · Scan TCP & UDP</p>
          </div>
        </div>
        <div className={`module-state ${scanning ? "busy" : status === "COMPLETE" ? "success" : ""}`}>
          <span />
          {status}
        </div>
      </header>

      {/* Prominent LAN Caution Banner */}
      <div className="network-caution-banner">
        <div className="caution-icon-box">
          <AlertTriangle size={18} />
        </div>
        <div>
          <strong>CAUTION:</strong> For local device name, MAC address, and OS model detection,
          the target device should be connected to the <u>SAME local network (LAN / Wi-Fi)</u>.
        </div>
      </div>

      <div className="network-scan-layout">
        <form className="advanced-network-scan-card" onSubmit={runNetworkCheck}>
          <div className="advanced-network-card-heading">
            <div>
              <span>TARGET DEVICE IP / HOST</span>
              <h3>Nmap Reconnaissance Scan</h3>
            </div>
            <Radar size={20} />
          </div>
          <label className="advanced-network-input">
            <Globe size={18} />
            <input
              value={target}
              onChange={(event) => setTarget(event.target.value)}
              placeholder="e.g. 192.168.0.1, 192.168.1.15, or host.local"
              disabled={scanning}
            />
          </label>
          <div className="advanced-network-actions">
            <button className="advanced-network-run" type="submit" disabled={scanning}>
              {scanning ? <RefreshCw className="spin-icon" size={17} /> : <Radar size={17} />}
              {scanning ? "SCANNING TARGET..." : "SCAN TARGET DEVICE"}
            </button>
            {target && !scanning && (
              <button className="advanced-network-reset" onClick={reset} type="button">
                Clear
              </button>
            )}
          </div>
          {error && (
            <p className="advanced-network-error">
              <AlertTriangle size={16} />
              {error}
            </p>
          )}
          <p className="advanced-network-note">
            <ShieldCheck size={15} />
            Scans target device IP for OS model, device name, MAC address, and open TCP/UDP ports.
          </p>
        </form>

        <aside className="network-profile-card">
          <CircleDotDashed size={24} />
          <span>NMAP-STYLE ENGINE</span>
          <h3>Target Device Intelligence</h3>
          <ul>
            <li>
              <i /> Remote OS Model Fingerprint (-O / Heuristics)
            </li>
            <li>
              <i /> Device Name (Reverse DNS / NetBIOS / mDNS)
            </li>
            <li>
              <i /> Hardware MAC & Vendor Discovery
            </li>
            <li>
              <i /> Open TCP Ports & Services Scan
            </li>
            <li>
              <i /> Open UDP Ports Discovery (Nmap -sU)
            </li>
          </ul>
        </aside>
      </div>

      <div className="advanced-network-metrics">
        <Metric icon={Server} label="HOST STATUS" value={hostStatus} tone="blue" />
        <Metric
          icon={Cpu}
          label="OS MODEL"
          value={result?.os_model ? result.os_model.split("(")[0].trim() : "—"}
          tone="violet"
        />
        <Metric
          icon={Terminal}
          label="TCP OPEN PORTS"
          value={result ? openPorts.length : "—"}
          tone="green"
        />
        <Metric
          icon={Radio}
          label="UDP OPEN (-sU)"
          value={result ? udpPorts.length : "—"}
          tone="pink"
        />
      </div>

      {!result ? (
        scanning ? (
          <section className="network-live-progress">
            <div className="network-live-heading">
              <div>
                <span>LIVE SCAN PROGRESS</span>
                <h3>Scanning Target Device & Fingerprinting OS</h3>
              </div>
              <b>
                {completedPorts} / {totalPorts}
              </b>
            </div>
            <div className="network-progress-bar">
              <i style={{ width: `${(completedPorts / totalPorts) * 100}%` }} />
            </div>
            <div className="network-event-feed">
              {progress
                .slice(-12)
                .reverse()
                .map((entry, index) =>
                  entry.type === "port" ? (
                    <article
                      className="network-port-event"
                      key={`${entry.result.port}-${index}`}
                    >
                      <span>
                        {entry.result.protocol || "TCP"} {entry.result.port}
                      </span>
                      <b>{entry.result.service}</b>
                      <em className={entry.result.state.toLowerCase()}>
                        {entry.result.state}
                      </em>
                      <small>
                        {entry.result.response_time === null
                          ? "—"
                          : `${entry.result.response_time} ms`}
                      </small>
                    </article>
                  ) : (
                    <p key={`${entry.message}-${index}`}>
                      <i />
                      {entry.message}
                    </p>
                  )
                )}
            </div>
          </section>
        ) : (
          <section className="network-readiness-card">
            <div className="network-radar">
              <Wifi size={28} />
              <i />
              <i />
              <i />
            </div>
            <div>
              <span>RECON ENGINE READY</span>
              <h3>Enter a Target Device IP to Scan</h3>
              <p>
                Provide the IP of any device on the same local network (LAN / Wi-Fi) to discover its
                device name, operating system model, MAC address, and open TCP/UDP ports.
              </p>
            </div>
          </section>
        )
      ) : (
        <>
          {/* Target Device Intelligence Card */}
          <section className="network-device-recon-card">
            <div className="recon-card-header">
              <div className="recon-card-title">
                <Server size={22} />
                <div>
                  <span>TARGET DEVICE INTELLIGENCE</span>
                  <h3>{result.device_name || result.target}</h3>
                </div>
              </div>
              <span className="recon-engine-tag">{result.scan_engine || "Nmap Engine"}</span>
            </div>
            <div className="recon-details-grid">
              <div className="recon-detail-cell">
                <label>TARGET IP</label>
                <strong>{result.ip_address || result.target}</strong>
              </div>
              <div className="recon-detail-cell">
                <label>DEVICE NAME</label>
                <strong>{result.device_name || "Unknown"}</strong>
              </div>
              <div className="recon-detail-cell highlight">
                <label>OS MODEL & FINGERPRINT</label>
                <strong className="os-name-pill">{result.os_model || "Unknown OS"}</strong>
              </div>
              <div className="recon-detail-cell">
                <label>DEVICE TYPE</label>
                <strong style={{ textTransform: "capitalize" }}>
                  {result.device_type || "general purpose"}
                </strong>
              </div>
              <div className="recon-detail-cell">
                <label>MAC ADDRESS / VENDOR</label>
                <strong>
                  {result.mac_address ? (
                    `${result.mac_address}${result.mac_vendor ? ` (${result.mac_vendor})` : ""}`
                  ) : (
                    <span style={{ color: "#7a87a7" }}>
                      Remote / Loopback (MAC available for LAN hosts)
                    </span>
                  )}
                </strong>
              </div>
            </div>
          </section>

          <div className="advanced-network-results-grid">
            {/* TCP Ports */}
            <section className="network-result-card">
              <div className="result-card-heading">
                <div>
                  <span>PORT SCAN</span>
                  <h3>Open TCP Ports ({openPorts.length})</h3>
                </div>
                <Terminal size={19} />
              </div>
              {openPorts.length ? (
                <div className="advanced-port-list">
                  {openPorts.map((port) => (
                    <article key={`tcp-${port.port}`}>
                      <b>{port.port}</b>
                      <div>
                        <strong>{port.service}</strong>
                        <span>TCP {port.response_time ? `· ${port.response_time} ms` : ""}</span>
                      </div>
                      <em>OPEN</em>
                    </article>
                  ))}
                </div>
              ) : (
                <div className="result-empty">
                  <CheckCircle2 size={21} />
                  <p>No open TCP ports found on scanned ports.</p>
                </div>
              )}
            </section>

            {/* UDP Ports (Nmap -sU) */}
            <section className="network-result-card">
              <div className="result-card-heading">
                <div>
                  <span>UDP PORT SCAN (NMAP -sU)</span>
                  <h3>Open UDP Ports ({udpPorts.length})</h3>
                </div>
                <Radio size={19} />
              </div>
              {udpPorts.length ? (
                <div className="advanced-port-list">
                  {udpPorts.map((port) => (
                    <article key={`udp-${port.port}`}>
                      <b style={{ color: "#ff8ee8" }}>{port.port}</b>
                      <div>
                        <strong>{port.service}</strong>
                        <span>UDP</span>
                      </div>
                      <em className="udp-pill">{port.state || "OPEN|FILTERED"}</em>
                    </article>
                  ))}
                </div>
              ) : (
                <div className="result-empty">
                  <CheckCircle2 size={21} />
                  <p>No responding UDP services found on scanned ports.</p>
                </div>
              )}
            </section>
          </div>

          {banners.length > 0 && (
            <section className="banner-result-card">
              <div className="result-card-heading">
                <div>
                  <span>SERVICE DETAILS</span>
                  <h3>HTTP Banners</h3>
                </div>
                <Wifi size={19} />
              </div>
              {banners.map((banner) => (
                <article key={banner.port}>
                  <b>PORT {banner.port}</b>
                  <code>{banner.banner || banner.error || "No banner returned."}</code>
                </article>
              ))}
            </section>
          )}
        </>
      )}
    </section>
  );
}
