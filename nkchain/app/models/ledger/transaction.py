#This is the LedgerTransaction model

#This code represents the financial event itself. The transaction.
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column


from app.database.connection import Base

#The transaction is the container for the accounting event.

class LedgerTransaction(Base):
    __tablename__ = "ledger_transactions"

    id: Mapped[int] = mapped_column(primary_key = True)

    reference: Mapped[str] = mapped_column(
        String(100),
        unique = True,
        nullable = False
    )

    """
    The below "status" block is added so that the transactions statuses of every
    transaction can be known and tracked. for now, there are generally four statuses"""
    status: Mapped[str] = mapped_column(
        String(20),
        default = "COMPLETED",
        nullable = False
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        default = lambda: datetime.now(timezone.utc),
        nullable = False
)

#this entire code represents the financial event itself
#This code doesn't contain the actual debit and credit amounts yet.
#Those will live in LedgerEntry.

#the transaction is the container for the accounting event.

