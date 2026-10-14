import asyncio
import httpx
from app.main import app

async def check_all():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/api/samples")
        samples = r.json()["samples"]
        print(f"Testing {len(samples)} sample problem solutions...")
        for s in samples:
            r = await client.post("/api/generate", json={"code": s["code"], "language": s["language"]})
            assert r.status_code == 200, f"Failed for {s['title']}: {r.text}"
            data = r.json()
            count = len(data["test_cases"])
            passed = data["metrics"]["passed_count"]
            failed = data["metrics"]["failed_count"]
            bugs = data["metrics"]["bugs_exposed_count"]
            print(f"  [OK] {s['title']} ({s['language']}): {count} cases | Passed: {passed}, Failed: {failed}, Bugs Caught: {bugs}")
            assert count >= 100, f"Expected >= 100 cases, but got {count} for {s['title']}"
        print("\nSUCCESS: All sample problems generate at least 100 test cases!")

if __name__ == "__main__":
    asyncio.run(check_all())

