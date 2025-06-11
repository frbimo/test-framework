from typing import List, Optional, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, HttpUrl
from modules.test_specification import TestSpecification
from modules.test_metadata import TestMetadata
from modules.test_bed_component import TestbedComponentsItem
from modules.test_lab import TestLab
from modules.test_result import TestGroup, TestCase

class TestReport(BaseModel):
    schemaVersion: int = Field(1, description="test schema.")
    testMetadata: TestMetadata = Field(..., description="test metadata.")  # Removed max_length
    tags: Optional[List[str]] = Field(None, description="test metadata.")  # Changed ... to None
    testbedComponents: Optional[List[TestbedComponentsItem]] = Field(None, description="testbed components.")
    testLab: Optional[TestLab] = Field(None, description="test lab.")
    testSpecifications: List[TestSpecification] = Field(..., description="test specifications.")
    
    # need to be fix. TODO: Match the spec for oneOf between TestGroup and TestCase
    testResults: Optional[List[Union[TestCase, TestGroup]]] = Field(None, description="test results.")
    notes: Optional[str] = Field(None, description="notes.")

