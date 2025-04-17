import json
from pydantic import (
    BaseModel, Field, EmailStr, AnyUrl, model_validator, field_validator,
    ValidationError, ConfigDict
)
from typing import List, Optional, Union, Dict, Any, Literal
from enum import Enum
from datetime import datetime
from uuid import UUID

from modules.configuration import ConfigurationParameters
# --- Enums defined in the schema ---

class UnitsEnum(str, Enum):
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

class ResultTypeEnum(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    SKIP = "SKIP"

class TestStatusEnum(str, Enum):
    MANDATORY = "mandatory"
    CONDITIONALLY_MANDATORY = "conditionally.mandatory"
    OPTIONAL = "optional"

class TestTypeEnum(str, Enum):
    CONFORMANCE = "conformance"
    INTEROPERABILITY = "interoperability"
    END_TO_END = "end-to-end"
    OTHER = "Other" # Note: Enum member names cannot contain '-', replaced with '_' if needed, but value must match JSON.

class InterfaceUnderTestEnum(str, Enum):
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

class DeploymentRfScenarioEnum(str, Enum):
    RURAL = "rural"
    URBAN = "urban"
    DENSE_URBAN = "dense.urban"
    LOS = "LOS"
    NLOS = "NLOS"
    NLOS_ALT = "nLOS" # Using alias for nLOS if needed, or adjust enum name


# --- Models defined in $defs ---

class Contact(BaseModel):
    firstName: str = Field(..., max_length=255)
    lastName: str = Field(..., max_length=255)
    organization: Optional[str] = Field(None, max_length=255)
    email: EmailStr = Field(...) # max_length validated by EmailStr implicitly usually
    phone: Optional[str] = Field(None, max_length=255)

    model_config = ConfigDict(extra='forbid')

class DecoratedLink(BaseModel):
    displayName: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=1023)
    url: AnyUrl = Field(...)

    model_config = ConfigDict(extra='forbid')

class Artifact(BaseModel):
    name: str = Field(..., max_length=255)
    path: str = Field(..., max_length=1023)
    description: str = Field(..., max_length=4095)

    model_config = ConfigDict(extra='forbid')

class Measurement(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=1023)
    values: List[Any] = Field(..., min_length=1) # Type Any allows mixed types as per schema
    units: UnitsEnum = Field(...)
    references: Optional[List[DecoratedLink]] = Field(None, min_length=1)

    model_config = ConfigDict(extra='forbid')

class Metric(BaseModel):
    description: str = Field(..., max_length=1023)
    measurements: List[Measurement] = Field(..., min_length=1)
    status: TestStatusEnum = Field(...)
    result: ResultTypeEnum = Field(...)

    # WARN should not be used for metric result per schema description
    @field_validator('result')
    @classmethod
    def check_metric_result(cls, v: ResultTypeEnum) -> ResultTypeEnum:
        if v == ResultTypeEnum.WARN:
            raise ValueError("WARN value should not be used for metrics.")
        return v

    model_config = ConfigDict(extra='forbid')


class TestNote(BaseModel):
    title: str = Field(..., max_length=255)
    body: str = Field(..., max_length=4095)

    model_config = ConfigDict(extra='forbid')

