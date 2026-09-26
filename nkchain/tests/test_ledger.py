#tests needs a safe database transaction that doesn't contaminate the real nkchain PostgreSQL database
#the accounting invariant is more fundamental than the API.

#the purpose of this code is to test the ledger without actually modifying the real nkchain database.

#so that is why a seperate postgreSQL database is used for tests.
#the second reason why a seperate database is used for tests is because automated tests will make and delete data repeatedly.

from decimal import Decimal

import pytest

from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.wallet import Wallet
from app.models.ledger.entry import LedgerEntry
from app.models.ledger.transaction import LedgerTransaction
from app.services.ledger_service import create_transfer


from app.services.ledger_service import(
    create_transfer,
    get_wallet_balance,
    fund_wallet#this specific import is what allows fund_wallet to be used below in the first place
)

def test_create_balanced_transfer(db): #this block of code tests that valid transactions work
    sender = User(username = "alice")
    receiver = User(username = "bob")
    
    db.add(sender)#these two db.add method calls can simply be db.add_all([sender, receiver])
    db.add(receiver)
    db.commit()

    sender_wallet = Wallet(#this entire block can be on a single line but for consistency and readability, I'll leave it like this
        user_id = sender.id,
        asset = "USDT",
    )

    receiver_wallet = Wallet(#this entire block can be on a single line but for consistency and readability, I'll leave it like this
        user_id = receiver.id,
        asset = "USDT",
    )

    db.add(sender_wallet)# these two db.add method calls can simply be db.add_all([sender_wallet, receiver_wallet]) but for readability and consistency sake, i'll leave them like this

    db.add(receiver_wallet)
    db.commit()

    #the below block is added so that the sender is funded first so that they have the balance to make transactions in the first place
    fund_wallet(
        db = db,
        wallet_id = sender_wallet.id,
        asset = "USDT",
        amount = Decimal("200"),
        reference = "initial-funding"
    )
    db.commit()


    transaction = create_transfer(# this block executes transfers
        db = db,
        reference = "test-transfer-001",
        sender_wallet_id = sender_wallet.id,
        receiver_wallet_id = receiver_wallet.id,
        asset = "USDT",
        amount = Decimal("100"),
    )

    db.commit()

    entries = (
        db.query(LedgerEntry)
        .filter(LedgerEntry.transaction_id == transaction.id)
        .all()
    )

    assert len(entries) == 2

    total_debits = sum(entry.debit for entry in entries)
    total_credits = sum(entry.credit for entry in entries)

    assert total_debits == Decimal("100")
    assert total_credits == Decimal("100")
    assert total_debits == total_credits


#The below three functions test invalid transactions

def test_transfer_rejects_zero_amount(db):
    sender = User(username = "alice")
    receiver = User(username = "bob")


    db.add(sender)
    db.add(receiver)
    db.commit()

    sender_wallet = Wallet(
        user_id = sender.id,
        asset = "USDT"
    )

    receiver_wallet = Wallet(
        user_id = receiver.id,
        asset = "USDT"
    )

    db.add(sender_wallet)
    db.add(receiver_wallet)
    db.commit()

    with pytest.raises(ValueError, match = "Transfer amount must be greater than zero"):
        #pytest.raises() means that the code in this block is expected to throw a ValueError
        create_transfer(#if create_transfer doesn't reject the invalid amount, the test fails
            db = db,
            reference = "test-zero-transfer",
            sender_wallet_id = sender_wallet.id,
            receiver_wallet_id = receiver_wallet.id,
            asset = "USDT",
            amount = Decimal("0"),

        )


#the below block of code tests whether transactions without any money actually being sent are
# rejected.
def test_transfer_rejects_negative_amount(db):
    sender = User(username = "alice")
    receiver = User(username = "bob")

    db.add(sender)
    db.add(receiver)
    db.commit()

