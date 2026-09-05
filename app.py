
import streamlit as st
import pandas as pd
import sqlite3
import re
import os
from datetime import datetime
from pathlib import Path
import io

# ---------------- DB path ----------------
_db_env = os.environ.get("HISAB_DB_PATH")
if _db_env:
    DB_PATH = Path(_db_env)
else:
    DB_PATH = Path(__file__).with_name("hisab.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

try:
    import pdfplumber
except Exception:
    pdfplumber = None

st.set_page_config(page_title="Hisab Software Pro", page_icon="💰", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
/* ===== HISAB SOFTWARE PRO ===== */
:root{
    --hs-bg:#0b1020;
    --hs-panel:#121a2b;
    --hs-panel-2:#182236;
    --hs-border:#26334b;
    --hs-text:#f8fafc;
    --hs-muted:#94a3b8;
    --hs-accent:#7c3aed;
    --hs-accent-2:#2563eb;
    --hs-success:#10b981;
    --hs-danger:#ef4444;
    --hs-warning:#f59e0b;
}

/* Main background */
.stApp {
    background:
        radial-gradient(circle at top right, rgba(124,58,237,.12), transparent 28%),
        radial-gradient(circle at top left, rgba(37,99,235,.10), transparent 24%),
        var(--hs-bg);
    color: var(--hs-text);
}

/* Main content width */
.block-container {
    max-width: 1450px;
    padding-top: 1.6rem;
    padding-bottom: 3rem;
}

/* Hide default chrome */
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header[data-testid="stHeader"] {background:transparent;}

/* Hero */
.hs-hero{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:18px;
    padding:24px 26px;
    margin:4px 0 18px 0;
    border:1px solid var(--hs-border);
    border-radius:22px;
    background:linear-gradient(135deg, rgba(24,34,54,.96), rgba(18,26,43,.92));
    box-shadow:0 16px 40px rgba(0,0,0,.22);
}
.hs-title{
    font-size:34px;
    font-weight:800;
    letter-spacing:-.7px;
    margin:0;
}
.hs-sub{
    margin-top:6px;
    color:var(--hs-muted);
    font-size:14px;
}
.hs-badge{
    display:inline-flex;
    align-items:center;
    gap:8px;
    padding:8px 12px;
    border-radius:999px;
    font-size:12px;
    font-weight:700;
    background:linear-gradient(135deg, rgba(124,58,237,.20), rgba(37,99,235,.18));
    border:1px solid rgba(124,58,237,.35);
    color:#ddd6fe;
    white-space:nowrap;
}

/* Tabs */
button[data-baseweb="tab"] {
    border-radius:12px !important;
    padding:10px 14px !important;
    margin-right:6px !important;
    background:#111827 !important;
    border:1px solid #26334b !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background:linear-gradient(135deg, #6d28d9, #2563eb) !important;
    color:white !important;
    border-color:transparent !important;
}
div[data-baseweb="tab-list"] {
    gap:6px;
    background:transparent;
    padding-bottom:8px;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background:linear-gradient(180deg, rgba(24,34,54,.98), rgba(17,24,39,.98));
    border:1px solid var(--hs-border);
    border-radius:18px;
    padding:18px 18px;
    box-shadow:0 10px 24px rgba(0,0,0,.16);
}
div[data-testid="stMetricLabel"] p{
    color:var(--hs-muted) !important;
    font-size:13px !important;
    font-weight:600 !important;
}
div[data-testid="stMetricValue"]{
    font-size:27px !important;
    font-weight:800 !important;
    letter-spacing:-.4px;
}

/* Inputs */
div[data-baseweb="select"] > div,
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stDateInput"] input {
    background:#111827 !important;
    border:1px solid var(--hs-border) !important;
    border-radius:12px !important;
}
div[data-baseweb="select"] > div:focus-within,
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color:#7c3aed !important;
    box-shadow:0 0 0 2px rgba(124,58,237,.14) !important;
}

