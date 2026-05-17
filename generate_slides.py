#!/usr/bin/env python3
"""
generate_slides.py — Genera i deck .pptx per tutti i 35 moduli CCNP ENCOR 350-401.
Uso: python generate_slides.py [MOD-XX]  oppure senza argomenti per tutti.
Deps: python-pptx >= 1.0, lxml
"""

import os
import sys
from pptx import Presentation
from pptx.util import Cm, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.oxml.ns import qn
from pptx.oxml import parse_xml

# ─── Palette ──────────────────────────────────────────────────────────────────
ARANCIO  = RGBColor(0xEF, 0x6A, 0x01)
NERO     = RGBColor(0x00, 0x00, 0x00)
AVORIO   = RGBColor(0xED, 0xEB, 0xDC)
GIALLO   = RGBColor(0xFF, 0xB6, 0x00)
BIANCO   = RGBColor(0xFF, 0xFF, 0xFF)
DARK_BG  = RGBColor(0x1A, 0x1A, 0x1A)
PALE_ORA = RGBColor(0xFB, 0xE4, 0xCC)
DARK_YEL = RGBColor(0x4A, 0x3D, 0x00)

# ─── Dimensioni ───────────────────────────────────────────────────────────────
W = Cm(33.87); H = Cm(19.05)
F_SANS = "Montserrat"; F_MONO = "Courier New"
PAD_L = Cm(1.06); HDR_55 = Cm(1.46); HDR_60 = Cm(1.59)

# ─── Helpers ──────────────────────────────────────────────────────────────────

def new_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])

def _remove_border(shp):
    spPr = shp._element.spPr
    ln = spPr.find(qn('a:ln'))
    if ln is not None:
        spPr.remove(ln)
    ns = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
    spPr.append(parse_xml(f'<a:ln {ns}><a:noFill/></a:ln>'))

def rect(slide, x, y, w, h, fill=None, border=None, border_w=Pt(1)):
    shp = slide.shapes.add_shape(1, int(x), int(y), int(w), int(h))
    if fill is not None:
        shp.fill.solid(); shp.fill.fore_color.rgb = fill
    else:
        shp.fill.background()
    if border is not None:
        shp.line.color.rgb = border; shp.line.width = int(border_w)
    else:
        _remove_border(shp)
    return shp

def rect_dashed(slide, x, y, w, h, color=ARANCIO, lw=Pt(1.5)):
    shp = slide.shapes.add_shape(1, int(x), int(y), int(w), int(h))
    shp.fill.background()
    shp.line.color.rgb = color; shp.line.width = int(lw)
    shp.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    return shp

def txt(slide, x, y, w, h, text, font=F_SANS, size=18, color=NERO,
        bold=False, italic=False, align=PP_ALIGN.LEFT, wrap=True):
    tb = slide.shapes.add_textbox(int(x), int(y), int(w), int(h))
    tf = tb.text_frame; tf.word_wrap = wrap
    tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
    p = tf.paragraphs[0]; p.alignment = align
    run = p.add_run(); run.text = text
    run.font.name = font; run.font.size = Pt(size)
    run.font.color.rgb = color; run.font.bold = bold; run.font.italic = italic
    return tb

def hdr(slide, title, fill=NERO, color=BIANCO, height=HDR_55, size=22, pad=PAD_L):
    shp = rect(slide, 0, 0, W, height, fill=fill)
    tf = shp.text_frame; tf.word_wrap = False
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_top = tf.margin_bottom = 0
    tf.margin_left = int(pad); tf.margin_right = int(pad)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.LEFT
    run = p.add_run(); run.text = title
    run.font.name = F_SANS; run.font.size = Pt(size)
    run.font.color.rgb = color; run.font.bold = True
    return shp

def code_box(slide, x, y, w, h, lines):
    shp = rect(slide, x, y, w, h, fill=DARK_BG, border=ARANCIO, border_w=Pt(1))
    tf = shp.text_frame; tf.word_wrap = False
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_top = int(Cm(0.3)); tf.margin_bottom = int(Cm(0.3))
    tf.margin_left = int(Cm(0.4)); tf.margin_right = int(Cm(0.4))
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        run = p.add_run(); run.text = line
        run.font.name = F_MONO; run.font.size = Pt(13)
        run.font.color.rgb = BIANCO
    return shp

def style_cell(cell, text, bg, fg, size=13, bold=False, align=PP_ALIGN.LEFT):
    cell.fill.solid(); cell.fill.fore_color.rgb = bg
    tf = cell.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_top = tf.margin_bottom = int(Pt(5))
    tf.margin_left = tf.margin_right = int(Pt(8))
    p = tf.paragraphs[0]; p.alignment = align
    for r in p.runs: p._p.remove(r._r)
    run = p.add_run(); run.text = text
    run.font.name = F_SANS; run.font.size = Pt(size)
    run.font.color.rgb = fg; run.font.bold = bold

# ─── Layout builders ──────────────────────────────────────────────────────────

def slide_cover(prs, mod_id, title, area, hours, codes):
    slide = new_slide(prs)
    rect(slide, 0, 0, W, H, fill=NERO)
    rect(slide, 0, 0, W, Cm(0.25), fill=ARANCIO)
    rect(slide, 0, H - Cm(0.15), W, Cm(0.15), fill=ARANCIO)
    txt(slide, W - Cm(5.5), Cm(0.5), Cm(5), Cm(0.9), "MAGNETICO",
        size=12, color=AVORIO, bold=True, align=PP_ALIGN.RIGHT)
    txt(slide, Cm(2.5), Cm(5.5), W - Cm(5), Cm(3.8),
        f"{mod_id} — {title}",
        size=38, color=ARANCIO, bold=True, align=PP_ALIGN.CENTER)
    sep_w = Cm(15)
    rect(slide, (W - sep_w) / 2, Cm(9.7), sep_w, Cm(0.06), fill=ARANCIO)
    txt(slide, Cm(2.5), Cm(10.1), W - Cm(5), Cm(1.8),
        f"{area}  ·  {hours}  ·  {codes}",
        size=17, color=AVORIO, align=PP_ALIGN.CENTER)
    txt(slide, Cm(0), H - Cm(1.5), W, Cm(1.0),
        "CCNP ENCOR 350-401  —  Materiale Didattico",
        size=11, color=AVORIO, align=PP_ALIGN.CENTER)

def slide_agenda(prs, items):
    slide = new_slide(prs)
    rect(slide, 0, 0, W, H, fill=AVORIO)
    hdr(slide, "AGENDA", fill=NERO, color=BIANCO, height=HDR_60, size=24)
    num_w = Cm(2.2); lbl_x = PAD_L + num_w + Cm(0.3)
    lbl_w = W - lbl_x - Cm(1.5); row_h = Cm(2.4)
    start_y = HDR_60 + Cm(0.8)
    for i, label in enumerate(items[:6]):
        y = start_y + i * row_h
        txt(slide, PAD_L, y, num_w, row_h,
            f"{i+1:02d}", size=22, color=ARANCIO, bold=True)
        rect(slide, PAD_L + num_w + Cm(0.1), y + Cm(0.3),
             Cm(0.05), row_h - Cm(0.6), fill=ARANCIO)
        txt(slide, lbl_x, y + Cm(0.2), lbl_w, row_h - Cm(0.2),
            label, size=19, color=NERO)

def slide_section(prs, title, subtitle=""):
    slide = new_slide(prs)
    rect(slide, 0, 0, W, H, fill=ARANCIO)
    title_y = H / 2 - Cm(4.0)
    txt(slide, Cm(2.5), title_y, W - Cm(5), Cm(3.5),
        title, size=44, color=BIANCO, bold=True, align=PP_ALIGN.CENTER)
    sep_w = Cm(12)
    sep_y = title_y + Cm(3.8)
    rect(slide, (W - sep_w) / 2, sep_y, sep_w, Cm(0.08), fill=BIANCO)
    if subtitle:
        txt(slide, Cm(3), sep_y + Cm(0.35), W - Cm(6), Cm(2.0),
            subtitle, size=20, color=BIANCO, align=PP_ALIGN.CENTER)

def slide_teoria(prs, title, bullet_points, key_concept=""):
    """bullet_points: lista di stringhe (max 6)"""
    slide = new_slide(prs)
    rect(slide, 0, 0, W, H, fill=AVORIO)
    hdr(slide, title, fill=NERO, color=BIANCO, height=HDR_55, size=20)
    box_h = Cm(2.2)
    body_top = HDR_55 + Cm(0.35)
    body_bot = H - box_h - Cm(0.45)
    body_h = body_bot - body_top
    accent_w = Cm(0.35)
    body_left = Cm(0.25) + accent_w + Cm(0.3)
    body_w = W - body_left - Cm(1.0)
    rect(slide, Cm(0.25), body_top, accent_w, body_h, fill=ARANCIO)
    body_text = "\n".join(f"• {p}" if not p.startswith("•") else p
                          for p in bullet_points)
    txt(slide, body_left, body_top + Cm(0.15), body_w, body_h - Cm(0.3),
        body_text, size=17, color=NERO, wrap=True)
    box_y = H - box_h - Cm(0.25)
    rect(slide, Cm(0.5), box_y, W - Cm(1.0), box_h, fill=PALE_ORA)
    kc = key_concept or bullet_points[-1] if bullet_points else ""
    txt(slide, Cm(1.0), box_y + Cm(0.3), W - Cm(2.0), box_h - Cm(0.35),
        f"Concetto chiave:  {kc}", size=15, color=ARANCIO, bold=True, wrap=True)

def slide_diagramma(prs, title, caption, nodes, links=None):
    """Disegna un diagramma semplice con rettangoli e testo."""
    slide = new_slide(prs)
    rect(slide, 0, 0, W, H, fill=BIANCO)
    hdr(slide, title, fill=NERO, color=BIANCO, height=HDR_55, size=20)
    caption_h = Cm(0.85)
    margin = Cm(0.7)
    diag_top = HDR_55 + Cm(0.35)
    diag_h = H - diag_top - caption_h - Cm(0.5)
    # Disegna area diagramma con bordo tratteggiato
    rect_dashed(slide, margin, diag_top, W - 2 * margin, diag_h)
    # Disegna nodi: nodes = [(label, x_frac, y_frac), ...]
    for label, xf, yf in nodes:
        nx = margin + (W - 2 * margin) * xf - Cm(2.0)
        ny = diag_top + diag_h * yf - Cm(0.5)
        rect(slide, nx, ny, Cm(4.0), Cm(1.0), fill=NERO)
        txt(slide, nx, ny, Cm(4.0), Cm(1.0),
            label, size=11, color=BIANCO, bold=True, align=PP_ALIGN.CENTER)
    cap_y = H - caption_h - Cm(0.15)
    txt(slide, PAD_L, cap_y, W - 2 * PAD_L, caption_h,
        caption, size=13, color=NERO, italic=True)

