import gradio as gr
import auth
import database
import workflow
import pdf_generator
import os
import time

# --- 1. LOGIC & AUTH FUNCTIONS ---

def login(username, password):
    if auth.authenticate_user(username, password):
        history = database.get_history(username)
        # Create history list for sidebar
        hist_text = "\n".join([f"📝 {h[0][:15]}..." for h in history]) if history else "No chats yet."
        
        return {
            login_overlay: gr.update(visible=False),
            main_layout: gr.update(visible=True),
            # Update Profile Initial (Top Right)
            profile_html: f"""
                <div class='profile-container'>
                    <span class='profile-badge'>PROFILE</span>
                    <div class='profile-icon'>{username[0].upper()}</div>
                </div>""",
            # Update Hero Text (Center Screen)
            hero_html: f"""
                <div class='hero-container'>
                    <span class='gradient-text'>Hello, {username}</span><br>
                    <span class='hero-subtext'>What would you like to research today?</span>
                </div>""",
            history_list: hist_text,
            current_user_state: username,
            login_error: ""
        }
    else:
        return {login_error: "<p style='color: #ef4444; text-align: center; font-weight: bold;'>❌ Invalid credentials.</p>"}

def register(username, password):
    success, msg = auth.register_user(username, password)
    return msg

def logout():
    return {
        login_overlay: gr.update(visible=True),
        main_layout: gr.update(visible=False),
        current_user_state: ""
    }

def delete_account(username):
    if database.delete_user(username):
        return logout()
    return None

# --- 2. STREAMING AGENT LOGIC ---
def run_agent_stream(topic, user):
    if not topic: 
        yield gr.update(visible=False), None, None, ""
        return

    # PHASE 1: UI TRANSITION (Hide Hero, Show Thinking)
    yield (
        gr.update(visible=False), # Hide Hero Text
        gr.update(visible=False), # Hide Chips
        gr.update(visible=True, value="<div class='status-pill'>🧠 Thinking...</div>"), # Show Status
        None, None, ""
    )
    time.sleep(1.0) 

    # PHASE 2: SEARCHING
    yield (
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(value="<div class='status-pill'>🔎 Searching academic sources...</div>"),
        None, None, ""
    )
    
    # --- CALL BACKEND ---
    try:
        report_text, papers_meta = workflow.run_research(topic)
    except Exception as e:
        yield gr.update(visible=False), gr.update(visible=False), gr.update(value=f"❌ Error: {str(e)}"), None, None, ""
        return

    # PHASE 3: PROCESSING
    yield (
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(value="<div class='status-pill'>✍️ Drafting research report...</div>"),
        None, None, ""
    )
    time.sleep(0.5)

    # PHASE 4: TYPEWRITER STREAMING
    # Prepare metadata HTML first
    meta_html = "<div class='meta-box'><h3>📚 Referenced Sources</h3><table><tr><th>Title</th><th>Year</th></tr>"
    paper_files = []
    for p in papers_meta:
        meta_html += f"<tr><td>{p['title']}</td><td>{p['year']}</td></tr>"
        if os.path.exists(p['path']): paper_files.append(p['path'])
    meta_html += "</table></div>"

    streamed_text = ""
    lines = report_text.split("\n")
    
    for line in lines:
        streamed_text += line + "\n"
        yield (
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(value=streamed_text), 
            None, None, ""
        )
        time.sleep(0.02) # Fast typing effect

    # PHASE 5: FINAL ASSETS
    if user: database.save_research(user, topic, report_text[:200])
    report_pdf_path = pdf_generator.create_pdf(report_text)
    
    yield (
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(value=report_text), 
        report_pdf_path, 
        paper_files, 
        meta_html
    )


