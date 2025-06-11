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


class ConfigurationArtifactsItem(BaseModel):
    """Paths, relative to the root of the archive, to configuration files relating to this component."""
    name: str = Field(..., description="Short name or reference for the file and its contents.", max_length=255)
    path: str = Field(..., description="Path, relative to the root of the results archive, to the file or object.", max_length=1023)
    description: Optional[str] = Field(None, description="Detailed description of the file and its contents.", max_length=4095)

    class Config:
        extra = "forbid"


class TestbedComponentsItem(BaseModel):
    """Array of DUT/SUT components, including test and measurement equipment."""
    componentDescription: Optional[str] = Field(None, description="Description of the component role with the testing (i.e. O-DU, O-RU, RIC, UE, etc.).", max_length=255)
    manufacturerName: Optional[str] = Field(None, description="Company producing the product (hardware or software)", max_length=255)
    manufacturerModel: Optional[str] = Field(None, description="Product modle number or other unique identifier.", max_length=255)
    serialNumber: Optional[str] = Field(None, description="Product serial number.", max_length=255)
    testbedInventoryId: Optional[str] = Field(None, description="Opaque ID number used by lab for invetory management.", max_length=255)
    softwareVersion: Optional[str] = Field(None, description="Software version that was installed during the testing.", max_length=255)
    hardwareVersion: Optional[str] = Field(None, description="Hardware version that was used during the testing.", max_length=255)
    firmwareVersion: Optional[str] = Field(None, description="Firmware version that was installed during the testing.", max_length=255)
    contacts: Optional[List[ContactsItem]] = Field(None, description="Company contacts for this product.")
    configurationArtifacts: Optional[List[ConfigurationArtifactsItem]] = Field(None, description="Paths, relative to the root of the archive, to configuration files relating to this component.", min_items=1)
    configurationNotes:Optional[str] = Field(None, description="notes during the testing.", max_length=255)
    configurationParameters: Optional[ConfigurationParameters] = Field(None, description="Configuration parameters used during the testing.")
    class Config:
        extra = "forbid"