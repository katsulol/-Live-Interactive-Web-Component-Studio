"""Robust hybrid code execution engine.
- Web (HTML/JS): Rendered in browser iframe.
- Python: Run locally via Python 3.12 (instant) or Wandbox fallback.
- JavaScript: Run locally via Node.js (instant) or Wandbox fallback.
- Java / C++ / Rust / Go: Run via Wandbox API with verified compiler targets.
"""
import sys
import os
import re
import subprocess
import requests
from typing import Dict, Any

WANDBOX_API = "https://wandbox.org/api/compile.json"
WANDBOX_LIST_API = "https://wandbox.org/api/list.json"

# Verified active Wandbox compilers
VERIFIED_COMPILERS = {
    "java": "openjdk-jdk-22+36",
    "c++": "gcc-head",
    "cpp": "gcc-head",
    "c": "gcc-head-c",
    "rust": "rust-1.82.0",
    "go": "go-1.23.2",
    "python": "cpython-head",
    "javascript": "nodejs-20.17.0"
}

_DYNAMIC_COMPILER_CACHE = {}

def get_compiler(language: str) -> str:
    """Retrieve verified compiler string with dynamic fallback from Wandbox."""
    lang = language.lower().strip()
    if lang in VERIFIED_COMPILERS:
        return VERIFIED_COMPILERS[lang]
        
    global _DYNAMIC_COMPILER_CACHE
    if not _DYNAMIC_COMPILER_CACHE:
        try:
            resp = requests.get(WANDBOX_LIST_API, timeout=6)
            if resp.status_code == 200:
                for item in resp.json():
                    l_key = item.get("language", "").lower()
                    if l_key and l_key not in _DYNAMIC_COMPILER_CACHE:
                        _DYNAMIC_COMPILER_CACHE[l_key] = item.get("name")
        except Exception:
            pass

    return _DYNAMIC_COMPILER_CACHE.get(lang, "gcc-head")

def execute_code(language: str, code: str, stdin: str = "") -> Dict[str, Any]:
    """Execute code and return structured execution result."""
    lang = language.lower().strip()

    # Web Mode: rendered in iframe
    if lang in ("html", "html/js", "web"):
        return {
            "success": True,
            "stdout": "Web Component rendered in live browser iframe.",
            "stderr": "",
            "exit_code": 0,
            "engine": "Browser Iframe"
        }

    # Python Mode: prefer local execution
    if lang == "python":
        local_res = _run_python_local(code, stdin)
        if local_res["success"] or "Timed out" in local_res["stderr"]:
            return local_res
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
    compiler = get_compiler(language)
    
    # In Java on Wandbox, convert public class to package-private to avoid filename mismatch
    clean_code = code
    if language == "java":
        clean_code = re.sub(r"\bpublic\s+class\s+(\w+)", r"class \1", clean_code)

    payload = {
        "compiler": compiler,
        "code": clean_code,
        "stdin": stdin,
    }

    try:
        resp = requests.post(WANDBOX_API, json=payload, timeout=25)
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
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Sandbox compilation timed out (25s limit).",
            "exit_code": -1,
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
