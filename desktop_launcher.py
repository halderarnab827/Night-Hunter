"""Launch the Night Hunter desktop dashboard from the Windows executable."""

from __future__ import annotations

import os
import threading
import webbrowser

from waitress import serve

from api.server import app


HOST = "127.0.0.1"
PORT = int(os.environ.get("NIGHT_HUNTER_PORT", "5000"))
CLOUD_APP_URL = "https://night-hunter-f2w4.onrender.com/app"
LOCAL_APP_URL = f"http://{HOST}:{PORT}"


def open_dashboard() -> None:
    """Open the live cloud server if connected to the internet, else local server."""
    try:
        import urllib.request
        req = urllib.request.Request(
            "https://night-hunter-f2w4.onrender.com/api/status",
            headers={"User-Agent": "NightHunterDesktop/1.0.3"}
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            if resp.status == 200:
                print(f"[+] Night Hunter Cloud Server online. Connecting to: {CLOUD_APP_URL}")
                webbrowser.open_new(CLOUD_APP_URL)
                return
    except Exception as err:
        print(f"[*] Cloud server check: {err}. Starting local fallback engine...")

    print(f"[+] Opening local dashboard: {LOCAL_APP_URL}")
    webbrowser.open_new(LOCAL_APP_URL)


if __name__ == "__main__":
    threading.Timer(1.0, open_dashboard).start()
    serve(app, host=HOST, port=PORT)
