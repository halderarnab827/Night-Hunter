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
  return (
    <div className="landing-root">
      <header className="landing-nav">
        <a className="landing-brand" href="#top" aria-label="Night Hunter home">
          <img src="/night-hunter-logo.jpeg" alt="" />
          <span>NIGHT <b>HUNTER</b></span>
        </a>
        <nav>
          <a href="#features">Platform</a>
          <a href="#downloads">Downloads</a>
          <a href="#how-it-works">Install</a>
        </nav>
        <a className="nav-app-link" href="/app">Launch dashboard <ArrowUpRight size={15} /></a>
      </header>

      <main id="top">
        <section className="premium-hero">
          <div className="hero-orbit orbit-one" />
          <div className="hero-orbit orbit-two" />
          <div className="hero-grid-lines" />
          <div className="hero-copy">
            <p className="landing-eyebrow"><span /> DEFENSIVE SECURITY PLATFORM</p>
            <h1>See the threat.<br /><em>Own the response.</em></h1>
            <p className="hero-description">A focused security workspace for authorized analysis, from your browser to your command line.</p>
            <div className="hero-actions">
              <a className="hero-primary" href="#downloads">Get Night Hunter <Download size={18} /></a>
              <a className="hero-secondary" href="/app">Explore dashboard <ArrowUpRight size={17} /></a>
            </div>
            <div className="hero-proof">
              <span><Check size={14} /> Windows, Linux & Android</span>
              <span><Check size={14} /> Built for authorized testing</span>
            </div>
          </div>
          <div className="hero-mark" aria-hidden="true">
            <div className="mark-scan" />
            <img src="/night-hunter-logo.jpeg" alt="" />
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
          <div><p className="landing-eyebrow"><span /> SIMPLE BY DESIGN</p><h2>From download<br />to defense.</h2></div>
          <ol>
            <li><b>01</b><span><strong>Choose your platform</strong><small>Download the release that matches your device.</small></span></li>
            <li><b>02</b><span><strong>Install once</strong><small>Windows opens the dashboard; Linux and Termux install the NightHunter command.</small></span></li>
            <li><b>03</b><span><strong>Analyze responsibly</strong><small>Use Night Hunter only on systems and networks you own or are authorized to assess.</small></span></li>
          </ol>
        </section>
      </main>

      <footer className="landing-footer">
        <div className="landing-brand"><img src="/night-hunter-logo.jpeg" alt="" /><span>NIGHT <b>HUNTER</b></span></div>
        <p>Defensive tooling for authorized security testing.</p>
        <a href="/app">Launch dashboard <ArrowUpRight size={15} /></a>
      </footer>
    </div>
  );
}
