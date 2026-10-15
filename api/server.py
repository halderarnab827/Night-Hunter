from pathlib import Path
import json
import sys
import re

from flask import Flask, Response, jsonify, request, send_from_directory, stream_with_context
from flask_cors import CORS


PROJECT_ROOT = Path(sys._MEIPASS) if getattr(sys, "frozen", False) else Path(__file__).resolve().parents[1]
# Docker always builds the current frontend into ``frontend/dist``.  Prefer it
# over the repository's checked-in ``dist`` directory, which can be from an
# older release and otherwise makes a successful deployment serve stale UI.
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist" if (PROJECT_ROOT / "frontend" / "dist").is_dir() else (PROJECT_ROOT / "dist")
RELEASES_DIR = PROJECT_ROOT / "releases"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from modules.web_security.pentest import run_web_pentest
from modules.web_security.scanner_hub import run_local_scanner, scanner_status
from modules.password_security import checker
from modules.network_security import checker as network_checker
from modules.network_security.device_scanner import nmap_profile_status, run_nmap_profile
from modules.phishing.url_analyzer import PhishingAnalyzer
from modules.cryptography import crypto_tools
from modules.reports.report_exporter import REPORTS_DIRECTORY
from modules.reports.history import get_activity_history, record_activity


app = Flask(__name__)
CORS(app)


def remember_activity(module, target, status, summary, output=None):
    """History must never stop a completed security check from being returned."""
    try:
        record_activity(module, target, status, summary, output)
    except OSError as error:
        print(f"[!] Could not save activity history: {error}")


def analyze_scam_message(text_content):
    """Return a transparent, local heuristic assessment of pasted scam text.

    This deliberately does not send the message to a third party.  A match is a
    warning signal, not proof that a sender is malicious.
    """
    normalized = re.sub(r"\s+", " ", text_content.lower())
    signal_definitions = [
        ("Credential or OTP request", 28, [
            "one time password", "one-time password", "verification code", "share your otp",
            "send otp", "enter otp", "cvv", "pin number", "seed phrase", "recovery phrase"
        ]),
        ("Urgency or pressure", 16, [
            "urgent", "immediately", "act now", "within 24", "last warning", "expires today",
            "limited time", "do not ignore", "final notice"
        ]),
        ("Account or identity threat", 18, [
            "account suspended", "account locked", "account restricted", "verify your account",
            "unusual activity", "unrecognized login", "identity verification"
        ]),
        ("Payment or refund lure", 16, [
            "payment failed", "refund", "unpaid invoice", "unusual charge", "processing fee",
            "pay now", "bank transfer", "upi", "wallet address"
        ]),
        ("Delivery or prize lure", 12, [
            "parcel", "package", "delivery failed", "customs fee", "you have won", "claim prize"
        ]),
        ("Crypto or investment scam indicator", 20, [
            "guaranteed return", "double your money", "airdrop", "connect wallet", "crypto giveaway",
            "investment opportunity", "trading signal"
        ]),
        ("Impersonation language", 12, [
            "customer support", "bank security team", "tax department", "police department",
            "microsoft support", "official representative"
        ]),
        ("Off-platform contact request", 10, [
            "contact us on whatsapp", "message on telegram", "call this number", "contact agent"
        ]),
    ]

    patterns = []
    score = 0
    for category, weight, phrases in signal_definitions:
        matched = [phrase for phrase in phrases if phrase in normalized]
        if matched:
            patterns.append({
                "category": category,
                "keywords": matched,
                "weight": weight,
            })
            score += weight

    found_urls = re.findall(r"(?:https?://|www\.)[^\s<>\"']+", text_content, flags=re.IGNORECASE)
    found_urls = [url.rstrip(".,;:!?)]") for url in found_urls]
    shortened_urls = [url for url in found_urls if re.search(r"(?:bit\.ly|tinyurl\.com|t\.co|shorturl\.at)/", url, re.I)]
    if shortened_urls:
        patterns.append({
            "category": "Shortened link", "keywords": shortened_urls[:3], "weight": 12,
        })
        score += 12

    phone_numbers = re.findall(r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)", text_content)
    if phone_numbers:
        patterns.append({
            "category": "Phone contact included", "keywords": phone_numbers[:3], "weight": 4,
        })
        score += 4

    score = min(score, 100)
    risk_level = "LOW" if score < 20 else "MEDIUM" if score < 45 else "HIGH" if score < 70 else "CRITICAL"
    actions = [
        "Do not reply, call supplied numbers, open attachments, or use links from the message.",
        "Verify the request through the organisation's official website or a number you already trust.",
    ]
    if score >= 45:
        actions.extend([
            "Do not share passwords, OTPs, PINs, card details, recovery phrases, or remote-access codes.",
            "Report the message through your mail, messaging, bank, or platform reporting tools.",
        ])
    if score >= 70:
        actions.append("If information was already shared, change affected passwords from the official site and contact the real provider immediately.")

    url_reports = []
    for url in found_urls[:5]:
        try:
            fixed_url = url if url.startswith("http") else f"https://{url}"
            url_reports.append(PhishingAnalyzer(fixed_url, fetch_content=False).analyze())
        except Exception:
            continue

    high_risk_links = sum(1 for report in url_reports if report.get("risk_score", 0) >= 60)
    if high_risk_links:
        score = min(100, score + min(25, high_risk_links * 12))
        risk_level = "CRITICAL" if score >= 70 else "HIGH" if score >= 45 else "MEDIUM"

    return {
        "mode": "message_triage",
        "risk_score": score,
        "risk_level": risk_level,
        "assessment_note": "This is a local heuristic assessment. It identifies warning signals; it does not prove fraud or sender identity.",
        "scam_patterns": patterns,
        # Kept for existing clients that display the older field.
        "urgency_triggers": patterns,
        "recommended_actions": actions,
        "extracted_urls": found_urls,
        "url_reports": url_reports,
        "total_links": len(found_urls),
        "high_risk_links": high_risk_links,
    }