/* Buttons */
.stButton > button,
.stDownloadButton > button {
    border-radius:12px !important;
    border:1px solid rgba(124,58,237,.45) !important;
    background:linear-gradient(135deg, #6d28d9, #2563eb) !important;
    color:white !important;
    font-weight:700 !important;
    padding:.6rem 1rem !important;
    box-shadow:0 8px 18px rgba(37,99,235,.16);
}
.stButton > button:hover,
.stDownloadButton > button:hover {
    transform:translateY(-1px);
    filter:brightness(1.08);
}

/* File uploader */
div[data-testid="stFileUploader"] {
    border:1px dashed #334155;
    border-radius:16px;
    padding:8px;
    background:rgba(17,24,39,.55);
}

/* Dataframe */
div[data-testid="stDataFrame"] {
    border:1px solid var(--hs-border);
    border-radius:16px;
    overflow:hidden;
    box-shadow:0 10px 24px rgba(0,0,0,.10);
}

/* Section subtitles */
h1,h2,h3{
    letter-spacing:-.3px;
}
h3{
    margin-top:1.2rem !important;
}

/* Alert boxes */
div[data-testid="stAlert"]{
    border-radius:14px !important;
    border:1px solid var(--hs-border) !important;
}

/* Expander */
details{
    border:1px solid var(--hs-border) !important;
    border-radius:14px !important;
    background:#111827 !important;
}

/* Horizontal rules */
hr{
    border-color:#26334b !important;
}

/* Mobile */
@media (max-width: 768px){
    .block-container {padding-left:1rem;padding-right:1rem;}
    .hs-hero{padding:18px;align-items:flex-start;flex-direction:column;}
    .hs-title{font-size:28px;}
}
</style>
""", unsafe_allow_html=True)


# ---------------- DB ----------------
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            txn_date TEXT,
            direction TEXT,
            party TEXT,
            details TEXT,
            payment_type TEXT,
            mode TEXT,
            account_source TEXT,
            amount REAL,
            balance REAL,
            source TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    return conn


CONN = get_conn()

# ---------------- DB migrations ----------------
def ensure_columns():
    cur = CONN.execute("PRAGMA table_info(transactions)")
    existing = {row[1] for row in cur.fetchall()}
    wanted = {
        "category": "TEXT",
        "reference_no": "TEXT",
        "source_file": "TEXT",
    }
    for col, typ in wanted.items():
        if col not in existing:
            CONN.execute(f"ALTER TABLE transactions ADD COLUMN {col} {typ}")
    CONN.commit()

ensure_columns()

# ---------------- Receivable / Payable dues ----------------
def ensure_dues_table():
    CONN.execute("""
        CREATE TABLE IF NOT EXISTS party_dues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            due_date TEXT,
            party TEXT,
            due_type TEXT,
            total_amount REAL,
            settled_amount REAL DEFAULT 0,
            note TEXT,
            created_at TEXT
        )
    """)
    CONN.commit()

ensure_dues_table()

def load_dues():
    return pd.read_sql_query(
        "SELECT * FROM party_dues ORDER BY due_date DESC, id DESC", CONN
    )

def add_due(due_date, party, due_type, total_amount, settled_amount=0, note=""):
    CONN.execute(
        """
        INSERT INTO party_dues
        (due_date, party, due_type, total_amount, settled_amount, note, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(due_date),
            str(party).strip(),
            str(due_type),
            float(total_amount or 0),
            float(settled_amount or 0),
            str(note or "").strip(),
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    CONN.commit()

def delete_due_ids(ids):
    if not ids:
        return
    q = ",".join("?" for _ in ids)
    CONN.execute(f"DELETE FROM party_dues WHERE id IN ({q})", ids)
    CONN.commit()

def party_payment_summary(df):
    columns = [
        "Party", "Received From Party", "Paid To Party",
        "Net Cash Flow", "Transactions"
    ]
    if df is None or df.empty:
        return pd.DataFrame(columns=columns)

    work = df.copy()
    work["party"] = work["party"].fillna("").astype(str).str.strip()
    work = work[work["party"] != ""]
    if work.empty:
        return pd.DataFrame(columns=columns)

    summary = (
        work.pivot_table(
            index="party",
            columns="direction",
            values="amount",
            aggfunc="sum",
            fill_value=0
        )
        .reset_index()
    )
    if "IN" not in summary.columns:
        summary["IN"] = 0.0
    if "OUT" not in summary.columns:
        summary["OUT"] = 0.0

    counts = work.groupby("party").size().rename("Transactions").reset_index()
    summary = summary.merge(counts, on="party", how="left")
    summary["Net Cash Flow"] = summary["IN"] - summary["OUT"]
    summary = summary.rename(columns={
        "party": "Party",
        "IN": "Received From Party",
        "OUT": "Paid To Party",
    })
    summary = summary[columns].sort_values(
        ["Paid To Party", "Received From Party"],
        ascending=[False, False]
    ).reset_index(drop=True)
    return summary

def dues_with_remaining(dues):
    if dues is None or dues.empty:
        return pd.DataFrame(columns=[
            "id","due_date","party","due_type","total_amount",
            "settled_amount","remaining","note","created_at"
        ])
    d = dues.copy()
    d["total_amount"] = pd.to_numeric(d["total_amount"], errors="coerce").fillna(0)
    d["settled_amount"] = pd.to_numeric(d["settled_amount"], errors="coerce").fillna(0)
    d["remaining"] = (d["total_amount"] - d["settled_amount"]).clip(lower=0)
    return d

def build_excel_export(transactions, dues):
    """Create a polished, multi-sheet Excel accounting report."""
    out = io.BytesIO()

    tx = transactions.copy() if transactions is not None else pd.DataFrame()
    d = dues_with_remaining(dues)
    party_summary = party_payment_summary(tx)

    total_received = float(tx.loc[tx["direction"] == "IN", "amount"].sum()) if not tx.empty else 0.0
    total_paid = float(tx.loc[tx["direction"] == "OUT", "amount"].sum()) if not tx.empty else 0.0
    receivable = float(d.loc[d["due_type"] == "RECEIVABLE", "remaining"].sum()) if not d.empty else 0.0
    payable = float(d.loc[d["due_type"] == "PAYABLE", "remaining"].sum()) if not d.empty else 0.0

    with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
        wb = writer.book

        title_fmt = wb.add_format({
            "bold": True, "font_size": 18, "font_color": "#FFFFFF",
            "bg_color": "#111827", "align": "left", "valign": "vcenter"
        })
        section_fmt = wb.add_format({
            "bold": True, "font_size": 12, "font_color": "#FFFFFF",
            "bg_color": "#4F46E5", "align": "left"
        })
        header_fmt = wb.add_format({
            "bold": True, "font_color": "#FFFFFF", "bg_color": "#1F2937",
            "border": 1, "border_color": "#374151", "align": "center",
            "valign": "vcenter"
        })
        text_fmt = wb.add_format({"border": 1, "border_color": "#E5E7EB"})
        money_fmt = wb.add_format({
            "num_format": '₹#,##0.00', "border": 1, "border_color": "#E5E7EB"
        })
        money_bold_fmt = wb.add_format({
            "bold": True, "num_format": '₹#,##0.00',
            "bg_color": "#F3F4F6", "border": 1, "border_color": "#D1D5DB"
        })
        label_fmt = wb.add_format({
            "bold": True, "font_color": "#374151", "bg_color": "#F9FAFB",
            "border": 1, "border_color": "#E5E7EB"
        })
        value_fmt = wb.add_format({
            "bold": True, "font_size": 12, "num_format": '₹#,##0.00',
            "border": 1, "border_color": "#E5E7EB"
        })
        green_fmt = wb.add_format({
            "bold": True, "font_color": "#047857", "bg_color": "#ECFDF5",
            "num_format": '₹#,##0.00', "border": 1, "border_color": "#A7F3D0"
        })
        red_fmt = wb.add_format({
            "bold": True, "font_color": "#B91C1C", "bg_color": "#FEF2F2",
            "num_format": '₹#,##0.00', "border": 1, "border_color": "#FECACA"
        })

        # ---- Summary ----
        ws = wb.add_worksheet("Summary")
        writer.sheets["Summary"] = ws
        ws.set_column("A:A", 28)
        ws.set_column("B:B", 20)
        ws.set_column("D:D", 28)
        ws.set_column("E:E", 20)
        ws.set_row(0, 30)
        ws.merge_range("A1:E1", "HISAB SOFTWARE PRO — ACCOUNT SUMMARY", title_fmt)

        summary_rows = [
            ("Total Received", total_received, "Total Paid", total_paid),
            ("Net Cash Movement", total_received - total_paid, "Transactions", len(tx)),
            ("લેવાના પૈસા બાકી (Receivable)", receivable, "દેવાના પૈસા બાકી (Payable)", payable),
        ]
        for i, (l1, v1, l2, v2) in enumerate(summary_rows, start=2):
            ws.write(i, 0, l1, label_fmt)
            ws.write(i, 1, v1, green_fmt if "Received" in l1 or "લેવાના" in l1 else value_fmt)
            ws.write(i, 3, l2, label_fmt)
            if l2 == "Transactions":
                ws.write_number(i, 4, int(v2), value_fmt)
            else:
                ws.write(i, 4, v2, red_fmt if "Paid" in l2 or "દેવાના" in l2 else value_fmt)

        ws.write(7, 0, "Party-wise Payment Snapshot", section_fmt)
        if not party_summary.empty:
            start = 8
            cols = list(party_summary.columns)
            for c, col in enumerate(cols):
                ws.write(start, c, col, header_fmt)
            for r, row in enumerate(party_summary.itertuples(index=False), start=start + 1):
                vals = list(row)
                for c, val in enumerate(vals):
                    if c in (1, 2, 3):
                        ws.write_number(r, c, float(val or 0), money_fmt)
                    elif c == 4:
                        ws.write_number(r, c, int(val or 0), text_fmt)
                    else:
                        ws.write(r, c, val, text_fmt)
            ws.autofilter(start, 0, start + len(party_summary), len(cols) - 1)
            ws.freeze_panes(start + 1, 0)
            ws.set_column("A:A", 32)
            ws.set_column("B:D", 20)
            ws.set_column("E:E", 14)

        # ---- Party Summary ----
        ps = wb.add_worksheet("Party Summary")
        writer.sheets["Party Summary"] = ps
        ps.merge_range("A1:E1", "PARTY-WISE PAYMENT SUMMARY", title_fmt)
        ps.set_row(0, 30)
        ps.set_column("A:A", 34)
        ps.set_column("B:D", 20)
        ps.set_column("E:E", 14)

        headers = ["Party", "Received From Party", "Paid To Party", "Net Cash Flow", "Transactions"]
        for c, h in enumerate(headers):
            ps.write(2, c, h, header_fmt)
        for r, row in enumerate(party_summary.itertuples(index=False), start=3):
            vals = list(row)
            ps.write(r, 0, vals[0], text_fmt)
            ps.write_number(r, 1, float(vals[1] or 0), money_fmt)
            ps.write_number(r, 2, float(vals[2] or 0), money_fmt)
            ps.write_number(r, 3, float(vals[3] or 0), money_fmt)
            ps.write_number(r, 4, int(vals[4] or 0), text_fmt)
        if len(party_summary):
            ps.autofilter(2, 0, 2 + len(party_summary), 4)
        ps.freeze_panes(3, 0)

        # ---- Transactions ----
        ts = wb.add_worksheet("Transactions")
        writer.sheets["Transactions"] = ts
        ts.merge_range("A1:N1", "LINE-BY-LINE TRANSACTIONS", title_fmt)
        ts.set_row(0, 30)

        tx_cols = [
            "S.No.", "Date", "Direction", "Party", "Category",
            "Payment Type", "Mode", "Money In", "Money Out",
            "Balance", "Reference No", "Details", "Account Source", "Source File"
        ]
        for c, h in enumerate(tx_cols):
            ts.write(2, c, h, header_fmt)

        if not tx.empty:
            tx_work = tx.copy().reset_index(drop=True)
            tx_work["Money In"] = tx_work.apply(
                lambda r: float(r["amount"]) if r["direction"] == "IN" else 0.0, axis=1
            )
            tx_work["Money Out"] = tx_work.apply(
                lambda r: float(r["amount"]) if r["direction"] == "OUT" else 0.0, axis=1
            )
            for idx, row in tx_work.iterrows():
                rr = idx + 3
                values = [
                    idx + 1,
                    row.get("txn_date", ""),
                    row.get("direction", ""),
                    row.get("party", ""),
                    row.get("category", ""),
                    row.get("payment_type", ""),
                    row.get("mode", ""),
                    row.get("Money In", 0),
                    row.get("Money Out", 0),
                    row.get("balance", None),
                    row.get("reference_no", ""),
                    row.get("details", ""),
                    row.get("account_source", ""),
                    row.get("source_file", ""),
                ]
                for c, val in enumerate(values):
                    if c in (7, 8, 9) and val is not None and not pd.isna(val):
                        ts.write_number(rr, c, float(val), money_fmt)
                    else:
                        ts.write(rr, c, "" if pd.isna(val) else val, text_fmt)
            ts.autofilter(2, 0, 2 + len(tx_work), len(tx_cols) - 1)

        ts.freeze_panes(3, 0)
        ts.set_column("A:A", 8)
        ts.set_column("B:C", 13)
        ts.set_column("D:D", 30)
        ts.set_column("E:G", 18)
        ts.set_column("H:J", 16)
        ts.set_column("K:K", 22)
        ts.set_column("L:L", 55)
        ts.set_column("M:N", 24)

        # ---- Receivable / Payable ----
        ds = wb.add_worksheet("Receivable Payable")
        writer.sheets["Receivable Payable"] = ds
        ds.merge_range("A1:I1", "લેવાના / દેવાના પૈસા બાકી", title_fmt)
        ds.set_row(0, 30)

        due_headers = [
            "S.No.", "ID", "Date", "Party", "Type",
            "Total Amount", "Settled", "Remaining", "Note"
        ]
        for c, h in enumerate(due_headers):
            ds.write(2, c, h, header_fmt)

        if not d.empty:
            d_work = d.reset_index(drop=True)
            for idx, row in d_work.iterrows():
                rr = idx + 3
                due_label = "લેવાના (Receivable)" if row["due_type"] == "RECEIVABLE" else "દેવાના (Payable)"
                values = [
                    idx + 1, row.get("id", ""), row.get("due_date", ""),
                    row.get("party", ""), due_label,
                    row.get("total_amount", 0), row.get("settled_amount", 0),
                    row.get("remaining", 0), row.get("note", "")
                ]
                for c, val in enumerate(values):
                    if c in (5, 6, 7):
                        ds.write_number(rr, c, float(val or 0), money_fmt)
                    else:
                        ds.write(rr, c, val, text_fmt)
            ds.autofilter(2, 0, 2 + len(d_work), len(due_headers) - 1)

        ds.freeze_panes(3, 0)
        ds.set_column("A:B", 8)
        ds.set_column("C:C", 14)
        ds.set_column("D:D", 32)
        ds.set_column("E:E", 23)
        ds.set_column("F:H", 18)
        ds.set_column("I:I", 45)

        # ---- Step-by-Step ----
        guide = wb.add_worksheet("Step-by-Step")
        writer.sheets["Step-by-Step"] = guide
        guide.merge_range("A1:D1", "HOW TO READ THIS EXCEL — STEP BY STEP", title_fmt)
        guide.set_row(0, 30)
        guide.set_column("A:A", 10)
        guide.set_column("B:B", 26)
        guide.set_column("C:C", 60)
        guide.set_column("D:D", 26)

        steps = [
            (1, "Summary", "Overall received, paid, net cash movement અને લેવાના/દેવાના બાકી જુઓ.", "Start here"),
            (2, "Party Summary", "કઈ party પાસેથી કેટલું મળ્યું અને કઈ partyને કેટલું payment આપ્યું તે જુઓ.", "Party-wise"),
            (3, "Transactions", "દરેક transaction line-by-line date, party, mode, amount, ref અને details સાથે જુઓ.", "Detailed ledger"),
            (4, "Receivable Payable", "લેવાના અને દેવાના બાકી amount party-wise જુઓ.", "Outstanding dues"),
            (5, "Filters", "દરેક data sheetમાં header filter use કરીને party/date/type પ્રમાણે શોધો.", "Use Excel filters"),
        ]
        guide_headers = ["Step", "Sheet", "What You Get", "Use"]
        for c, h in enumerate(guide_headers):
            guide.write(2, c, h, header_fmt)
        for r, row in enumerate(steps, start=3):
            for c, val in enumerate(row):
                guide.write(r, c, val, text_fmt)

    out.seek(0)
    return out.getvalue()


def insert_rows(df):
    if df is None or df.empty:
        return 0
    cols = [
        "txn_date","direction","party","details","payment_type","mode",
        "account_source","amount","balance","source",
        "category","reference_no","source_file"
    ]
    work = df.copy()
    for c in cols:
        if c not in work.columns:
            work[c] = None
    work = work[cols]
    work["created_at"] = datetime.now().isoformat(timespec="seconds")
    work.to_sql("transactions", CONN, if_exists="append", index=False)
    return len(work)

def load_transactions():
    return pd.read_sql_query(
        "SELECT * FROM transactions ORDER BY txn_date DESC, id DESC", CONN
    )

def delete_ids(ids):
    if not ids:
        return
    q = ",".join("?" for _ in ids)
    CONN.execute(f"DELETE FROM transactions WHERE id IN ({q})", ids)
    CONN.commit()

# ---------------- Helpers ----------------
def clean_col(c):
    c = str(c).strip().lower()
    c = re.sub(r"[\n\r]+", " ", c)
    c = re.sub(r"[^a-z0-9 ]+", " ", c)
    c = re.sub(r"\s+", " ", c).strip()
    return c

def find_col(cols, keys):
    for c in cols:
        cl = clean_col(c)
        if any(k in cl for k in keys):
            return c
    return None

def to_num(v):
    if pd.isna(v):
        return None
    s = str(v).strip()
    if not s:
        return None
    s = s.replace(",", "").replace("₹", "").replace("INR", "").replace("Rs.", "").replace("Rs", "")
    s = re.sub(r"[^\d.\-]", "", s)
    if not s or s in {".","-"}:
        return None
    try:
        return float(s)
    except:
        return None

def parse_date(v):
    if pd.isna(v):
        return ""
    s = str(v).strip()
    if not s:
        return ""
    for dayfirst in (True, False):
        try:
            dt = pd.to_datetime(s, dayfirst=dayfirst, errors="raise")
            return dt.strftime("%Y-%m-%d")
        except:
            pass
    return s

def detect_mode(details):
    d = (details or "").lower()

    # True cash movements first
    if re.search(r"\bby cash\b", d) or "cash deposit" in d or "cash withdrawal" in d:
        return "Cash"

    # Electronic rails stay electronic even if note contains the word "cash"
    if d.startswith("upi/") or "gpay" in d or "google pay" in d or "phonepe" in d or "paytm" in d:
        return "UPI"
    if "neft" in d:
        return "NEFT"
    if "imps" in d:
        return "IMPS"
    if "rtgs" in d:
        return "RTGS"
    if "card" in d or "pos" in d:
        return "Card"
    if "cheque" in d or "chq" in d:
        return "Cheque"
    if "atm cash" in d:
        return "Cash"
    if "transfer" in d or "bank" in d:
        return "Bank Transfer"
    return "Other"

def detect_payment_type(details, mode=None):
    d = (details or "").lower()
    mode = mode or detect_mode(details)

    if mode == "Cash":
        return "Cash"

    # Bank charges remain online/account-side entries
    if any(k in d for k in [
        "gchrg/amb", "account maintenance", "non-maint", "non-main of amb",
        "non-main", "cash handling chg"
    ]):
        return "Online"

    # Known electronic modes are always Online
    if mode in {"UPI", "NEFT", "IMPS", "RTGS", "Card", "Cheque", "Bank Transfer"}:
        return "Online"

    return "Online"

def _clean_party_name(s):
    s = re.sub(r"\s+", " ", str(s or "")).strip(" /:-")
    return s[:80]

def extract_party(details):
    d = re.sub(r"\s+", " ", str(details or "")).strip()
    dl = d.lower()

    if any(k in dl for k in [
        "gchrg/amb", "account maintenance", "non-maint", "non-main of amb",
        "non-main", "cash handling chg"
    ]):
        return "Bank Charges"

    if re.search(r"\bby cash\b", dl):
        return "Cash Deposit"

    if d.upper().startswith("UPI/"):
        parts = d.split("/")
        if len(parts) >= 3:
            return _clean_party_name(parts[2])

    if d.upper().startswith("IMPS:"):
        parts = d.split(":", 3)
        if len(parts) == 4:
            return _clean_party_name(parts[3])

    if d.upper().startswith("IMPS/"):
        parts = d.split("/")
        if len(parts) >= 3:
            return _clean_party_name(parts[2])

    if d.upper().startswith("MB/NEFT/") or d.upper().startswith("MB/RTGS/"):
        parts = d.split("/")
        if len(parts) >= 4:
            return _clean_party_name(parts[3])

    if d.upper().startswith("NEFT/"):
        parts = d.split("/")
        if len(parts) >= 3:
            return _clean_party_name(parts[2])

    # Generic fallback
    parts = re.split(r"[/|:\-*]", d)
    parts = [p.strip() for p in parts if p.strip()]
    if len(parts) >= 2:
        for p in reversed(parts):
            if len(p) >= 3 and not re.fullmatch(r"\d+", p):
                return _clean_party_name(p)
    return _clean_party_name(d)


def extract_reference(details):
    d = str(details or "")
    patterns = [
        r"\bUPI/([0-9A-Za-z]+)",
        r"\bIMPS:([0-9A-Za-z]+)",
        r"\bIMPS/([0-9A-Za-z]+)",
        r"\bNEFT/([0-9A-Za-z]+)",
        r"\bMB/(?:NEFT|RTGS)/([0-9A-Za-z]+)",
    ]
    for pat in patterns:
        m = re.search(pat, d, flags=re.I)
        if m:
            return m.group(1)
    return ""

def detect_category(details, direction=None):
    d = (details or "").lower()

    if any(k in d for k in [
        "gchrg/amb", "account maintenance", "non-maint", "non-main",
        "cash handling chg"
    ]):
        return "Bank Charge"

    if re.search(r"\bby cash\b", d):
        return "Cash Deposit"

    if any(k in d for k in ["facebook", "meta", "googleindiadigit", "marketing"]):
        return "Advertising / Marketing"

    if "paytm sett" in d or "cashfree" in d or "phonepe limited" in d:
        return "Settlement"

    if any(k in d for k in ["rtgs", "neft", "imps", "upi"]):
        return "Transfer / Payment"

    if direction == "IN":
        return "Income"
    if direction == "OUT":
        return "Expense"
    return "Other"

def duplicate_mask(df):
    if df is None or df.empty:
        return pd.Series(dtype=bool)

    existing = load_transactions()
    if existing.empty:
        return pd.Series([False] * len(df), index=df.index)

    existing_keys = set()
    for _, r in existing.iterrows():
        key = (
            str(r.get("txn_date", "")),
            str(r.get("direction", "")),
            round(float(r.get("amount") or 0), 2),
            str(r.get("reference_no") or "").strip().lower(),
            str(r.get("details") or "").strip().lower(),
        )
        existing_keys.add(key)

    flags = []
    for _, r in df.iterrows():
        key = (
            str(r.get("txn_date", "")),
            str(r.get("direction", "")),
            round(float(r.get("amount") or 0), 2),
            str(r.get("reference_no") or "").strip().lower(),
            str(r.get("details") or "").strip().lower(),
        )
        flags.append(key in existing_keys)
    return pd.Series(flags, index=df.index)


# ---------------- Saraswat PDF parser ----------------
_SARASWAT_DATE_RE = re.compile(
    r"^\d{2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4}$"
)

def _cluster_by_top(words, tol=1.5):
    clusters = []
    for w in sorted(words, key=lambda z: (z["top"], z["x0"])):
        if not clusters or abs(w["top"] - clusters[-1][0]["top"]) > tol:
            clusters.append([w])
        else:
            clusters[-1].append(w)
    return clusters

def _amount_from_words(words):
    if not words:
        return None
    s = "".join(w["text"] for w in sorted(words, key=lambda z: (z["top"], z["x0"])))
    s = re.sub(r"[^\d.\-,]", "", s).replace(",", "")
    if not s:
        return None
    try:
        return float(s)
    except Exception:
        return None

def parse_saraswat_pdf(file_bytes):
    """
    Parser for Saraswat Co-operative Bank Transaction Summary Report.
    Returns raw statement columns: Date, Narration, Debit, Credit, Balance.
    Returns None when the PDF is not this bank's supported format.
    """
    if pdfplumber is None:
        return None

    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            if not pdf.pages:
                return None

            first_text = pdf.pages[0].extract_text() or ""
            if "Saraswat Co-operative Bank" not in first_text or "Transaction Summary Report" not in first_text:
                return None

            rows = []

            for page_no, page in enumerate(pdf.pages, start=1):
                words = page.extract_words(
                    x_tolerance=1,
                    y_tolerance=2,
                    keep_blank_chars=False,
                )
                if not words:
                    continue

                # Date anchors are built only from the left/date column.
                date_words = [
                    w for w in words
                    if w["x0"] < 95 and 80 < w["top"] < page.height - 40
                ]

                anchors = []
                for cluster in _cluster_by_top(date_words, tol=1.5):
                    txt = " ".join(w["text"] for w in sorted(cluster, key=lambda z: z["x0"]))
                    if _SARASWAT_DATE_RE.match(txt):
                        y = sum(w["top"] for w in cluster) / len(cluster)
                        anchors.append((y, txt))

                anchors.sort(key=lambda x: x[0])

                for i, (y, date_txt) in enumerate(anchors):
                    prev_y = anchors[i - 1][0] if i > 0 else max(80, y - 25)
                    next_y = anchors[i + 1][0] if i + 1 < len(anchors) else min(page.height - 40, y + 30)

                    low = (prev_y + y) / 2
                    high = (y + next_y) / 2

                    band = [w for w in words if low <= w["top"] < high]

                    narration_words = [
                        w for w in band if 95 <= w["x0"] < 228
                    ]
                    narration = " ".join(
                        w["text"]
                        for w in sorted(narration_words, key=lambda z: (round(z["top"], 1), z["x0"]))
                    )
                    narration = re.sub(r"\s+", " ", narration).strip()

                    debit = _amount_from_words([
                        w for w in band
                        if 290 <= w["x0"] < 370 and re.search(r"\d", w["text"])
                    ])
                    credit = _amount_from_words([
                        w for w in band
                        if 370 <= w["x0"] < 440 and re.search(r"\d", w["text"])
                    ])
                    balance = _amount_from_words([
                        w for w in band
                        if w["x0"] >= 440 and re.search(r"\d", w["text"])
                    ])

                    # A valid transaction has exactly one debit/credit side and a balance.
                    if not narration:
                        continue
                    if (debit is None and credit is None) or (debit is not None and credit is not None):
                        continue
                    if balance is None:
                        continue

                    rows.append({
                        "Date": date_txt,
                        "Narration": narration,
                        "Debit": debit,
                        "Credit": credit,
                        "Balance": balance,
                    })

            if not rows:
                return None

            result = pd.DataFrame(rows, columns=["Date", "Narration", "Debit", "Credit", "Balance"])

            # Continuity check. If the detected rows are not internally consistent,
            # do not silently import bad data; allow generic fallback instead.
            for i in range(1, len(result)):
                prev_balance = float(result.iloc[i - 1]["Balance"])
                debit = result.iloc[i]["Debit"]
                credit = result.iloc[i]["Credit"]
                debit = 0.0 if pd.isna(debit) else float(debit)
                credit = 0.0 if pd.isna(credit) else float(credit)
                current = float(result.iloc[i]["Balance"])
                expected = round(prev_balance + credit - debit, 2)
                if abs(expected - current) > 0.01:
                    return None

            return result
    except Exception:
        return None

def normalize_statement_df(raw, account_name="Bank Statement"):
    if raw is None or raw.empty:
        return pd.DataFrame()

    df = raw.copy()
    df.columns = [str(c).strip() for c in df.columns]
    cols = list(df.columns)

    date_c = find_col(cols, ["date", "txn date", "transaction date", "value date", "posting date"])
    desc_c = find_col(cols, ["description", "narration", "particular", "remarks", "details", "transaction details"])
    debit_c = find_col(cols, ["debit", "withdrawal", "withdraw", "dr"])
    credit_c = find_col(cols, ["credit", "deposit", "cr"])
    amount_c = find_col(cols, ["amount", "transaction amount"])
    type_c = find_col(cols, ["type", "dr cr", "cr dr"])
    balance_c = find_col(cols, ["balance", "closing balance", "available balance"])

    out = []
    for _, r in df.iterrows():
        date = parse_date(r.get(date_c)) if date_c else ""
        details = str(r.get(desc_c, "") or "").strip() if desc_c else ""

        debit = to_num(r.get(debit_c)) if debit_c else None
        credit = to_num(r.get(credit_c)) if credit_c else None
        amt = to_num(r.get(amount_c)) if amount_c else None
        typ = str(r.get(type_c, "") or "").lower() if type_c else ""
        bal = to_num(r.get(balance_c)) if balance_c else None

        direction = ""
        amount = None

        if credit not in (None, 0):
            direction, amount = "IN", abs(credit)
        elif debit not in (None, 0):
            direction, amount = "OUT", abs(debit)
        elif amt not in (None, 0):
            amount = abs(amt)
            if any(k in typ for k in ["cr", "credit", "deposit"]):
                direction = "IN"
            elif any(k in typ for k in ["dr", "debit", "withdraw"]):
                direction = "OUT"
            else:
                raw_amt = to_num(r.get(amount_c))
                direction = "OUT" if (raw_amt is not None and raw_amt < 0) else "IN"

        if not amount:
            continue

        mode = detect_mode(details)
        payment_type = detect_payment_type(details, mode=mode)

        out.append({
            "txn_date": date,
            "direction": direction,
            "party": extract_party(details),
            "details": details,
            "payment_type": payment_type,
            "mode": mode,
            "account_source": account_name,
            "amount": amount,
            "balance": bal,
            "source": "Statement Upload",
            "category": detect_category(details, direction),
            "reference_no": extract_reference(details),
            "source_file": "",
        })
    return pd.DataFrame(out)

def parse_pdf(file_bytes):
    if pdfplumber is None:
        return pd.DataFrame(), "pdfplumber is not installed."

    # 1) Saraswat-specific parser first
    saraswat = parse_saraswat_pdf(file_bytes)
    if saraswat is not None and not saraswat.empty:
        return saraswat, None

    # 2) Existing generic table fallback
    all_rows = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables() or []
            for table in tables:
                if len(table) < 2:
                    continue
                header = [str(x or "").strip() for x in table[0]]
                for row in table[1:]:
                    if len(row) == len(header):
                        all_rows.append(dict(zip(header, row)))
    if all_rows:
        return pd.DataFrame(all_rows), None

    # 3) Existing generic text fallback
    text_rows = []
    date_pat = r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})"
    amt_pat = r"([\d,]+\.\d{2})"
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.splitlines():
                dm = re.search(date_pat, line)
                amts = re.findall(amt_pat, line)
                if dm and amts:
                    txn_amt = amts[-2] if len(amts) >= 2 else amts[-1]
                    bal = amts[-1] if len(amts) >= 2 else None
                    details = line.replace(dm.group(1), "", 1).strip()
                    text_rows.append({
                        "Date": dm.group(1),
                        "Description": details,
                        "Amount": txn_amt,
                        "Balance": bal,
                    })
    return pd.DataFrame(text_rows), None

