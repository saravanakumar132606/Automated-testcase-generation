import asyncio
from app.analyzer import detect_language, fallback_static_analysis
from app.generator import TestCaseGenerator
from app.executor import TestExecutor
from app.reporter import generate_testcases_txt

code = '''class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        unordered_map<int, int> mp;
        for (int i = 0; i < nums.size(); i++) {
            int complement = target - nums[i];
            if (mp.find(complement) != mp.end()) {
                return {mp[complement], i};
            }
            mp[nums[i]] = i;
        }
        return {};
    }
};'''

async def run_pipeline():
    lang = detect_language(code)
    print(f"1. Language Detected: {lang}")
    analysis = fallback_static_analysis(code, lang)
    print(f"2. Method: {analysis.function_name}")
    print(f"   Signature: {analysis.signature}")
    print(f"   Purpose: {analysis.purpose}")
    print(f"   Parameters: {[(p.name, p.type_name) for p in analysis.input_parameters]}")

    cases = await TestCaseGenerator.generate_test_cases(analysis, code)
    print(f"\n3. Generated {len(cases)} test cases.")

    validated, metrics = TestExecutor.execute_and_validate(code, lang, analysis, cases)
    print(f"\n4. Execution Results: Passed: {metrics.passed_count}, Failed: {metrics.failed_count}, Errors: {metrics.error_count}, Unverified: {metrics.unverified_count}")

    print("\n5. First 2 test cases in testcases.txt format:")
    print("--------------------------------------------------")
    report = generate_testcases_txt(validated[:2], analysis, metrics)
    print(report)
    print("--------------------------------------------------")

if __name__ == "__main__":
    asyncio.run(run_pipeline())
