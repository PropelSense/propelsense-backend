"""
Report Service
Generates PDF reports using fpdf2
"""
from fpdf import FPDF
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.prediction_history import PredictionHistory
from app.models.sea_trial import SeaTrial
import logging

logger = logging.getLogger(__name__)

# ── Unicode → ASCII sanitiser (Helvetica only supports latin-1) ───────────────
_CHAR_MAP = {
    "\u2013": "-",   # en-dash
    "\u2014": "-",   # em-dash
    "\u2015": "-",   # horizontal bar
    "\u00b7": "|",   # middle dot
    "\u2018": "'",   # left single quote
    "\u2019": "'",   # right single quote
    "\u201c": '"',   # left double quote
    "\u201d": '"',   # right double quote
    "\u2026": "...", # ellipsis
    "\u00d7": "x",   # multiplication sign
    "\u00b0": "deg", # degree sign
}

def _safe(text) -> str:
    """Replace characters unsupported by Helvetica (latin-1) with ASCII equivalents."""
    s = str(text)
    for ch, repl in _CHAR_MAP.items():
        s = s.replace(ch, repl)
    # Final fallback: drop anything still outside latin-1
    return s.encode("latin-1", errors="replace").decode("latin-1")

# ── Colour palette (RGB) ───────────────────────────────────────────────────────
C_BG        = (18, 18, 20)      # near-black page
C_PANEL     = (36, 36, 40)      # card background
C_ACCENT    = (59, 130, 246)    # blue-500
C_TEXT      = (228, 228, 231)   # zinc-200
C_MUTED     = (113, 113, 122)   # zinc-500
C_BORDER    = (63, 63, 70)      # zinc-700
C_WHITE     = (255, 255, 255)
C_GREEN     = (52, 211, 153)    # emerald-400
C_AMBER     = (251, 191, 36)    # amber-400


class PropelSensePDF(FPDF):
    """Base PDF with PropelSense branding."""

    def __init__(self, subtitle: str = ""):
        super().__init__()
        self.subtitle = subtitle
        self.set_auto_page_break(auto=True, margin=18)

    def header(self):
        # Dark header bar
        self.set_fill_color(*C_BG)
        self.rect(0, 0, 210, 22, "F")

        # Accent stripe
        self.set_fill_color(*C_ACCENT)
        self.rect(0, 0, 210, 2, "F")

        # Brand name
        self.set_xy(10, 5)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(*C_WHITE)
        self.cell(60, 8, "PropelSense", ln=False)

        # Subtitle (report title)
        if self.subtitle:
            self.set_font("Helvetica", "", 9)
            self.set_text_color(*C_MUTED)
            self.set_xy(72, 7)
            self.cell(100, 6, self.subtitle, ln=False)

        # Page number (right)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*C_MUTED)
        self.set_xy(160, 7)
        self.cell(40, 6, f"Page {self.page_no()}", align="R", ln=False)

        self.ln(14)

    def footer(self):
        self.set_y(-12)
        self.set_fill_color(*C_BG)
        self.rect(0, self.get_y() - 2, 210, 14, "F")
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*C_MUTED)
        self.cell(0, 6, f"Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}  |  AI-Powered Vessel Propulsion Intelligence", align="C")

    # ── Helpers ──────────────────────────────────────────────────────────────
    def section_title(self, text: str):
        """Render a section heading with an accent underline."""
        self.ln(4)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*C_TEXT)
        self.cell(0, 7, _safe(text), ln=True)
        self.set_draw_color(*C_ACCENT)
        self.set_line_width(0.4)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def stat_card(self, x: float, y: float, w: float, h: float, label: str, value: str):
        """Render a small stat box."""
        self.set_fill_color(*C_PANEL)
        self.set_draw_color(*C_BORDER)
        self.set_line_width(0.3)
        self.rect(x, y, w, h, "FD")

        self.set_xy(x + 3, y + 3)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*C_MUTED)
        self.cell(w - 6, 5, _safe(label), ln=True)

        self.set_xy(x + 3, y + 8)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*C_WHITE)
        self.cell(w - 6, 7, _safe(value), ln=True)

    def table_header(self, cols: list[tuple[str, float]]):
        """cols = list of (label, width)"""
        self.set_fill_color(*C_PANEL)
        self.set_font("Helvetica", "B", 7)
        self.set_text_color(*C_MUTED)
        self.set_draw_color(*C_BORDER)
        self.set_line_width(0.2)
        for label, w in cols:
            self.cell(w, 6, label.upper(), border=1, fill=True)
        self.ln()

    def table_row(self, values: list[tuple[str, float]], zebra: bool = False):
        """values = list of (text, width)"""
        if zebra:
            self.set_fill_color(30, 30, 34)
        else:
            self.set_fill_color(*C_BG)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*C_TEXT)
        self.set_draw_color(*C_BORDER)
        self.set_line_width(0.2)
        for text, w in values:
            self.cell(w, 5.5, _safe(text)[:28], border=1, fill=True)
        self.ln()


