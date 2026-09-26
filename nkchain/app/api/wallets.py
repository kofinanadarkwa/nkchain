#this code is what creates the Wallet API
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from app.database.connection import get_db
from app.models.wallet import Wallet
from app.schemas.wallet import WalletCreate, WalletResponse



router = APIRouter(prefix = "/wallets", tags = ["Wallets"])


@router.post("/", response_model = WalletResponse)
def create_wallet(
    wallet_data: WalletCreate,
    db: Session = Depends(get_db)
):

    wallet = Wallet(
        user_id = wallet_data.user_id,
        asset = wallet_data.asset
    )

    db.add(wallet)
    db.commit()
    db.refresh(wallet)

    return wallet

