#this is the LedgerEntry model

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base



class LedgerEntry(Base):
    __tablename__ = "ledger_entries"


    id: Mapped[int] = mapped_column(primary_key = True)

    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("ledger_transactions.id"),
        nullable = False
    )

    wallet_id: Mapped[int] = mapped_column(
        ForeignKey("wallets.id"),
        nullable = False
    )

    asset: Mapped[str] = mapped_column(
        String(10),
        nullable = False
    )

    debit: Mapped[Decimal] = mapped_column(
        Numeric(30, 8),
        default = Decimal("0"),
        nullable = False
    )

    credit: Mapped[Decimal] = mapped_column(
        Numeric(30, 8),
        default = Decimal("0"),
        nullable = False
    )

#this is where the actual accounting information lives
#only one accounting convention will be used so as to make things simple

"""
the non negotiable invariant is: SUM(debits) == SUM(credits)
"""