# ── Report generators ─────────────────────────────────────────────────────────

def generate_prediction_summary(db: Session, user_id: str, user_email: str) -> bytes:
    """Generate a PDF summarising the user's prediction history."""

    records: list[PredictionHistory] = (
        db.query(PredictionHistory)
        .filter(PredictionHistory.user_id == user_id)
        .order_by(PredictionHistory.created_at.desc())
        .limit(100)
        .all()
    )

    total = len(records)
    powers = [r.predicted_power_kw for r in records if r.predicted_power_kw is not None]
    avg_kw  = sum(powers) / len(powers) if powers else 0
    max_kw  = max(powers) if powers else 0
    min_kw  = min(powers) if powers else 0

    pdf = PropelSensePDF(subtitle="Power Prediction Summary")
    pdf.set_fill_color(*C_BG)
    pdf.add_page()
    pdf.rect(0, 0, 210, 297, "F")   # dark page fill

    # ── Meta block ────────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*C_WHITE)
    pdf.cell(0, 10, "Power Prediction Summary Report", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*C_MUTED)
    pdf.cell(0, 5, f"User: {user_email}   |   Generated: {datetime.utcnow().strftime('%d %b %Y, %H:%M UTC')}", ln=True)
    pdf.ln(4)

    # ── Stat cards ────────────────────────────────────────────────────────────
    pdf.section_title("Summary Statistics")
    y = pdf.get_y()
    card_w, card_h, gap = 44, 20, 3
    x0 = 10
    pdf.stat_card(x0,           y, card_w, card_h, "TOTAL PREDICTIONS",     str(total))
    pdf.stat_card(x0 + card_w + gap,   y, card_w, card_h, "AVG POWER",      f"{avg_kw:,.0f} kW")
    pdf.stat_card(x0 + (card_w + gap)*2, y, card_w, card_h, "MAX POWER",    f"{max_kw:,.0f} kW")
    pdf.stat_card(x0 + (card_w + gap)*3, y, card_w, card_h, "MIN POWER",    f"{min_kw:,.0f} kW")
    pdf.set_y(y + card_h + 6)

    # ── Table ─────────────────────────────────────────────────────────────────
    pdf.section_title(f"Prediction Records (last {total})")

    cols = [
        ("#",        8),
        ("Date",    32),
        ("STW (kn)", 22),
        ("Wave (m)", 22),
        ("Aft Draft",22),
        ("Fore Draft",22),
        ("Time DryDock",24),
        ("Power (kW)", 28),
    ]
    pdf.table_header(cols)

    for i, r in enumerate(records):
        dt = r.created_at.strftime("%d %b %Y %H:%M") if r.created_at else "-"
        row = [
            (str(i + 1),                  cols[0][1]),
            (dt,                           cols[1][1]),
            (f"{r.stw:.1f}" if r.stw else "-", cols[2][1]),
            (f"{r.comb_wind_swell_wave_height:.2f}" if r.comb_wind_swell_wave_height else "-", cols[3][1]),
            (f"{r.draft_aft_telegram:.2f}" if r.draft_aft_telegram else "-", cols[4][1]),
            (f"{r.draft_fore_telegram:.2f}" if r.draft_fore_telegram else "-", cols[5][1]),
            (f"{r.time_since_dry_dock:.0f} d" if r.time_since_dry_dock else "-", cols[6][1]),
            (f"{r.predicted_power_kw:,.0f}" if r.predicted_power_kw else "-", cols[7][1]),
        ]
        pdf.table_row(row, zebra=(i % 2 == 0))

    if not records:
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(*C_MUTED)
        pdf.cell(0, 8, "No prediction records found.", ln=True)

    return bytes(pdf.output())