def slide_config(prs, title, lines, device="R1", highlight_idx=None):
    slide = new_slide(prs)
    rect(slide, 0, 0, W, H, fill=NERO)
    hdr(slide, title, fill=ARANCIO, color=NERO, height=HDR_55, size=20)
    m = Cm(1.0); code_top = HDR_55 + Cm(0.5)
    code_h = H - code_top - Cm(0.5); code_w = W - 2 * m
    code_box(slide, m, code_top, code_w, code_h, lines)
    if highlight_idx is not None:
        lp = Cm(0.6); mt = Cm(0.3)
        hl_y = code_top + mt + highlight_idx * lp
        rect(slide, m + Cm(0.1), hl_y, code_w - Cm(0.2), lp, fill=DARK_YEL)
    bw = Cm(2.0); bh = Cm(0.6)
    bx = m + code_w - bw - Cm(0.15); by = code_top + Cm(0.15)
    rect(slide, bx, by, bw, bh, fill=ARANCIO)
    txt(slide, bx, by, bw, bh, device, size=11, color=NERO, bold=True,
        align=PP_ALIGN.CENTER)

def slide_verifica(prs, title, lines, atteso_idx=None):
    slide = new_slide(prs)
    rect(slide, 0, 0, W, H, fill=NERO)
    hdr(slide, title, fill=ARANCIO, color=NERO, height=HDR_55, size=20)
    lbl_y = HDR_55 + Cm(0.25)
    txt(slide, PAD_L, lbl_y, Cm(14), Cm(0.65),
        "▼  VERIFICA ATTESA", size=13, color=GIALLO, bold=True)
    m = Cm(1.0); code_top = lbl_y + Cm(0.75)
    code_h = H - code_top - Cm(0.45); code_w = W - 2 * m
    code_box(slide, m, code_top, code_w, code_h, lines)
    if atteso_idx is not None:
        lp = Cm(0.6); mt = Cm(0.3)
        hl_y = code_top + mt + atteso_idx * lp
        txt(slide, W - Cm(6.5), hl_y, Cm(6), lp + Cm(0.1),
            "← atteso", size=13, color=ARANCIO, bold=True, align=PP_ALIGN.RIGHT)

def slide_troubleshooting(prs, rows):
    """rows: [(sintomo, causa_fix), ...]  max 4 righe"""
    slide = new_slide(prs)
    rect(slide, 0, 0, W, H, fill=AVORIO)
    hdr(slide, "Troubleshooting Guide",
        fill=NERO, color=BIANCO, height=HDR_55, size=20)
    t_m = Cm(0.7); t_top = HDR_55 + Cm(0.4)
    t_w = W - 2 * t_m; t_h = H - t_top - Cm(0.35)
    n_rows = len(rows) + 1
    tbl = slide.shapes.add_table(n_rows, 2,
                                  int(t_m), int(t_top),
                                  int(t_w), int(t_h)).table
    tbl.columns[0].width = int(t_w * 0.35)
    tbl.columns[1].width = int(t_w * 0.65)
    style_cell(tbl.cell(0, 0), "SINTOMO", NERO, BIANCO, size=14, bold=True,
               align=PP_ALIGN.CENTER)
    style_cell(tbl.cell(0, 1), "CAUSA + FIX", ARANCIO, NERO, size=14, bold=True,
               align=PP_ALIGN.CENTER)
    bgs = [BIANCO, AVORIO, BIANCO, AVORIO]
    for i, (s, f) in enumerate(rows):
        bg = bgs[i % 4]
        style_cell(tbl.cell(i + 1, 0), s, bg, NERO, size=13)
        style_cell(tbl.cell(i + 1, 1), f, bg, NERO, size=13)

def slide_exam_tips(prs, tips, q_a=None):
    """tips: lista 3-5 stringhe; q_a: [(domanda, risposta), ...]"""
    slide = new_slide(prs)
    rect(slide, 0, 0, W, H, fill=GIALLO)
    hdr(slide, "Exam Tips", fill=NERO, color=BIANCO, height=HDR_55, size=22)
    icon_y = HDR_55 + Cm(0.35)
    txt(slide, PAD_L, icon_y, Cm(2.2), Cm(2.2), "📋",
        size=32, color=NERO, align=PP_ALIGN.CENTER)
    tip_x = PAD_L + Cm(2.6); tip_w = W - tip_x - Cm(1.0)
    tip_h = Cm(1.65); tip_y0 = HDR_55 + Cm(0.4)
    for i, tip in enumerate(tips[:4]):
        txt(slide, tip_x, tip_y0 + i * tip_h, tip_w, tip_h,
            f"▶  {tip}", size=16, color=NERO, wrap=True)
    qa_top = tip_y0 + min(len(tips), 4) * tip_h + Cm(0.45)
    qa_h = H - qa_top - Cm(0.4)
    if qa_h > Cm(1.5):
        rect(slide, PAD_L, qa_top, W - 2 * PAD_L, qa_h,
             fill=BIANCO, border=NERO, border_w=Pt(1))
        if q_a:
            qa_text = "\n\n".join(f"Q:  {q}\nA:  {a}" for q, a in q_a[:2])
        else:
            qa_text = ""
        if qa_text:
            txt(slide, PAD_L + Cm(0.4), qa_top + Cm(0.25),
                W - 2 * PAD_L - Cm(0.8), qa_h - Cm(0.4),
                qa_text, size=14, color=NERO, wrap=True)

def slide_summary(prs, labels, bodies):
    """labels: 3 label; bodies: 3 testi"""
    slide = new_slide(prs)
    rect(slide, 0, 0, W, H, fill=ARANCIO)
    txt(slide, Cm(1), Cm(0.9), W - Cm(2), Cm(2.0),
        "TAKEAWAY", size=34, color=BIANCO, bold=True, align=PP_ALIGN.CENTER)
    sep_w = Cm(20)
    rect(slide, (W - sep_w) / 2, Cm(2.9), sep_w, Cm(0.06), fill=BIANCO)
    n = 3; mx = Cm(1.2); gap = Cm(0.7)
    bw = (W - 2 * mx - (n - 1) * gap) / n
    bt = Cm(3.3); bh = H - bt - Cm(1.6)
    for i in range(n):
        bx = mx + i * (bw + gap)
        rect(slide, bx, bt, bw, bh, fill=NERO)
        txt(slide, bx, bt + Cm(0.4), bw, Cm(1.6),
            str(i + 1), size=26, color=ARANCIO, bold=True,
            align=PP_ALIGN.CENTER)
        rect(slide, bx + Cm(0.9), bt + Cm(2.0), bw - Cm(1.8), Cm(0.06),
             fill=ARANCIO)
        txt(slide, bx + Cm(0.25), bt + Cm(2.3), bw - Cm(0.5), Cm(1.2),
            labels[i], size=16, color=BIANCO, bold=True,
            align=PP_ALIGN.CENTER)
        txt(slide, bx + Cm(0.35), bt + Cm(3.6), bw - Cm(0.7), bh - Cm(3.8),
            bodies[i], size=14, color=AVORIO, wrap=True,
            align=PP_ALIGN.CENTER)
    txt(slide, Cm(0), H - Cm(1.1), W, Cm(0.9),
        "CCNP ENCOR 350-401  —  Materiale Didattico",
        size=11, color=BIANCO, align=PP_ALIGN.CENTER)

# ─── Generatore deck ──────────────────────────────────────────────────────────

def make_deck(module_id, content):
    """
    content = {
      'title': str, 'area': str, 'hours': str, 'codes': str,
      'agenda': [str, ...],                 # titoli agenda (concetti)
      'topology': {'title', 'caption', 'nodes': [(label,xf,yf)]},
      'sections': [                          # blocchi teorici
        {'section': str, 'subtitle': str,   # slide Section Header
         'slides': [                         # slide Teoria o Tabella
           {'type': 'teoria', 'title': str, 'points': [str], 'key': str},
           {'type': 'config', 'title': str, 'lines': [str], 'device': str, 'hl': int|None},
           {'type': 'verifica', 'title': str, 'lines': [str], 'hl': int|None},
         ]
        }, ...
      ],
      'config_section': {'title': str, 'slides': [...]},  # opz
      'trouble': [(sintomo, fix), ...],
      'exam_tips': [str, ...],
      'exam_qa': [(q, a), ...],
      'summary': {'labels': [str,str,str], 'bodies': [str,str,str]}
    }
    """
    prs = Presentation()
    prs.slide_width = W; prs.slide_height = H

    # 1 — Cover
    slide_cover(prs, module_id, content['title'],
                content['area'], content['hours'], content['codes'])

    # 2 — Agenda
    slide_agenda(prs, content['agenda'])

    # 3 — Topologia
    topo = content.get('topology')
    if topo:
        slide_diagramma(prs, topo['title'], topo['caption'], topo['nodes'])

    # 4 — Sezioni teoriche
    for sec in content.get('sections', []):
        slide_section(prs, sec['section'], sec.get('subtitle', ''))
        for sl in sec.get('slides', []):
            if sl['type'] == 'teoria':
                slide_teoria(prs, sl['title'], sl['points'], sl.get('key', ''))
            elif sl['type'] == 'config':
                slide_config(prs, sl['title'], sl['lines'],
                             sl.get('device', 'R1'), sl.get('hl'))
            elif sl['type'] == 'verifica':
                slide_verifica(prs, sl['title'], sl['lines'], sl.get('hl'))

    # 5 — Sezione config/verifica se separata
    cfg_sec = content.get('config_section')
    if cfg_sec:
        slide_section(prs, "CONFIGURAZIONE & VERIFICA")
        for sl in cfg_sec.get('slides', []):
            if sl['type'] == 'config':
                slide_config(prs, sl['title'], sl['lines'],
                             sl.get('device', 'R1'), sl.get('hl'))
            elif sl['type'] == 'verifica':
                slide_verifica(prs, sl['title'], sl['lines'], sl.get('hl'))

    # 6 — Troubleshooting
    if content.get('trouble'):
        slide_troubleshooting(prs, content['trouble'])

    # 7 — Exam Tips
    slide_exam_tips(prs, content['exam_tips'], content.get('exam_qa'))

    # 8 — Summary
    s = content['summary']
    slide_summary(prs, s['labels'], s['bodies'])

    return prs


# ══════════════════════════════════════════════════════════════════════════════
# CONTENUTO MODULI
# ══════════════════════════════════════════════════════════════════════════════

MODULES = {}

