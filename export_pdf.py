#!/usr/bin/env python3
"""
export_pdf.py — Esporta workbook.md e note_docente.md in PDF A4.
                I blocchi Mermaid vengono renderizzati via mermaid.js in Chrome.
Uso:  python export_pdf.py [MOD-XX] [--force] [--css-only]
Deps: pip install pymdown-extensions
"""

import argparse, os, re, shutil, subprocess, sys, urllib.request
from pathlib import Path
import markdown

# ─── Configurazione ──────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
EXPORT_DIR  = BASE_DIR / "EXPORT"
PDF_DIR     = EXPORT_DIR / "PDF"
TMP_DIR     = EXPORT_DIR / "tmp"
JS_DIR      = EXPORT_DIR / "js"
CSS_PATH    = EXPORT_DIR / "style.css"
MERMAID_JS  = JS_DIR / "mermaid.min.js"
MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    str(Path.home() / "AppData/Local/Google/Chrome/Application/chrome.exe"),
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

WORKBOOK_MODS = [
    "MOD-01","MOD-02","MOD-03","MOD-04","MOD-05","MOD-06",
    "MOD-07","MOD-08","MOD-09","MOD-10","MOD-11","MOD-12",
    "MOD-13","MOD-14","MOD-15","MOD-16","MOD-17","MOD-18",
    "MOD-19","MOD-26","MOD-27","MOD-28","MOD-29","MOD-30","MOD-31",
]
NOTE_MODS = ["MOD-20","MOD-21","MOD-22","MOD-23","MOD-24","MOD-25","MOD-35"]

TARGET_FILES = (
    [(m, "workbook",     BASE_DIR / m / "workbook.md")     for m in WORKBOOK_MODS] +
    [(m, "note_docente", BASE_DIR / m / "note_docente.md") for m in NOTE_MODS]
)

# Estrae blocchi ```mermaid … ```
MERMAID_RE = re.compile(r'```mermaid\n(.*?)```', re.DOTALL)


# ─── CSS design system ───────────────────────────────────────────────────────
CSS_CONTENT = """\
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

:root {
  --arancio: #EF6A01;
  --avorio:  #EDEBDC;
  --giallo:  #FFB600;
  --nero:    #000000;
  --bianco:  #FFFFFF;
  --dark:    #1A1A1A;
}

@page {
  size: A4;
  margin: 2cm 2.2cm 2.4cm 2.2cm;
}

/* ── Corpo ─────────────────────────────────────────── */
body {
  font-family: 'Montserrat', 'Segoe UI', Arial, sans-serif;
  font-size: 10.5pt;
  color: var(--nero);
  background: var(--bianco);
  line-height: 1.65;
  max-width: 100%;
}

/* ── Titoli ─────────────────────────────────────────── */
h1 {
  font-size: 20pt;
  font-weight: 700;
  color: var(--arancio);
  border-bottom: 3px solid var(--arancio);
  padding-bottom: 6pt;
  margin-top: 0;
  page-break-after: avoid;
}
h2 {
  font-size: 14pt;
  font-weight: 700;
  color: var(--nero);
  border-left: 4px solid var(--arancio);
  padding-left: 10pt;
  margin-top: 24pt;
  page-break-after: avoid;
}
h3 {
  font-size: 11.5pt;
  font-weight: 600;
  color: var(--arancio);
  margin-top: 16pt;
  page-break-after: avoid;
}
h4 {
  font-size: 10.5pt;
  font-weight: 700;
  color: var(--nero);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  page-break-after: avoid;
}

/* ── Paragrafo e lista ──────────────────────────────── */
p  { margin: 6pt 0; }
ul { margin: 4pt 0; padding-left: 20pt; }
ol { margin: 4pt 0; padding-left: 22pt; }
li { margin-bottom: 3pt; }

/* ── Blockquote → callout avorio ───────────────────── */
blockquote {
  background: var(--avorio);
  border-left: 4px solid var(--arancio);
  margin: 10pt 0;
  padding: 8pt 12pt;
  border-radius: 2px;
}
blockquote p { margin: 0; }

/* ── Code inline ────────────────────────────────────── */
code {
  font-family: 'Courier New', Consolas, monospace;
  font-size: 9pt;
  background: #F0EEE5;
  padding: 1px 4px;
  border-radius: 2px;
}

/* ── Code block (codehilite) ────────────────────────── */
.codehilite {
  background: var(--dark);
  border-left: 3px solid var(--arancio);
  border-radius: 3px;
  padding: 10pt 12pt;
  margin: 8pt 0;
  overflow-x: auto;
  page-break-inside: avoid;
}
.codehilite code, .codehilite pre {
  background: transparent;
  color: var(--avorio);
  font-size: 9pt;
  padding: 0;
  border-radius: 0;
  white-space: pre-wrap;
  word-break: break-all;
}
pre {
  background: var(--dark);
  color: var(--avorio);
  font-size: 9pt;
  padding: 10pt 12pt;
  border-left: 3px solid var(--arancio);
  border-radius: 3px;
  white-space: pre-wrap;
  word-break: break-all;
  page-break-inside: avoid;
  margin: 8pt 0;
}
pre code { background: transparent; color: inherit; padding: 0; font-size: inherit; }

/* ── Tabelle ─────────────────────────────────────────── */
table {
  width: 100%;
  border-collapse: collapse;
  margin: 10pt 0;
  font-size: 9.5pt;
  page-break-inside: avoid;
}
th {
  background: var(--nero);
  color: var(--bianco);
  padding: 6pt 8pt;
  font-weight: 700;
  text-align: left;
}
td {
  border: 1px solid #C8C5B8;
  padding: 5pt 8pt;
  vertical-align: top;
}
tr:nth-child(even) td { background: var(--avorio); }

/* ── Separatori ──────────────────────────────────────── */
hr {
  border: none;
  border-top: 1px solid #C8C5B8;
  margin: 16pt 0;
}

/* ── Mermaid ─────────────────────────────────────────── */
.mermaid {
  display: block;
  text-align: center;
  margin: 12pt auto;
  page-break-inside: avoid;
  max-width: 100%;
}
.mermaid svg {
  max-width: 100%;
  height: auto;
}

/* ── Immagini ────────────────────────────────────────── */
img {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 10pt auto;
  page-break-inside: avoid;
}

/* ── Task list (pymdownx) ───────────────────────────── */
.task-list-item { list-style: none; }
.task-list-item input { margin-right: 6px; }

/* ── Copyright footer ────────────────────────────────── */
blockquote:last-of-type {
  font-size: 8.5pt;
  color: #666;
}

/* ── Print ───────────────────────────────────────────── */
@media print {
  body { font-size: 10pt; }
  h1 { color: var(--arancio) !important; }
  h2 { border-left-color: var(--arancio) !important; }
  h3 { color: var(--arancio) !important; }
  pre, .codehilite { background: var(--dark) !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  th  { background: var(--nero) !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  tr:nth-child(even) td { background: var(--avorio) !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  blockquote { background: var(--avorio) !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
"""


