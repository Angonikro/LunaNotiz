#!/bin/sh
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_DIR=$(dirname "$SCRIPT_DIR")
RELEASE_DIR="$PROJECT_DIR/release"
PKG="$PROJECT_DIR/.package-build"
VERSION=0.2.6
command -v dpkg-deb >/dev/null
command -v zip >/dev/null
python3 - "$SCRIPT_DIR/main.py" <<'PYCODE'
import ast, pathlib, sys
ast.parse(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
print("Python-Syntaxprüfung erfolgreich")
PYCODE
rm -rf "$PKG"
mkdir -p "$RELEASE_DIR" "$PKG/DEBIAN" "$PKG/opt/lunanotiz"   "$PKG/usr/bin" "$PKG/usr/share/applications"   "$PKG/usr/share/icons/hicolor/scalable/apps"
chmod u=rwx,go=rx,g-s "$PKG" "$PKG/DEBIAN"
cp "$SCRIPT_DIR/main.py" "$PKG/opt/lunanotiz/main.py"
cp "$SCRIPT_DIR/debian/control" "$PKG/DEBIAN/control"
cp "$SCRIPT_DIR/lunanotiz" "$PKG/usr/bin/lunanotiz"
cp "$SCRIPT_DIR/lunanotiz.desktop" "$PKG/usr/share/applications/lunanotiz.desktop"
cp "$SCRIPT_DIR/lunanotiz.svg" "$PKG/usr/share/icons/hicolor/scalable/apps/lunanotiz.svg"
chmod 0755 "$PKG/usr/bin/lunanotiz"
chmod 0644 "$PKG/opt/lunanotiz/main.py" "$PKG/DEBIAN/control"   "$PKG/usr/share/applications/lunanotiz.desktop" "$PKG/usr/share/icons/hicolor/scalable/apps/lunanotiz.svg"
dpkg-deb --build --root-owner-group "$PKG" "$RELEASE_DIR/lunanotiz_${VERSION}_all.deb"
rm -f "$RELEASE_DIR/LunaNotiz-${VERSION}-GitHub.zip"
cd "$PROJECT_DIR"
zip -r "$RELEASE_DIR/LunaNotiz-${VERSION}-GitHub.zip" LunaNotiz   -x '*/__pycache__/*' '*.pyc' '*/build/*' '*/dist/*' '*/.pytest_cache/*' '*/.mypy_cache/*'
rm -rf "$PKG"
echo "Release erstellt: $RELEASE_DIR"