@app.get("/api/status")
def api_status():

    return jsonify({
        "success": True,
        "tool": "NIGHT HUNTER",
        "status": "online",
        "version": "1.6.2"
    })

@app.get("/api/version")
def api_version():
    return jsonify({
        "success": True,
        "version": "1.6.2",
        "release_url": "https://night-hunter-f2w4.onrender.com/#downloads"
    })


@app.post("/api/web-security")
def web_security():

    try:

        data = request.get_json(silent=True)

        if not data:

            return jsonify({
                "success": False,
                "error": "Request body is missing."
            }), 400

        target = str(
            data.get("target", "")
        ).strip()

        if not target:

            return jsonify({
                "success": False,
                "error": "Target URL is required."
            }), 400

        if data.get("authorized") is not True:
            return jsonify({
                "success": False,
                "error": "Confirm that you own the target or have explicit permission before running an active web audit."
            }), 400

        if not target.startswith(
            ("http://", "https://")
        ):

            target = "https://" + target

        print()
        print("=" * 60)
        print("NIGHT HUNTER API - WEB SECURITY")
        print("=" * 60)
        print(f"Target: {target}")
        print()

        report = run_web_pentest(target)
        finding_count = len(report.get("findings", [])) if isinstance(report, dict) else 0
        remember_activity(
            "Web Security", target, "Complete",
            f"Completed defensive web inspection with {finding_count} finding(s).",
            report,
        )

        return jsonify({
            "success": True,
            "target": target,
            "report": report
        })

    except Exception as error:

        print()
        print("[!] Web Security API error:")
        print(error)

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@app.get("/api/web-security/scanners")
def web_security_scanners():
    """Return real integration availability for the current device."""
    return jsonify({"success": True, **scanner_status()})


@app.post("/api/web-security/scanners/<scanner>")
def web_security_external_scanner(scanner):
    """Launch an explicitly selected, installed local scanner after consent."""
    data = request.get_json(silent=True) or {}
    if data.get("authorized") is not True:
        return jsonify({
            "success": False,
            "error": "Confirm that you own the target or have explicit permission before running an external scanner."
        }), 400
    target = str(data.get("target", "")).strip()
    if not target:
        return jsonify({"success": False, "error": "Target URL is required."}), 400
    try:
        result = run_local_scanner(scanner.lower(), target)
        remember_activity(
            "Web Security", target, "Complete",
            f"Completed local {scanner.lower()} scan.", result,
        )
        return jsonify({"success": True, "result": result})
    except (RuntimeError, ValueError) as error:
        return jsonify({"success": False, "error": str(error)}), 400
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500


