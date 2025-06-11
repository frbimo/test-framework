from typing import List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, HttpUrl
from modules.configuration import ConfigurationParameters
from uuid import uuid4
class ContactsItem(BaseModel):
    """Contact information for person / party involved in the testing or an aspect of the testing."""
    firstName: str = Field(..., description="Contact's first name.", max_length=255)
    lastName: str = Field(..., description="Contact's last name.", max_length=255)
    organization: Optional[str] = Field(None, description="Organization or company the contact is associated with.", max_length=255)
    # email: EmailStr = Field(..., description="Contact's email address", max_length=255)
    phone: Optional[str] = Field(None, description="Contact's phone number.", max_length=255)

    class Config:
        extra = "forbid"


class ResultType(str, Enum):
    """A result. PASS/FAIL/etc. indicates the outcome of a test case, test metric, or test result."""
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    SKIP = "SKIP"


class DecoratedLinksItem(BaseModel):
    """A list of links to objects that have a display name, URL, and optionally a description."""
    displayName: str = Field(..., description="Text that is displayed as the link when rendered.", max_length=255)
    description: Optional[str] = Field(None, description="Longer, more descriptive text about the link and its contents.", max_length=1023)
    url: HttpUrl = Field(..., description="URL Path for the reference.")

    class Config:
        extra = "forbid"


class TestType(str, Enum):
    """Type of test results contained in the artifact container, with respect to the O-RAN Certification and Badging Programs."""
    CONFORMANCE = "conformance"
    INTEROPERABILITY = "interoperability"
    END_TO_END = "end-to-end"
    FUNCTIONAL = "functional"
    OTHER = "Other"


class InterfaceUnderTest(str, Enum):
    """Enum for the interface that was under test."""
    O_RU_OFH = "o-ru.ofh"
    O_RU_FHM = "o-ru.fhm"
    O_DU_OFH = "o-du.ofh"
    O_DU_FHM = "o-du.fhm"
    O_DU_E2 = "o-du.e2"
    O_DU_F1_C = "o-du.f1-c"
    O_DU_F1_U = "o-du.f1-u"
    O_DU_O1 = "o-du.o1"
    O_CU_F1_C = "o-cu.f1-c"
    O_CU_F1_U = "o-cu.f1-u"
    O_CU_E2 = "o-cu.e2"
    O_CU_E1 = "o-cu.e1"
    O_CU_O1 = "o-cu.o1"
    SMO_FHM = "smo.fhm"
    SMO_O2 = "smo.o2"
    SMO_O1 = "smo.o1"
    NON_RT_RIC_A1 = "non-rt-ric.a1"
    NEAR_RT_RIC_A1 = "near-rt-ric.a1"
    NEAR_RT_RIC_E2 = "near-rt-ric.e2"
    NEAR_RT_RIC_O1 = "near-rt-ric.o1"

class UEContext(BaseModel):
    numberOfUE: Optional[int] = Field(None, description="Number of User Equipment (UE) in the context.")
    location: Optional[str] = Field(None, description="Location of the UE context.")
    targetThroughput: Optional[float] = Field(None, description="Target throughput for the UE context.")
    slice: Optional[str] = Field(None, description="Network slice associated with the UE context.")
    qosId: Optional[int] = Field(None, description="5G QoS Identifier (5QI) for the UE context.")
    mobilityModel: Optional[str] = Field(None, description="Mobility model for the UE context.")    
    mobilitySpeed: Optional[float] = Field(None, description="Mobility speed for the UE context.")


class AdditionalContext(BaseModel):
    ueContext: Optional[UEContext] = Field(
        None,
        description="User Equipment (UE) context information."
    )

class TestMetadata(BaseModel):
    result: ResultType = Field(None, description="The overall, aggregated, test result. PASS indicates all required test cases also indicate PASS. FAIL indicates one or more required test cases indicate FAIL. WARN indicates behavior observed during the execution of the test case might cause concern, problems, or issues not directly relating to the required test metrics. SKIP should not be used.")

    contacts: Optional[List[ContactsItem]] = Field(None, description="Contacts relating to the testing, but not necessarily directly relating to the lab or a testbed component.")
    startDate: datetime = Field(..., description="Date and time the test was started.")
    stopDate: Optional[datetime] = Field(None, description="Date and time the test was completed.")
    dutName: str = Field(..., description="Name or reference to the device(s) in the list of testbed components that is considered the device(s) under test (DUT) or system under test (SUT).", max_length=255)
    interfaceUnderTest: Optional[List[InterfaceUnderTest]] = Field(None, description="Interface(s) that was under test within these test results.")
    result: Optional[ResultType] = Field(None, description="The overall, aggregated, test result. PASS indicates all required test cases also indicate PASS. FAIL indicates one or more required test cases indicate FAIL. WARN indicates behavior observed during the execution of the test case might cause concern, problems, or issues not directly relating to the required test metrics. SKIP should not be used.")
    testType: TestType = Field(..., description="Type of test result within this artifact.")
    testId: str = Field(default_factory=lambda: str(uuid4()), description="Certificate/Badge Reference ID, assigned by the laboratory, in the format of [O-RAN Designator]yy####, where yy is the two digit year, and #### is a four digit number defined by the laboratory.")
    additionalContext: Optional[List[AdditionalContext]] = Field(None, description="Additional context for the test results.")
   
    # iotProfile: Optional[Wg4IotProfile] = Field(None, description="Information about the
    configurationParameters: Optional[List[ConfigurationParameters]] = Field(None, description="Configuration parameters used during the test.")