def generate_sea_trial_summary(db: Session, user_email: str) -> bytes:
    """Generate a PDF summarising all sea trial records."""

    trials: list[SeaTrial] = (
        db.query(SeaTrial)
        .order_by(SeaTrial.trial_date.desc())
        .limit(100)
        .all()
    )

    total     = len(trials)
    completed = sum(1 for t in trials if str(t.status).lower() in ("completed", "trialstatus.completed"))
    act_powers = [t.actual_power for t in trials if t.actual_power]
    pred_powers = [t.predicted_power for t in trials if t.predicted_power]
    avg_actual  = sum(act_powers)  / len(act_powers)  if act_powers  else 0
    avg_pred    = sum(pred_powers) / len(pred_powers) if pred_powers else 0

    pdf = PropelSensePDF(subtitle="Sea Trial Summary")
    pdf.set_fill_color(*C_BG)
    pdf.add_page()
    pdf.rect(0, 0, 210, 297, "F")

    # ── Meta block ────────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*C_WHITE)
    pdf.cell(0, 10, "Sea Trial Performance Report", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*C_MUTED)
    pdf.cell(0, 5, f"User: {user_email}   |   Generated: {datetime.utcnow().strftime('%d %b %Y, %H:%M UTC')}", ln=True)
    pdf.ln(4)

    # ── Stat cards ────────────────────────────────────────────────────────────
    pdf.section_title("Summary Statistics")
    y = pdf.get_y()
    card_w, card_h, gap = 44, 20, 3
    x0 = 10
    pdf.stat_card(x0,                     y, card_w, card_h, "TOTAL TRIALS",       str(total))
    pdf.stat_card(x0 + card_w + gap,       y, card_w, card_h, "COMPLETED",         str(completed))
    pdf.stat_card(x0 + (card_w+gap)*2,     y, card_w, card_h, "AVG ACTUAL POWER",  f"{avg_actual:,.0f} kW")
    pdf.stat_card(x0 + (card_w+gap)*3,     y, card_w, card_h, "AVG PREDICTED PWR", f"{avg_pred:,.0f} kW")
    pdf.set_y(y + card_h + 6)

    # ── Table ─────────────────────────────────────────────────────────────────
    pdf.section_title(f"Sea Trial Records (last {total})")

    cols = [
        ("#",          8),
        ("Trial Name", 42),
        ("Vessel",     34),
        ("Date",       26),
        ("Status",     20),
        ("Act. Speed", 22),
        ("Act. Power", 24),
        ("Pred. Power",24),
    ]
    pdf.table_header(cols)

    for i, t in enumerate(trials):
        dt     = t.trial_date.strftime("%d %b %Y") if t.trial_date else "-"
        status = str(t.status).split(".")[-1].replace("_", " ").title() if t.status else "-"
        row = [
            (str(i + 1),                    cols[0][1]),
            (t.trial_name or "-",            cols[1][1]),
            (t.vessel_name or "-",           cols[2][1]),
            (dt,                             cols[3][1]),
            (status,                         cols[4][1]),
            (f"{t.actual_speed:.1f} kn" if t.actual_speed else "-", cols[5][1]),
            (f"{t.actual_power:,.0f} kW"  if t.actual_power  else "-", cols[6][1]),
            (f"{t.predicted_power:,.0f} kW" if t.predicted_power else "-", cols[7][1]),
        ]
        pdf.table_row(row, zebra=(i % 2 == 0))

    if not trials:
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(*C_MUTED)
        pdf.cell(0, 8, "No sea trial records found.", ln=True)

    return bytes(pdf.output())
