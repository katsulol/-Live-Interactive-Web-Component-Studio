"""Live Interactive Multi-Language Web Component & Code Studio — EF Minimalist Edition."""
import re
import difflib
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

import db
import generator
import runner

# Initialize database
db.init_db()

# Page Setup
st.set_page_config(
    page_title="CodeStudio — Autonomous Engineering Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Entrepreneur First Minimalist Styling System
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Container Spacing */
    .main .block-container {
        padding-top: 1.25rem;
        padding-bottom: 2.5rem;
        max-width: 95%;
    }

    /* EF Brand Mark */
    .brand-container {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 4px;
    }
    .brand-mark {
        font-size: 1.25rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        color: #FAFAFA;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .brand-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #E11D48;
        display: inline-block;
        box-shadow: 0 0 10px rgba(225, 29, 72, 0.7);
    }
    .brand-sub {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: #71717A;
    }

    /* EF Micro Badges */
    .ef-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 3px 10px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
        border-radius: 9999px;
        background: #18181B;
        border: 1px solid #27272A;
        color: #E4E4E7;
        margin-right: 6px;
    }
    .ef-pill-rose {
        background: rgba(225, 29, 72, 0.1);
        border-color: rgba(225, 29, 72, 0.28);
        color: #FB7185;
    }
    .ef-pill-emerald {
        background: rgba(16, 185, 129, 0.1);
        border-color: rgba(16, 185, 129, 0.28);
        color: #34D399;
    }

    /* Minimalist Cards */
    .ef-card {
        background: #111114;
        border: 1px solid #222226;
        border-radius: 8px;
        padding: 1.4rem;
        height: 100%;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }
    .ef-card:hover {
        border-color: #3F3F46;
    }
    .ef-card-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: #FB7185;
        margin-bottom: 0.5rem;
    }
    .ef-card-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #FAFAFA;
        letter-spacing: -0.02em;
        margin-bottom: 0.4rem;
    }
    .ef-card-body {
        font-size: 0.88rem;
        color: #A1A1AA;
        line-height: 1.5;
    }

    /* Terminal Console Window */
    .terminal-window {
        background: #09090C;
        border: 1px solid #27272A;
        border-radius: 8px;
        overflow: hidden;
        margin-top: 0.6rem;
    }
    .terminal-header {
        background: #121216;
        border-bottom: 1px solid #1E1E24;
        padding: 0.55rem 0.95rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .terminal-dots {
        display: flex;
        gap: 6px;
    }
    .terminal-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
    }
    .dot-red { background: #FF5F56; }
    .dot-yellow { background: #FFBD2E; }
    .dot-green { background: #27C93F; }
    .terminal-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #A1A1AA;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .terminal-body {
        padding: 1.1rem;
        font-family: 'JetBrains Mono', Courier, monospace;
        font-size: 0.85rem;
        color: #E4E4E7;
        white-space: pre-wrap;
        word-break: break-all;
        min-height: 200px;
        max-height: 500px;
        overflow-y: auto;
        line-height: 1.55;
    }

    /* Notification Banner */
    .ef-banner {
        background: #0E1613;
        border: 1px solid #1A3D2E;
        border-left: 3px solid #10B981;
        padding: 1rem 1.25rem;
        border-radius: 6px;
        margin-bottom: 1rem;
    }
    .ef-banner-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #6EE7B7;
        margin-bottom: 0.25rem;
    }
    .ef-banner-desc {
        font-size: 0.85rem;
        color: #D1FAE5;
        margin-bottom: 0.5rem;
    }

    /* Polished Tabs */
    button[data-baseweb="tab"] {
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        letter-spacing: -0.01em !important;
        padding: 0.65rem 1.1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "current_project_id" not in st.session_state:
    st.session_state.current_project_id = None
if "selected_version_id" not in st.session_state:
    st.session_state.selected_version_id = None
if "terminal_result" not in st.session_state:
    st.session_state.terminal_result = None
if "refinement_notice" not in st.session_state:
    st.session_state.refinement_notice = None

def compute_diff(old_code: str, new_code: str, old_label: str = "Old", new_label: str = "New"):
    """Compute unified diff and count added/removed lines."""
    old_lines = old_code.splitlines(keepends=True)
    new_lines = new_code.splitlines(keepends=True)
    diff = list(difflib.unified_diff(
        old_lines, new_lines,
        fromfile=old_label,
        tofile=new_label,
        n=3
    ))
    diff_text = "".join(diff)
    added = sum(1 for line in diff if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))
    return diff_text, added, removed

# Sidebar: Projects & Version History
with st.sidebar:
    st.markdown("""
    <div class="brand-container">
        <span class="brand-dot"></span>
        <span class="brand-mark">CODESTUDIO</span>
    </div>
    <div class="brand-sub">Autonomous Code Engine // 01</div>
    """, unsafe_allow_html=True)
    st.divider()

    # New Project Expander
    with st.expander("New Project", expanded=False):
        new_proj_name = st.text_input("Project Name", placeholder="e.g. Portfolio Tracker")
        new_proj_lang = st.selectbox(
            "Target Language",
            ["HTML/Tailwind (Visual)", "Python", "Java", "JavaScript", "C++", "Go", "Rust"]
        )
        if st.button("Initialize Project", width="stretch", type="primary"):
            if new_proj_name.strip():
                lang_key = "html" if "HTML" in new_proj_lang else new_proj_lang.lower().split()[0]
                new_id = db.create_project(new_proj_name.strip(), lang_key)
                st.session_state.current_project_id = new_id
                st.session_state.selected_version_id = None
                st.session_state.terminal_result = None
                st.rerun()
            else:
                st.error("Enter a project name.")

    # Project Selector
    projects = db.list_projects()
    if projects:
        st.markdown("<p style='font-family:\"JetBrains Mono\", monospace; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.12em; color:#71717A; margin-bottom:6px;'>Saved Vaults</p>", unsafe_allow_html=True)
        proj_options = {p["id"]: f"{p['name']} ({p['language'].upper()}) · v{p['version_count']}" for p in projects}
        
        if st.session_state.current_project_id not in proj_options:
            st.session_state.current_project_id = projects[0]["id"]
            
        selected_id = st.selectbox(
            "Select Project",
            options=list(proj_options.keys()),
            format_func=lambda x: proj_options[x],
            index=list(proj_options.keys()).index(st.session_state.current_project_id),
            label_visibility="collapsed"
        )
        if selected_id != st.session_state.current_project_id:
            st.session_state.current_project_id = selected_id
            st.session_state.selected_version_id = None
            st.session_state.terminal_result = None
            st.rerun()

        # Version History for Current Project
        current_project = db.get_project(st.session_state.current_project_id)
        versions = db.get_versions(st.session_state.current_project_id)

        if versions:
            st.markdown("<p style='font-family:\"JetBrains Mono\", monospace; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.12em; color:#71717A; margin-top:14px; margin-bottom:6px;'>Snapshot Timeline</p>", unsafe_allow_html=True)
            ver_options = {v["id"]: f"v{v['version_number']} [{v.get('language', 'code').upper()}] · {v['created_at'].split()[1][:5]} ({v['prompt'][:16]}...)" for v in versions}
            
            if st.session_state.selected_version_id not in ver_options:
                st.session_state.selected_version_id = versions[-1]["id"]
                
            chosen_ver_id = st.selectbox(
                "Active Snapshot",
                options=list(ver_options.keys()),
                format_func=lambda x: ver_options[x],
                index=list(ver_options.keys()).index(st.session_state.selected_version_id),
                label_visibility="collapsed"
            )
            if chosen_ver_id != st.session_state.selected_version_id:
                st.session_state.selected_version_id = chosen_ver_id
                st.session_state.terminal_result = None
                st.rerun()

        # Delete Project Option
        st.divider()
        if st.button("Delete Project Vault", width="stretch"):
            db.delete_project(st.session_state.current_project_id)
            st.session_state.current_project_id = None
            st.session_state.selected_version_id = None
            st.session_state.terminal_result = None
            st.rerun()
    else:
        st.info("No projects yet. Create one above to get started.")

    st.divider()
    st.markdown("<p style='font-family:\"JetBrains Mono\", monospace; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.12em; color:#71717A; margin-bottom:6px;'>Inference Engine</p>", unsafe_allow_html=True)
    selected_model = st.selectbox("Groq LLM Engine", generator.AVAILABLE_MODELS, index=0, label_visibility="collapsed")

# Main Application Area
if not st.session_state.current_project_id:
    # EF Landing / Welcome View
    st.markdown("""
    <div style="margin-top: 1.5rem; margin-bottom: 2rem;">
        <span class="ef-pill ef-pill-rose">Autonomous IDE // v1.0</span>
        <h1 style="font-size: 2.75rem; font-weight: 800; letter-spacing: -0.04em; color: #FAFAFA; margin-top: 0.75rem; margin-bottom: 0.5rem;">
            Build software from pure intent.
        </h1>
        <p style="font-size: 1.1rem; color: #A1A1AA; max-width: 680px; line-height: 1.6;">
            Turn natural language briefs into self-contained, interactive web applications and verified polyglot algorithms in seconds.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="ef-card">
            <div class="ef-card-tag">Sandbox // 01</div>
            <div class="ef-card-title">Live Web Studio</div>
            <div class="ef-card-body">Generates single-file HTML5 + Tailwind CSS + JavaScript web applications rendered directly in an interactive browser runtime.</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="ef-card">
            <div class="ef-card-tag">Execution // 02</div>
            <div class="ef-card-title">Polyglot Runner</div>
            <div class="ef-card-body">Compiles and runs Python 3.12, Java 22, Node.js, C++17, Rust, and Go with telemetry and live stdout/stderr streams.</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="ef-card">
            <div class="ef-card-tag">Evolution // 03</div>
            <div class="ef-card-title">Snapshot Diffing</div>
            <div class="ef-card-body">Refine code iteratively via natural language. Every modification produces an immutable snapshot with unified code diffs.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    st.info("Initialize a project vault in the sidebar to start building.")
    st.stop()

# Load current active project and version
current_project = db.get_project(st.session_state.current_project_id)
if not current_project:
    st.session_state.current_project_id = None
    st.rerun()

versions = db.get_versions(st.session_state.current_project_id)
active_version = None

if versions:
    if st.session_state.selected_version_id:
        active_version = next((v for v in versions if v["id"] == st.session_state.selected_version_id), versions[-1])
    else:
        active_version = versions[-1]

# Top Header Bar
header_cols = st.columns([2.3, 1.2, 0.75, 0.75])
with header_cols[0]:
    current_lang_tag = active_version.get("language", current_project["language"]).upper() if active_version else current_project["language"].upper()
    ver_str = f"v{active_version['version_number']}" if active_version else "v0"
    st.markdown(f"""
    <div style="display: flex; align-items: baseline; gap: 12px;">
        <h2 style="margin: 0; font-weight: 700; letter-spacing: -0.03em; color: #FAFAFA;">{current_project['name']}</h2>
        <div>
            <span class="ef-pill ef-pill-rose">{current_lang_tag}</span>
            <span class="ef-pill">{ver_str}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with header_cols[1]:
    target_langs = ["HTML/Tailwind (Visual)", "Python", "Java", "JavaScript", "C++", "Go", "Rust"]

    def get_lang_index(lang_code: str) -> int:
        for idx, tl in enumerate(target_langs):
            if (lang_code == "html" and "HTML" in tl) or (lang_code == tl.lower().split()[0]):
                return idx
        return 1

    def on_project_lang_change():
        key_name = f"proj_lang_selector_{current_project['id']}_{current_project['language']}"
        chosen_label = st.session_state.get(key_name)
        if chosen_label:
            clean_lang = "html" if "HTML" in chosen_label else chosen_label.lower().split()[0]
            db.update_project_language(current_project["id"], clean_lang)
            st.session_state.terminal_result = None
            all_v = db.get_versions(current_project["id"])
            matching = [v for v in all_v if v.get("language", "").lower() == clean_lang]
            if matching:
                st.session_state.selected_version_id = matching[-1]["id"]

    st.selectbox(
        "Project Language Mode",
        options=target_langs,
        index=get_lang_index(current_project["language"]),
        key=f"proj_lang_selector_{current_project['id']}_{current_project['language']}",
        on_change=on_project_lang_change,
        label_visibility="collapsed"
    )

with header_cols[2]:
    if active_version:
        ext_map = {"html": "html", "python": "py", "java": "java", "javascript": "js", "c++": "cpp", "go": "go", "rust": "rs"}
        ext = ext_map.get(active_version.get("language", current_project["language"]), "txt")
        filename = f"{current_project['name'].lower().replace(' ', '_')}_v{active_version['version_number']}.{ext}"
        st.download_button(
            label="Download",
            data=active_version["code"],
            file_name=filename,
            mime="text/plain",
            width="stretch"
        )

with header_cols[3]:
    if active_version and active_version.get("language") not in ("html", "web"):
        if st.button("Run Code", type="primary", width="stretch"):
            with st.spinner(f"Compiling & executing {active_version['language'].upper()}..."):
                res = runner.execute_code(active_version["language"], active_version["code"])
                st.session_state[f"term_res_{active_version['id']}"] = res
                st.rerun()

# Language Mismatch / Transpile Banner
if active_version and active_version.get("language", "").lower() != current_project["language"].lower():
    target_l = current_project["language"].upper()
    active_l = active_version.get("language", "code").upper()
    col_t_banner, col_t_actions = st.columns([2.5, 1.5])
    with col_t_banner:
        st.markdown(f"""
        <div style="background:#141416; border:1px solid #27272A; border-left:3px solid #E11D48; border-radius:6px; padding:0.6rem 0.9rem; margin-top:0.4rem; margin-bottom:0.6rem;">
            <div style="font-family:'JetBrains Mono', monospace; font-size:0.68rem; color:#E11D48; text-transform:uppercase; letter-spacing:0.08em; font-weight:600;">Language Mode Mismatch</div>
            <div style="font-size:0.85rem; color:#FAFAFA; margin-top:2px;">Project target is <b>{target_l}</b>, but active snapshot v{active_version['version_number']} is in <b>{active_l}</b>.</div>
        </div>
        """, unsafe_allow_html=True)
    with col_t_actions:
        st.markdown("<div style='margin-top:0.4rem;'></div>", unsafe_allow_html=True)
        if st.button(f"⚡ Transpile to {target_l}", type="primary", width="stretch", key="transpile_header_action"):
            with st.status(f"Transpiling codebase from {active_l} to {target_l} via Groq ({selected_model})...", expanded=True) as status:
                status.write(f"Generating idiomatic {target_l} equivalent...")
                if current_project["language"] in ("html", "web"):
                    conv_prompt = f"Convert this {active_l} program into a complete, modern, interactive visual Web Application with Tailwind CSS and JavaScript:\n\n{active_version['code']}"
                else:
                    conv_prompt = f"Convert this {active_l} program into a complete, standalone, production-ready {target_l} program with working main execution and console output:\n\n{active_version['code']}"
                
                res = generator.generate_code(conv_prompt, current_project["language"], model=selected_model)
                new_code = res["code"]
                
                status.write(f"Verifying runtime output for {target_l}...")
                new_output = ""
                if current_project["language"] not in ("html", "web"):
                    exec_res = runner.execute_code(current_project["language"], new_code)
                    if not exec_res.get("success") and exec_res.get("stderr"):
                        status.write("⚠️ Compiler error detected. Auto-healing with AI...")
                        fix_res = generator.fix_code(new_code, exec_res["stderr"], current_project["language"], model=selected_model)
                        re_res = runner.execute_code(current_project["language"], fix_res["code"])
                        if re_res.get("success") or len(re_res.get("stderr", "")) < len(exec_res.get("stderr", "")):
                            new_code = fix_res["code"]
                            exec_res = re_res
                    new_output = exec_res.get("stdout", "") or exec_res.get("stderr", "")
                
                new_ver_id = db.add_version(
                    current_project["id"],
                    f"Transpile from {active_l} to {target_l}",
                    new_code,
                    current_project["language"],
                    output=new_output or f"{target_l} code generated successfully."
                )
                st.session_state.selected_version_id = new_ver_id
                st.session_state["refinement_notice"] = {
                    "from_v": active_version["version_number"],
                    "to_v": active_version["version_number"] + 1,
                    "prompt": f"Transpiled from {active_l} to {target_l}",
                    "added": len(new_code.splitlines()),
                    "removed": 0,
                    "diff": ""
                }
                status.update(label=f"Successfully deployed v{active_version['version_number'] + 1} ({target_l}).", state="complete")
                st.toast(f"Transpiled to {target_l}.")
                st.rerun()

# Banner Alert if a Refinement was just applied
if st.session_state.refinement_notice:
    notice = st.session_state.refinement_notice
    with st.container():
        st.markdown(f"""
        <div class="ef-banner">
            <div class="ef-banner-title">● Snapshot v{notice['to_v']} Deployed (from v{notice['from_v']})</div>
            <div class="ef-banner-desc"><b>Modification:</b> <i>"{notice['prompt']}"</i></div>
            <span class="ef-pill ef-pill-emerald">+{notice['added']} lines added</span>
            <span class="ef-pill ef-pill-rose">-{notice['removed']} lines removed</span>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("Inspect Code Diff", expanded=False):
            if notice["diff"].strip():
                st.code(notice["diff"], language="diff")
            else:
                st.info("No textual code delta detected.")
        if st.button("Dismiss", key="dismiss_banner"):
            st.session_state.refinement_notice = None
            st.rerun()

st.divider()

# View: Initial Generation Prompt if no versions exist
if not active_version:
    st.markdown("<h3 style='font-weight:700; letter-spacing:-0.03em;'>Synthesize Initial Prototype</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#A1A1AA; font-size:0.95rem;'>Describe the specification for <b>{current_project['language'].upper()}</b>:</p>", unsafe_allow_html=True)

    sample_prompts = {
        "html": [
            "Mortgage & Amortization Calculator with real-time sliders, breakdown charts, and dark theme",
            "Kanban Board with drag-and-drop tasks, color priority tags, local persistence, and filtering",
            "Real-time Crypto Portfolio Simulator with simulated tick charts and buy/sell modal"
        ],
        "python": [
            "CLI Key-Value Store with WAL log, AES encryption, snapshot compression, and benchmarks",
            "Statistical Outlier Detection engine with synthetic time-series data and formatted ASCII summary",
            "A* Pathfinding visualization on a 20x20 grid with step-by-step heuristic metrics"
        ],
        "java": [
            "Self-balancing Red-Black Tree implementation with insertion, deletion, and level-order traversal",
            "Concurrent Banking Ledger with simulated thread-safe transactions and invariant audit check",
            "High-performance generic LRU Cache with TTL expiry and micro-benchmarks"
        ],
        "javascript": [
            "Distributed Event Bus simulation with regex topic matching, backpressure, and metrics",
            "Token Bucket Rate Limiter with simulated concurrent request spikes and rejection logs"
        ]
    }
    
    current_samples = sample_prompts.get(current_project["language"], sample_prompts["html"])
    st.markdown("<p style='font-family:\"JetBrains Mono\", monospace; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.1em; color:#71717A; margin-bottom:4px;'>Curated Blueprints</p>", unsafe_allow_html=True)
    selected_sample = None
    cols = st.columns(len(current_samples))
    for i, s_prompt in enumerate(current_samples):
        if cols[i].button(s_prompt[:42] + "...", key=f"chip_{i}", width="stretch"):
            selected_sample = s_prompt

    initial_prompt = st.text_area(
        "Prompt",
        value=selected_sample if selected_sample else "",
        placeholder="e.g. Build an interactive loan calculator with responsive dark theme and real-time computation...",
        height=130,
        label_visibility="collapsed"
    )

    if st.button("Synthesize Prototype with AI", type="primary", width="stretch"):
        if initial_prompt.strip():
            with st.spinner(f"Synthesizing {current_project['language'].upper()} prototype with Groq ({selected_model})..."):
                try:
                    res = generator.generate_code(initial_prompt, current_project["language"], model=selected_model)
                    new_code = res["code"]
                    init_output = ""
                    if current_project["language"] not in ("html", "web"):
                        exec_res = runner.execute_code(current_project["language"], new_code)
                        if not exec_res.get("success") and exec_res.get("stderr"):
                            with st.spinner("Compile error detected. Auto-fixing with AI..."):
                                fix_res = generator.fix_code(new_code, exec_res["stderr"], current_project["language"], model=selected_model)
                                re_res = runner.execute_code(current_project["language"], fix_res["code"])
                                if re_res.get("success") or len(re_res.get("stderr", "")) < len(exec_res.get("stderr", "")):
                                    new_code = fix_res["code"]
                                    exec_res = re_res
                        st.session_state[f"term_res_init"] = exec_res
                        init_output = exec_res.get("stdout", "") or exec_res.get("stderr", "")
                    
                    new_row_id = db.add_version(
                        current_project["id"],
                        initial_prompt,
                        new_code,
                        current_project["language"],
                        output=init_output
                    )
                    st.session_state.selected_version_id = new_row_id
                    st.success("Prototype synthesized successfully.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Generation error: {str(e)}")
        else:
            st.warning("Please provide a prompt.")
    st.stop()

# Existing Project with active version: 4 Tabs
tab_preview, tab_code, tab_refine, tab_diff = st.tabs([
    "Preview & Runtime",
    "Code Inspector",
    "Iterative AI Refinement",
    "Version Diff"
])

# TAB 1: PREVIEW / CONSOLE
with tab_preview:
    raw_code = active_version["code"].strip()
    is_html = (
        active_version.get("language", "").lower() in ("html", "web")
        or current_project.get("language", "").lower() in ("html", "web")
        or "<!doctype html" in raw_code.lower()
        or "<html" in raw_code.lower()
    )

    if is_html:
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: #A1A1AA;">
                Runtime // Browser Sandbox (v{active_version['version_number']})
            </span>
            <span class="ef-pill ef-pill-emerald">● Live DOM</span>
        </div>
        """, unsafe_allow_html=True)
        
        clean_html = re.sub(r"^```(?:html)?\s*", "", raw_code, flags=re.IGNORECASE)
        clean_html = re.sub(r"```\s*$", "", clean_html).strip()
        components.html(
            clean_html,
            height=720,
            scrolling=True
        )
    else:
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: #A1A1AA;">
                Runtime // {active_version.get('language', current_project['language']).upper()} Console (v{active_version['version_number']})
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        # Banner & Convert to Web UI Action
        col_mode_msg, col_mode_btn = st.columns([3, 1.2])
        with col_mode_msg:
            st.info("Operating in Terminal Mode. Output reflects CLI stdout.")
        with col_mode_btn:
            if st.button("Convert to Web UI", type="primary", width="stretch"):
                with st.status("Synthesizing interactive Web UI with Tailwind CSS...", expanded=True) as status:
                    status.write("Synthesizing responsive HTML/Tailwind/JS web app...")
                    convert_prompt = f"Convert this {current_project['name']} program into a modern, complete, interactive visual Web App with Tailwind CSS, input controls, buttons, dark mode, and real-time results:\n\n{active_version['code']}"
                    res = generator.generate_code(convert_prompt, "html", model=selected_model)
                    status.write("Saving snapshot to vault...")
                    db.update_project_language(current_project["id"], "html")
                    new_ver_id = db.add_version(
                        current_project["id"],
                        "Convert to Interactive Web UI",
                        res["code"],
                        "html",
                        output="Web Component rendered in browser sandbox."
                    )
                    st.session_state.selected_version_id = new_ver_id
                    st.session_state["refinement_notice"] = {
                        "from_v": active_version["version_number"],
                        "to_v": active_version["version_number"] + 1,
                        "prompt": "Converted to Interactive Web UI",
                        "added": len(res["code"].splitlines()),
                        "removed": 0,
                        "diff": ""
                    }
                    status.update(label="Converted to Visual Web App.", state="complete")
                    st.toast("Converted to Visual Web App.")
                    st.rerun()
        
        # Stdin input expander
        with st.expander("Program Input (stdin)", expanded=False):
            stdin_input = st.text_area("Input data for process stream", height=80, label_visibility="collapsed")
            if st.button("Execute with Input", width="stretch"):
                with st.spinner("Executing..."):
                    res = runner.execute_code(active_version.get("language", current_project["language"]), active_version["code"], stdin=stdin_input)
                    st.session_state[f"term_res_{active_version['id']}"] = res
                    st.rerun()

        # Display terminal output for active version
        term_res = st.session_state.get(f"term_res_{active_version['id']}")
        if not term_res:
            if active_version.get("output"):
                term_res = {
                    "success": True,
                    "stdout": active_version["output"],
                    "stderr": "",
                    "exit_code": 0,
                    "engine": "Snapshot Output"
                }
            else:
                with st.spinner("Executing initial run..."):
                    term_res = runner.execute_code(active_version.get("language", current_project["language"]), active_version["code"])
                    st.session_state[f"term_res_{active_version['id']}"] = term_res

        engine_name = term_res.get("engine", "Executor")
        exit_code = term_res.get("exit_code", 0)
        status_label = "SUCCESS" if term_res.get("success") else "FAILED"
        status_color = "#34D399" if term_res.get("success") else "#F87171"
        
        stdout_text = term_res.get("stdout", "").strip()
        stderr_text = term_res.get("stderr", "").strip()
        
        output_display = ""
        if stdout_text:
            output_display += stdout_text
        if stderr_text:
            if output_display:
                output_display += "\n\n--- ERRORS / WARNINGS ---\n"
            output_display += stderr_text
        if not output_display:
            output_display = "[Process executed with zero output]"
            
        if not term_res.get("success") or exit_code != 0:
            err_details = stderr_text or stdout_text or "Process exited with non-zero exit code."
            col_fix_msg, col_fix_btn = st.columns([2.5, 1.5])
            with col_fix_msg:
                st.markdown(f"""
                <div style="background:#181012; border:1px solid #5C1D24; border-left:3px solid #E11D48; border-radius:6px; padding:0.6rem 0.9rem; margin-top:0.3rem; margin-bottom:0.6rem;">
                    <span style="font-family:'JetBrains Mono', monospace; font-size:0.68rem; color:#E11D48; text-transform:uppercase; letter-spacing:0.08em; font-weight:600;">Compilation / Runtime Error</span>
                    <div style="font-size:0.85rem; color:#FECDD3; margin-top:2px;">Execution failed (Exit {exit_code}). Automated self-healing available.</div>
                </div>
                """, unsafe_allow_html=True)
            with col_fix_btn:
                st.markdown("<div style='margin-top:0.3rem;'></div>", unsafe_allow_html=True)
                if st.button("⚡ Auto-Fix Error with AI", type="primary", width="stretch", key=f"autofix_err_btn_{active_version['id']}"):
                    with st.status(f"Diagnosing and auto-fixing compiler error with Groq ({selected_model})...", expanded=True) as fix_status:
                        curr_lang = active_version.get("language", current_project["language"])
                        fix_status.write(f"Feeding compiler output to {selected_model}...")
                        fix_res = generator.fix_code(
                            broken_code=active_version["code"],
                            error_message=err_details,
                            language=curr_lang,
                            model=selected_model
                        )
                        fixed_code = fix_res["code"]
                        
                        fix_status.write(f"Re-compiling and verifying {curr_lang.upper()} output...")
                        retest_res = runner.execute_code(curr_lang, fixed_code)
                        
                        diff_text, added, removed = compute_diff(
                            active_version["code"],
                            fixed_code,
                            old_label=f"v{active_version['version_number']} (broken)",
                            new_label=f"v{active_version['version_number'] + 1} (fixed)"
                        )
                        
                        fix_status.write("Saving healed snapshot to vault...")
                        new_ver_id = db.add_version(
                            current_project["id"],
                            f"Auto-fix: {err_details.splitlines()[0][:32] if err_details else 'compiler fix'}",
                            fixed_code,
                            curr_lang,
                            output=retest_res.get("stdout", "") or retest_res.get("stderr", "")
                        )
                        st.session_state.selected_version_id = new_ver_id
                        st.session_state[f"term_res_{new_ver_id}"] = retest_res
                        st.session_state["refinement_notice"] = {
                            "from_v": active_version["version_number"],
                            "to_v": active_version["version_number"] + 1,
                            "prompt": "Auto-healed compilation error",
                            "added": added,
                            "removed": removed,
                            "diff": diff_text
                        }
                        if retest_res.get("success"):
                            fix_status.update(label="Self-healing successful! Zero compiler errors.", state="complete")
                            st.toast("Compiler error auto-fixed!")
                        else:
                            fix_status.update(label="Fix applied (check remaining diagnostics).", state="complete")
                        st.rerun()

        st.markdown(f"""
        <div class="terminal-window">
            <div class="terminal-header">
                <div class="terminal-dots">
                    <span class="terminal-dot dot-red"></span>
                    <span class="terminal-dot dot-yellow"></span>
                    <span class="terminal-dot dot-green"></span>
                </div>
                <span class="terminal-title">PROCESS // {engine_name}</span>
                <span style="font-family:'JetBrains Mono', monospace; font-size:0.72rem; color:{status_color}; font-weight:600;">{status_label} (EXIT {exit_code})</span>
            </div>
            <div class="terminal-body">{output_display}</div>
        </div>
        """, unsafe_allow_html=True)

# TAB 2: CODE INSPECTOR
with tab_code:
    code_lang = active_version.get("language", current_project["language"])
    col_code_top1, col_code_top2 = st.columns([3, 1])
    with col_code_top1:
        st.markdown(f"<p style='font-family:\"JetBrains Mono\", monospace; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.1em; color:#A1A1AA; margin:0;'>Artifact Source // {code_lang.upper()}</p>", unsafe_allow_html=True)
    with col_code_top2:
        st.markdown(f"<p style='font-family:\"JetBrains Mono\", monospace; font-size:0.75rem; color:#71717A; text-align:right; margin:0;'>{len(active_version['code'].splitlines())} lines · {len(active_version['code']):,} bytes</p>", unsafe_allow_html=True)
        
    syntax_map = {
        "html": "html",
        "web": "html",
        "python": "python",
        "java": "java",
        "javascript": "javascript",
        "js": "javascript",
        "c++": "cpp",
        "cpp": "cpp",
        "go": "go",
        "rust": "rust"
    }
    syntax_lang = syntax_map.get(code_lang.lower(), code_lang.lower())
    if code_lang.lower() != current_project["language"].lower():
        st.caption(f"Note: Snapshot v{active_version['version_number']} is in {code_lang.upper()}. Use the Transpile button above to convert it to {current_project['language'].upper()}.")
    st.code(active_version["code"], language=syntax_lang, line_numbers=True)

# TAB 3: ITERATIVE AI REFINEMENT
with tab_refine:
    st.markdown("<h4 style='font-weight:700; letter-spacing:-0.03em;'>Iterative Refinement Engine</h4>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A1A1AA; font-size:0.9rem;'>Issue natural language directives to update the codebase. Every modification generates an immutable snapshot with verified diffs.</p>", unsafe_allow_html=True)
    
    with st.expander(f"Original Prompt for active snapshot (v{active_version['version_number']})", expanded=False):
        st.info(active_version["prompt"])
        
    quick_mods = [
        "Add a dark mode toggle and polish color palette",
        "Add unit test cases to verify edge cases",
        "Add strict input validation and defensive error handling",
        "Refactor layout for mobile responsiveness"
    ]
    st.markdown("<p style='font-family:\"JetBrains Mono\", monospace; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.1em; color:#71717A; margin-bottom:4px;'>Quick Modifiers</p>", unsafe_allow_html=True)
    mod_cols = st.columns(len(quick_mods))
    chosen_mod = None
    for i, qm in enumerate(quick_mods):
        if mod_cols[i].button(qm, key=f"mod_chip_{i}", width="stretch"):
            chosen_mod = qm
            
    refine_prompt = st.text_area(
        "Modification Directive",
        value=chosen_mod if chosen_mod else "",
        placeholder="e.g. Add an interactive search filter box and animate transition cards...",
        height=120,
        label_visibility="collapsed"
    )
    
    if st.button("Synthesize Modifications (Deploy Next Snapshot)", type="primary", width="stretch"):
        if refine_prompt.strip():
            with st.status("Synthesizing refinements with AI...", expanded=True) as status:
                try:
                    target_lang = active_version.get("language", current_project["language"])
                    status.write(f"Querying Groq ({selected_model}) for {target_lang.upper()} with codebase context...")
                    res = generator.refine_code(
                        existing_code=active_version["code"],
                        modification_prompt=refine_prompt,
                        language=target_lang,
                        model=selected_model
                    )
                    updated_code = res["code"]
                    
                    status.write("Computing syntactic code diff...")
                    diff_text, added, removed = compute_diff(
                        active_version["code"],
                        updated_code,
                        old_label=f"v{active_version['version_number']}",
                        new_label=f"v{active_version['version_number'] + 1}"
                    )
                    
                    new_output = ""
                    if target_lang not in ("html", "web"):
                        status.write(f"Executing updated {target_lang.upper()} process...")
                        exec_res = runner.execute_code(target_lang, updated_code)
                        if not exec_res.get("success") and exec_res.get("stderr"):
                            status.write("⚠️ Compiler error encountered. Auto-healing with AI...")
                            fix_res = generator.fix_code(updated_code, exec_res["stderr"], target_lang, model=selected_model)
                            re_res = runner.execute_code(target_lang, fix_res["code"])
                            if re_res.get("success") or len(re_res.get("stderr", "")) < len(exec_res.get("stderr", "")):
                                updated_code = fix_res["code"]
                                exec_res = re_res
                        new_output = exec_res.get("stdout", "") or exec_res.get("stderr", "")
                    
                    status.write("Writing snapshot to vault...")
                    new_ver_id = db.add_version(
                        current_project["id"],
                        refine_prompt,
                        updated_code,
                        target_lang,
                        output=new_output
                    )
                    
                    all_vers = db.get_versions(current_project["id"])
                    new_ver_obj = next((v for v in all_vers if v["id"] == new_ver_id), None)
                    new_ver_num = new_ver_obj["version_number"] if new_ver_obj else active_version["version_number"] + 1

                    st.session_state["refinement_notice"] = {
                        "from_v": active_version["version_number"],
                        "to_v": new_ver_num,
                        "prompt": refine_prompt,
                        "added": added,
                        "removed": removed,
                        "diff": diff_text
                    }
                    st.session_state.selected_version_id = new_ver_id
                    
                    status.update(label=f"Snapshot v{new_ver_num} Deployed (+{added}/-{removed} lines)", state="complete")
                    st.toast(f"Snapshot v{new_ver_num} Deployed.")
                    st.rerun()
                except Exception as e:
                    status.update(label="Refinement failed", state="error")
                    st.error(f"Refinement error: {str(e)}")
        else:
            st.warning("Please describe what changes to apply.")

    # Show history of all prompts applied in this project
    if len(versions) > 1:
        st.divider()
        st.markdown("<p style='font-family:\"JetBrains Mono\", monospace; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.12em; color:#71717A; margin-bottom:8px;'>Evolutionary History</p>", unsafe_allow_html=True)
        for v in reversed(versions):
            st.markdown(f"<p style='font-size:0.86rem; color:#D4D4D8; margin-bottom:4px;'><b>v{v['version_number']}</b> <span style='color:#71717A;'>({v['created_at'].split()[1][:5]})</span>: <i>{v['prompt']}</i></p>", unsafe_allow_html=True)

# TAB 4: VERSION DIFF & COMPARISON
with tab_diff:
    st.markdown("<h4 style='font-weight:700; letter-spacing:-0.03em;'>Snapshot Comparator</h4>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A1A1AA; font-size:0.9rem;'>Inspect granular code changes between any two project snapshots.</p>", unsafe_allow_html=True)
    
    if len(versions) < 2:
        st.info("Only 1 version exists. Synthesize a refinement to generate and compare snapshots.")
    else:
        diff_col1, diff_col2 = st.columns(2)
        with diff_col1:
            base_v_num = st.selectbox(
                "Base Snapshot",
                options=[v["version_number"] for v in versions],
                index=max(0, len(versions) - 2),
                format_func=lambda x: f"Snapshot v{x} [{next((v.get('language', '').upper() for v in versions if v['version_number'] == x), '')}]"
            )
        with diff_col2:
            target_v_num = st.selectbox(
                "Compare Snapshot",
                options=[v["version_number"] for v in versions],
                index=len(versions) - 1,
                format_func=lambda x: f"Snapshot v{x} [{next((v.get('language', '').upper() for v in versions if v['version_number'] == x), '')}]"
            )
            
        base_v = next(v for v in versions if v["version_number"] == base_v_num)
        target_v = next(v for v in versions if v["version_number"] == target_v_num)
        
        diff_text, lines_added, lines_removed = compute_diff(
            base_v["code"],
            target_v["code"],
            old_label=f"v{base_v_num}",
            new_label=f"v{target_v_num}"
        )
        
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        stat_col1.metric("Lines Added", f"+{lines_added}")
        stat_col2.metric("Lines Removed", f"-{lines_removed}")
        stat_col3.metric("Net Delta", f"{lines_added - lines_removed:+d}")
        
        st.markdown(f"<p style='font-size:0.82rem; color:#71717A; margin-top:8px;'><b>v{base_v_num}:</b> <i>{base_v['prompt']}</i><br><b>v{target_v_num}:</b> <i>{target_v['prompt']}</i></p>", unsafe_allow_html=True)
        
        st.divider()
        if diff_text.strip():
            st.markdown("<p style='font-family:\"JetBrains Mono\", monospace; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.1em; color:#A1A1AA;'>Unified Code Diff</p>", unsafe_allow_html=True)
            st.code(diff_text, language="diff")
        else:
            st.info("The code in both selected snapshots is identical.")
