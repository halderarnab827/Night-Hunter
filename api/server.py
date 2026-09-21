from pathlib import Path
import json
import sys

from flask import Flask, Response, jsonify, request, send_from_directory, stream_with_context
from flask_cors import CORS


PROJECT_ROOT = Path(sys._MEIPASS) if getattr(sys, "frozen", False) else Path(__file__).resolve().parents[1]
FRONTEND_DIST = PROJECT_ROOT / "dist" if (PROJECT_ROOT / "dist").is_dir() else (PROJECT_ROOT / "frontend" / "dist")
RELEASES_DIR = PROJECT_ROOT / "releases"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from modules.web_security.pentest import run_web_pentest
from modules.password_security import checker
from modules.network_security import checker as network_checker
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


@app.get("/api/status")
def api_status():

    return jsonify({
        "success": True,
        "tool": "NIGHT HUNTER",
        "status": "online",
        "version": "1.0.4"
    })

@app.get("/api/version")
def api_version():
    return jsonify({
        "success": True,
        "version": "1.0.4",
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


@app.post("/api/phishing")
def phishing_analysis():
    """Analyze URL characteristics without fetching the remote page."""
    try:
        data = request.get_json(silent=True) or {}
        target = str(data.get("target", "")).strip()
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
        text = data.get("text")
        operation = str(data.get("operation", "hash")).strip().lower()

        if text is None or text == "":
            return jsonify({"success": False, "error": "Text is required."}), 400

        operations = {
            # Hash mode deliberately returns every supported digest. Users do
            # not need to choose an algorithm just to compare hashes.
            "hash": lambda: crypto_tools.hash_text_all(text),
            "base64_encode": lambda: crypto_tools.base64_encode(text),
            "base64_decode": lambda: crypto_tools.base64_decode(text),
            "hex_encode": lambda: crypto_tools.hex_encode(text),
            "hex_decode": lambda: crypto_tools.hex_decode(text),
            "url_encode": lambda: crypto_tools.url_encode(text),
            "url_decode": lambda: crypto_tools.url_decode(text),
            "rot13": lambda: crypto_tools.rot13(text),
        }
        if operation not in operations:
            return jsonify({"success": False, "error": "Unsupported operation."}), 400

        result = operations[operation]()
        # Keep source text out of history. Encoded/decoded output is still shown
        # because the user asked for an audit trail of the completed operation.
        remember_activity(
            "Crypto Lab", "Local text input", "Complete",
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
