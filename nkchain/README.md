# nkchain

nkchain is a simple python based crytocurrency settlement and double entry ledger system.

## Current status

As of 19/09/2026:
Part 1 - Foundation of Project:

These are done:

-FastApi application
-health check endpoint
-python virtual environment
-dependency management


As of 24/09/2026:
These are done:

-Project Foundation
-PostgreSQL database
-Database models
-wallet model
-Decimal-based financial amounts
-Pydantic API schemas
-User API
-Wallet API
-FastAPI rounting
-Database tables
-Ledger transaction model
-Ledger entry model
-Double-entry accounting concept
-Ledger service
-Basic ledger validation

current architecture:
                         nkchain
                             │
              ┌──────────────┴──────────────┐
              │                             │
           FastAPI                     PostgreSQL
              │                             │
       ┌──────┴──────┐              ┌───────┴────────┐
       │             │              │                │
     Users        Wallets         Users           Wallets
                                    │
                                    │
                              Ledger Transactions
                                    │
                                    ↓
                              Ledger Entries
                                    │
                              ┌─────┴─────┐
                              ↓           ↓
                           Debit       Credit


As of 26/09/2026:
This is the current architecture and status:

Part 1 - Double-Entry Core and Settlement Engine(completed):

-FastAPI Application and Endpoint: 
      The API routes for managing users, wallets and for processing transfers.

-Double-Entry Ledger Engine: 
      Every single transaction without exception always creates matching debits and credits.

-The Ledger as the source of truth: 
      Wallet balances are calculated dynamically from immutable ledger entries.

-Financial Integrity Safeguards:
      -Pre-transfer balance checks prevent overdraws.

      -Concurrency protection is ensured through pessimistic PostgreSQL row locks( this is the "with_for_update" function in the "app/services/ledger_service.py" file).

      -Strict idempotent transaction execution is ensured via unique reference tracing

      -Lifecycle state machine( this is just the four states of "COMPLETED", "PENDING", "FAILED", and "REVERSED").

-Test Suite:
      These are automated tests using "pytest" covering double-entry balance equality, rollback guarantees, insufficient funds, idempotency and API integration.

##setup and running

#the environment:
      -python 3.14+
      -postgresql
      

#for running tests and file and folder creation and navigation:
      powershell and "python -m pytest" run within powershell


