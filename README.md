# nkchain

nkchain is a simple Python-based cryptocurrency settlement and double-entry ledger system.

## Current Status

**As of 26/09/2026** — Part 1: Double-Entry Core and Settlement Engine (completed)

- **FastAPI Application and Endpoints**: API routes for managing users, wallets, and processing transfers.
  
- **Double-Entry Ledger Engine**: Every transaction, without exception, creates matching debits and credits.
  
- **The Ledger as Source of Truth**: Wallet balances are calculated dynamically from immutable ledger entries.
  
- **Financial Integrity Safeguards**:
  - Pre-transfer balance checks prevent overdraws.
    
  - Concurrency protection via pessimistic PostgreSQL row locks (`with_for_update` in `app/services/ledger_service.py`).
    
  - Strict idempotent transaction execution via unique reference tracking.
    
  - Lifecycle state machine with four states: `COMPLETED`, `PENDING`, `FAILED`, `REVERSED`.
    
- **Test Suite**: Automated tests using `pytest`, covering double-entry balance equality, rollback guarantees, insufficient funds, idempotency, and API integration.

## Requirements

- Python 3.14
- PostgreSQL

## Setup

```bash
# clone the repo
git clone https://github.com/<your-username>/nkchain.git
cd nkchain

# create and activate a virtual environment
python -m venv venv
venv\Scripts\activate      # Windows (PowerShell)
source venv/bin/activate   # macOS/Linux

# install dependencies
pip install -r requirements.txt

# configure environment variables
copy .env.example .env     # Windows
cp .env.example .env       # macOS/Linux
# then edit .env with your PostgreSQL connection details
```

## Running Tests

```bash
python -m pytest
```

