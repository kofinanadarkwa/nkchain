#the whole point of this file is to test the endpoint end-to-end via FastAPI's TestClient

import pytest
from fastapi.testclient import TestClient
from decimal import Decimal

from app.main import app
from app.database.connection import get_db
from app.models import User, Wallet
from app.services.ledger_service import fund_wallet

@pytest.fixture
def client(db):
    #this block overrides get_db dependency to use the isolated test database session
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_api_transfer_success_and_duplicate_conflict(client, db):
    #this block sets up users and wallets
    alice = User(username = "api_alice")
    bob = User(username = "api_bob")
    db.add_all([alice, bob])
    db.commit()

    alice_wallet = Wallet(user_id = alice.id, asset = "USDT")
    bob_wallet = Wallet(user_id = bob.id, asset = "USDT")
    db.add_all([alice_wallet, bob_wallet])
    db.commit()

    #this funds alice's wallet with 200 USDT
    fund_wallet(
        db = db,
        wallet_id = alice_wallet.id,
        asset = "USDT",
        amount = Decimal("200"),
        reference = "api-fund-alice"
    )
    db.commit()

    payload = {#this is a dictionary
        "sender_wallet_id": alice_wallet.id,
        "receiver_wallet_id": bob_wallet.id,
        "asset": "USDT",
        "amount": "50.00",
        "reference": "unique-api-ref-001"
    }


    #this is the first transfer request which will be successful
    response = client.post("/transfers/", json = payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["reference"] == "unique-api-ref-001"


    #this is an intentional duplicate Idempotency Key that will trigger a 409 conflict
    duplicate_response = client.post("/transfers/", json = payload)
    assert duplicate_response.status_code == 409
    assert "already exists" in duplicate_response.json()["detail"]

def test_api_transfer_insufficient_funds(client, db):
    alice = User(username = "api_alice_poor")
    bob = User(username = "api_bob_poor")
    db.add_all([alice, bob])
    db.commit()

    alice_wallet = Wallet(user_id = alice.id, asset = "USDT")
    bob_wallet = Wallet(user_id = bob.id , asset = "USDT")
    db.add_all([alice_wallet, bob_wallet])
    db.commit()

    payload = {
        "sender_wallet_id": alice_wallet.id,
        "receiver_wallet_id": bob_wallet.id,
        "asset": "USDT",
        "amount": "50.00"
    }

    response = client.post("/transfers/", json = payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient funds for transfer"