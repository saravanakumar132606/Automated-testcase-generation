import collections
import json
import logging
from typing import Any, Dict, Optional, Tuple
from .models import CodeAnalysis

logger = logging.getLogger(__name__)

class ReferenceOracle:
    """
    Independent reference implementation and behavioral ground truth.
    Never relies on the submitted user code to determine expected outputs.
    """

    @staticmethod
    def get_expected_output(
        analysis: CodeAnalysis,
        test_inputs: Dict[str, Any],
        raw_code: str,
        api_key: Optional[str] = None
    ) -> Tuple[Any, bool]:
        """
        Determines the independently verified expected output.
        Returns: (expected_value, is_verified)
        """
        import re
        func_clean = re.sub(r'[^a-z0-9]', '', analysis.function_name.lower())
        code_clean = re.sub(r'[^a-z0-9]', '', raw_code.lower())
        purpose_clean = re.sub(r'[^a-z0-9]', '', analysis.purpose.lower())
        param_names = [p.name for p in analysis.input_parameters]

        # 1. Anagram Verification Oracle
        if "anagram" in func_clean or "anagram" in purpose_clean or "anagram" in code_clean:
            s = test_inputs.get("s", test_inputs.get(param_names[0] if param_names else "s", ""))
            t = test_inputs.get("t", test_inputs.get(param_names[1] if len(param_names) > 1 else "t", ""))
            if isinstance(s, str) and isinstance(t, str):
                expected = collections.Counter(s) == collections.Counter(t)
                return expected, True

        # 2. Palindrome Verification Oracle
        if "palindrome" in func_clean or "palindrome" in purpose_clean or "palindrome" in code_clean:
            s = test_inputs.get("s", test_inputs.get(param_names[0] if param_names else "s", ""))
            if isinstance(s, str):
                clean = "".join(ch.lower() for ch in s if ch.isalnum())
                expected = (clean == clean[::-1])
                return expected, True

        # 3. Two Sum Verification Oracle
        if "twosum" in func_clean or "twosum" in code_clean or ("sum" in func_clean and ("target" in test_inputs or "nums" in test_inputs)):
            nums = test_inputs.get("nums", test_inputs.get(param_names[0] if param_names else "nums", []))
            target = test_inputs.get("target", test_inputs.get(param_names[1] if len(param_names) > 1 else "target", 0))
            if isinstance(nums, list) and isinstance(target, int):
                seen = {}
                found = []
                for i, x in enumerate(nums):
                    needed = target - x
                    if needed in seen:
                        found = [seen[needed], i]
                        break
                    seen[x] = i
                return found, True

        # 4. Binary Search Verification Oracle
        if "binarysearch" in func_clean or "binarysearch" in code_clean or ("search" in func_clean and "target" in test_inputs):
            nums = test_inputs.get("nums", test_inputs.get(param_names[0] if param_names else "nums", []))
            target = test_inputs.get("target", test_inputs.get(param_names[1] if len(param_names) > 1 else "target", 0))
            if isinstance(nums, list) and isinstance(target, int):
                try:
                    idx = nums.index(target)
                    return idx, True
                except ValueError:
                    return -1, True

        # 5. Add Two Numbers Linked List Verification Oracle
        if "addtwonumbers" in func_clean or ("add" in func_clean and "two" in func_clean) or ("listnode" in code_clean and "carry" in code_clean):
            p1 = param_names[0] if len(param_names) > 0 else "l1"
            p2 = param_names[1] if len(param_names) > 1 else "l2"
            l1 = test_inputs.get(p1, test_inputs.get("l1", []))
            l2 = test_inputs.get(p2, test_inputs.get("l2", []))
            if isinstance(l1, list) and isinstance(l2, list):
                carry = 0
                i, j = 0, 0
                res = []
                while i < len(l1) or j < len(l2) or carry:
                    x = l1[i] if i < len(l1) else 0
                    y = l2[j] if j < len(l2) else 0
                    s = x + y + carry
                    carry = s // 10
                    res.append(s % 10)
                    i += 1
                    j += 1
                return res, True

        # 6. Average / Mean Verification Oracle
        if "average" in func_clean or "mean" in func_clean:
            numbers = test_inputs.get("numbers", test_inputs.get(param_names[0] if param_names else "numbers", []))
            if isinstance(numbers, list):
                if len(numbers) == 0:
                    # In clean specification, empty input should either raise an error or be handled gracefully
                    return "ZeroDivisionError (or 0.0 if handled)", False
                expected = sum(numbers) / len(numbers)
                return expected, True

        # 6. Fallback LLM Independent Oracle if API key is provided
        if api_key:
            try:
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=api_key)
                oracle_prompt = f"""
You are an independent formal software verification oracle.
Given the following specification of the algorithm:
Purpose: {analysis.purpose}
Function Signature: {analysis.signature}
Algorithmic Contract: {analysis.algorithmic_logic}

Input Values:
{json.dumps(test_inputs)}

Compute the exact, logically correct mathematical/expected output according to the problem specification.
If the expected output is unambiguous, return JSON:
{{"verified": true, "expected_output": <value>}}
If the behavior on this input is ambiguous, undefined, or unsupported by contract, return JSON:
{{"verified": false, "expected_output": "Unverified"}}
"""
                resp = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=oracle_prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.0
                    )
                )
                data = json.loads(resp.text)
                return data.get("expected_output", "Unverified"), bool(data.get("verified", False))
            except Exception as e:
                logger.warning(f"LLM Oracle failed: {e}")

        # When an expected output cannot be reliably determined, label it as Unverified
        return "Unverified", False
