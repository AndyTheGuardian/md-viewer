# Markdown Viewer

A native Linux Mint viewer that opens `.md` files and displays them formatted like a Word document.

## Original requirements

- A Markdown file viewer for Linux Mint.
- Accepts `.md` files.
- Displays them formatted like a Word document.
- *(Added 2026-10-27)* Two more view modes:
  - "Source": normal, unformatted Markdown.
  - "VS Code": formatted the way VS Code's Markdown preview does it.
- *(Added 2026-10-27)* A theme switch with three choices: Follow system, Dark, Light.
- *(Added 2026-10-31)* Editing in the code (Source) view, switched on with a button. Built with GtkSourceView, on the git branch `feature/source-editor`.
- *(Added 2026-10-31)* Creating a new .md file.

## Files

| Path | Purpose |
|---|---|
| `~/Claude/md-viewer/md_viewer.py` | The whole app (single file, executable) |
| `~/Claude/md-viewer/PROJECT.md` | This file: project notes, kept up to date |
| `~/Claude/md-viewer/OFFENE-PUNKTE.md` | Open questions, assumptions and known limitations (German, with IDs) |
| `~/.config/md-viewer/settings.ini` | Saved preferences: `[viewer] theme=system\|light\|dark`. Created on the first change. The view mode is not saved. |
| `~/.local/share/applications/markdown-viewer.desktop` | Menu launcher ("Markdown Viewer", Office category). It registers `text/markdown` and `text/x-markdown`, so the app shows up under "Open With" for .md files. No other app had claimed .md files, so `xdg-mime query default text/markdown` now returns this launcher, which means double-clicking an .md file opens it in the viewer. |

Run: `python3 ~/Claude/md-viewer/md_viewer.py [file.md ...]`

## Tech stack

- Python 3 + GTK 3 (PyGObject) for the window, header bar and file dialog.
- WebKit2GTK 4.1 to display the rendered page.
- GtkSourceView 4 (`GtkSource` 4, preinstalled with xed) for the editor in Source view.
- `markdown-it-py` 3.0 (the `python3-markdown-it` package, preinstalled) as a CommonMark parser, with the `table` and `strikethrough` rules enabled and inline HTML allowed.
- Tested on Linux Mint 22.3, which runs as a VM here without 3D acceleration.

## Design and behaviour

**View modes**

The header bar has a linked toggle with three modes, in this order (changed on user request): **Source | VS Code | Document**. Ctrl+1, Ctrl+2 and Ctrl+3 also switch between them, in the same order. Default: Source.

**Code-block syntax highlighting in all views**
- Document and VS Code views: markdown-it's `highlight` option calls `highlight_code()`.
  - It runs Pygments `get_lexer_by_name(lang)` with `HtmlFormatter(nowrap=True)`, and markdown-it wraps the result in `<pre><code>`.
  - Fenced blocks without a language tag, or with an unknown one, stay plain.
- Source view: the `MarkdownLexer` delegates fenced blocks to the matching language lexer.
- `HIGHLIGHT_CSS` holds the token colours (VS Code Light+ / Dark+, `--hl-*` variables) and is prepended to every mode's CSS by `build_css()`.
  - `SOURCE_CSS` comes later and overrides the classes that mean Markdown syntax in Source view (`gh`, `gu`, `sb`, `nt`, `na`, `gd`, …).
  - `build_css()` collects *all* `:root` blocks into the print override, so printouts use light code colours too.
- How it works:
  - It is a stateful window action, `win.view-mode`.
  - Each window has its own mode. Every window opens in **Source** (`DEFAULT_VIEW_MODE`), changed on user request. The last-used mode is deliberately *not* remembered any more.
  - Switching re-renders the page and keeps the reading position as a *fraction* of the page height, because the layouts have different lengths.
- **Document** (`DOCUMENT_CSS`): the Word look described below.
- **VS Code** (`VSCODE_CSS`): modelled on VS Code's built-in Markdown preview with the Light/Dark Modern themes.
  - Full window width with 26 px side padding.
  - Fonts: Segoe UI, falling back to Ubuntu; 14 px with 22 px line height.
  - Headings are 600 weight. H1 and H2 have bottom borders.
  - Code blocks have rounded, shaded backgrounds.
  - Block quotes have a 5 px left bar.
  - Tables have only horizontal rules.
  - Colours:

    | Theme | Background | Text | Links |
    |---|---|---|---|
    | Light | `#fff` | `#3b3b3b` | `#005fb8` |
    | Dark | `#1f1f1f` | `#ccc` | `#4daafc` |

