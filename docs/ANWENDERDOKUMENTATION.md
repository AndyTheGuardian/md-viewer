# Markdown Viewer – Anwenderdokumentation

Stand: 07.11.2026

Diese Dokumentation beschreibt, was der Markdown Viewer kann, was er voraussetzt und wie man ihn installiert, einrichtet und bei Problemen wieder zum Laufen bringt. Die Bedienung Schritt für Schritt steht im [Benutzerhandbuch](BENUTZERHANDBUCH.md), der technische Aufbau in der [Entwicklerdokumentation](ENTWICKLERDOKUMENTATION.md).

## 1. Zweck und Funktionsumfang

Der Markdown Viewer ist ein Programm für Linux Mint zum Lesen und Bearbeiten von Markdown-Dateien (`.md`).

| Funktion | Kurzbeschreibung |
|---|---|
| Drei Ansichten | **VS Code** (wie die Markdown-Vorschau von VS Code, Standard), **Source** (Quelltext mit Syntaxhervorhebung und Zeilennummern), **Document** (wie ein Word-Dokument auf einer A4-Seite) |
| Tabs | Mehrere Dateien gleichzeitig in einem Fenster; jede Datei hat ihre eigene Ansicht und ihren eigenen Zoom |
| Bearbeiten | Editor mit Zeilennummern, Hervorhebung in VS-Code-Farben, Rückgängig/Wiederholen; Speichern mit Strg+S |
| Neue Datei | Legt eine leere `.md`-Datei an und öffnet sie direkt zum Bearbeiten |
| Theme | Hell, Dunkel oder wie das System |
| Drucken | Drucken oder als PDF speichern, immer im hellen Design |
| Automatisches Neuladen | Ändert ein anderes Programm die Datei, wird die Anzeige sofort aktualisiert |

Unterstützte Markdown-Elemente: Überschriften, Absätze, **fett**, *kursiv*, ~~durchgestrichen~~, Listen (auch verschachtelt), Tabellen mit Ausrichtung, Zitate, Code (auch mit Syntaxhervorhebung für die angegebene Sprache), Links, Bilder, Trennlinien und HTML im Text.

Nicht unterstützt: Fußnoten, Aufgabenlisten (`- [ ]`), automatisch erkannte URLs ohne Link-Syntax und Diagramme (z. B. Mermaid). Diagramme erscheinen als Codeblock.

## 2. Systemvoraussetzungen

| Bereich | Voraussetzung |
|---|---|
| Betriebssystem | Linux Mint 22.x (getestet mit 22.3 „Zena“) oder ein anderes Ubuntu-24.04-basiertes System mit Desktop |
| Python | Python 3.12 |
| Pakete | `python3-gi`, `gir1.2-gtk-3.0`, `gir1.2-webkit2-4.1`, `gir1.2-gtksource-4`, `python3-markdown-it`, `python3-pygments` |
| Optional | `fonts-crosextra-carlito` für die Schrift der Document-Ansicht (sieht aus wie Calibri; sonst wird Liberation Sans verwendet) |

Auf Linux Mint 22.3 sind alle Pflichtpakete bereits vorinstalliert. Getestete Versionen:

| Paket | Version |
|---|---|
| gir1.2-gtk-3.0 | 3.24.41 |
| gir1.2-webkit2-4.1 | 2.52.6 |
| gir1.2-gtksource-4 | 4.8.4 |
| python3-gi | 3.48.2 |
| python3-markdown-it | 3.0.0 |
| python3-pygments | 2.17.2 |

## 3. Installation

### 3.1 Programm ablegen

Das Programm besteht aus dem Ordner `md-viewer` mit dem Skript `md_viewer.py` und den Unterordnern `styles` und `language-specs`. Der Ordner kann an einem beliebigen Ort liegen; hier wird `~/Claude/md-viewer` verwendet.

Fehlende Pakete installieren (nur nötig, wenn sie nicht vorhanden sind):

```bash
sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-webkit2-4.1 gir1.2-gtksource-4 python3-markdown-it python3-pygments
```

Optional die Calibri-ähnliche Schrift für die Document-Ansicht:

```bash
sudo apt install fonts-crosextra-carlito
```

Das Skript ausführbar machen:

```bash
chmod +x ~/Claude/md-viewer/md_viewer.py
```

### 3.2 Menüeintrag und Dateizuordnung

Damit der Viewer im Startmenü erscheint und `.md`-Dateien per Doppelklick öffnet, wird die Datei `~/.local/share/applications/markdown-viewer.desktop` mit diesem Inhalt angelegt (den Pfad bei `Exec` an den eigenen Ablageort anpassen):

```ini
[Desktop Entry]
Type=Application
Name=Markdown Viewer
Comment=View Markdown files formatted like a Word document
Exec=python3 /home/andy/Claude/md-viewer/md_viewer.py %F
Icon=x-office-document
Terminal=false
Categories=Office;Viewer;
MimeType=text/markdown;text/x-markdown;
```

Danach den Viewer als Standardprogramm für Markdown festlegen:

```bash
update-desktop-database ~/.local/share/applications
```

```bash
xdg-mime default markdown-viewer.desktop text/markdown
```

Prüfen: `xdg-mime query default text/markdown` muss `markdown-viewer.desktop` ausgeben.

### 3.3 Programm starten

- Über das Startmenü: **Büro → Markdown Viewer**
- Per Doppelklick auf eine `.md`-Datei im Dateimanager oder über **Öffnen mit**
- Im Terminal, auch mit mehreren Dateien:

```bash
python3 ~/Claude/md-viewer/md_viewer.py datei1.md datei2.md
```

