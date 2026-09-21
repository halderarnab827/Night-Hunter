import { useEffect, useState } from "react";

import {
  LayoutDashboard,
  Globe,
  LockKeyhole,
  Network,
  ShieldAlert,
  KeyRound,
  FileText,
  Settings,
  Bell,
  Activity,
  Terminal,
  ArrowUpRight,
  ChevronRight,
  Play,
  RotateCcw,
  Sparkles,
  AlertTriangle,
  Download,
  RefreshCw,
  X,
} from "lucide-react";

import "./App.css";
import WebSecurity from "./components/WebSecurity";
import PasswordSecurity from "./components/PasswordSecurity";
import NetworkSecurity from "./components/AdvancedNetworkSecurity";
import PhishingAnalyzer from "./components/PhishingAnalyzer";
import Cryptography from "./components/Cryptography";
import Reports from "./components/Reports";
import SettingsPage from "./components/Settings";
import { applyTheme, readTheme } from "./theme";

const translations = {
  en: { dashboard:"Dashboard", web:"Web Security", password:"Password Security", network:"Network Security", phishing:"Phishing Analyzer", crypto:"Cryptography", reports:"Reports", settings:"Settings", modules:"SECURITY MODULES", preferences:"Preferences", online:"SYSTEM ONLINE", welcome:"Welcome back", mission:"Your security. Our mission.", monitor:"LIVE THREAT MONITOR", activity:"Recent Activity", securityModules:"Security Modules", launch:"Launch" },
  hi: { dashboard:"डैशबोर्ड", web:"वेब सुरक्षा", password:"पासवर्ड सुरक्षा", network:"नेटवर्क सुरक्षा", phishing:"फ़िशिंग विश्लेषक", crypto:"क्रिप्टोग्राफी", reports:"रिपोर्ट", settings:"सेटिंग्स", modules:"सुरक्षा मॉड्यूल", preferences:"पसंद", online:"सिस्टम ऑनलाइन", welcome:"वापसी पर स्वागत है", mission:"आपकी सुरक्षा। हमारा मिशन।", monitor:"लाइव थ्रेट मॉनिटर", activity:"हाल की गतिविधि", securityModules:"सुरक्षा मॉड्यूल", launch:"खोलें" },
  bn: { dashboard:"ড্যাশবোর্ড", web:"ওয়েব সিকিউরিটি", password:"পাসওয়ার্ড সিকিউরিটি", network:"নেটওয়ার্ক সিকিউরিটি", phishing:"ফিশিং বিশ্লেষক", crypto:"ক্রিপ্টোগ্রাফি", reports:"রিপোর্ট", settings:"সেটিংস", modules:"সিকিউরিটি মডিউল", preferences:"পছন্দ", online:"সিস্টেম অনলাইন", welcome:"ফিরে আসার জন্য স্বাগতম", mission:"আপনার নিরাপত্তা। আমাদের লক্ষ্য।", monitor:"লাইভ থ্রেট মনিটর", activity:"সাম্প্রতিক কার্যকলাপ", securityModules:"সিকিউরিটি মডিউল", launch:"চালু করুন" },
  es: { dashboard:"Panel", web:"Seguridad web", password:"Seguridad de contraseña", network:"Seguridad de red", phishing:"Analizador de phishing", crypto:"Criptografía", reports:"Historial", settings:"Ajustes", modules:"MÓDULOS DE SEGURIDAD", preferences:"Preferencias", online:"SISTEMA EN LÍNEA", welcome:"Bienvenido de nuevo", mission:"Tu seguridad. Nuestra misión.", monitor:"MONITOR DE AMENAZAS", activity:"Actividad reciente", securityModules:"Módulos de seguridad", launch:"Abrir" },
};


const isLocal =
  typeof window !== "undefined" &&
  (window.location.hostname === "localhost" ||
   window.location.hostname === "127.0.0.1" ||
   window.location.hostname === "0.0.0.0");