@app.post("/api/password-security")
def password_security():

    try:

        data = request.get_json(silent=True)

        if not data:

            return jsonify({
                "success": False,
                "error": "Request body is missing."
            }), 400

        password = str(
            data.get("password", "")
        )

        if not password:

            return jsonify({
                "success": False,
                "error": "Password is required."
            }), 400

        print()
        print("=" * 60)
        print("NIGHT HUNTER API - PASSWORD SECURITY")
        print("=" * 60)
        print("Password analysis started.")
        print()

        # Never print or store the actual password.
        analysis = checker.analyze_password(
            password
        )
        remember_activity(
            "Password Security", "Password input", "Complete",
            f"Password strength: {analysis.get('rating', 'analysed')}", analysis,
        )

        return jsonify({
            "success": True,
            "analysis": analysis
        })

    except Exception as error:

        print()
        print("[!] Password Security API error:")
        print(error)

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@app.post("/api/network-security")
def network_security():

    try:

        data = request.get_json(silent=True)

        if not data:

            return jsonify({
                "success": False,
                "error": "Request body is missing."
            }), 400

        target = str(
            data.get("target", "")
        ).strip()

        if not target:

            return jsonify({
                "success": False,
                "error": "Target host or IP is required."
            }), 400

        print()
        print("=" * 60)
        print("NIGHT HUNTER API - NETWORK SECURITY")
        print("=" * 60)
        print(f"Target: {target}")
        print()

        result = network_checker.run_network_check(
            target
        )

        if not result.get("success", False):

            return jsonify({
                "success": False,
                "error": result.get(
                    "error",
                    "Network check failed."
                ),
                "result": result
            }), 400

        remember_activity(
            "Network Security", target, "Complete",
            f"Completed authorized network inspection; {result.get('total_open_ports', 0)} open port(s) found.",
            result,
        )

        return jsonify({
            "success": True,
            "target": target,
            "result": result
        })

    except Exception as error:

        print()
        print("[!] Network Security API error:")
        print(error)

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@app.post("/api/network-security/stream")
def network_security_stream():
    """Stream each advanced network-check result to the local dashboard."""
    data = request.get_json(silent=True) or {}
    target = str(data.get("target", "")).strip()

    if not target:
        return jsonify({
            "success": False,
            "error": "Target host or IP is required."
        }), 400

    def generate():
        for update in network_checker.iter_network_check(target):
            if update.get("type") == "complete":
                result = update.get("result", {})
                if result.get("success"):
                    remember_activity(
                        "Network Security", target, "Complete",
                        f"Completed authorized network inspection; {result.get('total_open_ports', 0)} open port(s) found.",
                        result,
                    )
            yield f"data: {json.dumps(update)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/api/network-security/nmap/status")
def network_nmap_status():
    return jsonify({"success": True, "nmap": nmap_profile_status()})


@app.post("/api/network-security/nmap")
def network_nmap_scan():
    data = request.get_json(silent=True) or {}
    target = str(data.get("target", "")).strip()
    profile = str(data.get("profile", "inventory")).strip()
    result = run_nmap_profile(target, profile)
    if not result.get("success"):
        return jsonify(result), 400
    remember_activity("Network Security", target, "Complete", f"Completed local Nmap {profile} profile.", result)
    return jsonify(result)


@app.post("/api/phishing")
def phishing_analysis():
    """Analyze URL characteristics without fetching remote page, with email/text triage and homoglyphs."""
    try:
        data = request.get_json(silent=True) or {}
        target = str(data.get("target", "")).strip()
        mode = str(data.get("mode", "url")).strip()
        text_content = str(data.get("text", "")).strip()
        if mode in {"email_triage", "message_triage", "sms_triage"} or (not target and text_content):
            if not text_content:
                return jsonify({"success": False, "error": "Paste a message, email, or SMS to analyse."}), 400
            result = analyze_scam_message(text_content)
            remember_activity(
                "Phishing Analyzer", f"Message triage ({result['total_links']} link(s))", "Complete",
                f"Local scam triage: {result['risk_level']} risk; {len(result['scam_patterns'])} signal group(s).", result,
            )
            return jsonify({"success": True, "report": result})

        if not target:
            return jsonify({"success": False, "error": "A URL is required."}), 400

        # Keep the browser-facing endpoint passive: it evaluates the supplied URL
        # itself and does not request potentially malicious content.
        report = PhishingAnalyzer(target, fetch_content=False).analyze()
        risk = report.get("risk_level", report.get("risk", "Analysed")) if isinstance(report, dict) else "Analysed"
        remember_activity(
            "Phishing Analyzer", target, "Complete",
            f"Completed passive URL inspection. Risk: {risk}.", report,
        )
        return jsonify({"success": True, "report": report})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@app.post("/api/cryptography")
