#!/usr/bin/env python3
"""LunaNotiz – lokale, zweisprachige Notizenverwaltung."""
from __future__ import annotations

import os
import json
import base64
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QComboBox, QDialog, QDialogButtonBox, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMessageBox, QPushButton,
    QMenu, QSplitter, QTextEdit, QVBoxLayout, QWidget, QFileDialog, QInputDialog,
    QFormLayout,
)

APP_NAME = "LunaNotiz"
VERSION = "0.2.6"
UI_LANGUAGE = "de"

TRANSLATIONS = {
    "Notiz bearbeiten": "Edit note", "Neue Notiz": "New note",
    "Titel": "Title", "Titel der Notiz": "Note title",
    "Inhalt": "Content", "Deine Gedanken …": "Your thoughts …",
    "Speichern": "Save", "Abbrechen": "Cancel",
    "Notizen durchsuchen …": "Search notes …",
    "Noch keine Notizen\nErstelle deine erste Notiz, um hier loszulegen.":
        "No notes yet\nCreate your first note to get started.",
    "Erste Notiz erstellen": "Create first note", "＋ Neue": "＋ New",
    "Löschen": "Delete", "Wähle links eine Notiz oder erstelle eine neue.":
        "Select a note on the left or create a new one.",
    "Änderungen speichern": "Save changes",
    "Notizen werden nur lokal auf diesem Gerät gespeichert.":
        "Notes are stored locally on this device only.",
    "Rückgängig": "Undo", "Wiederholen": "Redo", "Ausschneiden": "Cut",
    "Kopieren": "Copy", "Einfügen": "Paste", "Alles auswählen": "Select all",
    "Titel fehlt": "Title required", "Bitte gib der Notiz einen Titel.":
        "Please enter a title for the note.",
    "Notiz gespeichert": "Note saved", "Ungespeicherte Änderungen":
        "Unsaved changes",
    "Möchtest du deine Änderungen vor dem Beenden speichern?":
        "Would you like to save your changes before exiting?",
    "Bitte gib der Notiz einen Titel, bevor du speicherst.":
        "Please enter a title before saving the note.",
    "Notiz löschen": "Delete note", "Diese Notiz wirklich löschen?":
        "Are you sure you want to delete this note?",
    "Sprache": "Language", "Deutsch": "German", "Englisch": "English",
    "Wörter": "Words", "Zeichen": "Characters", "Zuletzt geändert":
        "Last modified", "Noch nicht gespeichert": "Not saved yet",
    "Änderungen speichern?": "Save changes?",
    "Möchtest du die Änderungen an dieser Notiz speichern, verwerfen oder den Wechsel abbrechen?":
        "Would you like to save the changes to this note, discard them, or cancel switching?",
    "Notiz konnte nicht gespeichert werden.": "Could not save the note.",
    "Notiz wurde gelöscht.": "Note deleted.",
    "Offline-Notizen für deine Gedanken": "Offline notes for your thoughts",
    "Alle Notizen": "All notes",
    "Keine Treffer": "No matches",
    "Notiz": "Note", "Neue": "New",
    "Datei": "File", "Exportieren …": "Export …", "Importieren …": "Import …",
    "Sicherheit": "Security", "PIN-Schutz aktivieren / PIN ändern …": "Enable PIN protection / change PIN …",
    "Ja": "Yes", "Nein": "No", "OK": "OK",
    "PIN-Schutz deaktivieren": "Disable PIN protection", "PIN-Schutz ist bereits aktiviert.": "PIN protection is already enabled.", "Neue PIN": "New PIN",
    "PIN (4–8 Ziffern)": "PIN (4–8 digits)", "PIN wiederholen": "Repeat PIN",
    "Möchtest du LunaNotiz mit einer PIN schützen?": "Would you like to protect LunaNotiz with a PIN?",
    "Die PIN muss aus 4 bis 8 Ziffern bestehen.": "The PIN must contain 4 to 8 digits.",
    "Die PINs stimmen nicht überein.": "The PINs do not match.", "PIN gespeichert.": "PIN saved.",
    "Bei Verlust der PIN ist kein Zugriff mehr möglich.": "If the PIN is lost, access cannot be recovered.",
    "Falsche PIN.": "Incorrect PIN.", "PIN-Schutz wirklich deaktivieren?": "Really disable PIN protection?",
    "Exportformat": "Export format", "Normales JSON": "Regular JSON",
    "Verschlüsselte Sicherung (AES-256-GCM)": "Encrypted backup (AES-256-GCM)",
    "Notizen exportieren": "Export notes", "Backup-Passwort": "Backup password",
    "Bitte Backup-Passwort eingeben:": "Please enter backup password:",
    "Exportformat auswählen:": "Select export format:",
    "Importmodus auswählen:": "Select import mode:",
    "Passwort wiederholen": "Repeat password", "Die Passwörter stimmen nicht überein.": "The passwords do not match.",
    "Export abgeschlossen.": "Export completed.", "Notizen importieren": "Import notes",
    "Importmodus": "Import mode", "Zusammenführen": "Merge",
    "Alle vorhandenen Notizen ersetzen": "Replace all existing notes",
    "Wirklich alle vorhandenen Notizen ersetzen?": "Really replace all existing notes?",
    "Sicherung ungültig, beschädigt oder Passwort falsch.": "Backup invalid, damaged, or password incorrect.",
    "Import abgeschlossen.": "Import completed.",
    "Öffnen": "Open", "Dateiname:": "File name:", "Dateityp:": "File type:",
    "Speichern": "Save", "Abbrechen": "Cancel", "PIN-Schutz deaktiviert. Du kannst ihn jederzeit über Sicherheit wieder aktivieren.": "PIN protection disabled. You can enable it again at any time under Security.",
}