function App() {

  const [activePage, setActivePage] = useState("Dashboard");
  const [language, setLanguage] = useState(() => readTheme().language || "en");
  const [terminalLines, setTerminalLines] = useState([
    "[+] NIGHT HUNTER core initialized.",
    "[+] Security modules loaded.",
    "[+] Report engine loaded.",
    "[+] System ready."
  ]);
  const [showMandatoryModal, setShowMandatoryModal] = useState(() => {
    // Only lock local instances if not yet acknowledged; cloud server runs latest build automatically
    if (!isLocal) return false;
    return sessionStorage.getItem("nh_v103_update_acknowledged") !== "true";
  });
  const [showPatchNotes, setShowPatchNotes] = useState(false);

  function handleDownloadUpdate() {
    window.open("https://night-hunter-f2w4.onrender.com/#downloads", "_blank");
    sessionStorage.setItem("nh_v103_update_acknowledged", "true");
    setShowMandatoryModal(false);
  }

  function handleOpenCloudServer() {
    window.location.href = "https://night-hunter-f2w4.onrender.com/app";
    sessionStorage.setItem("nh_v103_update_acknowledged", "true");
    setShowMandatoryModal(false);
  }

  function handleAcknowledgeUpdate() {
    sessionStorage.setItem("nh_v103_update_acknowledged", "true");
    setShowMandatoryModal(false);
  }

  useEffect(() => {
    applyTheme(readTheme());
    const updateLanguage = (event) => setLanguage(event.detail || "en");
    window.addEventListener("night-hunter-language", updateLanguage);
    return () => window.removeEventListener("night-hunter-language", updateLanguage);
  }, []);

  const t = translations[language] || translations.en;


  const modules = [
    {
      name: "Web Security",
      label: t.web, description: "Scan · Discover · Fix",
      icon: Globe,
    },
    {
      name: "Password Security",
      label: t.password, description: "Audit · Strengthen",
      icon: LockKeyhole,
    },
    {
      name: "Network Security",
      label: t.network, description: "Monitor · Analyze · Protect",
      icon: Network,
    },
    {
      name: "Phishing Analyzer",
      label: t.phishing, description: "Detect · Verify · Analyze",
      icon: ShieldAlert,
    },
    {
      name: "Cryptography",
      label: t.crypto, description: "Encrypt · Decrypt · Hash",
      icon: KeyRound,
    },
    {
      name: "Reports",
      label: t.reports, description: "Generate · Export · Share",
      icon: FileText,
    },
  ];


  function openPage(page) {
    setActivePage(page);
  }


  function launchModule(moduleName) {
    setActivePage(moduleName);

    setTerminalLines((oldLines) => [
      ...oldLines,
      `[>] Opening ${moduleName}...`,
      `[+] ${moduleName} interface ready.`
    ]);
  }


  function resetDashboard() {
    setActivePage("Dashboard");

    setTerminalLines([
      "[+] NIGHT HUNTER core initialized.",
      "[+] Security modules loaded.",
      "[+] Report engine loaded.",
      "[+] System ready."
    ]);
  }

  function renderPageContent() {

    if (activePage === "Dashboard") {
      return <Dashboard />;
    }
    if (activePage === "Web Security") {
  return <WebSecurity />;
    }
    if (activePage === "Password Security") {
      return <PasswordSecurity />;
    }
    if (activePage === "Network Security") {
  return <NetworkSecurity />;
}
    if (activePage === "Phishing Analyzer") {
      return <PhishingAnalyzer />;
    }
    if (activePage === "Cryptography") {
      return <Cryptography />;
    }
    if (activePage === "Reports") {
      return <Reports />;
    }

    if (activePage === "Settings") {
      return <SettingsPage />;
    }


    const selectedModule = modules.find(
      (module) => module.name === activePage
    );


    if (selectedModule) {

      const Icon = selectedModule.icon;

      return (
        <div className="module-page">

          <div className="module-page-header">

            <div>

              <p className="eyebrow">
                NIGHT HUNTER SECURITY MODULE
              </p>

              <h2>
                {selectedModule.name}
              </h2>

              <p className="subtitle">
                {selectedModule.description}
              </p>

            </div>

            <div className="large-module-icon">
              <Icon size={38} />
            </div>

          </div>


          <div className="module-action-grid">

            <div className="action-panel">

              <div className="action-icon">
                <Play size={20} />
              </div>

              <h3>
                Start Module
              </h3>

              <p>
                Launch the {selectedModule.name} engine from the NIGHT HUNTER interface.
              </p>

              <button
                className="primary-action"
                onClick={() => {
                  setTerminalLines((oldLines) => [
                    ...oldLines,
                    `[>] ${selectedModule.name} started.`,
                    `[+] Waiting for target input...`
                  ]);
                }}
              >
                Start
                <ArrowUpRight size={16} />
              </button>

            </div>


            <div className="action-panel">

              <div className="action-icon blue">
                <Terminal size={20} />
              </div>

              <h3>
                Module Terminal
              </h3>

              <p>
                View module activity and backend execution output.
              </p>

              <button
                className="secondary-action"
                onClick={() => {
                  setTerminalLines((oldLines) => [
                    ...oldLines,
                    `[+] ${selectedModule.name} terminal opened.`
                  ]);
                }}
              >
                Open Terminal
              </button>

            </div>


            <div className="action-panel">

              <div className="action-icon pink">
                <FileText size={20} />
              </div>

              <h3>
                Reports
              </h3>

              <p>
                Security reports generated by this module will appear here.
              </p>

              <button
                className="secondary-action"
                onClick={() => openPage("Reports")}
              >
                View Reports
              </button>

            </div>

          </div>


          <div className="module-terminal">

            <div className="panel-header">

              <div>
                <span className="panel-kicker">
                  MODULE CONSOLE
                </span>

                <h3>
                  {selectedModule.name}
                </h3>
              </div>

              <Activity size={18} />

            </div>

            <div className="terminal-body">

              {terminalLines.slice(-8).map((line, index) => (
                <p key={`${line}-${index}`}>
                  {line}
                </p>
              ))}

              <p className="terminal-cursor">
                _
              </p>

            </div>

          </div>


          <button
            className="back-button"
            onClick={resetDashboard}
          >
            <ChevronRight size={16} />
            Back to Dashboard
          </button>

        </div>
      );
    }


    return null;
  }


  function Dashboard() {

    return (
      <section className="dashboard">

        <div className="welcome-row">

          <div>

            <p className="eyebrow">
              SECURITY OPERATIONS CENTER
            </p>

            <h2>
              {t.welcome},{" "}
              <span>Night Hunter</span>
            </h2>

            <p className="subtitle">
              {t.mission}
            </p>

          </div>

          <div className="version">
            NIGHT HUNTER <strong>v1.0</strong>
          </div>

        </div>


        <div className="stats-grid">

          <div className="stat-card">
            <span>MODULES</span>
            <strong>6</strong>
            <small>Security modules</small>
          </div>

          <div className="stat-card">
            <span>TOOLS</span>
            <strong>42</strong>
            <small>Available tools</small>
          </div>

          <div className="stat-card">
            <span>FINDINGS</span>
            <strong>1.2K</strong>
            <small>Security findings</small>
          </div>

          <div className="stat-card">
            <span>STATUS</span>
            <strong className="online-text">
              ONLINE
            </strong>
            <small>Core engine active</small>
          </div>

        </div>


        <div className="hero-grid">

          <div className="threat-visual">

            <div className="visual-label">
              <Activity size={16} />
              {t.monitor}
            </div>

            <div className="dashboard-logo-display">
              <img src="/night-hunter-logo.jpeg" alt="Night Hunter logo" />
              <span>DEFENSIVE SECURITY PLATFORM</span>
            </div>

            <div className="visual-footer">
              <span>
                TARGET ANALYSIS
              </span>

              <strong>
                SECURITY ENGINE ACTIVE
              </strong>
            </div>

          </div>


          <div className="threat-feed">

            <div className="panel-header">

              <div>
                <span className="panel-kicker">
                  GLOBAL THREAT FEED
                </span>

                <h3>
                  {t.activity}
                </h3>
              </div>

              <span className="live-badge">
                LIVE
              </span>

            </div>


            <div className="feed-item">

              <span className="feed-dot pink"></span>

              <div>
                <strong>
                  Security engine ready
                </strong>

                <small>
                  NIGHT HUNTER core initialized
                </small>
              </div>

              <time>
                now
              </time>

            </div>


            <div className="feed-item">

              <span className="feed-dot blue"></span>

              <div>
                <strong>
                  Report engine online
                </strong>

                <small>
                  JSON · TXT · HTML available
                </small>
              </div>

              <time>
                now
              </time>

            </div>


            <div className="feed-item">

              <span className="feed-dot violet"></span>

              <div>
                <strong>
                  Modules detected
                </strong>

                <small>
                  6 security modules available
                </small>
              </div>

              <time>
                now
              </time>

            </div>

          </div>

        </div>


        <div className="section-heading">

          <div>

            <p className="eyebrow">
              NIGHT HUNTER ENGINE
            </p>

            <h3>
              {t.securityModules}
            </h3>

          </div>

          <button
            className="view-button"
            onClick={() => openPage("Web Security")}
          >
            Open Web Security
            <ArrowUpRight size={16} />
          </button>

        </div>


        <div className="module-grid">

          {modules.map((module) => {

            const Icon = module.icon;

            return (
              <div
                className="module-card"
                key={module.name}
              >

                <div className="module-icon">
                  <Icon size={23} />
                </div>

                <h3>
                  {module.label}
                </h3>

                <p>
                  {module.description}
                </p>

                <button
                  className="launch-button"
                  onClick={() => launchModule(module.name)}
                >
                  {t.launch}
                  <ArrowUpRight size={16} />
                </button>

              </div>
            );

          })}

        </div>


        <div className="bottom-grid">


          <div className="terminal-panel">

            <div className="panel-header">

              <div>

                <span className="panel-kicker">
                  TERMINAL
                </span>

                <h3>
                  NIGHT HUNTER CLI
                </h3>

              </div>

              <Terminal size={18} />

            </div>


            <div className="terminal-body">

              {terminalLines.slice(-8).map((line, index) => (
                <p key={`${line}-${index}`}>
                  {line}
                </p>
              ))}

              <p className="terminal-cursor">
                _
              </p>

            </div>

          </div>


        </div>

      </section>
    );
  }


  return (
    <div className="night-hunter">
      {/* MANDATORY UPDATE MODAL (LOCKS DASHBOARD UNTIL UPDATED) */}
      {showMandatoryModal && (
        <div className="nh-update-modal-backdrop" role="dialog" aria-modal="true">
          <div className="nh-update-modal-card">
            <div className="nh-update-badge-row">
              <span className="nh-update-pill">
                <Sparkles size={14} /> NEW VERSION v1.0.3 RELEASED
              </span>
              <span className="nh-lock-status-pill">
                <AlertTriangle size={13} /> ACTION REQUIRED
              </span>
            </div>

            <h2>Mandatory Version Update Required</h2>
            <p className="nh-update-tagline">
              Your local installation must be updated to <strong>v1.0.3</strong>. Previous builds contain critical service glitches in Network Information, OS scanning, and Phishing detection. The dashboard is paused until you download the update.
            </p>

            <div className="nh-update-highlights">
              <p><strong>What is resolved in v1.0.3:</strong></p>
              <ul>
                <li>
                  <strong>🎯 Nmap Target Device Recon:</strong> Fixed Network Information! Now scans LAN target devices for exact <u>OS Model &amp; Fingerprint</u>, device name, and MAC vendor instead of local machine info.
                </li>
                <li>
                  <strong>📡 UDP Port Scanner (-sU):</strong> Scans open UDP ports with service mapping.
                </li>
                <li>
                  <strong>⚠️ LAN Caution Warning:</strong> Safety reminder that target devices must reside on your local subnet.
                </li>
                <li>
                  <strong>🛡️ Upgraded Phishing Engine:</strong> High-risk brand impersonation on paths/subdomains now flagged accurately.
                </li>
              </ul>
            </div>

            <div className="nh-update-warning-box">
              <AlertTriangle size={18} color="#ffb84d" />
              <span>
                To ensure security operations and scans are accurate, please download the updated release.
              </span>
            </div>

            <div className="nh-update-modal-actions">
              <button
                className="nh-btn-primary-update"
                onClick={handleOpenCloudServer}
              >
                <Play size={17} /> OPEN IN LIVE CLOUD SERVER (ALWAYS PATCHED)
              </button>
              <button
                className="nh-btn-secondary-update"
                onClick={handleDownloadUpdate}
              >
                <Download size={15} /> Download Offline v1.0.3
              </button>
              <button
                className="nh-btn-secondary-update"
                onClick={handleAcknowledgeUpdate}
                style={{ background: "transparent", border: "1px dashed rgba(255,255,255,0.2)" }}
              >
                Continue with Local &rarr;
              </button>
            </div>

            <div className="nh-update-quick-commands">
              <small>Linux / Termux quick update command:</small>
              <code>cd ~/.local/share/NightHunter/app &amp;&amp; git pull origin main</code>
            </div>
          </div>
        </div>
      )}

      {/* PATCH NOTES MODAL (ACCESSIBLE FROM CLOUD DASHBOARD) */}
      {showPatchNotes && (
        <div className="nh-update-modal-backdrop" role="dialog" aria-modal="true">
          <div className="nh-update-modal-card">
            <div className="nh-update-badge-row">
              <span className="nh-update-pill">
                <Sparkles size={14} /> LIVE PATCH v1.0.3
              </span>
              <button
                className="nh-modal-close-btn"
                onClick={() => setShowPatchNotes(false)}
                aria-label="Close patch notes"
              >
                <X size={18} />
              </button>
            </div>

            <h2>What's New in Night Hunter v1.0.3</h2>
            <p className="nh-update-tagline">
              This dashboard runs directly on the live server. Every patch and update is automatically active for all users without manual downloading.
            </p>

            <div className="nh-update-highlights">
              <p><strong>Resolved in this release:</strong></p>
              <ul>
                <li>
                  <strong>🎯 Nmap Target Device Recon:</strong> Scans target IPs on your local LAN for exact <u>OS Model &amp; Fingerprint</u>, device name, and MAC hardware vendor.
                </li>
                <li>
                  <strong>📡 UDP Port Scanner (-sU):</strong> Scans open UDP ports with service mapping.
                </li>
                <li>
                  <strong>⚠️ LAN Caution Notice:</strong> Guidance for local subnet targeting.
                </li>
                <li>
                  <strong>🛡️ Phishing Threat Engine:</strong> High/Critical threat classification for brand impersonation and suspicious paths.
                </li>
              </ul>
            </div>

            <div className="nh-update-modal-actions">
              <button
                className="nh-btn-primary-update"
                onClick={() => setShowPatchNotes(false)}
              >
                Continue to Dashboard &rarr;
              </button>
              <a
                href="/landing#downloads"
                className="nh-btn-secondary-update"
              >
                <Download size={15} /> Get Offline Packages
              </a>
            </div>
          </div>
        </div>
      )}

      <div className="dashboard-update-bar">
        <Sparkles size={16} color="#ffd480" />
        {isLocal ? (
          <>
            <span><strong>Local Machine Build:</strong> You are running locally. Run directly on the live cloud server for instant automatic patches!</span>
            <a href="https://night-hunter-f2w4.onrender.com/app" className="btn-dash-update">Open Live Cloud Server &rarr;</a>
          </>
        ) : (
          <>
            <span><strong>Night Hunter Cloud Engine (v1.0.3 Live):</strong> Direct server execution active. All patches and threat updates live!</span>
            <button onClick={() => setShowPatchNotes(true)} className="btn-dash-update">What's New in v1.0.3 &rarr;</button>
          </>
        )}
      </div>
      <header className="app-header">
        <button className="header-brand" type="button" onClick={resetDashboard}>
          <img className="header-logo-image" src="/night-hunter-logo.jpeg" alt="Night Hunter" />
          <span><strong>NIGHT <b>HUNTER</b></strong><small>SCAN&nbsp;&nbsp;/&nbsp;&nbsp;ANALYZE&nbsp;&nbsp;/&nbsp;&nbsp;DEFEND</small></span>
        </button>
        <div className="header-actions">
          <div className="system-status">
            <span></span>
            {isLocal ? "LOCAL ENGINE" : "CLOUD SERVER ONLINE"}
          </div>
          <a href="/landing" className="nav-site-link">Website &amp; Docs</a>
          <button className="icon-button" onClick={() => setTerminalLines((oldLines) => [...oldLines, "[!] No new security notifications."])} aria-label="Notifications"><Bell size={19} /></button>
          <button className="icon-button" onClick={() => openPage("Settings")} aria-label="Open settings"><Settings size={19} /></button>
        </div>
      </header>
      <div className="app-workspace">


      {/* SIDEBAR */}

      <aside className="sidebar">

        <nav className="navigation">

          <div className="nav-section-title">
            MAIN
          </div>


          <button
            className={`nav-item ${
              activePage === "Dashboard"
                ? "active"
                : ""
            }`}
            onClick={() => openPage("Dashboard")}
          >

            <LayoutDashboard size={19} />

            <span>
              {t.dashboard}
            </span>

          </button>


          <div className="nav-section-title">
            {t.modules}
          </div>


          {modules.map((module) => {

            const Icon = module.icon;

            return (
              <button
                className={`nav-item ${
                  activePage === module.name
                    ? "active"
                    : ""
                }`}
                key={module.name}
                onClick={() => openPage(module.name)}
              >

                <Icon size={19} />

                <div>

                  <span>
                    {module.label}
                  </span>

                  <small>
                    {module.description}
                  </small>

                </div>

              </button>
            );

          })}


          <button
            className={`nav-item ${
              activePage === "Settings"
                ? "active"
                : ""
            }`}
            onClick={() => openPage("Settings")}
          >

            <Settings size={19} />

            <div>

              <span>
                {t.settings}
              </span>

              <small>
                {t.preferences}
              </small>

            </div>

          </button>

        </nav>


        <div className="sidebar-footer">

          <div className="footer-status">

            <span className="status-dot"></span>

            SYSTEM ONLINE

          </div>

          <p>
            Night Hunter v1.0
          </p>

        </div>

      </aside>


      {/* MAIN */}

      <main className="main-content">


        {renderPageContent()}

      </main>

      </div>
    </div>
  );
}


export default App;