# ─── MOD-01 ───────────────────────────────────────────────────────────────────
MODULES['MOD-01'] = {
    'title': 'OSPFv2 Fondamenta',
    'area': 'AREA 1 — OSPF', 'hours': '2h', 'codes': '3.2.a · 3.2.b',
    'agenda': [
        'Sub-interface 802.1Q: configurazione e best practice',
        'OSPF: processo, Router-ID e selezione',
        'Network statement vs ip ospf area',
        'DR/BDR Election: regole e controllo',
        'Network type point-to-point e costo OSPF',
        'Troubleshooting adiacenze: stati e cause',
    ],
    'topology': {
        'title': 'Topologia MOD-01 — OSPFv2 Multi-Area',
        'caption': 'R3-R6: Area 0 Backbone (broadcast + ring P2P) · R1/R7: Area 15/99 · R2: Area 25 · ABR: R5',
        'nodes': [
            ('R1\nABR 15/99', 0.1, 0.4),
            ('R3\nDROTHER', 0.3, 0.25),
            ('R4\nDR prio 255', 0.45, 0.4),
            ('R5\nABR 0/15/25', 0.6, 0.4),
            ('R6\nBDR prio 100', 0.75, 0.25),
            ('R2\nArea 25', 0.9, 0.55),
            ('R7\nArea 99', 0.1, 0.7),
        ],
    },
    'sections': [
        {
            'section': 'Sub-interface 802.1Q',
            'subtitle': 'Multiplexing logico su interfaccia fisica',
            'slides': [
                {
                    'type': 'teoria',
                    'title': 'Sub-interface 802.1Q — Come funziona',
                    'points': [
                        'Una sub-interface (virtuale) suddivide logicamente una porta fisica con tag VLAN 802.1Q',
                        'Sintassi IOS: interface eth0/0.<vlan>  →  encapsulation dot1Q <vlan>',
                        "L'interfaccia fisica padre deve avere no ip address + no shutdown (nessuna configurazione IP)",
                        'Il numero sub-interface coincide per convenzione con il numero VLAN (leggibilità)',
                        'Ogni sub-interface ha il proprio indirizzo IP e partecipa independentemente ai protocolli',
                        'In ambiente IOU: tutta la connettività inter-router avviene via sub-interface (no link fisici diretti)',
                    ],
                    'key': 'La fisica è uno, il logico è molti — tag VLAN separa il traffico di più reti su un solo cavo.',
                },
                {
                    'type': 'config',
                    'title': 'Sub-interface 802.1Q — Snippet',
                    'lines': [
                        'interface Ethernet0/0',
                        ' no ip address',
                        ' no shutdown          ! padre deve essere UP',
                        '!',
                        'interface Ethernet0/0.34',
                        ' encapsulation dot1Q 34     ! tag VLAN 34',
                        ' ip address 10.0.34.1 255.255.255.252',
                        ' description P2P_R3-R4_Area0',
                        ' no shutdown',
                        ' ip ospf 100 area 0         ! abilita direttamente OSPF',
                    ],
                    'device': 'R3', 'hl': 5,
                },
            ],
        },
        {
            'section': 'OSPF: Processo e Router-ID',
            'subtitle': 'Identità univoca nel dominio di routing',
            'slides': [
                {
                    'type': 'teoria',
                    'title': 'OSPF Router-ID — Selezione e Best Practice',
                    'points': [
                        'Il Router-ID identifica univocamente il router nella LSDB OSPF',
                        'Ordine di selezione: 1) router-id configurato  2) IP loopback più alto  3) IP fisico più alto',
                        'Best practice: configurare sempre esplicitamente (router-id x.x.x.x)',
                        'Senza configurazione esplicita: cambio IP = cambio Router-ID = instabilità LSDB',
                        'Convenzione laboratorio: R1 → 1.1.1.1,  R2 → 2.2.2.2, ... R7 → 7.7.7.7',
                        'Network statement vs ip ospf area: due metodi equivalenti per abilitare OSPF su un\'interfaccia',
                    ],
                    'key': 'router-id esplicito = comportamento deterministico. Senza: rischio instabilità al riavvio.',
                },
                {
                    'type': 'teoria',
                    'title': 'Network Statement vs ip ospf area',
                    'points': [
                        '• network 10.0.0.0 0.0.0.7 area 0 → abilita tutte le interfacce con IP nel range',
                        '• ip ospf 100 area 0 (su interfaccia) → esplicito, per-interfaccia, più leggibile',
                        'passive-interface: impedisce l\'invio di Hello ma mantiene il prefisso nella LSDB',
                        'Tecnica sicura: passive-interface default + no passive-interface su porte OSPF attive',
                        'ip ospf network point-to-point: elimina DR/BDR su link con un solo neighbor (sub-if P2P)',
                        'Broadcast (default Ethernet): DR/BDR election — usare solo su segmenti multi-router',
                    ],
                    'key': 'ip ospf area per-interfaccia è più preciso e meno soggetto a errori di wildcard.',
                },
            ],
        },
        {
            'section': 'DR/BDR Election',
            'subtitle': 'Riduzione adiacenze su segmenti broadcast',
            'slides': [
                {
                    'type': 'teoria',
                    'title': 'DR/BDR — Perché esiste e Come funziona',
                    'points': [
                        'Problema: N router su broadcast → N*(N-1)/2 adiacenze (45 con 10 router)',
                        'Soluzione: DR centralizza — tutti inviano aggiornamenti al DR (224.0.0.6)',
                        'DR li riflette a tutti (224.0.0.5) — riduce a N-1 adiacenze reali',
                        'Regole election: 1) priority più alta  2) Router-ID più alto (pareggio)',
                        'NON preemptive: il DR caduto che torna diventa DROTHER anche con priority alta',
                        'Forza rielelezione: clear ip ospf process (interrompe tutte le adiacenze)',
                    ],
                    'key': 'Election non preemptive: modificare priority non basta — serve clear ip ospf process.',
                },
                {
                    'type': 'verifica',
                    'title': 'Verifica DR/BDR Election',
                    'lines': [
                        'R4# show ip ospf interface ethernet 0/0.3456',
                        '  Network Type BROADCAST, Cost: 10',
                        '  Designated Router (ID) 4.4.4.4, Interface address 10.0.0.4',
                        '  Backup Designated router (ID) 6.6.6.6, Interface address 10.0.0.6',
                        '',
                        'R4# show ip ospf neighbor',
                        'Neighbor ID  Pri  State      Dead Time  Address    Interface',
                        '3.3.3.3        0  FULL/DROTHER  00:00:38  10.0.0.3  Et0/0.3456',
                        '5.5.5.5        0  FULL/DROTHER  00:00:36  10.0.0.5  Et0/0.3456',
                        '6.6.6.6      100  FULL/BDR      00:00:37  10.0.0.6  Et0/0.3456',
                    ],
                    'hl': 7,
                },
            ],
        },
        {
            'section': 'Troubleshooting Adiacenze OSPF',
            'subtitle': 'Macchina a stati e cause di blocco',
            'slides': [
                {
                    'type': 'teoria',
                    'title': 'Stati Adiacenza OSPF — Dove si blocca e Perché',
                    'points': [
                        'DOWN → INIT: Hello ricevuto ma router locale non è nella lista neighbor (link unidirezionale)',
                        'INIT → 2-WAY: Hello bidirezionale OK (DROTHER-DROTHER fermano qui — normale)',
                        'EXSTART: negoziazione master/slave per DB exchange → MTU mismatch blocca qui',
                        'EXCHANGE: scambio DBD → MTU mismatch o database corrotto',
                        'FULL: adiacenza completa e LSDB sincronizzata — stato desiderato',
                        'Triade errori più comuni: timer mismatch · area mismatch · authentication mismatch',
                    ],
                    'key': 'EXSTART/EXCHANGE = quasi sempre MTU mismatch. Rimedio: ip ospf mtu-ignore.',
                },
            ],
        },
    ],
    'config_section': {
        'slides': [
            {
                'type': 'config',
                'title': 'OSPF — Comandi Chiave',
                'lines': [
                    'router ospf 100',
                    ' router-id 3.3.3.3            ! sempre esplicito',
                    ' network 10.0.0.0 0.0.0.7 area 0',
                    ' passive-interface default     ! blocca Hello su tutte',
                    ' no passive-interface Et0/0.3456  ! riabilita OSPF attivo',
                    '!',
                    'interface Ethernet0/0.34',
                    ' ip ospf 100 area 0            ! metodo diretto',
                    ' ip ospf network point-to-point ! niente DR/BDR',
                    ' ip ospf cost 1000             ! sfavorisce il percorso',
                    ' ip ospf priority 0            ! escluso dalla election',
                ],
                'device': 'R3', 'hl': 4,
            },
        ],
    },
    'trouble': [
        ('Adiacenza bloccata in EXSTART', 'MTU mismatch — ip ospf mtu-ignore su entrambi i lati'),
        ('Neighbor in INIT, non avanza', 'Autenticazione MD5 su un solo lato — verificare show ip ospf interface'),
        ('DR non è il router desiderato', 'Election non preemptive — eseguire clear ip ospf process dopo aver modificato priority'),
        ('Sub-interface non passa traffico', 'encapsulation dot1Q mancante o VLAN non permessa sul trunk switch'),
    ],
    'exam_tips': [
        'Router-ID: configurare sempre esplicitamente. Senza: cambio IP = instabilità OSPF',
        'ip ospf network point-to-point su link P2P elimina DR/BDR e accelera convergenza',
        'Election DR/BDR NON è preemptive: priority alta non basta, serve clear ip ospf process',
        'EXSTART/EXCHANGE bloccato = MTU mismatch (quasi sempre)',
    ],
    'exam_qa': [
        ('Un router OSPF resta in EXSTART. Causa più probabile?',
         'MTU mismatch — impedisce lo scambio dei DBD. Fix: ip ospf mtu-ignore'),
        ('Come escludere un router dalla election senza disabilitare OSPF?',
         'ip ospf priority 0 sull\'interfaccia — partecipa all\'area ma non vince mai DR/BDR'),
    ],
    'summary': {
        'labels': ['Router-ID Esplicito', 'Network Type P2P', 'DR/BDR Election'],
        'bodies': [
            'Sempre configurare router-id x.x.x.x: comportamento deterministico, nessuna sorpresa al riavvio.',
            'ip ospf network point-to-point su sub-if con un solo neighbor: elimina DR/BDR, convergenza più rapida.',
            'Non preemptive: modificare priority richiede clear ip ospf process per forzare la rielelezione.',
        ],
    },
}

