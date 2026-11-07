"""End-to-end test of tabs, view modes and editing; drives the real GTK app.

Run: python3 tests/test_tabs.py   (needs a display; prints PASS/FAIL per check, exit code 1 on failure)
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import md_viewer as mv  # noqa: E402
from gi.repository import Gdk, Gio, GLib, Gtk  # noqa: E402

mv.APP_ID = "local.MarkdownViewerTest"  # never the real id: a running viewer would get our files
tmp = tempfile.mkdtemp(prefix="md-viewer-test-")
OUT = tmp
mv.CONFIG_FILE = os.path.join(tmp, "settings.ini")  # never touch the user's settings


def make(name, data):
    path = os.path.join(tmp, name)
    with open(path, "wb") as f:
        f.write(data)
    return path


a = make("a.md", b"# A\r\n\r\nFirst file.\r\n")
b = make("b.md", b"# B\n\nSecond file with a [link](c.md).\n")
c = make("c.md", b"# C\n")
d = make("d.md", b"# D\n")
bad = make("bad.md", b"# Bad \xff\n")

answer = {"r": Gtk.ResponseType.CANCEL}
dialogs = []
Gtk.MessageDialog.run = lambda dlg: (dialogs.append(dlg.props.text), answer["r"])[1]
chooser = {"names": []}
Gtk.FileChooserNative.run = lambda dlg: Gtk.ResponseType.ACCEPT
Gtk.FileChooserNative.get_filename = lambda dlg: os.path.join(tmp, chooser["names"][0])
Gtk.FileChooserNative.get_filenames = lambda dlg: [os.path.join(tmp, n) for n in chooser["names"]]

results = []


def check(name, cond):
    results.append(("PASS" if cond else "FAIL", name))


def titles(win):
    return [win.notebook.get_tab_label(t).label.get_text() for t in win.tabs]


def mode_buttons(win):
    box = [ch for ch in win.header.get_children()
           if isinstance(ch, Gtk.Box) and all(isinstance(b, Gtk.ToggleButton) for b in ch.get_children())][0]
    return [(btn.get_label(), btn.get_active()) for btn in box.get_children()]


def shot(win, name):
    gw = win.get_window()
    Gdk.pixbuf_get_from_window(gw, 0, 0, gw.get_width(), gw.get_height() // 2).savev(
        os.path.join(OUT, name), "png", [], [])


def steps(app):
    win = app.viewer_windows()[0]
    yield
    check("starts with one placeholder tab, tab bar hidden",
          len(win.tabs) == 1 and win.tab.path is None and not win.notebook.get_show_tabs())
    check("toggle order VS Code, Source, Document; VS Code active",
          mode_buttons(win) == [("VS Code", True), ("Source", False), ("Document", False)])
    check("default view is vscode", win.tab.view_mode == "vscode")

    win.open_paths([a, b])
    yield
    check("two files in two tabs (placeholder reused)", titles(win) == ["a.md", "b.md"])
    check("tab bar visible, last opened is current", win.notebook.get_show_tabs() and win.tab.path == b)
    check("header follows current tab", win.get_title().startswith("b.md"))

    chooser["names"] = ["c.md", "a.md"]  # multi-select; a.md is already open
    win.choose_files()
    yield
    check("Open with several files: new tabs, no duplicates", titles(win) == ["a.md", "b.md", "c.md"])
    check("already open file is shown", win.tab.path == a)

    tab_a = win.tab
    tab_a.set_view_mode("document")
    tab_a.zoom(0.2)
    yield
    check("view per tab: a in document", mode_buttons(win)[2] == ("Document", True))
    check("zoom per tab: a at 120%", win.zoom_label.get_label() == "120%")
    win.cycle_tab(1)
    yield
    check("switching to b shows b's view and zoom", win.tab.path == b and win.tab.view_mode == "vscode"
          and mode_buttons(win)[0] == ("VS Code", True) and win.zoom_label.get_label() == "100%")
    win.cycle_tab(-1)
    yield
    check("back on a: document view, 120%", win.tab is tab_a and mode_buttons(win)[2] == ("Document", True)
          and win.zoom_label.get_label() == "120%")
    tab_a.zoom(None)

    # Editing from a non-source view switches to Source
    tab_b = app.find_tab(b)
    win.show_tab(tab_b)
    check("edit enabled in VS Code view", win.lookup_action("edit").get_enabled())
    win.activate_action("edit", None)
    yield
    check("editing switched b to Source", tab_b.editing and tab_b.view_mode == "source"
          and tab_b.stack.get_visible_child() is tab_b.editor)
    check("Source button active, Save visible", mode_buttons(win)[1] == ("Source", True)
          and win.save_btn.get_visible())
    buf = tab_b.editor.buffer
    buf.insert(buf.get_end_iter(), "Edited.\n")
    check("tab label and title show *", titles(win)[1] == "*b.md" and win.get_title().startswith("*b.md"))
    shot(win, "t-editing.png")

    win.cycle_tab(-1)
    yield
    check("other tab is not in edit mode", not win.tab.editing and not win.save_btn.get_visible()
          and win.lookup_action("edit").get_state().get_boolean() is False)
    win.show_tab(tab_b)

    # switching view while editing: cancel keeps editing
    answer["r"] = Gtk.ResponseType.CANCEL
    win.lookup_action("view-mode").change_state(GLib.Variant.new_string("vscode"))
    yield
    check("cancel keeps Source + editing", tab_b.editing and tab_b.view_mode == "source"
          and mode_buttons(win)[1] == ("Source", True))

    # close tab with unsaved edits: cancel, then save
    tab_b_count = len(win.tabs)
    win.close_tab(tab_b)
    yield
    check("close tab cancelled", len(win.tabs) == tab_b_count and tab_b.editing)
    answer["r"] = Gtk.ResponseType.ACCEPT
    win.close_tab(tab_b)
    yield
    check("save on close writes the file and closes the tab",
          "Edited." in open(b).read() and len(win.tabs) == tab_b_count - 1)

    # links open in a new tab
    tab_a.emit("open-file", d)
    yield
    check("link opens a new tab", titles(win) == ["a.md", "c.md", "d.md"] and win.tab.path == d)

    # files opened from outside (file manager / second launch) become tabs
    app.open([Gio.File.new_for_path(b)], "")
    yield
    check("app.open adds a tab in the active window", len(app.viewer_windows()) == 1
          and titles(win)[-1] == "b.md")

    # New file: new tab, editing, Source view
    chooser["names"] = ["new"]
    win.new_file()
    yield
    new_tab = win.tab
    check("New: tab with new.md in Source, editing", new_tab.path == os.path.join(tmp, "new.md")
          and new_tab.editing and new_tab.view_mode == "source" and len(win.tabs) == 5)

    # CRLF preserved on save
    win.show_tab(tab_a)
    tab_a.set_editing(True)
    yield
    check("a switched from document to Source for editing", tab_a.view_mode == "source" and tab_a.editing)
    tab_a.editor.buffer.insert(tab_a.editor.buffer.get_end_iter(), "More.\n")
    check("CRLF kept on save", tab_a.save() and open(a, "rb").read().endswith(b"First file.\r\nMore.\r\n"))
    with open(a, "ab") as f:
        f.write(b"external\r\n")
    yield
    check("external change ignored while editing", "external" not in tab_a.editor.text)
    tab_a.set_editing(False)
    yield

    # invalid UTF-8 can't be edited
    win.open_paths([bad])
    yield
    check("invalid UTF-8 tab not editable", not win.lookup_action("edit").get_enabled())

    # window close asks for unsaved tabs
    new_tab.editor.buffer.insert_at_cursor("x")
    answer["r"] = Gtk.ResponseType.CANCEL
    n = len(dialogs)
    win.close()
    yield
    check("window close cancelled by unsaved tab", len(dialogs) == n + 1 and win.get_visible()
          and win.tab is new_tab)

    # close every tab: placeholder remains, tab bar hidden
    answer["r"] = Gtk.ResponseType.REJECT
    for tab in list(win.tabs):
        win.close_tab(tab)
    yield
    check("closing all tabs leaves the placeholder", len(win.tabs) == 1 and win.tab.path is None
          and not win.notebook.get_show_tabs())

    for status, name in results:
        print(status, name)
    for w in app.get_windows():
        w.destroy()
    app.quit()


class TestApp(mv.ViewerApp):
    def do_activate(self):
        mv.ViewerApp.do_activate(self)
        it = steps(self)
        GLib.timeout_add(1000, lambda: next(it, "done") != "done")


TestApp().run([])
print(f"{sum(s == 'PASS' for s, _ in results)}/{len(results)} passed; files in {tmp}")
sys.exit(0 if results and all(s == "PASS" for s, _ in results) else 1)
