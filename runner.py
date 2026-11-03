"""Robust hybrid code execution engine.
- Web (HTML/JS): Rendered in browser iframe.
- Python: Run locally via Python 3.12 (instant) or Wandbox fallback.
- JavaScript: Run locally via Node.js (instant) or Wandbox fallback.
- Java / C++ / Rust / Go: Run via Wandbox API (free, no auth, full sandbox).
"""
import sys
import os
import re
import subprocess
import requests
from typing import Dict, Any

WANDBOX_API = "https://wandbox.org/api/compile.json"

WANDBOX_COMPILERS = {
    "java": "openjdk-jdk-22+36",
    "c++": "gcc-13.2.0",
    "cpp": "gcc-13.2.0",
    "c": "gcc-13.2.0",
    "rust": "rust-1.78.0",
    "go": "go-1.22.2",
    "python": "cpython-3.12.3",
    "javascript": "nodejs-20.17.0"
}

def execute_code(language: str, code: str, stdin: str = "") -> Dict[str, Any]:
    """Execute code and return structured execution result."""
    lang = language.lower().strip()

    # Web Mode: rendered directly in iframe
    if lang in ("html", "html/js", "web"):
        return {
            "success": True,
            "stdout": "Web Component rendered in live iframe.",
            "stderr": "",
            "exit_code": 0,
            "engine": "Browser Iframe"
        }

    # Python Mode: prefer local execution
    if lang == "python":
        local_res = _run_python_local(code, stdin)
        if local_res["success"] or "Timed out" in local_res["stderr"]:
            return local_res
        # Fall back to Wandbox if local execution failed unexpectedly
        return _run_wandbox("python", code, stdin)

    # JavaScript / Node: prefer local node if available
    if lang in ("javascript", "js", "node"):
        local_res = _run_node_local(code, stdin)
        if local_res["success"] or "not recognized" not in local_res["stderr"]:
            return local_res
        return _run_wandbox("javascript", code, stdin)

    # Java / C++ / Rust / Go: run via Wandbox sandbox
    return _run_wandbox(lang, code, stdin)

def _run_python_local(code: str, stdin: str = "") -> Dict[str, Any]:
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            input=stdin,
            text=True,
            capture_output=True,
            timeout=8
        )
        return {
            "success": proc.returncode == 0,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "exit_code": proc.returncode,
            "engine": f"Local Python ({sys.version.split()[0]})"
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Execution timed out (limit: 8s).",
            "exit_code": -1,
            "engine": "Local Python"
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Local Python runner error: {str(e)}",
            "exit_code": 1,
            "engine": "Local Python"
        }

def _run_node_local(code: str, stdin: str = "") -> Dict[str, Any]:
    try:
        proc = subprocess.run(
            ["node", "-e", code],
            input=stdin,
            text=True,
            capture_output=True,
            timeout=8
        )
        return {
            "success": proc.returncode == 0,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "exit_code": proc.returncode,
            "engine": "Local Node.js"
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Execution timed out (limit: 8s).",
            "exit_code": -1,
            "engine": "Local Node.js"
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "exit_code": 1,
            "engine": "Local Node.js"
        }

def _run_wandbox(language: str, code: str, stdin: str = "") -> Dict[str, Any]:
    compiler = WANDBOX_COMPILERS.get(language, WANDBOX_COMPILERS.get("c++"))
    
    # In Java on Wandbox, class Prog or non-public class avoids "class is public should be in file named..."
    clean_code = code
    if language == "java":
        # Replace 'public class <Name>' with 'class <Name>'
        clean_code = re.sub(r"\bpublic\s+class\s+(\w+)", r"class \1", clean_code)

    payload = {
        "compiler": compiler,
        "code": clean_code,
        "stdin": stdin,
    }

    try:
        resp = requests.post(WANDBOX_API, json=payload, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            stdout = data.get("program_output", "") or data.get("program_message", "")
            stderr = data.get("compiler_error", "") or data.get("program_error", "")
            status = data.get("status", "0")
            
            return {
                "success": status == "0" and not stderr,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": int(status) if status.isdigit() else 0,
                "engine": f"Wandbox Sandbox ({compiler})"
            }
        else:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Sandbox HTTP {resp.status_code}: {resp.text}",
                "exit_code": 1,
                "engine": "Wandbox Sandbox"
            }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Sandbox execution error: {str(e)}",
            "exit_code": 1,
            "engine": "Wandbox Sandbox"
        }
