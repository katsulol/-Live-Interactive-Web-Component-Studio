"""Groq LLM code generator and iterative refiner."""
import os
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

DEFAULT_MODEL = "openai/gpt-oss-120b"
AVAILABLE_MODELS = [
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-20b"
]

SYSTEM_PROMPTS = {
    "html": """You are an elite frontend engineer and UI/UX designer.
When generating a Web Component / App:
- Output a single, self-contained HTML file.
- Use Tailwind CSS via CDN: <script src="https://cdn.tailwindcss.com"></script>.
- If icons are needed, use Lucide or FontAwesome via CDN or inline SVGs.
- If charts/animations are needed, use Chart.js or Canvas.
- Write fully functional, beautiful, modern, responsive JavaScript directly inside <script> tags.
- Include interactive features (state changes, calculations, buttons, dark mode toggle, filters).
- CRITICAL: Output ONLY the raw executable code inside a ```html ... ``` block. No markdown chatter before or after.
""",
    "python": """You are a senior Python engineer.
When generating Python code:
- Output clean, modern, standalone Python 3 code.
- Include working test cases, clear stdout outputs, and docstrings.
- Self-contained: runs from top to bottom with standard library or common packages.
- CRITICAL: Output ONLY the raw executable code inside a ```python ... ``` block. No markdown chatter.
""",
    "java": """You are a senior Java engineer.
When generating Java code:
- Output a single standalone Java program with a public class named `Main` containing `public static void main(String[] args)`.
- Self-contained in one file.
- Include realistic demo data and clear console print statements to verify output.
- CRITICAL: Output ONLY the raw executable code inside a ```java ... ``` block. No markdown chatter.
""",
    "c++": """You are a senior C++ engineer.
When generating C++ code:
- Output modern C++17/C++20 standard standalone code with `int main()`.
- Include clear std::cout statements to demonstrate functionality.
- CRITICAL: Output ONLY the raw executable code inside a ```cpp ... ``` block. No markdown chatter.
""",
    "javascript": """You are a senior JavaScript / Node engineer.
When generating JavaScript code:
- Output standalone runnable Node.js/JS code with console.log outputs.
- CRITICAL: Output ONLY the raw executable code inside a ```javascript ... ``` block. No markdown chatter.
""",
    "default": """You are an expert polyglot software engineer.
Output clean, production-ready, standalone code.
CRITICAL: Output ONLY the raw code inside a markdown code block (e.g., ```language ... ```). No fluff or conversation.
"""
}

def get_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set. Check your .env file.")
    return Groq(api_key=api_key)

def clean_code(raw_response: str) -> str:
    """Extract clean code from markdown code fences or return raw if no fences."""
    pattern = r"```(?:[a-zA-Z0-9_\-\+]+)?\s*\n([\s\S]*?)```"
    match = re.search(pattern, raw_response)
    if match:
        return match.group(1).strip()
    return raw_response.strip()

def generate_code(prompt: str, language: str = "html", model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """Generate brand new code from a natural language prompt."""
    client = get_client()
    lang_key = "html" if language.lower() in ("html", "html/js", "web") else language.lower()
    system_prompt = SYSTEM_PROMPTS.get(lang_key, SYSTEM_PROMPTS["default"])

    user_message = f"Language: {language}\nCreate a complete, fully functional, self-contained project for the following request:\n{prompt}"

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.3,
        max_tokens=4096
    )

    raw_text = response.choices[0].message.content or ""
    code = clean_code(raw_text)
    
    return {
        "code": code,
        "language": language,
        "prompt": prompt,
        "model": model,
        "tokens_used": response.usage.total_tokens if response.usage else 0
    }

def refine_code(
    existing_code: str,
    modification_prompt: str,
    language: str,
    history: Optional[list] = None,
    model: str = DEFAULT_MODEL
) -> Dict[str, Any]:
    """Iteratively refine or update existing code based on user feedback."""
    client = get_client()
    lang_key = "html" if language.lower() in ("html", "html/js", "web") else language.lower()
    system_prompt = SYSTEM_PROMPTS.get(lang_key, SYSTEM_PROMPTS["default"])

    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation context if available
    if history:
        for turn in history[-4:]:
            messages.append({"role": turn.get("role", "user"), "content": turn.get("content", "")})

    refine_instruction = f"""Here is the CURRENT existing code in {language}:
```{language}
{existing_code}
```

REQUESTED MODIFICATIONS:
{modification_prompt}

Please update the code to apply these exact changes while preserving all existing functionality and formatting.
CRITICAL: Return the FULL updated standalone code in a ```{language} ... ``` code block. No partial snippets, no diffs.
"""

    messages.append({"role": "user", "content": refine_instruction})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
        max_tokens=4096
    )

    raw_text = response.choices[0].message.content or ""
    code = clean_code(raw_text)

    return {
        "code": code,
        "language": language,
        "prompt": modification_prompt,
        "model": model,
        "tokens_used": response.usage.total_tokens if response.usage else 0
    }
