from pydantic import BaseModel, Field

class SmsReply(BaseModel):
    """
    A Pydantic model for validating the SMS reply form data.
    """
    From: str = Field(...)
    Body: str = Field(...)