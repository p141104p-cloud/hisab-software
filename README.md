
# Hisab Software

A local accounting / payment tracker for:

- Bank statement upload (CSV, Excel, PDF)
- Auto-detect Date, Narration, Debit, Credit, Amount, Balance
- Auto classify IN / OUT
- Auto classify Online / Cash
- Detect UPI / NEFT / IMPS / RTGS / Card / Cash / Bank Transfer
- Review + edit detected rows before import
- Smart text entry:
  - `Ravi ne 5000 cash apya`
  - `ABC customer pasethi 12500 UPI avya`
- Dashboard filters: All / Online / Cash
- Party/detail search
- SQLite local database
- CSV backup export

## Install

1. Install Python 3.10+
2. Open Terminal / CMD in this folder
3. Run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app will open in your browser.

## Important

Bank PDF layouts vary by bank. CSV/Excel exports are the most reliable.
The PDF parser is generic and may need a bank-specific template for some banks.
Always review detected rows before pressing Import.

## Data

Your entries are stored in:
`hisab.db`

Keep a backup of this file or export CSV regularly.
