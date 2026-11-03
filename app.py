"""Live Interactive Multi-Language Web Component & Code Studio."""
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
    page_title="CodeStudio - Live Multi-Language AI Playground",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 95%;
    }
    .badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        font-size: 0.8rem;
        font-weight: 600;
        border-radius: 9999px;
        background-color: #2563eb;
        color: white;
        margin-right: 0.5rem;
    }
    .badge-secondary {
        background-color: #4b5563;
    }
    .badge-success {
        background-color: #059669;
    }
    .terminal-box {
        background-color: #0d1117;
        color: #58a6ff;
        padding: 1rem;
        border-radius: 8px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.9rem;
        border: 1px solid #30363d;
        white-space: pre-wrap;
        word-break: break-all;
        min-height: 180px;
        max-height: 450px;
        overflow-y: auto;
    }
    .terminal-err {
        color: #f85149;
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
    st.markdown("## ⚡ **CodeStudio AI**")
    st.caption("Prompt $\\rightarrow$ Working Code $\\rightarrow$ Live Execution")
    st.divider()

    # New Project Expander
    with st.expander("➕ **Create New Project**", expanded=False):
        new_proj_name = st.text_input("Project Name", placeholder="e.g. Finance Dashboard or QuickSort")
        new_proj_lang = st.selectbox(
            "Target Language",
            ["HTML/Tailwind (Visual)", "Python", "Java", "JavaScript", "C++", "Go", "Rust"]
        )
        if st.button("Create Project", use_container_width=True, type="primary"):
            if new_proj_name.strip():
                # Clean language key
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
        st.markdown("### 📁 **Your Projects**")
        proj_options = {p["id"]: f"{p['name']} ({p['language'].upper()}) - v{p['version_count']}" for p in projects}
        
        # Default to first project if none selected
        if st.session_state.current_project_id not in proj_options:
            st.session_state.current_project_id = projects[0]["id"]
            
        selected_id = st.selectbox(
            "Select Project",
            options=list(proj_options.keys()),
            format_func=lambda x: proj_options[x],
            index=list(proj_options.keys()).index(st.session_state.current_project_id)
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
            st.markdown("### ⏱️ **Version Timeline**")
            ver_options = {v["id"]: f"v{v['version_number']} - {v['created_at'].split()[1][:5]} ({v['prompt'][:20]}...)" for v in versions}
            
            # Default to latest version if not set or invalid
            if st.session_state.selected_version_id not in ver_options:
                st.session_state.selected_version_id = versions[-1]["id"]
                
            chosen_ver_id = st.selectbox(
                "Active Version Snapshot",
                options=list(ver_options.keys()),
                format_func=lambda x: ver_options[x],
                index=list(ver_options.keys()).index(st.session_state.selected_version_id)
            )
            if chosen_ver_id != st.session_state.selected_version_id:
                st.session_state.selected_version_id = chosen_ver_id
                st.session_state.terminal_result = None
                st.rerun()

        # Delete Project Option
        st.divider()
        if st.button("🗑️ Delete Current Project", use_container_width=True):
            db.delete_project(st.session_state.current_project_id)
            st.session_state.current_project_id = None
            st.session_state.selected_version_id = None
            st.session_state.terminal_result = None
            st.rerun()
    else:
        st.info("No projects yet. Create one above to get started!")

    st.divider()
    # Model Selector
    selected_model = st.selectbox("Groq LLM Engine", generator.AVAILABLE_MODELS, index=0)

# Main Application Area
if not st.session_state.current_project_id:
    # Landing / Welcome View
    st.markdown("## 🚀 **Welcome to CodeStudio AI**")
    st.markdown("Generate interactive web components and runnable multi-language code in seconds.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🌐 **Live Web Studio**")
        st.write("Generates single-file HTML/Tailwind/JS apps rendered live in an interactive sandbox.")
    with col2:
        st.markdown("### 💻 **Multi-Language Runner**")
        st.write("Generates Python, Java, JavaScript, and C++ code. Runs instantly with terminal output.")
    with col3:
        st.markdown("### 🔄 **Iterative Versioning**")
        st.write("Refine code iteratively via natural language with snapshot timeline & rollback.")

    st.info("👈 Create a project in the sidebar to start!")
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

# Header Bar
header_cols = st.columns([2.2, 1.3, 0.9, 0.9])
with header_cols[0]:
    lang_upper = current_project['language'].upper()
    ver_str = f"v{active_version['version_number']}" if active_version else "v0 (Empty)"
    st.markdown(f"## **{current_project['name']}**")
    st.markdown(f"<span class='badge'>{lang_upper}</span> <span class='badge badge-secondary'>{ver_str}</span>", unsafe_allow_html=True)

with header_cols[1]:
    # Language Mode Switcher
    target_langs = ["HTML/Tailwind (Visual)", "Python", "Java", "JavaScript", "C++", "Go", "Rust"]
    current_idx = 0
    for idx, tl in enumerate(target_langs):
        if (current_project["language"] == "html" and "HTML" in tl) or (current_project["language"] == tl.lower().split()[0]):
            current_idx = idx
            break
    new_lang_choice = st.selectbox(
        "Project Language Mode",
        options=target_langs,
        index=current_idx,
        key=f"proj_lang_selector_{current_project['id']}"
    )
    clean_new_lang = "html" if "HTML" in new_lang_choice else new_lang_choice.lower().split()[0]
    if clean_new_lang != current_project["language"]:
        db.update_project_language(current_project["id"], clean_new_lang)
        st.session_state.terminal_result = None
        st.rerun()

with header_cols[2]:
    if active_version:
        # File extension helper
        ext_map = {"html": "html", "python": "py", "java": "java", "javascript": "js", "c++": "cpp", "go": "go", "rust": "rs"}
        ext = ext_map.get(current_project["language"], "txt")
        filename = f"{current_project['name'].lower().replace(' ', '_')}_v{active_version['version_number']}.{ext}"
        st.download_button(
            label="💾 Download",
            data=active_version["code"],
            file_name=filename,
            mime="text/plain",
            use_container_width=True
        )

with header_cols[3]:
    if active_version and current_project["language"] not in ("html", "web"):
        if st.button("▶️ Run Code", type="primary", use_container_width=True):
            with st.spinner(f"Running {current_project['language'].upper()}..."):
                res = runner.execute_code(current_project["language"], active_version["code"])
                st.session_state.terminal_result = res
                st.rerun()

# Banner Alert if a Refinement was just applied
if st.session_state.refinement_notice:
    notice = st.session_state.refinement_notice
    with st.container():
        st.markdown(f"""
        <div style="background-color: #064e3b; border: 1px solid #059669; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <h4 style="color: #6ee7b7; margin: 0 0 0.5rem 0;">✨ Version {notice['to_v']} Successfully Created from v{notice['from_v']}!</h4>
            <p style="color: #d1fae5; margin: 0 0 0.5rem 0;"><b>Change Request:</b> <i>"{notice['prompt']}"</i></p>
            <span class="badge badge-success">+{notice['added']} lines added</span>
            <span class="badge" style="background-color: #dc2626;">-{notice['removed']} lines removed</span>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("🔍 View Change Diff (What Changed)", expanded=True):
            if notice["diff"].strip():
                st.code(notice["diff"], language="diff")
            else:
                st.info("No code text differences detected.")
        if st.button("✕ Dismiss Notification", key="dismiss_banner"):
            st.session_state.refinement_notice = None
            st.rerun()

st.divider()

# View: Initial Generation Prompt if no versions exist
if not active_version:
    st.markdown("### 💡 **Generate Initial Code**")
    st.write(f"Describe what you want to build in **{current_project['language'].upper()}**:")

    # Starter inspiration chips
    sample_prompts = {
        "html": [
            "Modern Loan & Mortgage Calculator with interactive sliders and monthly breakdown chart",
            "Interactive Kanban Board with drag-and-drop tasks, color tags, and dark mode",
            "Crypto Price Tracker dashboard with simulated live charts and buy/sell modal"
        ],
        "python": [
            "CLI Password Manager simulation with AES encryption, password generator, and strength meter",
            "Data Analysis script generating synthetic sales data, summaries, and ASCII charts",
            "A* Pathfinding algorithm on a 20x20 grid with step-by-step console visualization"
        ],
        "java": [
            "Complete Binary Search Tree implementation with insert, delete, and in-order/pre-order traversals",
            "Bank Account Simulator with multi-threaded deposits, withdrawals, and transaction audit log",
            "LRU Cache implementation with generic keys/values and benchmark demonstration"
        ],
        "javascript": [
            "Event-driven Pub/Sub message broker system with subscriber filtering and metrics",
            "Rate-limiting Token Bucket algorithm demonstration with simulated burst traffic"
        ]
    }
    
    current_samples = sample_prompts.get(current_project["language"], sample_prompts["html"])
    st.caption("Or pick a template:")
    selected_sample = None
    cols = st.columns(len(current_samples))
    for i, s_prompt in enumerate(current_samples):
        if cols[i].button(s_prompt[:45] + "...", key=f"chip_{i}", use_container_width=True):
            selected_sample = s_prompt

    initial_prompt = st.text_area(
        "Prompt",
        value=selected_sample if selected_sample else "",
        placeholder="e.g. Build an interactive loan calculator with responsive dark theme...",
        height=140
    )

    if st.button("🚀 Generate Code with AI", type="primary", use_container_width=True):
        if initial_prompt.strip():
            with st.spinner(f"Generating {current_project['language'].upper()} code with Groq ({selected_model})..."):
                try:
                    res = generator.generate_code(initial_prompt, current_project["language"], model=selected_model)
                    new_code = res["code"]
                    # If non-web, run immediately to populate output
                    init_output = ""
                    if current_project["language"] not in ("html", "web"):
                        exec_res = runner.execute_code(current_project["language"], new_code)
                        st.session_state.terminal_result = exec_res
                        init_output = exec_res.get("stdout", "") or exec_res.get("stderr", "")
                    
                    new_row_id = db.add_version(
                        current_project["id"],
                        initial_prompt,
                        new_code,
                        current_project["language"],
                        output=init_output
                    )
                    st.session_state.selected_version_id = new_row_id
                    st.success(f"Version 1 generated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Generation error: {str(e)}")
        else:
            st.warning("Please enter a prompt first.")
    st.stop()

# Existing Project with active version: 4 Tabs (Live Preview/Console, Code View, AI Iteration, Diff Viewer)
tab_preview, tab_code, tab_refine, tab_diff = st.tabs([
    "🖥️ **Live Execution & Preview**",
    "📝 **Code Inspector**",
    "💬 **Iterative AI Refinement**",
    "🔍 **Version Diff & History**"
])

# TAB 1: PREVIEW / CONSOLE
with tab_preview:
    if current_project["language"] in ("html", "web"):
        st.markdown(f"#### 🌐 **Live Web Preview** (Sandboxed Browser — v{active_version['version_number']})")
        components.html(
            active_version["code"],
            height=680,
            scrolling=True,
            key=f"html_iframe_v_{active_version['id']}_{len(active_version['code'])}"
        )
    else:
        st.markdown(f"#### 💻 **Terminal Output** ({current_project['language'].upper()} — v{active_version['version_number']})")
        
        # Banner & Convert to Web UI Action
        col_mode_msg, col_mode_btn = st.columns([2.8, 1.2])
        with col_mode_msg:
            st.warning("⚠️ **Mode: Python Terminal / Console**. The box below shows terminal text output. Want a visual clickable UI with buttons & styling?")
        with col_mode_btn:
            if st.button("🌐 Convert to Visual Web UI", type="primary", use_container_width=True):
                with st.status("🔄 Generating interactive Web UI with Tailwind CSS...", expanded=True) as status:
                    status.write("🧠 Synthesizing full interactive HTML/Tailwind/JS web app...")
                    convert_prompt = f"Convert this {current_project['name']} program into a modern, complete, interactive visual Web App with Tailwind CSS, input controls, buttons, dark mode, and real-time results:\n\n{active_version['code']}"
                    res = generator.generate_code(convert_prompt, "html", model=selected_model)
                    status.write("💾 Updating project mode to HTML and saving snapshot...")
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
                    status.update(label="✅ Converted to Visual Web App!", state="complete")
                    st.toast("✅ Converted to Visual Web App!")
                    st.rerun()
        
        # Stdin input expander
        with st.expander("⌨️ Optional Program Input (stdin)", expanded=False):
            stdin_input = st.text_area("Input to feed to program", height=80)
            if st.button("Run with this Input"):
                with st.spinner("Executing..."):
                    res = runner.execute_code(current_project["language"], active_version["code"], stdin=stdin_input)
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
                with st.spinner("Running initial execution..."):
                    term_res = runner.execute_code(current_project["language"], active_version["code"])
                    st.session_state[f"term_res_{active_version['id']}"] = term_res

        engine_name = term_res.get("engine", "Executor")
        exit_code = term_res.get("exit_code", 0)
        status_label = "🟢 SUCCESS" if term_res.get("success") else "🔴 FAILED"
        
        st.caption(f"Status: **{status_label}** (Exit Code: {exit_code}) | Engine: `{engine_name}`")
        
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
            output_display = "[Program executed with no console output]"
            
        st.markdown(f"<div class='terminal-box'>{output_display}</div>", unsafe_allow_html=True)

# TAB 2: CODE INSPECTOR
with tab_code:
    col_code_top1, col_code_top2 = st.columns([3, 1])
    with col_code_top1:
        st.markdown(f"#### 📄 **Source Code** ({current_project['language'].upper()})")
    with col_code_top2:
        st.caption(f"Lines: {len(active_version['code'].splitlines())} | Chars: {len(active_version['code'])}")
        
    syntax_lang = "html" if current_project["language"] in ("html", "web") else current_project["language"]
    st.code(active_version["code"], language=syntax_lang, line_numbers=True)

# TAB 3: ITERATIVE AI REFINEMENT
with tab_refine:
    st.markdown("#### 💬 **Iterate & Modify with AI**")
    st.markdown("Ask the LLM to make changes, add features, refactor, or fix bugs. Each modification creates a new tracked version snapshot.")
    
    # Prompt used for current active version
    with st.expander(f"ℹ️ Original Prompt for active snapshot (v{active_version['version_number']})", expanded=False):
        st.info(active_version["prompt"])
        
    quick_mods = [
        "Add a dark mode toggle and improve color scheme",
        "Add unit test cases to verify edge cases",
        "Add error handling and input validation",
        "Make design responsive with mobile drawer"
    ]
    st.caption("Quick modification suggestions:")
    mod_cols = st.columns(len(quick_mods))
    chosen_mod = None
    for i, qm in enumerate(quick_mods):
        if mod_cols[i].button(qm, key=f"mod_chip_{i}", use_container_width=True):
            chosen_mod = qm
            
    refine_prompt = st.text_area(
        "What changes would you like to make?",
        value=chosen_mod if chosen_mod else "",
        placeholder="e.g. Add a search filter box and make the buttons rounded with hover animations...",
        height=120
    )
    
    if st.button("🚀 Apply Modifications (Create Next Version)", type="primary", use_container_width=True):
        if refine_prompt.strip():
            with st.status("🔄 Synthesizing refinements with AI...", expanded=True) as status:
                try:
                    status.write(f"🧠 Querying Groq ({selected_model}) with current code and instructions...")
                    res = generator.refine_code(
                        existing_code=active_version["code"],
                        modification_prompt=refine_prompt,
                        language=current_project["language"],
                        model=selected_model
                    )
                    updated_code = res["code"]
                    
                    status.write("⚡ Computing line-by-line differences...")
                    diff_text, added, removed = compute_diff(
                        active_version["code"],
                        updated_code,
                        old_label=f"v{active_version['version_number']}",
                        new_label=f"v{active_version['version_number'] + 1}"
                    )
                    
                    new_output = ""
                    if current_project["language"] not in ("html", "web"):
                        status.write(f"▶️ Executing updated {current_project['language'].upper()} code...")
                        exec_res = runner.execute_code(current_project["language"], updated_code)
                        st.session_state.terminal_result = exec_res
                        new_output = exec_res.get("stdout", "") or exec_res.get("stderr", "")
                    
                    status.write("💾 Storing new snapshot in SQLite database...")
                    new_ver_id = db.add_version(
                        current_project["id"],
                        refine_prompt,
                        updated_code,
                        current_project["language"],
                        output=new_output
                    )
                    
                    # Fetch exact version number
                    all_vers = db.get_versions(current_project["id"])
                    new_ver_obj = next((v for v in all_vers if v["id"] == new_ver_id), None)
                    new_ver_num = new_ver_obj["version_number"] if new_ver_obj else active_version["version_number"] + 1

                    # Store notice so the user gets immediate visual feedback after rerun
                    st.session_state["refinement_notice"] = {
                        "from_v": active_version["version_number"],
                        "to_v": new_ver_num,
                        "prompt": refine_prompt,
                        "added": added,
                        "removed": removed,
                        "diff": diff_text
                    }
                    # Activate the newly created version immediately!
                    st.session_state.selected_version_id = new_ver_id
                    
                    status.update(label=f"✅ Version {new_ver_num} Created! (+{added}/-{removed} lines)", state="complete")
                    st.toast(f"✅ Version {new_ver_num} Created! (+{added}/-{removed} lines)")
                    st.rerun()
                except Exception as e:
                    status.update(label="❌ Refinement failed", state="error")
                    st.error(f"Refinement error: {str(e)}")
        else:
            st.warning("Please describe what changes you want to apply.")

    # Show history of all prompts applied in this project
    if len(versions) > 1:
        st.divider()
        st.markdown("#### 📜 **Refinement History in this Project**")
        for v in reversed(versions):
            st.markdown(f"**v{v['version_number']}** ({v['created_at'].split()[1][:5]}): *{v['prompt']}*")

# TAB 4: VERSION DIFF & COMPARISON
with tab_diff:
    st.markdown("#### 🔍 **Version Diff Inspector**")
    st.markdown("Compare code differences between any two snapshots of this project.")
    
    if len(versions) < 2:
        st.info("Only 1 version exists so far. Apply a refinement in the **'Iterative AI Refinement'** tab to generate a new version and compare changes!")
    else:
        diff_col1, diff_col2 = st.columns(2)
        with diff_col1:
            base_v_num = st.selectbox(
                "Base Version (Old)",
                options=[v["version_number"] for v in versions],
                index=max(0, len(versions) - 2),
                format_func=lambda x: f"Version {x}"
            )
        with diff_col2:
            target_v_num = st.selectbox(
                "Compare With (New)",
                options=[v["version_number"] for v in versions],
                index=len(versions) - 1,
                format_func=lambda x: f"Version {x}"
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
        stat_col1.metric("Lines Added (+)", f"+{lines_added}")
        stat_col2.metric("Lines Removed (-)", f"-{lines_removed}")
        stat_col3.metric("Net Change", f"{lines_added - lines_removed:+d}")
        
        st.caption(f"**Base Prompt (v{base_v_num}):** {base_v['prompt']}")
        st.caption(f"**Target Prompt (v{target_v_num}):** {target_v['prompt']}")
        
        st.divider()
        if diff_text.strip():
            st.markdown("##### 📄 **Unified Code Diff** (Green: Added | Red: Removed)")
            st.code(diff_text, language="diff")
        else:
            st.info("The code in both selected versions is identical.")