# --- 3. PROFESSIONAL CSS STYLING ---
frontend_css = """
/* GLOBAL RESETS */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

.gradio-container { 
    background-color: #0b0f19 !important; 
    font-family: 'Inter', sans-serif !important; 
}
body { background-color: #0b0f19; }

/* TYPOGRAPHY */
h1, h2, h3, p, span, div { color: #e2e8f0 !important; }

/* 1. LOGIN CARD (Centered Glassmorphism) */
.login-card {
    background: rgba(30, 41, 59, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 40px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    text-align: center;
}
/* FIX 1: Custom class for Login Title size override */
.login-title h2 {
    font-size: 32px !important;
    margin-bottom: 10px;
}

/* 2. SIDEBAR (Minimalist) */
.sidebar-col { 
    background-color: #0f172a !important; 
    border-right: 1px solid #1e293b; 
    height: 100vh; 
    padding: 20px;
    display: flex; 
    flex-direction: column;
}
.sidebar-header {
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 30px;
    background: linear-gradient(to right, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
/* FIX 2: Class for Recent Activity Label */
.recent-label p {
    font-size: 12px !important;
    color: #64748b !important;
    margin-top: 30px !important;
    font-weight: bold;
}
/* FIX 3: Class for Sidebar Footer alignment */
.sidebar-footer {
    margin-top: auto;
    width: 100%;
}

.history-item { color: #94a3b8 !important; font-size: 13px; margin-bottom: 8px; }

/* 3. HERO SECTION (Centered) */
.hero-container {
    text-align: center;
    margin-top: 10vh;
    margin-bottom: 40px;
    animation: fadeIn 1s ease-in;
}
.gradient-text {
    font-size: 56px;
    font-weight: 800;
    background: linear-gradient(135deg, #60a5fa, #a855f7, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-subtext {
    font-size: 24px;
    color: #94a3b8 !important;
    font-weight: 300;
}

/* 4. SEARCH PILL (Floating Input) */
.search-pill textarea {
    background-color: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 30px !important;
    color: white !important;
    font-size: 18px !important;
    padding: 18px 25px !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}
.search-pill textarea:focus {
    border-color: #818cf8 !important;
    background-color: #0f172a !important;
    box-shadow: 0 0 0 4px rgba(129, 140, 248, 0.1);
}

/* 5. SUGGESTION CHIPS */
.chip-btn {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
    color: #cbd5e1 !important;
    font-size: 13px !important;
    padding: 8px 16px !important;
    transition: transform 0.2s;
}
.chip-btn:hover { 
    background: #334155 !important; 
    transform: translateY(-2px);
}

/* 6. PROFILE BADGE (Top Right) */
.profile-container {
    display: flex; 
    align-items: center; 
    justify-content: flex-end;
}
.profile-badge {
    background: linear-gradient(135deg, #4f46e5, #9333ea);
    color: white !important;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 800;
    margin-right: 10px;
    letter-spacing: 1px;
}
.profile-icon {
    width: 38px;
    height: 38px;
    background: #334155;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    border: 2px solid #1e293b;
}

/* 7. STATUS & RESULTS */
.status-pill {
    color: #818cf8;
    font-family: monospace;
    font-size: 16px;
    margin-bottom: 20px;
    display: inline-block;
    padding: 5px 15px;
    background: rgba(129, 140, 248, 0.1);
    border-radius: 20px;
    animation: pulse 1.5s infinite;
}
.result-area {
    font-size: 16px;
    line-height: 1.7;
    color: #e2e8f0;
}
.meta-box {
    background: #1e293b;
    padding: 20px;
    border-radius: 12px;
    margin-top: 20px;
    border: 1px solid #334155;
}
.meta-box table { width: 100%; border-collapse: collapse; }
.meta-box th { text-align: left; color: #94a3b8; padding-bottom: 10px; border-bottom: 1px solid #334155; }
.meta-box td { padding: 8px 0; border-bottom: 1px solid #334155; font-size: 14px; }

/* ANIMATIONS */
@keyframes pulse { 0% { opacity: 0.6; } 50% { opacity: 1; } 100% { opacity: 0.6; } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
"""

# Theme Configuration
theme = gr.themes.Soft(
    primary_hue="indigo",
    radius_size="lg",
    font=[gr.themes.GoogleFont("Inter"), "sans-serif"]
).set(
    body_background_fill="#0b0f19",
    block_background_fill="#0b0f19",
    block_border_width="0px"
)

