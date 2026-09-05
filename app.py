
import streamlit as st
import pandas as pd
import sqlite3
import re
from datetime import datetime
from pathlib import Path
import io

DB_PATH = Path(__file__).with_name("hisab.db")

try:
    import pdfplumber
except Exception:
    pdfplumber = None

st.set_page_config(page_title="Hisab Software", page_icon="💰", layout="wide")

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

def insert_rows(df):
    if df is None or df.empty:
        return 0
    cols = ["txn_date","direction","party","details","payment_type","mode",
            "account_source","amount","balance","source"]
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

def detect_payment_type(details):
    d = (details or "").lower()
    if any(k in d for k in ["cash", "atm cash", "cash withdrawal", "cash deposit"]):
        return "Cash"
    return "Online"

def detect_mode(details):
    d = (details or "").lower()
    if "upi" in d or "gpay" in d or "google pay" in d or "phonepe" in d or "paytm" in d:
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
    if "cash" in d or "atm" in d:
        return "Cash"
    if "transfer" in d or "bank" in d:
        return "Bank Transfer"
    return "Other"

def extract_party(details):
    d = str(details or "").strip()
    # Try common banking separators
    parts = re.split(r"[/|:\-*]", d)
    parts = [p.strip() for p in parts if p.strip()]
    if len(parts) >= 2:
        for p in reversed(parts):
            if len(p) >= 3 and not re.fullmatch(r"\d+", p):
                return p[:80]
    return d[:80] if d else ""

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
                # negative amount is normally debit
                raw_amt = to_num(r.get(amount_c))
                direction = "OUT" if (raw_amt is not None and raw_amt < 0) else "IN"

        if not amount:
            continue

        payment_type = detect_payment_type(details)
        mode = detect_mode(details)

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
        })
    return pd.DataFrame(out)

def parse_pdf(file_bytes):
    if pdfplumber is None:
        return pd.DataFrame(), "pdfplumber is not installed."
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

    # Generic text fallback for common bank statement layouts
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
                    # fallback assumes last amount balance, previous amount txn amount
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

    # Amount: support 5000, 5,000, 5000.50, ₹5000
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
        direction = "OUT"  # safer default for "X ne 5000"

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

    # Find party roughly before common relation words or amount
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
    }

# ---------------- UI ----------------
st.title("💰 Hisab Software")
st.caption("Bank statement upload + smart manual entry + Online/Cash/All payment tracking")

tabs = st.tabs(["📊 Dashboard", "🏦 Statement Upload", "✍️ Smart Entry", "📒 All Entries", "⚙️ Data"])

with tabs[0]:
    df = load_transactions()
    c1, c2, c3 = st.columns(3)
    view = c1.selectbox("View", ["All", "Online", "Cash"])
    date_from = c2.date_input("From", value=None)
    date_to = c3.date_input("To", value=None)

    f = df.copy()
    if view != "All":
        f = f[f["payment_type"] == view]
    if date_from:
        f = f[pd.to_datetime(f["txn_date"], errors="coerce").dt.date >= date_from]
    if date_to:
        f = f[pd.to_datetime(f["txn_date"], errors="coerce").dt.date <= date_to]

    total_in = f.loc[f["direction"]=="IN", "amount"].fillna(0).sum() if not f.empty else 0
    total_out = f.loc[f["direction"]=="OUT", "amount"].fillna(0).sum() if not f.empty else 0
    fund = total_in - total_out

    a,b,c = st.columns(3)
    a.metric("Total Received", f"₹{total_in:,.2f}")
    b.metric("Total Paid", f"₹{total_out:,.2f}")
    c.metric("Current Fund", f"₹{fund:,.2f}")

    if not f.empty:
        show = f[["txn_date","direction","party","details","payment_type","mode","account_source","amount","balance"]]
        st.dataframe(show, use_container_width=True, hide_index=True)
    else:
        st.info("No entries yet.")

with tabs[1]:
    st.subheader("Upload Bank Statement")
    st.write("Supported: CSV, Excel, PDF. First review the detected rows, then import.")
    account_name = st.text_input("Bank / Account Name", value="Main Bank")
    up = st.file_uploader("Choose statement", type=["csv","xlsx","xls","pdf"])

    if up is not None:
        raw, err = parse_uploaded(up)
        if err:
            st.error(err)
        elif raw.empty:
            st.warning("No table/transactions detected. This PDF may need a bank-specific template.")
        else:
            st.markdown("**Raw statement preview**")
            st.dataframe(raw.head(30), use_container_width=True)

            normalized = normalize_statement_df(raw, account_name=account_name)
            if normalized.empty:
                st.warning("Rows were found, but debit/credit/amount columns could not be detected.")
                st.info("Tip: CSV/Excel export from your bank gives the best result.")
            else:
                st.markdown("**Detected transactions — edit before import**")
                edited = st.data_editor(
                    normalized,
                    use_container_width=True,
                    num_rows="dynamic",
                    column_config={
                        "payment_type": st.column_config.SelectboxColumn(options=["Online","Cash"]),
                        "direction": st.column_config.SelectboxColumn(options=["IN","OUT"]),
                    }
                )
                if st.button("✅ Import Approved Rows", type="primary"):
                    n = insert_rows(edited)
                    st.success(f"{n} transactions imported.")

with tabs[2]:
    st.subheader("Smart Manual Entry")
    st.write('Example: **"Ravi ne 5000 cash apya"** or **"ABC customer pasethi 12500 UPI avya"**')
    txt = st.text_area("Write one transaction", height=120, placeholder="Ravi ne 5000 cash apya")

    if txt:
        row = manual_text_to_row(txt)
        if row:
            preview = pd.DataFrame([row])
            st.markdown("**Detected entry — edit if needed**")
            edited = st.data_editor(
                preview,
                use_container_width=True,
                column_config={
                    "payment_type": st.column_config.SelectboxColumn(options=["Online","Cash"]),
                    "direction": st.column_config.SelectboxColumn(options=["IN","OUT"]),
                }
            )
            if st.button("➕ Save Entry", type="primary"):
                insert_rows(edited)
                st.success("Entry saved.")
        else:
            st.warning("Amount could not be detected.")

with tabs[3]:
    df = load_transactions()
    st.subheader("All Entries")
    if df.empty:
        st.info("No entries yet.")
    else:
        c1,c2,c3 = st.columns(3)
        view2 = c1.selectbox("Payment Type", ["All","Online","Cash"], key="all_view")
        direction2 = c2.selectbox("IN / OUT", ["All","IN","OUT"])
        party_q = c3.text_input("Search Party / Details")

        f = df.copy()
        if view2 != "All":
            f = f[f["payment_type"] == view2]
        if direction2 != "All":
            f = f[f["direction"] == direction2]
        if party_q:
            mask = (
                f["party"].fillna("").str.contains(party_q, case=False, regex=False) |
                f["details"].fillna("").str.contains(party_q, case=False, regex=False)
            )
            f = f[mask]

        st.dataframe(f, use_container_width=True, hide_index=True)

        st.markdown("**Delete selected IDs**")
        ids_text = st.text_input("Enter IDs separated by comma, e.g. 12,13")
        if st.button("Delete IDs"):
            try:
                ids = [int(x.strip()) for x in ids_text.split(",") if x.strip()]
                delete_ids(ids)
                st.success("Deleted.")
            except:
                st.error("Invalid IDs.")

with tabs[4]:
    st.subheader("Backup / Export")
    df = load_transactions()
    if not df.empty:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV Backup", csv, "hisab_backup.csv", "text/csv")
    st.warning("Your data is stored locally in hisab.db beside the app.py file.")
