# Offene Punkte – md-viewer

Stand: 2026-10-31

## Offen

| ID | Art | Beschreibung | Status |
|---|---|---|---|
| A2 | Annahme | Speichern, ungespeicherte Änderungen und Button-Sichtbarkeit (ursprünglich F2–F4) wurden nach den vorgeschlagenen Standards umgesetzt: Strg+S bzw. Save-Button, Rückfrage „Save / Discard / Cancel“, Bearbeiten nur in der Source-Ansicht. Der Anwender hat dazu nicht ausdrücklich geantwortet. | vom Anwender zu bestätigen |
| E2 | Einschränkung | Wird die Datei während der Bearbeitung von außen geändert, bemerkt der Editor das nicht. Beim Speichern werden die externen Änderungen überschrieben. | bekannt; ggf. Warnung vor dem Speichern nachrüsten |
| E3 | Einschränkung | Der Editor nutzt die GtkSourceView-Farbschemata `classic` (hell) und `oblivion` (dunkel). Die Farben weichen vom VS-Code-Look der Lesansicht ab. Code in Fenced-Blocks (z. B. ```` ```python ````) wird im Editor nicht nach Sprache eingefärbt. | bekannt, akzeptiert |
| E4 | Einschränkung | Dateien mit gemischten Zeilenenden (LF und CRLF) werden beim Speichern einheitlich mit CRLF geschrieben. | bekannt, akzeptiert |
| E5 | Einschränkung | Dateien, die kein gültiges UTF-8 sind, können nicht bearbeitet werden: Der Bearbeiten-Button ist deaktiviert, damit beim Speichern keine Bytes verloren gehen. | bekannt, gewollt |
| E6 | Einschränkung | Die Leseposition beim Wechsel zwischen Lesansicht und Editor wird nur näherungsweise übernommen (über den Anteil der Zeilen). | bekannt, akzeptiert |

## Erledigt

| ID | Beschreibung | Erledigt am |
|---|---|---|
| F1 | Editor-Umsetzung: Der Anwender hat sich für **GtkSourceView** entschieden. | 2026-10-31 |
| F5 | Git: Der Anwender hat `git init` freigegeben. `main` enthält den Stand vom 2026-10-27, die Funktion liegt auf dem Branch `feature/source-editor`. | 2026-10-31 |
| F2–F4 | Speichern, ungespeicherte Änderungen, Button-Sichtbarkeit: nach Standardvorschlag umgesetzt, siehe Annahme A2. | 2026-10-31 |
| A1 | „Code-Ansicht“ = Ansicht **Source** (so umgesetzt). | 2026-10-31 |
| E1 | Der automatische Reload ist während der Bearbeitung unterdrückt; Reload und Drucken sind dann deaktiviert. | 2026-10-31 |