def cryptography():
    try:
        data = request.get_json(silent=True) or {}
        operation = str(data.get("operation", "hash")).strip().lower()
        text = data.get("text")

        if operation == "generate_keys":
            result = crypto_tools.generate_security_keys()
            remember_activity(
                "Crypto Lab", "CSPRNG Key Generation", "Complete",
                "Generated secure random cryptographic tokens and keys.",
                {"operation": operation, "result": result},
            )
            return jsonify({"success": True, "operation": operation, "result": result})

        if text is None or text == "":
            return jsonify({"success": False, "error": "Text is required."}), 400

        operations = {
            "hash": lambda: crypto_tools.hash_text_all(text),
            "identify": lambda: crypto_tools.get_hash_information(text),
            "base64_encode": lambda: crypto_tools.base64_encode(text),
            "base64_decode": lambda: crypto_tools.base64_decode(text),
            "base32_encode": lambda: crypto_tools.base32_encode(text),
            "base32_decode": lambda: crypto_tools.base32_decode(text),
            "hex_encode": lambda: crypto_tools.hex_encode(text),
            "hex_decode": lambda: crypto_tools.hex_decode(text),
            "binary_encode": lambda: crypto_tools.binary_encode(text),
            "binary_decode": lambda: crypto_tools.binary_decode(text),
            "url_encode": lambda: crypto_tools.url_encode(text),
            "url_decode": lambda: crypto_tools.url_decode(text),
            "rot13": lambda: crypto_tools.rot13(text),
            "caesar_encrypt": lambda: crypto_tools.caesar_encrypt(text, data.get("shift", 3)),
            "caesar_decrypt": lambda: crypto_tools.caesar_decrypt(text, data.get("shift", 3)),
            "jwt_inspect": lambda: crypto_tools.inspect_jwt(text),
            "hmac_sha256": lambda: crypto_tools.hmac_digest(text, data.get("key", "night_hunter_secret"), "sha256"),
            "hmac_sha512": lambda: crypto_tools.hmac_digest(text, data.get("key", "night_hunter_secret"), "sha512"),
        }
        if operation not in operations:
            return jsonify({"success": False, "error": "Unsupported operation."}), 400

        result = operations[operation]()
        remember_activity(
            "Crypto Lab", "Local input", "Complete",
            f"Completed {operation.replace('_', ' ')} operation.",
            {"operation": operation, "result": result},
        )
        return jsonify({
            "success": True,
            "operation": operation,
            "result": result,
        })
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@app.get("/api/reports")
def reports():
    files = []
    for path in sorted(REPORTS_DIRECTORY.glob("night_hunter_*"), key=lambda item: item.stat().st_mtime, reverse=True):
        if path.is_file() and path.suffix.lower() in {".json", ".txt", ".html"}:
            files.append({
                "name": path.name,
                "format": path.suffix[1:].upper(),
                "size": path.stat().st_size,
                "modified": path.stat().st_mtime,
            })
    return jsonify({"success": True, "reports": files})


@app.get("/api/history")
def activity_history():
    """Dashboard activity, saved locally after each completed module action."""
    return jsonify({"success": True, "history": get_activity_history()})


@app.get("/downloads/<path:filename>")
def download_release(filename):
    """Direct high-speed download for Night Hunter release packages."""
    if RELEASES_DIR.is_dir() and (RELEASES_DIR / filename).is_file():
        return send_from_directory(RELEASES_DIR, filename, as_attachment=True)
    return jsonify({"success": False, "error": f"Release file '{filename}' not found."}), 404


@app.get("/")
@app.get("/<path:path>")
def frontend(path=""):
    """Serve the production React dashboard from the same local server."""
    requested_file = FRONTEND_DIST / path

    if path and requested_file.is_file():
        return send_from_directory(FRONTEND_DIST, path)

    return send_from_directory(FRONTEND_DIST, "index.html")


if __name__ == "__main__":

    print()
    print("=" * 60)
    print("        NIGHT HUNTER API SERVER")
    print("=" * 60)
    print()

    print("[+] API server starting...")
    print()

    print("[+] Web Security endpoint:")
    print("    POST /api/web-security")
    print()

    print("[+] Password Security endpoint:")
    print("    POST /api/password-security")
    print()

    print("[+] Network Security endpoint:")
    print("    POST /api/network-security")
    print()

    print("[+] Health endpoint:")
    print("    GET  /api/status")
    print()

    print("[+] Local server:")
    print("    http://127.0.0.1:5000")
    print()

    print("[*] Press CTRL+C to stop.")
    print("=" * 60)
    print()

    app.run(host="127.0.0.1", port=5000, debug=False)