#both sender_wallet and receiver_wallet are both on top of the user_id function
    sender_wallet = Wallet(
        user_id = sender.id,
        asset = "USDT",

    )       

    receiver_wallet = Wallet(
        user_id = receiver.id,
        asset = "USDT",

    )

    db.add(sender_wallet)
    db.add(receiver_wallet)
    db.commit()

    with pytest.raises(ValueError, match = "Transfer amount must be greater than zero"):
        create_transfer(
            db = db,
            reference = "test-negative-transfer",
            sender_wallet_id = sender_wallet.id,
            receiver_wallet_id = receiver_wallet.id,
            asset = "USDT",
            amount = Decimal("-50"),
        )

"""
this is a succesful test:    

create_transfer()
       ↓
invalid amount
       ↓
ValueError
       ↓
pytest says PASS

"""

def test_failed_transaction_is_rolled_back(db):# this is the test rollback
    sender = User(username = "alice_rollback")
    receiver = User(username = "bob_rollback")

    db.add(sender)
    db.add(receiver)
    db.commit()

    sender_wallet = Wallet(
        user_id = sender.id,
        asset = "USDT",
    )

    receiver_wallet = Wallet(
        user_id = receiver.id,
        asset = "USDT",

    )

    db.add(sender_wallet)
    db.add(receiver_wallet)
    db.commit()

    #the below block of code is added so that the sender is funded first before a transfer and the balanced check is passed.
    fund_wallet(
        db = db,
        wallet_id = sender_wallet.id,
        asset = "USDT",
        amount = Decimal("100"),
        reference = "rollback-test-funding"
    )
    db.commit()


    try:
        create_transfer(
            db = db,
            reference = "test-rollback",
            sender_wallet_id = sender_wallet.id,
            receiver_wallet_id = receiver_wallet.id,
            asset = "USDT",
            amount = Decimal("100"),
        )

        #this simulates a failure after ledger entries have been created
        raise RuntimeError("Simulated database failure")

    except RuntimeError:
        db.rollback()

    transaction = (
        db.query(LedgerTransaction)
        .filter(
            LedgerTransaction.reference == "test-rollback"

        )
        .first()
    )

    assert transaction is None

"""
The sequence of this specific test is:

create_transfer()
       ↓
transaction created
       ↓
ledger entries created
       ↓
SIMULATED FAILURE
       ↓
db.rollback()
       ↓
everything disappears

"""

#when (reference = "test-rollback") is specifically searched for, "transaction is None" is expected because the database would roll the entire operation back

"""

db.rollback() is not in create_transfer() because nkchain operations will definitely become larger
if the ledger service independently commits or rolls back, it becomes difficult to make the entire operation atomic

so the higher level service will eventually control the transaction boundary.

"""

def test_wallet_balance_from_ledger(db):
    user = User(
        username = "balance_test_user"
    )

    db.add(user)
    db.commit()


    wallet = Wallet(
        user_id = user.id,
        asset = "USDT"
    )

    db.add(wallet)
    db.commit()


    balance = get_wallet_balance(
        db = db,
        wallet_id = wallet.id,
        asset = "USDT"
    )

    assert balance == Decimal("0")



#the below block is simply a test function
def test_fund_wallet(db):
    user = User(
        username = "funding_test_user"
    )

    db.add(user)
    db.commit()

    wallet = Wallet(
        user_id = user.id,
        asset = "USDT"
    )

    db.add(wallet)
    db.commit()

    fund_wallet(
        db = db,
        wallet_id = wallet.id,
        asset = "USDT",
        amount = Decimal("1000"),
        reference = "funding-test-001"
    )

    db.commit()

    balance = get_wallet_balance(
        db = db,
        wallet_id = wallet.id,
        asset = "USDT"
    )

    assert balance == Decimal("1000")


