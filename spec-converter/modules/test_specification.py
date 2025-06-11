from __future__ import annotations

from typing import Optional, List, Union, Literal, Any, Dict
from datetime import datetime, time
from enum import Enum

from pydantic import BaseModel, Field, validator, model_validator, ConfigDict

class ConditionEnum(str, Enum):
    IS_EQUAL_TO = "IS_EQUAL_TO"
    IS_LESS_THAN = "IS_LESS_THAN"
    IS_GREATER_THAN = "IS_GREATER_THAN" 
    IS_WITHIN_RANGE = "IS_WITHIN_RANGE"
    IS_OUTSIDE_RANGE = "IS_OUTSIDE_RANGE"
    IS_ONE_OF = "IS_ONE_OF"
    IS_NOT_ONE_OF = "IS_NOT_ONE_OF"
    IS_EQUAL_TO_OR_LESS_THAN = "IS_EQUAL_TO_OR_LESS_THAN"
    IS_EQUAL_TO_OR_GREATER_THAN = "IS_EQUAL_TO_OR_GREATER_THAN"
    IS_ALL_OF = "IS_ALL_OF"
    IS_GREATER_THAN_OR_EQUAL_TO = "IS_GREATER_THAN_OR_EQUAL_TO"
    IS_LESS_THAN_OR_EQUAL_TO = "IS_LESS_THAN_OR_EQUAL_TO"
    IS_NOT_ALL_OF = "IS_NOT_ALL_OF"
    IS_NOT_EQUAL_TO = "IS_NOT_EQUAL_TO"
    IS_NOT_WITHIN = "IS_NOT_WITHIN"

    
class ObjectTypeBaseEnum(str, Enum):
    RAN_SUBNETWORK = "RAN_SUBNETWORK"; EDGE_SERVICE_SUPPORT = "EDGE_SERVICE_SUPPORT"
    FIVEGC_SUBNETWORK = "5GC_SUBNETWORK"; RADIO_SERVICE = "Radio_Service"

class ExpectationVerbEnum(str, Enum):
    DELIVER = "DELIVER"; ENSURE = "ENSURE"; EXPECT="EXPECT"

class RATTypeEnum(str, Enum):
    UTRAN = "UTRAN"; EUTRAN = "EUTRAN"; NR = "NR"


# --- Reused/Adapted Pydantic Models ---

class GeoPoint(BaseModel):
    model_config = ConfigDict(extra='forbid')
    # Use float for latitude/longitude, pydantic will coerce "31.2696"
    latitude: float
    longitude: float

# Specific structure from the example request
class ConvexGeoPolygon(BaseModel):
    model_config = ConfigDict(extra='forbid')
    convexGeoPolygon: List[GeoPoint]

class Frequency(BaseModel):
    model_config = ConfigDict(extra='forbid')
    # Use int for arfcn, pydantic will coerce "384000"
    arfcn: int

# Specific structure from the example request for TimeWindow values
class TimeWindowValue(BaseModel):
     model_config = ConfigDict(extra='forbid')
     # Using str as format is non-standard YYYY-MM-DD-HH-MM-SS
     startTime: datetime
     endTime: datetime

# Base Context - Accepts different value range types
class ContextRequest(BaseModel):
    model_config = ConfigDict(extra='allow') # Allow variations in valueRange
    contextAttribute: str
    contextCondition: ConditionEnum
    contextValueRange: Any # Allow flexible types based on attribute

# Specific Context structures seen in the example
class CoverageAreaPolygonContextRequest(ContextRequest):
    contextAttribute: Literal["CoverageAreaPolygon"] = "CoverageAreaPolygon"
    contextCondition: Literal[ConditionEnum.IS_ALL_OF] = ConditionEnum.IS_ALL_OF
    # Matches the example: list containing one object with convexGeoPolygon
    contextValueRange: List[ConvexGeoPolygon]

class PLMNContextRequest(ContextRequest):
    contextAttribute: Literal["PLMN"] = "PLMN"
    contextCondition: Literal[ConditionEnum.IS_ALL_OF] = ConditionEnum.IS_ALL_OF
    # Matches example: List of strings (Pydantic coerces "46000")
    contextValueRange: List[str]

class DlFrequencyContextRequest(ContextRequest):
    contextAttribute: Literal["DlFrequency"] = "DlFrequency"
    contextCondition: Literal[ConditionEnum.IS_ALL_OF] = ConditionEnum.IS_ALL_OF
    # Matches example: List containing one Frequency object
    contextValueRange: List[Frequency]

class RATContextRequest(ContextRequest):
    contextAttribute: Literal["RAT"] = "RAT"
    contextCondition: Literal[ConditionEnum.IS_ALL_OF] = ConditionEnum.IS_ALL_OF
    # Matches example: List of RATTypeEnum values
    contextValueRange: List[RATTypeEnum]

class TargetAssuranceTimeContextRequest(ContextRequest):
    contextAttribute: Literal["TargetAssuranceTime"] = "TargetAssuranceTime"
    contextCondition: Literal[ConditionEnum.IS_EQUAL_TO] = ConditionEnum.IS_EQUAL_TO
    # Matches example: List containing one TimeWindowValue object
    contextValueRange: List[TimeWindowValue]

# Union for context validation (optional, Pydantic handles Any well here)
AnyContextRequest = Union[
    CoverageAreaPolygonContextRequest,
    PLMNContextRequest,
    DlFrequencyContextRequest,
    RATContextRequest,
    TargetAssuranceTimeContextRequest,
    ContextRequest # Fallback for generic contexts
]

class ExpectationTargetRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    targetName: str
    targetCondition: ConditionEnum
    # Accept string based on example, but allow others too if needed later
    targetValueRange: Union[str, int, float, List, Dict]
    targetUnit: Optional[str] = None
    targetScope: Optional[str] = None

# --- Models adapted for the *specific request structure* ---

# Represents the fragments within the example's expectationObject list
class ExpectationObjectFragment(BaseModel):
    model_config = ConfigDict(extra='allow') # Allow different keys in fragments
    objectType: Optional[ObjectTypeBaseEnum] = None
    objectInstance: Optional[str] = None
    objectContexts: Optional[List[AnyContextRequest]] = Field(None, Set=True)

    # Ensure only one key is present per fragment (as seen in example)
    @model_validator(mode='before')
    @classmethod
    def check_one_key(cls, values):
        present_keys = [k for k in ['objectType', 'objectInstance', 'objectContexts'] if k in values]
        if len(present_keys) != 1:
            raise ValueError(f"Each fragment in expectationObject list must have exactly one key from ['objectType', 'objectInstance', 'objectContexts']. Found: {present_keys}")
        return values


class TestSpecification(BaseModel):
    model_config = ConfigDict(extra='allow')
    # expectationId: str
    expectationVerb: ExpectationVerbEnum
    # This is the key change: expecting a list of fragments
    expectationObject: List[ExpectationObjectFragment] = Field(..., min_length=1)
    expectationTargets: List[ExpectationTargetRequest] = Field(..., min_length=1, Set=True)