- **Source** (`SOURCE_CSS`, `render_source()`): the raw Markdown text, HTML-escaped, with syntax highlighting.
  - Highlighting uses the Pygments `MarkdownLexer` (`python3-pygments` 2.17, preinstalled). It is created with `stripnl=False, ensurenl=False` so line numbers match the file.
  - Tokens are split at newlines so each line stays its own div. Each piece is a `<span>` with Pygments' short class (`token_class()`, e.g. `gh`, `k`, `s2`).
  - The lexer reports list bullets and `> ` as `Keyword`, and quote text as `Emph`. `render_source()` relabels them as `k marker` (matched by `MARKER_RE`) and `ge quote`, so keywords inside code blocks aren't coloured as list markers.
  - Code inside fenced blocks with a language tag (` ```python `) is highlighted in that language, because the lexer delegates to it.
  - Colours follow VS Code Light+ / Dark+:

    | Element | Light | Dark |
    |---|---|---|
    | Headings (bold) | `#800000` | `#569cd6` |
    | List markers | `#0451a5` | `#6796e6` |
    | Quotes (italic) | `#0451a5` | `#6a9955` |
    | Inline code and fences | `#800000` | `#ce9178` |
    | Link text | `#a31515` | `#ce9178` |
    | URLs | `#0070c1` | `#3794ff` |

    - `**bold**` and `*italic*` are drawn bold or italic, and `~~strike~~` is struck through.
    - Code inside fences uses the usual VS Code colours for keywords, functions, types, variables, strings, numbers and comments.
  - Not highlighted, because the lexer doesn't recognise them: tables and `---` rules.
  - If Pygments is missing, Source view falls back to plain text.
  - Each source line is a `<div class="line">`.
  - Line numbers are drawn in a gutter by a CSS counter, so they are not copied along with selected text.
  - Long lines wrap.
  - Colours and font match the VS Code editor (Droid Sans Mono / DejaVu Sans Mono, 14 px).
- The status bar shows the word count (always of the rendered text), the line count and the path.

**Editing in Source view**
- The pencil toggle button in the header bar (or Ctrl+E) switches the Source view into an editor.
  - It is a stateful boolean window action, `win.edit`. It is only enabled in Source view with a file open, and not for files that aren't valid UTF-8, because saving would lose their bytes.
  - The read-only WebView and the editor (`SourceEditor`, a `GtkSource.View` in a `Gtk.ScrolledWindow`) share a `Gtk.Stack`.
  - The editor has line numbers, Markdown highlighting from GtkSourceView's own `markdown.lang`, undo/redo (Ctrl+Z / Ctrl+Shift+Z), auto-indent and word wrap. It uses the same monospace font as the Source view.
  - Colour schemes: `classic` for light, `oblivion` for dark (`EDITOR_SCHEMES`). They differ from the VS Code colours of the read-only view, because GtkSourceView ships no VS Code scheme.
  - The editor follows the zoom level by scaling its font with a CSS provider.
  - Entering and leaving the editor keeps the reading position (approximately, as a fraction of the lines).
- Saving: the **Save** button (only shown while editing) or Ctrl+S.
  - Files are written as UTF-8 and keep their original line ends (`read_markdown()` / `encode_markdown()` detect and restore CRLF).
  - Unsaved changes show as `*` in front of the title.
- Unsaved changes: leaving the editor, switching the view, opening another file or closing the window asks "Save / Discard / Cancel" (`confirm_unsaved()`).
- While editing, Reload and Print are disabled, and the automatic reload on file changes is suppressed, so it can't overwrite the text being edited.

**New file**
- The **New** button (or Ctrl+N) first asks where to save, using a save dialog that suggests `Untitled.md` and starts in the current file's folder.
- It then creates the empty file and opens it in a new window, in Source view and already in edit mode (`ViewerApp.open_window(path, edit=True)`).
  - A window that shows no file (the placeholder) is reused instead of opening a second one.
- If the name has no Markdown suffix, `.md` is added. If a file with that name already exists, nothing is overwritten and an error is shown, because the dialog only confirmed overwriting the name without `.md`.
- Choosing an existing name *with* the suffix asks the dialog's usual "Replace?" question; replacing empties that file.

**Theme (Follow system / Light / Dark)**
- The theme is chosen from the moon-icon menu button in the header bar.
  - It is a stateful app action, `app.theme`, shown as radio items.
  - The choice is app-wide (all windows) and saved in settings.ini.
- Page colours: each stylesheet defines CSS variables on `:root` (light) and `html.dark`, and `render()` sets `class="dark|light"` on `<html>`.
  - The WebView's background colour is set to match (`BACKGROUNDS`), so there's no white flash while a page loads.
  - Printing always uses the light palette: `build_css()` copies the `:root` variables into `@media print { html.dark {...} }`.
- Window chrome (`ThemeManager`) also switches. GTK 3 can't force a dark theme to light, so the app overrides its *own* `gtk-theme-name` with the light or dark variant of the system theme:
  - Light: `Mint-Y-Dark-Aqua` → `Mint-Y-Aqua`.
  - Dark: `Mint-Y-Aqua` → `Mint-Y-Dark-Aqua`, or `<name>-Dark`.
  - This is only done if the variant is installed. Otherwise it falls back to `gtk-application-prefer-dark-theme`.
  - "Follow system" resets both overrides.
- How the system theme is detected:
  - The theme name comes from `org.cinnamon.desktop.interface gtk-theme`, falling back to GNOME's.
  - The system counts as dark if that name contains "dark", or if `org.x.apps.portal` or `org.gnome.desktop.interface` `color-scheme` is `prefer-dark`.
  - Changes to these GSettings are watched live, so "Follow system" updates immediately.
- This machine currently uses `Mint-Y-Dark-Aqua` with `color-scheme=prefer-dark`, i.e. a dark system.

**Word-like page styling (`DOCUMENT_CSS`)**
- The page is a white A4 sheet (21 cm wide, at least 29.7 cm tall) with 2.54 cm margins and a drop shadow, centred on a grey `#e7e7e7` canvas, like Word's Print Layout.
- Body text: Calibri, 11 pt, line height 1.15, 8 pt spacing after paragraphs.
  - Font fallbacks: Carlito (metric-compatible with Calibri), then Liberation Sans. Carlito is *not* installed on this machine; it can be added with `sudo apt install fonts-crosextra-carlito`.
- Headings use Word's default styles: Calibri Light in blue `#2F5496`. Sizes are H1 16 pt, H2 13 pt, H3 12 pt in dark blue `#1F3763`, and H4 italic.
- Tables look like Word's "Table Grid": 1 px black borders, 5.4 pt cell padding, bold header row, and the column alignment from the Markdown is kept.
- Code uses Consolas, falling back to Liberation Mono, on a light grey shaded block.
- Block quotes are indented, italic and grey, like Word's Quote style.
- Links use Word's hyperlink blue `#0563C1`.
- Dark variant, similar to Word's dark mode:

  | Element | Colour |
  |---|---|
  | Canvas | `#1e1e1e` |
  | Page | `#2b2b2b` |
  | Text | `#e6e6e6` |
  | Headings | `#7fa7e3` |
  | Links | `#6cb4ff` |
  | Table grid | `#8c8c8c` |

- The page is one continuous sheet that grows with the content. There are no real on-screen page breaks.
- Printing switches to `@page A4` with 2.54 cm margins, so the output is properly paginated.

**Markdown features**
- CommonMark, including lists nested with 2-space indents.
- GitHub tables and `~~strikethrough~~`.
- Inline HTML is allowed, but document scripts never run (`enable_javascript_markup = False`).
- Headings get GitHub-style ids (`render_markdown()`), so `[link](#heading)` jumps within the document. Duplicate headings get `-1`, `-2` suffixes.
- Not supported: footnotes, task lists, auto-linking of bare URLs. These need the `mdit_py_plugins` / `linkify-it-py` packages, which are not installed. `MarkdownIt("gfm-like")` crashes without linkify.

**Window and controls**
- Header bar:
  - **New** and **Open** buttons.
  - Reload button.
  - View-mode toggle: Source, VS Code, Document.
  - Edit toggle (pencil) and, while editing, a Save button.
  - Zoom −, a percentage button that resets zoom, and zoom +.
  - Theme menu: Follow system, Light, Dark.
  - Print button, for printing or saving as PDF.
- Status bar: word count and the full path of the open file.
- Keyboard shortcuts:

  | Keys | Action |
  |---|---|
  | Ctrl+N | New file |
  | Ctrl+O | Open |
  | Ctrl+P | Print |
  | F5 or Ctrl+R | Reload |
  | Ctrl++ / Ctrl+− / Ctrl+0 | Zoom in / out / reset (30 % to 300 %) |
  | Ctrl+1 / Ctrl+2 / Ctrl+3 | Source / VS Code / Document view |
  | Ctrl+E | Start / stop editing (Source view) |
  | Ctrl+S | Save while editing |
  | Ctrl+W or Ctrl+Q | Close |

- Ways to open a file: the file dialog (filtered to .md, .markdown, .mdown and .mkd), the command line, "Open With", or dragging a file onto the window.
- When there is no file, a placeholder page is shown.
- The view reloads automatically when the file is saved, using `Gio.FileMonitor`, and keeps the scroll position.
- Link handling:
  - `#anchors` are followed inside the page.
  - Links to other local `.md` files open in the viewer.
  - Everything else (http, mailto, other files) opens in the default app.
- The browser-only entries (Back, Forward, Reload, Inspect) are removed from the right-click menu.
- Each file opens in its own window (`NON_UNIQUE` app).

**Known environment quirk**
- WebKit's GPU compositing showed a blank page on this VM.
- The script therefore sets `WEBKIT_DISABLE_COMPOSITING_MODE=1` and `WEBKIT_DISABLE_DMABUF_RENDERER=1` before importing WebKit.

## Verification done

- Rendered a sample document to a PNG and checked headings, the nested list, the table with alignment, the code block, the quote, strikethrough and the anchor link.
- Checked that heading ids are generated correctly, including for duplicate headings.
- Auto-reload: appending to the open file changed the word count from 65 to 70 without user action.
- Screenshots of all 6 combinations (3 view modes × light/dark) were checked. The window chrome switched to `Mint-Y-Aqua` for Light and `Mint-Y-Dark-Aqua` for Dark.
- Edit mode (2026-10-31), with a scripted GTK test (18 checks, all passed) and screenshots in light, dark and at 150 % zoom:
  - Edit is enabled only in Source view, and not for an invalid-UTF-8 file.
  - Save button visible and Reload/Print disabled while editing; `*` in the title when modified.
  - An external file change while editing does not touch the buffer.
  - Cancel on a view switch keeps the editor and the view toggle; Save writes the file and switches; Discard leaves the file unchanged; Cancel on close keeps the window open.
  - CRLF files are saved with CRLF.
- New file (2026-10-31), with a scripted GTK test (10 checks, all passed; the file dialog was stubbed):
  - The suggested name is `Untitled.md`; a name without a suffix gets `.md`.
  - The file is created empty; an empty window is reused, otherwise a second window opens, in Source view and editing.
  - An existing `notes.md` is not overwritten when `notes` is entered; Cancel creates nothing.
  - The edit-mode test still passes 18/18.
- Testing gotcha: don't redirect `XDG_CONFIG_HOME` in tests. dconf reads the user's GSettings from there, so the app then sees default (light) desktop settings. Patch `md_viewer.CONFIG_FILE` instead.

## Ideas / possible changes (not done)

- Real on-screen page breaks (multiple A4 sheets).
- Footnotes and task lists, via `mdit_py_plugins`.
- A sidebar with a table of contents built from the headings.

## Changelog

- **2026-10-27**
  - Initial version: viewer, launcher and tests.
  - Switched the parser from Python-Markdown to markdown-it, because Python-Markdown doesn't nest 2-space-indented lists.
  - Disabled WebKit GPU compositing to fix the blank page on the VM.
  - User request: an unformatted-Markdown view, a VS Code-style view and a theme switch. Added:
    - Document / VS Code / Source view modes (Ctrl+1–3).
    - The Follow system / Light / Dark theme menu, which switches both the page colours and the app's GTK theme variant.
    - Light and dark palettes for all modes.
    - Settings saved in `~/.config/md-viewer/settings.ini`.
    - A line count in the status bar.
  - User request: syntax highlighting in Source view. Added Pygments-based highlighting with VS Code Light+/Dark+ colours.
    - Verified that the line count matches the file, including leading and trailing blank lines.
    - Verified with screenshots in light and dark.
  - User request: syntax highlighting for code blocks in the other views too, and the view order changed to Source, VS Code, Document.
    - Added `highlight_code()` and the shared `HIGHLIGHT_CSS`.
    - Reordered the toggle; Ctrl+1–3 follow the new order.
    - Verified with screenshots of all 6 combinations using Python and JS blocks (JS identifiers use the `nx` class).
  - User request: make Source the default view.
    - Added `DEFAULT_VIEW_MODE = "source"`.
    - Removed view-mode persistence; it would have overridden the default, since `view_mode=vscode` was saved.
    - Deleted the stale `view_mode` line from the user's settings.ini.
    - Verified that new windows open in Source even after another window switches mode.
  - Moved the project from `~/md-viewer` to `~/Claude/md-viewer`.
    - Updated the menu launcher's `Exec` path.
    - The settings stay in `~/.config/md-viewer/`.
    - Replaced the deprecated `Gio.Settings.list_keys()` with `settings_schema.has_key()`.
    - Verified that the app still starts.
- **2026-10-31**
  - Put the project under git (`main` holds the state from 2026-10-27).
  - User request: editing in the code view, switched on by a button. Added on branch `feature/source-editor`:
    - The GtkSourceView editor in Source view, the edit toggle (Ctrl+E) and saving (Save button, Ctrl+S).
    - The Save / Discard / Cancel prompt for unsaved changes.
    - Reading files as bytes, so invalid UTF-8 and CRLF line ends are detected.
  - User request: creating a new .md file. Added the New button (Ctrl+N): it asks for the location first, then opens the empty file in a new window, ready to edit.
