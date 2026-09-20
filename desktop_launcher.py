"""Launch the Night Hunter desktop dashboard from the Windows executable."""

from __future__ import annotations

import os
import threading
import webbrowser

from waitress import serve

from api.server import app


HOST = "127.0.0.1"
PORT = int(os.environ.get("NIGHT_HUNTER_PORT", "5000"))


def open_dashboard() -> None:
    webbrowser.open_new(f"http://{HOST}:{PORT}")


if __name__ == "__main__":
    threading.Timer(1.0, open_dashboard).start()
    serve(app, host=HOST, port=PORT)
