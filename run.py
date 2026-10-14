#!python3.11
"""
Launcher script for LLM-Based Automated Test Case Generation System.
Starts the FastAPI backend which also serves the compiled React frontend.
"""
import os
import sys

# Ensure backend is in sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(root_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import socket
import webbrowser
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()

import uvicorn

def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0

def find_available_port(start_port: int = 8000, host: str = "127.0.0.1") -> int:
    port = start_port
    while is_port_in_use(port, host):
        port += 1
    return port

def main():
    host = "127.0.0.1"
    requested_port = int(os.environ.get("PORT", 8000))
    port = find_available_port(requested_port, host)
    
    if port != requested_port:
        print(f"[!] Note: Port {requested_port} is already in use by another process. Automatically using port {port} instead.")

    url = f"http://{host}:{port}"

    print("=" * 60)
    print("  LLM-Based Automated Test Case Generation System")
    print("=" * 60)
    print(f" Starting server at: {url}")
    print(f" Web UI: {url}")
    print(f" Interactive API Docs: {url}/docs")
    print(" Press Ctrl+C to terminate.")
    print("=" * 60)

    try:
        # Open browser automatically
        webbrowser.open(url)
    except Exception:
        pass

    uvicorn.run("app.main:app", host=host, port=port, reload=False, app_dir=backend_dir)

if __name__ == "__main__":
    main()
