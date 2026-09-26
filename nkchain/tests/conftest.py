#this is the pytest configuration
#every test gets a fresh database schema
#no test leaves garbage behind for the subsequent tests

"""
it goes like this: Test starts -> Create tables -> Open database Session ->
Run test -> Close session -> Delete Tables -> Test Finished

"""
import pytest

from app.database.connection import Base
from app.database.test_connection import TestSessionLocal, test_engine

from app.models import User, Wallet
from app.models.ledger.entry import LedgerEntry
from app.models.ledger.transaction import LedgerTransaction

@pytest.fixture
def db():
    Base.metadata.create_all(bind = test_engine)

    session = TestSessionLocal()

    try:
        yield session

    finally:
        session.close()
        Base.metadata.drop_all(bind = test_engine)