# ─── MOD-02 ───────────────────────────────────────────────────────────────────
MODULES['MOD-02'] = {
    'title': 'OSPFv2 Aree & Summarization',
    'area': 'AREA 1 — OSPF', 'hours': '2h', 'codes': '3.2.a · 3.2.b',
    'agenda': [
        'Architettura OSPF multi-area: ABR e backbone',
        'Summarization inter-area con area range',
        'Stub Area e Totally-Stub Area',
        'NSSA e redistribuzione esterna',
        'Virtual Link: quando e come usarlo',
        'ASBR e summary-address per rotte esterne',
    ],
    'topology': {
        'title': 'Topologia MOD-02 — Aree e ABR',
        'caption': 'R5: ABR Area0/15/25 · R1: ABR Area15/99 · Area 0: backbone con R3-R4-R5-R6 · summarization su R5',
        'nodes': [
            ('R7\nArea 99', 0.08, 0.3),
            ('R1\nABR 15/99', 0.22, 0.3),
            ('R5\nABR 0/15/25', 0.5, 0.5),
            ('R3/R4/R6\nArea 0', 0.65, 0.35),
            ('R2\nArea 25', 0.85, 0.5),
        ],
    },
    'sections': [
        {
            'section': 'OSPF Multi-Area',
            'subtitle': 'Scalabilità e riduzione della LSDB',
            'slides': [
                {
                    'type': 'teoria',
                    'title': 'Architettura Multi-Area OSPF',
                    'points': [
                        'Area 0 (backbone): obbligatoria — tutte le altre aree devono connettersi ad area 0',
                        'ABR (Area Border Router): connette due o più aree, mantiene LSDB separate per ciascuna',
                        'LSA Type 1 (Router LSA): restano confinati nell\'area di origine',
                        'LSA Type 3 (Summary LSA): generati dall\'ABR per annunciare prefissi inter-area',
                        'Vantaggio: fallimento in area X non causa recalcolo SPF nelle altre aree',
                        'ASBR: redistribuisce rotte esterne (LSA Type 5) verso tutto il dominio OSPF',
                    ],
                    'key': 'Ogni area ha la propria LSDB — ABR traduce Type 1/2 in Type 3 verso le altre aree.',
                },
                {
                    'type': 'teoria',
                    'title': 'Stub, Totally-Stub e NSSA',
                    'points': [
                        'Stub area: blocca LSA Type 5 (rotte esterne) — ABR inietta default route (Type 3)',
                        'Totally-Stub: blocca anche LSA Type 3 (inter-area) — solo default route rimane',
                        'NSSA (Not-So-Stubby Area): come stub ma permette redistribuzione locale (LSA Type 7)',
                        'LSA Type 7 → Type 5: l\'ABR converte quando esce dall\'NSSA verso il backbone',
                        'Tutti i router in un\'area stub/NSSA devono avere la stessa configurazione (area X stub)',
                        'Totally-NSSA (area X nssa no-summary): massima riduzione LSDB con redistribuzione locale',
                    ],
                    'key': 'Totally-Stub = minima LSDB possibile: solo prefissi interni + default route dall\'ABR.',
                },
            ],
        },
        {
            'section': 'Summarization e Virtual Link',
            'subtitle': 'Ottimizzazione e continuità backbone',
            'slides': [
                {
                    'type': 'teoria',
                    'title': 'Summarization Inter-Area e ASBR',
                    'points': [
                        'area range (su ABR): aggrega prefissi inter-area — riduce LSDB nelle aree adiacenti',
                        'Sintassi: area 15 range 10.15.0.0 255.255.252.0  (su ABR che confina con Area 15)',
                        'summary-address (su ASBR): aggrega rotte esterne (Type 5) prima dell\'annuncio',
                        'Vantaggio: meno LSA = convergenza più rapida + meno memoria nei router interni',
                        'Attenzione: la summary route è attiva solo se almeno un prefisso subordinato esiste',
                        'Discard route: IOS installa automaticamente una rotta Null0 per evitare loop',
                    ],
                    'key': 'area range sull\'ABR: N prefissi dell\'area diventano 1 summary verso il backbone.',
                },
                {
                    'type': 'teoria',
                    'title': 'Virtual Link — Quando e Come',
                    'points': [
                        'Problema: una nuova area non può connettersi direttamente ad Area 0',
                        'Virtual Link: estende logicamente Area 0 attraverso una transit area non-stub',
                        'Sintassi: area <transit-area> virtual-link <router-id-remoto>  su entrambi gli ABR',
                        'Limitazioni: la transit area NON può essere stub/totally-stub/NSSA',
                        'Il Virtual Link è un\'interfaccia OSPF logica — vive in Area 0, transita altrove',
                        'Uso reale limitato: preferire ridisegno topologico se possibile',
                    ],
                    'key': 'Virtual Link come eccezione, non come design normale — transit area non può essere stub.',
                },
            ],
        },
    ],
    'config_section': {
        'slides': [
            {
                'type': 'config',
                'title': 'ABR Summarization + Stub + Virtual Link',
                'lines': [
                    'router ospf 100',
                    ' area 15 range 10.15.0.0 255.255.252.0  ! summarize Area 15',
                    ' area 25 range 10.25.0.0 255.255.252.0  ! summarize Area 25',
                    ' area 25 stub                            ! totally-stub: aggiungere no-summary',
                    ' area 99 virtual-link 1.1.1.1            ! VL via Area 15 (R5→R1)',
                    '!',
                    '! Su ASBR per rotte redistribuite:',
                    ' summary-address 192.168.100.0 255.255.252.0',
                ],
                'device': 'R5', 'hl': 1,
            },
            {
                'type': 'verifica',
                'title': 'Verifica Summarization e Stub',
                'lines': [
                    'R5# show ip route ospf',
                    'O IA 10.15.0.0/22 [110/11] via 10.1.15.2   ! summary Area 15',
                    'O*IA 0.0.0.0/0   [110/1]  via 10.0.0.4     ! default in stub',
                    '',
                    'R5# show ip ospf border-routers',
                    'OSPF Process 100 internal Routing Table',
                    'Codes: i - Intra-area route, I - Inter-area route',
                    'i 1.1.1.1 [11] via 10.1.15.2, Et0/0.51, ABR, Area 15',
                ],
                'hl': 1,
            },
        ],
    },
    'trouble': [
        ('Virtual Link non si forma', 'Transit area configurata come stub — VL richiede transit area non-stub'),
        ('Summary non appare nella routing table', 'Nessun prefisso subordinato attivo — verificare che almeno una rotta dell\'area esista'),
        ('Default route non ricevuta in stub area', 'Non tutti i router dell\'area hanno "area X stub" — configurazione deve essere uniforme'),
        ('LSA Type 5 presenti in stub area', 'Un router dell\'area non ha "area X stub" — blocca propagazione'),
    ],
    'exam_tips': [
        'Tutti i router in una stub area devono avere "area X stub" — configurazione non-uniforme = adiacenza down',
        'area range va configurato sull\'ABR, lato area da aggregare — non nel backbone',
        'Virtual Link: transit area non può essere stub/NSSA — altrimenti non funziona',
        'LSA Type 7 (NSSA) viene convertito in Type 5 dall\'ABR verso il backbone',
    ],
    'exam_qa': [
        ('Differenza tra Stub e Totally-Stub?',
         'Stub blocca Type 5 (esterne). Totally-Stub blocca anche Type 3 (inter-area) — solo default route rimane.'),
        ('Perché la transit area di un Virtual Link non può essere stub?',
         'Il VL appartiene ad Area 0: richiederebbe LSA di Area 0 attraverso la transit area, impossibile in stub.'),
    ],
    'summary': {
        'labels': ['Gerarchia Aree', 'Summarization ABR', 'Stub/Totally-Stub'],
        'bodies': [
            'Area 0 obbligatoria. ABR traduce LSA Type 1/2 in Type 3. Virtual Link solo come eccezione.',
            'area range sull\'ABR aggrega N prefissi in 1 summary — riduce LSDB e accelera convergenza.',
            'Stub blocca Type 5; Totally-Stub blocca anche Type 3. NSSA permette redistribuzione locale.',
        ],
    },
}

# ─── MOD-03 ───────────────────────────────────────────────────────────────────
MODULES['MOD-03'] = {
    'title': 'OSPFv3 Dual-Stack',
    'area': 'AREA 1 — OSPF', 'hours': '1.5h', 'codes': '3.2.b',
    'agenda': [
        'OSPFv2 vs OSPFv3: differenze architetturali',
        'OSPFv3 per IPv6: processo e configurazione',
        'Address-Family: dual-stack su singolo processo',
        'Link-Local come sorgente Hello OSPFv3',
        'Verifica e troubleshooting OSPFv3',
    ],
    'topology': {
        'title': 'Topologia MOD-03 — OSPFv3 Dual-Stack',
        'caption': 'Stessa topologia MOD-02 con indirizzi IPv6. Area 0: 2001:db8:0::/64. R5 ABR dual-stack.',
        'nodes': [
            ('R1\nArea 15\nIPv6', 0.15, 0.35),
            ('R5\nABR 0/15/25\nDual-stack', 0.5, 0.5),
            ('R3/R4/R6\nArea 0\n2001:db8:0::/64', 0.7, 0.3),
            ('R2\nArea 25\nIPv6', 0.85, 0.6),
        ],
    },
    'sections': [
        {
            'section': 'OSPFv3 vs OSPFv2',
            'subtitle': 'Evoluzione per il supporto IPv6 e dual-stack',
            'slides': [
                {
                    'type': 'teoria',
                    'title': 'Differenze Chiave OSPFv2 → OSPFv3',
                    'points': [
                        'OSPFv2: solo IPv4. OSPFv3: IPv6 native, poi esteso a dual-stack con address-family',
                        'Transport: OSPFv3 usa link-local IPv6 (fe80::) come sorgente dei pacchetti Hello',
                        'Router-ID: rimane un valore 32-bit anche in OSPFv3 (non è un indirizzo IPv6)',
                        'Autenticazione: OSPFv2 usa area/interface auth; OSPFv3 usa IPSec (AH/ESP)',
                        'Configurazione: ipv6 router ospf <pid> oppure router ospfv3 <pid> address-family',
                        'Link-local come next-hop: OSPFv3 usa il link-local del neighbor come next-hop nelle rotte',
                    ],
                    'key': 'OSPFv3 usa link-local IPv6 per i Hello — il Router-ID rimane 32-bit come in OSPFv2.',
                },
                {
                    'type': 'teoria',
                    'title': 'Configurazione OSPFv3 — Metodi',
                    'points': [
                        'Metodo 1 (classic): ipv6 router ospf <pid> + ipv6 ospf <pid> area X sull\'interfaccia',
                        'Metodo 2 (address-family): router ospfv3 <pid> + address-family ipv6 unicast per IPv6',
                        'Dual-stack: router ospfv3 include sia address-family ipv4 che ipv6 — un solo processo',
                        'Su ogni interfaccia: ospfv3 <pid> ipv4 area X  e  ospfv3 <pid> ipv6 area X',
                        'ipv6 unicast-routing: obbligatorio per abilitare il forwarding IPv6 sul router',
                        'passive-interface funziona anche in OSPFv3 — stessa logica OSPFv2',
                    ],
                    'key': 'address-family nel router ospfv3: un solo processo gestisce sia IPv4 che IPv6 — approccio moderno.',
                },
            ],
        },
        {
            'section': 'Verifica e Differenze Operative',
            'subtitle': 'Comandi show e interpretazione output',
            'slides': [
                {
                    'type': 'verifica',
                    'title': 'Verifica OSPFv3 Dual-Stack',
                    'lines': [
                        'R5# show ospfv3 neighbor',
                        'OSPFv3 100 address-family ipv6 (router-id 5.5.5.5)',
                        'Neighbor ID  Pri  State   Dead  Interface-ID  Interface',
                        '3.3.3.3        1  FULL/DROTHER  00:00:38  6  Et0/0.3456',
                        '4.4.4.4        1  FULL/DR       00:00:36  7  Et0/0.3456',
                        '',
                        'R5# show ipv6 route ospf',
                        'OI 2001:db8:15::/64 [110/11] via FE80::1, Et0/0.51',
                    ],
                    'hl': 3,
                },
            ],
        },
    ],
    'config_section': {
        'slides': [
            {
                'type': 'config',
                'title': 'OSPFv3 Address-Family — Snippet',
                'lines': [
                    'ipv6 unicast-routing',
                    '!',
                    'router ospfv3 100',
                    ' router-id 5.5.5.5',
                    ' address-family ipv4 unicast',
                    '  area 0 range 10.0.0.0 255.255.248.0',
                    ' address-family ipv6 unicast',
                    '  area 0 range 2001:db8::/48',
                    '!',
                    'interface Ethernet0/0.3456',
                    ' ospfv3 100 ipv4 area 0',
                    ' ospfv3 100 ipv6 area 0',
                ],
                'device': 'R5', 'hl': 4,
            },
        ],
    },
    'trouble': [
        ('Adiacenza OSPFv3 non si forma', 'ipv6 unicast-routing non abilitato — prerequisito assoluto per OSPFv3'),
        ('Router-ID non configurato', 'Nessuna interfaccia IPv4 attiva — configurare router-id manualmente in ospfv3'),
        ('Next-hop nelle rotte IPv6 è link-local', 'Comportamento normale in OSPFv3 — il link-local fe80:: è usato come next-hop'),
        ('show ospfv3 neighbor vuoto', 'Interfaccia non abilitata in OSPFv3 — verificare ospfv3 <pid> area su ogni interfaccia'),
    ],
    'exam_tips': [
        'OSPFv3 usa link-local come sorgente Hello — il Router-ID rimane 32-bit (come OSPFv2)',
        'ipv6 unicast-routing: obbligatorio prima di configurare qualsiasi protocollo IPv6',
        'address-family ipv4/ipv6 in ospfv3: un processo gestisce entrambi i protocolli',
        'Autenticazione OSPFv3 usa IPSec (non MD5 come OSPFv2)',
    ],
    'exam_qa': [
        ('OSPFv3 usa quale indirizzo come sorgente dei pacchetti Hello?',
         'Il link-local IPv6 (fe80::) dell\'interfaccia — non l\'indirizzo globale.'),
        ('Come mantenere la compatibilità dual-stack con un solo processo OSPF?',
         'router ospfv3 con address-family ipv4 unicast e address-family ipv6 unicast.'),
    ],
    'summary': {
        'labels': ['Link-Local Source', 'Router-ID 32-bit', 'Address-Family'],
        'bodies': [
            'OSPFv3 usa fe80:: come sorgente Hello — indirizzo link-local, non globale.',
            'Il Router-ID rimane 32-bit anche in OSPFv3 — deve essere configurato se mancano interfacce IPv4.',
            'ospfv3 con address-family: un processo gestisce IPv4 e IPv6 — approccio moderno e pulito.',
        ],
    },
}

