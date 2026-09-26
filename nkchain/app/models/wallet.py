#This is the wallet model

from decimal import Decimal# Decimal should be used and not "float" for financial amounts.

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base



class Wallet(Base):#Every wallet belongs to a user
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(primary_key = True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),# this specific line creates the database relationship so that wallets belong to users.
        nullable = False
    )

    asset: Mapped[str] = mapped_column(
        String(10),
        nullable = False

    )

    balance: Mapped[Decimal] = mapped_column(# Once again, Decimal and NOT "float" should be used for financial related stuff.
        Numeric(30, 8),
        default = Decimal("0"),# this is an initial temporary column because a proper ledger will be treated as the ultimate source of truth
        nullable = False
    )