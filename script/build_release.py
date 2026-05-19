#!/usr/bin/env python3
"""
build_release.py — Packaging release CCNP ENCOR 350-401.
Genera ENCOR_materiale_didattico_v1.0.zip in script/output/

Uso: python script/build_release.py
"""

import re, sys, zipfile
from datetime import date
from pathlib import Path

# ─── Configurazione ──────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent.parent
PDF_DIR     = BASE_DIR / "EXPORT" / "PDF"
OUTPUT_DIR  = Path(__file__).parent / "output"
VERSION     = "1.0"
ZIP_NAME    = f"ENCOR_materiale_didattico_v{VERSION}.zip"
ZIP_ROOT    = "ENCOR_materiale_didattico"

ALL_MODS = [f"MOD-{i:02d}" for i in range(1, 36)]


# ─── Parsing frontmatter YAML ────────────────────────────────────────────────

def parse_frontmatter(readme_path):
    """Estrae titolo e area dal frontmatter YAML di MOD-XX/README.md."""
    try:
        text = readme_path.read_text(encoding="utf-8-sig")  # gestisce BOM
    except FileNotFoundError:
        return {}, False

    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}, False

    fields = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            fields[key.strip()] = val.strip()
    return fields, True


def folder_name(mod_id, titolo):
    if titolo:
        return f"{mod_id} — {titolo}"
    return mod_id


# ─── Raccolta file per modulo ────────────────────────────────────────────────

def collect_module(mod_id):
    """Ritorna dict con tutti i file disponibili per il modulo."""
    mod_dir = BASE_DIR / mod_id
    fields, _ = parse_frontmatter(mod_dir / "README.md")
    titolo = fields.get("titolo", "")
    area   = fields.get("area", "")

    workbook  = PDF_DIR / f"{mod_id}_workbook.pdf"
    soluzione = PDF_DIR / f"{mod_id}_soluzione.pdf"
    slide     = mod_dir / f"{mod_id}_slide.pptx"
    cfg_dir   = mod_dir / "cfg"
    cfg_files = sorted(cfg_dir.glob("*-cfg")) if cfg_dir.is_dir() else []

    return {
        "mod_id":   mod_id,
        "titolo":   titolo,
        "area":     area,
        "folder":   folder_name(mod_id, titolo),
        "workbook":  workbook  if workbook.exists()  else None,
        "soluzione": soluzione if soluzione.exists() else None,
        "slide":     slide     if slide.exists()     else None,
        "cfg":       cfg_files,
    }


# ─── Generazione README.txt ──────────────────────────────────────────────────

def build_readme_txt(modules):
    sep = "═" * 43
    lines = [
        "CCNP ENCOR 350-401 — Materiale Didattico",
        f"Versione: {VERSION}",
        f"Data: {date.today().strftime('%d/%m/%Y')}",
        "",
        sep,
        "CONTENUTO DEL PACCHETTO",
        sep,
        "Questo archivio contiene il materiale didattico",
        "per il corso di certificazione Cisco CCNP ENCOR",
        "350-401. 35 moduli autonomi organizzati per",
        "area tematica.",
        "",
        sep,
        "COME USARE IL MATERIALE",
        sep,
        "Ogni modulo e' autonomo e contiene:",
        "· workbook.pdf  — guida operativa con teoria",
        "                  e task step-by-step",
        "· slide.pptx    — supporto teorico per il docente",
        "· cfg/          — configurazioni iniziali device",
        "                  (copia e incolla sul device)",
        "",
        "PIATTAFORME LAB SUPPORTATE",
        "GNS3 · ContainerLab (vrnetlab/IOU) · EVE-NG",
        "",
        sep,
        "INDICE MODULI",
        sep,
    ]

    for m in modules:
        wb_str  = "presente" if m["workbook"]  else "assente"
        sol_str = "presente" if m["soluzione"] else "assente"
        sl_str  = "presente" if m["slide"]     else "assente"
        cfg_n   = len(m["cfg"])
        cfg_str = f"{cfg_n} file presenti" if cfg_n else "assente"

        label = f"{m['mod_id']}"
        if m["titolo"]:
            label += f" · {m['titolo']}"
        if m["area"]:
            label += f" · {m['area']}"

        lines += [
            "",
            label,
            f"  Workbook  : {wb_str}",
            f"  Soluzione : {sol_str}",
            f"  Slide     : {sl_str}",
            f"  Cfg       : {cfg_str}",
        ]

    lines += [
        "",
        sep,
        "(C) 2026 Matteo Mirenda — Tutti i diritti riservati.",
        "Materiale ad uso esclusivo degli studenti",
        "iscritti al corso. Vietata la riproduzione",
        "o distribuzione senza autorizzazione scritta.",
        sep,
    ]

    return "\n".join(lines)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = OUTPUT_DIR / ZIP_NAME

    # Raccolta dati tutti i moduli
    all_modules = [collect_module(m) for m in ALL_MODS]

    # Classificazione
    complete, warnings, skipped = [], [], []
    included = []

    for m in all_modules:
        has_wb    = m["workbook"]  is not None
        has_sol   = m["soluzione"] is not None
        has_slide = m["slide"]     is not None
        has_cfg   = len(m["cfg"]) > 0
        has_any   = has_wb or has_slide or has_cfg

        if not has_any:
            skipped.append(m)
            continue

        included.append(m)
        missing = []
        if not has_wb:    missing.append("workbook.pdf")
        if not has_sol:   missing.append("soluzione.pdf")
        if not has_slide: missing.append("slide.pptx")
        if not has_cfg:   missing.append("cfg/")

        if missing:
            warnings.append((m["mod_id"], missing))
        else:
            complete.append(m["mod_id"])

    # Generazione ZIP
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:

        # README.txt in root
        readme_txt = build_readme_txt(included)
        zf.writestr(f"{ZIP_ROOT}/README.txt", readme_txt.encode("utf-8"))

        for m in included:
            folder = f"{ZIP_ROOT}/{m['folder']}"

            if m["workbook"]:
                zf.write(m["workbook"],  f"{folder}/workbook.pdf")
            if m["soluzione"]:
                zf.write(m["soluzione"], f"{folder}/soluzione.pdf")
            if m["slide"]:
                zf.write(m["slide"], f"{folder}/{m['mod_id']}_slide.pptx")
            for cfg in m["cfg"]:
                zf.write(cfg, f"{folder}/cfg/{cfg.name}")

    zip_mb = zip_path.stat().st_size / 1024 / 1024

    # ─── Report ──────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  ENCOR Release v{VERSION} — Build Report")
    print(f"{'='*60}")
    print(f"  [OK ] Moduli completi (wb+sol+slide+cfg): {len(complete)}")
    if complete:
        print(f"        {', '.join(complete)}")

    if warnings:
        print(f"\n  [WARN] Moduli con file mancanti: {len(warnings)}")
        for mod_id, missing in warnings:
            print(f"        {mod_id}: mancano {', '.join(missing)}")

    if skipped:
        print(f"\n  [INFO] Moduli skippati (nessun file): {len(skipped)}")
        for m in skipped:
            print(f"        {m['mod_id']}")

    print(f"\n  [ZIP ] Dimensione: {zip_mb:.1f} MB")
    print(f"  [ZIP ] Path: {zip_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
