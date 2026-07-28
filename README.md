# Finz Accounting Data Pipeline

## Overview
This application ingests raw bank transaction data, normalizes it, detects duplicates,
classifies transactions using deterministic rules + Gemini AI, generates cash-basis P&L
statements, syncs approved transactions to QuickBooks Online, and reconciles the results.

## Architecture
- **Backend:** Python + FastAPI
- **Database:** MongoDB (Atlas)
- **AI Classification:** Google Gemini (gemini-2.0-flash)
- **Accounting Integration:** QuickBooks Online API (OAuth 2.0, sandbox)

## Data Model
- `raw_transactions` — untouched source rows, preserved for auditability
- `transactions` — normalized transaction records with classification, review, and sync status
- `chart_of_accounts` — QBO account definitions used as the allowed classification list
- `learned_mappings` — vendor description patterns mapped to corrected accounts
- `qbo_tokens` — OAuth access/refresh tokens for the QuickBooks sandbox connection

## Normalization
Dates, amounts, currency, and descriptions are cleaned and standardized. Raw records are
preserved separately from normalized records so original source data is never altered,
per the challenge requirements.

## Duplicate Handling
Transactions are matched on `source_transaction_id` + `bank_account`. Duplicates are
flagged (`duplicate: true`) rather than deleted, preserving them for auditability.

## Classification
Deterministic rules run first (owner capital, transfers, known vendors like Google Ads)
since these don't require AI judgment. Everything else is classified by Gemini, which
returns a transaction type, suggested QBO account, confidence score, and explanation.
Gemini's output is validated against the allowed transaction types and the actual chart
of accounts before being accepted — invalid or low-confidence classifications are flagged
`needs_review` rather than silently accepted.

## Review Workflow
Individual transactions can be reviewed and corrected via `PATCH /transactions/{id}/classification`.
Given the time constraints of this challenge, a bulk-approve endpoint
(`POST /transactions/approve-all-classified`) was also added to approve all successfully
classified, non-duplicate transactions at once — the underlying per-transaction endpoints
support full manual review and correction.

## Corrections Memory
When a user's correction differs from Gemini's original suggestion, the pattern is saved
to `learned_mappings` so repeated vendors classify consistently going forward.

## P&L Methodology
Generated in Python (not AI) as: Net Revenue = Revenue − Refunds; Gross Profit = Net Revenue
− COGS; Net Profit = Gross Profit − Operating Expenses. Transfers, owner activity, duplicates,
and fixed-asset purchases are excluded. Generated for April, May, June, and the full quarter.

## QuickBooks Integration
OAuth 2.0 authorization code flow against the sandbox. Approved transactions are synced as
QBO Deposits (income) or Purchases (expenses). [State honestly here: e.g. "Account ID mapping
between our internal chart_of_accounts and QuickBooks' internally-assigned account IDs is
simplified due to time constraints — a production version would fetch and store the actual
QBO account ID after creating each account via API rather than relying on defaults."]

## Idempotency
Before syncing, each transaction's `qbo_sync_status` is checked — already-synced transactions
are skipped, preventing duplicate posting on repeated sync runs.

## Reconciliation
Compares the application's internally generated P&L against QuickBooks' own Profit & Loss
report (pulled via the Reports API) for each month and the full quarter, reporting the
difference and a match/mismatch status per account.

## Assumptions
- [List anything you assumed — e.g. "Assumed cash-basis accounting throughout, per the
  Company Setup sheet." / "Assumed Deposit/Purchase transaction types were sufficient
  without needing Journal Entries."]

## Known Limitations
- [Be honest here — e.g. "QBO account ID mapping is simplified." / "Bulk-approve was used
  instead of full manual review of all 200 transactions due to time constraints." /
  "Reconciliation shows [match/a mismatch of $X] — [your best explanation if you saw one]."]

## AI Usage Note
Used OpenAI Codex and Claude to scaffold FastAPI structure, MongoDB integration, QuickBooks
OAuth flow, and Gemini classification logic. Used Gemini (gemini-2.0-flash) for transaction
classification within the app itself. Personally validated: the duplicate detection logic
against the dataset's intentionally overlapping source files, the normalization output
against the raw source data, and the P&L calculations against a manual spot-check of several
transactions.

## Setup Instructions
1. Clone the repo: `git clone [your repo URL]`
2. Create a Python virtual environment: `python3 -m venv .venv && source .venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt` (or install packages listed in
   the codebase: fastapi, uvicorn, pymongo, motor, google-generativeai, pandas, openpyxl,
   python-dotenv, requests, python-multipart)
4. Create a `.env` file with: `MONGODB_URI`, `MONGODB_DATABASE`, `GEMINI_API_KEY`,
   `QBO_CLIENT_ID`, `QBO_CLIENT_SECRET`, `QBO_REDIRECT_URI`, `QBO_REALM_ID`, `QBO_ENVIRONMENT`
5. Run the backend: `uvicorn backend.app.main:app --reload`
6. Visit `http://127.0.0.1:8000/docs` for the full interactive API.