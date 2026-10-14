import asyncio
from app.analyzer import detect_language, fallback_static_analysis
from app.generator import TestCaseGenerator
from app.oracle import ReferenceOracle

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

async def test():
    lang = detect_language(code)
    print(f"Detected language: {lang}")
    analysis = fallback_static_analysis(code, lang)
    print(f"Function: {analysis.function_name}")
    print(f"Signature: {analysis.signature}")
    print(f"Parameters: {[(p.name, p.type_name) for p in analysis.input_parameters]}")
    print(f"Purpose: {analysis.purpose}")

    cases = await TestCaseGenerator.generate_test_cases(analysis, code)
    print(f"\nGenerated {len(cases)} test cases:")
    for c in cases[:3]:
        print(f"--- {c.title} ---")
        print(f"Input: {c.input_formatted}")
        print(f"Expected: {c.expected_output}")

if __name__ == "__main__":
    asyncio.run(test())