# ─── MOD-04 ───────────────────────────────────────────────────────────────────
MODULES['MOD-04'] = {
    'title': 'OSPF Troubleshooting',
    'area': 'AREA 1 — OSPF', 'hours': '4h', 'codes': '1.10.a-d',
    'agenda': [
        'Metodologia troubleshooting OSPF strutturata',
        'Scenario A: adiacenze mancanti (timer, auth, area)',
        'Scenario B: rotte assenti nella routing table',
        'Scenario C: External Type E1 vs E2 e metriche',
        'Scenario D: OSPFv3 dual-stack diagnostica',
        'Tool: debug ip ospf e interpretazione output',
    ],
    'topology': {
        'title': 'Topologia MOD-04 — Troubleshooting Lab',
        'caption': 'R3: ABR + ASBR (redistribuisce static) · R4: ABR · R5: Area 2 Stub · auth MD5 su R1-R4',
        'nodes': [
            ('R1\nArea 0', 0.12, 0.3),
            ('R2\nArea 0', 0.35, 0.3),
            ('R3\nABR+ASBR', 0.58, 0.5),
            ('R4\nABR 0/1/2', 0.75, 0.3),
            ('R5\nArea 2 Stub', 0.9, 0.5),
        ],
    },
    'sections': [
        {
            'section': 'Metodologia Troubleshooting',
            'subtitle': 'Approccio sistematico a problemi OSPF',
            'slides': [
                {
                    'type': 'teoria',
                    'title': 'Framework Troubleshooting OSPF',
                    'points': [
                        'Livello 1 — Fisica: interfaccia UP/UP? show interfaces / show ip interface brief',
                        'Livello 2 — Adiacenza: show ip ospf neighbor → stato e Dead timer',
                        'Livello 3 — LSDB: show ip ospf database → LSA presenti e completi',
                        'Livello 4 — Routing Table: show ip route ospf → prefissi installati nel RIB',
                        'Livello 5 — Forwarding: ping / traceroute → traffico effettivo',
                        'Debug: debug ip ospf adj | hello → usare con cautela, poi undebug all',
                    ],
                    'key': 'Seguire la pila dal basso: fisica → adiacenza → LSDB → RIB → forwarding.',
                },
                {
                    'type': 'teoria',
                    'title': 'E1 vs E2 — Metriche Rotte Esterne',
                    'points': [
                        'E1 (External Type 1): metrica = costo OSPF interno + seed metric esterna',
                        'E2 (External Type 2, default): metrica = solo seed metric esterna (costo interno ignorato)',
                        'E2 preferisce il percorso con seed metric più bassa — indifferente alla topologia interna',
                        'E1 preferisce il percorso totale più corto — tiene conto della topologia OSPF',
                        'Redistribuzione: redistribute static metric 20 metric-type 1 subt type come E1',
                        'In pratica: E1 per rotte dove conta la topologia interna; E2 per rotte "flat"',
                    ],
                    'key': 'E2 default: metrica statica. E1: metrica cumulativa. Usare E1 quando la topologia interna conta.',
                },
            ],
        },
    ],
    'config_section': {
        'slides': [
            {
                'type': 'config',
                'title': 'Debug e Diagnostica OSPF',
                'lines': [
                    '! --- Sequenza diagnostica standard ---',
                    'show ip ospf neighbor          ! stato adiacenze',
                    'show ip ospf neighbor detail   ! MTU, auth, timers',
                    'show ip ospf database          ! LSDB completa',
                    'show ip ospf database external ! solo LSA Type 5',
                    'show ip route ospf             ! RIB OSPF',
                    '!',
                    'debug ip ospf adj              ! messaggi adiacenza',
                    'debug ip ospf hello            ! pacchetti Hello',
                    'undebug all                    ! stop debug',
                ],
                'device': 'R1', 'hl': 1,
            },
        ],
    },
    'trouble': [
        ('Area 0 non si vede da area stub', 'LSA Type 5 bloccati in stub area — usare NSSA se serve redistribuzione locale'),
        ('E2 route preferisce percorso sbagliato', 'E2 ignora costo interno — passare a metric-type 1 per routing topology-aware'),
        ('MD5 auth: adiacenza bloccata in INIT', 'Key mismatch o key-id diverso — verificare ip ospf authentication message-digest e key id'),
        ('OSPFv3 prefix non appare nel RIB', 'ipv6 unicast-routing non abilitato o interfaccia non abilitata in area'),
    ],
    'exam_tips': [
        'E2 (default): metrica solo esterna. E1: metrica esterna + interna. E1 più corretto per topologie complesse',
        'show ip ospf neighbor detail: mostra MTU, dead timer, auth type — tutto ciò che causa blocco',
        'Stub area: area X stub su TUTTI i router dell\'area — anche su un solo router = adiacenza down',
        'debug ip ospf adj: vedere perché due router non formano adiacenza in tempo reale',
    ],
    'exam_qa': [
        ('Differenza tra E1 e E2 nelle rotte OSPF esterne?',
         'E2 (default): metrica = solo seed metric esterna. E1: metrica = seed + costo OSPF interno accumulato.'),
        ('Quale comando mostra l\'autenticazione configurata su un\'interfaccia OSPF?',
         'show ip ospf interface <int> — mostra auth type, key-id e stato.'),
    ],
    'summary': {
        'labels': ['Framework L1→L5', 'E1 vs E2', 'Debug Selettivo'],
        'bodies': [
            'Fisica → adiacenza → LSDB → RIB → forwarding. Non saltare livelli.',
            'E2 metrica piatta (default); E1 cumulativa. Usare E1 quando la topologia interna conta.',
            'debug ip ospf adj/hello + undebug all. show ip ospf neighbor detail = primo posto dove guardare.',
        ],
    },
}

