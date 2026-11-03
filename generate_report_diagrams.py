"""Generate high-resolution academic diagrams and visual figures for CodeStudio Project Report."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs('report_assets', exist_ok=True)

# ----------------- FIGURE 3.1: ARCHITECTURE DIAGRAM -----------------
def create_architecture_diagram():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Background
    fig.patch.set_facecolor('#FFFFFF')

    # Title
    ax.text(50, 96, "CodeStudio: End-to-End System Architecture", 
            ha='center', va='center', fontsize=14, fontweight='bold', color='#0F172A', fontfamily='sans-serif')

    # Tier 1: Presentation
    t1 = patches.FancyBboxPatch((5, 78), 90, 14, boxstyle="round,pad=1", ec="#3B82F6", fc="#EFF6FF", lw=1.5)
    ax.add_patch(t1)
    ax.text(7, 89, "TIER 1: PRESENTATION & USER INTERACTION (Streamlit Reactive Shell)", fontsize=10, fontweight='bold', color='#1E40AF')
    ax.text(10, 82, "[Tab 1: Preview & Console]   [Tab 2: Code Inspector]   [Tab 3: AI Refinement]   [Tab 4: Snapshot Diff Comparator]", 
            fontsize=9, color='#1E293B')

    # Arrow 1->2
    ax.annotate('', xy=(50, 71), xytext=(50, 78), arrowprops=dict(arrowstyle="->", color="#64748B", lw=2))

    # Tier 2: Orchestration & Inference
    t2 = patches.FancyBboxPatch((5, 50), 90, 20, boxstyle="round,pad=1", ec="#8B5CF6", fc="#F5F3FF", lw=1.5)
    ax.add_patch(t2)
    ax.text(7, 67, "TIER 2: ORCHESTRATION & INFERENCE ENGINE (generator.py)", fontsize=10, fontweight='bold', color='#5B21B6')
    ax.text(8, 60, "• Strict Zero-Shot Polyglot System Prompts (HTML, Python, Java, C++, JS, Go, Rust)\n• Low-Latency Tensor Streaming Inference Engine (Max Tokens: 8,192)\n• Compile-Time Self-Healing Engine: fix_code(broken_source, compiler_traceback, T=0.1)", 
            fontsize=8.5, color='#334155', linespacing=1.4)

    # Arrows 2->3 and 2->4
    ax.annotate('', xy=(28, 43), xytext=(28, 50), arrowprops=dict(arrowstyle="->", color="#64748B", lw=2))
    ax.annotate('', xy=(72, 43), xytext=(72, 50), arrowprops=dict(arrowstyle="->", color="#64748B", lw=2))

    # Tier 3: Hybrid Execution Sandboxing
    t3 = patches.FancyBboxPatch((5, 12), 43, 30, boxstyle="round,pad=1", ec="#10B981", fc="#ECFDF5", lw=1.5)
    ax.add_patch(t3)
    ax.text(7, 39, "TIER 3: HYBRID EXECUTION SANDBOX", fontsize=9.5, fontweight='bold', color='#065F46')
    ax.text(7, 33, "1. Browser DOM Sandbox\n   - Isolated iframe (HTML5/Tailwind/JS)\n2. Local Subprocess Sandbox (8s Timeout)\n   - Python 3.12 & Node.js Engine\n3. Containerized Cloud Sandbox (25s Timeout)\n   - Wandbox GCC-head, OpenJDK 22, Rustc, Go", 
            fontsize=8, color='#1E293B', linespacing=1.35)

    # Tier 4: Relational SQLite Vault
    t4 = patches.FancyBboxPatch((52, 12), 43, 30, boxstyle="round,pad=1", ec="#F59E0B", fc="#FFFBEB", lw=1.5)
    ax.add_patch(t4)
    ax.text(54, 39, "TIER 4: RELATIONAL SNAPSHOT VAULT", fontsize=9.5, fontweight='bold', color='#92400E')
    ax.text(54, 33, "• SQLite3 Embedded Database (studio.db)\n• WAL Journal Mode (Zero Read-Lock Contention)\n• projects table: Vault metadata & active mode\n• versions table: Immutable source snapshots\n• difflib Syntactic Diffing (+Added, -Removed lines)", 
            fontsize=8, color='#1E293B', linespacing=1.35)

    # Feedback loop arrow (Tier 3 -> Tier 2 Self-Healing)
    ax.annotate('Compiler Error / Stderr Feedback', xy=(48, 57), xytext=(28, 43),
                arrowprops=dict(arrowstyle="->", color="#EF4444", lw=1.8, linestyle="dashed"),
                fontsize=7.5, fontweight='bold', color='#B91C1C')

    plt.tight_layout()
    plt.savefig('report_assets/fig_3_1_architecture.png', bbox_inches='tight')
    plt.close()
    print("Created fig_3_1_architecture.png")

# ----------------- FIGURE 3.2: DFD LEVEL 0 -----------------
def create_dfd0():
    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    ax.text(50, 94, "Figure 3.2: Data Flow Diagram Level 0 (Context Diagram)", 
            ha='center', va='center', fontsize=12, fontweight='bold', color='#0F172A')

    # External Entity 1: User
    e1 = patches.Rectangle((4, 35), 20, 30, ec="#1E293B", fc="#F1F5F9", lw=1.5)
    ax.add_patch(e1)
    ax.text(14, 50, "Developer /\nUser", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#0F172A')

    # Central Process: CodeStudio
    p0 = patches.Circle((50, 50), 18, ec="#3B82F6", fc="#EFF6FF", lw=2)
    ax.add_patch(p0)
    ax.text(50, 50, "0.0\nCodeStudio\nAutonomous\nIDE System", ha='center', va='center', fontsize=9, fontweight='bold', color='#1D4ED8')

    # External Entity 2: Remote Compilers
    e2 = patches.Rectangle((76, 55), 20, 26, ec="#1E293B", fc="#F1F5F9", lw=1.5)
    ax.add_patch(e2)
    ax.text(86, 68, "Remote Compiler\nSandboxes\n(Wandbox REST)", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#0F172A')

    # External Entity 3: Local SQLite Store
    e3 = patches.Rectangle((76, 18), 20, 26, ec="#1E293B", fc="#F1F5F9", lw=1.5)
    ax.add_patch(e3)
    ax.text(86, 31, "Relational Vault\n(SQLite3\nstudio.db)", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#0F172A')

    # Flows User <-> CodeStudio
    ax.annotate('Prompt Directives & Commands', xy=(32, 54), xytext=(24, 54), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=1.5), fontsize=7.5)
    ax.annotate('DOM Previews, Telemetry & Diffs', xy=(24, 46), xytext=(32, 46), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=1.5), fontsize=7.5)

    # Flows CodeStudio <-> Wandbox
    ax.annotate('Source Payload', xy=(76, 72), xytext=(66, 60), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=1.5), fontsize=7.5)
    ax.annotate('Stdout / Stderr / Exit Code', xy=(66, 55), xytext=(76, 63), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=1.5), fontsize=7.5)

    # Flows CodeStudio <-> SQLite
    ax.annotate('Snapshots & Diffs', xy=(76, 33), xytext=(66, 42), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=1.5), fontsize=7.5)
    ax.annotate('Historical Versions', xy=(66, 38), xytext=(76, 27), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=1.5), fontsize=7.5)

    plt.tight_layout()
    plt.savefig('report_assets/fig_3_2_dfd0.png', bbox_inches='tight')
    plt.close()
    print("Created fig_3_2_dfd0.png")

# ----------------- FIGURE 3.3: DFD LEVEL 1 -----------------
def create_dfd1():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    ax.text(50, 96, "Figure 3.3: Data Flow Diagram Level 1 (Modular Process Flow)", 
            ha='center', va='center', fontsize=12, fontweight='bold', color='#0F172A')

    # Process 1.0: Vault Management
    p1 = patches.FancyBboxPatch((5, 68), 24, 18, boxstyle="round,pad=0.5", ec="#2563EB", fc="#EFF6FF", lw=1.5)
    ax.add_patch(p1)
    ax.text(17, 77, "1.0 Vault & Mode\nManagement", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1E40AF')

    # Data Store D1: projects table
    ds1 = patches.Rectangle((36, 72), 22, 10, ec="#B45309", fc="#FEF3C7", lw=1.2)
    ax.add_patch(ds1)
    ax.text(47, 77, "D1: projects Table", ha='center', va='center', fontsize=8, fontweight='bold', color='#92400E')

    # Process 2.0: Prompt Synthesis
    p2 = patches.FancyBboxPatch((5, 38), 24, 18, boxstyle="round,pad=0.5", ec="#7C3AED", fc="#F5F3FF", lw=1.5)
    ax.add_patch(p2)
    ax.text(17, 47, "2.0 Prompt-to-Code\nSynthesis Engine", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#5B21B6')

    # Process 3.0: Hybrid Execution
    p3 = patches.FancyBboxPatch((40, 38), 24, 18, boxstyle="round,pad=0.5", ec="#059669", fc="#ECFDF5", lw=1.5)
    ax.add_patch(p3)
    ax.text(52, 47, "3.0 Hybrid Sandboxed\nExecution", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#065F46')

    # Process 4.0: Self-Healing Diagnostician
    p4 = patches.FancyBboxPatch((40, 8), 24, 18, boxstyle="round,pad=0.5", ec="#DC2626", fc="#FEF2F2", lw=1.5)
    ax.add_patch(p4)
    ax.text(52, 17, "4.0 Compile-Time\nSelf-Healing Loop", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#991B1B')

    # Process 5.0: Diffing & Archival
    p5 = patches.FancyBboxPatch((72, 38), 24, 18, boxstyle="round,pad=0.5", ec="#D97706", fc="#FFFBEB", lw=1.5)
    ax.add_patch(p5)
    ax.text(84, 47, "5.0 Version Diffing\n& Vault Archival", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#92400E')

    # Data Store D2: versions table
    ds2 = patches.Rectangle((72, 72), 24, 10, ec="#B45309", fc="#FEF3C7", lw=1.2)
    ax.add_patch(ds2)
    ax.text(84, 77, "D2: versions Table", ha='center', va='center', fontsize=8, fontweight='bold', color='#92400E')

    # Connectors
    ax.annotate('', xy=(36, 77), xytext=(29, 77), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.5))
    ax.annotate('', xy=(17, 56), xytext=(17, 68), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.5))
    ax.annotate('', xy=(40, 47), xytext=(29, 47), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.5))
    ax.annotate('', xy=(72, 47), xytext=(64, 47), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.5))
    ax.annotate('', xy=(84, 72), xytext=(84, 56), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.5))

    # Error feedback
    ax.annotate('Compiler Stderr', xy=(52, 26), xytext=(52, 38), arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.5), fontsize=7.5, color="#B91C1C")
    ax.annotate('Patched Code', xy=(40, 42), xytext=(40, 22), arrowprops=dict(arrowstyle="->", color="#16A34A", lw=1.5), fontsize=7.5, color="#15803D")

    plt.tight_layout()
    plt.savefig('report_assets/fig_3_3_dfd1.png', bbox_inches='tight')
    plt.close()
    print("Created fig_3_3_dfd1.png")

# ----------------- FIGURE 3.4: SEQUENCE DIAGRAM -----------------
def create_sequence_diagram():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    ax.text(50, 96, "Figure 3.4: Module Interaction Sequence Diagram (Runtime Flow)", 
            ha='center', va='center', fontsize=12, fontweight='bold', color='#0F172A')

    actors = ["Developer", "app.py (UI)", "generator.py", "runner.py", "SQLite (db.py)"]
    xs = [10, 30, 50, 70, 90]

    for i, a in enumerate(actors):
        # Header box
        box = patches.FancyBboxPatch((xs[i]-8, 86), 16, 6, boxstyle="round,pad=0.3", ec="#334155", fc="#F8FAFC", lw=1.2)
        ax.add_patch(box)
        ax.text(xs[i], 89, a, ha='center', va='center', fontsize=8, fontweight='bold', color='#0F172A')
        # Lifeline
        ax.plot([xs[i], xs[i]], [12, 86], color="#94A3B8", linestyle="--", lw=1)

    # Sequence steps
    steps = [
        (1, 10, 30, 80, "1: Enter prompt specification"),
        (2, 30, 50, 72, "2: generate_code(prompt, lang)"),
        (3, 50, 50, 65, "3: Query LPU with polyglot prompt"),
        (4, 50, 30, 58, "4: Return clean code"),
        (5, 30, 70, 50, "5: execute_code(lang, code)"),
        (6, 70, 30, 42, "6: Return compiler error (exit != 0)"),
        (7, 30, 50, 34, "7: fix_code(broken_code, stderr)"),
        (8, 50, 30, 27, "8: Return healed code patch"),
        (9, 30, 70, 21, "9: Re-execute & verify (exit == 0)"),
        (10, 30, 90, 14, "10: add_version(healed_code)")
    ]

    for s_num, x1, x2, y, label in steps:
        if x1 == x2: # self call
            ax.annotate('', xy=(x1+3, y-2), xytext=(x1, y), arrowprops=dict(arrowstyle="->", color="#2563EB", lw=1.2))
            ax.text(x1+4, y-1, label, fontsize=7.5, color='#1E40AF')
        else:
            col = "#DC2626" if s_num in [6, 7] else ("#16A34A" if s_num in [8, 9] else "#2563EB")
            ax.annotate('', xy=(x2, y), xytext=(x1, y), arrowprops=dict(arrowstyle="->", color=col, lw=1.3))
            ax.text((x1+x2)/2, y+1.5, label, ha='center', va='bottom', fontsize=7.5, fontweight='bold' if s_num in [6,7,8] else 'normal', color=col)

    plt.tight_layout()
    plt.savefig('report_assets/fig_3_4_sequence.png', bbox_inches='tight')
    plt.close()
    print("Created fig_3_4_sequence.png")

# ----------------- FIGURE 4.1: UI LANDING MOCKUP -----------------
def create_ui_landing():
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#09090B')

    # Header / Brand bar
    ax.text(5, 93, "●  CODESTUDIO", fontsize=11, fontweight='bold', color='#FAFAFA', fontfamily='monospace')
    ax.text(26, 93, "AUTONOMOUS POLYGLOT STUDIO // v1.0", fontsize=8, color='#E11D48', fontfamily='monospace')

    # Sidebar
    sb = patches.Rectangle((3, 5), 24, 82, ec="#27272A", fc="#111114", lw=1)
    ax.add_patch(sb)
    ax.text(5, 82, "SAVED VAULTS", fontsize=7.5, fontweight='bold', color='#71717A', fontfamily='monospace')
    ax.text(5, 76, "• Stock Tracker (HTML) · v2", fontsize=7.5, color='#E4E4E7')
    ax.text(5, 71, "• Fibonacci WAL (PYTHON) · v5", fontsize=7.5, color='#E4E4E7')
    ax.text(5, 66, "• Red-Black Tree (C++) · v3", fontsize=7.5, color='#E4E4E7')
    ax.text(5, 58, "SNAPSHOT TIMELINE", fontsize=7.5, fontweight='bold', color='#71717A', fontfamily='monospace')
    ax.text(5, 52, "▶ v5 [PYTHON] (WAL Log)", fontsize=7.5, color='#E11D48', fontweight='bold')
    ax.text(5, 47, "  v4 [PYTHON] (AES Encrypt)", fontsize=7.5, color='#A1A1AA')
    ax.text(5, 42, "  v1 [PYTHON] (Init Engine)", fontsize=7.5, color='#A1A1AA')

    # Main Area: Landing Cards
    ax.text(32, 82, "Build software from pure intent.", fontsize=15, fontweight='bold', color='#FAFAFA')
    ax.text(32, 76, "Turn natural language briefs into self-contained web apps and verified polyglot algorithms.", fontsize=8.5, color='#A1A1AA')

    # 3 Cards
    c1 = patches.Rectangle((32, 42), 19, 28, ec="#27272A", fc="#141416", lw=1)
    c2 = patches.Rectangle((53, 42), 19, 28, ec="#27272A", fc="#141416", lw=1)
    c3 = patches.Rectangle((74, 42), 19, 28, ec="#27272A", fc="#141416", lw=1)
    ax.add_patch(c1); ax.add_patch(c2); ax.add_patch(c3)

    ax.text(34, 64, "SANDBOX // 01", fontsize=7, color='#E11D48', fontfamily='monospace')
    ax.text(34, 58, "Live Web Studio", fontsize=9.5, fontweight='bold', color='#FAFAFA')
    ax.text(34, 48, "Single-file HTML5 +\nTailwind CSS + JS in\nreactive DOM iframe.", fontsize=7.5, color='#A1A1AA')

    ax.text(55, 64, "RUNNER // 02", fontsize=7, color='#E11D48', fontfamily='monospace')
    ax.text(55, 58, "Polyglot Engine", fontsize=9.5, fontweight='bold', color='#FAFAFA')
    ax.text(55, 48, "Compiles Python 3.12,\nJava 22, C++17, Rust,\nand Go with live stdout.", fontsize=7.5, color='#A1A1AA')

    ax.text(76, 64, "HEALING // 03", fontsize=7, color='#E11D48', fontfamily='monospace')
    ax.text(76, 58, "Self-Healing Diff", fontsize=9.5, fontweight='bold', color='#FAFAFA')
    ax.text(76, 48, "Automatic compiler\nerror repair loop with\nunified line diffs.", fontsize=7.5, color='#A1A1AA')

    # Prompt box
    p_box = patches.Rectangle((32, 14), 61, 22, ec="#27272A", fc="#111114", lw=1)
    ax.add_patch(p_box)
    ax.text(34, 29, "Describe the specification for your program:", fontsize=8, color='#71717A')
    ax.text(34, 21, "e.g. CLI Key-Value Store with WAL log, AES encryption, and micro-benchmarks...", fontsize=8, color='#A1A1AA', fontfamily='monospace')

    btn = patches.Rectangle((73, 16), 18, 7, ec="#E11D48", fc="#E11D48")
    ax.add_patch(btn)
    ax.text(82, 19.5, "Synthesize with AI", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#FFFFFF')

    plt.tight_layout()
    plt.savefig('report_assets/fig_4_1_ui_landing.png', bbox_inches='tight')
    plt.close()
    print("Created fig_4_1_ui_landing.png")

# ----------------- FIGURE 4.2: TERMINAL RUNNER MOCKUP -----------------
def create_ui_terminal():
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#09090B')

    # Header Bar
    ax.text(5, 93, "Stock Portfolio Engine", fontsize=11, fontweight='bold', color='#FAFAFA')
    badge1 = patches.Rectangle((32, 90), 12, 6, ec="#E11D48", fc="#271015")
    ax.add_patch(badge1)
    ax.text(38, 93, "PYTHON", ha='center', va='center', fontsize=7, fontweight='bold', color='#E11D48', fontfamily='monospace')
    badge2 = patches.Rectangle((46, 90), 8, 6, ec="#27272A", fc="#18181B")
    ax.add_patch(badge2)
    ax.text(50, 93, "v3", ha='center', va='center', fontsize=7, color='#A1A1AA', fontfamily='monospace')

    # Tabs
    ax.text(5, 83, "[ Preview & Runtime ]", fontsize=8.5, fontweight='bold', color='#FAFAFA')
    ax.text(28, 83, "Code Inspector", fontsize=8.5, color='#71717A')
    ax.text(45, 83, "Iterative Refinement", fontsize=8.5, color='#71717A')
    ax.text(68, 83, "Version Diff", fontsize=8.5, color='#71717A')

    # Terminal Window Container
    term_box = patches.Rectangle((5, 10), 90, 68, ec="#27272A", fc="#050507", lw=1.2)
    ax.add_patch(term_box)

    # Window bar
    t_bar = patches.Rectangle((5, 71), 90, 7, ec="#27272A", fc="#111114")
    ax.add_patch(t_bar)
    # macOS dots
    dot1 = patches.Circle((7.5, 74.5), 1.2, fc="#EF4444")
    dot2 = patches.Circle((10.5, 74.5), 1.2, fc="#F59E0B")
    dot3 = patches.Circle((13.5, 74.5), 1.2, fc="#10B981")
    ax.add_patch(dot1); ax.add_patch(dot2); ax.add_patch(dot3)

    ax.text(50, 74.5, "PROCESS // Local Python 3.12 Engine", ha='center', va='center', fontsize=7.5, color='#A1A1AA', fontfamily='monospace')
    ax.text(88, 74.5, "● SUCCESS (EXIT 0)", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#34D399', fontfamily='monospace')

    # Terminal output text
    output = """=== STOCK PORTFOLIO VALUATION ENGINE (v3) ===
