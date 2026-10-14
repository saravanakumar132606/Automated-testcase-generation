import asyncio
from app.analyzer import detect_language, fallback_static_analysis
from app.generator import TestCaseGenerator
from app.executor import TestExecutor
from app.reporter import generate_testcases_txt
from app.samples import SAMPLE_CODES

async def run_tests():
    print("==================================================")
    print("Testing Backend Pipeline with Anagram Checker Bug")
    print("==================================================")

    sample = SAMPLE_CODES[0] # Anagram checker
    code = sample["code"]
    lang = detect_language(code)
    print(f"Detected language: {lang}")

    # Step 1: Static / Rule Analysis
    analysis = fallback_static_analysis(code, lang)
    print(f"Inferred purpose: {analysis.purpose}")
    print(f"Inferred function: {analysis.signature}")
    print(f"Potential bugs identified: {analysis.potential_bugs}")

    # Step 2: Generation
    test_cases = await TestCaseGenerator.generate_test_cases(analysis, code)
    print(f"Generated {len(test_cases)} categorized test cases.")

    # Step 3: Execution and Validation
    validated, metrics = TestExecutor.execute_and_validate(code, lang, analysis, test_cases)
    print(f"Execution complete. Passed: {metrics.passed_count}, Failed: {metrics.failed_count}, Bugs Exposed: {metrics.bugs_exposed_count}")

    # Verify that the 'aab' vs 'abb' test case was executed and caught the bug!
    bug_case = next((tc for tc in validated if "aab" in tc.inputs.get("s", "") or "abb" in tc.inputs.get("t", "")), None)
    if bug_case:
        print("\n--- Bug Exposing Test Case Inspection ---")
        print(f"Title: {bug_case.title}")
        print(f"Input: {bug_case.input_formatted}")
        print(f"Expected: {bug_case.expected_output}")
        print(f"Actual: {bug_case.actual_output}")
        print(f"Status: {bug_case.status}")
        print(f"Reason: {bug_case.reason}")
        assert bug_case.status == "FAIL", f"Expected bug case to FAIL, got {bug_case.status}"
        print(">>> SUCCESS: Seeded frequency bug was correctly caught and flagged as FAIL!")

    # Step 4: Report generation
    report = generate_testcases_txt(validated, analysis, metrics)
    print("\n--- Sample of testcases.txt Output ---")
    print("\n".join(report.splitlines()[:25]))
    print("...\n--- End of Sample ---")

    print("\nALL BACKEND MODULE TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_tests())
