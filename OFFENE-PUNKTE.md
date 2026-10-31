# Offene Punkte – md-viewer

Stand: 2026-10-31

## Offen

| ID | Art | Beschreibung | Status |
|---|---|---|---|
| A2 | Annahme | Speichern, ungespeicherte Änderungen und Button-Sichtbarkeit (ursprünglich F2–F4) wurden nach den vorgeschlagenen Standards umgesetzt: Strg+S bzw. Save-Button, Rückfrage „Save / Discard / Cancel“, Bearbeiten nur in der Source-Ansicht. Der Anwender hat dazu nicht ausdrücklich geantwortet. | vom Anwender zu bestätigen |
| E2 | Einschränkung | Wird die Datei während der Bearbeitung von außen geändert, bemerkt der Editor das nicht. Beim Speichern werden die externen Änderungen überschrieben. | bekannt; ggf. Warnung vor dem Speichern nachrüsten |
| E9 | Einschränkung | Code in Fenced-Blöcken wird im Editor zeilenweise hervorgehoben. Mehrzeilige Strings und Kommentare (z. B. Python-Docstrings, `/* … */`) sind daher nur in ihrer ersten Zeile gefärbt. Grund: Sonst kann die eingebettete Grammatik das schließende ```` ``` ```` „verschlucken“ (z. B. JS-Template-Strings), und der Rest der Datei wird falsch gefärbt. | bekannt, bewusst gewählt |
| E10 | Einschränkung | Restliche Unterschiede zur Lesansicht: Einfache Bezeichner (Variablen, Klassennamen) färbt GtkSourceView nicht ein, Pygments schon. Inline-HTML ist im Editor als Tag gefärbt, in der Lesansicht nicht. Nur 27 Sprachen werden in Fenced-Blöcken erkannt; andere sind einfarbig. | bekannt, akzeptiert |
| E4 | Einschränkung | Dateien mit gemischten Zeilenenden (LF und CRLF) werden beim Speichern einheitlich mit CRLF geschrieben. | bekannt, akzeptiert |
| E5 | Einschränkung | Dateien, die kein gültiges UTF-8 sind, können nicht bearbeitet werden: Der Bearbeiten-Button ist deaktiviert, damit beim Speichern keine Bytes verloren gehen. | bekannt, gewollt |
| E6 | Einschränkung | Die Leseposition beim Wechsel zwischen Lesansicht und Editor wird nur näherungsweise übernommen (über den Anteil der Zeilen). | bekannt, akzeptiert |
| A3 | Annahme | „Neue Datei“ öffnet ein neues Fenster. Zeigt das aktuelle Fenster aber gar keine Datei (Platzhalter), wird es wiederverwendet, statt ein leeres Fenster stehen zu lassen. | vom Anwender zu bestätigen |
| E7 | Einschränkung | Wählt man bei „Neue Datei“ eine bestehende .md-Datei und bestätigt „Ersetzen“, wird diese geleert. | bekannt, akzeptiert (Standardverhalten des Dialogs) |
| E8 | Einschränkung | Durch den zusätzlichen New-Button wird der Titel in der Kopfzeile bei schmalem Fenster früher abgeschnitten. | bekannt, akzeptiert |

## Erledigt

| ID | Beschreibung | Erledigt am |
|---|---|---|
| F1 | Editor-Umsetzung: Der Anwender hat sich für **GtkSourceView** entschieden. | 2026-10-31 |
| F5 | Git: Der Anwender hat `git init` freigegeben. Die Funktionen wurden auf `feature/source-editor` entwickelt und am 2026-10-31 in `main` gemergt. | 2026-10-31 |
| F2–F4 | Speichern, ungespeicherte Änderungen, Button-Sichtbarkeit: nach Standardvorschlag umgesetzt, siehe Annahme A2. | 2026-10-31 |
| A1 | „Code-Ansicht“ = Ansicht **Source** (so umgesetzt). | 2026-10-31 |
| F6 | Neue Datei: Der Anwender hat entschieden, dass zuerst der Speicherort gewählt wird und die Datei in einem neuen Fenster öffnet. | 2026-10-31 |
| E3 | Editor-Farben: VS-Code-Farbschemata (`styles/`) und eine erweiterte Grammatik (`language-specs/mdviewer-markdown.lang`) eingebaut. Zitattext und Code in Fenced-Blöcken werden jetzt eingefärbt. Rest siehe E9, E10. | 2026-10-31 |
| E1 | Der automatische Reload ist während der Bearbeitung unterdrückt; Reload und Drucken sind dann deaktiviert. | 2026-10-31 |
