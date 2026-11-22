# Änderungsprotokoll

## 0.2.6 – 22.11.2026
- Speichern-Schaltfläche im Export-Dateidialog zusätzlich über Qt-Label, Standardbutton, Button-Rolle und sichtbare Schaltflächen lokalisiert.
- Öffnen- und Abbrechen-Beschriftungen erhalten denselben robusten Fallback.


## 0.2.5 – 22.11.2026
- Passwortabfragen für verschlüsselte Backups verwenden eigene Dialoge mit lokalisierten Schaltflächen „OK“ und „Abbrechen“.
- Auch die Auswahl von Exportformat und Importmodus verwendet eigene Dialoge statt QInputDialog-Standardbuttons.
- Damit sind die betroffenen Passwort- und Auswahlfenster unabhängig von der Systemsprache vollständig lokalisiert.


## 0.2.4 – 22.11.2026
- Verbleibende englische Standardschaltflächen in den Import-/Export-Dateidialogen lokalisiert: „Öffnen“, „Speichern“ und „Abbrechen“.
- Lösch- und Import-Ersetzungsabfragen verwenden nun den einheitlichen Ja/Nein-Dialog mit deutschen Schaltflächen.
- Native Dateidialoge durch Qt-eigene Dialoge mit explizit gesetzten Beschriftungen ersetzt.


## 0.2.3 – 22.11.2026
- PIN-Schutz lässt sich nach dem Deaktivieren jederzeit über Sicherheit wieder aktivieren.
- Menüpunkt eindeutig benannt: „PIN-Schutz aktivieren / PIN ändern …“.
- Deaktivierter Zustand bleibt deaktiviert, bis der Nutzer den Schutz ausdrücklich wieder einschaltet.


## 0.2.2
- Fehler beim Start behoben: Übersetzungsschlüssel im Wörterbuch waren fälschlich mit `tr()` umschlossen und führten zu einem NameError.
- Übersetzungswörterbuch und Versionsangaben korrigiert.


## 0.2.1 – 22.11.2026
- Export aller Notizen als JSON ergänzt.
- Verschlüsselter Backup-Export und -Import mit AES-256-GCM ergänzt; Schlüsselableitung über scrypt.
- Import unterstützt Zusammenführen oder nach Bestätigung vollständiges Ersetzen vorhandener Notizen.
- Optionaler PIN-Schutz beim Programmstart ergänzt; PIN wird gesalzen und mit scrypt abgeleitet gespeichert.
- PIN kann in den Sicherheitseinstellungen geändert oder deaktiviert werden.
- Abhängigkeit `python3-cryptography` ergänzt.

## 0.1.9
- Vorherige Version; lokale SQLite-Notizverwaltung mit Suche und deutsch/englischer Oberfläche.
