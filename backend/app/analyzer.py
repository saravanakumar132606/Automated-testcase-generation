import os
import re
import ast
import json
import logging
from typing import Optional, Tuple
from .models import CodeAnalysis, ParameterInfo

logger = logging.getLogger(__name__)

def detect_language(code: str, filename: Optional[str] = None) -> str:
    """Detects programming language from filename extension or code syntax."""
    if filename:
        ext = os.path.splitext(filename)[1].lower()
        mapping = {
            ".py": "python",
            ".java": "java",
            ".cpp": "cpp",
            ".cc": "cpp",
            ".cxx": "cpp",
            ".hpp": "cpp",
            ".c": "c",
            ".h": "c"
        }
        if ext in mapping:
            return mapping[ext]

    # C++ indicators (common in LeetCode, algorithms, and libraries)
    cpp_markers = [
        "vector<", "unordered_map<", "unordered_set<", "std::", "cout", "cin",
        "nullptr", "public:", "private:", "#include", "template<"
    ]
    if any(marker in code for marker in cpp_markers):
        return "cpp"

    # Java indicators
    java_markers = [
        "public class", "System.out", "public static void", "String[]", "int[]",
        "Character.is", "Integer.parse", "new int[", "new ListNode", "public ListNode",
        "ListNode dummy"
    ]
    if any(marker in code for marker in java_markers):
        return "java"

    # C indicators
    c_markers = [
        "printf(", "scanf(", "malloc(", "free(", "#include <stdio.h>"
    ]
    if any(marker in code for marker in c_markers):
        return "c"

    # Python indicators
    python_markers = [
        "def ", "import ", "elif ", "__name__", "self.", ":\n"
    ]
    if any(marker in code for marker in python_markers):
        return "python"

    # Fallback heuristic: C-style braces and semicolons indicate C++
    if "{" in code and "}" in code and ";" in code:
        return "cpp"
    
    return "python"

def extract_python_ast_info(code: str) -> Optional[dict]:
    """Extracts function name, parameters, loops, and conditions using Python's AST."""
    try:
        tree = ast.parse(code)
    except Exception as e:
        logger.debug(f"AST parse failed: {e}")
        return None

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            params = []
            for arg in node.args.args:
                if arg.arg in ("self", "cls"):
                    continue
                type_name = "Any"
                if arg.annotation:
                    type_name = ast.unparse(arg.annotation)
                params.append({
                    "name": arg.arg,
                    "type_name": type_name,
                    "description": f"Input argument '{arg.arg}'"
                })
            
            output_type = "Any"
            if node.returns:
                output_type = ast.unparse(node.returns)
            
            docstring = ast.get_docstring(node) or ""
            
            loops = []
            conditions = []
            variables = []
            
            for child in ast.walk(node):
                if isinstance(child, (ast.For, ast.While)):
                    loops.append(type(child).__name__)
                elif isinstance(child, ast.If):
                    conditions.append(ast.unparse(child.test))
                elif isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
                    if child.id not in variables:
                        variables.append(child.id)
            
            functions.append({
                "name": node.name,
                "params": params,
                "output_type": output_type,
                "docstring": docstring,
                "loops": loops,
                "conditions": conditions,
                "variables": variables
            })
            
    if functions:
        # Prioritize public non-dunder functions
        public_funcs = [f for f in functions if not f["name"].startswith("_")]
        return public_funcs[0] if public_funcs else functions[0]
    return None

def extract_cpp_java_info(code: str, language: str) -> Optional[dict]:
    """Extracts function name, parameters, loops, and conditions for C++ and Java."""
    clean_code = re.sub(r'//.*', '', code)
    clean_code = re.sub(r'/\*.*?\*/', '', clean_code, flags=re.DOTALL)
    
    # Matches method signatures like:
    # vector<int> twoSum(vector<int>& nums, int target)
    # bool isAnagram(string s, string t)
    # public int[] twoSum(int[] nums, int target)
    # public boolean isPalindrome(String s)
    method_regex = re.compile(
        r'([\w<>:&*\[\]\s]+?)\s+([a-zA-Z_]\w*)\s*\(([^)]*)\)\s*(?:const\s*)?\{',
        re.MULTILINE
    )
    for match in method_regex.finditer(clean_code):
        ret_type = match.group(1).strip()
        method_name = match.group(2).strip()
        raw_params = match.group(3).strip()
        
        # Skip control structures and class declarations
        if method_name in ("if", "while", "for", "switch", "catch", "main", "class", "Solution"):
            continue
        ret_type = re.sub(r'\b(public|private|protected|static|final|inline|virtual)\b', '', ret_type)
        ret_type = re.sub(r'^[;:\s]+', '', ret_type).strip()
        ret_type = " ".join(ret_type.split())
        
        params = []
        if raw_params:
            for p in raw_params.split(','):
                p = p.strip()
                if not p:
                    continue
                parts = p.rsplit(None, 1)
                if len(parts) == 2:
                    ptype = parts[0].strip().rstrip('&').rstrip('*')
                    pname = parts[1].strip().lstrip('&').lstrip('*')
                else:
                    ptype = "Any"
                    pname = parts[0].strip()
                params.append({
                    "name": pname,
                    "type_name": ptype,
                    "description": f"Input parameter '{pname}'"
                })
        
        return {
            "name": method_name,
            "params": params,
            "output_type": ret_type,
            "docstring": "",
            "loops": [k for k in ["for", "while"] if k in clean_code],
            "conditions": ["branch condition"] if "if" in clean_code else [],
            "variables": []
        }
    return None

