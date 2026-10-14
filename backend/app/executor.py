import math
import logging
from typing import List, Tuple
from .models import CodeAnalysis, TestCaseItem, ExecutionMetrics
from .sandbox import SafeSandbox

logger = logging.getLogger(__name__)

def outputs_match(actual: any, expected: any) -> bool:
    """Intelligently compares actual vs expected outputs considering types."""
    if expected == "Unverified":
        return False
    if actual == expected:
        return True
    
    # Handle boolean vs string representations
    if isinstance(expected, bool) and isinstance(actual, str):
        return str(expected).lower() == actual.lower()
    if isinstance(actual, bool) and isinstance(expected, str):
        return str(actual).lower() == expected.lower()

    # Handle float precision
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return math.isclose(float(actual), float(expected), rel_tol=1e-5, abs_tol=1e-5)

    # Handle list comparisons where elements might be in either order (e.g. two sum indices)
    if isinstance(actual, list) and isinstance(expected, list):
        if sorted(actual) == sorted(expected):
            return True

    return False

class TestExecutor:
    """
    Executes generated test cases against the solution in an isolated sandbox,
    validates outcomes, and compiles execution metrics.
    """

    @classmethod
    def execute_and_validate(
        cls,
        code: str,
        language: str,
        analysis: CodeAnalysis,
        test_cases: List[TestCaseItem]
    ) -> Tuple[List[TestCaseItem], ExecutionMetrics]:
        total_time_ms = 0.0
        passed_count = 0
        failed_count = 0
        error_count = 0
        unverified_count = 0
        bugs_exposed_count = 0

        if language == "python" and test_cases:
            inputs_list = [tc.inputs for tc in test_cases]
            batch_results = SafeSandbox.execute_python_batch(
                code=code,
                function_name=analysis.function_name,
                test_inputs_list=inputs_list
            )
        else:
            batch_results = None

        for idx, tc in enumerate(test_cases):
            try:
                if batch_results and idx < len(batch_results):
                    actual, exec_status, err_msg, elapsed = batch_results[idx]
                else:
                    actual, exec_status, err_msg, elapsed = SafeSandbox.execute_generic(
                        code=code,
                        language=language,
                        function_name=analysis.function_name,
                        inputs=tc.inputs
                    )
            except Exception as e:
                logger.warning(f"Error executing test case {tc.id}: {e}")
                actual, exec_status, err_msg, elapsed = None, "ERROR", str(e), 0.0

            tc.actual_output = actual
            tc.execution_time_ms = round(elapsed, 2)
            tc.error_message = err_msg
            total_time_ms += elapsed

            if exec_status == "ERROR":
                tc.status = "ERROR"
                error_count += 1
                if tc.is_bug_exposing:
                    bugs_exposed_count += 1
                    tc.reason += f" [DEFECT EXPOSED: Program crashed with {err_msg}]"
            elif tc.expected_output == "Unverified" or exec_status == "UNVERIFIED":
                tc.status = "UNVERIFIED"
                unverified_count += 1
            else:
                if outputs_match(actual, tc.expected_output):
                    tc.status = "PASS"
                    passed_count += 1
                else:
                    tc.status = "FAIL"
                    failed_count += 1
                    if tc.is_bug_exposing:
                        bugs_exposed_count += 1
                    # Add informative defect note if not already present
                    if "incorrectly" not in tc.reason.lower():
                        tc.reason += f" [MISMATCH: Expected {tc.expected_output}, but solution returned {actual}]"

        total_tested = passed_count + failed_count + error_count
        pass_rate = round((passed_count / total_tested * 100.0), 1) if total_tested > 0 else 0.0

        metrics = ExecutionMetrics(
            total_cases=len(test_cases),
            passed_count=passed_count,
            failed_count=failed_count,
            error_count=error_count,
            unverified_count=unverified_count,
            pass_rate=pass_rate,
            bugs_exposed_count=bugs_exposed_count,
            duplicate_eliminated_count=0, # Populated by generator
            total_time_ms=round(total_time_ms, 2),
            coverage_summary=f"Covered {len(test_cases)} logical partitions spanning boundary, representative, and defect-hunting branches."
        )

        return test_cases, metrics