# ─── MOD-05 ───────────────────────────────────────────────────────────────────
MODULES['MOD-05'] = {
    'title': 'BGP Fondamenta',
    'area': 'AREA 2 — BGP', 'hours': '2h', 'codes': '3.2.c · 1.11.a · 1.11.b',
    'agenda': [
        'BGP: Autonomous System e sessioni eBGP/iBGP',
        'iBGP full-mesh: update-source e next-hop-self',
        'BGP network statement e Origin attribute',
        'Processo di selezione best-path BGP',
        'Prefix-list e route-map come filtri',
        'Troubleshooting peering BGP',
    ],
    'topology': {
        'title': 'Topologia MOD-05 — BGP Multi-AS',
        'caption': 'AS 65001 (ISP): R1-R2-R3 iBGP full-mesh. AS 65000 (Customer): R4-R5-R6. eBGP: R1↔R4 e R3↔R5.',
        'nodes': [
            ('R1\nAS 65001\nBorder', 0.15, 0.3),
            ('R2\nAS 65001\nInternal', 0.35, 0.5),
            ('R3\nAS 65001\nBorder', 0.55, 0.3),
            ('R4\nAS 65000\nBorder', 0.15, 0.7),
            ('R5\nAS 65000\nBorder', 0.55, 0.7),
            ('R6\nAS 65000\nInternal', 0.85, 0.5),
        ],
    },
    'sections': [
        {
            'section': 'BGP Fondamenta',
            'subtitle': 'Il protocollo di routing di Internet',
            'slides': [
                {
                    'type': 'teoria',
                    'title': 'BGP — Autonomous System e Sessioni',
                    'points': [
                        'BGP: Border Gateway Protocol — routing inter-AS (EGP), path vector protocol',
                        'AS (Autonomous System): insieme di reti sotto un\'unica amministrazione, numero 16/32-bit',
                        'eBGP: sessione tra router in AS diversi — tipicamente link diretto, TTL=1',
                        'iBGP: sessione tra router nello stesso AS — tipicamente via loopback, no TTL limit',
                        'TCP port 179: BGP usa TCP come transport — no hello periodici, keepalive ogni 60s',
                        'BGP non scopre la topologia: riceve prefissi con path attributes da peer',
                    ],
                    'key': 'eBGP = tra AS diversi. iBGP = stesso AS via loopback. BGP è path vector, non distance vector.',
                },
                {
                    'type': 'teoria',
                    'title': 'iBGP Full-Mesh: update-source e next-hop-self',
                    'points': [
                        'iBGP full-mesh: ogni router deve avere sessione con tutti gli altri (N*(N-1)/2)',
                        'update-source Loopback0: usa loopback come sorgente TCP — più stabile di un indirizzo fisico',
                        'Problema next-hop iBGP: il next-hop di una rotta eBGP non cambia in iBGP',
                        'next-hop-self: forza il router a diventare next-hop per i prefissi annunciati agli iBGP peer',
                        'IBGP split-horizon: un router iBGP non ri-annuncia prefissi appresi da iBGP ad altri iBGP',
                        'Soluzione full-mesh: Route Reflector (MOD-07) o Confederation per grandi AS',
                    ],
                    'key': 'Sempre: update-source Lo0 + next-hop-self su ogni iBGP neighbor che non ha visibilità diretta.',
                },
                {
                    'type': 'teoria',
                    'title': 'BGP Best-Path Selection — Regole',
                    'points': [
                        '1. Weight (Cisco proprietario): più alto vince — locale al router, non propagato',
                        '2. Local Preference: più alto vince — propagato in iBGP, controlla traffico uscente',
                        '3. Locally originated: network/redistribute/aggregate preferito su appreso',
                        '4. AS-Path length: più corto vince',
                        '5. Origin: IGP (i) < EGP (e) < Incomplete (?)',
                        '6. MED: più basso vince — suggerisce al peer l\'exit point preferito (entrante)',
                    ],
                    'key': 'Mnemonico: "We Love Oranges As Oranges Mean Pure Refreshment" — Weight, LP, Locally originated...',
                },
            ],
        },
    ],
    'config_section': {
        'slides': [
            {
                'type': 'config',
                'title': 'BGP iBGP Full-Mesh — Configurazione Base',
                'lines': [
                    'router bgp 65000',
                    ' bgp router-id 4.4.4.4',
                    ' bgp log-neighbor-changes',
                    ' neighbor 5.5.5.5 remote-as 65000      ! iBGP',
                    ' neighbor 5.5.5.5 update-source Lo0    ! stabilità',
                    ' neighbor 5.5.5.5 next-hop-self        ! fix next-hop',
                    ' neighbor 172.16.14.1 remote-as 65001  ! eBGP',
                    ' !',
                    ' address-family ipv4',
                    '  network 4.4.4.4 mask 255.255.255.255 ! annuncia loopback',
                    '  neighbor 5.5.5.5 activate',
                    '  neighbor 172.16.14.1 activate',
                ],
                'device': 'R4', 'hl': 4,
            },
            {
                'type': 'verifica',
                'title': 'Verifica BGP Peering',
                'lines': [
                    'R4# show bgp summary',
                    'Neighbor      V  AS    MsgRcvd  MsgSent  Up/Down   State/PfxRcd',
                    '5.5.5.5       4  65000     150     148  01:22:14         3',
                    '172.16.14.1   4  65001      88      90  00:45:30         5',
                    '',
                    'R4# show bgp ipv4 unicast 100.0.0.1',
                    'BGP routing table entry for 100.0.0.0/8',
                    '  100.0.0.0/8, from 172.16.14.1, Origin IGP, metric 0, localpref 100',
                    '  Path: 65001',
                ],
                'hl': 2,
            },
        ],
    },
    'trouble': [
        ('Sessione BGP in ACTIVE', 'TCP non raggiunge il peer — verificare routing verso update-source, ACL, TTL eBGP'),
        ('Prefisso non appare nel BGP table', 'network statement: il prefisso deve esistere nel RIB locale con la maschera esatta'),
        ('Next-hop non raggiungibile in iBGP', 'Manca next-hop-self sul border router — il next-hop eBGP non è noto internamente'),
        ('Prefisso appresto da iBGP non ri-annunciato', 'iBGP split-horizon — serve full-mesh o Route Reflector'),
    ],
    'exam_tips': [
        'update-source Loopback0 + next-hop-self: coppia inseparabile per iBGP corretto',
        'BGP usa TCP 179 — se la sessione non sale, prima verificare connettività TCP',
        'network statement BGP: il prefisso DEVE esistere nel RIB con maschera esatta',
        'Local Preference (default 100): più alto = preferito. Controlla traffico USCENTE dall\'AS.',
    ],
    'exam_qa': [
        ('Perché next-hop-self è necessario in iBGP?',
         'Il next-hop eBGP non cambia in iBGP: i router interni non sanno raggiungere il next-hop esterno.'),
        ('Differenza tra Weight e Local Preference?',
         'Weight: Cisco only, locale al router, non propagato. Local-Pref: propagato in iBGP, condiviso nell\'AS.'),
    ],
    'summary': {
        'labels': ['eBGP vs iBGP', 'update-source + NH-self', 'Best-Path'],
        'bodies': [
            'eBGP: AS diversi, TTL=1. iBGP: stesso AS, via loopback, no TTL limit, split-horizon.',
            'iBGP via loopback richiede: update-source Lo0 (stabilità) + next-hop-self (next-hop accessibile).',
            'Weight → LP → Local → AS-Path → Origin → MED. LP controlla uscita; AS-Path controlla entrata.',
        ],
    },
}

# ─── MOD-06 ───────────────────────────────────────────────────────────────────
MODULES['MOD-06'] = {
    'title': 'BGP Traffic Engineering',
    'area': 'AREA 2 — BGP', 'hours': '2h', 'codes': '1.11.c · 1.11.d · 1.11.e',
    'agenda': [
        'Default route da ISP: network vs default-originate',
        'Local Preference per controllare traffico uscente',
        'AS-Path Prepend per controllare traffico entrante',
        'BGP Community: comunicazione policy inter-AS',
        'MED: suggerire entry-point preferito al peer',
    ],
    'topology': {
        'title': 'Topologia MOD-06 — BGP Traffic Engineering',
        'caption': 'AS 65000 (Customer) dual-homed: R4↔R1 primario, R5↔R3 secondario. TE con LP e AS-Path Prepend.',
        'nodes': [
            ('R1\nAS 65001\nPrimario', 0.2, 0.2),
            ('R3\nAS 65001\nSecondario', 0.7, 0.2),
            ('R4\nAS 65000\nBorder Prim', 0.2, 0.7),
            ('R5\nAS 65000\nBorder Sec', 0.7, 0.7),
            ('R6\nAS 65000\nInternal', 0.5, 0.5),
        ],
    },
    'sections': [
        {
            'section': 'BGP Traffic Engineering',
            'subtitle': 'Controllare il flusso del traffico in e out',
            'slides': [
                {
                    'type': 'teoria',
                    'title': 'Local Preference — Traffico Uscente',
                    'points': [
                        'Local Preference: attributo well-known discretionary, propagato solo in iBGP',
                        'Valore default: 100. Più alto = preferito per il traffico uscente dall\'AS',
                        'Usa route-map per impostare LP: neighbor X route-map SET-LP in',
                        'Scenario: link primario LP=200, link secondario LP=50 → tutto esce dal primario',
                        'Failover automatico: se LP=200 cade, LP=50 diventa best path',
                        'LP influenza solo il traffico uscente dall\'AS (OUTBOUND)',
                    ],
                    'key': 'Local Preference: alto = preferito per uscita. Configurato INBOUND sul border router.',
                },
                {
                    'type': 'teoria',
                    'title': 'AS-Path Prepend — Traffico Entrante',
                    'points': [
                        'AS-Path: lista di AS attraversati — più corto = preferito dalla selezione BGP standard',
                        'AS-Path Prepend: aggiunge ripetizioni del proprio AS nel path annunciato',
                        'Effetto: il path artificialmente più lungo viene sfavorito dai peer',
                        'Sintassi route-map: set as-path prepend <AS> <AS> <AS> (ripetizioni)',
                        'Configurato OUTBOUND sul border router che vuole sfavorire quel link',
                        'Influenza il traffico ENTRANTE nell\'AS (peer vede path più lungo)',
                    ],
                    'key': 'AS-Path Prepend: rendere un path più lungo per dirottare il traffico entrante sul link preferito.',
                },
                {
                    'type': 'teoria',
                    'title': 'BGP Community — Policy Inter-AS',
                    'points': [
                        'Community: tag 32-bit (AA:NN) applicato ai prefissi BGP — comunicazione di policy',
                        'Community well-known: NO_EXPORT (non uscire dall\'AS), NO_ADVERTISE (non annunciare)',
                        'Community custom: accordo bilaterale tra AS per comunicare preferenze',
                        'Uso tipico: ISP offre community 65001:100=preferenza alta, 65001:50=bassa',
                        'Il Customer tagga i prefissi con la community ISP per influenzare routing',
                        'send-community: obbligatorio nella neighbor config (default: community non trasmessa)',
                    ],
                    'key': 'Community = etichetta su un prefisso BGP per comunicare policy tra AS — send-community obbligatorio.',
                },
            ],
        },
    ],
    'config_section': {
        'slides': [
            {
                'type': 'config',
                'title': 'Local Preference + AS-Path Prepend',
                'lines': [
                    '! Local Pref sul link primario (R4)',
                    'route-map SET-LP-HIGH permit 10',
                    ' set local-preference 200',
                    'router bgp 65000',
                    ' neighbor 172.16.14.1 route-map SET-LP-HIGH in',
                    '!',
                    '! AS-Path Prepend sul link secondario (R5)',
                    'route-map PREPEND-SECONDARY permit 10',
                    ' set as-path prepend 65000 65000',
                    'router bgp 65000',
                    ' neighbor 172.16.35.1 route-map PREPEND-SECONDARY out',
                ],
                'device': 'R4/R5', 'hl': 2,
            },
        ],
    },
    'trouble': [
        ('LP non cambia best path', 'LP cambia ma serve clear ip bgp soft — oppure route-map non matchata'),
        ('AS-Path Prepend non ha effetto', 'send-community mancante o route-map non applicata outbound'),
        ('Community non propagata al peer', 'Manca neighbor X send-community — default: community non inviata'),
        ('Default route non ricevuta', 'neighbor X default-originate sul provider, oppure network 0.0.0.0 nel RIB'),
    ],
    'exam_tips': [
        'Local Preference (alto = preferito) controlla traffico USCENTE — configurato inbound sul border',
        'AS-Path Prepend (path lungo = sfavorito) controlla traffico ENTRANTE — configurato outbound',
        'Community: send-community deve essere esplicito nella neighbor config',
        'MED: più basso = preferito — suggerisce al peer il punto di ingresso preferito (solo tra stesso AS)',
    ],
    'exam_qa': [
        ('Come far uscire tutto il traffico dal link primario?',
         'Local Preference alta (es. 200) sul link primario con route-map in inbound.'),
        ('Come far entrare il traffico dal link primario?',
         'AS-Path Prepend sul link secondario (outbound) — path più lungo = sfavorito dal peer.'),
    ],
    'summary': {
        'labels': ['Local Preference', 'AS-Path Prepend', 'BGP Community'],
        'bodies': [
            'LP alto = uscita preferita. Configurato inbound sul border. Propagato in iBGP nell\'AS.',
            'Prepend = path lungo = sfavorito. Configurato outbound. Influenza traffico entrante.',
            'Community = etichetta policy. send-community obbligatorio. NO_EXPORT, NO_ADVERTISE built-in.',
        ],
    },
}