class WG4IotProfile(BaseModel):
    wg4IotSpecificationVersion: str = Field(..., pattern=r"^[0-9][0-9][.][0-9][0-9]$")
    mPlaneIotProfileName: Optional[str] = Field(None, min_length=10, max_length=128)
    mPlaneIotProfileTestConfiguration: Optional[str] = Field(None, min_length=10, max_length=128)
    cusPlaneIotProfileName: Optional[str] = Field(None, min_length=10, max_length=128)
    cusPlaneIotProfileTestConfiguration: Optional[str] = Field(None, min_length=10, max_length=128)

    @model_validator(mode='after') # Use 'after' to validate populated fields
    def check_profile_names(self) -> 'WG4IotProfile':
        if not self.mPlaneIotProfileName and not self.cusPlaneIotProfileName:
            raise ValueError("At least one of mPlaneIotProfileName or cusPlaneIotProfileName must be provided.")
        # Check dependencies if needed (e.g., if mPlaneName provided, mPlaneConfig should be too - schema doesn't mandate this)
        # if self.mPlaneIotProfileName and not self.mPlaneIotProfileTestConfiguration:
        #     raise ValueError("mPlaneIotProfileTestConfiguration is required if mPlaneIotProfileName is provided.")
        # if self.cusPlaneIotProfileName and not self.cusPlaneIotProfileTestConfiguration:
        #     raise ValueError("cusPlaneIotProfileTestConfiguration is required if cusPlaneIotProfileName is provided.")
        return self

    model_config = ConfigDict(extra='forbid')

# Forward references are needed for recursive/interdependent models
class TestCase(BaseModel):
    number: str = Field(..., max_length=32, pattern=r"^([0-9]+)([.][0-9]+)*$")
    name: str = Field(..., max_length=255)
    description: str = Field(..., max_length=1023)
    result: ResultTypeEnum = Field(...)
    status: TestStatusEnum = Field(...)
    artifacts: Optional[List[Artifact]] = Field(None, min_length=1)
    links: Optional[List[DecoratedLink]] = Field(None, min_length=1)
    measurements: Optional[List[Measurement]] = Field(None, min_length=1)
    metrics: List[Metric] = Field(..., min_length=1)
    notes: Optional[List[TestNote]] = Field(None, min_length=1)
    startDate: Optional[datetime] = None
    stopDate: Optional[datetime] = None
    contacts: Optional[List[Contact]] = Field(None, min_length=1)

    model_config = ConfigDict(extra='forbid')

class TestGroup(BaseModel):
    number: str = Field(..., max_length=32, pattern=r"^([0-9]+)([.][0-9]+)*$")
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=4095)
    groupItems: List[Union['TestGroup', TestCase]] = Field(..., min_length=1) # Forward reference using string

    model_config = ConfigDict(extra='forbid')


# --- Top Level Models ---

class TestMetadata(BaseModel):
    contacts: Optional[List[Contact]] = Field(None, min_length=1)
    startDate: datetime = Field(...)
    stopDate: Optional[datetime] = None
    dutName: str = Field(..., max_length=255)
    interfaceUnderTest: Optional[List[InterfaceUnderTestEnum]] = Field(None, min_length=1)
    result: ResultTypeEnum = Field(...)
    testType: TestTypeEnum = Field(...)
    testId: Union[str, UUID] = Field(...) # Allow UUID or the specific string pattern
    iotProfile: Optional[WG4IotProfile] = None
    configurationParameters: Optional[ConfigurationParameters] = None

    # Validate testId pattern if it's a string
    @field_validator('testId')
    @classmethod
    def check_test_id_format(cls, v):
        if isinstance(v, str):
            pattern = r"^[A-Za-z0-9]{3,4}([23][0-9]){1}[0-9]{4}$"
            if not (9 <= len(v) <= 10 and re.match(pattern, v)):
                 # Try parsing as UUID as fallback before raising error
                try:
                    UUID(v)
                    return v # It's a valid UUID string
                except ValueError:
                    raise ValueError(f"testId string '{v}' does not match pattern '{pattern}' or UUID format")
        elif not isinstance(v, UUID):
             raise TypeError("testId must be a string or UUID")
        return v

    # SKIP should not be used for overall result per schema description
    @field_validator('result')
    @classmethod
    def check_overall_result(cls, v: ResultTypeEnum) -> ResultTypeEnum:
        if v == ResultTypeEnum.SKIP:
            raise ValueError("SKIP value should not be used for overall testMetadata result.")
        return v

    model_config = ConfigDict(extra='forbid')

