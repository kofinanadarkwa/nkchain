# NKChain

NKChain is a Python-based cryptocurrency settlement engine built around a double-entry ledger. It provides an API for managing users, wallets, and transfers, with a focus on financial integrity, transaction consistency, and reliable payment processing.

## Current Status

**Part 1: Double-Entry Core and Settlement Engine**

The internal ledger and settlement core has been implemented.

### Core Features

- **Double-Entry Accounting:** Transfers generate corresponding debit and credit entries.
- **Ledger as the Source of Truth:** Wallet balances are calculated from ledger entries rather than treated as the authoritative financial record.
- **Balance Validation:** Transfers are checked against available balances to prevent overspending.
- **Concurrency Protection:** PostgreSQL row-level locking helps prevent conflicting transfers from spending the same funds concurrently.
- **Idempotency:** Unique transaction references help prevent duplicate transaction execution.
- **Transaction Lifecycle:** Transactions use the states `PENDING`, `COMPLETED`, `FAILED`, and `REVERSED`.
- **Automated Testing:** Pytest tests cover ledger balance equality, rollback behaviour, insufficient funds, idempotency, and API integration.

## Architecture

NKChain separates API handling, financial business logic, and persistent data storage.

- **API Layer:** FastAPI endpoints handle requests involving users, wallets, and transfers.
- **Ledger Service:** Contains the core transfer-processing and accounting logic.
- **Database Layer:** PostgreSQL stores application records and ledger entries.
- **Ledger-Based Balance Calculation:** Account balances are derived from recorded ledger activity.

## Technology Stack

- Python 3.14
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pytest
- PgAdmin4

## Requirements

- Python 3.14
- PostgreSQL

## Setup

Clone the repository:

```bash
git clone https://github.com/kofinanadarkwa/nkchain.git
cd nkchain
```

Create and activate a virtual environment.

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the environment:

```powershell
# Windows
copy .env.example .env
```

```bash
# macOS / Linux
cp .env.example .env
```

Update `.env` with your PostgreSQL connection details.

Complete any required database initialization or migrations before running the application.

## Running Tests

```bash
python -m pytest
```

## Project Goals

NKChain is a learning and portfolio project exploring the engineering principles behind cryptocurrency settlement systems, including double-entry accounting, transaction consistency, concurrency control, and idempotent processing.
