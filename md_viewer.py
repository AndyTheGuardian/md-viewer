#!/usr/bin/env python3
"""Markdown viewer for Linux Mint: Word-like, VS Code-like or raw source view."""

import html
import os
import re
import sys
from urllib.parse import unquote, urlparse

# WebKit's GPU compositing renders a blank page on machines without working
# 3D acceleration (e.g. VMs); software rendering is plenty for documents.
os.environ.setdefault("WEBKIT_DISABLE_COMPOSITING_MODE", "1")
os.environ.setdefault("WEBKIT_DISABLE_DMABUF_RENDERER", "1")

import gi  # noqa: E402
from markdown_it import MarkdownIt  # noqa: E402

try:
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import MarkdownLexer, get_lexer_by_name
    from pygments.token import STANDARD_TYPES
    from pygments.util import ClassNotFound
except ImportError:  # no syntax colouring; everything shows as plain text
    MarkdownLexer = None

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("WebKit2", "4.1")
from gi.repository import Gdk, Gio, GLib, Gtk, WebKit2  # noqa: E402

APP_NAME = "Markdown Viewer"


def highlight_code(code, lang, _attrs):
    """Colour a fenced code block by its language tag; "" lets markdown-it escape it plainly."""
    if MarkdownLexer is None or not lang:
        return ""
    try:
        lexer = get_lexer_by_name(lang, stripnl=False)
    except ClassNotFound:
        return ""
    return highlight(code, lexer, HtmlFormatter(nowrap=True))


# GitHub-flavoured: CommonMark + tables, strikethrough and inline HTML
MD = MarkdownIt("commonmark", {"html": True, "highlight": highlight_code}).enable(
    ["table", "strikethrough"])
MD_SUFFIXES = (".md", ".markdown", ".mdown", ".mkd")
ZOOM_STEP = 0.1
CONFIG_FILE = os.path.join(GLib.get_user_config_dir(), "md-viewer", "settings.ini")

VIEW_MODES = [("source", "Source", "Markdown source with syntax highlighting (Ctrl+1)"),
              ("vscode", "VS Code", "Formatted like the VS Code Markdown preview (Ctrl+2)"),
              ("document", "Document", "Formatted like a Word document (Ctrl+3)")]
DEFAULT_VIEW_MODE = "source"  # every window opens in this view
THEMES = [("system", "Follow system"), ("light", "Light"), ("dark", "Dark")]

# Every stylesheet defines its colours as variables on :root (light) and
# html.dark (dark); printing always uses the light palette.

