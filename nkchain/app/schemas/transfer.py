#this is the transfer schema
from typing import Optional# this import is what allows TransferCreate to accept an optional reference parameter

from decimal import Decimal

from pydantic import BaseModel


class TransferCreate(BaseModel):
    sender_wallet_id: int
    receiver_wallet_id: int
    asset: str
    amount: Decimal
    reference: Optional[str] = None # Idempotency key provided from client


class TransferResponse(BaseModel):
    transaction_id: int
    reference: str
    status: str

"""
the transfer schema is separate from the waller schema because they are different
concepts.

Therefore, as long as nkchain is concerned, these two concepts should be kept separate
"""

