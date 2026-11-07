"""Recreates the user-manual screenshots (docs/bilder/) and sample files (docs/beispiel/).

Run: python3 tools/doku_screenshots.py   (needs a display)
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import md_viewer as mv  # noqa: E402
from gi.repository import Gdk, GLib, Gtk  # noqa: E402

mv.APP_ID = "local.MarkdownViewerDocShots"
OUT = os.path.join(ROOT, "docs", "bilder")
os.makedirs(OUT, exist_ok=True)
mv.CONFIG_FILE = os.path.join(tempfile.mkdtemp(prefix="md-viewer-shots-"), "settings.ini")
tmp = os.path.join(ROOT, "docs", "beispiel")  # shipped as sample files for the manual
os.makedirs(tmp, exist_ok=True)
Gtk.MessageDialog.run = lambda dlg: Gtk.ResponseType.REJECT  # discard the demo edit at the end


def make(name, text):
    path = os.path.join(tmp, name)
    with open(path, "w") as f:
        f.write(text)
    return path


example = make("Projektplan.md", """# Projektplan Website-Relaunch

Dieses Dokument beschreibt **Ziele**, *Zeitplan* und offene Punkte des Relaunchs.
Details stehen in der [Anforderungsliste](Anforderungen.md).

## Ziele

- Ladezeit unter 2 Sekunden
- Barrierefreiheit nach WCAG 2.1 AA
  - Kontraste prüfen
  - Tastaturbedienung testen
- Neues Redaktionssystem

## Zeitplan

| Phase | Start | Ende | Status |
|:---|:---:|:---:|---:|
| Konzept | 01.12. | 19.12. | fertig |
| Umsetzung | 05.01. | 27.02. | läuft |
| Abnahme | 02.03. | 13.03. | offen |

> Hinweis: Die Abnahme setzt einen vollständigen Testlauf voraus.

## Build-Skript

```python
def build(target="production"):
    \"\"\"Baut die Website für das angegebene Ziel.\"\"\"
    for page in pages:
        render(page, minify=True)
    return f"Fertig: {len(pages)} Seiten"
```
""")
other1 = make("Anforderungen.md", "# Anforderungen\n\n1. Responsive Layout\n2. Suche\n")
other2 = make("Notizen.md", "# Notizen\n\n- Termin mit Agentur vereinbaren\n")


def shot(win, name):
    gw = win.get_window()
    Gdk.pixbuf_get_from_window(gw, 0, 0, gw.get_width(), gw.get_height()).savev(
        os.path.join(OUT, name), "png", [], [])
    print("saved", name)


def steps(app, win):
    win.open_paths([example, other1, other2])
    yield
    win.show_tab(app.find_tab(example))  # also presents the window: unfocused windows draw a faded header
    yield
    for theme, suffix in (("light", "hell"), ("dark", "dunkel")):
        app.activate_action("theme", GLib.Variant.new_string(theme))
        tab = win.tab
        tab.set_view_mode("vscode")
        yield
        yield
        shot(win, f"ansicht-vscode-{suffix}.png")
        if theme == "light":
            tab.set_view_mode("source")
            yield
            yield
            shot(win, "ansicht-source-hell.png")
            tab.set_view_mode("document")
            yield
            yield
            shot(win, "ansicht-document-hell.png")
            tab.set_view_mode("vscode")
            yield
        tab.set_editing(True)
        yield
        buf = tab.editor.buffer
        buf.place_cursor(buf.get_iter_at_line(12))
        buf.insert_at_cursor("- Mehrsprachigkeit (Deutsch, Englisch)\n")
        yield
        yield
        shot(win, f"editor-{suffix}.png")
        tab.set_editing(False)  # discards the demo line (dialog stubbed to Discard)
        yield
    for w in app.get_windows():
        w.destroy()
    app.quit()


class ShotApp(mv.ViewerApp):
    def do_activate(self):
        mv.ViewerApp.do_activate(self)
        win = self.viewer_windows()[0]
        win.resize(1100, 760)
        it = steps(self, win)
        GLib.timeout_add(900, lambda: next(it, "done") != "done")


ShotApp().run([])
