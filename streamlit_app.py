# =============================================================================
# Audit Pro — Continuous Assurance Platform
# Reto ICJCE 2026 · Demo prototype para presentación a inversionistas
# =============================================================================
# Stack: Streamlit + Plotly + Pandas
# Run:   streamlit run auditflow_pro.py
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import textwrap

# -----------------------------------------------------------------------------
# 1. PAGE CONFIG
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Audit Pro · Auditoria Continua",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Audit Pro · Reto ICJCE 2026 · Auditoría continua asistida por IA"},
)

# -----------------------------------------------------------------------------
# 2. DESIGN TOKENS (única fuente de verdad de color)
# -----------------------------------------------------------------------------
C = {
    "ink":      "#0A0F1C",
    "surface":  "#131A2C",
    "surface2": "#1B2238",
    "line":     "#232B45",
    "line_soft":"#1A2138",
    "text":     "#E8EAF0",
    "dim":      "#8A91A8",
    "faint":    "#5A6178",
    "gold":     "#D4A574",
    "gold_2":   "#B8894F",
    "amber":    "#E8A04A",
    "risk":     "#E5604E",
    "ok":       "#7AB89B",
    "info":     "#6B8FB3",
}

# Referencias profesionales NIA-ES (Normas Internacionales de Auditoría adaptadas a España)
NIA_REFS = {
    "240": "Responsabilidades del auditor en relación con el fraude",
    "315": "Identificación y valoración de los riesgos de incorrección material",
    "320": "Importancia relativa o materialidad",
    "330": "Respuestas del auditor a los riesgos valorados",
    "500": "Evidencia de auditoría",
    "520": "Procedimientos analíticos",
    "530": "Muestreo de auditoría",
    "540": "Auditoría de estimaciones contables",
    "550": "Partes vinculadas",
    "560": "Hechos posteriores al cierre",
}