def parse_uploaded(uploaded):
    name = uploaded.name.lower()
    data = uploaded.getvalue()
    if name.endswith(".csv"):
        raw = pd.read_csv(io.BytesIO(data))
        return raw, None
    if name.endswith(".xlsx") or name.endswith(".xls"):
        raw = pd.read_excel(io.BytesIO(data))
        return raw, None
    if name.endswith(".pdf"):
        return parse_pdf(data)
    return pd.DataFrame(), "Unsupported file type."

def manual_text_to_row(text):
    t = " ".join(str(text).strip().split())
    if not t:
        return None

    nums = re.findall(r"(?:₹\s*)?(\d[\d,]*(?:\.\d{1,2})?)", t)
    if not nums:
        return None
    amount = float(nums[-1].replace(",", ""))

    low = t.lower()
    out_words = [
        "apya", "aapya", "paid", "pay", "gave", "gaya", "expense",
        "kharch", "debit", "out", "nikalya", "withdraw"
    ]
    in_words = [
        "avya", "aavya", "malya", "received", "receive", "income",
        "credit", "in", "jama", "deposit"
    ]

    if any(w in low for w in out_words):
        direction = "OUT"
    elif any(w in low for w in in_words):
        direction = "IN"
    else:
        direction = "OUT"

    if any(w in low for w in ["cash", "rokda", "offline"]):
        ptype, mode = "Cash", "Cash"
    elif any(w in low for w in ["upi", "gpay", "phonepe", "paytm"]):
        ptype, mode = "Online", "UPI"
    elif "neft" in low:
        ptype, mode = "Online", "NEFT"
    elif "imps" in low:
        ptype, mode = "Online", "IMPS"
    elif "rtgs" in low:
        ptype, mode = "Online", "RTGS"
    elif any(w in low for w in ["bank", "transfer"]):
        ptype, mode = "Online", "Bank Transfer"
    else:
        ptype, mode = "Online", "Other"

    party = t
    party = re.sub(r"(₹\s*)?\d[\d,]*(?:\.\d{1,2})?", "", party)
    party = re.sub(
        r"\b(ne|thi|pasethi|pase thi|ko|se|to|from|cash|upi|gpay|phonepe|paytm|bank|transfer|apya|aapya|avya|aavya|malya|paid|received|jama|kharch)\b",
        " ", party, flags=re.I
    )
    party = re.sub(r"\s+", " ", party).strip(" -,:")
    party = party[:80] or "Manual Entry"

    return {
        "txn_date": datetime.now().strftime("%Y-%m-%d"),
        "direction": direction,
        "party": party,
        "details": t,
        "payment_type": ptype,
        "mode": mode,
        "account_source": "Manual",
        "amount": amount,
        "balance": None,
        "source": "Smart Text Entry",
        "category": detect_category(t, direction),
        "reference_no": extract_reference(t),
        "source_file": "",
    }

