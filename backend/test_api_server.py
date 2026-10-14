import asyncio
import httpx
from app.main import app

async def test_api_client():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Test 1: Health
        r = await client.get("/api/health")
        assert r.status_code == 200, f"Health failed: {r.status_code}"
        print("[OK] Health endpoint:", r.json())

        # Test 2: Samples
        r = await client.get("/api/samples")
        assert r.status_code == 200, f"Samples failed: {r.status_code}"
        samples = r.json()["samples"]
        print(f"[OK] Samples endpoint: {len(samples)} samples found")

        # Test 3: Generate for Anagram
        anagram = samples[0]
        r = await client.post("/api/generate", json={"code": anagram["code"], "language": "python"})
        assert r.status_code == 200, f"Generate failed: {r.status_code}, {r.text}"
        data = r.json()
        print(f"[OK] Generate endpoint: {len(data['test_cases'])} test cases generated")
        print(f"  Purpose: {data['analysis']['purpose']}")
        print(f"  Passed: {data['metrics']['passed_count']}, Failed: {data['metrics']['failed_count']}, Bugs Caught: {data['metrics']['bugs_exposed_count']}")

        # Test 4: Download report
        r = await client.post("/api/download-report", json={"report_text": data["report_text"]})
        assert r.status_code == 200, f"Download failed: {r.status_code}"
        assert "Content-Disposition" in r.headers
        assert "testcases.txt" in r.headers["Content-Disposition"]
        print("[OK] Download report endpoint (Content-Disposition: testcases.txt)")

        # Test 5: Static frontend index.html
        r = await client.get("/")
        assert r.status_code == 200, f"Frontend static failed: {r.status_code}"
        assert "<div id=\"root\"></div>" in r.text
        print("[OK] Frontend static index.html served seamlessly at root '/'!")

        print("\nALL FASTAPI ENDPOINTS & STATIC FRONTEND SERVING VERIFIED 100% OK!")

if __name__ == "__main__":
    asyncio.run(test_api_client())
