#!/bin/sh
set -eu

# Läuft im Quellcodeordner; alle Ausgaben bleiben im Projektstamm/release.
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
RELEASE_DIR="$PROJECT_DIR/release"
VERSION=0.1.9
PACKAGE_ROOT="$PROJECT_DIR/.package-build"

command -v dpkg-deb >/dev/null 2>&1 || { echo "dpkg-deb fehlt" >&2; exit 1; }
command -v zip >/dev/null 2>&1 || { echo "zip fehlt" >&2; exit 1; }
python3 - "$SCRIPT_DIR/main.py" <<'PY'
import ast, pathlib, sys
ast.parse(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
print("Python-Syntaxprüfung erfolgreich")
PY

rm -rf "$PACKAGE_ROOT"
mkdir -p "$RELEASE_DIR" "$PACKAGE_ROOT/DEBIAN" \
  "$PACKAGE_ROOT/opt/lunanotiz" "$PACKAGE_ROOT/usr/bin" \
  "$PACKAGE_ROOT/usr/share/applications" "$PACKAGE_ROOT/usr/share/icons/hicolor/scalable/apps"
# Strip inherited setgid bits from build directories before dpkg-deb validates them.
chmod 0755 "$PACKAGE_ROOT" "$PACKAGE_ROOT/DEBIAN"
cp "$SCRIPT_DIR/main.py" "$PACKAGE_ROOT/opt/lunanotiz/main.py"
chmod 0644 "$PACKAGE_ROOT/opt/lunanotiz/main.py"
cp "$SCRIPT_DIR/debian/control" "$PACKAGE_ROOT/DEBIAN/control"
cp "$SCRIPT_DIR/lunanotiz" "$PACKAGE_ROOT/usr/bin/lunanotiz"
chmod 0755 "$PACKAGE_ROOT/usr/bin/lunanotiz"
cp "$SCRIPT_DIR/lunanotiz.desktop" "$PACKAGE_ROOT/usr/share/applications/lunanotiz.desktop"
chmod 0644 "$PACKAGE_ROOT/usr/share/applications/lunanotiz.desktop"
cp "$SCRIPT_DIR/lunanotiz.svg" "$PACKAGE_ROOT/usr/share/icons/hicolor/scalable/apps/lunanotiz.svg"
chmod 0644 "$PACKAGE_ROOT/usr/share/icons/hicolor/scalable/apps/lunanotiz.svg"
chmod u=rwx,go=rx,g-s "$PACKAGE_ROOT/DEBIAN"
dpkg-deb --build --root-owner-group "$PACKAGE_ROOT" "$RELEASE_DIR/lunanotiz_${VERSION}_all.deb"

rm -f "$RELEASE_DIR/LunaNotiz-${VERSION}-GitHub.zip"
cd "$PROJECT_DIR"
zip -r "$RELEASE_DIR/LunaNotiz-${VERSION}-GitHub.zip" quellcode \
  -x '*/__pycache__/*' '*.pyc' '*/build/*' '*/dist/*' '*/.pytest_cache/*' '*/.mypy_cache/*'
rm -rf "$PACKAGE_ROOT"
echo "Erstellt: release/lunanotiz_${VERSION}_all.deb"
echo "Erstellt: release/LunaNotiz-${VERSION}-GitHub.zip"
