#this is the test database configuration

import os 

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

test_engine = create_engine(TEST_DATABASE_URL)

TestSessionLocal = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = test_engine
)

#this is a seperate engine from the production engine