class TestbedComponent(BaseModel):
    componentDescription: str = Field(..., max_length=255)
    manufacturerName: str = Field(..., max_length=255)
    manufacturerModel: str = Field(..., max_length=255)
    serialNumber: Optional[str] = Field(None, max_length=255)
    testbedInventoryId: Optional[str] = Field(None, max_length=255)
    softwareVersion: Optional[str] = Field(None, max_length=255)
    hardwareVersion: Optional[str] = Field(None, max_length=255)
    firmwareVersion: Optional[str] = Field(None, max_length=255)
    contacts: Optional[List[Contact]] = Field(None, min_length=1)
    configurationArtifacts: Optional[List[Artifact]] = Field(None, min_length=1)
    configurationNotes: Optional[List[TestNote]] = Field(None, min_length=1)
    configurationParameters: Optional[ConfigurationParameters] = None

    @model_validator(mode='after')
    def check_version_fields(self) -> 'TestbedComponent':
        if not self.softwareVersion and not self.hardwareVersion and not self.firmwareVersion:
            raise ValueError("At least one of softwareVersion, hardwareVersion, or firmwareVersion must be provided.")
        return self

    model_config = ConfigDict(extra='forbid')

class TestLab(BaseModel):
    name: str = Field(..., max_length=255)
    address: str = Field(..., max_length=512)
    contacts: List[Contact] = Field(..., min_length=1)
    links: Optional[List[DecoratedLink]] = Field(None, min_length=1)

    model_config = ConfigDict(extra='forbid')

class TestSpecification(BaseModel):
    name: str = Field(..., max_length=255)
    version: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=512)
    links: List[DecoratedLink] = Field(..., min_length=1)

    model_config = ConfigDict(extra='forbid')


# --- Main Schema Model ---

class TestResultsSummary(BaseModel):
    schema_ref: Optional[AnyUrl] = Field(None, alias="$schema")
    schemaVersion: Literal[1] = Field(...)
    testMetadata: TestMetadata = Field(...)
    tags: Optional[List[str]] = Field(None, min_length=1) # Add pattern validation if needed
    testbedComponents: List[TestbedComponent] = Field(..., min_length=1)
    testLab: TestLab = Field(...)
    testSpecifications: List[TestSpecification] = Field(..., min_length=1)
    testResults: List[Union[TestGroup, TestCase]] = Field(..., min_length=1)
    notes: Optional[List[TestNote]] = Field(None, min_length=1)

    @field_validator('tags', mode='before') # Validate before type conversion
    @classmethod
    def check_tag_pattern(cls, v):
        if v is None:
            return None
        if isinstance(v, list):
            pattern = r"^[a-z0-9-]+$"
            for tag in v:
                if not isinstance(tag, str) or not re.match(pattern, tag) or len(tag) > 255:
                     raise ValueError(f"Invalid tag: '{tag}'. Must match pattern '{pattern}' and max length 255.")
        return v

    model_config = {
        'extra': 'forbid',
        'populate_by_name': True # Needed for '$schema' alias
    }

# --- Update forward references ---
# This is crucial for Pydantic to resolve the string references like 'TestGroup'
TestGroup.model_rebuild()
TestCase.model_rebuild() # Although TestCase doesn't directly reference TestGroup, rebuild if dependencies changed
TestResultsSummary.model_rebuild() # Rebuild the main model as well

# Need re for pattern validation in validators
import re

print("Pydantic models defined successfully.")

# 2. Example Data

