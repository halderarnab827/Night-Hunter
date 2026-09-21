import { useEffect } from "react";
import {
  ArrowUpRight,
  Check,
  ChevronDown,
  Download,
  Globe2,
  KeyRound,
  Laptop,
  Network,
  ShieldCheck,
  Smartphone,
  Terminal,
} from "lucide-react";
import "./LandingPage.css";

const releaseBase = "https://github.com/halderarnab827/Night-Hunter/releases/download/v1.0.2";

const downloads = [
  { icon: Laptop, name: "Windows", detail: "Desktop dashboard · .exe", href: `${releaseBase}/NightHunter.exe`, action: "Download for Windows" },
  { icon: Terminal, name: "Linux", detail: "Terminal edition · .tar.gz", href: `${releaseBase}/night-hunter-linux.tar.gz`, action: "Download for Linux" },
  { icon: Smartphone, name: "Termux", detail: "Android terminal · .zip", href: `${releaseBase}/night-hunter-termux.zip`, action: "Download for Termux" },
];

export default function LandingPage() {
  useEffect(() => {
    document.title = "Night Hunter - Defensive Security Platform | Nighthunter";
  }, []);

  return (
    <div className="landing-root">
      <header className="landing-nav">
        <a className="landing-brand" href="#top" aria-label="Night Hunter home">
          <img src="/night-hunter-logo.jpeg" alt="Night Hunter Logo" />
          <span>NIGHT <b>HUNTER</b></span>
        </a>
        <nav>
          <a href="#features">Platform</a>
          <a href="#downloads">Downloads</a>
          <a href="#how-it-works">How to Use</a>
        </nav>
        <a className="nav-app-link" href="#downloads">Download <Download size={15} /></a>
      </header>

      <main id="top">
        <section className="premium-hero">
          <div className="hero-orbit orbit-one" />
          <div className="hero-orbit orbit-two" />
          <div className="hero-grid-lines" />
          <div className="hero-copy">
            <p className="landing-eyebrow"><span /> DEFENSIVE SECURITY PLATFORM</p>
            <h1>See the threat.<br /><em>Own the response.</em></h1>
            <p className="hero-description">A focused security workspace for authorized analysis, penetration testing, and defensive auditing across your devices.</p>
            <div className="hero-actions">
              <a className="hero-primary" href="#downloads">Download Night Hunter <Download size={18} /></a>
              <a className="hero-secondary" href="#how-it-works">How to Use <ChevronDown size={17} /></a>
            </div>
            <div className="hero-proof">
              <span><Check size={14} /> Windows, Linux & Android</span>
              <span><Check size={14} /> Built for authorized testing</span>
            </div>
          </div>
          <div className="hero-mark" aria-hidden="true">
            <div className="mark-scan" />
            <img src="/night-hunter-logo.jpeg" alt="Night Hunter Logo" />
            <div className="mark-caption">NIGHT HUNTER <span>01 / DEFENSIVE OPS</span></div>
          </div>
          <p className="hero-scroll">SCROLL TO EXPLORE <ChevronDown size={15} /></p>
        </section>

        <section className="statement-section" id="features">
          <p className="landing-eyebrow"><span /> THE NIGHT HUNTER PLATFORM</p>
          <div className="statement-heading">
            <h2>One command center.<br />A clearer security picture.</h2>
            <p>Designed for people who need a refined place to inspect their own systems, understand findings, and act with confidence.</p>
          </div>
          <div className="feature-columns">
            <article><Globe2 /><h3>Web intelligence</h3><p>Inspect security headers, endpoints, technologies, and defensive recommendations.</p></article>
            <article><Network /><h3>Network visibility</h3><p>Review authorized hosts, common services, and open ports with live results.</p></article>
            <article><KeyRound /><h3>Identity & crypto</h3><p>Analyze password strength, inspect suspicious links, and compare cryptographic outputs.</p></article>
          </div>
        </section>

        <section className="downloads-section" id="downloads">
          <div className="downloads-title"><p className="landing-eyebrow"><span /> DOWNLOADS</p><h2>Choose your<br /><em>environment.</em></h2></div>
          <div className="download-list">
            {downloads.map(({ icon: Icon, name, detail, href, action }) => (
              <a className="download-row" href={href} key={name}>
                <span className="download-icon"><Icon size={23} /></span>
                <span><strong>{name}</strong><small>{detail}</small></span>
                <span className="download-action">{action} <ArrowUpRight size={18} /></span>
              </a>
            ))}
          </div>
        </section>

        <section className="install-section" id="how-it-works">
          <div>
            <p className="landing-eyebrow"><span /> COMPLETE USER GUIDELINE</p>
            <h2>Installation &amp;<br />Troubleshooting</h2>
            <div style={{ marginTop: '20px', padding: '16px', borderRadius: '6px', background: 'rgba(154, 85, 255, 0.1)', border: '1px solid rgba(154, 85, 255, 0.3)', color: '#d5c6e6', fontSize: '13px', lineHeight: '1.6' }}>
              <strong style={{ color: '#fff', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                <ShieldCheck size={16} color="#4ade80" /> 100% Safe &amp; Open Source
              </strong>
              Night Hunter runs entirely locally on your machine with no hidden telemetry or external tracking. All source code is publicly auditable on GitHub.
            </div>
          </div>
          <ol>
            <li>
              <b>WINDOWS</b>
              <span>
                <strong>Windows 10 / 11 Setup &amp; Safety Verification</strong>
                <small>1. Click <b>"Download for Windows"</b> to get <code>NightHunter.exe</code>.</small>
                <small>2. Double-click the file to open.</small>
                <small style={{ marginTop: '6px', background: 'rgba(255,255,255,0.06)', padding: '8px 12px', borderRadius: '4px', borderLeft: '3px solid #f24fcf' }}>
                  <b style={{ color: '#fff' }}>Windows SmartScreen Note:</b> Because Night Hunter is an open-source project without a costly enterprise signing certificate, Windows Defender may show <em>"Windows protected your PC"</em>.
                  <br />&rarr; Click <b>"More info"</b> and then <b>"Run anyway"</b>.
                </small>
                <small style={{ color: '#dd9dff', marginTop: '6px' }}>&#10003; The local engine starts and automatically opens your dashboard at <code>http://127.0.0.1:5000</code>.</small>
              </span>
            </li>
            <li>
              <b>LINUX</b>
              <span>
                <strong>Linux (Ubuntu, Kali, Debian, Arch, Mint)</strong>
                <small>1. Download <code>night-hunter-linux.tar.gz</code>.</small>
                <small>2. Open terminal and extract: <code>tar -xzf night-hunter-linux.tar.gz &amp;&amp; cd night-hunter-linux</code></small>
                <small>3. Run installer: <code>bash install.sh</code></small>
                <small>4. Launch anytime from terminal: <code>NightHunter</code> (or <code>nighthunter</code>)</small>
                <small style={{ marginTop: '6px', background: 'rgba(255,255,255,0.06)', padding: '8px 12px', borderRadius: '4px', borderLeft: '3px solid #dd9dff' }}>
                  <b style={{ color: '#fff' }}>If terminal says "command not found":</b>
                  <br />Run this one command to link it globally:
                  <br /><code style={{ color: '#4ade80' }}>sudo ln -sf ~/.local/bin/NightHunter /usr/local/bin/NightHunter</code>
                  <br />Or run directly: <code>~/.local/bin/NightHunter</code>
                </small>
              </span>
            </li>
            <li>
              <b>TERMUX</b>
              <span>
                <strong>Android Setup via Termux</strong>
                <small>1. Download <code>night-hunter-termux.zip</code> on your Android device.</small>
                <small>2. In Termux, navigate to downloads: <code>cd ~/storage/downloads &amp;&amp; unzip night-hunter-termux.zip</code></small>
                <small>3. Run installer: <code>cd night-hunter-termux &amp;&amp; bash termux-install.sh</code></small>
                <small>4. Start anytime by typing: <code>NightHunter</code></small>
              </span>
            </li>
          </ol>
        </section>
      </main>

      <footer className="landing-footer">
        <div className="landing-brand"><img src="/night-hunter-logo.jpeg" alt="Night Hunter Logo" /><span>NIGHT <b>HUNTER</b></span></div>
        <p>Defensive tooling for authorized security testing.</p>
        <a href="#downloads">Download Night Hunter <Download size={15} /></a>
      </footer>
    </div>
  );
}