# ---------------- UI ----------------
st.markdown("""
<div class="hs-hero">
    <div>
        <div class="hs-title">💰 Hisab Software <span style="font-size:14px;color:#c4b5fd;vertical-align:middle;">PRO</span></div>
        <div class="hs-sub">Smart accounting • Bank statement automation • Cash & Online tracking • Party reports</div>
    </div>
    <div class="hs-badge">● LIVE FINANCE DASHBOARD</div>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs([
    "📊 Dashboard",
    "🏦 Statement Upload",
    "✍️ Smart Entry",
    "📒 Transactions",
    "👤 Party Report",
    "💳 લેવા / દેવા બાકી",
    "📂 Category Report",
    "⚙️ Data & Excel"
])

# ---------------- Dashboard ----------------
with tabs[0]:
    df = load_transactions()

    st.markdown("### Financial Overview")
    st.caption("તમારા બધા payment, cash flow અને latest balance એક જ જગ્યાએ.")

    f1, f2, f3, f4 = st.columns(4)
    view = f1.selectbox("Payment Type", ["All", "Online", "Cash"])
    mode_filter = f2.selectbox("Mode", ["All", "UPI", "IMPS", "NEFT", "RTGS", "Cash", "Bank Transfer", "Other"])
    date_from = f3.date_input("From", value=None)
    date_to = f4.date_input("To", value=None)

    f = df.copy()
    if not f.empty:
        if view != "All":
            f = f[f["payment_type"] == view]
        if mode_filter != "All":
            f = f[f["mode"] == mode_filter]
        dt = pd.to_datetime(f["txn_date"], errors="coerce")
        if date_from:
            f = f[dt.dt.date >= date_from]
            dt = pd.to_datetime(f["txn_date"], errors="coerce")
        if date_to:
            f = f[dt.dt.date <= date_to]

    total_in = f.loc[f["direction"]=="IN", "amount"].fillna(0).sum() if not f.empty else 0
    total_out = f.loc[f["direction"]=="OUT", "amount"].fillna(0).sum() if not f.empty else 0
    net = total_in - total_out
    count = len(f)

    a,b,c,d = st.columns(4)
    a.metric("Total Received", f"₹{total_in:,.2f}")
    b.metric("Total Paid", f"₹{total_out:,.2f}")
    c.metric("Net Movement", f"₹{net:,.2f}")
    d.metric("Transactions", f"{count:,}")

    online = f[f["payment_type"]=="Online"] if not f.empty else f
    cash = f[f["payment_type"]=="Cash"] if not f.empty else f

    e,fm,g = st.columns(3)
    e.metric("Online Net", f"₹{(online.loc[online['direction']=='IN','amount'].sum() - online.loc[online['direction']=='OUT','amount'].sum()) if not online.empty else 0:,.2f}")
    fm.metric("Cash Net", f"₹{(cash.loc[cash['direction']=='IN','amount'].sum() - cash.loc[cash['direction']=='OUT','amount'].sum()) if not cash.empty else 0:,.2f}")
    last_balance = None
    if not f.empty and f["balance"].notna().any():
        tmp = f.copy()
        tmp["_dt"] = pd.to_datetime(tmp["txn_date"], errors="coerce")
        tmp = tmp.sort_values(["_dt","id"])
        last_balance = tmp[tmp["balance"].notna()].iloc[-1]["balance"]
    g.metric("Latest Bank Balance", f"₹{float(last_balance):,.2f}" if last_balance is not None else "—")

    dues_df = dues_with_remaining(load_dues())
    receivable_due = dues_df.loc[dues_df["due_type"]=="RECEIVABLE","remaining"].sum() if not dues_df.empty else 0
    payable_due = dues_df.loc[dues_df["due_type"]=="PAYABLE","remaining"].sum() if not dues_df.empty else 0

    st.markdown("### Outstanding / બાકી")
    oa, ob = st.columns(2)
    oa.metric("લેવાના પૈસા બાકી", f"₹{receivable_due:,.2f}")
    ob.metric("દેવાના પૈસા બાકી", f"₹{payable_due:,.2f}")

    if not f.empty:
        show = f.copy()
        show.insert(0, "S.No.", range(1, len(show)+1))
        show["Money In"] = show.apply(lambda r: r["amount"] if r["direction"]=="IN" else 0, axis=1)
        show["Money Out"] = show.apply(lambda r: r["amount"] if r["direction"]=="OUT" else 0, axis=1)
        cols = [
            "S.No.","txn_date","party","category","payment_type","mode",
            "Money In","Money Out","balance","reference_no","details"
        ]
        st.dataframe(show[cols], width="stretch", hide_index=True)
    else:
        st.info("No transactions yet.")

# ---------------- Statement Upload ----------------
with tabs[1]:
    st.subheader("Bank Statement Import")
    st.caption("Statement upload કરો, transaction line-by-line review કરો અને પછી જ import કરો.")
    st.write("PDF / CSV / Excel upload કરો. દરેક transaction અલગ line માં clean preview થશે.")

    c1, c2 = st.columns(2)
    account_name = c1.text_input("Bank / Account Name", value="Main Bank")
    up = c2.file_uploader("Choose statement", type=["csv","xlsx","xls","pdf"])

    if up is not None:
        raw, err = parse_uploaded(up)
        if err:
            st.error(err)
        elif raw.empty:
            st.warning("No transactions detected.")
        else:
            normalized = normalize_statement_df(raw, account_name=account_name)
            if normalized.empty:
                st.warning("Transactions found but columns could not be normalized.")
            else:
                normalized["source_file"] = up.name
                normalized["reference_no"] = normalized["details"].apply(extract_reference)
                normalized["category"] = normalized.apply(
                    lambda r: detect_category(r["details"], r["direction"]), axis=1
                )
                normalized["Duplicate?"] = duplicate_mask(normalized)

                total_in = normalized.loc[normalized["direction"]=="IN","amount"].sum()
                total_out = normalized.loc[normalized["direction"]=="OUT","amount"].sum()
                closing = normalized["balance"].dropna().iloc[-1] if normalized["balance"].notna().any() else None

                m1,m2,m3,m4 = st.columns(4)
                m1.metric("Detected Rows", len(normalized))
                m2.metric("Received", f"₹{total_in:,.2f}")
                m3.metric("Paid", f"₹{total_out:,.2f}")
                m4.metric("Closing Balance", f"₹{float(closing):,.2f}" if closing is not None else "—")

                st.markdown("### Line-by-line Review")
                review = normalized.copy()
                review.insert(0, "S.No.", range(1, len(review)+1))
                review["Money In"] = review.apply(lambda r: r["amount"] if r["direction"]=="IN" else 0, axis=1)
                review["Money Out"] = review.apply(lambda r: r["amount"] if r["direction"]=="OUT" else 0, axis=1)

                display_cols = [
                    "S.No.","txn_date","party","category","payment_type","mode",
                    "Money In","Money Out","balance","reference_no","details","Duplicate?"
                ]
                st.dataframe(review[display_cols], width="stretch", hide_index=True)

                st.markdown("### Edit Before Import")
                edit_cols = [
                    "txn_date","direction","party","category","payment_type","mode",
                    "amount","balance","reference_no","details","account_source","source_file"
                ]
                edited = st.data_editor(
                    normalized[edit_cols],
                    width="stretch",
                    num_rows="dynamic",
                    column_config={
                        "direction": st.column_config.SelectboxColumn(options=["IN","OUT"]),
                        "payment_type": st.column_config.SelectboxColumn(options=["Online","Cash"]),
                        "mode": st.column_config.SelectboxColumn(options=["UPI","IMPS","NEFT","RTGS","Cash","Bank Transfer","Other"]),
                        "category": st.column_config.SelectboxColumn(options=[
                            "Income","Expense","Bank Charge","Cash Deposit","Settlement",
                            "Advertising / Marketing","Transfer / Payment","Other"
                        ]),
                    }
                )

                skip_dupes = st.checkbox("Skip duplicate transactions", value=True)
                if st.button("✅ Import Approved Rows", type="primary"):
                    work = edited.copy()
                    work["source"] = "Statement Upload"
                    if skip_dupes:
                        dm = duplicate_mask(work)
                        work = work[~dm]
                    n = insert_rows(work)
                    st.success(f"{n} transactions imported successfully.")

# ---------------- Smart Entry ----------------
with tabs[2]:
    st.subheader("Quick Smart Entry")
    st.caption("એક sentence લખો અને software transaction details auto-detect કરશે.")
    st.write('Example: **"Ravi ne 5000 cash apya"** / **"ABC pasethi 12500 UPI avya"**')
    txt = st.text_area("Write transaction", height=120)

    if txt:
        row = manual_text_to_row(txt)
        if row:
            preview = pd.DataFrame([row])
            edited = st.data_editor(preview, width="stretch")
            if st.button("➕ Save Entry", type="primary"):
                insert_rows(edited)
                st.success("Entry saved.")
        else:
            st.warning("Amount could not be detected.")

# ---------------- Transactions ----------------
with tabs[3]:
    st.subheader("Transaction Ledger")
    st.caption("Search, filter અને line-by-line transaction history.")
    df = load_transactions()

    if df.empty:
        st.info("No entries yet.")
    else:
        q1,q2,q3,q4 = st.columns(4)
        ptype = q1.selectbox("Type", ["All","Online","Cash"], key="tx_ptype")
        direction = q2.selectbox("IN / OUT", ["All","IN","OUT"], key="tx_dir")
        mode = q3.selectbox("Mode", ["All","UPI","IMPS","NEFT","RTGS","Cash","Bank Transfer","Other"], key="tx_mode")
        search = q4.text_input("Search Party / Details / Ref")

        f = df.copy()
        if ptype != "All":
            f = f[f["payment_type"] == ptype]
        if direction != "All":
            f = f[f["direction"] == direction]
        if mode != "All":
            f = f[f["mode"] == mode]
        if search:
            s = search.lower()
            mask = (
                f["party"].fillna("").str.lower().str.contains(s, regex=False) |
                f["details"].fillna("").str.lower().str.contains(s, regex=False) |
                f["reference_no"].fillna("").str.lower().str.contains(s, regex=False)
            )
            f = f[mask]

        show = f.copy()
        show.insert(0, "S.No.", range(1, len(show)+1))
        show["Money In"] = show.apply(lambda r: r["amount"] if r["direction"]=="IN" else 0, axis=1)
        show["Money Out"] = show.apply(lambda r: r["amount"] if r["direction"]=="OUT" else 0, axis=1)

        cols = [
            "S.No.","id","txn_date","party","category","payment_type","mode",
            "Money In","Money Out","balance","reference_no","details","source_file"
        ]
        st.dataframe(show[cols], width="stretch", hide_index=True)

        ids_text = st.text_input("Delete IDs (comma separated)")
        if st.button("Delete Selected IDs"):
            try:
                ids = [int(x.strip()) for x in ids_text.split(",") if x.strip()]
                delete_ids(ids)
                st.success("Deleted.")
            except:
                st.error("Invalid IDs.")

# ---------------- Party Report ----------------
with tabs[4]:
    st.subheader("Party Payment & Statement")
    st.caption("કઈ partyને કેટલું payment આપ્યું, કેટલું મળ્યું અને સંપૂર્ણ transaction history.")

    df = load_transactions()

    if df.empty:
        st.info("No entries yet.")
    else:
        summary = party_payment_summary(df)

        st.markdown("### Party-wise Payment Summary")
        st.caption("Paid To Party columnમાં દરેક partyને આપેલું કુલ payment દેખાશે.")
        summary_show = summary.copy()
        summary_show.insert(0, "S.No.", range(1, len(summary_show)+1))
        st.dataframe(
            summary_show,
            width="stretch",
            hide_index=True,
            column_config={
                "Received From Party": st.column_config.NumberColumn(format="₹ %.2f"),
                "Paid To Party": st.column_config.NumberColumn(format="₹ %.2f"),
                "Net Cash Flow": st.column_config.NumberColumn(format="₹ %.2f"),
            }
        )

        parties = list(summary["Party"])
        selected = st.selectbox("Select Party for Full Statement", parties)

        pf = df[df["party"] == selected].copy()
        rec = pf.loc[pf["direction"]=="IN","amount"].sum()
        paid = pf.loc[pf["direction"]=="OUT","amount"].sum()

        dues_all = dues_with_remaining(load_dues())
        party_dues = dues_all[dues_all["party"] == selected] if not dues_all.empty else dues_all
        party_receivable = (
            party_dues.loc[party_dues["due_type"]=="RECEIVABLE","remaining"].sum()
            if not party_dues.empty else 0
        )
        party_payable = (
            party_dues.loc[party_dues["due_type"]=="PAYABLE","remaining"].sum()
            if not party_dues.empty else 0
        )

        a,b,c,d = st.columns(4)
        a.metric("Received From Party", f"₹{rec:,.2f}")
        b.metric("Paid To Party", f"₹{paid:,.2f}")
        c.metric("લેવાના બાકી", f"₹{party_receivable:,.2f}")
        d.metric("દેવાના બાકી", f"₹{party_payable:,.2f}")

        pf = pf.sort_values(["txn_date","id"], ascending=[False,False])
        pf.insert(0, "S.No.", range(1, len(pf)+1))
        pf["Money In"] = pf.apply(lambda r: r["amount"] if r["direction"]=="IN" else 0, axis=1)
        pf["Money Out"] = pf.apply(lambda r: r["amount"] if r["direction"]=="OUT" else 0, axis=1)

        st.markdown("### Line-by-line Party Transactions")
        st.dataframe(
            pf[[
                "S.No.","txn_date","category","payment_type","mode",
                "Money In","Money Out","balance","reference_no","details"
            ]],
            width="stretch",
            hide_index=True
        )

        if not party_dues.empty:
            st.markdown("### Party Outstanding Details")
            due_show = party_dues.copy()
            due_show["Type"] = due_show["due_type"].map({
                "RECEIVABLE": "લેવાના (Receivable)",
                "PAYABLE": "દેવાના (Payable)"
            })
            due_show = due_show[[
                "id","due_date","Type","total_amount","settled_amount","remaining","note"
            ]]
            st.dataframe(
                due_show,
                width="stretch",
                hide_index=True,
                column_config={
                    "total_amount": st.column_config.NumberColumn("Total", format="₹ %.2f"),
                    "settled_amount": st.column_config.NumberColumn("Settled", format="₹ %.2f"),
                    "remaining": st.column_config.NumberColumn("Remaining", format="₹ %.2f"),
                }
            )

# ---------------- Receivable / Payable ----------------
with tabs[5]:
    st.subheader("લેવાના / દેવાના પૈસા બાકી")
    st.caption("Party પ્રમાણે outstanding amount add કરો અને remaining balance જુઓ.")

    dues = dues_with_remaining(load_dues())

    receivable_total = dues.loc[dues["due_type"]=="RECEIVABLE","remaining"].sum() if not dues.empty else 0
    payable_total = dues.loc[dues["due_type"]=="PAYABLE","remaining"].sum() if not dues.empty else 0

    m1, m2 = st.columns(2)
    m1.metric("લેવાના પૈસા બાકી", f"₹{receivable_total:,.2f}")
    m2.metric("દેવાના પૈસા બાકી", f"₹{payable_total:,.2f}")

    st.markdown("### Add / Update Outstanding")
    c1, c2, c3 = st.columns(3)
    due_date = c1.date_input("Date", key="due_date_input")
    party_name = c2.text_input("Party Name", key="due_party")
    due_type_label = c3.selectbox(
        "Type",
        ["લેવાના (Receivable)", "દેવાના (Payable)"],
        key="due_type_select"
    )

    c4, c5 = st.columns(2)
    total_amount = c4.number_input("Total Amount", min_value=0.0, step=100.0, key="due_total")
    settled_amount = c5.number_input("Already Settled / Paid", min_value=0.0, step=100.0, key="due_settled")
    note = st.text_input("Note / Details", key="due_note")

    remaining_preview = max(float(total_amount) - float(settled_amount), 0)
    st.info(f"Remaining / બાકી: ₹{remaining_preview:,.2f}")

    if st.button("➕ Save Outstanding Entry", type="primary"):
        if not party_name.strip():
            st.error("Party name જરૂરી છે.")
        elif total_amount <= 0:
            st.error("Total amount 0 કરતાં વધારે હોવું જોઈએ.")
        else:
            due_type = "RECEIVABLE" if "લેવાના" in due_type_label else "PAYABLE"
            add_due(
                due_date.strftime("%Y-%m-%d"),
                party_name,
                due_type,
                total_amount,
                settled_amount,
                note
            )
            st.success("Outstanding entry saved.")

    st.markdown("### Outstanding List")
    dues = dues_with_remaining(load_dues())
    if dues.empty:
        st.info("No outstanding entries yet.")
    else:
        f1, f2 = st.columns(2)
        type_filter = f1.selectbox(
            "Filter Type",
            ["All", "લેવાના (Receivable)", "દેવાના (Payable)"],
            key="due_filter_type"
        )
        party_search = f2.text_input("Search Party", key="due_party_search")

        show = dues.copy()
        if type_filter != "All":
            wanted = "RECEIVABLE" if "લેવાના" in type_filter else "PAYABLE"
            show = show[show["due_type"] == wanted]
        if party_search:
            show = show[
                show["party"].fillna("").str.contains(party_search, case=False, regex=False)
            ]

        show["Type"] = show["due_type"].map({
            "RECEIVABLE": "લેવાના (Receivable)",
            "PAYABLE": "દેવાના (Payable)"
        })
        show.insert(0, "S.No.", range(1, len(show)+1))

        st.dataframe(
            show[[
                "S.No.","id","due_date","party","Type",
                "total_amount","settled_amount","remaining","note"
            ]],
            width="stretch",
            hide_index=True,
            column_config={
                "total_amount": st.column_config.NumberColumn("Total Amount", format="₹ %.2f"),
                "settled_amount": st.column_config.NumberColumn("Settled", format="₹ %.2f"),
                "remaining": st.column_config.NumberColumn("Remaining / બાકી", format="₹ %.2f"),
            }
        )

        delete_due_text = st.text_input("Delete Outstanding IDs (comma separated)")
        if st.button("Delete Outstanding IDs"):
            try:
                ids = [int(x.strip()) for x in delete_due_text.split(",") if x.strip()]
                delete_due_ids(ids)
                st.success("Outstanding entries deleted.")
            except Exception:
                st.error("Invalid IDs.")

# ---------------- Category Report ----------------
with tabs[6]:
    st.subheader("Category Analytics")
    st.caption("Expense અને income કઈ categoryમાં કેટલું છે તે જુઓ.")
    df = load_transactions()

    if df.empty:
        st.info("No entries yet.")
    else:
        work = df.copy()
        work["category"] = work["category"].fillna("Other")
        summary = (
            work.groupby(["category","direction"])["amount"]
            .sum()
            .unstack(fill_value=0)
            .reset_index()
        )
        if "IN" not in summary.columns:
            summary["IN"] = 0
        if "OUT" not in summary.columns:
            summary["OUT"] = 0
        summary["Net"] = summary["IN"] - summary["OUT"]
        summary = summary.rename(columns={"IN":"Received","OUT":"Paid"})
        st.dataframe(summary, width="stretch", hide_index=True)

# ---------------- Data / Backup ----------------
with tabs[7]:
    st.subheader("Data, Excel & Backup")
    st.caption("Full accounting report Excelમાં step-by-step અને line-by-line export કરો.")

    df = load_transactions()
    dues = load_dues()

    st.markdown("### Excel Report")
    st.write(
        "Excel fileમાં **Summary, Party Summary, Transactions, "
        "Receivable Payable અને Step-by-Step** sheets આવશે."
    )

    excel_bytes = build_excel_export(df, dues)
    st.download_button(
        "⬇️ Download Complete Excel Report",
        data=excel_bytes,
        file_name=f"hisab_complete_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
    )

    st.markdown("### Step-by-Step")
    st.write(
        "1. **Summary** → overall received, paid અને બાકી જુઓ.  \n"
        "2. **Party Summary** → કઈ partyને કેટલું આપ્યું / મળ્યું જુઓ.  \n"
        "3. **Transactions** → દરેક transaction line-by-line જુઓ.  \n"
        "4. **Receivable Payable** → લેવાના / દેવાના outstanding જુઓ.  \n"
        "5. Excel header filtersથી party/date/type પ્રમાણે search કરો."
    )

    if not df.empty:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Raw CSV Backup",
            csv,
            "hisab_backup.csv",
            "text/csv"
        )

    st.info(f"Database: {DB_PATH}")