# -----------------------------------------------------------------------------
# 3. CSS (un único bloque, sin !important salvo donde Streamlit obliga)
# -----------------------------------------------------------------------------
def inject_css():
    st.markdown(textwrap.dedent(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ---------- BASE: BULLETPROOF DARK ---------- */
    /* Todos los contenedores Streamlit deben heredar el oscuro.  */
    /* Esto evita las bandas blancas que aparecen cuando algún    */
    /* contenedor padre tiene fondo claro por defecto.            */
    html, body {{
        background-color: {C['ink']} !important;
        color: {C['text']};
    }}
    .stApp {{
        background-color: {C['ink']} !important;
        color: {C['text']};
        min-height: 100vh;
        font-family: 'Inter', -apple-system, sans-serif;
    }}
    .stApp > header,
    header[data-testid="stHeader"] {{
        background: transparent !important;
    }}
    .main,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"],
    [data-testid="stMarkdown"],
    [data-testid="stMarkdownContainer"],
    [data-baseweb="tab-panel"],
    [data-baseweb="tab-list"],
    [data-baseweb="tab-highlight"],
    [data-baseweb="tab-border"],
    section.main {{
        background-color: transparent !important;
    }}
    .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 6rem;
        max-width: 1400px;
        background-color: transparent !important;
        min-height: calc(100vh - 80px);
    }}
    /* Tablas HTML: nada de fondos blancos heredados */
    table, thead, tbody, tr, td, th {{
        background-color: transparent;
    }}
    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, sans-serif;
    }}

    /* Forzar texto claro */
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown {{ color: {C['text']}; }}

    /* ---------- ANIMACIONES (entrada de pestañas + KPI bars) ---------- */
    /* Cuando una pestaña se vuelve visible, su contenido entra con fade+up */
    [data-baseweb="tab-panel"] > div {{
        animation: af-tab-in 0.45s cubic-bezier(0.16, 1, 0.3, 1) both;
    }}
    @keyframes af-tab-in {{
        from {{ opacity: 0; transform: translateY(14px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    /* Plotly charts: leve scale-in para sensación de "init" */
    .js-plotly-plot, .stPlotlyChart {{
        animation: af-chart-in 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
    }}
    @keyframes af-chart-in {{
        from {{ opacity: 0; transform: translateY(10px) scale(0.98); }}
        to   {{ opacity: 1; transform: translateY(0) scale(1); }}
    }}
    /* KPI bars que crecen desde 0 hasta su valor */
    .af-kpi-bar {{
        height: 4px;
        background: rgba(255,255,255,0.06);
        border-radius: 2px;
        margin: 8px 0 4px 0;
        overflow: hidden;
    }}
    .af-kpi-bar-fill {{
        height: 100%;
        width: 0%;
        border-radius: 2px;
        animation: af-bar-grow 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }}
    @keyframes af-bar-grow {{
        from {{ width: 0%; }}
        to   {{ width: var(--bar-target, 0%); }}
    }}
    /* Hover sutil en filas de tabla */
    table tbody tr {{
        transition: background-color 0.15s ease;
    }}
    table tbody tr:hover {{
        background-color: rgba(212,165,116,0.04) !important;
    }}
    /* Scroll horizontal en tablas anchas — responsive */
    .af-table-wrap {{
        overflow-x: auto;
        background-color: {C['surface']};
        border: 1px solid {C['line']};
        border-radius: 10px;
    }}
    .af-table-wrap > table {{ margin: 0; }}

    /* ---------- TIPO ---------- */
    .af-eyebrow {{
        font-size: 11px; font-weight: 600; letter-spacing: 0.16em;
        text-transform: uppercase; color: {C['gold']};
        display: inline-block; margin-bottom: 8px;
    }}
    .af-title {{
        font-family: 'Fraunces', Georgia, serif;
        font-weight: 500; font-size: 36px; letter-spacing: -0.02em;
        line-height: 1.1; color: {C['text']}; margin: 0 0 8px 0;
    }}
    .af-title em {{ font-style: italic; font-weight: 400; color: {C['gold']}; }}
    .af-sub {{
        font-size: 15px; color: {C['dim']}; line-height: 1.6;
        max-width: 760px; margin-bottom: 24px;
    }}
    .af-section {{
        font-family: 'Fraunces', serif; font-weight: 500;
        font-size: 20px; color: {C['text']};
        margin: 8px 0 4px 0; letter-spacing: -0.01em;
    }}
    .af-section-sub {{ font-size: 13px; color: {C['faint']}; margin-bottom: 14px; }}

    /* ---------- SIDEBAR ---------- */
    section[data-testid="stSidebar"] {{
        background: {C['surface']};
        border-right: 1px solid {C['line']};
    }}
    section[data-testid="stSidebar"] .block-container {{ padding-top: 2rem; }}
    .af-brand {{
        display: flex; align-items: center; gap: 10px;
        padding-bottom: 18px; border-bottom: 1px solid {C['line']};
        margin-bottom: 18px;
    }}
    .af-logo {{
        width: 34px; height: 34px;
        background: linear-gradient(135deg, {C['gold']} 0%, {C['gold_2']} 100%);
        border-radius: 7px; display: grid; place-items: center;
        color: {C['ink']}; font-family: 'Fraunces', serif;
        font-weight: 700; font-size: 18px;
        box-shadow: 0 4px 14px rgba(212,165,116,0.25);
    }}
    .af-brand-name {{
        font-family: 'Fraunces', serif; font-size: 19px;
        font-weight: 600; letter-spacing: -0.02em; color: {C['text']};
        line-height: 1;
    }}
    .af-brand-tag {{
        font-size: 10px; color: {C['faint']};
        letter-spacing: 0.1em; text-transform: uppercase;
        margin-top: 3px; font-weight: 500;
    }}
    .af-side-label {{
        font-size: 10px; font-weight: 600; letter-spacing: 0.12em;
        text-transform: uppercase; color: {C['faint']};
        margin: 14px 0 6px 0;
    }}
    .af-side-card {{
        background: {C['surface2']}; border: 1px solid {C['line']};
        border-radius: 8px; padding: 12px 14px; margin-bottom: 10px;
    }}
    .af-side-row {{
        display: flex; justify-content: space-between;
        font-size: 12px; padding: 3px 0;
    }}
    .af-side-row .l {{ color: {C['dim']}; }}
    .af-side-row .v {{ color: {C['text']}; font-family: 'JetBrains Mono', monospace; font-size: 11px; }}
    .af-status {{
        display: inline-flex; align-items: center; gap: 7px;
        font-size: 12px; font-weight: 500; color: {C['ok']};
    }}
    .af-status-dot {{
        width: 7px; height: 7px; border-radius: 50%;
        background: {C['ok']}; box-shadow: 0 0 8px {C['ok']};
        animation: af-pulse 2s infinite;
    }}
    @keyframes af-pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
    }}

    /* ---------- VALUE STRIP (siempre visible) ---------- */
    .af-strip {{
        display: grid; grid-template-columns: repeat(4, 1fr); gap: 0;
        background: {C['surface']}; border: 1px solid {C['line']};
        border-radius: 10px; overflow: hidden; margin-bottom: 22px;
    }}
    .af-strip-cell {{
        padding: 14px 18px; border-right: 1px solid {C['line']};
    }}
    .af-strip-cell:last-child {{ border-right: none; }}
    .af-strip-label {{
        font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase;
        color: {C['faint']}; font-weight: 600; margin-bottom: 4px;
    }}
    .af-strip-value {{
        font-family: 'Fraunces', serif; font-size: 22px; font-weight: 500;
        color: {C['text']}; letter-spacing: -0.02em; line-height: 1.1;
    }}
    .af-strip-delta {{ font-size: 11px; color: {C['ok']}; margin-top: 2px; }}

    /* ---------- KPI CARDS ---------- */
    .af-kpi {{
        background: {C['surface']}; border: 1px solid {C['line']};
        border-radius: 10px; padding: 18px 20px; height: 100%;
        transition: border-color 0.2s;
    }}
    .af-kpi:hover {{ border-color: {C['gold']}; }}
    .af-kpi-label {{
        font-size: 10px; font-weight: 600; letter-spacing: 0.1em;
        text-transform: uppercase; color: {C['faint']}; margin-bottom: 8px;
    }}
    .af-kpi-value {{
        font-family: 'Fraunces', serif; font-size: 28px; font-weight: 500;
        color: {C['text']}; letter-spacing: -0.02em; line-height: 1; margin-bottom: 4px;
    }}
    .af-kpi-value .unit {{ font-size: 13px; color: {C['dim']}; font-family: 'Inter', sans-serif; font-weight: 400; margin-left: 4px; }}
    .af-kpi-trend {{ font-size: 12px; font-weight: 500; }}
    .af-kpi-trend.up {{ color: {C['ok']}; }}
    .af-kpi-trend.down {{ color: {C['risk']}; }}
    .af-kpi-trend.neutral {{ color: {C['dim']}; }}

    /* ---------- ALERTS ---------- */
    .af-alert {{
        background: {C['surface']}; border: 1px solid {C['line']};
        border-left: 3px solid {C['info']};
        border-radius: 8px; padding: 16px 20px; margin-bottom: 12px;
    }}
    .af-alert.critical {{ border-left-color: {C['risk']}; }}
    .af-alert.high     {{ border-left-color: {C['amber']}; }}
    .af-alert.medium   {{ border-left-color: {C['info']}; }}
    .af-alert.low      {{ border-left-color: {C['ok']}; }}
    .af-alert-head {{
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 6px;
    }}
    .af-alert-id {{
        font-family: 'JetBrains Mono', monospace; font-size: 11px;
        color: {C['faint']}; letter-spacing: 0.04em;
    }}
    .af-alert-title {{
        font-family: 'Fraunces', serif; font-size: 16px; font-weight: 500;
        color: {C['text']}; letter-spacing: -0.01em;
    }}
    .af-alert-body {{ font-size: 13px; color: {C['dim']}; line-height: 1.55; margin-top: 4px; }}
    .af-tag {{
        display: inline-block; font-size: 10px;
        padding: 2px 7px; border-radius: 4px;
        background: {C['surface2']}; color: {C['dim']};
        border: 1px solid {C['line']};
        font-family: 'JetBrains Mono', monospace; margin-right: 4px;
    }}
    .af-sev {{
        display: inline-flex; align-items: center; gap: 5px;
        padding: 2px 7px; border-radius: 4px;
        font-size: 10px; font-weight: 600; letter-spacing: 0.06em;
        text-transform: uppercase;
    }}
    .af-sev.critical {{ background: rgba(229,96,78,0.10); color: {C['risk']}; }}
    .af-sev.high     {{ background: rgba(232,160,74,0.10); color: {C['amber']}; }}
    .af-sev.medium   {{ background: rgba(107,143,179,0.12); color: {C['info']}; }}
    .af-sev.low      {{ background: rgba(122,184,155,0.12); color: {C['ok']}; }}

    /* ---------- TRIPLE RECON ---------- */
    .af-recon-grid {{
        display: grid; grid-template-columns: 1fr 1fr 1fr;
        gap: 12px; margin-top: 12px;
    }}
    .af-recon-card {{
        background: {C['ink']}; border: 1px solid {C['line']};
        border-radius: 8px; padding: 14px 16px;
    }}
    .af-recon-card.match {{ border-color: rgba(122,184,155,0.4); }}
    .af-recon-card.mismatch {{ border-color: rgba(229,96,78,0.4); }}
    .af-recon-source {{
        font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase;
        color: {C['faint']}; font-weight: 600; margin-bottom: 8px;
    }}
    .af-recon-key {{ font-size: 11px; color: {C['dim']}; }}
    .af-recon-val {{
        font-family: 'JetBrains Mono', monospace; font-size: 13px;
        color: {C['text']}; padding: 2px 0;
    }}
    .af-recon-val.diff {{ color: {C['risk']}; font-weight: 600; }}
    .af-recon-val.ok {{ color: {C['ok']}; }}

    /* ---------- UPLOAD ---------- */
    .af-upload {{
        background: {C['surface']}; border: 2px dashed {C['line']};
        border-radius: 10px; padding: 26px 22px; text-align: center;
        transition: all 0.2s;
    }}
    .af-upload:hover {{ border-color: {C['gold']}; background: rgba(212,165,116,0.04); }}
    .af-upload-icon {{ font-size: 26px; margin-bottom: 6px; color: {C['gold']}; }}
    .af-upload-title {{
        font-family: 'Fraunces', serif; font-size: 16px; font-weight: 500;
        color: {C['text']}; margin-bottom: 4px;
    }}
    .af-upload-sub {{ font-size: 12px; color: {C['dim']}; }}

    /* ---------- COPILOT ---------- */
    .af-copilot-header {{
        background: linear-gradient(135deg, {C['surface2']} 0%, {C['surface']} 100%);
        border: 1px solid {C['line']};
        border-radius: 10px; padding: 18px 22px; margin-bottom: 16px;
        display: flex; align-items: center; gap: 14px;
    }}
    .af-copilot-avatar {{
        width: 42px; height: 42px;
        background: linear-gradient(135deg, {C['gold']}, {C['gold_2']});
        border-radius: 10px; display: grid; place-items: center;
        color: {C['ink']}; font-family: 'Fraunces', serif;
        font-weight: 700; font-size: 18px;
    }}
    .af-copilot-name {{
        font-family: 'Fraunces', serif; font-weight: 500;
        font-size: 17px; color: {C['text']}; letter-spacing: -0.01em;
    }}
    .af-copilot-role {{ font-size: 12px; color: {C['dim']}; }}
    .af-suggest {{
        display: inline-block; background: {C['surface2']};
        border: 1px solid {C['line']}; border-radius: 6px;
        padding: 6px 12px; margin: 3px; font-size: 12px;
        color: {C['dim']}; cursor: pointer;
    }}

    /* ---------- TABS ---------- */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0; border-bottom: 1px solid {C['line']};
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 42px; padding: 0 18px;
        background: transparent;
        font-size: 13px; font-weight: 500;
        color: {C['dim']};
        border-radius: 0;
    }}
    .stTabs [aria-selected="true"] {{
        color: {C['text']};
        border-bottom: 2px solid {C['gold']};
        background: transparent;
    }}

    /* ---------- BUTTONS ---------- */
    .stButton > button {{
        background: {C['gold']};
        color: {C['ink']};
        border: 1px solid {C['gold']};
        border-radius: 7px; padding: 10px 18px;
        font-weight: 600; font-size: 13px;
        font-family: 'Inter', sans-serif;
        transition: all 0.18s;
    }}
    .stButton > button:hover {{
        background: {C['amber']};
        border-color: {C['amber']};
        color: {C['ink']};
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(212,165,116,0.3);
    }}
    .stButton > button:focus:not(:active) {{
        background: {C['gold']}; color: {C['ink']}; border-color: {C['gold']};
    }}

    /* Dataframes */
    [data-testid="stDataFrame"] {{
        background: {C['surface']}; border: 1px solid {C['line']};
        border-radius: 10px; padding: 8px;
    }}

    /* Inputs / Chat */
    [data-testid="stChatInput"] textarea {{
        background: {C['surface2']}; color: {C['text']};
        border: 1px solid {C['line']}; border-radius: 8px;
    }}
    [data-testid="stChatMessage"] {{
        background: {C['surface']}; border: 1px solid {C['line']};
        border-radius: 10px;
    }}

    /* Footer compliance */
    .af-footer {{
        margin-top: 50px; padding-top: 18px;
        border-top: 1px solid {C['line']};
        display: flex; justify-content: space-between;
        font-size: 11px; color: {C['faint']};
    }}
    </style>
    """), unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 4. PLOTLY THEME (consistente con paleta)
# -----------------------------------------------------------------------------
def af_plotly_layout(**kwargs):
    base = dict(
        paper_bgcolor=C["surface"],
        plot_bgcolor=C["surface"],
        font=dict(family="Inter", color=C["text"], size=12),
        margin=dict(l=10, r=10, t=30, b=30),
        xaxis=dict(gridcolor=C["line_soft"], linecolor=C["line"], zeroline=False, color=C["dim"]),
        yaxis=dict(gridcolor=C["line_soft"], linecolor=C["line"], zeroline=False, color=C["dim"]),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["dim"], size=11)),
        hoverlabel=dict(bgcolor=C["surface2"], font_color=C["text"], bordercolor=C["line"]),
    )
    base.update(kwargs)
    return base


# -----------------------------------------------------------------------------
# 5. DATA FACTORY (caché para velocidad de demo)
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_demo_data():
    np.random.seed(42)

    # ----- CLIENTE -----
    client = {
        "name": "Distribuciones Martínez S.L.",
        "cif": "B-87654321",
        "sector": "Comercio mayorista de alimentación",
        "period": "Ejercicio 2024",
        "engagement": "ENG-2026-0341",
        "team": [
            {"role": "Socio firmante", "name": "Javier Pérez Aldaz, ROAC nº 18.234"},
            {"role": "Gerente",        "name": "Marta García Soler"},
            {"role": "Senior",         "name": "Carlos Ruiz Lema"},
            {"role": "Junior",         "name": "Ismael Ahmed"},
        ],
    }

    # ----- VOLUMETRÍAS -----
    volumes = {
        "transactions": 45_210,
        "invoices_in":  12_847,
        "invoices_out":  9_412,
        "journal_entries": 22_951,
        "vendors": 487,
        "revenue": 18_412_645.27,
        "coverage_pct": 100.0,
        "hours_saved": 124,
        # alerts_total y alerts_critical se calculan dinámicamente desde la lista
        # para evitar drift entre declarado y observado.
    }

    # ----- ALERTAS (catálogo enriquecido) -----
    alerts = [
        {
            "id": "A-101", "severity": "critical",
            "title": "Discrepancia OCR ↔ ERP en factura F-2024-0099",
            "body": ("La extracción OCR de la factura física registra un total de 1.210,00 €, "
                     "pero el asiento contable #4402 (cuenta 600.001) refleja 2.210,00 €. "
                     "Sobrevaloración del gasto de 1.000,00 € sin documento justificativo."),
            "tags": ["NIA-ES 240", "NIA-ES 500", "Triple conciliación", "Cuenta 600.001"],
            "amount": 1000.00, "vendor": "Aceros Levante S.A.", "date": "2024-07-12",
            "recommendation": "Solicitar copia original a proveedor y revisar autorización del asiento.",
        },
        {
            "id": "A-102", "severity": "critical",
            "title": "Factura duplicada: F-2024-0105 contabilizada dos veces",
            "body": ("Misma factura registrada en asientos #4501 y #4588 con distinto número de "
                     "documento interno. Importe: 8.420,00 €. Ambos pagos liquidados al proveedor."),
            "tags": ["NIA-ES 240", "Duplicate detection", "Pago doble"],
            "amount": 8420.00, "vendor": "Logística Mediterránea S.L.", "date": "2024-09-03",
            "recommendation": "Iniciar reclamación al proveedor; revisar control de bloqueo de duplicados en ERP.",
        },
        {
            "id": "A-103", "severity": "critical",
            "title": "Anomalía Benford en facturación a partes vinculadas",
            "body": ("Distribución del primer dígito en las facturas a la sociedad vinculada "
                     "Martínez Holding S.L. desvía -8,4 puntos sobre el dígito '1' (Benford). "
                     "Test χ² supera el umbral de significación (p < 0,01)."),
            "tags": ["NIA-ES 240", "NIA-ES 550", "Ley de Benford", "Partes vinculadas"],
            "amount": None, "vendor": "Martínez Holding S.L.", "date": "2024-Q4",
            "recommendation": "Ampliar pruebas sustantivas sobre operaciones intragrupo y verificar precios de transferencia.",
        },
        {
            "id": "A-104", "severity": "critical",
            "title": "Diferencia material en conciliación bancaria",
            "body": ("Saldo contable cuenta 572.001 (Banco Santander): 412.380,55 €. "
                     "Saldo según extracto: 398.205,33 €. Diferencia: 14.175,22 € sin partidas pendientes identificadas."),
            "tags": ["NIA-ES 500", "NIA-ES 505", "Conciliación bancaria"],
            "amount": 14175.22, "vendor": "Banco Santander", "date": "2024-12-31",
            "recommendation": "Solicitar circularización al banco y revisar cobros/pagos de los últimos 5 días hábiles.",
        },
        {
            "id": "A-201", "severity": "high",
            "title": "Pagos en fin de semana fuera de patrón",
            "body": ("Detectados 17 asientos de pago contabilizados en sábado o domingo, "
                     "frente a una media histórica de 2 al año. Concentrados en julio-agosto."),
            "tags": ["NIA-ES 315", "NIA-ES 240", "Patrón temporal"],
            "amount": 47820.00, "vendor": "Múltiples", "date": "2024-Jul-Ago",
            "recommendation": "Revisar autorizaciones y entrevistar al responsable de tesorería.",
        },
        {
            "id": "A-202", "severity": "high",
            "title": "Operaciones round number cluster",
            "body": ("23 asientos por importe exactamente redondo (múltiplos de 1.000 €) "
                     "en cuenta 629 'Otros servicios'. La probabilidad estadística es < 0,3%."),
            "tags": ["NIA-ES 240", "Round number anomaly"],
            "amount": 89000.00, "vendor": "Múltiples", "date": "2024",
            "recommendation": "Solicitar documentación soporte de cada operación; cruzar con contratos vigentes.",
        },
        {
            "id": "A-203", "severity": "high",
            "title": "Concentración anómala en cierre de ejercicio",
            "body": ("38% del gasto anual de la cuenta 622 'Reparaciones' se concentra en los "
                     "últimos 10 días del ejercicio. Histórico: 9% en mismo periodo."),
            "tags": ["NIA-ES 520", "Cut-off testing"],
            "amount": 156400.00, "vendor": "Múltiples", "date": "2024-12-21/31",
            "recommendation": "Verificar fechas de devengo real vs. registro; revisar política de provisiones.",
        },
        {
            "id": "A-204", "severity": "high",
            "title": "Amortización fuera del rango fiscal admisible",
            "body": ("Elemento 'Maquinaria línea envasado II' amortizado al 18% anual. "
                     "Coeficiente máximo según tablas oficiales: 12%. Exceso fiscal: 32.450 €."),
            "tags": ["NIA-ES 540", "Amortización", "Impuesto Sociedades"],
            "amount": 32450.00, "vendor": "—", "date": "2024",
            "recommendation": "Recalcular dotación según coeficiente máximo y proponer ajuste extracontable.",
        },
        {
            "id": "A-301", "severity": "medium",
            "title": "Proveedor con NIF inválido detectado",
            "body": "Proveedor 'Servicios Express XYZ' registrado con NIF B-99999999 (formato inválido). 4 facturas, 3.847 €.",
            "tags": ["NIA-ES 500", "Validación maestros"],
            "amount": 3847.00, "vendor": "Servicios Express XYZ", "date": "2024",
            "recommendation": "Verificar identificación fiscal en AEAT; bloquear nuevo registro hasta validación.",
        },
        {
            "id": "A-302", "severity": "medium",
            "title": "Operación >3.005,06 € no declarada en Modelo 347",
            "body": "Volumen anual con proveedor 'Suministros Industriales del Norte S.A.' = 4.812,00 €. No aparece en M-347 presentado.",
            "tags": ["Fiscal", "Modelo 347"],
            "amount": 4812.00, "vendor": "Suministros Industriales del Norte S.A.", "date": "2024",
            "recommendation": "Presentar declaración complementaria del Modelo 347.",
        },
        {
            "id": "A-303", "severity": "medium",
            "title": "Asiento sin documento adjunto",
            "body": "9 asientos contables superiores a 5.000 € sin evidencia documental adjunta en el ERP.",
            "tags": ["NIA-ES 500", "Evidencia"],
            "amount": 67200.00, "vendor": "Múltiples", "date": "2024",
            "recommendation": "Exigir adjunto antes de validar el asiento; auditar workflow de aprobación.",
        },
    ]

    # ----- BENFORD DATA -----
    benford_expected = {
        1: 30.10, 2: 17.61, 3: 12.49, 4: 9.69, 5: 7.92,
        6: 6.69, 7: 5.80, 8: 5.12, 9: 4.58
    }
    # Observed (con anomalías): dígito 1 baja, dígito 7 sube
    benford_observed = {
        1: 21.7, 2: 16.9, 3: 13.1, 4: 10.4, 5: 8.6,
        6: 7.5, 7: 9.8, 8: 6.2, 9: 5.8
    }

    # ----- KPIs -----
    kpis = pd.DataFrame([
        {"Indicador": "Ratio liquidez",        "Actual": "0,85", "Histórica": "1,40", "Sector": "1,28", "Δ vs hist.": "−39%", "Estado": "critical", "Detalle": "Por debajo del umbral 1,0 — riesgo continuidad"},
        {"Indicador": "Periodo medio cobro",   "Actual": "52 días", "Histórica": "38 días", "Sector": "42 días", "Δ vs hist.": "+37%", "Estado": "critical", "Detalle": "Deterioro significativo del circulante"},
        {"Indicador": "Margen bruto",          "Actual": "31,2%", "Histórica": "34,1%", "Sector": "33,5%", "Δ vs hist.": "−2,9 pp", "Estado": "high", "Detalle": "Caída fuera de banda ±2σ"},
        {"Indicador": "Endeudamiento total",   "Actual": "58,4%", "Histórica": "55,2%", "Sector": "52,8%", "Δ vs hist.": "+3,2 pp", "Estado": "medium", "Detalle": "Dentro del rango aceptable"},
        {"Indicador": "ROE",                   "Actual": "8,2%", "Histórica": "11,4%", "Sector": "10,1%", "Δ vs hist.": "−3,2 pp", "Estado": "high", "Detalle": "Erosión de rentabilidad"},
        {"Indicador": "ROA",                   "Actual": "4,1%", "Histórica": "5,7%", "Sector": "5,2%", "Δ vs hist.": "−1,6 pp", "Estado": "medium", "Detalle": "Eficiencia de activos en descenso"},
        {"Indicador": "EBITDA / Ventas",       "Actual": "9,8%", "Histórica": "12,1%", "Sector": "11,4%", "Δ vs hist.": "−2,3 pp", "Estado": "high", "Detalle": "Compresión operativa"},
        {"Indicador": "Z-Score (Altman)",      "Actual": "2,14", "Histórica": "2,87", "Sector": "—", "Δ vs hist.": "−0,73", "Estado": "high", "Detalle": "Zona gris (1,81 < Z < 2,99) — vigilar"},
    ])

    # ----- FISCAL CROSS-CHECK -----
    fiscal = pd.DataFrame([
        {"Modelo": "303 IVA — Repercutido",    "Contable": 3_866_654.30, "Declarado": 3_866_654.30, "Diferencia": 0.00,      "Estado": "ok"},
        {"Modelo": "303 IVA — Soportado",      "Contable": 2_184_972.18, "Declarado": 2_177_840.55, "Diferencia": 7_131.63,  "Estado": "high"},
        {"Modelo": "111 IRPF — Retenciones",   "Contable":   148_240.00, "Declarado":   148_240.00, "Diferencia": 0.00,      "Estado": "ok"},
        {"Modelo": "115 IRPF — Arrendamientos","Contable":    24_192.00, "Declarado":    24_192.00, "Diferencia": 0.00,      "Estado": "ok"},
        {"Modelo": "200 I. Sociedades — BI",   "Contable": 1_842_315.41, "Declarado": 1_809_865.41, "Diferencia": 32_450.00, "Estado": "critical"},
        {"Modelo": "347 — Op. >3.005,06 €",    "Contable":     4_812.00, "Declarado":         0.00, "Diferencia":  4_812.00, "Estado": "medium"},
        {"Modelo": "349 — Op. intracomunit.",  "Contable":   312_408.55, "Declarado":   312_408.55, "Diferencia": 0.00,      "Estado": "ok"},
    ])

    # ----- AMORTIZATION -----
    amortization = pd.DataFrame([
        {"Activo": "Maquinaria línea envasado I",   "Cuenta": "213.001", "Coste": 480_000, "Vida útil (años)": 10, "% aplicado": "10,0%", "% máx. fiscal": "12,0%", "Dotación 2024": 48_000, "Acumulada": 240_000, "Neto": 240_000, "Estado": "ok"},
        {"Activo": "Maquinaria línea envasado II",  "Cuenta": "213.002", "Coste": 360_000, "Vida útil (años)":  6, "% aplicado": "18,0%", "% máx. fiscal": "12,0%", "Dotación 2024": 64_800, "Acumulada": 129_600, "Neto": 230_400, "Estado": "critical"},
        {"Activo": "Mobiliario oficinas centrales", "Cuenta": "216.001", "Coste":  78_500, "Vida útil (años)": 10, "% aplicado": "10,0%", "% máx. fiscal": "10,0%", "Dotación 2024":  7_850, "Acumulada":  31_400, "Neto":  47_100, "Estado": "ok"},
        {"Activo": "Equipos informáticos 2022",     "Cuenta": "217.001", "Coste":  64_200, "Vida útil (años)":  4, "% aplicado": "25,0%", "% máx. fiscal": "25,0%", "Dotación 2024": 16_050, "Acumulada":  32_100, "Neto":  32_100, "Estado": "ok"},
        {"Activo": "Vehículo turismo dirección",    "Cuenta": "218.001", "Coste":  52_000, "Vida útil (años)":  6, "% aplicado": "16,0%", "% máx. fiscal": "16,0%", "Dotación 2024":  8_320, "Acumulada":  16_640, "Neto":  35_360, "Estado": "ok"},
        {"Activo": "Edificio almacén Sagunto",      "Cuenta": "211.001", "Coste":1_240_000, "Vida útil (años)": 50, "% aplicado": "2,0%", "% máx. fiscal": "3,0%",  "Dotación 2024": 24_800, "Acumulada": 198_400, "Neto":1_041_600, "Estado": "ok"},
    ])

    # ----- RECONCILIATION DATASET -----
    reconciliation = [
        {"key": "F-2024-0099", "ocr": 1210.00, "erp": 2210.00, "bank": 2210.00, "vendor": "Aceros Levante S.A.",      "status": "mismatch", "diff": 1000.00},
        {"key": "F-2024-0100", "ocr": 4830.00, "erp": 4830.00, "bank": 4830.00, "vendor": "Transportes Castellón",     "status": "match",    "diff": 0},
        {"key": "F-2024-0101", "ocr":  872.50, "erp":  872.50, "bank":  872.50, "vendor": "Material Oficina IBC",      "status": "match",    "diff": 0},
        {"key": "F-2024-0102", "ocr":15400.00, "erp":15400.00, "bank":15400.00, "vendor": "Logística Mediterránea",    "status": "match",    "diff": 0},
        {"key": "F-2024-0103", "ocr": 2150.00, "erp": 2150.00, "bank": 2150.00, "vendor": "Aceros Levante S.A.",      "status": "match",    "diff": 0},
        {"key": "F-2024-0105", "ocr": 8420.00, "erp": 8420.00, "bank": 8420.00, "vendor": "Logística Mediterránea",    "status": "duplicate","diff": 8420.00},
        {"key": "F-2024-0107", "ocr":  590.00, "erp":  590.00, "bank":  590.00, "vendor": "Suministros del Norte",    "status": "match",    "diff": 0},
        {"key": "F-2024-0108", "ocr": 3120.40, "erp": 3120.40, "bank": 3120.40, "vendor": "Talleres Roquetas",         "status": "match",    "diff": 0},
        {"key": "F-2024-0110", "ocr": 7800.00, "erp": 7800.00, "bank":     None,"vendor": "Servicios Express XYZ",     "status": "pending",  "diff": 0},
    ]

    # ----- RISK BY AREA -----
    risk_areas = pd.DataFrame({
        "Área": ["Compras", "Tesorería", "Partes vinculadas", "Personal", "Impuestos", "Inmovilizado", "Ventas", "Existencias"],
        "Riesgo": [85, 72, 68, 35, 58, 51, 22, 28],
    }).sort_values("Riesgo", ascending=True)

    # ----- TIMELINE (transacciones por mes) -----
    months = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
    timeline = pd.DataFrame({
        "Mes": months,
        "Transacciones": [3520, 3410, 3680, 3590, 3920, 3760, 4280, 3120, 3950, 4120, 3890, 3970],
        "Alertas":       [   1,    0,    1,    2,    1,    1,    4,    2,    2,    1,    1,    2],
    })

    return {
        "client": client,
        "volumes": volumes,
        "alerts": alerts,
        "benford_expected": benford_expected,
        "benford_observed": benford_observed,
        "kpis": kpis,
        "fiscal": fiscal,
        "amortization": amortization,
        "reconciliation": reconciliation,
        "risk_areas": risk_areas,
        "timeline": timeline,
    }


# -----------------------------------------------------------------------------
# 6. UI HELPERS
# -----------------------------------------------------------------------------
def fmt_eur(n, decimals=2):
    if n is None:
        return "—"
    s = f"{n:,.{decimals}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".") + " €"

def value_strip(data):
    volumes = data["volumes"]
    alerts_total = len(data["alerts"])
    alerts_critical = sum(1 for a in data["alerts"] if a["severity"] == "critical")
    st.markdown(textwrap.dedent(f"""
    <div class="af-strip">
      <div class="af-strip-cell">
        <div class="af-strip-label">Cobertura analizada</div>
        <div class="af-strip-value">100<span style="font-size:14px;color:{C['dim']}">%</span></div>
        <div class="af-strip-delta">vs. 5–10% en muestreo tradicional</div>
      </div>
      <div class="af-strip-cell">
        <div class="af-strip-label">Transacciones</div>
        <div class="af-strip-value">{volumes['transactions']:,}</div>
        <div class="af-strip-delta" style="color:{C['dim']}">analizadas en {volumes['hours_saved']*0.5:.0f} min</div>
      </div>
      <div class="af-strip-cell">
        <div class="af-strip-label">Horas auditor ahorradas</div>
        <div class="af-strip-value">+{volumes['hours_saved']}<span style="font-size:14px;color:{C['dim']}">h</span></div>
        <div class="af-strip-delta">≈ {volumes['hours_saved']*70:,} € en honorarios</div>
      </div>
      <div class="af-strip-cell">
        <div class="af-strip-label">Hallazgos materiales</div>
        <div class="af-strip-value">{alerts_total}</div>
        <div class="af-strip-delta" style="color:{C['risk']}">{alerts_critical} críticos · NIA-ES 240</div>
      </div>
    </div>
    """), unsafe_allow_html=True)


def kpi_card(label, value, unit="", trend=None, trend_dir="neutral", bar_pct=None, bar_color=None):
    """
    KPI card con barra opcional que se anima desde 0% hasta `bar_pct`%
    cada vez que la pestaña se abre. `bar_color` por defecto se elige
    según `trend_dir`.
    """
    trend_html = ""
    if trend is not None:
        trend_html = f'<div class="af-kpi-trend {trend_dir}">{trend}</div>'
    unit_html = f'<span class="unit">{unit}</span>' if unit else ""

    bar_html = ""
    if bar_pct is not None:
        if bar_color is None:
            bar_color = {
                "up":      C["ok"],
                "down":    C["risk"],
                "neutral": C["gold"],
            }.get(trend_dir, C["gold"])
        # Clamp 0..100
        pct = max(0, min(100, float(bar_pct)))
        bar_html = (
            f'<div class="af-kpi-bar">'
            f'  <div class="af-kpi-bar-fill" '
            f'       style="--bar-target:{pct:.1f}%; background:{bar_color};"></div>'
            f'</div>'
        )

    st.html(f"""
    <div class="af-kpi">
      <div class="af-kpi-label">{label}</div>
      <div class="af-kpi-value">{value}{unit_html}</div>
      {bar_html}
      {trend_html}
    </div>
    """)


def alert_card(a):
    tags_html = "".join([f'<span class="af-tag">{t}</span>' for t in a["tags"]])
    sev_label = {"critical":"Crítico", "high":"Alto", "medium":"Medio", "low":"Bajo"}[a["severity"]]
    amount_html = ""
    if a.get("amount"):
        amount_html = f'<div style="font-family: \'JetBrains Mono\', monospace; font-size:13px; color:{C["amber"]}; margin-top:6px;">Impacto cuantificado: {fmt_eur(a["amount"])}</div>'
    rec_html = f'<div style="margin-top:10px; padding-top:10px; border-top: 1px dashed {C["line_soft"]}; font-size:12px; color:{C["dim"]};"><span style="color:{C["gold"]}; font-weight:600;">▸ Recomendación:</span> {a["recommendation"]}</div>'

    st.markdown(textwrap.dedent(f"""
    <div class="af-alert {a['severity']}">
      <div class="af-alert-head">
        <div>
          <span class="af-alert-id">{a['id']}</span>
          <span class="af-sev {a['severity']}" style="margin-left:8px;">{sev_label}</span>
        </div>
        <div style="font-size:12px; color:{C['faint']}; font-family: 'JetBrains Mono', monospace;">{a.get('date','')}</div>
      </div>
      <div class="af-alert-title">{a['title']}</div>
      <div class="af-alert-body">{a['body']}</div>
      {amount_html}
      <div style="margin-top:10px;">{tags_html}</div>
      {rec_html}
    </div>
    """), unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 7. SIDEBAR (contexto persistente del expediente)
# -----------------------------------------------------------------------------
def render_sidebar(client, loaded):
    with st.sidebar:
        st.markdown(textwrap.dedent(f"""
        <div class="af-brand">
          <div class="af-logo">A</div>
          <div>
            <div class="af-brand-name">Audit Pro</div>
            <div class="af-brand-tag">Auditoria Continua · ICJCE</div>
          </div>
        </div>
        """), unsafe_allow_html=True)

        if loaded:
            st.markdown(f'<div class="af-side-label">Expediente activo</div>', unsafe_allow_html=True)
            st.markdown(textwrap.dedent(f"""
            <div class="af-side-card">
              <div style="font-family:'Fraunces',serif; font-size:15px; color:{C['text']}; font-weight:500; margin-bottom:6px;">{client['name']}</div>
              <div class="af-side-row"><span class="l">CIF</span><span class="v">{client['cif']}</span></div>
              <div class="af-side-row"><span class="l">Ejercicio</span><span class="v">{client['period']}</span></div>
              <div class="af-side-row"><span class="l">Engagement</span><span class="v">{client['engagement']}</span></div>
              <div class="af-side-row"><span class="l">Sector</span><span class="v" style="font-size:10px;">CNAE 4631</span></div>
            </div>
            """), unsafe_allow_html=True)

            st.markdown(f'<div class="af-side-label">Equipo de auditoría</div>', unsafe_allow_html=True)
            team_rows = "".join([
                f'<div class="af-side-row"><span class="l">{m["role"]}</span><span class="v" style="font-size:10px; max-width:130px; text-align:right; line-height:1.3;">{m["name"]}</span></div>'
                for m in client["team"]
            ])
            st.markdown(f'<div class="af-side-card">{team_rows}</div>', unsafe_allow_html=True)
        else:
            st.markdown(textwrap.dedent(f"""
            <div class="af-side-card" style="text-align:center;">
              <div style="font-size:12px; color:{C['dim']};">Ningún expediente activo</div>
              <div style="font-size:11px; color:{C['faint']}; margin-top:4px;">Cargue datos en la pestaña <b>Carga</b></div>
            </div>
            """), unsafe_allow_html=True)

        st.markdown(f'<div class="af-side-label">Estado del sistema</div>', unsafe_allow_html=True)
        st.markdown(textwrap.dedent(f"""
        <div class="af-side-card">
          <div class="af-status"><span class="af-status-dot"></span>Motor de análisis activo</div>
          <div style="font-size:10px; color:{C['faint']}; margin-top:6px;">v2.4.1 · NIA-ES & RGPD compliant</div>
        </div>
        """), unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 8. VIEWS
# -----------------------------------------------------------------------------
def render_intro():
    st.markdown(textwrap.dedent(f"""
    <div class="af-eyebrow">Reto ICJCE 2026 · Digitalización de la auditoría</div>
    <h1 class="af-title">Auditoría continua sobre el <em>100%</em> del universo de datos.</h1>
    <p class="af-sub">
      AuditFlow Pro reemplaza el muestreo estadístico tradicional por un análisis exhaustivo
      asistido por IA. Triple conciliación automatizada (factura ↔ ERP ↔ banco), detección
      de anomalías (Benford, patrones temporales, partes vinculadas) y trazabilidad completa
      contra normativa NIA-ES, alineado con el plan ICJCE de digitalización 2026.
    </p>
    """), unsafe_allow_html=True)


def render_carga(data):
    st.markdown(f'<div class="af-section">Carga de información contable</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="af-section-sub">Soporta XML/XLS/CSV/PDF — sufijos AEAT y formatos PGC. Procesamiento OCR sobre documento físico.</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="af-upload"><div class="af-upload-icon">▦</div><div class="af-upload-title">Facturas emitidas / recibidas</div><div class="af-upload-sub">PDF · XML Facturae · ZIP de lote</div></div>', unsafe_allow_html=True)
        st.file_uploader("Facturas", type=["pdf","xml","zip","csv"], label_visibility="collapsed", key="up_inv")

        st.markdown('<div class="af-upload" style="margin-top:14px;"><div class="af-upload-icon">▤</div><div class="af-upload-title">Libro Mayor / Balanza de comprobación</div><div class="af-upload-sub">XLS · CSV · cuentas 8 dígitos PGC</div></div>', unsafe_allow_html=True)
        st.file_uploader("Mayor", type=["xls","xlsx","csv"], label_visibility="collapsed", key="up_may")

    with c2:
        st.markdown('<div class="af-upload"><div class="af-upload-icon">▥</div><div class="af-upload-title">Libro Diario</div><div class="af-upload-sub">Asientos del periodo · Formato AEAT SII compatible</div></div>', unsafe_allow_html=True)
        st.file_uploader("Diario", type=["xls","xlsx","csv","xml"], label_visibility="collapsed", key="up_dia")

        st.markdown('<div class="af-upload" style="margin-top:14px;"><div class="af-upload-icon">▧</div><div class="af-upload-title">Extracto bancario</div><div class="af-upload-sub">Norma 43 · Formato CSV o agregador</div></div>', unsafe_allow_html=True)
        st.file_uploader("Banco", type=["csv","txt","xls","xlsx"], label_visibility="collapsed", key="up_ban")

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

    cta_l, cta_c, cta_r = st.columns([1,2,1])
    with cta_c:
        st.markdown(textwrap.dedent(f"""
        <div style="background:{C['surface2']}; border:1px solid {C['gold']}; border-radius:10px; padding:16px 20px; text-align:center;">
          <div style="font-family:'Fraunces',serif; font-size:17px; color:{C['text']}; font-weight:500; margin-bottom:4px;">Modo demostración</div>
          <div style="font-size:12px; color:{C['dim']}; margin-bottom:10px;">Caso real con anomalías inyectadas — Distribuciones Martínez S.L.</div>
        </div>
        """), unsafe_allow_html=True)
        if st.button("Cargar caso de demostración", key="load_demo", use_container_width=True):
            st.session_state["loaded"] = True
            n = len(data["alerts"])
            st.toast(f"45.210 transacciones cargadas · {n} hallazgos detectados", icon="✅")
            st.rerun()

    if st.session_state.get("loaded"):
        st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
        st.markdown(f'<div class="af-section">Pipeline de análisis</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="af-section-sub">Procesamiento completado en 47 segundos. Universo analizado: 100%.</div>', unsafe_allow_html=True)

        steps = [
            ("01", "Ingesta", "45.210 registros · 4 fuentes"),
            ("02", "Validación", "Integridad · Cuadre asientos"),
            ("03", "Conciliación triple", "Factura ↔ ERP ↔ Banco"),
            ("04", "Detección IA", "Benford · Patrones · Partes vinculadas"),
            ("05", "Reporting", "18 alertas · Trazabilidad NIA"),
        ]
        cols = st.columns(5)
        for i, (num, name, stat) in enumerate(steps):
            with cols[i]:
                st.markdown(textwrap.dedent(f"""
                <div style="background:{C['surface']}; border:1px solid rgba(122,184,155,0.3); border-radius:8px; padding:12px 14px;">
                  <div style="font-family:'JetBrains Mono',monospace; font-size:10px; color:{C['ok']};">▣ {num}</div>
                  <div style="font-size:13px; color:{C['text']}; font-weight:600; margin-top:4px;">{name}</div>
                  <div style="font-size:11px; color:{C['dim']}; margin-top:2px;">{stat}</div>
                </div>
                """), unsafe_allow_html=True)


def render_dashboard(data):
    if not st.session_state.get("loaded"):
        _empty_state("Carga datos para ver el dashboard ejecutivo.")
        return

    v = data["volumes"]
    alerts_total = len(data["alerts"])
    alerts_critical = sum(1 for a in data["alerts"] if a["severity"] == "critical")
    st.markdown(f'<div class="af-section">Dashboard ejecutivo</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="af-section-sub">{data["client"]["name"]} · {data["client"]["period"]} · Engagement {data["client"]["engagement"]}</div>', unsafe_allow_html=True)

    # KPIs principales — con barras animadas que crecen desde 0
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Cobertura analizada", "100", "%", "Universo completo (no muestreo)", "up", bar_pct=100)
    with c2: kpi_card("Hallazgos materiales", str(alerts_total), "", f"{alerts_critical} críticos requieren acción", "down", bar_pct=(alerts_critical/alerts_total)*100)
    with c3: kpi_card("Riesgo agregado", "Medio", "", "Score IA: 64/100", "neutral", bar_pct=64, bar_color=C["amber"])
    with c4: kpi_card("Eficiencia auditor", f"+{v['hours_saved']}", "h", f"≈ {v['hours_saved']*70:,} € equivalente", "up", bar_pct=82)

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

    # Charts: timeline + risk by area
    cl, cr = st.columns([1.6, 1])
    with cl:
        st.markdown(f'<div class="af-section" style="font-size:15px;">Evolución de transacciones y alertas</div>', unsafe_allow_html=True)
        tl = data["timeline"]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=tl["Mes"], y=tl["Transacciones"], name="Transacciones",
            marker_color=C["line"], opacity=0.8,
            yaxis="y", hovertemplate="%{x}: %{y:,} tx<extra></extra>"
        ))
        fig.add_trace(go.Scatter(
            x=tl["Mes"], y=tl["Alertas"], name="Alertas detectadas",
            mode="lines+markers", line=dict(color=C["gold"], width=2.5),
            marker=dict(size=8, color=C["gold"], line=dict(color=C["ink"], width=2)),
            yaxis="y2", hovertemplate="%{x}: %{y} alertas<extra></extra>"
        ))
        fig.update_layout(
            **af_plotly_layout(
                height=280,
                yaxis=dict(title="Transacciones", gridcolor=C["line_soft"], color=C["dim"]),
                yaxis2=dict(title="Alertas", overlaying="y", side="right", color=C["gold"], gridcolor="rgba(0,0,0,0)"),
                showlegend=False,
            )
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with cr:
        st.markdown(f'<div class="af-section" style="font-size:15px;">Riesgo por área</div>', unsafe_allow_html=True)
        ra = data["risk_areas"]
        colors = [C["risk"] if v >= 70 else (C["amber"] if v >= 50 else (C["info"] if v >= 30 else C["ok"])) for v in ra["Riesgo"]]
        fig2 = go.Figure(go.Bar(
            x=ra["Riesgo"], y=ra["Área"], orientation="h",
            marker_color=colors,
            hovertemplate="%{y}: score %{x}/100<extra></extra>"
        ))
        fig2.update_layout(**af_plotly_layout(height=280, xaxis=dict(range=[0,100], gridcolor=C["line_soft"], color=C["dim"])))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # Severity breakdown
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    st.markdown(f'<div class="af-section" style="font-size:15px;">Distribución de hallazgos por severidad</div>', unsafe_allow_html=True)
    sev_counts = {"Crítico":0,"Alto":0,"Medio":0,"Bajo":0}
    for a in data["alerts"]:
        sev_counts[{"critical":"Crítico","high":"Alto","medium":"Medio","low":"Bajo"}[a["severity"]]] += 1
    sev_df = pd.DataFrame({"sev": list(sev_counts.keys()), "n": list(sev_counts.values())})
    sev_colors = {"Crítico": C["risk"], "Alto": C["amber"], "Medio": C["info"], "Bajo": C["ok"]}
    fig3 = go.Figure(go.Bar(
        x=sev_df["sev"], y=sev_df["n"],
        marker_color=[sev_colors[s] for s in sev_df["sev"]],
        text=sev_df["n"], textposition="outside",
        textfont=dict(color=C["text"], size=14),
        hovertemplate="%{x}: %{y} hallazgos<extra></extra>"
    ))
    fig3.update_layout(**af_plotly_layout(height=210, showlegend=False))
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})


def render_conciliacion(data):
    if not st.session_state.get("loaded"):
        _empty_state("Carga datos para ejecutar la conciliación triple.")
        return

    st.markdown(f'<div class="af-section">Conciliación triple automatizada</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="af-section-sub">Cruce simultáneo de tres fuentes independientes: documento físico (OCR), registro contable (ERP) y movimiento bancario.</div>', unsafe_allow_html=True)

    recon = data["reconciliation"]
    total = len(recon)
    matched = sum(1 for r in recon if r["status"] == "match")
    mismatched = sum(1 for r in recon if r["status"] == "mismatch")
    duplicates = sum(1 for r in recon if r["status"] == "duplicate")
    pending = sum(1 for r in recon if r["status"] == "pending")

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Cuadrados", f"{matched}/{total}", "", f"{matched/total*100:.0f}% del muestrario", "up", bar_pct=(matched/total)*100)
    with c2: kpi_card("Discrepancias", str(mismatched), "", "Importe distinto entre fuentes", "down", bar_pct=(mismatched/total)*100, bar_color=C["risk"])
    with c3: kpi_card("Duplicados", str(duplicates), "", "Mismo doc. registrado 2 veces", "down", bar_pct=(duplicates/total)*100, bar_color=C["amber"])
    with c4: kpi_card("Pendientes", str(pending), "", "Falta movimiento bancario", "neutral", bar_pct=(pending/total)*100, bar_color=C["info"])

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)
    st.markdown(f'<div class="af-section" style="font-size:15px;">Caso destacado · Discrepancia material</div>', unsafe_allow_html=True)

    # Render the highlighted case (F-2024-0099) with all 3 sources
    case = next(r for r in recon if r["key"] == "F-2024-0099")
    st.markdown(textwrap.dedent(f"""
    <div class="af-recon-grid">
      <div class="af-recon-card match">
        <div class="af-recon-source">▣ Fuente 1 — Documento OCR</div>
        <div class="af-recon-key">Factura física escaneada</div>
        <div class="af-recon-val">REF: {case['key']}</div>
        <div class="af-recon-val">PROV: {case['vendor']}</div>
        <div class="af-recon-val ok">TOTAL: {fmt_eur(case['ocr'])}</div>
      </div>
      <div class="af-recon-card mismatch">
        <div class="af-recon-source">▣ Fuente 2 — ERP / Libro Mayor</div>
        <div class="af-recon-key">Asiento contable nº 4402</div>
        <div class="af-recon-val">CUENTA: 600.001</div>
        <div class="af-recon-val">FECHA: 12/07/2024</div>
        <div class="af-recon-val diff">REGISTRO: {fmt_eur(case['erp'])}</div>
      </div>
      <div class="af-recon-card mismatch">
        <div class="af-recon-source">▣ Fuente 3 — Movimiento bancario</div>
        <div class="af-recon-key">Banco Santander · cta 572.001</div>
        <div class="af-recon-val">FECHA VAL.: 14/07/2024</div>
        <div class="af-recon-val">CONCEPTO: TRF F-2024-0099</div>
        <div class="af-recon-val diff">CARGO: {fmt_eur(case['bank'])}</div>
      </div>
    </div>
    <div style="background:{C['surface']}; border:1px solid {C['risk']}; border-left-width:3px; border-radius:8px; padding:14px 18px; margin-top:14px;">
      <div style="font-family:'Fraunces',serif; font-size:15px; font-weight:500; color:{C['risk']}; margin-bottom:6px;">▸ Conclusión del motor</div>
      <div style="font-size:13px; color:{C['dim']}; line-height:1.6;">
        El documento físico (factura del proveedor) refleja un total de <b style="color:{C['text']}">1.210,00 €</b>.
        Tanto el ERP como el banco ejecutaron <b style="color:{C['risk']}">2.210,00 €</b>.
        La sobrevaloración (1.000,00 €) coincide en contabilidad y pago, lo que descarta error
        de tecleo y exige investigación sustantiva (NIA-ES 240, 500). Recomendación: bloqueo
        del proveedor pendiente de circularización.
      </div>
    </div>
    """), unsafe_allow_html=True)

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)
    st.markdown(f'<div class="af-section" style="font-size:15px;">Detalle de cruces</div>', unsafe_allow_html=True)

    df = pd.DataFrame(recon)
    df["OCR"] = df["ocr"].apply(lambda x: fmt_eur(x) if x else "—")
    df["ERP"] = df["erp"].apply(lambda x: fmt_eur(x) if x else "—")
    df["Banco"] = df["bank"].apply(lambda x: fmt_eur(x) if x else "—")
    df["Diferencia"] = df["diff"].apply(lambda x: fmt_eur(x) if x else "—")
    status_map = {"match": "✓ Cuadrado", "mismatch": "✗ Discrepancia", "duplicate": "⊘ Duplicado", "pending": "⋯ Pendiente"}
    df["Estado"] = df["status"].map(status_map)
    show = df[["key", "vendor", "OCR", "ERP", "Banco", "Diferencia", "Estado"]].rename(
        columns={"key":"Documento", "vendor":"Proveedor"}
    )
    st.dataframe(show, use_container_width=True, hide_index=True)


def render_alertas(data):
    if not st.session_state.get("loaded"):
        _empty_state("Carga datos para ver el detalle de hallazgos.")
        return

    st.markdown(f'<div class="af-section">Hallazgos detectados</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="af-section-sub">Cada hallazgo está vinculado a su evidencia, su tipología de riesgo y la NIA-ES aplicable.</div>', unsafe_allow_html=True)

    sev_filter = st.radio(
        "Filtrar por severidad",
        ["Todos", "Crítico", "Alto", "Medio"],
        horizontal=True,
        label_visibility="collapsed",
        key="sev_filter",
    )
    map_sev = {"Crítico":"critical", "Alto":"high", "Medio":"medium"}
    alerts = data["alerts"]
    if sev_filter != "Todos":
        alerts = [a for a in alerts if a["severity"] == map_sev[sev_filter]]

    st.markdown(f'<div style="font-size:12px; color:{C["faint"]}; margin:10px 0 14px 0;">{len(alerts)} hallazgo(s) listado(s)</div>', unsafe_allow_html=True)

    for a in alerts:
        alert_card(a)


def render_fiscal(data):
    if not st.session_state.get("loaded"):
        _empty_state("Carga datos para ejecutar el cruce fiscal.")
        return

    st.markdown(f'<div class="af-section">Cruce fiscal con declaraciones AEAT</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="af-section-sub">Comparativa entre saldos contables y modelos presentados (303, 111, 115, 200, 347, 349).</div>', unsafe_allow_html=True)

    fiscal = data["fiscal"].copy()
    total_diff = fiscal["Diferencia"].sum()
    n_issues = (fiscal["Estado"] != "ok").sum()

    c1, c2, c3 = st.columns(3)
    with c1: kpi_card("Modelos cruzados", str(len(fiscal)), "", "Ejercicio 2024", "neutral", bar_pct=100)
    with c2: kpi_card("Discrepancias", str(int(n_issues)), "", f"{int(n_issues)} requieren ajuste", "down", bar_pct=(n_issues/len(fiscal))*100, bar_color=C["risk"])
    with c3: kpi_card("Diferencia agregada", fmt_eur(total_diff, 0), "", "Ajuste fiscal estimado", "neutral", bar_pct=68, bar_color=C["amber"])

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # Tabla con coloreado por estado (renderizado como HTML para control fino)
    rows_html = ""
    for _, r in fiscal.iterrows():
        sev = r["Estado"]
        sev_label = {"ok":"✓ Cuadrado", "medium":"⚠ Atención", "high":"⚠ Atención", "critical":"✗ Discrepancia material"}[sev]
        sev_color = {"ok":C["ok"], "medium":C["info"], "high":C["amber"], "critical":C["risk"]}[sev]
        diff_html = fmt_eur(r["Diferencia"], 2) if r["Diferencia"] != 0 else "—"
        rows_html += f"""
        <tr>
          <td style="padding:11px 16px;">{r['Modelo']}</td>
          <td style="padding:11px 16px; text-align:right; font-family:'JetBrains Mono',monospace;">{fmt_eur(r['Contable'], 2)}</td>
          <td style="padding:11px 16px; text-align:right; font-family:'JetBrains Mono',monospace;">{fmt_eur(r['Declarado'], 2)}</td>
          <td style="padding:11px 16px; text-align:right; font-family:'JetBrains Mono',monospace; color:{sev_color}; font-weight:{600 if sev!='ok' else 400};">{diff_html}</td>
          <td style="padding:11px 16px; color:{sev_color}; font-size:12px; font-weight:500;">{sev_label}</td>
        </tr>
        """
    rows_html +=''
    st.html(f"""
    <div style="background:{C['surface']}; border:1px solid {C['line']}; border-radius:10px; overflow:hidden;">
      <table style="width:100%; border-collapse:collapse; font-size:13px;">
        <thead style="background:{C['surface2']};">
          <tr>
            <th style="text-align:left; padding:11px 16px; font-size:11px; letter-spacing:0.08em; color:{C['faint']}; text-transform:uppercase; border-bottom:1px solid {C['line']};">Modelo</th>
            <th style="text-align:right; padding:11px 16px; font-size:11px; letter-spacing:0.08em; color:{C['faint']}; text-transform:uppercase; border-bottom:1px solid {C['line']};">Saldo contable</th>
            <th style="text-align:right; padding:11px 16px; font-size:11px; letter-spacing:0.08em; color:{C['faint']}; text-transform:uppercase; border-bottom:1px solid {C['line']};">Declarado AEAT</th>
            <th style="text-align:right; padding:11px 16px; font-size:11px; letter-spacing:0.08em; color:{C['faint']}; text-transform:uppercase; border-bottom:1px solid {C['line']};">Diferencia</th>
            <th style="text-align:left; padding:11px 16px; font-size:11px; letter-spacing:0.08em; color:{C['faint']}; text-transform:uppercase; border-bottom:1px solid {C['line']};">Estado</th>
          </tr>
        </thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
    """)

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)
    st.markdown(textwrap.dedent(f"""
    <div style="background:{C['surface']}; border-left:3px solid {C['risk']}; border-radius:8px; padding:14px 18px;">
      <div style="font-family:'Fraunces',serif; font-size:15px; color:{C['text']}; font-weight:500; margin-bottom:4px;">▸ Discrepancia material — Modelo 200 (Impuesto sobre Sociedades)</div>
      <div style="font-size:13px; color:{C['dim']}; line-height:1.6;">
        La base imponible declarada (1.809.865,41 €) es inferior en 32.450,00 € al resultado contable
        ajustado. La diferencia coincide con el exceso de amortización del activo "Maquinaria línea
        envasado II" (ver pestaña <b>Amortización</b> · alerta A-204). Se recomienda complementaria
        del Modelo 200 o ajuste extracontable positivo en próxima declaración.
      </div>
    </div>
    """), unsafe_allow_html=True)


def render_amortizacion(data):
    if not st.session_state.get("loaded"):
        _empty_state("Carga datos para verificar la política de amortización.")
        return

    st.markdown(f'<div class="af-section">Verificación de amortización del inmovilizado</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="af-section-sub">Cruce de coeficientes aplicados contra tablas oficiales del Real Decreto 1777/2004.</div>', unsafe_allow_html=True)

    amort = data["amortization"]
    total_coste = amort["Coste"].sum()
    total_dot = amort["Dotación 2024"].sum()
    n_issues = (amort["Estado"] != "ok").sum()

    c1, c2, c3 = st.columns(3)
    with c1: kpi_card("Activos analizados", str(len(amort)), "", f"Coste agregado: {fmt_eur(total_coste,0)}", "neutral", bar_pct=100)
    with c2: kpi_card("Dotación 2024", fmt_eur(total_dot, 0), "", "Total registrado en P&L", "neutral", bar_pct=58, bar_color=C["gold"])
    with c3: kpi_card("Anomalías detectadas", str(int(n_issues)), "", "Requieren ajuste fiscal", "down" if n_issues else "up", bar_pct=(n_issues/len(amort))*100, bar_color=C["risk"] if n_issues else C["ok"])

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # Render tabla
    rows = ""
    for _, r in amort.iterrows():
        sev = r["Estado"]
        sev_color = C["risk"] if sev == "critical" else (C["amber"] if sev == "high" else C["dim"])
        flag = "✗" if sev == "critical" else ("⚠" if sev == "high" else "✓")
        flag_color = C["risk"] if sev == "critical" else (C["amber"] if sev == "high" else C["ok"])
        rows += f"""
        <tr>
          <td style="padding:11px 16px;">{r['Activo']}</td>
          <td style="padding:11px 16px; font-family:'JetBrains Mono',monospace; color:{C['dim']}; font-size:12px;">{r['Cuenta']}</td>
          <td style="padding:11px 16px; text-align:right; font-family:'JetBrains Mono',monospace;">{fmt_eur(r['Coste'],0)}</td>
          <td style="padding:11px 16px; text-align:center; font-family:'JetBrains Mono',monospace; color:{C['dim']};">{r['% aplicado']}</td>
          <td style="padding:11px 16px; text-align:center; font-family:'JetBrains Mono',monospace; color:{C['dim']};">{r['% máx. fiscal']}</td>
          <td style="padding:11px 16px; text-align:right; font-family:'JetBrains Mono',monospace; color:{sev_color}; font-weight:{600 if sev!='ok' else 400};">{fmt_eur(r['Dotación 2024'],0)}</td>
          <td style="padding:11px 16px; text-align:center; color:{flag_color}; font-size:16px;">{flag}</td>
        </tr>
        """
    st.html(f"""
    <div style="background:{C['surface']}; border:1px solid {C['line']}; border-radius:10px; overflow:hidden;">
      <table style="width:100%; border-collapse:collapse; font-size:13px;">
        <thead style="background:{C['surface2']};">
          <tr>
            <th style="text-align:left; padding:11px 16px; font-size:11px; letter-spacing:0.08em; color:{C['faint']}; text-transform:uppercase;">Activo</th>
            <th style="text-align:left; padding:11px 16px; font-size:11px; letter-spacing:0.08em; color:{C['faint']}; text-transform:uppercase;">Cuenta</th>
            <th style="text-align:right; padding:11px 16px; font-size:11px; letter-spacing:0.08em; color:{C['faint']}; text-transform:uppercase;">Coste</th>
            <th style="text-align:center; padding:11px 16px; font-size:11px; letter-spacing:0.08em; color:{C['faint']}; text-transform:uppercase;">% aplicado</th>
            <th style="text-align:center; padding:11px 16px; font-size:11px; letter-spacing:0.08em; color:{C['faint']}; text-transform:uppercase;">% máx. fiscal</th>
            <th style="text-align:right; padding:11px 16px; font-size:11px; letter-spacing:0.08em; color:{C['faint']}; text-transform:uppercase;">Dotación 2024</th>
            <th style="text-align:center; padding:11px 16px; font-size:11px; letter-spacing:0.08em; color:{C['faint']}; text-transform:uppercase;">OK</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    """)

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)
    st.markdown(textwrap.dedent(f"""
    <div style="background:{C['surface']}; border-left:3px solid {C['risk']}; border-radius:8px; padding:14px 18px;">
      <div style="font-family:'Fraunces',serif; font-size:15px; color:{C['text']}; font-weight:500; margin-bottom:4px;">▸ Hallazgo A-204 · Maquinaria línea envasado II</div>
      <div style="font-size:13px; color:{C['dim']}; line-height:1.6;">
        Coeficiente aplicado: <b style="color:{C['risk']}">18% anual</b>. Coeficiente máximo según
        tablas: <b style="color:{C['ok']}">12%</b>. El exceso de dotación (32.450 €) es no deducible
        fiscalmente y debe revertirse mediante ajuste positivo extracontable. Impacto en cuota IS
        estimado: <b style="color:{C['amber']}">8.112,50 €</b> (tipo general 25%).
      </div>
    </div>
    """), unsafe_allow_html=True)


def render_kpis(data):
    if not st.session_state.get("loaded"):
        _empty_state("Carga datos para ver el análisis de KPIs y Benford.")
        return

    st.markdown(f'<div class="af-section">KPIs financieros y test de Benford</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="af-section-sub">Análisis comparativo con históricos (±2σ) y sector. Test de Benford sobre primer dígito de facturación.</div>', unsafe_allow_html=True)

    # ---------- BENFORD ----------
    st.markdown(f'<div class="af-section" style="font-size:15px; margin-top:8px;">Ley de Benford · Distribución del primer dígito</div>', unsafe_allow_html=True)

    digits = list(range(1, 10))
    expected = [data["benford_expected"][d] for d in digits]
    observed = [data["benford_observed"][d] for d in digits]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=digits, y=observed, name="Observado",
        marker_color=[
            C["risk"] if abs(o - e) > 4 else C["gold"]
            for o, e in zip(observed, expected)
        ],
        hovertemplate="Dígito %{x}: %{y:.1f}% observado<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=digits, y=expected, name="Esperado (Benford)",
        mode="lines+markers", line=dict(color=C["text"], width=2, dash="dot"),
        marker=dict(color=C["text"], size=7),
        hovertemplate="Dígito %{x}: %{y:.1f}% esperado<extra></extra>",
    ))
    fig.update_layout(**af_plotly_layout(
        height=300,
        xaxis=dict(title="Primer dígito significativo", dtick=1, gridcolor=C["line_soft"], color=C["dim"]),
        yaxis=dict(title="Frecuencia (%)", gridcolor=C["line_soft"], color=C["dim"]),
        legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center", bgcolor="rgba(0,0,0,0)", font=dict(color=C["dim"])),
    ))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Chi-squared estilo
    chi2 = sum((o-e)**2 / e for o, e in zip(observed, expected))
    cb1, cb2, cb3 = st.columns(3)
    with cb1: kpi_card("Estadístico χ²", f"{chi2:.2f}", "", "Umbral significación: 15,51 (α=0,05)", "down", bar_pct=min(chi2/15.51*100, 100), bar_color=C["risk"])
    with cb2: kpi_card("Desviación máxima", "−8,4", "pp", "Dígito '1' (esperado 30,1%)", "down", bar_pct=70, bar_color=C["risk"])
    with cb3: kpi_card("p-valor", "<0,01", "", "Distribución no compatible con Benford", "down", bar_pct=92, bar_color=C["risk"])

    st.markdown(textwrap.dedent(f"""
    <div style="background:{C['surface']}; border-left:3px solid {C['amber']}; border-radius:8px; padding:14px 18px; margin-top:14px;">
      <div style="font-family:'Fraunces',serif; font-size:15px; color:{C['text']}; font-weight:500; margin-bottom:4px;">▸ Interpretación</div>
      <div style="font-size:13px; color:{C['dim']}; line-height:1.6;">
        La frecuencia observada del dígito '1' (21,7%) es significativamente inferior a la esperada
        (30,1%), mientras que el dígito '7' aparece sobrerrepresentado. Este patrón es consistente
        con manipulación selectiva de importes en facturación a partes vinculadas y motiva la
        ampliación de pruebas sustantivas (NIA-ES 240, NIA-ES 550).
      </div>
    </div>
    """), unsafe_allow_html=True)

    # ---------- KPIs FINANCIEROS ----------
    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
    st.markdown(f'<div class="af-section" style="font-size:15px;">Análisis de ratios financieros</div>', unsafe_allow_html=True)

    kpis = data["kpis"]
    rows = ""
    for _, r in kpis.iterrows():
        sev = r["Estado"]
        sev_color = {"critical":C["risk"], "high":C["amber"], "medium":C["info"], "ok":C["ok"]}[sev]
        sev_label = {"critical":"Crítico", "high":"Alerta", "medium":"Atención", "ok":"Normal"}[sev]
        rows += f"""
        <tr>
          <td style="padding:11px 16px;">{r['Indicador']}</td>
          <td style="padding:11px 16px; text-align:right; font-family:'JetBrains Mono',monospace; color:{C['text']}; font-weight:600;">{r['Actual']}</td>
          <td style="padding:11px 16px; text-align:right; font-family:'JetBrains Mono',monospace; color:{C['dim']};">{r['Histórica']}</td>
          <td style="padding:11px 16px; text-align:right; font-family:'JetBrains Mono',monospace; color:{C['dim']};">{r['Sector']}</td>
          <td style="padding:11px 16px; text-align:right; font-family:'JetBrains Mono',monospace; color:{sev_color}; font-weight:600;">{r['Δ vs hist.']}</td>
          <td style="padding:11px 16px;"><span class="af-sev {sev}">{sev_label}</span></td>
          <td style="padding:11px 16px; font-size:12px; color:{C['dim']};">{r['Detalle']}</td>
        </tr>
        """
    st.html(f"""
    <div style="background:{C['surface']}; border:1px solid {C['line']}; border-radius:10px; overflow:hidden;">
      <table style="width:100%; border-collapse:collapse; font-size:13px;">
        <thead style="background:{C['surface2']};">
          <tr>
            <th style="text-align:left; padding:11px 16px; font-size:11px; letter-spacing:0.08em; color:{C['faint']}; text-transform:uppercase;">Indicador</th>
            <th style="text-align:right; padding:11px 16px; font-size:11px; letter-spacing:0.08em; color:{C['faint']}; text-transform:uppercase;">Actual</th>
            <th style="text-align:right; padding:11px 16px; font-size:11px; letter-spacing:0.08em; color:{C['faint']}; text-transform:uppercase;">Hist. 3a</th>
            <th style="text-align:right; padding:11px 16px; font-size:11px; letter-spacing:0.08em; color:{C['faint']}; text-transform:uppercase;">Sector</th>
            <th style="text-align:right; padding:11px 16px; font-size:11px; letter-spacing:0.08em; color:{C['faint']}; text-transform:uppercase;">Δ</th>
            <th style="text-align:left; padding:11px 16px; font-size:11px; letter-spacing:0.08em; color:{C['faint']}; text-transform:uppercase;">Estado</th>
            <th style="text-align:left; padding:11px 16px; font-size:11px; letter-spacing:0.08em; color:{C['faint']}; text-transform:uppercase;">Detalle</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    """)


def render_copilot(data):
    st.markdown(textwrap.dedent(f"""
    <div class="af-copilot-header">
      <div class="af-copilot-avatar">V</div>
      <div>
        <div class="af-copilot-name">VeraCopilot</div>
        <div class="af-copilot-role">Asistente de auditoría · Acceso a expediente activo</div>
      </div>
      <div style="margin-left:auto;" class="af-status"><span class="af-status-dot"></span>En línea</div>
    </div>
    """), unsafe_allow_html=True)

    if not st.session_state.get("loaded"):
        _empty_state("Carga datos en la pestaña <b>Carga</b> para que VeraCopilot pueda analizarlos.")
        return

    if "messages" not in st.session_state:
        alerts_total = len(data["alerts"])
        alerts_critical = sum(1 for a in data["alerts"] if a["severity"] == "critical")
        st.session_state.messages = [{
            "role": "assistant",
            "content": (
                f"He completado el análisis del ejercicio 2024 de **{data['client']['name']}**. "
                f"Identifico **{alerts_total} hallazgos**, "
                f"**{alerts_critical} de severidad crítica**. "
                "¿Por cuál quieres que empiece?"
            )
        }]

    # Sugerencias rápidas
    st.markdown(f'<div style="font-size:11px; color:{C["faint"]}; letter-spacing:0.08em; text-transform:uppercase; margin:4px 0 8px 0; font-weight:600;">Preguntas sugeridas</div>', unsafe_allow_html=True)
    sc1, sc2, sc3 = st.columns(3)
    sugerencias = [
        ("¿Por qué A-101 es crítica?", "a-101"),
        ("Resumen de hallazgos críticos", "resumen"),
        ("Explica el test de Benford", "benford"),
    ]
    for col, (label, key) in zip([sc1, sc2, sc3], sugerencias):
        if col.button(label, key=f"sg_{key}", use_container_width=True):
            st.session_state["__forced_q"] = label

    # Caja de input arriba (antes que la lista de mensajes)
    forced = st.session_state.pop("__forced_q", None)
    prompt = st.chat_input("Pregunta sobre cualquier hallazgo, ratio o área de riesgo…")
    if forced and not prompt:
        prompt = forced

    # Procesar nuevo mensaje (si existe) ANTES de renderizar la conversación,
    # para que aparezca inmediatamente en la parte superior del historial.
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        response = _copilot_answer(prompt, data)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Renderizar mensajes en orden reverso por pares (último intercambio primero,
    # manteniendo el orden interno user → assistant dentro de cada par).
    msgs = st.session_state.messages
    if msgs and msgs[0]["role"] == "assistant" and len(msgs) % 2 == 1:
        # Saludo inicial del asistente (sin pareja) — irá al final del historial
        greeting = [msgs[0]]
        rest = msgs[1:]
    else:
        greeting = []
        rest = msgs

    pairs = [rest[i:i + 2] for i in range(0, len(rest), 2)]
    display = []
    for pair in reversed(pairs):
        display.extend(pair)
    display.extend(greeting)

    # Separador visual sutil entre input y conversación
    if display:
        st.markdown(
            f'<div style="height:1px; background:{C["line"]}; margin:14px 0 10px 0;"></div>',
            unsafe_allow_html=True,
        )

    for m in display:
        with st.chat_message(m["role"], avatar="🤖" if m["role"] == "assistant" else None):
            st.markdown(m["content"])


def _copilot_answer(q: str, data) -> str:
    """Router de respuestas. Mucho más rico que la versión anterior."""
    qn = q.lower()

    # A-101
    if "101" in qn or "discrepancia" in qn or "ocr" in qn:
        return (
            "**Hallazgo A-101 · Severidad crítica**\n\n"
            "El motor OCR leyó **1.210,00 €** en el documento físico de la factura "
            "F-2024-0099 (proveedor *Aceros Levante S.A.*). El asiento contable #4402 "
            "registró **2.210,00 €** en la cuenta 600.001, y el cargo bancario coincidió "
            "con el ERP — es decir, se pagaron 1.000 € de más sin soporte documental.\n\n"
            "Es **crítica** porque (1) afecta a una cuenta de gasto, (2) el flujo monetario "
            "se completó, y (3) la diferencia coincide con un múltiplo redondo, patrón "
            "consistente con manipulación deliberada (NIA-ES 240, NIA-ES 500).\n\n"
            "**Acción sugerida:** circularizar al proveedor, revisar autorizaciones del "
            "asiento y bloquear pagos pendientes."
        )

    # A-102 / duplicada
    if "102" in qn or "duplicad" in qn:
        return (
            "**Hallazgo A-102 · Factura duplicada**\n\n"
            "La factura F-2024-0105 (*Logística Mediterránea S.L.*, 8.420,00 €) fue "
            "contabilizada en los asientos #4501 y #4588 con números internos distintos, "
            "y ambos pagos se ejecutaron al banco del proveedor.\n\n"
            "El control de bloqueo por número de documento no se activó, lo que apunta a "
            "una debilidad sistemática del entorno de control (NIA-ES 315).\n\n"
            "**Acción:** reclamar 8.420 € al proveedor y reforzar la regla de unicidad en el ERP."
        )

    # Benford
    if "benford" in qn:
        return (
            "**Test de Benford · Resultado**\n\n"
            "Aplicado sobre los importes de facturación, el primer dígito significativo "
            "muestra una desviación notable: el dígito *1* aparece en el **21,7%** de los "
            "casos cuando Benford predice **30,1%**, mientras que el *7* está sobrerrepresentado.\n\n"
            "El estadístico χ² supera el umbral de significación al 1%. Cuando se filtra por "
            "facturación a *Martínez Holding S.L.* (parte vinculada), la desviación se acentúa.\n\n"
            "**Implicación:** patrón compatible con manipulación selectiva de importes. "
            "Procedimientos sustantivos adicionales sobre operaciones intragrupo (NIA-ES 550) "
            "y revisión de precios de transferencia."
        )

    # Resumen
    if "resumen" in qn or "crític" in qn or "summary" in qn:
        return (
            "**Resumen de hallazgos críticos (4)**\n\n"
            "1. **A-101** — Sobrevaloración de gasto por 1.000 € (Aceros Levante)\n"
            "2. **A-102** — Factura duplicada de 8.420 € (Logística Mediterránea)\n"
            "3. **A-103** — Anomalía Benford en partes vinculadas (Martínez Holding)\n"
            "4. **A-104** — Descuadre conciliación bancaria de 14.175 € (Santander)\n\n"
            "**Impacto cuantificado agregado:** 23.595 €. El conjunto de patrones (round numbers, "
            "fines de semana, cluster de cierre) eleva el score de riesgo de fraude a **Medio-Alto** "
            "y requiere ampliación del programa de pruebas (NIA-ES 240, 330).\n\n"
            "¿Quieres que detalle el plan de respuesta?"
        )

    # Fiscal / IVA / 200 / sociedades
    if any(k in qn for k in ["fiscal", "iva", "303", "200", "sociedades", "modelo", "347"]):
        return (
            "**Estado fiscal del expediente**\n\n"
            "Cruce contra modelos AEAT presentados:\n\n"
            "- **Modelo 200 (IS)**: base imponible declarada inferior en **32.450 €** al resultado "
            "ajustado. Coincide con el exceso de amortización del activo 'Maquinaria línea envasado II'.\n"
            "- **Modelo 303 (IVA soportado)**: descuadre de 7.131 € pendiente de justificación.\n"
            "- **Modelo 347**: una operación de 4.812 € con *Suministros del Norte* no fue declarada.\n\n"
            "**Impacto fiscal estimado en cuota IS**: ≈ **8.112 €** (tipo 25%) más posibles intereses."
        )

    # Amortización
    if "amortiz" in qn or "depreciaci" in qn or "204" in qn:
        return (
            "**Hallazgo A-204 · Amortización fuera de tablas**\n\n"
            "El activo *Maquinaria línea envasado II* (cuenta 213.002) se amortiza al **18% anual**, "
            "pero el coeficiente máximo según tablas oficiales (RD 1777/2004) es **12%**.\n\n"
            "El exceso de dotación en 2024 asciende a **32.450 €** y debe revertirse vía ajuste "
            "positivo extracontable. Si no se corrige, expone a la sociedad a una contingencia "
            "fiscal por el periodo no prescrito (4 ejercicios)."
        )

    # KPIs / liquidez / ratios
    if any(k in qn for k in ["kpi", "liquidez", "ratio", "endeudamiento", "margen", "altman", "z-score"]):
        return (
            "**Diagnóstico financiero**\n\n"
            "Tres ratios fuera de banda ±2σ vs. histórico de 3 años:\n\n"
            "- **Liquidez**: 0,85 (vs 1,40 hist.) — riesgo de tensión de circulante\n"
            "- **Periodo medio cobro**: 52 días (vs 38) — deterioro de gestión de clientes\n"
            "- **Z-Score Altman**: 2,14 — zona gris (1,81–2,99) que requiere monitorización\n\n"
            "El conjunto sugiere presión sobre la generación de caja. Recomendación de "
            "procedimientos analíticos adicionales sobre saldos de clientes y rotación de existencias "
            "(NIA-ES 520)."
        )

    # Conciliación bancaria
    if "104" in qn or "conciliaci" in qn or "banco" in qn:
        return (
            "**Hallazgo A-104 · Descuadre bancario**\n\n"
            "Cuenta 572.001 (Banco Santander). Saldo contable: **412.380,55 €**. "
            "Saldo según extracto: **398.205,33 €**. Diferencia: **14.175,22 €** sin partidas "
            "pendientes que la justifiquen.\n\n"
            "Recomendación: solicitar circularización bancaria conforme a NIA-ES 505 y revisar "
            "los movimientos de los últimos 5 días hábiles del ejercicio."
        )

    # Default
    return (
        "Tengo acceso al expediente completo: hallazgos, conciliación triple, cruce fiscal, "
        "amortización, KPIs y test de Benford. Puedes preguntarme por cualquier alerta concreta "
        "(p. ej. *A-101*, *A-204*), por un área de riesgo, o pedirme un resumen ejecutivo. "
        "¿Quieres que prepare la sección del informe para revisión del socio?"
    )


def _empty_state(msg):
    st.markdown(textwrap.dedent(f"""
    <div style="background:{C['surface']}; border:1px dashed {C['line']}; border-radius:10px; padding:36px; text-align:center; margin-top:8px;">
      <div style="font-family:'Fraunces',serif; font-size:18px; color:{C['text']}; margin-bottom:6px;">Sin datos cargados</div>
      <div style="font-size:13px; color:{C['dim']};">{msg}</div>
    </div>
    """), unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 9. MAIN
# -----------------------------------------------------------------------------
def main():
    inject_css()

    if "loaded" not in st.session_state:
        st.session_state["loaded"] = False

    data = get_demo_data()
    render_sidebar(data["client"], st.session_state["loaded"])

    render_intro()
    if st.session_state["loaded"]:
        value_strip(data)

    tabs = st.tabs([
        "Carga",
        "Dashboard",
        "Conciliación",
        "Alertas",
        "Fiscal",
        "Amortización",
        "KPIs & Benford",
        "VeraCopilot",
    ])
    with tabs[0]: render_carga(data)
    with tabs[1]: render_dashboard(data)
    with tabs[2]: render_conciliacion(data)
    with tabs[3]: render_alertas(data)
    with tabs[4]: render_fiscal(data)
    with tabs[5]: render_amortizacion(data)
    with tabs[6]: render_kpis(data)
    with tabs[7]: render_copilot(data)

    st.markdown(textwrap.dedent(f"""
    <div class="af-footer">
      <span>AuditFlow Pro · Reto ICJCE 2026 · Equipo: Ismael Ahmed, Iancarlo Falcon, Aaron Aguirre</span>
      <span>NIA-ES · RGPD · Datos sintéticos para demo</span>
    </div>
    """), unsafe_allow_html=True)


if __name__ == "__main__":
    main()

