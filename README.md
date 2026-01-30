# ProfiLehrePlus Seminar Manager (Parser)

Dieses Modul liefert eine kleine Parsing-Grundlage für die Management-Seite von
"Mein ProfiLehrePlus". Ziel ist, Seminar-Links, Anmeldungszahlen und Hinweise
zur Durchführungsform (Präsenz/Online/Hybrid) zuverlässig aus dem HTML zu
extrahieren und damit eure interne Datenstruktur zu füllen.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Beispiel-Workflow

1. Mit eurem bestehenden Playwright-Skript HTML speichern (z. B. `page.content()`)
   und in eine Datei schreiben (Management-Seite + Detail-Seite je Seminar).
2. Das HTML mit den Parsern auslesen:

```python
from pathlib import Path

from plp_seminarmanager import parse_detail_html, parse_management_html, TaskManager

management_html = Path("plp_debug/03_management_ok.html").read_text(encoding="utf-8")
seminars = parse_management_html(management_html)

# Detail-Seite (Beispiel für das erste Seminar)
detail_html = Path("plp_debug/sem1_detail.html").read_text(encoding="utf-8")
detail = parse_detail_html(detail_html)
seminars[0].detail = detail

print(seminars[0].title)
print(seminars[0].detail.delivery_mode)
print(seminars[0].detail.registered_count)
print(seminars[0].link_urls())

# Aufgaben im Team
manager = TaskManager()
manager.add_task(
    seminar_id=seminars[0].seminar_id,
    title="14 Tage vorher Mail senden",
    due_date="2024-11-05",
    assigned_to="Teammitglied A",
)
```

## Was ist abgedeckt?

- **Links pro Seminar**: Alle Links aus der Management-Tabelle + Detail-Seite.
- **Anzahl angemeldeter Personen**: Regex-basierte Extraktion (z. B. "Angemeldet: 12").
- **Durchführungsform**: Erkennung über Schlüsselwörter in der Ausschreibung.
- **Aufgaben**: einfache In-Memory-Taskverwaltung, inkl. Abhaken.

## Nächste Schritte

- Persistenz (z. B. SQLite) für Seminare und Aufgaben.
- Scraper, der die Detail-URLs automatisch aufruft und HTML speichert.
- Erweiterte Regeln für Durchführungsform je nach PLP-Textstruktur.