# Word-like styling: grey canvas, white A4 sheet with 2.54 cm margins,
# Calibri 11 pt body and Word's default blue heading styles.
DOCUMENT_CSS = """
:root {
  --canvas: #e7e7e7; --paper: #fff; --text: #000; --heading: #2F5496; --heading-dark: #1F3763;
  --link: #0563C1; --quote: #404040; --code-bg: #f2f2f2; --code-border: #d9d9d9;
  --rule: #a5a5a5; --grid: #000; --muted: #7f7f7f; --shadow: rgba(0,0,0,.25);
}
html.dark {
  --canvas: #1e1e1e; --paper: #2b2b2b; --text: #e6e6e6; --heading: #7fa7e3; --heading-dark: #a3bfe9;
  --link: #6cb4ff; --quote: #b5b5b5; --code-bg: #363636; --code-border: #4a4a4a;
  --rule: #6a6a6a; --grid: #8c8c8c; --muted: #9a9a9a; --shadow: rgba(0,0,0,.6);
}
@page { size: A4; margin: 2.54cm; }
html { background: var(--canvas); }
body {
  margin: 0; padding: 32px 16px;
  font-family: Calibri, Carlito, "Liberation Sans", Arial, sans-serif;
  font-size: 11pt; line-height: 1.15; color: var(--text);
}
.page {
  box-sizing: border-box; width: 21cm; max-width: 100%; min-height: 29.7cm;
  margin: 0 auto; padding: 2.54cm; background: var(--paper);
  box-shadow: 0 1px 4px var(--shadow), 0 0 1px var(--shadow);
}
p, ul, ol, dl, table, pre, blockquote { margin: 0 0 8pt; }
h1, h2, h3, h4, h5, h6 {
  font-family: "Calibri Light", Carlito, "Liberation Sans", Arial, sans-serif;
  font-weight: normal; color: var(--heading); margin: 12pt 0 4pt; line-height: 1.1;
}
h1 { font-size: 16pt; }
h2 { font-size: 13pt; }
h3 { font-size: 12pt; color: var(--heading-dark); }
h4 { font-size: 11pt; font-style: italic; }
h5 { font-size: 11pt; }
h6 { font-size: 11pt; color: var(--heading-dark); }
.page > :first-child { margin-top: 0; }
a { color: var(--link); }
ul, ol { padding-left: 0.63cm; }
li { margin: 0 0 2pt; }
li > p { margin: 0; }
blockquote {
  margin-left: 0.86cm; margin-right: 0.86cm; padding: 0;
  font-style: italic; color: var(--quote);
}
code {
  font-family: Consolas, "Liberation Mono", monospace; font-size: 10pt;
  background: var(--code-bg); padding: 0 2px;
}
pre {
  background: var(--code-bg); border: 1px solid var(--code-border); padding: 6pt 8pt;
  white-space: pre-wrap; word-wrap: break-word;
}
pre code { background: none; padding: 0; }
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid var(--grid); padding: 0 5.4pt; vertical-align: top; text-align: left; }
th { font-weight: bold; }
hr { border: none; border-top: 1px solid var(--rule); margin: 12pt 0; }
img { max-width: 100%; }
.placeholder { color: var(--muted); text-align: center; padding-top: 8cm; }
.placeholder h1 { color: var(--muted); }
@media print {
  html, body { background: #fff; padding: 0; }
  .page { width: auto; min-height: 0; padding: 0; box-shadow: none; }
}
"""

# Modelled on VS Code's built-in Markdown preview (Light/Dark Modern themes).
VSCODE_CSS = """
:root {
  --bg: #ffffff; --text: #3b3b3b; --link: #005fb8; --rule: rgba(0,0,0,.18);
  --code-bg: rgba(220,220,220,.4); --inline-bg: rgba(0,0,0,.06);
  --quote-bg: #f2f2f2; --quote-border: #e5e5e5; --th-border: rgba(0,0,0,.69);
  --td-border: rgba(0,0,0,.18); --muted: #8b8b8b;
}
html.dark {
  --bg: #1f1f1f; --text: #cccccc; --link: #4daafc; --rule: rgba(255,255,255,.18);
  --code-bg: rgba(10,10,10,.4); --inline-bg: rgba(255,255,255,.1);
  --quote-bg: #2b2b2b; --quote-border: #616161; --th-border: rgba(255,255,255,.69);
  --td-border: rgba(255,255,255,.18); --muted: #8b8b8b;
}
html { background: var(--bg); }
body {
  margin: 0; padding: 0 26px 26px; color: var(--text); word-wrap: break-word;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe WPC", "Segoe UI", system-ui,
               "Ubuntu", "Droid Sans", sans-serif;
  font-size: 14px; line-height: 22px;
}
.page > :first-child { margin-top: 26px; }
h1, h2, h3, h4, h5, h6 { font-weight: 600; margin-top: 24px; margin-bottom: 16px; line-height: 1.25; }
h1 { font-size: 2em; padding-bottom: .3em; border-bottom: 1px solid var(--rule); }
h2 { font-size: 1.5em; padding-bottom: .3em; border-bottom: 1px solid var(--rule); }
h3 { font-size: 1.25em; }
h4 { font-size: 1em; }
h5 { font-size: .875em; }
h6 { font-size: .85em; }
p, ul, ol, table, pre, blockquote { margin: 0 0 16px; }
ul, ol { padding-left: 2em; }
a { color: var(--link); text-decoration: none; }
a:hover { text-decoration: underline; }
hr { border: 0; height: 1px; background: var(--rule); }
code {
  font-family: "Droid Sans Mono", "DejaVu Sans Mono", "Liberation Mono", monospace;
  font-size: 1em; line-height: 1.357em; background: var(--inline-bg);
  padding: 1px 3px; border-radius: 4px;
}
pre { background: var(--code-bg); padding: 16px; border-radius: 3px; overflow: auto; }
pre code { background: none; padding: 0; white-space: pre; }
blockquote {
  margin: 0 7px 16px 5px; padding: 0 16px 0 10px;
  background: var(--quote-bg); border-left: 5px solid var(--quote-border);
}
blockquote > :last-child { margin-bottom: 0; padding-bottom: 1px; }
table { border-collapse: collapse; }
th { text-align: left; border-bottom: 1px solid var(--th-border); }
th, td { padding: 5px 10px; }
tbody tr + tr td { border-top: 1px solid var(--td-border); }
img { max-width: 100%; }
.placeholder { color: var(--muted); text-align: center; padding-top: 30vh; }
.placeholder h1 { border: none; }
"""

