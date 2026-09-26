# nkchain

`nkchain` is a Python-based cryptocurrency payment and settlement engine built with FastAPI and PostgreSQL. It uses double-entry accounting to ensure every transaction is accurate, balance-checked, and protected against double-spending.

## What It Does

* **Double-Entry Ledger:** Every transaction creates matching debit and credit entries. Wallet balances are calculated dynamically from the ledger.
* **Double-Spend Protection:** Uses PostgreSQL row locking (`with_for_update`) to prevent two transactions from spending the same funds at the exact same microsecond.
* **Idempotency:** Ensures duplicate network requests or retries won't process the same payment twice.
* **Transaction States:** Tracks payment lifecycles clearly using `PENDING`, `COMPLETED`, `FAILED`, and `REVERSED` states.
* **Automated Testing:** Fully tested with `pytest` covering balance checks, rollbacks, and API endpoints.

## Tech Stack

* **Language:** Python 3.14+
* **Framework:** FastAPI, Pydantic
* **Database:** PostgreSQL, SQLAlchemy
* **Testing:** Pytest, HTTPX

## Quick Start

###1. Install Dependencies

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

### 2. Configure environment
   
Copy .env.example to .env and configure your local PostgreSQL database URL: cp .env.example .env

### 3. Create Test Database
   
Ensure PostgreSQL is running locally and create a dedicated database for testing: CREATE DATABASE chainledger_test_db;

###4. Run Automated Tests

Execute the full integration test suite to verify double-entry rules, balance checks, and row locking: python -m pytest
