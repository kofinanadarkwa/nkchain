#this is the code that makes up the transfer API

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError


from app.database.connection import get_db
from app.models.wallet import Wallet
from app.schemas.transfer import TransferCreate, TransferResponse
from app.services.ledger_service import create_transfer

#the below five imports were added later and seperately from the above imports.
#they were added so that the get_wallet_balance function in the code below is able to run in this file
#they were copied from C:\nkchain\tests\test_ledger.py
#and the initial reason why added the get_wallet_balance function in the first place was because I already had the create_transfer import
"""
And another reason why I added the get_wallet_balance function is because so that I don't have to add this code:

from app.services.ledger_service import(
    create_transfer,
    get_wallet_balance
    )"""


from decimal import Decimal
from sqlalchemy import func
#the ledger is the ultimate source of truth for wallet balances.
#
from sqlalchemy.orm import Session

from app.models.ledger.entry import LedgerEntry
from app.models.ledger.transaction import LedgerTransaction


router = APIRouter(
    prefix = "/transfers",
    tags = ["Transfers"],

)

@router.post("/", response_model = TransferResponse)
def create_transfer_endpoint(
    transfer_data: TransferCreate,
    db: Session = Depends(get_db)

    ):

    if transfer_data.sender_wallet_id == transfer_data.receiver_wallet_id:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Sender and receiver wallets must be different"
        )

    sender_wallet = db.get(
        Wallet,
        transfer_data.sender_wallet_id
    )

    receiver_wallet = db.get(
    Wallet,
    transfer_data.receiver_wallet_id
    )

    if sender_wallet is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Sender wallet not found"
        )

    if receiver_wallet is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Receiver wallet not found"

        )

    if sender_wallet.asset != transfer_data.asset:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Sender Wallet asset does not match transfer asset"

        )

    if receiver_wallet.asset != transfer_data.asset:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Receiver wallet asset does not match transfer asset"
        )

    #either the provided referenced should be used or a unique reference key should be generated
    reference = transfer_data.reference or f"transfer-{uuid4()}"

    try:
        transaction = create_transfer(
            db = db,
            reference = reference,
            sender_wallet_id = sender_wallet.id,
            receiver_wallet_id = receiver_wallet.id,
            asset = transfer_data.asset,
            amount = transfer_data.amount
        )

        db.commit()

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = str(error),

        )

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = f"Transaction with reference '{reference}' already exists."
        )
    return TransferResponse(
        transaction_id = transaction.id,
        reference = transaction.reference,
        status = transaction.status,

    )




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


#the below block of code is a test that I added after get_wallet_balance:

def test_wallet_balance_from_ledger(db):
    wallet = Wallet(
        user_id = 1,
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
    
"""
#this tests the most basic case which is:
No ledger entries -> Balance = 0
"""