import asyncio
import httpx
from app.main import app

async def run_comprehensive_tests():
    print("=" * 60)
    print("  Comprehensive File Upload & Function Verification Test")
    print("=" * 60)

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Test 1: Upload .py file via /api/upload-content (JSON text)
        r = await client.post("/api/upload-content", json={
            "filename": "solution.py",
            "content": "def is_anagram(s: str, t: str) -> bool:\n    return sorted(s) == sorted(t)"
        })
        assert r.status_code == 200, f"Test 1 failed: {r.text}"
        data = r.json()
        assert data["language"] == "python"
        print("[PASS] Test 1: JSON upload of .py file (detected: python)")

        # Test 2: Upload .txt file containing Python code via /api/upload-content
        r = await client.post("/api/upload-content", json={
            "filename": "my_code.txt",
            "content": "def is_anagram(s, t):\n    return sorted(s) == sorted(t)"
        })
        assert r.status_code == 200, f"Test 2 failed: {r.text}"
        data = r.json()
        assert data["language"] == "python"
        print("[PASS] Test 2: JSON upload of .txt file (detected: python)")

        # Test 3: Upload .cpp file via /api/upload-content
        r = await client.post("/api/upload-content", json={
            "filename": "solution.cpp",
            "content": "#include <vector>\nusing namespace std;\nclass Solution {\npublic:\n    bool isAnagram(string s, string t) { return true; }\n};"
        })
        assert r.status_code == 200, f"Test 3 failed: {r.text}"
        data = r.json()
        assert data["language"] == "cpp"
        print("[PASS] Test 3: JSON upload of .cpp file (detected: cpp)")

        # Test 4: Upload file with no extension via /api/upload-content
        r = await client.post("/api/upload-content", json={
            "filename": "solution",
            "content": "public class Solution {\n    public boolean isPalindrome(String s) { return true; }\n}"
        })
        assert r.status_code == 200, f"Test 4 failed: {r.text}"
        data = r.json()
        assert data["language"] == "java"
        print("[PASS] Test 4: JSON upload of file without extension (detected: java)")

        # Test 5: Multipart upload of .py file via /api/upload
        files = {"file": ("code.py", b"def add(a, b):\n    return a + b", "text/x-python")}
        r = await client.post("/api/upload", files=files)
        assert r.status_code == 200, f"Test 5 failed: {r.text}"
        assert r.json()["language"] == "python"
        print("[PASS] Test 5: Multipart FormData upload of .py file")

        # Test 6: Multipart upload with UTF-8 BOM
        bom_content = b"\xef\xbb\xbfdef test():\n    return 42"
        files = {"file": ("bom_test.py", bom_content, "text/x-python")}
        r = await client.post("/api/upload", files=files)
        assert r.status_code == 200, f"Test 6 failed: {r.text}"
        assert not r.json()["code"].startswith("\ufeff")
        print("[PASS] Test 6: UTF-8 BOM properly stripped on upload")

        # Test 7: Reject binary file upload
        bin_content = b"\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        files = {"file": ("binary.bin", bin_content, "application/octet-stream")}
        r = await client.post("/api/upload", files=files)
        assert r.status_code == 400
        assert "binary" in r.json()["detail"].lower()
        print("[PASS] Test 7: Binary file upload properly rejected with 400 error")

        # Test 8: Reject empty file upload
        files = {"file": ("empty.py", b"", "text/plain")}
        r = await client.post("/api/upload", files=files)
        assert r.status_code == 400
        assert "empty" in r.json()["detail"].lower()
        print("[PASS] Test 8: Empty file upload properly rejected with 400 error")

        # Test 9: End-to-End Test Case Generation on LeetCode class-based code
        leetcode_code = """
class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        # Intentional frequency bug using set
        return len(s) == len(t) and set(s) == set(t)
"""
        r = await client.post("/api/generate", json={"code": leetcode_code, "language": "auto"})
        assert r.status_code == 200, f"Test 9 failed: {r.text}"
        gen_data = r.json()
        assert gen_data["language"] == "python"
        assert len(gen_data["test_cases"]) >= 100
        assert gen_data["metrics"]["bugs_exposed_count"] > 0
        print(f"[PASS] Test 9: LeetCode `class Solution` executed successfully with {len(gen_data['test_cases'])} test cases and exposed seeded bug!")

    print("\nALL FILE UPLOAD & PIPELINE CHECKS PASSED 100%!")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_tests())