# Raw Markdown in an editor-like view (VS Code editor colours and gutter).
# Syntax colours follow VS Code's Light+/Dark+ themes, keyed by Pygments' token classes.
SOURCE_CSS = """
:root {
  --bg: #ffffff; --text: #3b3b3b; --gutter: #6e7681; --muted: #8b8b8b;
  --heading: #800000; --marker: #0451a5; --raw: #800000; --link-text: #a31515;
  --link-url: #0070c1; --quote: #0451a5;
}
html.dark {
  --bg: #1f1f1f; --text: #cccccc; --gutter: #6e7681; --muted: #8b8b8b;
  --heading: #569cd6; --marker: #6796e6; --raw: #ce9178; --link-text: #ce9178;
  --link-url: #3794ff; --quote: #6a9955;
}
/* Markdown tokens (these override the code colours from HIGHLIGHT_CSS) */
.gh, .gu { color: var(--heading); font-weight: bold; }
.gs { font-weight: bold; }
.ge { font-style: italic; }
.gd { text-decoration: line-through; color: inherit; }
.sb { color: var(--raw); }
.nt { color: var(--link-text); }
.na { color: var(--link-url); }
.marker { color: var(--marker); }
.quote { color: var(--quote); }
html { background: var(--bg); }
body {
  margin: 0; padding: 12px 16px 12px 0; color: var(--text); counter-reset: line;
  font-family: "Droid Sans Mono", "DejaVu Sans Mono", "Liberation Mono", monospace;
  font-size: 14px; line-height: 19px;
}
.line {
  position: relative; padding-left: 72px; min-height: 19px;
  white-space: pre-wrap; word-wrap: break-word; tab-size: 4;
}
.line::before {
  counter-increment: line; content: counter(line);
  position: absolute; left: 0; width: 48px; text-align: right;
  color: var(--gutter); user-select: none;
}
.placeholder { color: var(--muted); text-align: center; padding-top: 30vh;
  font-family: system-ui, "Ubuntu", sans-serif; }
"""

# Code colours for all views (fenced blocks), following VS Code Light+ / Dark+
# and keyed by Pygments' short token classes.
HIGHLIGHT_CSS = """
:root {
  --hl-keyword: #0000ff; --hl-control: #af00db; --hl-function: #795e26; --hl-type: #267f99;
  --hl-variable: #001080; --hl-string: #a31515; --hl-number: #098658; --hl-comment: #008000;
  --hl-tag: #800000; --hl-attr: #e50000; --hl-regex: #811f3f;
}
html.dark {
  --hl-keyword: #569cd6; --hl-control: #c586c0; --hl-function: #dcdcaa; --hl-type: #4ec9b0;
  --hl-variable: #9cdcfe; --hl-string: #ce9178; --hl-number: #b5cea8; --hl-comment: #6a9955;
  --hl-tag: #569cd6; --hl-attr: #9cdcfe; --hl-regex: #d16969;
}
.k, .kc, .kd, .kp, .kr, .kt, .ow { color: var(--hl-keyword); }
.kn { color: var(--hl-control); }
.nf, .fm, .nb, .bp, .nd { color: var(--hl-function); }
.nc, .nn, .ne { color: var(--hl-type); }
.n, .nx, .nl, .nv, .vc, .vg, .vi, .vm, .py { color: var(--hl-variable); }
.no { color: var(--hl-number); }
.s, .s1, .s2, .sa, .sb, .sc, .dl, .sd, .se, .sh, .si, .sx, .ss { color: var(--hl-string); }
.sr { color: var(--hl-regex); }
.m, .mb, .mf, .mh, .mi, .il, .mo { color: var(--hl-number); }
.c, .c1, .ch, .cm, .cp, .cpf, .cs { color: var(--hl-comment); font-style: italic; }
.nt { color: var(--hl-tag); }
.na { color: var(--hl-attr); }
.gh, .gu { font-weight: bold; }
.gs { font-weight: bold; }
.ge { font-style: italic; }
.gi { color: var(--hl-string); }
.gd { color: var(--hl-attr); }
"""