[INIT] Loading real-time synthetic ticker stream...
[DATA] AAPL: $182.45 (+1.2%) | TSLA: $214.10 (-0.8%) | NVDA: $890.15 (+3.4%)
[EXEC] Running Black-Scholes volatility simulation (N=10,000 paths)...
--------------------------------------------------------------------------------
PORTFOLIO SUMMARY:
  Total Assets Value:    $1,248,500.00
  Daily Net Yield:       +$14,230.50 (+1.15%)
  95% Value-at-Risk:     -$8,450.00 (Safe bound)
[BENCH] Execution latency: 42.8ms | Memory footprint: 14.2 MB
--------------------------------------------------------------------------------
[PROCESS COMPLETED WITH EXIT STATUS 0]"""
    ax.text(7, 65, output, fontsize=8, color='#E4E4E7', fontfamily='monospace', va='top', linespacing=1.35)

    plt.tight_layout()
    plt.savefig('report_assets/fig_4_2_terminal_run.png', bbox_inches='tight')
    plt.close()
    print("Created fig_4_2_terminal_run.png")

# ----------------- FIGURE 4.3: SELF-HEALING & DIFF MOCKUP -----------------
def create_ui_self_healing():
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#09090B')

    ax.text(5, 93, "Red-Black Tree Visualizer", fontsize=11, fontweight='bold', color='#FAFAFA')
    ax.text(35, 93, "AUTONOMOUS SELF-HEALING ENGINE", fontsize=7.5, color='#E11D48', fontfamily='monospace')

    # Notification Banner
    ban = patches.Rectangle((5, 74), 90, 15, ec="#1A3D2E", fc="#0E1613", lw=1.2)
    ax.add_patch(ban)
    ax.text(7, 84, "● Snapshot v4 Deployed (Auto-Healed from v3)", fontsize=9, fontweight='bold', color='#6EE7B7')
    ax.text(7, 78, "Diagnosed compilation fault: 'cout undeclared; missing <iostream>'. Auto-healed and re-verified.", fontsize=8, color='#D1FAE5')
    badge_add = patches.Rectangle((75, 78), 9, 7, ec="#10B981", fc="#064E3B")
    ax.add_patch(badge_add)
    ax.text(79.5, 81.5, "+4 lines", ha='center', va='center', fontsize=7, color='#A7F3D0', fontfamily='monospace')
    badge_rem = patches.Rectangle((85, 78), 9, 7, ec="#EF4444", fc="#7F1D1D")
    ax.add_patch(badge_rem)
    ax.text(89.5, 81.5, "-1 lines", ha='center', va='center', fontsize=7, color='#FECACA', fontfamily='monospace')

    # Unified Diff Box
    diff_box = patches.Rectangle((5, 10), 90, 60, ec="#27272A", fc="#111114", lw=1)
    ax.add_patch(diff_box)
    ax.text(7, 65, "UNIFIED CODE DELTA // difflib engine (v3 -> v4)", fontsize=8, fontweight='bold', color='#A1A1AA', fontfamily='monospace')

    diff_lines = [
        ("--- v3 (Broken)", '#A1A1AA'),
        ("+++ v4 (Auto-Healed)", '#A1A1AA'),
        ("@@ -1,6 +1,9 @@", '#818CF8'),
        ("-#include <vector>", '#F87171'),
        ("+#include <iostream>", '#34D399'),
        ("+#include <vector>", '#34D399'),
        ("+#include <memory>", '#34D399'),
        (" namespace rbtree {", '#E4E4E7'),
        ("     template<typename T>", '#E4E4E7'),
        ("     void printNode(const T& val) {", '#E4E4E7'),
        ("-        cout << val << endl;  // Error: undeclared", '#F87171'),
        ("+        std::cout << val << std::endl;  // Auto-fixed", '#34D399'),
        ("     }", '#E4E4E7')
    ]

    y_pos = 58
    for line, col in diff_lines:
        ax.text(8, y_pos, line, fontsize=8, color=col, fontfamily='monospace')
        y_pos -= 3.6

    plt.tight_layout()
    plt.savefig('report_assets/fig_4_3_self_healing_diff.png', bbox_inches='tight')
    plt.close()
    print("Created fig_4_3_self_healing_diff.png")

if __name__ == "__main__":
    create_architecture_diagram()
    create_dfd0()
    create_dfd1()
    create_sequence_diagram()
    create_ui_landing()
    create_ui_terminal()
    create_ui_self_healing()
    print("All 7 figures generated successfully!")
