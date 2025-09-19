from pydantic import BaseModel, Field

# A Pydantic model for User Symptom Query
class UserQuery(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    query: str = Field(..., description="User's symptom query")

# A Pydantic model for the response to the user
class QueryResponse(BaseModel):
    response: str = Field(..., description="The response to the user's query")
