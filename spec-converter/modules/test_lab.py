from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from modules.configuration import ConfigurationParameters

class ContactsItem(BaseModel):
    """Contact information for person / party involved in the testing or an aspect of the testing."""
    firstName: str = Field(..., description="Contact's first name.", max_length=255)
    lastName: str = Field(..., description="Contact's last name.", max_length=255)
    organization: Optional[str] = Field(None, description="Organization or company the contact is associated with.", max_length=255)
    email: str = Field(..., description="Contact's email address", max_length=255)
    phone: Optional[str] = Field(None, description="Contact's phone number.", max_length=255)

    class Config:
        extra = "forbid"

class TestLab(BaseModel):
    name: str = Field(..., description="Name of the test lab.", max_length=255)
    address: Optional[str] = Field(None, description="Address of the test lab.", max_length=255)
    contacts: Optional[List[ContactsItem]] = Field(None, description="Company contacts for this product.")