PRINT_LIGHT = "@media print { html.dark { %s } }"

PAGE_TEMPLATE = """<!doctype html>
<html class="{theme}"><head><meta charset="utf-8"><title>{title}</title>
<style>{css}</style></head>
<body><div class="page">{body}</div></body></html>"""

PLACEHOLDER = """<div class="placeholder">
<h1>No document open</h1>
<p>Open a Markdown file with <b>Ctrl+O</b>, or drop one onto this window.</p>
</div>"""

# Page background per (mode, dark), so the view doesn't flash white while loading
BACKGROUNDS = {("document", False): "#e7e7e7", ("document", True): "#1e1e1e",
               ("vscode", False): "#ffffff", ("vscode", True): "#1f1f1f",
               ("source", False): "#ffffff", ("source", True): "#1f1f1f"}


def build_css(mode):
    css = HIGHLIGHT_CSS + {"document": DOCUMENT_CSS, "vscode": VSCODE_CSS, "source": SOURCE_CSS}[mode]
    light_vars = "".join(re.findall(r":root\s*\{(.*?)\}", css, re.S))
    return css + PRINT_LIGHT % light_vars


def render_markdown(source):
    """Render Markdown to HTML, giving headings GitHub-style ids so #anchor links work."""
    body = MD.render(source)
    used = {}

    def add_id(m):
        text = html.unescape(re.sub(r"<[^>]+>", "", m.group(3)))
        slug = re.sub(r"[^\w\- ]", "", text.strip().lower()).replace(" ", "-")
        n = used.get(slug, 0)
        used[slug] = n + 1
        if n:
            slug = f"{slug}-{n}"
        return f'<h{m.group(1)}{m.group(2)} id="{html.escape(slug)}">{m.group(3)}</h{m.group(1)}>'

    return re.sub(r"<h([1-6])([^>]*)>(.*?)</h\1>", add_id, body, flags=re.S)


MARKER_RE = re.compile(r"[*+-]|\d+[.)]|>")


def token_class(ttype):
    """Pygments' short CSS class for a token type ("gh", "k", ...; "" for plain text)."""
    while ttype not in STANDARD_TYPES:
        ttype = ttype.parent
    return STANDARD_TYPES[ttype]


def render_source(source):
    """Show the raw Markdown text with syntax colouring, one numbered line per div."""
    if MarkdownLexer is None:
        tokens = [(None, source)]
    else:
        # Keep leading/trailing blank lines so the line numbers match the file
        tokens = MarkdownLexer(stripnl=False, ensurenl=False).get_tokens(source)
    lines = [[]]
    in_quote = False
    for ttype, value in tokens:
        cls = token_class(ttype) if ttype else ""
        # The lexer reports list bullets and "> " as keywords and quote text as emphasis
        if cls == "k" and MARKER_RE.fullmatch(value.strip()):
            in_quote = value.strip() == ">"
            cls = "k marker"
        elif cls == "ge" and in_quote:
            cls = "ge quote"
            in_quote = False
        # Tokens can span lines; split them so every line stays its own div
        for i, part in enumerate(value.split("\n")):
            if i:
                lines.append([])
            if part:
                text = html.escape(part)
                lines[-1].append(f'<span class="{cls}">{text}</span>' if cls else text)
    return "".join(f'<div class="line">{"".join(parts)}</div>' for parts in lines)