def tr(text: str) -> str:
    if UI_LANGUAGE == "en":
        return TRANSLATIONS.get(text, text)
    return text


def data_path() -> Path:
    """XDG-konformer, benutzerspezifischer Speicherort der SQLite-Datenbank."""
    base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    folder = base / "lunanotiz"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "notizen.sqlite3"


class NotesStore:
    def __init__(self, path: Path):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("""CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )""")
        self.db.commit()

    def all(self, query: str = "") -> list[sqlite3.Row]:
        term = f"%{query}%"
        return list(self.db.execute(
            "SELECT id,title,body,updated_at FROM notes "
            "WHERE title LIKE ? OR body LIKE ? ORDER BY updated_at DESC,id DESC",
            (term, term),
        ))

    def get(self, note_id: int) -> sqlite3.Row | None:
        return self.db.execute(
            "SELECT id,title,body,updated_at FROM notes WHERE id=?", (note_id,)
        ).fetchone()

    def save(self, note_id: int | None, title: str, body: str) -> int:
        if note_id is None:
            cur = self.db.execute(
                "INSERT INTO notes(title,body) VALUES(?,?)", (title, body)
            )
            note_id = int(cur.lastrowid)
        else:
            self.db.execute(
                "UPDATE notes SET title=?,body=?,updated_at=datetime('now','localtime') WHERE id=?",
                (title, body, note_id),
            )
        self.db.commit()
        return note_id

    def delete(self, note_id: int) -> None:
        self.db.execute("DELETE FROM notes WHERE id=?", (note_id,))
        self.db.commit()

    def close(self) -> None:
        self.db.close()


def derive_key(password: str, salt: bytes) -> bytes:
    return Scrypt(salt=salt, length=32, n=2**15, r=8, p=1).derive(password.encode("utf-8"))


def ask_yes_no(parent, title: str, message: str, default_yes: bool = False) -> bool:
    """Ja/Nein-Dialog mit explizit lokalisierten Schaltflächen."""
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Question)
    box.setWindowTitle(title)
    box.setText(message)
    yes_button = box.addButton(tr("Ja"), QMessageBox.YesRole)
    no_button = box.addButton(tr("Nein"), QMessageBox.NoRole)
    box.setDefaultButton(yes_button if default_yes else no_button)
    box.exec()
    return box.clickedButton() is yes_button


def localized_file_dialog(parent, title: str, save: bool, name_filter: str, initial_path: str = "") -> str | None:
    """Nicht-nativen Dateidialog verwenden und Aktionsschaltflächen selbst übersetzen."""
    dialog = QFileDialog(parent, title, initial_path, name_filter)
    dialog.setOption(QFileDialog.DontUseNativeDialog, True)
    if save:
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setFileMode(QFileDialog.AnyFile)
    else:
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setFileMode(QFileDialog.ExistingFile)
    # Qt-Plattformstile können die Aktionsschaltfläche trotz eigenem Dialog
    # weiterhin mit dem englischen Standardtext beschriften. Deshalb sowohl
    # Standardbutton/Role als auch die tatsächlich sichtbaren Buttons setzen.
    accept_text = tr("Speichern") if save else tr("Öffnen")
    dialog.setLabelText(QFileDialog.Accept, accept_text)
    dialog.setLabelText(QFileDialog.Reject, tr("Abbrechen"))
    button_box = dialog.findChild(QDialogButtonBox)
    if button_box:
        accept_button = button_box.button(QDialogButtonBox.Save if save else QDialogButtonBox.Open)
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        if accept_button:
            accept_button.setText(accept_text)
        if cancel_button:
            cancel_button.setText(tr("Abbrechen"))
        # Fallback für Plattformstile, die einen Standardbutton mit anderem
        # Standard-Enum erzeugen, aber trotzdem in der Buttonbox führen.
        for button in button_box.buttons():
            if button.text().replace("&", "").strip().lower() in {"save", "open"}:
                button.setText(accept_text)
            elif button.text().replace("&", "").strip().lower() == "cancel":
                button.setText(tr("Abbrechen"))
    # Zusätzlicher Fallback für Qt-Themes, die Buttons direkt am Dialog führen.
    for button in dialog.findChildren(QPushButton):
        label = button.text().replace("&", "").strip().lower()
        if label in {"save", "open"}:
            button.setText(accept_text)
        elif label == "cancel":
            button.setText(tr("Abbrechen"))
    if dialog.exec() != QDialog.Accepted:
        return None
    selected = dialog.selectedFiles()
    return selected[0] if selected else None