# ─── Funzioni core ───────────────────────────────────────────────────────────

def find_chrome():
    for p in CHROME_PATHS:
        if Path(p).exists():
            return Path(p)
    for name in ("chrome", "google-chrome", "msedge"):
        found = shutil.which(name)
        if found:
            return Path(found)
    return None


def check_dependencies(chrome_exe):
    ok = True
    if chrome_exe is None:
        print("[ERROR] Chrome/Edge non trovato. Percorsi cercati:")
        for p in CHROME_PATHS:
            print(f"         {p}")
        ok = False
    try:
        import pymdownx  # noqa: F401
    except ImportError:
        print("[ERROR] pymdownx mancante → pip install pymdown-extensions")
        ok = False
    if not ok:
        sys.exit(1)


def ensure_dirs():
    for d in (PDF_DIR, TMP_DIR, JS_DIR):
        d.mkdir(parents=True, exist_ok=True)


def ensure_mermaid_js():
    if not MERMAID_JS.exists():
        print("[INFO] Download mermaid.min.js da CDN jsDelivr...")
        try:
            req = urllib.request.Request(MERMAID_CDN, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                MERMAID_JS.write_bytes(resp.read())
            print(f"[INFO] Salvato: {MERMAID_JS}  ({MERMAID_JS.stat().st_size // 1024} KB)")
        except Exception as exc:
            print(f"[WARN] Download fallito: {exc}")
            print("[WARN] I diagrammi Mermaid verranno mostrati come testo grezzo.")


def mermaid_block_to_div(code):
    """Trasforma codice Mermaid in <div class='mermaid'> sicuro per HTML."""
    safe = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'<div class="mermaid">\n{safe}\n</div>\n'


def md_to_html_body(content):
    """Markdown → HTML body. I blocchi mermaid diventano <div class=mermaid>."""
    # Estrae e sostituisce blocchi mermaid PRIMA del parsing Markdown
    processed = MERMAID_RE.sub(lambda m: mermaid_block_to_div(m.group(1)), content)

    md = markdown.Markdown(extensions=[
        "tables",
        "fenced_code",
        "attr_list",
        "codehilite",
        "pymdownx.tasklist",
        "pymdownx.smartsymbols",
    ], extension_configs={
        "codehilite": {"noclasses": True, "pygments_style": "monokai"},
        "pymdownx.tasklist": {"custom_checkbox": True},
    })
    return md.convert(processed)


def build_full_html(body_html, mod_id, title):
    """Assembla documento HTML completo con CSS e mermaid.js."""
    css_uri  = CSS_PATH.as_uri()
    merm_uri = MERMAID_JS.as_uri() if MERMAID_JS.exists() else ""

    mermaid_tags = ""
    if merm_uri:
        mermaid_tags = f"""\
<script src="{merm_uri}"></script>
<script>
mermaid.initialize({{
  startOnLoad: true,
  theme: "neutral",
  flowchart: {{ useMaxWidth: true, htmlLabels: true }},
  themeVariables: {{
    primaryColor: "#EDEBDC",
    primaryBorderColor: "#EF6A01",
    lineColor: "#000000",
    fontFamily: "Montserrat, Segoe UI, sans-serif",
    fontSize: "13px"
  }}
}});
</script>"""

    return f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<title>{title}</title>
<link rel="stylesheet" href="{css_uri}">
</head>
<body>
{body_html}
{mermaid_tags}
</body>
</html>"""


def html_to_pdf(html_path, pdf_path, chrome_exe, timeout=90):
    """Converte HTML → PDF A4 via Chrome headless. Tenta due strategie."""
    base_cmd = [
        str(chrome_exe),
        "--headless",
        f"--print-to-pdf={pdf_path}",
        "--print-to-pdf-no-header",   # Chrome < 112
        "--no-pdf-header-footer",     # Chrome >= 112
        "--no-sandbox",
        "--disable-gpu",
        "--disable-extensions",
        "--run-all-compositor-stages-before-draw",
        html_path.as_uri(),
    ]
    # Prima strategia: virtual time budget per dare tempo a Mermaid di renderizzarsi
    cmd_with_vt = base_cmd[:-1] + ["--virtual-time-budget=5000", base_cmd[-1]]
    try:
        subprocess.run(cmd_with_vt, capture_output=True, timeout=timeout)
        if pdf_path.exists() and pdf_path.stat().st_size > 1000:
            return True
    except subprocess.TimeoutExpired:
        pass

    # Seconda strategia: senza virtual time budget (compatibilità)
    try:
        subprocess.run(base_cmd, capture_output=True, timeout=timeout)
        return pdf_path.exists() and pdf_path.stat().st_size > 1000
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Timeout: {pdf_path.name}")
        return False


def write_css():
    CSS_PATH.write_text(CSS_CONTENT, encoding="utf-8")
    print(f"[CSS ] {CSS_PATH}")


# ─── Esportazione modulo ─────────────────────────────────────────────────────

def export_module(mod_id, file_type, md_path, chrome_exe, args):
    if not md_path.exists():
        print(f"[SKIP] Non trovato: {md_path.relative_to(BASE_DIR)}")
        return False

    pdf_name = f"{mod_id}_{file_type}.pdf"
    pdf_path = PDF_DIR / pdf_name

    if pdf_path.exists() and not args.force:
        size_kb = pdf_path.stat().st_size // 1024
        print(f"[SKIP] {pdf_name}  ({size_kb} KB, già presente — usa --force)")
        return True

    print(f"[....] {mod_id} {file_type} -> {pdf_name}")

    content = md_path.read_text(encoding="utf-8")

    # Titolo dal primo H1
    m = re.match(r"^#\s+(.+)$", content, re.MULTILINE)
    title = m.group(1).strip() if m else f"{mod_id} — {file_type}"

    body_html = md_to_html_body(content)
    full_html  = build_full_html(body_html, mod_id, title)

    html_path = TMP_DIR / f"{mod_id}_{file_type}.html"
    html_path.write_text(full_html, encoding="utf-8")

    ok = html_to_pdf(html_path, pdf_path, chrome_exe)

    html_path.unlink(missing_ok=True)

    if ok:
        size_kb = pdf_path.stat().st_size // 1024
        print(f"[OK  ] {pdf_name}  ({size_kb} KB)")
    else:
        print(f"[FAIL] {pdf_name}")
    return ok


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Esporta workbook e note_docente CCNP ENCOR in PDF A4.")
    parser.add_argument("module", nargs="?", metavar="MOD-XX",
                        help="Esporta solo questo modulo (es. MOD-01)")
    parser.add_argument("--force", action="store_true",
                        help="Rigenera anche se il PDF esiste già")
    parser.add_argument("--css-only", action="store_true",
                        help="Rigenera solo style.css, senza esportare PDF")
    args = parser.parse_args()

    if args.css_only:
        ensure_dirs()
        write_css()
        return

    chrome_exe = find_chrome()
    check_dependencies(chrome_exe)
    ensure_dirs()
    write_css()
    ensure_mermaid_js()

    targets = TARGET_FILES
    if args.module:
        mod = args.module.upper()
        targets = [(m, ft, p) for m, ft, p in TARGET_FILES if m == mod]
        if not targets:
            valid = ", ".join(m for m, _, _ in TARGET_FILES)
            print(f"[ERROR] Modulo '{mod}' non riconosciuto.\n        Validi: {valid}")
            sys.exit(1)

    ok_count  = 0
    skip_count = 0
    fail_list  = []

    for mod_id, file_type, md_path in targets:
        result = export_module(mod_id, file_type, md_path, chrome_exe, args)
        pdf_path = PDF_DIR / f"{mod_id}_{file_type}.pdf"
        if not md_path.exists():
            skip_count += 1
        elif result:
            ok_count += 1
        else:
            fail_list.append(f"{mod_id}/{file_type}")

    total = len(targets)
    print("\n" + "=" * 60)
    print(f" Export completato: {ok_count}/{total} PDF generati")
    if skip_count:
        print(f" File non trovati:  {skip_count}")
    if fail_list:
        print(f" Errori ({len(fail_list)}): {', '.join(fail_list)}")
    print(f" Output: {PDF_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