# ─── MOD-07 ───────────────────────────────────────────────────────────────────
MODULES['MOD-07'] = {
    'title': 'BGP Route Reflector & IPv6 BGP',
    'area': 'AREA 2 — BGP', 'hours': '1.5h', 'codes': '1.11.d',
    'agenda': [
        'Problema del full-mesh iBGP: scalabilità',
        'Route Reflector: cluster e RR client',
        'BGP Confederation: alternativa al RR',
        'MP-BGP: address-family per IPv6',
        'Exam Tips e riepilogo scaling BGP',
    ],
    'topology': {
        'title': 'Topologia MOD-07 — Route Reflector',
        'caption': 'RR centrale connesso a 4 RR-client. Senza RR: 10 sessioni iBGP. Con RR: 4 sessioni.',
        'nodes': [
            ('RR\nRoute Reflector', 0.5, 0.5),
            ('Client1', 0.15, 0.2),
            ('Client2', 0.85, 0.2),
            ('Client3', 0.15, 0.8),
            ('Client4', 0.85, 0.8),
        ],
    },
    'sections': [
        {
            'section': 'Route Reflector',
            'subtitle': 'Eliminare il full-mesh iBGP',
            'slides': [
                {
                    'type': 'teoria',
                    'title': 'Il Problema del Full-Mesh iBGP',
                    'points': [
                        'iBGP split-horizon: un router non ri-annuncia prefix iBGP ad altri peer iBGP',
                        'Soluzione originale: full-mesh — ogni router ha sessione con tutti (N*(N-1)/2)',
                        'Con 100 router: 4950 sessioni BGP — non scalabile in grandi AS',
                        'Route Reflector (RR): può ri-annunciare prefix iBGP ai client — viola split-horizon in modo controllato',
                        'Confederation: divide l\'AS in sotto-AS (sub-AS) — eBGP interno tra sub-AS',
                        'RR è lo standard moderno; Confederation più raro, usata in grosse telco',
                    ],
                    'key': 'RR risolve il full-mesh iBGP: il RR ri-annuncia prefix ai client — da N*(N-1)/2 a N sessioni.',
                },
                {
                    'type': 'teoria',
                    'title': 'Route Reflector — Cluster e Regole',
                    'points': [
                        'RR cluster: uno o più RR + i loro client — identificato da cluster-id',
                        'Client → RR: RR riflette a tutti gli altri client e ai non-client iBGP',
                        'Non-client → RR: RR riflette solo ai client (non ad altri non-client)',
                        'Cluster-list: attributo aggiunto dal RR per prevenire loop tra RR multipli',
                        'Originator-ID: RR aggiunge l\'ID del router originante per prevenire loop',
                        'Configurazione: neighbor X route-reflector-client sull\'RR',
                    ],
                    'key': 'RR aggiunge cluster-list e originator-id per prevenire loop — trasparente ai client.',
                },
                {
                    'type': 'teoria',
                    'title': 'MP-BGP — Multi-Protocol BGP per IPv6',
                    'points': [
                        'MP-BGP (RFC 4760): estende BGP per portare NLRI di famiglie diverse da IPv4',
                        'address-family ipv6 unicast: abilita il trasporto di prefissi IPv6 in BGP',
                        'I session BGP stessi (TCP 179) — solo i NLRI cambiano address-family',
                        'Neighbor per IPv6: usa indirizzo IPv6 o loopback IPv4 con activate in af ipv6',
                        'next-hop per IPv6: il next-hop nella af ipv6 è un indirizzo IPv6',
                        'VPNv4, VPNv6, L2VPN: tutte le varianti MPLS usano MP-BGP',
                    ],
                    'key': 'MP-BGP = una sessione TCP porta NLRI di più famiglie. address-family seleziona il tipo.',
                },
            ],
        },
    ],
    'config_section': {
        'slides': [
            {
                'type': 'config',
                'title': 'Route Reflector — Configurazione',
                'lines': [
                    'router bgp 65000',
                    ' bgp router-id 10.0.0.1',
                    ' ! Sessioni verso i client',
                    ' neighbor 1.1.1.1 remote-as 65000',
                    ' neighbor 1.1.1.1 update-source Lo0',
                    ' neighbor 1.1.1.1 route-reflector-client   ! questo è client',
                    ' neighbor 2.2.2.2 remote-as 65000',
                    ' neighbor 2.2.2.2 update-source Lo0',
                    ' neighbor 2.2.2.2 route-reflector-client',
                    ' ! Non-client: sessione normale (no rr-client)',
                    ' neighbor 3.3.3.3 remote-as 65000',
                ],
                'device': 'RR', 'hl': 5,
            },
        ],
    },
    'trouble': [
        ('Loop BGP con RR multipli', 'Manca cluster-id configurato uguale su RR ridondanti dello stesso cluster'),
        ('Client non riceve prefissi da altri client', 'RR non ha route-reflector-client configurato su tutti i client'),
        ('MP-BGP IPv6: no prefix nella table', 'neighbor non activato in address-family ipv6 unicast'),
        ('Sessione RR non si forma', 'update-source mancante — RR deve raggiungere il loopback del client'),
    ],
    'exam_tips': [
        'RR evita il full-mesh: route-reflector-client sul RR — il client non sa di essere reflectato',
        'cluster-id su RR ridondanti evita loop — stessa cluster-id su tutti gli RR dello stesso cluster',
        'MP-BGP: address-family ipv6 unicast + neighbor X activate — stessa sessione TCP, diversi NLRI',
        'Confederation: sub-AS con eBGP interno — alternativa più complessa al RR',
    ],
    'exam_qa': [
        ('Perché il Route Reflector non rompe la regola split-horizon?',
         'RR aggiunge cluster-list e originator-id — i loop vengono rilevati e i prefix scartati.'),
        ('Differenza tra RR e Confederation?',
         'RR: singolo AS, client trasparenti, più semplice. Confederation: divide in sub-AS con eBGP interno.'),
    ],
    'summary': {
        'labels': ['Full-mesh → RR', 'Cluster + Loop Prev.', 'MP-BGP'],
        'bodies': [
            'RR risolve scalabilità iBGP: da N*(N-1)/2 a N sessioni. route-reflector-client sul RR.',
            'cluster-list + originator-id prevengono loop. RR ridondanti: stesso cluster-id.',
            'MP-BGP porta IPv6, VPNv4, L2VPN in BGP. address-family + neighbor activate.',
        ],
    },
}

# ─── MOD-08 ───────────────────────────────────────────────────────────────────
MODULES['MOD-08'] = {
    'title': 'Redistribuzione BGP↔OSPF & Prefix Filtering',
    'area': 'AREA 3 — ROUTE MANIPULATION', 'hours': '2h', 'codes': '1.3 · 1.4 · 1.5 · 3.2.d',
    'agenda': [
        'Prefix-list: filtrare prefissi per lunghezza',
        'Route-map: strumento universale di manipolazione',
        'Redistribuzione OSPF→BGP e BGP→OSPF',
        'Loop di redistribuzione e route tagging',
        'Route-map in redistribuzione vs BGP neighbor policy',
    ],
    'topology': {
        'title': 'Topologia MOD-08 — Redistribuzione Multi-AS',
        'caption': 'CORE: punto di redistribuzione BGP↔OSPF. WAN-A/WAN-B: dual-homed. LAN-A/LAN-B: solo OSPF.',
        'nodes': [
            ('ISP-A\nAS 100', 0.08, 0.3),
            ('WAN-A\nAS 65001', 0.25, 0.3),
            ('CORE\nAS 65000', 0.5, 0.5),
            ('WAN-B\nAS 65002', 0.75, 0.3),
            ('ISP-B\nAS 200', 0.92, 0.3),
            ('LAN-A\nOSPF', 0.35, 0.75),
            ('LAN-B\nOSPF', 0.65, 0.75),
        ],
    },
    'sections': [
        {
            'section': 'Prefix-List e Route-Map',
            'subtitle': 'Strumenti fondamentali di policy routing',
            'slides': [
                {
                    'type': 'teoria',
                    'title': 'Prefix-List — Filtrare per Rete e Lunghezza',
                    'points': [
                        'Prefix-list: filtra prefissi IP per network e/o lunghezza maschera',
                        'Sintassi: ip prefix-list NAME [seq N] permit|deny <prefix/len> [ge X] [le Y]',
                        'ge (greater-equal): maschera ≥ ge. le (less-equal): maschera ≤ le',
                        'Esempio: 10.0.0.0/8 ge 24 le 32 → tutti gli host dentro 10.0.0.0/8 con /24-/32',
                        'Più efficiente di una ACL per il filtraggio di routing (valutazione O(1) con PATRICIA tree)',
                        'Implicit deny alla fine — come ACL: aggiungere permit any se necessario',
                    ],
                    'key': 'prefix-list ge/le: filtrare range di maschere in un unico statement. Più preciso delle ACL.',
                },
                {
                    'type': 'teoria',
                    'title': 'Route-Map — Strumento Universale',
                    'points': [
                        'Route-map: serie ordinata di clausole permit/deny con condizioni match e azioni set',
                        'match: ip address (ACL/prefix-list), ip next-hop, tag, metric, route-type...',
                        'set: metric, local-preference, as-path prepend, community, tag, weight...',
                        'Uso: redistribuzione (seleziona cosa redistribuire), BGP (policy neighbor), PBR',
                        'Clausola senza match → matcha tutto (catch-all)',
                        'Implicit deny finale: i prefix non matchati non vengono redistribuiti',
                    ],
                    'key': 'Route-map = IF (match) THEN (set). Implicit deny finale — aggiungere permit 999 se necessario.',
                },
            ],
        },
        {
            'section': 'Redistribuzione e Loop Prevention',
            'subtitle': 'Collegare BGP e OSPF senza loop',
            'slides': [
                {
                    'type': 'teoria',
                    'title': 'Redistribuzione Bidirezionale BGP↔OSPF',
                    'points': [
                        'Redistribuzione OSPF→BGP: redistribute ospf <pid> [route-map FILTER] in router bgp',
                        'Redistribuzione BGP→OSPF: redistribute bgp <AS> subnets [route-map FILTER] in router ospf',
                        'subnets: obbligatorio per redistribuire prefissi con maschera variabile in OSPF',
                        'Problema loop: A redistribuisce BGP→OSPF; B vede la rotta OSPF e la ri-annuncia in BGP',
                        'Soluzione route tagging: set tag su redistribute BGP→OSPF; deny tag in redistribute OSPF→BGP',
                        'Tag è un marcatore 32-bit che viaggia con la rotta e può essere testato con match tag',
                    ],
                    'key': 'Loop redistribuzione BGP↔OSPF: prevenire con route tag. Marcare BGP→OSPF, bloccare OSPF→BGP.',
                },
            ],
        },
    ],
    'config_section': {
        'slides': [
            {
                'type': 'config',
                'title': 'Redistribuzione con Tag Anti-Loop',
                'lines': [
                    '! OSPF: accetta BGP ma marca, blocca tagged OSPF→BGP',
                    'route-map BGP-TO-OSPF permit 10',
                    ' set tag 65000               ! marca rotte BGP in OSPF',
                    'route-map OSPF-TO-BGP deny 10',
                    ' match tag 65000             ! blocca rotte già da BGP',
                    'route-map OSPF-TO-BGP permit 20',
                    '!',
                    'router ospf 1',
                    ' redistribute bgp 65000 subnets route-map BGP-TO-OSPF',
                    'router bgp 65000',
                    ' redistribute ospf 1 route-map OSPF-TO-BGP',
                ],
                'device': 'CORE', 'hl': 3,
            },
        ],
    },
    'trouble': [
        ('Loop di redistribuzione', 'Manca anti-loop con tag — rotte BGP→OSPF→BGP si amplificano'),
        ('Rotte non redistribuite in OSPF', 'Manca subnets nella redistribuzione OSPF — solo classful redistribuito senza'),
        ('Prefix-list blocca tutto', 'Implicit deny finale — verificare il deny/permit dell\'ultima clausola'),
        ('Route-map non matcha', 'match ip address usa ACL o prefix-list — verificare che il nome corrisponda'),
    ],
    'exam_tips': [
        'redistribute bgp X subnets: subnets obbligatorio per redistribuire prefissi VLSM in OSPF',
        'Loop BGP↔OSPF: set tag in redistribuzione + match tag in deny per prevenire rientro',
        'prefix-list ge/le: filtra range di maschere — più preciso ed efficiente di ACL estesa',
        'Route-map implicit deny: senza permit finale, tutto viene bloccato',
    ],
    'exam_qa': [
        ('Perché subnets è necessario in redistribute bgp into OSPF?',
         'Senza subnets, OSPF redistribuisce solo rotte classful (legacy). Con subnets: tutto incluso VLSM.'),
        ('Come prevenire loop in redistribuzione bidirezionale?',
         'Marcare rotte BGP→OSPF con set tag. Bloccare in OSPF→BGP con match tag + deny.'),
    ],
    'summary': {
        'labels': ['Prefix-List ge/le', 'Route-Map IF/THEN', 'Anti-Loop Tag'],
        'bodies': [
            'prefix-list filtra per network + lunghezza maschera. ge/le per range. Più efficiente di ACL.',
            'Route-map: match (condizione) + set (azione). Implicit deny finale.',
            'Loop BGP↔OSPF: set tag in BGP→OSPF. match tag + deny in OSPF→BGP.',
        ],
    },
}