# Example 1: Minimal valid data focusing on required fields
example_data_1 = {
    # "$schema": "https://o-ran.org/schemas/o-ran-test-results", # Optional in Pydantic model
    "schemaVersion": 1,
    "testMetadata": {
        "startDate": "2024-01-15T09:00:00Z",
        "dutName": "O-DU-Sim-1",
        "result": "PASS",
        "testType": "conformance",
        "testId": "ORAN240001",
        "interfaceUnderTest": ["o-du.f1-c", "o-du.f1-u"]
    },
    "testbedComponents": [
        {
            "componentDescription": "O-DU Simulator",
            "manufacturerName": "SimCorp",
            "manufacturerModel": "DU-Sim-X1",
            "softwareVersion": "2.1.0"
        },
        {
            "componentDescription": "O-RU Simulator",
            "manufacturerName": "SimCorp",
            "manufacturerModel": "RU-Sim-Y2",
            "firmwareVersion": "1.0.5b"
        }
    ],
    "testLab": {
        "name": "Open Test Lab",
        "address": "123 Test Street, Testville, TS 12345",
        "contacts": [
            {
                "firstName": "Lab",
                "lastName": "Admin",
                "email": "admin@opentestlab.com"
            }
        ]
    },
    "testSpecifications": [
        {
            "name": "O-RAN.WG4.MP.O-DU",
            "version": "v10.00",
            "links": [
                {
                    "displayName": "O-RAN WG4 M-Plane Spec",
                    "url": "https://oran-spec-repo.net/wg4/mplane/v10"
                }
            ]
        }
    ],
    "testResults": [
        {
            # Represents a TestCase directly in the list
            "number": "3.1",
            "name": "Basic M-Plane Connection",
            "description": "Verify establishment of NETCONF session.",
            "result": "PASS",
            "status": "mandatory",
            "metrics": [
                {
                    "description": "NETCONF session established within 5 seconds.",
                    "measurements": [
                        {
                            "name": "Session Establishment Time",
                            "values": [3.2],
                            "units": "second"
                        }
                    ],
                    "status": "mandatory",
                    "result": "PASS"
                }
            ]
        }
    ]
}

