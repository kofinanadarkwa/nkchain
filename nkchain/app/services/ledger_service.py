#the commented out blocks are among the first version of ledger_service.py
# the rest of the code is the final balanced transaction function



from decimal import Decimal

from sqlalchemy import func
#the ledger is the ultimate source of truth for all wallet balances. At all points in time.
#
from sqlalchemy.orm import Session

from app.models.ledger.entry import LedgerEntry
from app.models.ledger.transaction import LedgerTransaction
from app.models.wallet import Wallet


def create_transfer(
    db: Session,
    reference: str,
    sender_wallet_id: int,
    receiver_wallet_id: int,
    asset: str,
    amount: Decimal        
    ):
    
    if amount <= 0:
        raise ValueError("Transfer amount must be greater than zero")

    
    """if debit < 0 or credit < 0:
        raise ValueError("Debit and credit cannot be negative")#this is the most extreme edge-case

    if debit == 0 and credit == 0:
        raise ValueError("Either debit or credit must have a value")

    if debit > 0 and credit > 0:
        raise ValueError("An entry cannot have both debit and credit")
    """


    """
    The below block of code is for Concurrency Protection. This means that if two transfers from the same wallet cannot happen at the same exact
    millisecond. the block locks the sender's wallet record.

    the code locks the sender's wallet row for UPDATE in order to prevent concurrent race conditions
    """
    sender_wallet = (
        db.query(Wallet)
        .filter(Wallet.id == sender_wallet_id)
        .with_for_update()#this exact line is for concurrency protection with pessimistic locking.
        #.with_for_update() acquires a pessimistic row-level lock on the sender's wallet row in PostgreSQL before reading the balance.
        .first()
    )

    if not sender_wallet:
        raise ValueError("Sender wallet not found")



    """
    this below block is a small block of code that fetches the sender's current balance and raises a
    ValueError if the requested transfer amount exceeds what they hold. 

    This makes sure that they cannor send more than what they have."""    
    sender_balance = get_wallet_balance(
        db = db,
        wallet_id = sender_wallet_id,
        asset = asset
    )
    if sender_balance < amount:
        raise ValueError("Insufficient funds for transfer")



    #this block creates the ledger transaction and entries
    transaction = LedgerTransaction(
        reference = reference,
        status = "COMPLETED"#line added to track the status of the transaction
    )


    db.add(transaction)#in this line, sqlalchemy knows that we want to inset the transaction, but the database hasn't necessarily assigned its ID yet.
    db.flush()# this line sends the pending INSERT to PostgreSQL without commiting the overal database transaction.


    sender_entry = LedgerEntry(
        transaction_id = transaction.id,
        wallet_id = sender_wallet_id,
        asset = asset,
        debit = Decimal("0"),
        credit = amount
    )

    receiver_entry = LedgerEntry(
        transaction_id = transaction.id,
        wallet_id = receiver_wallet_id,
        asset = asset,
        debit = amount,
        credit = Decimal("0"),
    )
    """entry = LedgerEntry(
        transaction_id = transaction.id,
        wallet_id = wallet_id,
        asset = asset,
        debit = debit,
        credit = credit

    )

"""

    db.add(sender_entry)
    db.add(receiver_entry)
    
    total_debits = receiver_entry.debit
    total_credits = sender_entry.credit

    if total_debits != total_credits:
        raise ValueError("Ledger transaction is not balanced")


    return transaction

#this code is what makes this project a financial system and not just some normal wallet app
#this code is one of the biggest differences between them

#now, each transaction operation can behave as one atomic database transaction
#there should be no partial financial transactions at all costs. 

# #it's do all or do nothing.

#the service creates the financial operation and the caller controls the larger database transaction


def get_wallet_balance(#this is a wallet balance calculation function that depends on from sqlalchemy import func
        #the ledger is the ultimate source of truth for wallet balances.
        #balances are calculated from an immutable ledger history rather than trusting mutable balance columns.
        db: Session,
        wallet_id: int,
        asset: str
    ) -> Decimal:

    total_debits = (
        db.query(func.coalesce(func.sum(LedgerEntry.debit), 0))
        .filter(
            LedgerEntry.wallet_id == wallet_id,
            LedgerEntry.asset == asset
        )
        .scalar()
    )

    total_credits = (
        db.query(func.coalesce(func.sum(LedgerEntry.credit), 0))
        .filter(
            LedgerEntry.wallet_id == wallet_id,
            LedgerEntry.asset == asset
        )
        .scalar()
    )

    return Decimal(str(total_debits)) - Decimal(str(total_credits))


#the below block of code is a funding operation.
#It is the answer to how sender wallets get initial money in the first place
def fund_wallet(
    db: Session,
    wallet_id:int,
    asset: str,
    amount: Decimal,
    reference: str
    ):

    if amount <= 0:
        raise ValueError("Funding amount must be greater than zero")

    transaction = LedgerTransaction(
        reference = reference,
        status = "COMPLETED"#added to track the status of the transaction

    )

    db.add(transaction)
    db.flush()#

    funding_entry = LedgerEntry(
        transaction_id = transaction.id,
        wallet_id = wallet_id,
        asset = asset,
        debit = amount,
        credit = Decimal("0")

    )

    db.add(funding_entry)

    return transaction