# ─── MOD-09 ───────────────────────────────────────────────────────────────────
MODULES['MOD-09'] = {
    'title': 'PBR & Route Manipulation Avanzata',
    'area': 'AREA 3 — ROUTE MANIPULATION', 'hours': '2h', 'codes': '1.2 · 1.6 · 3.2.d',
    'agenda': [
        'Policy-Based Routing (PBR): routing per sorgente',
        'ip route-map e set ip next-hop verify-availability',
        'Administrative Distance: preferenza protocolli',
        'Floating static route: backup condizionale',
        'IP SLA + Object Tracking: rotte condizionali',
    ],
    'topology': {
        'title': 'Topologia MOD-09 — PBR Guest vs Produzione',
        'caption': 'LAN-A: rete prod (10.10.0.0) via WAN-A; rete guest (10.99.0.0) forzata via WAN-B con PBR su CORE.',
        'nodes': [
            ('ISP-A\nAS 100', 0.08, 0.3),
            ('WAN-A\nAS 65001', 0.25, 0.3),
            ('CORE\nPBR qui', 0.5, 0.5),
            ('WAN-B\nAS 65002', 0.75, 0.3),
            ('ISP-B\nAS 200', 0.92, 0.3),
            ('LAN-A\nprod+guest', 0.3, 0.75),
        ],
    },
    'sections': [
        {
            'section': 'Policy-Based Routing',
            'subtitle': 'Routing basato su policy anziché destinazione',
            'slides': [
                {
                    'type': 'teoria',
                    'title': 'PBR — Routing per Sorgente (e non solo)',
                    'points': [
                        'PBR bypassa la routing table normale per il traffico matchato',
                        'Match: ip address (ACL che seleziona il traffico) — per IP sorgente, destinazione, DSCP...',
                        'set ip next-hop: forza il next-hop per il traffico matchato',
                        'set ip next-hop verify-availability: verifica che il next-hop sia raggiungibile via IP SLA',
                        'Applicato INBOUND sull\'interfaccia verso la sorgente: ip policy route-map NAME',
                        'Uso tipico: traffico guest→ISP-B, traffico prod→ISP-A su stesso router',
                    ],
                    'key': 'PBR = routing basato su attributi arbitrari del pacchetto — applicato inbound sull\'ingresso traffico.',
                },
            ],
        },
        {
            'section': 'Administrative Distance e IP SLA',
            'subtitle': 'Preferenza protocolli e rotte condizionali',
            'slides': [
                {
                    'type': 'teoria',
                    'title': 'Administrative Distance — Preferenza Protocolli',
                    'points': [
                        'AD: valore 0-255, più basso = più fidato — usato per scegliere tra protocolli diversi',
                        'AD default: Connected=0, Static=1, EIGRP summary=5, OSPF=110, IS-IS=115, RIP=120',
                        'Floating static route: static con AD > protocollo dinamico (es. AD=200 vs OSPF=110)',
                        'Quando OSPF è attivo → OSPF installa la rotta. OSPF cade → static emerge',
                        'Modifica AD: ip route 0.0.0.0 0.0.0.0 10.0.0.1 200 (AD 200)',
                        'Utile per backup con failover automatico senza dover monitorare protocolli',
                    ],
                    'key': 'Floating static: AD più alto del protocollo dinamico — appare nel RIB solo se il protocollo cade.',
                },
                {
                    'type': 'teoria',
                    'title': 'IP SLA + Object Tracking',
                    'points': [
                        'IP SLA: sonda proattiva (ICMP echo, UDP jitter, HTTP...) verso un target',
                        'Risultato: UP se la sonda ha successo, DOWN se fallisce (configurable thresholds)',
                        'Object Tracking: traccia stato di un SLA, interfaccia o route',
                        'Rotta condizionale: ip route 0.0.0.0 ... track 1 — installata solo se track 1 = UP',
                        'Combinazione con PBR: set ip next-hop verify-availability usa track object implicito',
                        'Frequenza sonda: ip sla schedule — configurare probe frequency e react threshold',
                    ],
                    'key': 'IP SLA + track: rotta installata condizionalmente. PBR verify-availability: next-hop testato live.',
                },
            ],
        },
    ],
    'config_section': {
        'slides': [
            {
                'type': 'config',
                'title': 'PBR Guest Traffic',
                'lines': [
                    'ip access-list extended GUEST-TRAFFIC',
                    ' permit ip 10.99.0.0 0.0.0.255 any',
                    '!',
                    'route-map PBR-GUEST permit 10',
                    ' match ip address GUEST-TRAFFIC',
                    ' set ip next-hop verify-availability 10.0.23.1 1 track 10',
                    '!',
                    '! IP SLA per verificare WAN-B',
                    'ip sla 10',
                    ' icmp-echo 10.0.23.1',
                    'ip sla schedule 10 life forever start-time now',
                    'track 10 ip sla 10 reachability',
                ],
                'device': 'CORE', 'hl': 5,
            },
        ],
    },
    'trouble': [
        ('PBR non ha effetto', 'ip policy route-map non applicato inbound sull\'interfaccia corretta'),
        ('next-hop verify-availability fallisce', 'Track non configurato o SLA non schedulato — verify-availability richiede track object'),
        ('Floating static non emerge', 'AD della static NON è maggiore del protocollo dinamico — verificare valore AD'),
        ('IP SLA sempre DOWN', 'Target non raggiungibile o frequenza probe troppo bassa — verificare routing e sla schedule'),
    ],
    'exam_tips': [
        'PBR applicato INBOUND: ip policy route-map sull\'interfaccia di ingresso del traffico',
        'Floating static: AD > protocollo dinamico. OSPF=110 → static AD=150 per backup',
        'IP SLA: proattivo — rileva il fallimento PRIMA che OSPF/BGP convergano',
        'verify-availability nel PBR usa implicitamente un track object per testare il next-hop',
    ],
    'exam_qa': [
        ('Come forzare traffico da una subnet specifica verso un next-hop diverso dalla routing table?',
         'PBR: ACL seleziona la subnet + route-map con set ip next-hop + ip policy inbound sull\'interfaccia.'),
        ('Quando una floating static route viene installata nel RIB?',
         'Solo quando il protocollo con AD inferiore non ha più la rotta — floating static emerge automaticamente.'),
    ],
    'summary': {
        'labels': ['PBR Inbound', 'Floating Static', 'IP SLA + Track'],
        'bodies': [
            'PBR matcha ACL + set next-hop. Applicato inbound. Bypassa routing table per traffico selezionato.',
            'AD floating > protocollo: backup automatico. OSPF cade → static emerge. Zero configurazione manuale.',
            'IP SLA proba il next-hop. track object condiziona rotte e PBR. Failover pre-routing.',
        ],
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def generate_module(mod_id):
    content = MODULES.get(mod_id)
    if not content:
        print(f"  [SKIP] {mod_id} — contenuto non ancora definito")
        return 0
    out_dir = mod_id
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{mod_id}_slide.pptx")
    prs = make_deck(mod_id, content)
    prs.save(out_path)
    n = len(prs.slides)
    print(f"  [OK] {out_path}  ({n} slide)")
    return n


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else None
    all_ids = [f"MOD-{i:02d}" for i in range(1, 36)]
    to_gen = [target] if target else all_ids

    total = 0
    for mod_id in to_gen:
        total += generate_module(mod_id)

    print(f"\n[DONE] Totale slide generate: {total}")


if __name__ == "__main__":
    main()