# Example 2: More complex data with optional fields and nested groups
example_data_2 = {
    "$schema": "https://o-ran.org/schemas/o-ran-test-results",
    "schemaVersion": 1,
    "testMetadata": {
        "contacts": [
             {
                "firstName": "Lead",
                "lastName": "Tester",
                "organization": "Open Test Lab",
                "email": "lead.tester@opentestlab.com",
                "phone": "+1-555-123-4567"
            }
        ],
        "startDate": "2024-03-10T10:00:00+01:00",
        "stopDate": "2024-03-12T17:30:00+01:00",
        "dutName": "VendorX RU Model 7",
        "interfaceUnderTest": ["o-ru.ofh"],
        "result": "FAIL",
        "testType": "interoperability",
        "testId": "IOTX249876",
        "iotProfile": {
             "wg4IotSpecificationVersion": "10.00",
             "mPlaneIotProfileName": "O-RAN-WG4.IOT-v10.00-MP-RuVendorX",
             "mPlaneIotProfileTestConfiguration": "MP-RuVendorX-CuSimCorp-Basic"
        },
        "configurationParameters": {
            "deploymentArchitecture": "outdoor",
            "deploymentScale": "macro",
            "frequencyRange5G": ["fr1"],
            "band5G": ["n78"],
            "subCarrierSpacing": "30kHz",
            "totalResourceBlocks": 273,
            "duplexMode": "tdd",
            "numTxAntenna": 4,
            "numRxAntenna": 4,
            "customParam": "customValue123" # Example of an additional property
        }
    },
    "tags": ["fronthaul", "m-plane", "ru-vendor-x", "iot"],
    "testbedComponents": [
        {
            "componentDescription": "O-RU (DUT)",
            "manufacturerName": "VendorX",
            "manufacturerModel": "RU Model 7",
            "serialNumber": "VXRM7-SN001",
            "hardwareVersion": "rev B",
            "firmwareVersion": "FXOS-3.2.1",
             "contacts": [
                {
                    "firstName": "VendorX",
                    "lastName": "Support",
                    "email": "support@vendorx.com"
                }
            ],
            "configurationArtifacts": [
                { "name": "RU Config", "path": "configs/ru_config_vxrm7.xml", "description": "Startup XML config used for the RU."}
            ],
            "configurationNotes": [
                {"title": "Antenna Setup", "body": "Connected to 4x4 antenna array XYZ."}
            ],
            "configurationParameters": {
                "totalTransmitPowerIntoAntenna": 43.0, # dBm assumed
                 "localIpAddress": "192.168.1.10" # Another custom/additional param
            }
        },
        {
            "componentDescription": "O-DU+O-CU Simulator",
            "manufacturerName": "SimCorp",
            "manufacturerModel": "CU-DU-Sim-Z9",
            "softwareVersion": "4.0.0-beta",
            "testbedInventoryId": "LAB-SC-Z9-002"
        },
         {
            "componentDescription": "Timing Source",
            "manufacturerName": "Precision Time Inc.",
            "manufacturerModel": "PTP Grandmaster 1000",
            "firmwareVersion": "2.5"
        }
    ],
    "testLab": {
        "name": "Advanced Interop Facility",
        "address": "456 Interop Drive, Tech Park, TP 67890",
        "contacts": [
            { "firstName": "Facility", "lastName": "Manager", "email": "manager@interopfacility.org" },
            { "firstName": "Lead", "lastName": "Tester", "email": "lead.tester@opentestlab.com" } # Re-use contact ok
        ],
        "links": [
            {"displayName": "Lab Website", "url": "http://www.interopfacility.org"}
        ]
    },
    "testSpecifications": [
        {
            "name": "O-RAN.WG4.IOT",
            "version": "v10.00",
            "description": "WG4 Interoperability Test Specification",
            "links": [
                { "displayName": "IOT Spec (PDF)", "url": "https://oran-spec-repo.net/wg4/iot/v10.pdf" }
            ]
        },
         {
            "name": "O-RAN.WG5.FH.CONF",
            "version": "v08.00",
            "description": "WG5 Fronthaul Conformance Test Specification (referenced)",
            "links": [
                { "displayName": "WG5 FH Conf Spec", "url": "https://oran-spec-repo.net/wg5/fh-conf/v8" }
            ]
        }
    ],
    "testResults": [
        {
            "number": "1",
            "name": "M-Plane Tests",
            "description": "Tests related to the Management Plane interface.",
            "groupItems": [
                 { # Test Case inside group
                    "number": "1.1",
                    "name": "NETCONF Connection",
                    "description": "Verify NETCONF setup from DU Sim to RU DUT.",
                    "result": "PASS",
                    "status": "mandatory",
                    "startDate": "2024-03-10T10:30:00+01:00",
                    "stopDate": "2024-03-10T10:35:00+01:00",
                    "metrics": [
                         {
                            "description": "Session established",
                            "measurements": [{"name": "Session Status", "values": [True], "units": "boolean"}],
                            "status": "mandatory",
                            "result": "PASS"
                         }
                    ],
                     "artifacts": [
                         {"name": "Netconf Log", "path": "logs/1.1_netconf.log", "description": "Trace of NETCONF session"}
                     ]
                },
                { # Test Case inside group
                    "number": "1.2",
                    "name": "Software Download",
                    "description": "Verify the SW download procedure.",
                    "result": "FAIL",
                    "status": "mandatory",
                    "startDate": "2024-03-10T11:00:00+01:00",
                    "stopDate": "2024-03-10T11:45:00+01:00",
                    "metrics": [
                        {
                            "description": "SW download completes successfully.",
                            "measurements": [{"name": "Download Status", "values": ["Timeout"], "units": "text"}],
                            "status": "mandatory",
                            "result": "FAIL"
                        },
                        {
                            "description": "SW download time within limit (30 mins).",
                            "measurements": [{"name": "Download Time", "values": [45.0*60], "units": "second"}],
                            "status": "mandatory",
                            "result": "FAIL"
                        }
                    ],
                    "notes": [
                        {"title": "Failure Cause", "body": "Download timed out after 45 minutes. Expected completion within 30."},
                        {"title": "Investigation", "body": "Check network connection between DU Sim and RU."}
                    ]
                }
            ] # End groupItems for group 1
        },
        {
            "number": "2",
            "name": "CUS-Plane Tests",
            "description": "Tests related to Control, User, and Synchronization Planes.",
            "groupItems": [
                 { # Nested Test Group
                    "number": "2.1",
                    "name": "C-Plane Setup",
                    "groupItems": [
                         { # Test Case inside nested group
                            "number": "2.1.1",
                            "name": "Initial UL C-Plane",
                            "description": "Verify first UL C-plane message reception.",
                            "result": "SKIP",
                            "status": "conditionally.mandatory",
                            "metrics": [
                                {
                                    "description": "RU receives Initial UL C-Plane message.",
                                     "measurements": [{"name": "Message Received", "values": ["N/A"], "units": "text"}],
                                     "status": "conditionally.mandatory",
                                     "result": "SKIP" # Cannot be WARN
                                }
                            ],
                            "notes": [{"title": "Skipped Reason", "body": "Skipped due to M-Plane SW Download failure."}]
                         }
                    ] # End groupItems for group 2.1
                 }
            ] # End groupItems for group 2
        }
    ], # End testResults
    "notes": [
        {"title": "Overall Summary", "body": "Testing halted due to critical failure in SW download (Test 1.2). CUS-Plane tests were not executed."},
        {"title": "Next Steps", "body": "VendorX to investigate SW download issue on RU Model 7 FW FXOS-3.2.1."}
    ]
}


