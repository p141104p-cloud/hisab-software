
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
    "📂 Category Report",
    "⚙️ Data"
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
    st.subheader("Party Statement")
    st.caption("કોઈ પણ party સાથે કેટલું આવ્યું અને કેટલું ગયું તેનો સંપૂર્ણ હિસાબ.")
    df = load_transactions()

    if df.empty:
        st.info("No entries yet.")
    else:
        parties = sorted([p for p in df["party"].dropna().unique() if str(p).strip()])
        selected = st.selectbox("Select Party", parties)

        pf = df[df["party"] == selected].copy()
        rec = pf.loc[pf["direction"]=="IN","amount"].sum()
        paid = pf.loc[pf["direction"]=="OUT","amount"].sum()

        a,b,c = st.columns(3)
        a.metric("Received From Party", f"₹{rec:,.2f}")
        b.metric("Paid To Party", f"₹{paid:,.2f}")
        c.metric("Net", f"₹{rec-paid:,.2f}")

        pf.insert(0, "S.No.", range(1, len(pf)+1))
        st.dataframe(
            pf[["S.No.","txn_date","direction","category","mode","amount","balance","reference_no","details"]],
            width="stretch",
            hide_index=True
        )

# ---------------- Category Report ----------------
with tabs[5]:
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
with tabs[6]:
    st.subheader("Data & Backup")
    st.caption("તમારા accounting recordsની backup copy રાખો.")
    df = load_transactions()

    if not df.empty:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Full CSV Backup", csv, "hisab_backup.csv", "text/csv")

    st.info(f"Database: {DB_PATH}")