def word_count(html_body):
    text = html.unescape(re.sub(r"<[^>]+>", " ", html_body))
    return len(re.findall(r"\w+", text))


# ---- desktop theme handling -------------------------------------------------

def settings_if_installed(schema_id):
    source = Gio.SettingsSchemaSource.get_default()
    return Gio.Settings.new(schema_id) if source and source.lookup(schema_id, True) else None


def theme_installed(name):
    dirs = [os.path.expanduser("~/.themes"), os.path.join(GLib.get_user_data_dir(), "themes"),
            *[os.path.join(d, "themes") for d in GLib.get_system_data_dirs()]]
    return any(os.path.isdir(os.path.join(d, name, "gtk-3.0")) for d in dirs)


class ThemeManager:
    """Resolves Follow system / Light / Dark and applies it to the GTK window chrome."""

    def __init__(self, on_change):
        self.on_change = on_change
        self.gtk = Gtk.Settings.get_default()
        self.initial_theme = self.gtk.props.gtk_theme_name
        # Cinnamon (Mint) stores the theme in its own schema; fall back to GNOME's
        self.desktop = (settings_if_installed("org.cinnamon.desktop.interface")
                        or settings_if_installed("org.gnome.desktop.interface"))
        self.schemes = [s for s in (settings_if_installed("org.x.apps.portal"),
                                    settings_if_installed("org.gnome.desktop.interface")) if s]
        for s in [self.desktop, *self.schemes]:
            if s:
                s.connect("changed", lambda *_: self.on_change())
        self.choice = "system"

    def system_theme(self):
        if self.desktop and self.desktop.props.settings_schema.has_key("gtk-theme"):
            return self.desktop.get_string("gtk-theme")
        return self.initial_theme

    def system_is_dark(self):
        if "dark" in self.system_theme().lower():
            return True
        return any(s.props.settings_schema.has_key("color-scheme") and s.get_string("color-scheme") == "prefer-dark"
                   for s in self.schemes)

    def is_dark(self):
        return self.system_is_dark() if self.choice == "system" else self.choice == "dark"

    def apply(self):
        """Switch the app's own GTK theme to the light/dark variant of the system theme."""
        name = self.system_theme()
        self.gtk.reset_property("gtk-theme-name")
        self.gtk.reset_property("gtk-application-prefer-dark-theme")
        if self.choice == "system" or self.is_dark() == self.system_is_dark():
            return
        if self.choice == "light":
            candidates = [re.sub(r"-[Dd]ark", "", name)]
        else:
            candidates = [re.sub(r"^(Mint-[A-Z])(?=-|$)", r"\1-Dark", name), f"{name}-Dark", f"{name}-dark"]
        variant = next((c for c in candidates if c != name and theme_installed(c)), None)
        if variant:
            self.gtk.props.gtk_theme_name = variant
        else:
            self.gtk.props.gtk_application_prefer_dark_theme = self.choice == "dark"


class ViewerWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title=APP_NAME)
        self.set_default_size(1000, 900)
        self.path = None
        self.source = None
        self.monitor = None
        self.restore_scroll = None

        mode_action = Gio.SimpleAction.new_stateful(
            "view-mode", GLib.VariantType.new("s"), GLib.Variant.new_string(DEFAULT_VIEW_MODE))
        mode_action.connect("change-state", self.on_view_mode)
        self.add_action(mode_action)

        header = Gtk.HeaderBar(show_close_button=True, title=APP_NAME)
        self.set_titlebar(header)
        self.header = header

        open_btn = Gtk.Button.new_with_mnemonic("_Open")
        open_btn.set_tooltip_text("Open a Markdown file (Ctrl+O)")
        open_btn.connect("clicked", lambda *_: self.choose_file())
        header.pack_start(open_btn)

        self.reload_btn = self.icon_button("view-refresh-symbolic", "Reload (F5)", self.reload)
        header.pack_start(self.reload_btn)

        mode_box = Gtk.Box()
        mode_box.get_style_context().add_class("linked")
        for key, label, tooltip in VIEW_MODES:
            btn = Gtk.ToggleButton(label=label, tooltip_text=tooltip)
            btn.set_detailed_action_name(f"win.view-mode::{key}")
            mode_box.pack_start(btn, False, False, 0)
        header.pack_start(mode_box)

        self.print_btn = self.icon_button("document-print-symbolic", "Print / save as PDF (Ctrl+P)",
                                          self.print_document)
        header.pack_end(self.print_btn)

        theme_menu = Gio.Menu()
        for key, label in THEMES:
            theme_menu.append(label, f"app.theme::{key}")
        theme_btn = Gtk.MenuButton(menu_model=theme_menu, tooltip_text="Theme")
        theme_btn.add(Gtk.Image.new_from_icon_name("weather-clear-night-symbolic", Gtk.IconSize.BUTTON))
        header.pack_end(theme_btn)

        zoom_box = Gtk.Box()
        zoom_box.get_style_context().add_class("linked")
        zoom_box.pack_start(self.icon_button("zoom-out-symbolic", "Zoom out (Ctrl+-)",
                                             lambda: self.zoom(-ZOOM_STEP)), False, False, 0)
        self.zoom_label = Gtk.Button(label="100%")
        self.zoom_label.set_tooltip_text("Reset zoom (Ctrl+0)")
        self.zoom_label.connect("clicked", lambda *_: self.zoom(None))
        zoom_box.pack_start(self.zoom_label, False, False, 0)
        zoom_box.pack_start(self.icon_button("zoom-in-symbolic", "Zoom in (Ctrl++)",
                                             lambda: self.zoom(ZOOM_STEP)), False, False, 0)
        header.pack_end(zoom_box)

        settings = WebKit2.Settings()
        settings.set_enable_javascript_markup(False)  # never run scripts from documents
        settings.set_allow_file_access_from_file_urls(True)
        self.webview = WebKit2.WebView.new_with_settings(settings)
        self.webview.connect("decide-policy", self.on_decide_policy)
        self.webview.connect("load-changed", self.on_load_changed)
        self.webview.connect("context-menu", self.on_context_menu)

        self.status = Gtk.Label(xalign=0)
        self.status.set_margin_start(10)
        self.status.set_margin_end(10)
        self.status.set_margin_top(3)
        self.status.set_margin_bottom(3)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(self.webview, True, True, 0)
        box.pack_start(Gtk.Separator(), False, False, 0)
        box.pack_start(self.status, False, False, 0)
        self.add(box)

        self.connect("key-press-event", self.on_key)
        self.render()

    def icon_button(self, icon, tooltip, callback):
        btn = Gtk.Button.new_from_icon_name(icon, Gtk.IconSize.BUTTON)
        btn.set_tooltip_text(tooltip)
        btn.connect("clicked", lambda *_: callback())
        return btn

    @property
    def view_mode(self):
        return self.lookup_action("view-mode").get_state().get_string()

    # ---- loading and rendering ------------------------------------------

    def open_file(self, path):
        path = os.path.abspath(path)
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                self.source = f.read()
        except OSError as e:
            self.error(f"Could not open {path}", str(e))
            return

        if path != self.path:
            self.restore_scroll = None
            self.watch(path)
        self.path = path
        title = os.path.basename(path)
        self.header.set_title(title)
        self.header.set_subtitle(os.path.dirname(path))
        self.set_title(f"{title} – {APP_NAME}")
        self.render()

    def render(self):
        """(Re)draw the page for the current file, view mode and theme."""
        mode = self.view_mode
        dark = self.get_application().themes.is_dark()
        rgba = Gdk.RGBA()
        rgba.parse(BACKGROUNDS[(mode, dark)])
        self.webview.set_background_color(rgba)

        if self.path is None:
            body, base, title = PLACEHOLDER, "file:///", APP_NAME
        else:
            body = render_source(self.source) if mode == "source" else render_markdown(self.source)
            base = Gio.File.new_for_path(self.path).get_uri()
            title = os.path.basename(self.path)
        page = PAGE_TEMPLATE.format(theme="dark" if dark else "light", title=html.escape(title),
                                    css=build_css(mode), body=body)
        self.webview.load_html(page, base)

        if self.path is None:
            self.status.set_text("Ready")
        else:
            words = word_count(render_markdown(self.source) if mode == "source" else body)
            lines = self.source.count("\n") + 1
            self.status.set_text(f"{words:,} words    {lines:,} lines    {self.path}")
        for w in (self.reload_btn, self.print_btn):
            w.set_sensitive(self.path is not None)

    def rerender(self, from_disk=False):
        """Redraw while keeping the reading position (as a fraction, since layouts differ)."""
        js = "window.scrollY / Math.max(1, document.documentElement.scrollHeight - window.innerHeight)"
        self.webview.evaluate_javascript(js, -1, None, None, None, self.on_scroll_read, from_disk)

    def on_scroll_read(self, webview, result, from_disk):
        try:
            self.restore_scroll = webview.evaluate_javascript_finish(result).to_double()
        except GLib.Error:
            self.restore_scroll = None
        if from_disk and self.path:
            self.open_file(self.path)
        else:
            self.render()

    def reload(self):
        if self.path:
            self.rerender(from_disk=True)

    def on_load_changed(self, webview, event):
        if event == WebKit2.LoadEvent.FINISHED and self.restore_scroll:
            js = ("window.scrollTo(0, %f * (document.documentElement.scrollHeight - window.innerHeight))"
                  % self.restore_scroll)
            webview.evaluate_javascript(js, -1, None, None, None, None, None)
            self.restore_scroll = None

    def on_view_mode(self, action, value):
        action.set_state(value)
        self.rerender()

    def watch(self, path):
        """Reload automatically whenever the file is saved by an editor."""
        if self.monitor:
            self.monitor.cancel()
        self.monitor = Gio.File.new_for_path(path).monitor_file(Gio.FileMonitorFlags.NONE, None)
        self.monitor.connect("changed", self.on_file_changed)

    def on_file_changed(self, _monitor, _file, _other, event):
        if event in (Gio.FileMonitorEvent.CHANGES_DONE_HINT, Gio.FileMonitorEvent.CREATED):
            self.reload()

    # ---- links and drops --------------------------------------------------

    def on_decide_policy(self, _webview, decision, decision_type):
        if decision_type != WebKit2.PolicyDecisionType.NAVIGATION_ACTION:
            return False
        uri = decision.get_navigation_action().get_request().get_uri()
        parsed = urlparse(uri)
        current = Gio.File.new_for_path(self.path).get_uri() if self.path else "file:///"
        if uri.split("#")[0] in (current, "file:///", "about:blank"):
            return False  # initial load or a jump to an anchor in this document

        decision.ignore()
        if parsed.scheme == "file" and parsed.path.lower().endswith(MD_SUFFIXES):
            self.open_file(unquote(parsed.path))  # linked or dropped Markdown file
        else:
            Gtk.show_uri_on_window(self, uri, Gdk.CURRENT_TIME)
        return True

    def on_context_menu(self, _webview, menu, _event, _hit):
        # Drop browser-only entries (Back, Forward, Stop, Reload, Inspect) from the right-click menu
        browser_only = {WebKit2.ContextMenuAction.GO_BACK, WebKit2.ContextMenuAction.GO_FORWARD,
                        WebKit2.ContextMenuAction.STOP, WebKit2.ContextMenuAction.RELOAD,
                        WebKit2.ContextMenuAction.INSPECT_ELEMENT}
        for item in list(menu.get_items()):
            if item.get_stock_action() in browser_only:
                menu.remove(item)
        return False

    # ---- actions --------------------------------------------------------

    def choose_file(self):
        dialog = Gtk.FileChooserNative.new("Open Markdown file", self, Gtk.FileChooserAction.OPEN,
                                           "_Open", "_Cancel")
        md_filter = Gtk.FileFilter()
        md_filter.set_name("Markdown files")
        for suffix in MD_SUFFIXES:
            md_filter.add_pattern(f"*{suffix}")
            md_filter.add_pattern(f"*{suffix.upper()}")
        dialog.add_filter(md_filter)
        any_filter = Gtk.FileFilter()
        any_filter.set_name("All files")
        any_filter.add_pattern("*")
        dialog.add_filter(any_filter)
        if self.path:
            dialog.set_current_folder(os.path.dirname(self.path))
        if dialog.run() == Gtk.ResponseType.ACCEPT:
            self.open_file(dialog.get_filename())
        dialog.destroy()

    def print_document(self):
        if self.path:
            WebKit2.PrintOperation.new(self.webview).run_dialog(self)

    def zoom(self, step):
        level = 1.0 if step is None else min(max(self.webview.get_zoom_level() + step, 0.3), 3.0)
        self.webview.set_zoom_level(level)
        self.zoom_label.set_label(f"{round(level * 100)}%")

    def on_key(self, _widget, event):
        ctrl = event.state & Gdk.ModifierType.CONTROL_MASK
        key = Gdk.keyval_name(event.keyval)
        if ctrl and key == "o":
            self.choose_file()
        elif ctrl and key == "p":
            self.print_document()
        elif (ctrl and key == "r") or key == "F5":
            self.reload()
        elif ctrl and key in ("plus", "equal", "KP_Add"):
            self.zoom(ZOOM_STEP)
        elif ctrl and key in ("minus", "KP_Subtract"):
            self.zoom(-ZOOM_STEP)
        elif ctrl and key in ("0", "KP_0"):
            self.zoom(None)
        elif ctrl and key in ("1", "2", "3", "KP_1", "KP_2", "KP_3"):
            mode = VIEW_MODES[int(key[-1]) - 1][0]
            self.lookup_action("view-mode").change_state(GLib.Variant.new_string(mode))
        elif ctrl and key in ("w", "q"):
            self.close()
        else:
            return False
        return True

    def error(self, title, detail):
        dialog = Gtk.MessageDialog(transient_for=self, message_type=Gtk.MessageType.ERROR,
                                   buttons=Gtk.ButtonsType.CLOSE, text=title)
        dialog.format_secondary_text(detail)
        dialog.run()
        dialog.destroy()


class ViewerApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="local.MarkdownViewer",
                         flags=Gio.ApplicationFlags.HANDLES_OPEN | Gio.ApplicationFlags.NON_UNIQUE)
        self.config = GLib.KeyFile()
        try:
            self.config.load_from_file(CONFIG_FILE, GLib.KeyFileFlags.NONE)
        except GLib.Error:
            pass
        self.themes = None

    def read_setting(self, key, allowed, default):
        try:
            value = self.config.get_string("viewer", key)
        except GLib.Error:
            return default
        return value if value in allowed else default

    def write_setting(self, key, value):
        self.config.set_string("viewer", key, value)
        try:
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            self.config.save_to_file(CONFIG_FILE)
        except (GLib.Error, OSError):
            pass  # preferences are a convenience; never fail because of them

    def do_startup(self):
        Gtk.Application.do_startup(self)
        self.themes = ThemeManager(self.on_theme_changed)
        self.themes.choice = self.read_setting("theme", [t[0] for t in THEMES], "system")
        self.themes.apply()
        action = Gio.SimpleAction.new_stateful(
            "theme", GLib.VariantType.new("s"), GLib.Variant.new_string(self.themes.choice))
        action.connect("change-state", self.on_theme_action)
        self.add_action(action)

    def on_theme_action(self, action, value):
        action.set_state(value)
        self.themes.choice = value.get_string()
        self.write_setting("theme", self.themes.choice)
        self.on_theme_changed()

    def on_theme_changed(self):
        self.themes.apply()
        for win in self.get_windows():
            if isinstance(win, ViewerWindow):
                win.rerender()


    def do_activate(self):
        ViewerWindow(self).show_all()

    def do_open(self, files, _n_files, _hint):
        for f in files:
            win = ViewerWindow(self)
            win.show_all()
            win.open_file(f.get_path())


if __name__ == "__main__":
    sys.exit(ViewerApp().run(sys.argv))
