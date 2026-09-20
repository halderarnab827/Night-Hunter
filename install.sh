#!/usr/bin/env bash
# Installer included in night-hunter-linux.tar.gz
set -euo pipefail

APP_NAME="NightHunter"
APP_DIR="${HOME}/.local/share/${APP_NAME}"
BIN_DIR="${HOME}/.local/bin"
SOURCE_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required. Install it with your Linux package manager, then run this installer again."
  exit 1
fi

mkdir -p "$APP_DIR" "$BIN_DIR"
rm -rf "$APP_DIR/app"
mkdir -p "$APP_DIR/app"

for item in api core modules utils main.py requirement.txt; do
  cp -R "$SOURCE_DIR/$item" "$APP_DIR/app/"
done

python3 -m venv "$APP_DIR/venv"
"$APP_DIR/venv/bin/python" -m pip install --upgrade pip
"$APP_DIR/venv/bin/python" -m pip install -r "$APP_DIR/app/requirement.txt"

cat > "$BIN_DIR/$APP_NAME" <<EOF
#!/usr/bin/env bash
exec "$APP_DIR/venv/bin/python" "$APP_DIR/app/main.py" "\$@"
EOF
chmod +x "$BIN_DIR/$APP_NAME"

echo
echo "Night Hunter installed successfully."
echo "Start it with: NightHunter"
echo "If the command is not found, close and reopen your terminal."