# --- 4. MAIN LAYOUT ---
with gr.Blocks(title="PaperMind") as demo:
    current_user_state = gr.State(value="")

    # --- LOGIN OVERLAY ---
    with gr.Group(visible=True) as login_overlay:
        with gr.Row():
            with gr.Column(scale=1): pass
            with gr.Column(scale=1):
                # Login Card Container
                with gr.Group(elem_classes="login-card"):
                    # FIX 1: Removed style argument, used CSS class "login-title"
                    gr.Markdown("## 🧠 PaperMind", elem_classes=["gradient-text", "login-title"])
                    gr.Markdown("Sign in to your professional workspace")
                    
                    with gr.Tabs():
                        with gr.Tab("Sign In"):
                            l_u = gr.Textbox(label="Username", elem_classes="search-pill")
                            l_p = gr.Textbox(label="Password", type="password", elem_classes="search-pill")
                            login_error = gr.Markdown("")
                            btn_log = gr.Button("Login", variant="primary")
                        with gr.Tab("Register"):
                            r_u = gr.Textbox(label="New Username", elem_classes="search-pill")
                            r_p = gr.Textbox(label="New Password", type="password", elem_classes="search-pill")
                            btn_reg = gr.Button("Create Account")
                            reg_msg = gr.Markdown("")
            with gr.Column(scale=1): pass

    # --- MAIN INTERFACE ---
    with gr.Row(visible=False) as main_layout:
        
        # 1. SIDEBAR
        with gr.Column(scale=1, elem_classes="sidebar-col", min_width=240):
            gr.Markdown("PaperMind", elem_classes="sidebar-header")
            
            btn_new = gr.Button("+ New Research", variant="secondary")
            
            # FIX 2: Removed style argument, used CSS class "recent-label"
            gr.Markdown("### Recent Activity", elem_classes="recent-label")
            
            history_list = gr.Textbox(show_label=False, interactive=False, lines=12, container=False)
            
            # Bottom Settings
            # FIX 3: Removed style argument, used CSS class "sidebar-footer"
            with gr.Group(elem_classes="sidebar-footer"):
                with gr.Accordion("⚙️ Settings", open=False):
                    btn_del = gr.Button("Delete Account", variant="stop", size="sm")
                    btn_logout = gr.Button("Log Out", size="sm")

        # 2. MAIN CONTENT AREA
        with gr.Column(scale=5):
            
            # TOP BAR (Profile)
            with gr.Row():
                with gr.Column(scale=10): pass 
                with gr.Column(scale=2, min_width=150):
                    profile_html = gr.HTML() # Injected on login

            # HERO SECTION (Centered)
            with gr.Group() as hero_section:
                hero_html = gr.HTML() # Injected on login
            
            # INPUT AREA (Floating Pill)
            with gr.Group():
                topic_in = gr.Textbox(
                    show_label=False, 
                    placeholder=" Ask anything... (e.g., 'Advancements in CRISPR')", 
                    lines=1, 
                    elem_classes="search-pill"
                )
                
                # SUGGESTION CHIPS
                with gr.Row(elem_id="chips", visible=True) as chips_row:
                    c1 = gr.Button(" Genomics", elem_classes="chip-btn")
                    c2 = gr.Button(" AI Ethics", elem_classes="chip-btn")
                    c3 = gr.Button(" Climate Tech", elem_classes="chip-btn")
                    c4 = gr.Button(" Space Propulsion", elem_classes="chip-btn")

            # RESULT AREA (Streamed Content)
            with gr.Group(visible=False) as result_area:
                result_text = gr.Markdown(elem_classes="result-area")
                
                with gr.Accordion("📂 Research Assets", open=False):
                    meta_display = gr.HTML()
                    with gr.Row():
                        report_file = gr.File(label="📄 Final Report")
                        papers_download = gr.File(label="📚 Source Files")

    # --- WIRING ---
    btn_reg.click(register, [r_u, r_p], reg_msg)
    
    # Login Flow
    btn_log.click(
        login, 
        [l_u, l_p], 
        [login_overlay, main_layout, hero_html, profile_html, history_list, current_user_state, login_error]
    )
    
    # Logout & Delete
    btn_logout.click(logout, None, [login_overlay, main_layout, current_user_state])
    btn_del.click(delete_account, [current_user_state], [login_overlay, main_layout, current_user_state])

    # Chip Helpers
    c1.click(lambda: "Recent advancements in Genomics", None, topic_in)
    c2.click(lambda: "Ethical implications of Artificial Intelligence", None, topic_in)
    c3.click(lambda: "Emerging technologies in Climate Change mitigation", None, topic_in)
    c4.click(lambda: "Future of Space Propulsion systems", None, topic_in)

    # MAIN STREAMING ACTION
    topic_in.submit(
        run_agent_stream, 
        [topic_in, current_user_state], 
        [hero_section, chips_row, result_text, report_file, papers_download, meta_display]
    ).then(
        lambda: gr.update(visible=True), None, result_area
    )
    
    # New Chat
    btn_new.click(
        lambda: (gr.update(value=""), gr.update(visible=True), gr.update(visible=True), gr.update(visible=False)),
        None,
        [topic_in, hero_section, chips_row, result_area]
    )

if __name__ == "__main__":
    # FIX 4: Passed theme and css here
    demo.launch(theme=theme, css=frontend_css)