# 3. Test Serialization and Deserialization

def test_serialization_deserialization(example_name: str, data: dict):
    print(f"\n--- Testing {example_name} ---")

    # --- Deserialization (JSON/Dict -> Pydantic Object) ---
    print("\n1. Deserializing dictionary into Pydantic object...")
    try:
        parsed_object = TestResultsSummary.model_validate(data)
        print("   Deserialization Successful!")
        # print("   Parsed Object (summary):")
        # print(f"   Test ID: {parsed_object.testMetadata.testId}")
        # print(f"   Overall Result: {parsed_object.testMetadata.result}")
        # print(f"   Number of Testbed Components: {len(parsed_object.testbedComponents)}")
        # print(f"   Number of Top-Level Test Results/Groups: {len(parsed_object.testResults)}")

    except ValidationError as e:
        print(f"   Deserialization Failed!")
        print(e)
        return # Stop if deserialization fails

    # --- Serialization (Pydantic Object -> JSON String) ---
    print("\n2. Serializing Pydantic object back into JSON string...")
    try:
        # Use by_alias=True to ensure field names like '$schema' and 'nr-arfcn' are correct in JSON
        # Use exclude_none=True to omit fields that are None (optional fields not provided)
        json_output = parsed_object.model_dump_json(indent=2, by_alias=True, exclude_none=True)
        print("   Serialization Successful!")
        print("   Generated JSON (first 500 chars):")
        print(json_output[:500] + "...")

        # Optional: Validate the generated JSON can be parsed back
        print("\n3. Verifying serialized JSON can be re-parsed...")
        reparsed_object = TestResultsSummary.model_validate_json(json_output)
        print("   Re-parsing successful!")
        assert reparsed_object == parsed_object # Check if objects are equivalent
        print("   Original and re-parsed objects are equivalent.")

    except Exception as e:
        print("   Serialization or Re-parsing Failed!")
        print(e)

    print(f"\n--- End Testing {example_name} ---")

# Run the tests

test_bed = TestbedComponent(
componentDescription="O-RU Simulator",
manufacturerName="Viavi",
manufacturerModel="TM500 RU SIM",
softwareVersion="2.0.0",
)
print(test_bed)

test_serialization_deserialization("Example 1 (Minimal)", example_data_1)
test_serialization_deserialization("Example 2 (Complex)", example_data_2)