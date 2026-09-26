#This the code that creates the User model

from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base



class User(Base):
    __tablename__ = "users"#This tells SQLAlchemy to create a PostgreSQL table called "users"

    id: Mapped[int] = mapped_column(primary_key = True)#This line makes every user get a unique ID
    username: Mapped[str] = mapped_column(#this allows the user to create a unique username

        String(50),
        unique = True,# This line is what makes sure that more than one person cannot have the same username
        nullable = False,# This line is what makes sure that a user cannot be created without creating a username first

)

    created_at: Mapped[datetime] = mapped_column(

        DateTime(timezone = True), # This makes the PostgreSQL store the column as "TIMESTAMP WITH TIME ZONE" which pairs properly with timezone-aware datetimes.
        
        default = lambda: datetime.now(timezone.utc),# this line allows Base to have a timezone-aware datetime
        # The "lambda" is needed so that SQLAlchemy calls the function each time a row is inserted.
        nullable = False,

)