class LocalizedTextDialog(QDialog):
    """Einzeilige Eingabe mit vollständig lokalisierten Schaltflächen."""
    def __init__(self, parent, title: str, label: str, password: bool = False):
        super().__init__(parent)
        self.setWindowTitle(title)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(label))
        self.edit = QLineEdit()
        if password:
            self.edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText(tr("OK"))
        buttons.button(QDialogButtonBox.Cancel).setText(tr("Abbrechen"))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def get_text(parent, title: str, label: str, password: bool = False):
        dialog = LocalizedTextDialog(parent, title, label, password)
        if dialog.exec() == QDialog.Accepted:
            return dialog.edit.text(), True
        return "", False


class LocalizedChoiceDialog(QDialog):
    """Auswahldialog ohne nicht übersetzte Qt-Standardbuttons."""
    def __init__(self, parent, title: str, label: str, choices: list[str], current: int = 0):
        super().__init__(parent)
        self.setWindowTitle(title)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(label))
        self.combo = QComboBox()
        self.combo.addItems(choices)
        self.combo.setCurrentIndex(max(0, min(current, len(choices) - 1)))
        layout.addWidget(self.combo)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText(tr("OK"))
        buttons.button(QDialogButtonBox.Cancel).setText(tr("Abbrechen"))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def get_item(parent, title: str, label: str, choices: list[str], current: int = 0):
        dialog = LocalizedChoiceDialog(parent, title, label, choices, current)
        if dialog.exec() == QDialog.Accepted:
            return dialog.combo.currentText(), True
        return "", False


class PinDialog(QDialog):
    def __init__(self, parent=None, confirm=False):
        super().__init__(parent)
        self.setWindowTitle(tr("Neue PIN") if confirm else "LunaNotiz – PIN")
        self.setMinimumWidth(320)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.pin = QLineEdit()
        self.pin.setEchoMode(QLineEdit.Password)
        self.pin.setMaxLength(8)
        form.addRow(tr("PIN (4–8 Ziffern)"), self.pin)
        self.confirm = None
        if confirm:
            self.confirm = QLineEdit()
            self.confirm.setEchoMode(QLineEdit.Password)
            self.confirm.setMaxLength(8)
            form.addRow(tr("PIN wiederholen"), self.confirm)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText(tr("OK"))
        buttons.button(QDialogButtonBox.Cancel).setText(tr("Abbrechen"))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self):
        return self.pin.text(), self.confirm.text() if self.confirm else None


def pin_digest(pin: str, salt: bytes) -> bytes:
    return derive_key(pin, salt)


def check_or_setup_pin(settings: QSettings) -> bool:
    salt_hex = settings.value("security/pin_salt", "")
    digest_hex = settings.value("security/pin_hash", "")
    if not salt_hex or not digest_hex:
        if settings.value("security/pin_setup_done", False, type=bool):
            return True
        answer = ask_yes_no(None, "LunaNotiz", tr("Möchtest du LunaNotiz mit einer PIN schützen?"), default_yes=True)
        if not answer:
            settings.setValue("security/pin_setup_done", True)
            settings.sync()
            return True
        dialog = PinDialog(confirm=True)
        if dialog.exec() != QDialog.Accepted:
            return False
        pin, repeat = dialog.values()
        if not pin.isdigit() or not 4 <= len(pin) <= 8:
            QMessageBox.warning(None, "LunaNotiz", tr("Die PIN muss aus 4 bis 8 Ziffern bestehen."))
            return False
        if pin != repeat:
            QMessageBox.warning(None, "LunaNotiz", tr("Die PINs stimmen nicht überein."))
            return False
        salt = os.urandom(16)
        settings.setValue("security/pin_salt", salt.hex())
        settings.setValue("security/pin_hash", pin_digest(pin, salt).hex())
        settings.setValue("security/pin_setup_done", True)
        settings.sync()
        QMessageBox.information(None, "LunaNotiz", tr("PIN gespeichert.") + "\n" + tr("Bei Verlust der PIN ist kein Zugriff mehr möglich."))
        return True
    dialog = PinDialog()
    if dialog.exec() != QDialog.Accepted:
        return False
    pin, _ = dialog.values()
    try:
        valid = pin_digest(pin, bytes.fromhex(salt_hex)).hex() == digest_hex
    except Exception:
        valid = False
    if not valid:
        QMessageBox.critical(None, "LunaNotiz", tr("Falsche PIN."))
    return valid


