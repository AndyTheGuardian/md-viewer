# Projektplan Website-Relaunch

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
    """Baut die Website für das angegebene Ziel."""
    for page in pages:
        render(page, minify=True)
    return f"Fertig: {len(pages)} Seiten"
```