Der Viewer läuft immer nur einmal. Wird er erneut gestartet (z. B. per Doppelklick auf eine weitere Datei), öffnet sich die Datei als neuer Tab im vorhandenen Fenster. Ein Start ohne Datei holt das vorhandene Fenster nach vorn.

## 4. Einstellungen und Dateien

| Datei | Inhalt |
|---|---|
| `~/.config/md-viewer/settings.ini` | Gewähltes Theme (`[viewer] theme=system`, `light` oder `dark`). Wird bei der ersten Änderung angelegt. |
| `~/.local/share/applications/markdown-viewer.desktop` | Menüeintrag und Dateizuordnung |

Die Ansicht (VS Code, Source, Document) und der Zoom werden bewusst nicht gespeichert: Jede Datei öffnet in der VS-Code-Ansicht mit 100 %.

## 5. Umgang mit Dateien und Datensicherheit

- **Kodierung:** Dateien werden als UTF-8 gelesen und gespeichert. Die Zeilenenden der Datei (Linux `LF` oder Windows `CRLF`) bleiben beim Speichern erhalten.
- **Ungültiges UTF-8:** Solche Dateien werden angezeigt (fehlerhafte Zeichen erscheinen als `�`), lassen sich aber nicht bearbeiten. So kann beim Speichern nichts verloren gehen.
- **Keine Skripte:** JavaScript in Dokumenten wird nie ausgeführt.
- **Links:** Links auf andere Markdown-Dateien öffnen im Viewer, alle anderen Links (Webseiten, E-Mail, andere Dateien) im jeweiligen Standardprogramm.
- **Rückfragen:** Wer ungespeicherte Änderungen hat und die Ansicht wechselt, den Tab oder das Fenster schließt oder den Bearbeitungsmodus verlässt, wird gefragt: Speichern, Verwerfen oder Abbrechen.
- **Automatisches Neuladen:** Ändert ein anderes Programm die Datei, wird die Anzeige aktualisiert. Während der Bearbeitung ist das abgeschaltet, damit die eigenen Änderungen nicht überschrieben werden.

## 6. Bekannte Einschränkungen

| Einschränkung | Auswirkung |
|---|---|
| Externe Änderungen während der Bearbeitung | Werden nicht erkannt. Beim Speichern werden sie überschrieben. |
| Gemischte Zeilenenden | Eine Datei mit LF- und CRLF-Zeilen wird beim Speichern einheitlich mit CRLF geschrieben. |
| Hervorhebung im Editor | Code in Codeblöcken wird zeilenweise hervorgehoben: Mehrzeilige Kommentare und Strings sind nur in ihrer ersten Zeile gefärbt. 27 Sprachen werden erkannt, andere bleiben einfarbig. Variablennamen werden im Editor nicht gefärbt. |
| Leseposition | Beim Wechsel zwischen Ansicht und Editor wird die Position nur ungefähr übernommen. |
| Ein Programm für alle Dateien | Stürzt der Viewer ab, sind alle Tabs geschlossen, und ungespeicherte Änderungen in allen Tabs gehen verloren. |
| Keine Sitzung | Offene Tabs werden beim Beenden nicht gemerkt. |
| Mehrere Dateien hineinziehen | Vermutlich öffnet sich nur die erste (nicht getestet). |
| Neue Datei mit vorhandenem Namen | Bestätigt man im Dialog „Ersetzen“, wird die vorhandene Datei geleert. |
| Seitenumbrüche | Die Document-Ansicht zeigt eine durchgehende Seite. Echte Seitenumbrüche gibt es erst beim Drucken. |

Die vollständige, laufend gepflegte Liste steht in [OFFENE-PUNKTE.md](../OFFENE-PUNKTE.md).

## 7. Fehlerbehebung

| Problem | Ursache und Lösung |
|---|---|
| Das Fenster bleibt weiß | Fehlende 3D-Beschleunigung (z. B. in einer virtuellen Maschine). Der Viewer schaltet die GPU-Darstellung deshalb selbst ab. Wird das Programm über einen eigenen Starter aufgerufen, darf dieser `WEBKIT_DISABLE_COMPOSITING_MODE` nicht auf `0` setzen. |
| Doppelklick öffnet ein anderes Programm | Die Zuordnung prüfen bzw. neu setzen (Abschnitt 3.2). |
| Eine Datei öffnet nicht als Tab, sondern gar nicht oder in einem anderen Fenster | Es läuft noch eine ältere Version des Viewers. Alle Viewer-Fenster schließen und neu starten. |
| Der Editor ist nicht farbig oder in anderen Farben | Die Ordner `styles` und `language-specs` fehlen neben `md_viewer.py`. Der Viewer nutzt dann die Standardfarben von GtkSourceView. |
| Der Bearbeiten-Button (Stift) ist ausgegraut | Es ist keine Datei geöffnet, oder die Datei ist kein gültiges UTF-8 (Tooltip des Buttons beachten). |
| Die Document-Ansicht sieht nicht nach Calibri aus | `fonts-crosextra-carlito` installieren (Abschnitt 3.1). |
| Fehlermeldung beim Start: `Namespace … not available` | Ein Paket aus Abschnitt 2 fehlt; der Name in der Meldung (z. B. `GtkSource`) zeigt, welches. |

## 8. Deinstallation

```bash
rm ~/.local/share/applications/markdown-viewer.desktop
```

```bash
rm -r ~/.config/md-viewer
```

Danach kann der Ordner `md-viewer` gelöscht werden. Die installierten Systempakete werden auch von anderen Programmen verwendet und sollten bleiben.