def test_transfer_rejects_insufficient_funds(db):
    alice = User(username = "alice_unfunded")
    bob = User(username = "bob_unfunded")
    db.add_all([alice, bob])
    db.commit()

    alice_wallet = Wallet(user_id = alice.id, asset = "USDT")
    bob_wallet = Wallet(user_id = bob.id, asset = "USDT")
    db.add_all([alice_wallet, bob_wallet])
    db.commit()

    #the below code is a test attempt to send 50 USDT with a wallet with no balance
    with pytest.raises(ValueError, match = "Insufficient funds for transfer"):
        create_transfer(
            db = db,
            reference = "test-insufficient-1",
            sender_wallet_id = alice_wallet.id,
            receiver_wallet_id = bob_wallet.id,
            asset = "USDT",
            amount = Decimal("50")
        )

def test_transfer_succeeds_with_sufficient_funds_and_rejects_overdraw(db):
    alice = User(username = "alice_funded")
    bob = User(username = "bob_funded")
    db.add_all([alice, bob])
    db.commit()

    alice_wallet = Wallet(user_id = alice.id, asset = "USDT")
    bob_wallet = Wallet(user_id = bob.id, asset = "USDT")
    db.add_all([alice_wallet, bob_wallet])
    db.commit()

    #the below block funds alice's wallet with 100 USDT just to test
    fund_wallet(
        db = db,
        wallet_id = alice_wallet.id,
        asset = "USDT",
        amount = Decimal("100"),
        reference = "funding-alice-001"
    )
    db.commit()

    #the below block is a test transfer of 40 USDT which should succeed
    create_transfer(
        db = db,
        reference = "transfer-alice-bob-001",
        sender_wallet_id = alice_wallet.id,
        receiver_wallet_id = bob_wallet.id,
        asset = "USDT",
        amount = Decimal("40")
    )

    db.commit()

    #assert is just a debugging keyword that helps in testing whether a specific condition in the code evaluates to True
    assert get_wallet_balance(db, alice_wallet.id, "USDT") == Decimal("60")
    assert get_wallet_balance(db, bob_wallet.id, "USDT") == Decimal("40")

    """the below block of code is a transfer attempt of 70 USDT which should definitely faile because the wallet only has 60 USDT left"""
    with pytest.raises(ValueError, match = "Insufficient funds for transfer"):
        create_transfer(
            db = db,
            reference = "transfer-alice-bob-002",#this simply means that alice is the sender and bob is the receiver of the test transfer of 70 USDT
            sender_wallet_id = alice_wallet.id,
            receiver_wallet_id = bob_wallet.id,
            asset = "USDT",
            amount = Decimal("70")
        )

"""The purpose of this below test transaction block is to verify that "create_transfer" and "fund_wallet" record
    transactions with the status "COMPLETED".
"""
def test_transaction_status_is_set_to_completed(db):
    user = User(username = "status_test_user")
    db.add(user)
    db.commit()

    wallet = Wallet(user_id = user.id, asset = "USDT")
    db.add(wallet)
    db.commit()

    tx = fund_wallet(
        db = db,
        wallet_id = wallet.id,
        asset = "USDT",
        amount = Decimal("500"),
        reference = "status-test-ref"
    )

    db.commit()

    assert tx.status == "COMPLETED"

def test_duplicate_reference_raises_integrity_error(db):
    user = User(username = "idempotency_user")
    db.add(user)
    db.commit()

    wallet = Wallet(user_id = user.id, asset = "USDT")
    db.add(wallet)
    db.commit()

    #this below block is the first attempt that succeeds
    fund_wallet(
        db = db,
        wallet_id = wallet.id,
        asset = "USDT",
        amount = Decimal("100"),
        reference = "unique-ref-100"
    )
    db.commit()

    #the below block is an intentional second attempt with the same reference
    #it fails the database unique constraint level

    with pytest.raises(IntegrityError):
        fund_wallet(
            db = db,
            wallet_id = wallet.id,
            asset = "USDT",
            amount = Decimal("100"),
            reference = "unique-ref-100"
        )

        db.commit()

    db.rollback()

    