class NoteDialog(QDialog):
    def __init__(self, parent: QWidget, title: str = "", body: str = ""):
        super().__init__(parent)
        self.setWindowTitle(tr("Notiz bearbeiten") if title or body else tr("Neue Notiz"))
        self.resize(540, 440)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.addWidget(QLabel(tr("Titel")))
        self.title_edit = QLineEdit(title)
        self.title_edit.setPlaceholderText(tr("Titel der Notiz"))
        layout.addWidget(self.title_edit)
        layout.addWidget(QLabel(tr("Inhalt")))
        self.body_edit = QTextEdit()
        self.body_edit.setPlainText(body)
        self.body_edit.setPlaceholderText(tr("Deine Gedanken …"))
        layout.addWidget(self.body_edit, 1)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText(tr("Speichern"))
        buttons.button(QDialogButtonBox.Cancel).setText(tr("Abbrechen"))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self) -> tuple[str, str]:
        return self.title_edit.text().strip(), self.body_edit.toPlainText().strip()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("Luna", "LunaNotiz")
        self.store = NotesStore(data_path())
        self.current_id: int | None = None
        self._loading_note = False
        self._saved_title = ""
        self._saved_body = ""
        self.setWindowTitle(f"LunaNotiz {VERSION}")
        self.resize(1050, 700)
        self._build_ui()
        self._build_shortcuts()
        self._apply_language()
        self.refresh()
        self.note_title.textChanged.connect(self.update_stats)
        self.note_body.textChanged.connect(self.update_stats)

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(18, 16, 18, 12)
        outer.setSpacing(12)

        file_menu = self.menuBar().addMenu(tr("Datei"))
        file_menu.addAction(tr("Exportieren …"), self.export_notes)
        file_menu.addAction(tr("Importieren …"), self.import_notes)
        security_menu = self.menuBar().addMenu(tr("Sicherheit"))
        security_menu.addAction(tr("PIN-Schutz aktivieren / PIN ändern …"), self.change_pin)
        security_menu.addAction(tr("PIN-Schutz deaktivieren"), self.disable_pin)

        header = QHBoxLayout()
        brand_col = QVBoxLayout()
        brand = QLabel("LunaNotiz")
        brand.setObjectName("brand")
        subtitle = QLabel(tr("Offline-Notizen für deine Gedanken"))
        subtitle.setObjectName("subtitle")
        brand_col.addWidget(brand)
        brand_col.addWidget(subtitle)
        header.addLayout(brand_col)
        header.addStretch(1)
        self.search = QLineEdit()
        self.search.setClearButtonEnabled(True)
        self.search.setPlaceholderText(tr("Notizen durchsuchen …"))
        self.search.setContextMenuPolicy(Qt.CustomContextMenu)
        self.search.customContextMenuRequested.connect(self.show_search_context_menu)
        self.search.setMaximumWidth(330)
        self.search.textChanged.connect(self.refresh)
        header.addWidget(self.search)
        self.language = QComboBox()
        self.language.addItem("Deutsch", "de")
        self.language.addItem("English", "en")
        saved_language = self.settings.value("language", "de")
        self.language.setCurrentIndex(1 if saved_language == "en" else 0)
        self.language.currentIndexChanged.connect(self.change_language)
        self.language.setMinimumWidth(115)
        header.addWidget(self.language)
        outer.addLayout(header)

        self.splitter = QSplitter(Qt.Horizontal)
        sidebar = QWidget()
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(0, 0, 8, 0)
        self.list_heading = QLabel(tr("Alle Notizen"))
        self.list_heading.setObjectName("sectionHeading")
        side.addWidget(self.list_heading)
        self.list = QListWidget()
        self.list.setObjectName("notesList")
        self.list.currentItemChanged.connect(self.select_note)
        side.addWidget(self.list, 1)
        self.empty_hint = QLabel(tr("Noch keine Notizen\nErstelle deine erste Notiz, um hier loszulegen."))
        self.empty_hint.setObjectName("emptyHint")
        self.empty_hint.setAlignment(Qt.AlignCenter)
        self.empty_hint.setWordWrap(True)
        side.addWidget(self.empty_hint)
        self.first_note_button = QPushButton(tr("Erste Notiz erstellen"))
        self.first_note_button.clicked.connect(self.new_note)
        side.addWidget(self.first_note_button)
        buttons = QHBoxLayout()
        self.add_button = QPushButton("＋ " + tr("Neue"))
        self.add_button.clicked.connect(self.new_note)
        self.delete_button = QPushButton(tr("Löschen"))
        self.delete_button.setObjectName("dangerButton")
        self.delete_button.clicked.connect(self.delete_note)
        buttons.addWidget(self.add_button)
        buttons.addWidget(self.delete_button)
        side.addLayout(buttons)
        self.splitter.addWidget(sidebar)

        editor = QWidget()
        edit_layout = QVBoxLayout(editor)
        edit_layout.setContentsMargins(8, 0, 0, 0)
        self.note_title = QLineEdit()
        self.note_title.setObjectName("noteTitle")
        self.note_title.setPlaceholderText(tr("Titel"))
        self.note_title.setContextMenuPolicy(Qt.CustomContextMenu)
        self.note_title.customContextMenuRequested.connect(self.show_title_context_menu)
        edit_layout.addWidget(self.note_title)
        self.meta_row = QHBoxLayout()
        self.modified_label = QLabel(tr("Noch nicht gespeichert"))
        self.modified_label.setObjectName("muted")
        self.meta_row.addWidget(self.modified_label)
        self.meta_row.addStretch(1)
        self.stats_label = QLabel()
        self.stats_label.setObjectName("muted")
        self.meta_row.addWidget(self.stats_label)
        edit_layout.addLayout(self.meta_row)
        self.note_body = QTextEdit()
        self.note_body.setObjectName("noteEditor")
        self.note_body.setPlaceholderText(tr("Wähle links eine Notiz oder erstelle eine neue."))
        self.note_body.setAcceptRichText(False)
        self.note_body.setContextMenuPolicy(Qt.CustomContextMenu)
        self.note_body.customContextMenuRequested.connect(self.show_editor_context_menu)
        edit_layout.addWidget(self.note_body, 1)
        bottom = QHBoxLayout()
        self.save_button = QPushButton(tr("Änderungen speichern"))
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self.save_note)
        bottom.addStretch(1)
        bottom.addWidget(self.save_button)
        edit_layout.addLayout(bottom)
        self.splitter.addWidget(editor)
        self.splitter.setSizes([310, 700])
        outer.addWidget(self.splitter, 1)

        self.statusBar().showMessage(tr("Notizen werden nur lokal auf diesem Gerät gespeichert."))
        brand_credit = QLabel("Goldisoft 2026")
        brand_credit.setObjectName("brandCredit")
        self.statusBar().addPermanentWidget(brand_credit)
        self.setStyleSheet("""
            QWidget { background:#25282d; color:#e8eaf0; font-size:14px; }
            QMainWindow { background:#1d2024; }
            #brand { color:#a8caff; font-size:27px; font-weight:750; }
            #subtitle,#muted { color:#929ba8; font-size:12px; }
            #sectionHeading { color:#c8d2df; font-size:13px; font-weight:650; padding:4px 2px; }
            QLineEdit,QTextEdit,QListWidget,QComboBox {
                background:#191c20; border:1px solid #414955; border-radius:8px;
                padding:9px; selection-background-color:#426b9b;
            }
            #noteTitle { font-size:20px; font-weight:650; padding:12px; }
            #noteEditor { font-size:15px; line-height:1.4; padding:14px; }
            QPushButton { background:#3b414a; border:1px solid #4b5360; border-radius:8px; padding:9px 14px; }
            QPushButton:hover { background:#526174; }
            QPushButton:pressed { background:#365c85; }
            #primaryButton { background:#426b9b; border-color:#5d8bc0; font-weight:650; }
            #primaryButton:hover { background:#527eaf; }
            #dangerButton { color:#ffb6b6; }
            #notesList { padding:5px; }
            QListWidget::item { padding:12px 10px; border-bottom:1px solid #343941; border-radius:5px; }
            QListWidget::item:selected { background:#35485f; color:#ffffff; }
            QSplitter::handle { background:#141619; width:3px; }
            QStatusBar { color:#aab3bf; border-top:1px solid #343941; }
            #brandCredit { color:#8f9db0; font-size:11px; padding:0 9px 0 14px; }
        """)

    def show_search_context_menu(self, position) -> None:
        edit = self.search
        menu = QMenu(edit)
        menu.addAction(tr("Rückgängig"), edit.undo).setEnabled(edit.isUndoAvailable())
        menu.addAction(tr("Wiederholen"), edit.redo).setEnabled(edit.isRedoAvailable())
        menu.addSeparator()
        has_selection = bool(edit.selectedText())
        menu.addAction(tr("Ausschneiden"), edit.cut).setEnabled(has_selection)
        menu.addAction(tr("Kopieren"), edit.copy).setEnabled(has_selection)
        menu.addAction(tr("Einfügen"), edit.paste).setEnabled(bool(QApplication.clipboard().text()))
        menu.addAction(tr("Löschen"), lambda: edit.insert("")).setEnabled(has_selection)
        menu.addSeparator()
        menu.addAction(tr("Alles auswählen"), edit.selectAll).setEnabled(bool(edit.text()))
        menu.exec(edit.mapToGlobal(position))

    def show_title_context_menu(self, position) -> None:
        edit = self.note_title
        menu = QMenu(edit)
        menu.addAction(tr("Rückgängig"), edit.undo).setEnabled(edit.isUndoAvailable())
        menu.addAction(tr("Wiederholen"), edit.redo).setEnabled(edit.isRedoAvailable())
        menu.addSeparator()
        has_selection = bool(edit.selectedText())
        menu.addAction(tr("Ausschneiden"), edit.cut).setEnabled(has_selection)
        menu.addAction(tr("Kopieren"), edit.copy).setEnabled(has_selection)
        menu.addAction(tr("Einfügen"), edit.paste).setEnabled(bool(QApplication.clipboard().text()))
        delete_action = menu.addAction(tr("Löschen"))
        delete_action.setEnabled(has_selection)
        delete_action.triggered.connect(self.delete_title_selection)
        menu.addSeparator()
        menu.addAction(tr("Alles auswählen"), edit.selectAll).setEnabled(bool(edit.text()))
        menu.exec(edit.mapToGlobal(position))

    def delete_title_selection(self) -> None:
        edit = self.note_title
        start = edit.selectionStart()
        length = len(edit.selectedText())
        if start >= 0 and length:
            text = edit.text()
            edit.setText(text[:start] + text[start + length:])
            edit.setCursorPosition(start)

    def show_editor_context_menu(self, position) -> None:
        menu = QMenu(self.note_body)
        doc = self.note_body.document()
        cursor = self.note_body.textCursor()
        menu.addAction(tr("Rückgängig"), self.note_body.undo).setEnabled(doc.isUndoAvailable())
        menu.addAction(tr("Wiederholen"), self.note_body.redo).setEnabled(doc.isRedoAvailable())
        menu.addSeparator()
        menu.addAction(tr("Ausschneiden"), self.note_body.cut).setEnabled(cursor.hasSelection())
        menu.addAction(tr("Kopieren"), self.note_body.copy).setEnabled(cursor.hasSelection())
        menu.addAction(tr("Einfügen"), self.note_body.paste).setEnabled(self.note_body.canPaste())
        menu.addAction(tr("Löschen"), cursor.removeSelectedText).setEnabled(cursor.hasSelection())
        menu.addSeparator()
        menu.addAction(tr("Alles auswählen"), self.note_body.selectAll).setEnabled(bool(self.note_body.toPlainText()))
        menu.exec(self.note_body.mapToGlobal(position))

    def _build_shortcuts(self) -> None:
        shortcuts = [
            ("Ctrl+N", self.new_note, "newNote"),
            ("Ctrl+S", self.save_note, "saveNote"),
            ("Ctrl+F", self.search.setFocus, "searchNotes"),
            ("Delete", self.delete_note, "deleteNote"),
        ]
        for sequence, callback, name in shortcuts:
            action = QAction(self)
            action.setShortcut(QKeySequence(sequence))
            action.triggered.connect(callback)
            self.addAction(action)

    def _apply_language(self) -> None:
        self.setWindowTitle(f"LunaNotiz {VERSION}")
        self.search.setPlaceholderText(tr("Notizen durchsuchen …"))
        self.list_heading.setText(tr("Alle Notizen"))
        self.empty_hint.setText(tr("Noch keine Notizen\nErstelle deine erste Notiz, um hier loszulegen."))
        self.first_note_button.setText(tr("Erste Notiz erstellen"))
        self.add_button.setText("＋ " + tr("Neue"))
        self.delete_button.setText(tr("Löschen"))
        self.note_title.setPlaceholderText(tr("Titel"))
        self.note_body.setPlaceholderText(tr("Wähle links eine Notiz oder erstelle eine neue."))
        self.save_button.setText(tr("Änderungen speichern"))
        self.statusBar().showMessage(tr("Notizen werden nur lokal auf diesem Gerät gespeichert."))
        self.update_stats()
        if self.current_id is not None:
            row = self.store.get(self.current_id)
            if row:
                self.modified_label.setText(f"{tr('Zuletzt geändert')}: {row['updated_at']}")
        elif not self.note_title.text() and not self.note_body.toPlainText():
            self.modified_label.setText(tr("Noch nicht gespeichert"))

    def change_language(self, _index: int) -> None:
        global UI_LANGUAGE
        new_language = self.language.currentData()
        if not new_language or new_language == UI_LANGUAGE:
            return
        UI_LANGUAGE = new_language
        self.settings.setValue("language", UI_LANGUAGE)
        self._apply_language()

    def _is_dirty(self) -> bool:
        if self.current_id is None:
            return bool(self.note_title.text().strip() or self.note_body.toPlainText())
        return (self.note_title.text().strip() != self._saved_title
                or self.note_body.toPlainText() != self._saved_body)

    def _confirm_pending_changes(self, switching: bool = False) -> bool:
        if not self._is_dirty():
            return True
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Question)
        box.setWindowTitle(tr("Änderungen speichern?") if switching else tr("Ungespeicherte Änderungen"))
        box.setText(tr("Möchtest du die Änderungen an dieser Notiz speichern, verwerfen oder den Wechsel abbrechen?")
                    if switching else tr("Möchtest du deine Änderungen vor dem Beenden speichern?"))
        save_btn = box.addButton(tr("Speichern"), QMessageBox.AcceptRole)
        discard_btn = box.addButton(tr("Verwerfen") if UI_LANGUAGE == "de" else "Discard", QMessageBox.DestructiveRole)
        cancel_btn = box.addButton(tr("Abbrechen"), QMessageBox.RejectRole)
        box.setDefaultButton(save_btn)
        box.exec()
        clicked = box.clickedButton()
        if clicked == save_btn:
            return self._save_current(show_message=False)
        if clicked == discard_btn:
            return True
        return False

    def _save_current(self, show_message: bool = True) -> bool:
        title = self.note_title.text().strip()
        body = self.note_body.toPlainText()
        if not title:
            QMessageBox.information(self, tr("Titel fehlt"), tr("Bitte gib der Notiz einen Titel."))
            return False
        try:
            self.current_id = self.store.save(self.current_id, title, body)
        except sqlite3.Error:
            QMessageBox.critical(self, APP_NAME, tr("Notiz konnte nicht gespeichert werden."))
            return False
        self._saved_title, self._saved_body = title, body
        row = self.store.get(self.current_id)
        self.modified_label.setText(f"{tr('Zuletzt geändert')}: {row['updated_at']}" if row else "")
        if show_message:
            self.statusBar().showMessage(tr("Notiz gespeichert"), 2500)
        self.refresh(select_id=self.current_id)
        return True

    def refresh(self, *_args, select_id: int | None = None) -> None:
        selected = self.current_id if select_id is None else select_id
        self.list.blockSignals(True)
        self.list.clear()
        rows = self.store.all(self.search.text())
        for row in rows:
            stamp = row["updated_at"]
            item = QListWidgetItem(f"{row['title']}\n{stamp}")
            item.setData(Qt.UserRole, row["id"])
            self.list.addItem(item)
            if row["id"] == selected:
                self.list.setCurrentItem(item)
        self.list.blockSignals(False)
        current = self.list.currentItem()
        is_empty = self.list.count() == 0
        self.empty_hint.setVisible(is_empty)
        self.first_note_button.setVisible(is_empty and not self.search.text())
        if is_empty:
            self.empty_hint.setText(
                tr("Keine Treffer") if self.search.text() and self.store.all()
                else tr("Noch keine Notizen\nErstelle deine erste Notiz, um hier loszulegen.")
            )
        if current is not None:
            selected_id = int(current.data(Qt.UserRole))
            if selected_id != self.current_id or not self._is_dirty():
                self.select_note(current)
        elif self.current_id is None:
            self.modified_label.setText(tr("Noch nicht gespeichert"))

    def select_note(self, current: QListWidgetItem | None, previous: QListWidgetItem | None = None) -> None:
        if self._loading_note or current is None:
            return
        target_id = int(current.data(Qt.UserRole))
        if target_id != self.current_id and self._is_dirty():
            if not self._confirm_pending_changes(switching=True):
                self.list.blockSignals(True)
                self.list.setCurrentItem(previous)
                self.list.blockSignals(False)
                return
            # Saving refreshes the list and restores the old selection. Re-select
            # the requested item after the confirmation dialog.
            for index in range(self.list.count()):
                item = self.list.item(index)
                if int(item.data(Qt.UserRole)) == target_id:
                    self.list.blockSignals(True)
                    self.list.setCurrentItem(item)
                    self.list.blockSignals(False)
                    break
        row = self.store.get(target_id)
        if not row:
            return
        self._loading_note = True
        self.current_id = target_id
        self.note_title.setText(row["title"])
        self.note_body.setPlainText(row["body"])
        self._saved_title, self._saved_body = row["title"], row["body"]
        self.modified_label.setText(f"{tr('Zuletzt geändert')}: {row['updated_at']}")
        self._loading_note = False
        self.update_stats()

    def update_stats(self, *_args) -> None:
        text = self.note_body.toPlainText()
        words = len(text.split())
        chars = len(text)
        self.stats_label.setText(f"{tr('Wörter')}: {words}  ·  {tr('Zeichen')}: {chars}")

    def new_note(self) -> None:
        if not self._confirm_pending_changes(switching=True):
            return
        dialog = NoteDialog(self)
        if dialog.exec() == QDialog.Accepted:
            title, body = dialog.values()
            if not title:
                QMessageBox.information(self, tr("Titel fehlt"), tr("Bitte gib der Notiz einen Titel."))
                return
            self.current_id = self.store.save(None, title, body)
            self.refresh(select_id=self.current_id)

    def save_note(self) -> None:
        self._save_current(show_message=True)

    def delete_note(self) -> None:
        if self.current_id is None:
            return
        if self._is_dirty() and not self._confirm_pending_changes(switching=True):
            return
        if ask_yes_no(self, tr("Notiz löschen"), tr("Diese Notiz wirklich löschen?"), default_yes=False):
            self.store.delete(self.current_id)
            self.current_id = None
            self._saved_title = self._saved_body = ""
            self.note_title.clear()
            self.note_body.clear()
            self.modified_label.setText(tr("Noch nicht gespeichert"))
            self.refresh(select_id=None)
            self.statusBar().showMessage(tr("Notiz wurde gelöscht."), 2500)

    def change_pin(self) -> None:
        # Dieser Menüpunkt funktioniert sowohl bei deaktiviertem als auch bei aktivem PIN-Schutz.
        dialog = PinDialog(self, confirm=True)
        if dialog.exec() != QDialog.Accepted:
            return
        pin, repeat = dialog.values()
        if not pin.isdigit() or not 4 <= len(pin) <= 8:
            QMessageBox.warning(self, APP_NAME, tr("Die PIN muss aus 4 bis 8 Ziffern bestehen."))
            return
        if pin != repeat:
            QMessageBox.warning(self, APP_NAME, tr("Die PINs stimmen nicht überein."))
            return
        salt = os.urandom(16)
        self.settings.setValue("security/pin_salt", salt.hex())
        self.settings.setValue("security/pin_hash", pin_digest(pin, salt).hex())
        self.settings.setValue("security/pin_setup_done", True)
        self.settings.sync()
        QMessageBox.information(self, APP_NAME, tr("PIN gespeichert."))

    def disable_pin(self) -> None:
        if not self.settings.value("security/pin_hash", ""):
            return
        if ask_yes_no(self, APP_NAME, tr("PIN-Schutz wirklich deaktivieren?"), default_yes=False):
            self.settings.remove("security/pin_salt")
            self.settings.remove("security/pin_hash")
            self.settings.remove("security/pin_salt")
            self.settings.setValue("security/pin_setup_done", True)
            self.settings.sync()
            self.statusBar().showMessage(tr("PIN-Schutz deaktiviert. Du kannst ihn jederzeit über Sicherheit wieder aktivieren."), 6000)

    def _backup_payload(self) -> bytes:
        notes = [dict(row) for row in self.store.all()]
        payload = {"format": "LunaNotiz", "version": 1,
                   "exported_at": datetime.now().isoformat(timespec="seconds"), "notes": notes}
        return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")

    def export_notes(self) -> None:
        choice, ok = LocalizedChoiceDialog.get_item(self, APP_NAME, tr("Exportformat auswählen:"),
            [tr("Normales JSON"), tr("Verschlüsselte Sicherung (AES-256-GCM)")], 1)
        if not ok:
            return
        encrypted = choice.startswith(tr("Verschlüsselte"))
        ext = ".lnbackup" if encrypted else ".json"
        path = localized_file_dialog(self, tr("Notizen exportieren"), True,
                                     "LunaNotiz Backup (*.lnbackup);;JSON (*.json)",
                                     "LunaNotiz-Backup" + ext)
        if not path:
            return
        data = self._backup_payload()
        if encrypted:
            password, ok = LocalizedTextDialog.get_text(self, APP_NAME, tr("Bitte Backup-Passwort eingeben:"), password=True)
            if not ok or not password:
                return
            repeat, ok = LocalizedTextDialog.get_text(self, APP_NAME, tr("Passwort wiederholen"), password=True)
            if not ok:
                return
            if password != repeat:
                QMessageBox.warning(self, APP_NAME, tr("Die Passwörter stimmen nicht überein."))
                return
            salt, nonce = os.urandom(16), os.urandom(12)
            encrypted_data = AESGCM(derive_key(password, salt)).encrypt(nonce, data, b"LunaNotiz-backup-v1")
            data = json.dumps({"format": "LunaNotiz-encrypted", "version": 1,
                "kdf": "scrypt", "salt": base64.b64encode(salt).decode("ascii"),
                "nonce": base64.b64encode(nonce).decode("ascii"),
                "ciphertext": base64.b64encode(encrypted_data).decode("ascii")}, indent=2).encode("utf-8")
        try:
            Path(path).write_bytes(data)
            QMessageBox.information(self, APP_NAME, tr("Export abgeschlossen."))
        except OSError as exc:
            QMessageBox.critical(self, APP_NAME, str(exc))

    def import_notes(self) -> None:
        path = localized_file_dialog(self, tr("Notizen importieren"), False,
                                     "LunaNotiz Backup (*.lnbackup *.json);;Alle Dateien (*)")
        if not path:
            return
        try:
            envelope = json.loads(Path(path).read_text(encoding="utf-8"))
            if envelope.get("format") == "LunaNotiz-encrypted":
                password, ok = LocalizedTextDialog.get_text(self, APP_NAME, tr("Bitte Backup-Passwort eingeben:"), password=True)
                if not ok or not password:
                    return
                salt = base64.b64decode(envelope["salt"], validate=True)
                nonce = base64.b64decode(envelope["nonce"], validate=True)
                ciphertext = base64.b64decode(envelope["ciphertext"], validate=True)
                clear = AESGCM(derive_key(password, salt)).decrypt(nonce, ciphertext, b"LunaNotiz-backup-v1")
                envelope = json.loads(clear.decode("utf-8"))
            if envelope.get("format") != "LunaNotiz" or not isinstance(envelope.get("notes"), list):
                raise ValueError("invalid backup")
            notes = envelope["notes"]
            if any(not isinstance(n, dict) or not isinstance(n.get("title"), str)
                   or not isinstance(n.get("body", ""), str) for n in notes):
                raise ValueError("invalid note")
        except Exception:
            QMessageBox.critical(self, APP_NAME, tr("Sicherung ungültig, beschädigt oder Passwort falsch."))
            return
        mode, ok = LocalizedChoiceDialog.get_item(self, APP_NAME, tr("Importmodus auswählen:"),
            [tr("Zusammenführen"), tr("Alle vorhandenen Notizen ersetzen")], 0)
        if not ok:
            return
        if mode == tr("Alle vorhandenen Notizen ersetzen") and not ask_yes_no(
                self, APP_NAME, tr("Wirklich alle vorhandenen Notizen ersetzen?"), default_yes=False):
            return
        try:
            with self.store.db:
                if mode == tr("Alle vorhandenen Notizen ersetzen"):
                    self.store.db.execute("DELETE FROM notes")
                for note in notes:
                    self.store.db.execute("INSERT INTO notes(title,body) VALUES(?,?)",
                                          (note["title"], note.get("body", "")))
            self.current_id = None
            self._saved_title = self._saved_body = ""
            self.note_title.clear()
            self.note_body.clear()
            self.refresh(select_id=None)
            QMessageBox.information(self, APP_NAME, tr("Import abgeschlossen."))
        except sqlite3.Error as exc:
            QMessageBox.critical(self, APP_NAME, str(exc))

    def closeEvent(self, event) -> None:
        if self._confirm_pending_changes(switching=False):
            self.store.close()
            event.accept()
        else:
            event.ignore()


def main() -> int:
    global UI_LANGUAGE
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("Luna")
    settings = QSettings("Luna", "LunaNotiz")
    UI_LANGUAGE = settings.value("language", "de")
    if not check_or_setup_pin(settings):
        return 0
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
