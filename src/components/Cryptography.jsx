import { useState } from "react";
import { Binary, Check, Copy, Fingerprint, KeyRound, Play, RefreshCw, ShieldCheck } from "lucide-react";

const operations = [
  { value: "hash", label: "Hash text", detail: "Generate every supported digest" },
  { value: "base64_encode", label: "Base64 encode", detail: "Convert text to Base64" },
  { value: "base64_decode", label: "Base64 decode", detail: "Decode Base64 text" },
  { value: "hex_encode", label: "Hex encode", detail: "Convert text to hexadecimal" },
  { value: "hex_decode", label: "Hex decode", detail: "Decode hexadecimal text" },
  { value: "url_encode", label: "URL encode", detail: "Escape text for a URL" },
  { value: "url_decode", label: "URL decode", detail: "Decode URL-escaped text" },
  { value: "rot13", label: "ROT13", detail: "Apply the reversible ROT13 transform" },
];

function titleForAlgorithm(algorithm) {
  return algorithm.replaceAll("_", "-").toUpperCase();
}

export default function Cryptography() {
  const [text, setText] = useState("");
  const [operation, setOperation] = useState("hash");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [running, setRunning] = useState(false);
  const [copied, setCopied] = useState("");
  const selectedOperation = operations.find((item) => item.value === operation);

  async function runTool(event) {
    event.preventDefault();
    if (!text.trim()) { setError("Enter text to use this tool."); return; }
    setRunning(true); setError(""); setResult(null); setCopied("");
    try {
      const response = await fetch("/api/cryptography", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text, operation }) });
      const data = await response.json();
      if (!response.ok || !data.success) throw new Error(data.error || "Cryptography operation failed.");
      setResult(data.result);
    } catch (requestError) { setError(requestError.message); }
    finally { setRunning(false); }
  }

  async function copy(value, label) {
    await navigator.clipboard.writeText(value);
    setCopied(label);
    window.setTimeout(() => setCopied(""), 1800);
  }

  const allHashes = operation === "hash" && result && typeof result === "object";

  return <section className="crypto-page">
    <header className="module-header crypto-header">
      <div className="module-heading"><div className="module-heading-icon"><KeyRound size={24} /></div><div><p className="eyebrow">NIGHT HUNTER · CRYPTOGRAPHY</p><h2>Crypto Lab</h2><p className="subtitle">Hash · Encode · Transform</p></div></div>
      <div className={`module-state ${running ? "busy" : ""}`}><span />{running ? "PROCESSING" : "READY"}</div>
    </header>

    <div className="crypto-layout">
      <form className="crypto-tool-card" onSubmit={runTool}>
        <div className="crypto-card-heading"><div><span>TEXT TOOL</span><h3>{selectedOperation.label}</h3></div><Binary size={19} /></div>
        <label className="crypto-label">OPERATION<select value={operation} onChange={(event) => { setOperation(event.target.value); setResult(null); setError(""); }} disabled={running}>{operations.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</select></label>
        <p className="crypto-operation-detail">{selectedOperation.detail}</p>
        <label className="crypto-label">INPUT TEXT<textarea value={text} onChange={(event) => setText(event.target.value)} placeholder="Enter text to process…" disabled={running} /></label>
        <button className="crypto-run-button" type="submit" disabled={running}>{running ? <RefreshCw className="spin-icon" size={17} /> : <Play size={17} />}{running ? "PROCESSING" : operation === "hash" ? "GENERATE ALL HASHES" : "RUN TOOL"}</button>
        {error && <p className="crypto-error">{error}</p>}
      </form>

      <aside className="crypto-side-card"><Fingerprint size={25} /><span>SMART HASHING</span><h3>All algorithms, one action.</h3><p>Hash Text automatically generates MD5, SHA family, SHA-3, BLAKE2b, and BLAKE2s results for comparison.</p><div className="crypto-algorithm-pills"><b>MD5</b><b>SHA-2</b><b>SHA-3</b><b>BLAKE2</b></div></aside>
    </div>

    <section className="crypto-output"><div className="crypto-output-heading"><div><p className="eyebrow">OUTPUT CONSOLE</p><h3>{allHashes ? "Generated Hashes" : "Result"}</h3></div>{result && <ShieldCheck size={20} />}</div>
      {!result ? <div className="crypto-empty"><Fingerprint size={23} /><div><strong>Ready for input</strong><p>Your processed result will appear here.</p></div></div> : allHashes ? <div className="hash-grid">{Object.entries(result).map(([algorithm, digest]) => <article className="hash-row" key={algorithm}><div><span>{titleForAlgorithm(algorithm)}</span><code>{digest}</code></div><button onClick={() => copy(digest, algorithm)} type="button" aria-label={`Copy ${algorithm} hash`}>{copied === algorithm ? <Check size={17} /> : <Copy size={17} />}</button></article>)}</div> : <div className="single-result"><code>{result}</code><button onClick={() => copy(result, "result")} type="button">{copied === "result" ? <Check size={17} /> : <Copy size={17} />}{copied === "result" ? "COPIED" : "COPY RESULT"}</button></div>}
    </section>
  </section>;
}
