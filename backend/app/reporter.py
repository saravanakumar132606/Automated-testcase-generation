from typing import List, Any
from .models import TestCaseItem, CodeAnalysis, ExecutionMetrics

def format_value(val: Any) -> str:
    """Formats output value into user-friendly representation."""
    if val is None:
        return "None"
    if isinstance(val, bool):
        return "true" if val else "false"
    return str(val)

def generate_testcases_txt(
    test_cases: List[TestCaseItem],
    analysis: CodeAnalysis = None,
    metrics: ExecutionMetrics = None
) -> str:
    """
    Generates the exact formatted string for `testcases.txt`
    matching the project specification.
    """
    sections = []

    for tc in test_cases:
        expected_str = format_value(tc.expected_output)
        actual_str = format_value(tc.actual_output) if tc.actual_output is not None else (tc.error_message or "N/A")
        
        tc_block = f"""Test Case {tc.id}: {tc.title}

Input:
{tc.input_formatted}

Expected Output: {expected_str}
Actual Output: {actual_str}
Status: {tc.status}

Reason:
{tc.reason}"""
        sections.append(tc_block)

    return "\n\n---\n\n".join(sections) + "\n"