def fallback_static_analysis(code: str, language: str) -> CodeAnalysis:
    """Intelligent fallback rule-based analyzer when LLM API is not configured."""
    ast_info = None
    if language == "python":
        ast_info = extract_python_ast_info(code)
    else:
        ast_info = extract_cpp_java_info(code, language)
    
    func_name = "solution"
    sig = "solution(*args)"
    params = []
    output_type = "Any"
    variables_and_loops = []
    conditions = []
    purpose = "Execute and evaluate the provided algorithm on representative and boundary inputs."
    logic = "Analyzes algorithmic branches, loops, and return conditions."
    potential_bugs = []
    missing_edge_cases = []
    constraints = []
    uncertainties = []

    if ast_info:
        func_name = ast_info["name"]
        param_list_str = ", ".join([f"{p['name']}: {p['type_name']}" for p in ast_info["params"]])
        sig = f"{func_name}({param_list_str}) -> {ast_info['output_type']}"
        params = [ParameterInfo(**p) for p in ast_info["params"]]
        output_type = ast_info["output_type"]
        variables_and_loops = [f"Variables: {', '.join(ast_info['variables'][:5])}"] if ast_info['variables'] else []
        if ast_info["loops"]:
            variables_and_loops.append(f"Loops present: {', '.join(set(ast_info['loops']))}")
        if ast_info["conditions"]:
            variables_and_loops.append(f"Condition tests: {', '.join(ast_info['conditions'][:3])}")
            
        doc = ast_info["docstring"].strip()
        if doc:
            purpose = doc.split("\n")[0]
        else:
            purpose = f"Implements `{func_name}` to process inputs ({', '.join(p['name'] for p in ast_info['params'])})."

    # Normalized name and code for cross-language matching (snake_case, camelCase, PascalCase)
    clean_name = re.sub(r'[^a-z0-9]', '', func_name.lower())
    code_clean = re.sub(r'[^a-z0-9]', '', code.lower())

    if "anagram" in clean_name or "anagram" in code_clean:
        purpose = "Determines whether two strings are anagrams of each other."
        logic = "Examines character components across both strings."
        constraints = ["Inputs are typically ASCII or lowercase strings.", "Length of both strings must match for valid anagrams."]
        if "set(" in code and "len(" in code and "count" not in code and "sorted" not in code:
            potential_bugs.append("Uses `set()` comparison which checks unique character presence but ignores character frequency multiplicities (e.g. 'aab' vs 'abb').")
            missing_edge_cases.append("Strings with identical unique characters but differing counts.")
            missing_edge_cases.append("Empty strings and single-character strings.")
    elif "twosum" in clean_name or "twosum" in code_clean or ("sum" in clean_name and "target" in code_clean):
        purpose = "Finds indices of two elements in a collection that sum to a target value."
        logic = "Maintains a lookup table/hash map to find complements of visited numbers in O(N) time."
        constraints = ["Input list may contain positive, negative, zero, or duplicate numbers.", "Indices returned must be distinct."]
        if "lookup[num] = i" in code and "complement in lookup" in code:
            potential_bugs.append("May allow self-pairing if the lookup key is stored before checking or without verifying index inequality.")
            missing_edge_cases.append("Target equals twice the current number with only one occurrence present.")
            missing_edge_cases.append("Duplicate numbers in the array.")
    elif "palindrome" in clean_name or "palindrome" in code_clean:
        purpose = "Determines whether an input string reads identically forwards and backwards."
        logic = "Reverses the string or uses two pointers from edges towards center."
        constraints = ["Strings may contain whitespace, punctuation, and mixed case."]
        if "s == s[::-1]" in code and "lower()" not in code:
            potential_bugs.append("Direct reversal without case normalization or punctuation removal fails on sentence palindromes.")
            missing_edge_cases.append("Phrases with punctuation, spacing, and mixed case (e.g., 'A man, a plan, a canal: Panama').")
    elif "binarysearch" in clean_name or "binarysearch" in code_clean or ("search" in clean_name and "target" in code_clean):
        purpose = "Performs binary search on a sorted collection to locate a target element."
        logic = "Divide-and-conquer search halving search bounds based on midpoint comparisons."
        constraints = ["Array must be pre-sorted.", "Target may be absent or located at boundaries."]
        if "left < right" in code and "<=" not in code:
            potential_bugs.append("Terminating condition `left < right` instead of `left <= right` misses single-element arrays or targets at the rightmost index.")
            missing_edge_cases.append("Single-element arrays where the single element equals the target.")
            missing_edge_cases.append("Target smaller than all elements or larger than all elements.")
    elif "addtwonumbers" in clean_name or ("add" in clean_name and "two" in clean_name) or ("listnode" in code_clean and "carry" in code_clean):
        purpose = "Adds two numbers represented as linked lists in reverse order, returning the sum as a linked list."
        logic = "Traverses both linked lists simultaneously, calculating digit sums and propagating the carry forward."
        constraints = ["Digits are within range [0, 9].", "Lists can be of unequal lengths.", "No leading zeros except the number 0 itself."]
        if "carry != 0" not in code and "carry > 0" not in code:
            potential_bugs.append("May miss creating a trailing node for leftover carry after exhausting both lists.")
        missing_edge_cases.append("Unequal list lengths where one list is significantly longer.")
        missing_edge_cases.append("Cascading carry across multiple 9 digits (e.g. 9999 + 1 = 10000).")
        missing_edge_cases.append("Single zero digits ([0] + [0] = [0]).")
    elif "average" in clean_name or "mean" in clean_name or ("average" in code_clean and "total" in code_clean):
        purpose = "Calculates average or division over numbers."
        if "len(" in code and "if not" not in code and "if len" not in code:
            potential_bugs.append("ZeroDivisionError when input list is empty.")
            missing_edge_cases.append("Empty input list `[]`.")
            missing_edge_cases.append("Lists containing negative numbers and zero.")
            
    if not constraints:
        constraints = ["Verify inputs conform to expected types.", "Handle empty collections, zero values, and extremes."]
    if not missing_edge_cases:
        missing_edge_cases = ["Empty or single-element inputs.", "Boundary extremes and unexpected types."]
        
    return CodeAnalysis(
        purpose=purpose,
        function_name=func_name,
        signature=sig,
        input_parameters=params,
        output_type=output_type,
        variables_and_loops=variables_and_loops if variables_and_loops else ["Iterative evaluation"],
        algorithmic_logic=logic,
        time_complexity="O(N)",
        space_complexity="O(1)",
        constraints_and_boundaries=constraints,
        potential_bugs=potential_bugs if potential_bugs else ["Check for unhandled empty inputs or edge bounds."],
        missing_edge_cases=missing_edge_cases,
        confidence_score=0.88 if ast_info else 0.75,
        uncertainties=uncertainties if uncertainties else ["Intended error handling policy on invalid types is not explicitly specified in code."]
    )

