#this code creates the wallet schemas

from decimal import Decimal

from pydantic import BaseModel #For validation



class WalletCreate(BaseModel):
    user_id: int
    asset: str



class WalletResponse(BaseModel):
    id: int
    user_id: int
    asset: str
    balance: Decimal

    model_config = {
        "from_attributes": True
    }