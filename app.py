"""Live Interactive Multi-Language Web Component & Code Studio."""
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
            
            # Default to latest version if not set
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
header_cols = st.columns([3, 1, 1])
with header_cols[0]:
    lang_upper = current_project['language'].upper()
    ver_str = f"v{active_version['version_number']}" if active_version else "v0 (Empty)"
    st.markdown(f"## **{current_project['name']}**")
    st.markdown(f"<span class='badge'>{lang_upper}</span> <span class='badge badge-secondary'>{ver_str}</span>", unsafe_allow_html=True)

with header_cols[1]:
    if active_version:
        # File extension helper
        ext_map = {"html": "html", "python": "py", "java": "java", "javascript": "js", "c++": "cpp", "go": "go", "rust": "rs"}
        ext = ext_map.get(current_project["language"], "txt")
        filename = f"{current_project['name'].lower().replace(' ', '_')}_v{active_version['version_number']}.{ext}"
        st.download_button(
            label="💾 Download Code",
            data=active_version["code"],
            file_name=filename,
            mime="text/plain",
            use_container_width=True
        )

with header_cols[2]:
    if active_version and current_project["language"] not in ("html", "web"):
        if st.button("▶️ Run Code", type="primary", use_container_width=True):
            with st.spinner(f"Running {current_project['language'].upper()}..."):
                res = runner.execute_code(current_project["language"], active_version["code"])
                st.session_state.terminal_result = res
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
                    
                    ver_num = db.add_version(
                        current_project["id"],
                        initial_prompt,
                        new_code,
                        current_project["language"],
                        output=init_output
                    )
                    st.session_state.selected_version_id = None
                    st.success(f"Version 1 generated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Generation error: {str(e)}")
        else:
            st.warning("Please enter a prompt first.")
    st.stop()

# Existing Project with active version: 3 Tabs (Live Preview/Console, Code View, AI Iteration)
tab_preview, tab_code, tab_refine = st.tabs([
    "🖥️ **Live Execution & Preview**",
    "📝 **Code Inspector**",
    "💬 **Iterative AI Refinement**"
])

# TAB 1: PREVIEW / CONSOLE
with tab_preview:
    if current_project["language"] in ("html", "web"):
        st.markdown("#### 🌐 **Live Web Preview** (Sandboxed Browser)")
        components.html(active_version["code"], height=680, scrolling=True)
    else:
        st.markdown(f"#### 💻 **Terminal Output** ({current_project['language'].upper()})")
        
        # Stdin input expander
        with st.expander("⌨️ Optional Program Input (stdin)", expanded=False):
            stdin_input = st.text_area("Input to feed to program", height=80)
            if st.button("Run with this Input"):
                with st.spinner("Executing..."):
                    res = runner.execute_code(current_project["language"], active_version["code"], stdin=stdin_input)
                    st.session_state.terminal_result = res
                    st.rerun()

        # Display terminal output
        term_res = st.session_state.terminal_result
        if not term_res:
            # Auto-run once if empty
            with st.spinner("Running initial execution..."):
                term_res = runner.execute_code(current_project["language"], active_version["code"])
                st.session_state.terminal_result = term_res

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
    st.markdown("Ask the LLM to make changes, add features, refactor, or fix bugs. Each change creates a new version.")
    
    # Prompt used for current version
    with st.expander(f"ℹ️ Original Prompt for v{active_version['version_number']}", expanded=False):
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
            with st.spinner(f"Refining code with Groq ({selected_model})..."):
                try:
                    res = generator.refine_code(
                        existing_code=active_version["code"],
                        modification_prompt=refine_prompt,
                        language=current_project["language"],
                        model=selected_model
                    )
                    updated_code = res["code"]
                    
                    # Run if non-web
                    new_output = ""
                    if current_project["language"] not in ("html", "web"):
                        exec_res = runner.execute_code(current_project["language"], updated_code)
                        st.session_state.terminal_result = exec_res
                        new_output = exec_res.get("stdout", "") or exec_res.get("stderr", "")
                    
                    new_ver_num = db.add_version(
                        current_project["id"],
                        refine_prompt,
                        updated_code,
                        current_project["language"],
                        output=new_output
                    )
                    st.session_state.selected_version_id = None
                    st.success(f"Created version {new_ver_num} successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Refinement error: {str(e)}")
        else:
            st.warning("Please describe what changes you want to apply.")
