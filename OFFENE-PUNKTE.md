# Offene Punkte – md-viewer

Stand: 2026-11-07

## Offen

| ID | Art | Beschreibung | Status |
|---|---|---|---|
| A2 | Annahme | Speichern und ungespeicherte Änderungen (ursprünglich F2/F3) wurden nach den vorgeschlagenen Standards umgesetzt: Strg+S bzw. Save-Button, Rückfrage „Save / Discard / Cancel“ (jetzt auch beim Schließen eines Tabs). Der Anwender hat dazu nicht ausdrücklich geantwortet. Die Button-Sichtbarkeit (F4) hat der Anwender am 2026-11-07 neu festgelegt, siehe F7. | vom Anwender zu bestätigen |
| E2 | Einschränkung | Wird die Datei während der Bearbeitung von außen geändert, bemerkt der Editor das nicht. Beim Speichern werden die externen Änderungen überschrieben. | bekannt; ggf. Warnung vor dem Speichern nachrüsten |
| E9 | Einschränkung | Code in Fenced-Blöcken wird im Editor zeilenweise hervorgehoben. Mehrzeilige Strings und Kommentare (z. B. Python-Docstrings, `/* … */`) sind daher nur in ihrer ersten Zeile gefärbt. Grund: Sonst kann die eingebettete Grammatik das schließende ```` ``` ```` „verschlucken“ (z. B. JS-Template-Strings), und der Rest der Datei wird falsch gefärbt. | bekannt, bewusst gewählt |
| E10 | Einschränkung | Restliche Unterschiede zur Lesansicht: Einfache Bezeichner (Variablen, Klassennamen) färbt GtkSourceView nicht ein, Pygments schon. Inline-HTML ist im Editor als Tag gefärbt, in der Lesansicht nicht. Nur 27 Sprachen werden in Fenced-Blöcken erkannt; andere sind einfarbig. | bekannt, akzeptiert |
| E4 | Einschränkung | Dateien mit gemischten Zeilenenden (LF und CRLF) werden beim Speichern einheitlich mit CRLF geschrieben. | bekannt, akzeptiert |
| E5 | Einschränkung | Dateien, die kein gültiges UTF-8 sind, können nicht bearbeitet werden: Der Bearbeiten-Button ist deaktiviert, damit beim Speichern keine Bytes verloren gehen. | bekannt, gewollt |
| E6 | Einschränkung | Die Leseposition beim Wechsel zwischen Lesansicht und Editor wird nur näherungsweise übernommen (über den Anteil der Zeilen). | bekannt, akzeptiert |
| E7 | Einschränkung | Wählt man bei „Neue Datei“ eine bestehende .md-Datei und bestätigt „Ersetzen“, wird diese geleert. | bekannt, akzeptiert (Standardverhalten des Dialogs) |
| E8 | Einschränkung | Durch den zusätzlichen New-Button wird der Titel in der Kopfzeile bei schmalem Fenster früher abgeschnitten. | bekannt, akzeptiert |
| E11 | Einschränkung | Alle Dateien laufen in einem Prozess (Single Instance). Stürzt die App ab, sind alle Tabs zu, und ungespeicherte Änderungen in allen Tabs gehen verloren. | bekannt, akzeptiert |
| E12 | Einschränkung | Offene Tabs werden beim Beenden nicht gemerkt und beim nächsten Start nicht wiederhergestellt. | bekannt; ggf. später nachrüsten |
| E13 | Einschränkung | Zieht man mehrere Dateien gleichzeitig ins Fenster, öffnet sich voraussichtlich nur die erste (WebKit verarbeitet nur eine Navigation). Nicht getestet. | ungeprüft |

## Erledigt

| ID | Beschreibung | Erledigt am |
|---|---|---|
| F1 | Editor-Umsetzung: Der Anwender hat sich für **GtkSourceView** entschieden. | 2026-10-31 |
| F5 | Git: Der Anwender hat `git init` freigegeben. Die Funktionen wurden auf `feature/source-editor` entwickelt und am 2026-10-31 in `main` gemergt. | 2026-10-31 |
| F2–F4 | Speichern, ungespeicherte Änderungen, Button-Sichtbarkeit: nach Standardvorschlag umgesetzt, siehe Annahme A2. | 2026-10-31 |
| A1 | „Code-Ansicht“ = Ansicht **Source** (so umgesetzt). | 2026-10-31 |
| F6 | Neue Datei: Der Anwender hat entschieden, dass zuerst der Speicherort gewählt wird und die Datei in einem neuen Fenster öffnet. | 2026-10-31 |
| E3 | Editor-Farben: VS-Code-Farbschemata (`styles/`) und eine erweiterte Grammatik (`language-specs/mdviewer-markdown.lang`) eingebaut. Zitattext und Code in Fenced-Blöcken werden jetzt eingefärbt. Rest siehe E9, E10. | 2026-10-31 |
| A3 | „Neue Datei“ in einem neuen Fenster mit Wiederverwendung leerer Fenster: überholt; neue Dateien öffnen jetzt als Tab (F7). | 2026-11-07 |
| F7 | Tabs: Der Anwender hat entschieden, dass von außen geöffnete Dateien (Doppelklick) als Tab im vorhandenen Fenster öffnen, „Open“ mehrere Dateien in neuen Tabs öffnet, Links in einem neuen Tab öffnen und Ansicht und Zoom pro Tab gelten. Außerdem: VS Code ist Standardansicht, Reihenfolge VS Code, Source, Document, und Bearbeiten bzw. Neue Datei wechseln automatisch in die Source-Ansicht. | 2026-11-07 |
| E1 | Der automatische Reload ist während der Bearbeitung unterdrückt; Reload und Drucken sind dann deaktiviert. | 2026-10-31 |
| A4 | Strg+W schließt den aktuellen Tab (auf dem leeren Platzhalter das Fenster), Strg+Q immer das Fenster: vom Anwender bestätigt. | 2026-11-07 |
| A5 | Ein erneuter Start aus dem Menü holt das vorhandene Fenster nach vorn; kein zweites Fenster: vom Anwender bestätigt. | 2026-11-07 |
| E14 | Im Dark Mode war der aktive Ansichts-Button kaum zu erkennen: Aktive Buttons der Kopfzeile sind jetzt ca. 10 % heller hinterlegt (nur im Dark Mode). | 2026-11-07 |
