from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ParameterInfo(BaseModel):
    name: str
    type_name: str
    description: Optional[str] = ""

class CodeAnalysis(BaseModel):
    purpose: str = Field(..., description="Inferred purpose and expected behavior of the program")
    function_name: str = Field(..., description="Main function or method name identified")
    signature: str = Field(..., description="Function signature with parameter names and types")
    input_parameters: List[ParameterInfo] = Field(default_factory=list, description="List of input parameters")
    output_type: str = Field(..., description="Expected return/output data type")
    variables_and_loops: List[str] = Field(default_factory=list, description="Key variables, conditions, and loops")
    algorithmic_logic: str = Field(..., description="Summary of the algorithmic approach")
    time_complexity: Optional[str] = Field(default="O(N)", description="Estimated time complexity")
    space_complexity: Optional[str] = Field(default="O(1)", description="Estimated space complexity")
    constraints_and_boundaries: List[str] = Field(default_factory=list, description="Input constraints and boundary conditions")
    potential_bugs: List[str] = Field(default_factory=list, description="Potential bugs, incorrect assumptions found in code")
    missing_edge_cases: List[str] = Field(default_factory=list, description="Missing edge-case handling in the solution")
    confidence_score: float = Field(default=0.9, ge=0.0, le=1.0, description="Confidence level in inferred requirements")
    uncertainties: List[str] = Field(default_factory=list, description="Explicit uncertainties or ambiguities if any")

class TestCaseItem(BaseModel):
    id: int
    title: str = Field(..., description="Descriptive title e.g. 'Valid Anagram' or 'Character Frequency Mismatch'")
    category: str = Field(..., description="Category: Normal, Boundary, Empty/Single, Duplicates, Negatives, Special Chars, Meaningful Words, Bug Hunting, Large")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Dictionary of parameter name to input value")
    input_formatted: str = Field(..., description="Pretty-formatted string of inputs")
    expected_output: Any = Field(..., description="Independently established expected output or 'Unverified'")
    actual_output: Optional[Any] = Field(default=None, description="Actual output from executing the solution")
    status: str = Field(default="UNVERIFIED", description="PASS, FAIL, ERROR, or UNVERIFIED")
    reason: str = Field(..., description="Reason for selecting this test case and explanation of mismatch if any")
    execution_time_ms: Optional[float] = Field(default=None, description="Execution time in milliseconds")
    error_message: Optional[str] = Field(default=None, description="Runtime or compilation error details")
    is_bug_exposing: bool = Field(default=False, description="Whether this test case successfully exposes a defect")

class ExecutionMetrics(BaseModel):
    total_cases: int = 0
    passed_count: int = 0
    failed_count: int = 0
    error_count: int = 0
    unverified_count: int = 0
    pass_rate: float = 0.0
    bugs_exposed_count: int = 0
    duplicate_eliminated_count: int = 0
    total_time_ms: float = 0.0
    coverage_summary: Optional[str] = ""

class CodeInputRequest(BaseModel):
    code: str
    language: str = "auto"
    filename: Optional[str] = None
    api_key: Optional[str] = None
    min_cases: int = 100

class GenerationResponse(BaseModel):
    success: bool
    language: str
    analysis: CodeAnalysis
    test_cases: List[TestCaseItem]
    metrics: ExecutionMetrics
    report_text: str
    error: Optional[str] = None

class ConfigStatus(BaseModel):
    gemini_configured: bool
    default_model: str
    supported_languages: List[str]
