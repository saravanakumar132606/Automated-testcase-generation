import os
import time
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env in the project root or backend directory
load_dotenv()

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .models import (
    CodeInputRequest,
    GenerationResponse,
    CodeAnalysis,
    ConfigStatus,
)
from .analyzer import detect_language, analyze_code_with_llm
from .generator import TestCaseGenerator
from .executor import TestExecutor
from .reporter import generate_testcases_txt
from .samples import SAMPLE_CODES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tcgen_api")

app = FastAPI(
    title="LLM-Based Automated Test Case Generation API",
    description="Automated Test Case Generation system inferring code semantics, generating targeted tests, and executing in safe isolation.",
    version="1.0.0"
)

# Enable CORS for frontend development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Runtime key storage (can also be loaded from GEMINI_API_KEY env)
runtime_api_key: Optional[str] = os.environ.get("GEMINI_API_KEY", "")

class KeyConfigRequest(BaseModel):
    api_key: str

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "Automated TestCase Generator"}

@app.get("/api/config", response_model=ConfigStatus)
def get_config():
    is_set = bool(runtime_api_key or os.environ.get("GEMINI_API_KEY"))
    return ConfigStatus(
        gemini_configured=is_set,
        default_model=os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite"),
        supported_languages=["python", "java", "cpp", "c"]
    )

@app.post("/api/config")
def update_config(req: KeyConfigRequest):
    global runtime_api_key
    runtime_api_key = req.api_key.strip()
    return {
        "status": "success",
        "gemini_configured": bool(runtime_api_key)
    }

@app.get("/api/samples")
def get_sample_codes():
    return {"samples": SAMPLE_CODES}

class UploadContentRequest(BaseModel):
    filename: str
    content: str

def validate_and_decode_code_text(raw_text: str, filename: Optional[str] = None) -> tuple:
    """Validates raw text, strips BOM, checks for emptiness/binary, and detects language."""
    if not raw_text or not raw_text.strip():
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty. Please provide a file containing source code."
        )

    # Clean BOM if present
    clean_text = raw_text.lstrip('\ufeff')

    # Detect if content is binary
    if '\x00' in clean_text:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file appears to be a binary file. Please upload a plain text source code file."
        )

    if len(clean_text) > 2_000_000:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum supported code size is 2MB."
        )

    detected_lang = detect_language(clean_text, filename)
    return clean_text, detected_lang

@app.post("/api/upload-content")
async def upload_code_content(req: UploadContentRequest):
    clean_text, detected_lang = validate_and_decode_code_text(req.content, req.filename)
    return {
        "filename": req.filename,
        "language": detected_lang,
        "code": clean_text
    }

try:
    @app.post("/api/upload")
    async def upload_code_file(file: UploadFile = File(...)):
        if not file.filename:
            raise HTTPException(status_code=400, detail="Uploaded file missing filename")

        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="The uploaded file is empty. Please provide a file containing source code.")

        if b'\x00' in content:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file appears to be a binary file. Please upload a plain text source code file (.py, .java, .cpp, .c, .txt)."
            )

        try:
            code_text = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            try:
                code_text = content.decode("latin-1")
            except Exception:
                raise HTTPException(status_code=400, detail="Could not decode file content as text. Please ensure it is a valid text file.")

        clean_text, detected_lang = validate_and_decode_code_text(code_text, file.filename)
        return {
            "filename": file.filename,
            "language": detected_lang,
            "code": clean_text
        }
except Exception as e:
    logger.warning(f"Multipart file upload disabled: {e}")

@app.post("/api/analyze", response_model=CodeAnalysis)
async def analyze_endpoint(req: CodeInputRequest):
    code = req.code.strip()
    if not code:
        raise HTTPException(status_code=400, detail="Submitted code cannot be empty.")
    
    language = req.language
    if language == "auto" or not language:
        language = detect_language(code, req.filename)

    key = req.api_key or runtime_api_key or os.environ.get("GEMINI_API_KEY")
    analysis = await analyze_code_with_llm(code, language, api_key=key)
    return analysis

@app.post("/api/generate", response_model=GenerationResponse)
async def generate_and_execute_endpoint(req: CodeInputRequest):
    code = req.code.strip()
    if not code:
        raise HTTPException(status_code=400, detail="Source code cannot be empty. Please provide or upload a solution.")

    if len(code) < 15:
        raise HTTPException(status_code=400, detail="The submitted code is too incomplete or ambiguous to analyze reliably.")

    language = req.language
    if language == "auto" or not language:
        language = detect_language(code, req.filename)

    key = req.api_key or runtime_api_key or os.environ.get("GEMINI_API_KEY")

    start_time = time.perf_counter()

    # Step 1: LLM & AST Code Analysis
    analysis = await analyze_code_with_llm(code, language, api_key=key)

    # Step 2: Meaningful Test Case Generation & Deduplication (Minimum 100 cases)
    test_cases = await TestCaseGenerator.generate_test_cases(analysis, code, api_key=key, min_cases=req.min_cases)

    # Step 3: Reference Execution and Validation
    validated_cases, metrics = TestExecutor.execute_and_validate(code, language, analysis, test_cases)

    # Step 4: Report Generation (testcases.txt format)
    report_text = generate_testcases_txt(validated_cases, analysis, metrics)

    total_latency_ms = (time.perf_counter() - start_time) * 1000.0
    metrics.total_time_ms = round(total_latency_ms, 2)

    return GenerationResponse(
        success=True,
        language=language,
        analysis=analysis,
        test_cases=validated_cases,
        metrics=metrics,
        report_text=report_text
    )

class DownloadReportRequest(BaseModel):
    report_text: str

@app.post("/api/download-report")
def download_report(req: DownloadReportRequest):
    return Response(
        content=req.report_text,
        media_type="text/plain",
        headers={
            "Content-Disposition": 'attachment; filename="testcases.txt"',
            "Cache-Control": "no-cache"
        }
    )

# Static files mount if frontend is built
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
