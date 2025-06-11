from typing import List, Optional, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, HttpUrl

class Units(str, Enum):
    """Units of the value(s)."""
    BOOLEAN = "boolean"
    BPS = "bps"
    KBPS = "kbps"
    MBPS = "Mbps"
    GBPS = "Gbps"
    DB = "dB"
    DBM = "dBm"
    COUNT = "count"
    MILLISECOND = "millisecond"
    SECOND = "second"
    BPS_HZ = "bps/Hz"
    PERCENTAGE = "percentage"
    TEXT = "text"
    Watt = "W"


class ResultType(str, Enum):
    """A result. PASS/FAIL/etc. indicates the outcome of a test case, test metric, or test result."""
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    SKIP = "SKIP"


class TestStatus(str, Enum):
    """Status of the test case or test metric"""
    MANDATORY = "mandatory"
    CONDITIONALLY_MANDATORY = "conditionally.mandatory"
    OPTIONAL = "optional"


class DecoratedLinksItem(BaseModel):
    """A list of links to objects that have a display name, URL, and optionally a description."""
    displayName: str = Field(..., description="Text that is displayed as the link when rendered.", max_length=255)
    description: Optional[str] = Field(None, description="Longer, more descriptive text about the link and its contents.", max_length=1023)
    url: HttpUrl = Field(..., description="URL Path for the reference.")

    class Config:
        extra = "forbid"


class ArtifactsItem(BaseModel):
    """Paths, relative to the root of the archive, to files relating to the test."""
    name: str = Field(..., description="Short name or reference for the file and its contents.", max_length=255)
    path: str = Field(..., description="Path, relative to the root of the results archieve, to the file or object.", max_length=1023)
    description: str = Field(..., description="Detailed description of the file and its contents.", max_length=4095)

    class Config:
        extra = "forbid"


class MeasurementsItem(BaseModel):
    """Test measurements recorded during the test procedure.  Measurements are in addition to values recorded or required as part a test metric."""
    name: str = Field(..., description="Name of the measurement.", max_length=255)
    description: Optional[str] = Field(None, description="Description of the measurement values.", max_length=1023)
    values: List[Union[int, float, str, bool]] = Field(..., description="Actual measurement value(s).  Must be an arary, of at least 1 value.  All values must be in the same units.", min_items=1)
    units: Units = Field(..., description="Units of the measurement value(s).")
    references: Optional[List[DecoratedLinksItem]] = Field(None, description="Link(s) to defintiion of counter or measurement parameter within O-RAN ALLIANCE, 3GPP, or other specification(s).")

    class Config:
        extra = "forbid"


class MetricsItem(BaseModel):
    """Test metrics or requirements for the test case. (Mandatory for test case)"""
    description: str = Field(..., description="Text of the test metric or test requirement, per the test specification.", max_length=1023)
    measurements: List[MeasurementsItem] = Field(..., description="One or more measurements required to determine the outcome of the metric or requirement.", min_items=1)
    status: TestStatus = Field(..., description="Status of the test metric.")
    result: ResultType = Field(..., description="Result or outcome of the test metric or requirement.  PASS indicates the requirement of the metric is met.  FAIL indicates the requirement was of the metric was not met.  SKIP indicates the requirement was not evaluated.  WARN value should not be used for metrics.")

    class Config:
        extra = "forbid"


class TestNotesItem(BaseModel):
    """A list of notes about the parent object."""
    title: str = Field(..., description="Title of the notecard.", max_length=255)
    body: str = Field(..., description="Content of the notecard.", max_length=4095)

    class Config:
        extra = "forbid"



