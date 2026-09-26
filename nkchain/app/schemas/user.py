from datetime import datetime

from pydantic import BaseModel#pydantic's core job is validation.



class UserCreate(BaseModel):# This validates json data that is coming in 
    username: str



class UserResponse(BaseModel):# this describes data that is going out and the what API returns to the client
    id: int  
    username: str
    created_at: datetime
#the output is filtered and shaped so only these fields are sent back

    model_config = {
        "from_attributes": True #from_attributes is what makes this work with my SQLAlchemy model
    }

"""the whole point of this code is so that when someone sends something in Json, FastApi can  
    validate it using UserCreate. And when a database User object is returned, FastApi can convert
    it into UserResponse.
    """