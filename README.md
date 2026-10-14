# LLM-Based Automated Test Case Generation from Source Code

An autonomous, end-to-end Automated Test Case Generation system that accepts only a user's solution code, analyzes it using a Large Language Model (Gemini 3.8 Flash via `google-genai` SDK) and AST static analysis, infers intended contracts and edge cases, generates logic-based test cases, executes them in an isolated subprocess sandbox against an independent reference oracle, exposes potential bugs, and exports the results in a downloadable `testcases.txt` report.

---

## Architecture Overview

```
                                      +--------------------------+
                                      |   Uploaded Source Code   |
                                      | (.py, .java, .cpp, .c)   |
                                      +-------------+------------+
                                                    |
                                                    v
                             +-----------------------------------------------+
                             |             Code Semantic Analyzer            |
                             |  - AST Structural Parser                      |
                             |  - Gemini 3.8 Flash (Structured Output)       |
                             |  - Fallback Semantic Heuristic Engine         |
                             +----------------------+------------------------+
                                                    | Inferred Contracts, Signatures,
                                                    | Boundaries & Potential Bugs
                                                    v
                             +-----------------------------------------------+
                             |           Test Case Generator Engine          |
                             |  - 9 Logical Categories                       |
                             |  - Seeded Defect Target Hunting               |
                             |  - Deduplication & Canonical Normalization    |
                             +----------------------+------------------------+
                                                    | Categorized Test Inputs
                                                    v
                +-----------------------------------+-----------------------------------+
                |                                                                       |
                v                                                                       v
+-------------------------------+                                       +-------------------------------+
|  Independent Reference Oracle |                                       |   Isolated Sandbox Runner     |
|  - Independent Math Truth     |                                       |   - Subprocess Isolation      |
|  - Reliable Behavioral Rules  |                                       |   - Timeout Enforcement       |
|  - Status: PASS/FAIL/ERROR/   |                                       |   - Sanitized Environment     |
|            UNVERIFIED         |                                       |   - Captures Actual Output    |
+---------------+---------------+                                       +---------------+---------------+
                | Expected Output                                                       | Actual Output
                +-----------------------------------+-----------------------------------+
                                                    |
                                                    v
                             +-----------------------------------------------+
                             |        Validation & Metric Comparator         |
                             |  - Mismatch Detection & Bug Exposure          |
                             |  - Execution Latency & Pass Rates             |
                             +----------------------+------------------------+
                                                    |
                                                    v
                             +-----------------------------------------------+
                             |            Export & User Interface            |
                             |  - React + Vite Interactive Dashboard         |
                             |  - Downloadable "testcases.txt" Report        |
                             +-----------------------------------------------+
```

---

## Key Features

1. **Zero-Manual-Input Requirement**:
   - The user provides **only** the solution code (uploaded file or pasted directly into the editor).
   - No problem statement, description, or manually crafted test cases required.

2. **Semantic Code Analysis**:
   - Infers program purpose, signatures, parameter types, conditions, loops, and algorithmic complexity.
   - Discovers subtle bugs, unhandled edge cases, and boundary vulnerabilities.
   - Explicitly notes ambiguities if requirements cannot be inferred with certainty.

3. **100+ Meaningful, Logic-Based Test Inputs (Minimum 100 Guaranteed)**:
   - Every problem generates **at least 100 to 140+ comprehensive, categorized test cases**:
     - Normal and representative inputs
     - Minimum and maximum boundary values
     - Empty and single-element inputs
     - Duplicate values and repeated characters
     - Negative numbers, zero, and positive numbers
     - Special characters, whitespace, and case variations
     - Meaningful words and domain phrases (e.g., `"listen"`/`"silent"`, `"book"`/`"kobo"`, `"aab"`/`"abb"`)
     - Invalid or contract-violating inputs
     - Defect-hunting inputs targeting suspected algorithm bugs
     - Large inputs for performance benchmarking (up to 5,000 elements)

4. **Independent Reference Validation & Safe Execution**:
   - Executes solution code in an isolated temporary environment with timeouts and sanitized environment variables.
   - Compares against an **independent reference oracle**; never assumes the user's uploaded code is correct.
   - Detects and categorizes outcomes as **`PASS`**, **`FAIL`**, **`ERROR`**, or **`UNVERIFIED`**.

5. **Official Test Case Report (`testcases.txt`)**:
   - Generates and downloads `testcases.txt` formatted according to the exact specification:
     ```
     Test Case 1: Valid Anagram

     Input:
     s = "listen"
     t = "silent"

     Expected Output: true
     Actual Output: true
     Status: PASS

     Reason:
     Both strings contain identical characters with identical frequencies.

     ---

     Test Case 2: Character Frequency Mismatch

     Input:
     s = "aab"
     t = "abb"

     Expected Output: false
     Actual Output: true
     Status: FAIL

     Reason:
     The submitted solution incorrectly accepts strings with different character frequencies.
     ```

6. **Interactive Modern Web Interface**:
   - Built with React, Vite, and Tailwind CSS.
   - Line-numbered code editor with file upload (drag & drop) and language auto-detection.
   - Pre-loaded interactive demo problems (Anagram frequency bug, Two Sum self-pairing bug, Palindrome punctuation bug, Binary Search boundary bug, Average ZeroDivision bug, C++, Java).
   - Real-time Execution Metrics Dashboard (Pass rate, Seeded bugs caught, Latency).
   - Filterable test case cards with side-by-side expected vs. actual output diffs.
   - One-click `testcases.txt` download and clipboard copy.

---

## Technology Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic v2
- **LLM Integration**: Google GenAI SDK (`google-genai`), structured output (`response_json_schema`) targeting `gemini-3.8-flash`
- **Static Analysis & Rule Engine**: Python `ast` module, heuristic pattern analyzers
- **Execution Sandbox**: Subprocess process isolation, timeout enforcement, sanitized environment
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide icons
- **Export Engine**: Standard RFC compliant text report exporter

---

## Quick Start & Running the Project

### 1. Launch the Application
Run the launcher script from the project root:
```powershell
python run.py
```
Or on Windows, simply double-click `start.bat`.

The system will start the web server at:
- **Web UI**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive OpenAPI Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Configure Gemini API Key (Optional)
The system works out-of-the-box using the built-in AST and Semantic Heuristic engine.
To activate Gemini 3.8 Flash for advanced reasoning:
- Click the **Gear icon (Settings)** in the top navigation bar of the Web UI and paste your API key, or
- Set the environment variable:
  ```powershell
  $env:GEMINI_API_KEY = "your-api-key"
  ```

---

## Running Backend Verification Tests

You can run automated integration tests directly via terminal:
```powershell
# Run Anagram bug detection and report verification test
python backend/test_backend.py

# Run all 5 seeded problem test suites
python backend/test_all_samples.py

# Run API server endpoint test
python backend/test_api_server.py
```
#   A u t o m a t e d - t e s t c a s e - g e n e r a t i o n  
 