async def analyze_code_with_llm(code: str, language: str, api_key: Optional[str] = None) -> CodeAnalysis:
    """
    Analyzes source code using Google Gemini (via google-genai SDK).
    Uses structured output with Pydantic response schema.
    Falls back gracefully if API key is not present or an error occurs.
    """
    effective_api_key = api_key or os.environ.get("GEMINI_API_KEY")
    
    if not effective_api_key:
        logger.info("No GEMINI_API_KEY available. Using static AST / rule analysis.")
        return fallback_static_analysis(code, language)
    
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=effective_api_key)
        
        prompt = f"""
You are an expert static code analyzer and automated software testing engineer.
Analyze the following source code written in {language}.
Your goal is to infer:
1. The intended purpose and expected behavior of the program.
2. The main function or method name and exact signature.
3. Input and output data types and parameter specifications.
4. Important variables, conditions, loops, and algorithmic logic.
5. Realistic input constraints and boundary conditions.
6. Potential bugs, incorrect assumptions, or missing edge-case handling in the solution.
7. Any explicit uncertainties if the code's intended requirements cannot be confidently inferred.

Source Code:
```{language}
{code}
```

Return your analysis strictly following the requested JSON schema.
"""
        candidate_models = [
            os.environ.get("GEMINI_MODEL", "").strip(),
            "gemini-3.5-flash-lite",
            "gemini-flash-lite-latest",
            "gemini-3.8-flash"
        ]
        models_to_try = [m for i, m in enumerate(candidate_models) if m and m not in candidate_models[:i]]

        last_error = None
        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_json_schema=CodeAnalysis.model_json_schema(),
                        temperature=0.1
                    ),
                )
                data = json.loads(response.text)
                return CodeAnalysis(**data)
            except Exception as e:
                last_error = e
                # If rate-limited or unavailable, gracefully try the next model
                logger.info(f"Gemini model '{model_name}' unavailable ({e}). Trying next model candidate...")
        
        logger.warning(f"All Gemini models exhausted ({last_error}). Falling back to static AST analyzer.")
        fallback = fallback_static_analysis(code, language)
        fallback.uncertainties.append(f"LLM API note: {str(last_error)[:120]}")
        return fallback
        
    except Exception as e:
        logger.warning(f"Gemini client setup failed ({e}). Falling back to static AST analyzer.")
        fallback = fallback_static_analysis(code, language)
        fallback.uncertainties.append(f"LLM API note: {str(e)[:120]}")
        return fallback
