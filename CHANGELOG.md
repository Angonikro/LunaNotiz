## 0.1.9 — Kontextmenüs in Titelfeld und Suche

- Rechtsklick im Suchfeld öffnet jetzt ebenfalls ein vollständig lokalisiertes Kontextmenü (Deutsch/Englisch).

- Rechtsklick im Titelfeld öffnet jetzt ein eigenes, vollständig lokalisiertes Kontextmenü (Deutsch/Englisch) mit Rückgängig, Wiederholen, Ausschneiden, Kopieren, Einfügen, Löschen und Alles auswählen.
- Versionsnummer und Paketmetadaten auf 0.1.9 aktualisiert.

# Änderungsprotokoll

## 0.1.8 — Zweisprachige Oberfläche und sicherere Bearbeitung

- Englische Beschriftung der Schaltfläche „＋ Neue“ korrigiert: Sie lautet jetzt „＋ New“.
- Herstellerhinweis „Goldisoft 2026“ dezent in der Statusleiste ergänzt.

- Vollständige deutsche und englische Oberfläche mit dauerhaft gespeicherter Sprachauswahl.
- Dialoge, Kontextmenü, Statusmeldungen, Platzhalter und Schaltflächen werden passend zur gewählten Sprache angezeigt.
- Wort- und Zeichenzähler im Editor ergänzt.
- Letzten gespeicherten Änderungszeitpunkt im Editor angezeigt.
- Tastenkürzel ergänzt: `Strg+N`, `Strg+S`, `Strg+F` und `Entf`.
- Ungespeicherte Änderungen werden beim Wechsel zu einer anderen Notiz, beim Anlegen einer neuen Notiz und beim Beenden geschützt.
- Suche und Sprachwechsel verwerfen keine ungespeicherten Texte.
- Graphit-Oberfläche mit besserer Gliederung, Abständen und deutlicheren Editor-Elementen überarbeitet.
- Debian-Abhängigkeit `python3-pyside6.qtgui` für Tastenkürzel ergänzt.
- README und Paketmetadaten aktualisiert; vorhandene SQLite-Datenbank bleibt erhalten.

## 0.1.7 — Rückfrage bei ungespeicherten Änderungen

- Beim Schließen fragt LunaNotiz bei Änderungen, ob gespeichert, verworfen oder das Schließen abgebrochen werden soll.
- Speichern prüft den Titel und legt eine neue Notiz an, wenn noch keine bestehende Notiz ausgewählt ist.

## 0.1.6 — Deutsches Editor-Kontextmenü

- Das Rechtsklick-Menü im Editor ist auf Deutsch: Rückgängig, Wiederholen, Ausschneiden, Kopieren, Einfügen, Löschen und Alles auswählen.
- Nicht verfügbare Aktionen sind abhängig von Auswahl und Zwischenablage deaktiviert.

## 0.1.5 — Notizauswahl aktualisiert den Editor

- Beim Wiederherstellen der Listenauswahl wird der Auswahl-Handler nun ausdrücklich aufgerufen.
- Dadurch werden Titel und Inhalt der ausgewählten Notiz nach Aktualisierungen wieder im Editor angezeigt.

## 0.1.4 — Verbesserter Einstieg ohne vorhandene Notizen

- Leerer Notizenbereich zeigt einen Hinweis und die Schaltfläche „Erste Notiz erstellen“.
- Die Schaltfläche öffnet den vorhandenen Dialog zur Notizerstellung.

## 0.1.3 — All-Architektur-Paket und Menüeintrag

- Paketarchitektur auf `all` umgestellt; DEB-Dateiname trägt `_all`.
- Desktop-Eintrag den Kategorien Dienstprogramme (`Utility`) und Büro (`Office`) zugeordnet.
- Versionsnummer auf 0.1.3 erhöht.

## 0.1.2 — Büro-Menüeintrag

- Desktop-Eintrag bleibt der Kategorie Büro (`Office`) zugeordnet und wird im Paket unter `/usr/share/applications/lunanotiz.desktop` installiert.
- Versionsnummer auf 0.1.2 erhöht.

## 0.1.1 — Paketrechte und Desktop-Menü

- Installierte Python-Datei erhält Leserechte für alle Benutzer.
- Desktop-Eintrag wird ausdrücklich der Kategorie Büro (Office) zugeordnet.
- Versionsnummer auf 0.1.1 erhöht.

## 0.1.0 — erste Version

- Erste eigenständige LunaNotiz-Version mit PySide6 und deutschem Graphit-Design.
- Notizen erstellen, bearbeiten, löschen und nach Titel/Inhalt durchsuchen.
- Dauerhafte Offline-Speicherung über SQLite im benutzerspezifischen Datenverzeichnis.
- Debian-Paketierung für ARM64 mit Starter und Desktop-Eintrag.