class Wg4IotProfile(BaseModel):
    """Values used within the IOT profile parameters, as defined by O-RAN ALLIANCE WG4. Copyright 2025 O-RAN ALLIANCE e.V. Licensed under the Standards Collaboration, Copyright License Version 1.0 (the 'License'); You may not use this file except in compliance with the License. You may obtain a copy of the License at https://www.o-ran.org/sccl"""
    wg4IotSpecificationVersion: str = Field(..., description="Version of the O-RAN ALLIANCE WG4.IOT.0 specification containing the profile values.", pattern=r"^[0-9][0-9][.][0-9][0-9]$")
    mPlaneIotProfileName: Optional[str] = Field(None, description="Name of the M-Plane IOT Profile, as defined within Annex A of the O-RAN ALLIANCE WG4.IOT.0 specification.", min_length=10, max_length=128)
    mPlaneIotProfileTestConfiguration: Optional[str] = Field(None, description="Name of the specific test configuration for the M-Plane IOT profile.", min_length=10, max_length=128)
    cusPlaneIotProfileName: Optional[str] = Field(None, description="Name of the CUS-Plane IOT Profile, as defined within Annex A of the O-RAN ALLIANCE WG4.IOT.0 specification.", min_length=10, max_length=128)
    cusPlaneIotProfileTestConfiguration: Optional[str] = Field(None, description="Name of the specific test configuration for the M-Plane IOT profile.", min_length=10, max_length=128)

    class Config:
        extra = "forbid"

class ContactsItem(BaseModel):
    """Contact information for person / party involved in the testing or an aspect of the testing."""
    firstName: str = Field(..., description="Contact's first name.", max_length=255)
    lastName: str = Field(..., description="Contact's last name.", max_length=255)
    organization: Optional[str] = Field(None, description="Organization or company the contact is associated with.", max_length=255)
    email: EmailStr = Field(..., description="Contact's email address", max_length=255)
    phone: Optional[str] = Field(None, description="Contact's phone number.", max_length=255)

    class Config:
        extra = "forbid"

class TestCase(BaseModel):
    number: str = Field(..., description="Test case number, in the format of x[.y].z.", max_length=32, pattern=r"^([0-9]+)([.][0-9]+)*$")
    name: str = Field(..., description="The name of the test case or group of tests.", max_length=255)
    description: str = Field(..., description="A description of the test case or group, stating the purpose or scope.", max_length=1023)
    result: ResultType = Field(..., description="Result or outcome of the test case.  PASS indicates all required metrics also indicate PASS.  FAIL indicates one or more required metrics indicate FAIL.  SKIP indicates the test case was not executed.  WARN indicates behavior observed during the execution of the test case might cause concern, problems, or issues not directly relating to the required test metrics.")
    status: TestStatus = Field(..., description="Status of the test case.")
    artifacts: Optional[List[ArtifactsItem]] = Field(None, description="Paths, relative to the root of the archive, to files relating to this specific test case.")
    links: Optional[List[DecoratedLinksItem]] = Field(None, description="Links to additional, external documentation specific to the test.")
    measurements: Optional[List[MeasurementsItem]] = Field(None, description="Test measurements recorded during the test procedure.  Measurements are in addition to values recorded or required as part a test metric.", min_items=1)
    metrics: List[MetricsItem] = Field(..., description="Test metrics or requirements for the test case. (Mandatory for test case)", min_items=1)
    notes: Optional[List[TestNotesItem]] = Field(None, description="A list of notes about the test.")
    startDate: Optional[datetime] = Field(None, description="Date and time the test case was started.")
    stopDate: Optional[datetime] = Field(None, description="Date and time the test case was completed.")
    contacts: Optional[List[ContactsItem]] = Field(None, description="")
    class Config:
        extra = "forbid"
    
class TestGroup(BaseModel):
    """Groups of test cases or test groups."""
    number: str = Field(..., description="Test case number, in the format of x[.y].z.", max_length=32, pattern=r"^([0-9]+)([.][0-9]+)*$")
    name: str = Field(..., description="Name of the test group.", max_length=255)
    description: Optional[str] = Field(None, description="Description of the test group.", max_length=4095)
    groupItems: List[Union[TestCase, "TestGroup"]] = Field(..., min_items=1)

    class Config:
        extra = "forbid"


