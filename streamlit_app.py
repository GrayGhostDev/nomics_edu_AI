import streamlit as st
import json
from datetime import datetime
import uuid
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
import os
from pathlib import Path
import hashlib
import pandas as pd
import threading

# Initialize session state
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'teacher_info' not in st.session_state:
    st.session_state.teacher_info = {}
if 'game_request' not in st.session_state:
    st.session_state.game_request = {}

# LLM Provider selection and API key input
if 'llm_provider' not in st.session_state:
    st.session_state.llm_provider = 'Ollama (local)'
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = ''

# Set page config
st.set_page_config(
    page_title="Nomics Education Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
st.markdown("""
    <style>
    /* Main container and general styles */
    .main {
        padding: 2rem;
        background-color: #1a1a2e;
        color: #e6e6e6;
    }
    
    /* Override Streamlit's default white background */
    .stApp {
        background-color: #1a1a2e;
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        margin-top: 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    /* Success message styling */
    .success-message {
        padding: 1.5rem;
        background-color: #1e4620;
        border-color: #2a5a2a;
        color: #b3ffb3;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Input fields styling */
    .stTextInput>div>div>input, 
    .stSelectbox>div>div>div,
    .stNumberInput>div>div>input,
    .stTextArea>div>div>textarea {
        border-radius: 8px;
        background-color: #2d2d44;
        color: #e6e6e6;
        border: 1px solid #404040;
    }
    
    /* Progress bar */
    .stProgress>div>div>div {
        background-color: #4CAF50;
    }
    
    /* Step container */
    .step-container {
        background-color: #242442;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        margin-bottom: 2rem;
        color: #e6e6e6;
    }
    
    /* Header container */
    .header-container {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(120deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
    }
    
    /* Subject cards */
    .subject-card {
        background-color: #2d2d44;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        color: #e6e6e6;
    }
    
    .subject-card h4 {
        color: #7fdbff;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .subject-card p, .subject-card ul {
        color: #cccccc;
    }
    
    .subject-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        background-color: #363654;
    }

    /* Override default text colors */
    h1, h2, h3, h4, h5, h6 {
        color: #7fdbff !important;
    }
    
    p, li, label, div {
        color: #e6e6e6 !important;
    }

    /* Selectbox dropdown */
    .stSelectbox>div>div>div>div {
        background-color: #2d2d44;
        color: #e6e6e6;
    }

    /* Slider */
    .stSlider>div>div>div {
        background-color: #4CAF50;
    }

    /* Game Generation Page Specific Styles */
    .generation-container {
        background-color: #1a1a2e;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: #e6e6e6;
    }

    .progress-card {
        background-color: #242442;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #4CAF50;
    }

    .analytics-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        margin: 1rem 0;
    }

    .analytics-card {
        background-color: #2d2d44;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }

    .analytics-card h4 {
        color: #7fdbff;
        margin-bottom: 0.5rem;
    }

    .analytics-card p {
        color: #e6e6e6;
        font-size: 1.2em;
    }

    .generation-step {
        display: flex;
        align-items: center;
        margin: 0.5rem 0;
        padding: 0.5rem;
        background-color: #2d2d44;
        border-radius: 8px;
    }

    .generation-step .status {
        margin-right: 1rem;
        font-size: 1.2em;
    }

    .generation-step .details {
        flex-grow: 1;
    }

    .generation-step .time {
        color: #7fdbff;
        font-size: 0.9em;
    }

    .success-banner {
        background: linear-gradient(120deg, #1e4620 0%, #2a5a2a 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        text-align: center;
        color: #b3ffb3;
    }

    .download-section {
        background-color: #242442;
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
    }

    .download-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
    }

    .file-stats {
        background-color: #2d2d44;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
    }

    .file-stats p {
        margin: 0.2rem 0;
        color: #e6e6e6;
    }

    .stepper {
        display: flex;
        justify-content: center;
        margin-bottom: 2rem;
    }
    .step {
        padding: 0.5em 1.5em;
        border-radius: 20px;
        margin: 0 0.5em;
        background: #242442;
        color: #7fdbff;
        font-weight: bold;
        border: 2px solid #4CAF50;
        opacity: 0.7;
    }
    .step.active {
        background: #4CAF50;
        color: #fff;
        opacity: 1;
    }
    .field-error input, .field-error textarea, .field-error select {
        border: 2px solid #ff4d4f !important;
        background-color: #2d1a1a !important;
    }
    .field-success input, .field-success textarea, .field-success select {
        border: 2px solid #4CAF50 !important;
        background-color: #1a2e1a !important;
    }
    </style>
""", unsafe_allow_html=True)

TEMPLATES_FILE = "templates.json"
ANALYTICS_FILE = "analytics.json"
USERS_FILE = "users.json"

# Admin password (for demo purposes, use a better system in production)
ADMIN_PASSWORD = "admin123"

TEMPLATES_LOCK = threading.Lock()
USERS_LOCK = threading.Lock()
ANALYTICS_LOCK = threading.Lock()

def load_templates():
    """Load available templates and subjects with their specific requirements from a JSON file."""
    if os.path.exists(TEMPLATES_FILE):
        with open(TEMPLATES_FILE, "r") as f:
            return json.load(f)
    # Fallback to default if file doesn't exist
    templates = {
        "Mathematics": {
            "games": {
                "NumberParkour": {
                    "description": "A parkour-style game where players solve math problems to progress",
                    "specific_fields": ["problem_types", "value_ranges", "difficulty_progression"]
                },
                "MathQuest": {
                    "description": "An adventure game with mathematical challenges and puzzles",
                    "specific_fields": ["quest_type", "math_concepts", "reward_system"]
                }
            }
        },
        "Science": {
            "games": {
                "BioLabSimulator": {
                    "description": "Simulate biology experiments in a virtual laboratory",
                    "specific_fields": ["experiment_types", "lab_equipment", "safety_protocols"]
                },
                "EcosystemExplorer": {
                    "description": "Explore and learn about different ecosystems and their interactions",
                    "specific_fields": ["ecosystem_type", "species_interactions", "environmental_factors"]
                }
            }
        },
        "History": {
            "games": {
                "CivilizationBuilder": {
                    "description": "Build and manage historical civilizations",
                    "specific_fields": ["historical_era", "civilization_aspects", "historical_events"]
                },
                "TimeTravelerChronicles": {
                    "description": "Travel through time to experience historical events",
                    "specific_fields": ["time_periods", "historical_figures", "key_decisions"]
                }
            }
        },
        "LanguageArts": {
            "games": {
                "BookDetectiveAgency": {
                    "description": "Solve mysteries using reading comprehension and literary analysis",
                    "specific_fields": ["genre", "reading_level", "literary_elements"]
                },
                "StoryForgerAdventure": {
                    "description": "Create and explore interactive storytelling adventures",
                    "specific_fields": ["story_themes", "character_types", "plot_elements"]
                }
            }
        },
        "Geography": {
            "games": {
                "CartographersQuest": {
                    "description": "Create and explore maps while learning geography",
                    "specific_fields": ["map_types", "geographical_features", "navigation_tools"]
                },
                "GlobalExplorerVR": {
                    "description": "Virtual reality exploration of world geography",
                    "specific_fields": ["regions", "cultural_elements", "geographical_phenomena"]
                }
            }
        }
    }
    return templates

def save_templates(templates):
    try:
        with TEMPLATES_LOCK:
            with open(TEMPLATES_FILE, "w") as f:
                json.dump(templates, f, indent=2)
    except Exception as e:
        st.error(f"Error saving templates: {e}")

def create_llm_prompt(teacher_info, game_request, template_content):
    """Create the prompt for the LLM"""
    prompt = f"""You are an expert Roblox educational game designer. Create a Lua script for an educational game based on the following requirements:

Teacher Information:
- Name: {teacher_info["name"]}
- School: {teacher_info["school"]}
- Grade Level: {teacher_info["grade_level"]}
- Teaching Style: {teacher_info["preferred_teaching_style"]}

Game Requirements:
- Subject: {game_request["subject"]}
- Topic: {game_request["topic"]}
- Learning Objectives: {', '.join(game_request["learning_objectives"])}
- Grade Level: {game_request["grade_level"]}
- Difficulty: {game_request["difficulty"]}
- Game Type: {game_request["game_type"]}
"""

    # Add game-specific requirements based on subject and game type
    if "game_specifics" in game_request and game_request["game_specifics"]:
        prompt += "\nGame-Specific Requirements:\n"
        
        for key, value in game_request["game_specifics"].items():
            if isinstance(value, list):
                prompt += f"- {key}: {', '.join(value)}\n"
            elif isinstance(value, dict):
                prompt += f"- {key}:\n"
                for sub_key, sub_value in value.items():
                    prompt += f"  - {sub_key}: {sub_value}\n"
            else:
                prompt += f"- {key}: {value}\n"

    prompt += f"""
Base Template:
{template_content}

Instructions:
1. Use the provided template as a base structure
2. Modify the template to incorporate the teacher's requirements and style
3. Ensure the content is appropriate for the specified grade level
4. Include all necessary Lua functions and game logic
5. Maintain proper Lua syntax and structure
6. Include appropriate comments and documentation

Generate ONLY the Lua code. Do not include any explanations or markdown formatting.
"""
    return prompt

def get_template_content(subject, game_type):
    """Get the content of the template file"""
    template_path = Path("Games") / subject / f"{game_type}.lua"
    try:
        with open(template_path, 'r') as f:
            return f.read()
    except Exception as e:
        st.error(f"Error reading template: {e}")
        return ""

def log_analytics(event_type, subject, game_type, user=None):
    entry = {
        "event": event_type,
        "subject": subject,
        "game_type": game_type,
        "timestamp": datetime.now().isoformat(),
        "user": user or "anonymous"
    }
    analytics = []
    if os.path.exists(ANALYTICS_FILE):
        with open(ANALYTICS_FILE, "r") as f:
            try:
                analytics = json.load(f)
            except Exception:
                analytics = []
    analytics.append(entry)
    try:
        with ANALYTICS_LOCK:
            with open(ANALYTICS_FILE, "w") as f:
                json.dump(analytics, f, indent=2)
    except Exception as e:
        st.error(f"Error saving analytics: {e}")

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    try:
        with USERS_LOCK:
            with open(USERS_FILE, "w") as f:
                json.dump(users, f, indent=2)
    except Exception as e:
        st.error(f"Error saving users: {e}")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# User authentication logic
if 'user' not in st.session_state:
    st.session_state.user = None

users = load_users()

# Sidebar login/registration
if st.session_state.user is None:
    st.sidebar.title("Teacher Login / Registration")
    auth_mode = st.sidebar.radio("Account", ["Login", "Register"])
    if auth_mode == "Login":
        login_email = st.sidebar.text_input("Email", key="login_email")
        login_password = st.sidebar.text_input("Password", type="password", key="login_password")
        if st.sidebar.button("Login"):
            if login_email in users and users[login_email]["password"] == hash_password(login_password):
                st.session_state.user = {
                    "email": login_email,
                    "name": users[login_email]["name"]
                }
                st.sidebar.success(f"Welcome, {users[login_email]['name']}!")
                st.rerun()
            else:
                st.sidebar.error("Invalid email or password.")
    else:
        reg_name = st.sidebar.text_input("Name", key="reg_name")
        reg_email = st.sidebar.text_input("Email", key="reg_email")
        reg_password = st.sidebar.text_input("Password", type="password", key="reg_password")
        reg_password2 = st.sidebar.text_input("Confirm Password", type="password", key="reg_password2")
        if st.sidebar.button("Register"):
            if not reg_name or not reg_email or not reg_password:
                st.sidebar.error("All fields are required.")
            elif reg_email in users:
                st.sidebar.error("Email already registered.")
            elif reg_password != reg_password2:
                st.sidebar.error("Passwords do not match.")
            else:
                users[reg_email] = {
                    "name": reg_name,
                    "password": hash_password(reg_password)
                }
                save_users(users)
                st.sidebar.success("Registration successful! Please log in.")
                st.rerun()
    st.stop()
else:
    st.sidebar.markdown(f"**Logged in as:** {st.session_state.user['name']} ({st.session_state.user['email']})")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

# Add Help & FAQ section in the sidebar
with st.sidebar.expander("❓ Help & FAQ", expanded=False):
    st.markdown("""
    **How do I create a game?**
    1. Log in or register as a teacher.
    2. Complete your teacher profile.
    3. Select a subject and game type.
    4. Fill in the game requirements and customization fields.
    5. Generate and download your game!

    **How do I use the admin panel?**
    - Enable Admin Mode in the sidebar and enter the admin password.
    - Manage templates, games, and view analytics.

    **Where are my games saved?**
    - Generated games are available for download after creation and are saved in the `games_output` folder on the server.

    **Who can see analytics?**
    - Teachers see only their own activity. Admins see all analytics and can filter/export data.

    **Need more help?**
    - Contact your platform administrator or refer to the project documentation.
    """)

def main():
    st.sidebar.title("Settings")
    admin_mode = st.sidebar.checkbox("Admin Mode")
    admin_authenticated = False
    if admin_mode:
        password = st.sidebar.text_input("Admin Password", type="password")
        if password == ADMIN_PASSWORD:
            admin_authenticated = True
            st.sidebar.success("Admin authenticated!")
        elif password:
            st.sidebar.error("Incorrect password.")

    templates = load_templates()

    if admin_mode and admin_authenticated:
        tab = st.sidebar.radio("Admin Panel", ["Templates", "Analytics"])
        if tab == "Analytics":
            st.title("Admin Analytics Dashboard")
            st.info("View usage statistics and recent activity.")
            analytics = []
            if os.path.exists(ANALYTICS_FILE):
                with open(ANALYTICS_FILE, "r") as f:
                    try:
                        analytics = json.load(f)
                    except Exception:
                        analytics = []
            if not analytics:
                st.warning("No analytics data yet.")
                st.stop()
            import pandas as pd
            df = pd.DataFrame(analytics)
            # --- FILTERS ---
            st.sidebar.markdown("---")
            st.sidebar.header("Analytics Filters")
            user_options = ["All"] + sorted([u for u in df["user"].unique() if u and u != "anonymous"])
            selected_user = st.sidebar.selectbox("User", user_options)
            subject_options = ["All"] + sorted(df["subject"].dropna().unique())
            selected_subject = st.sidebar.selectbox("Subject", subject_options)
            game_options = ["All"] + sorted(df["game_type"].dropna().unique())
            selected_game = st.sidebar.selectbox("Game Type", game_options)
            min_date = pd.to_datetime(df["timestamp"]).min().date()
            max_date = pd.to_datetime(df["timestamp"]).max().date()
            date_range = st.sidebar.date_input("Date Range", (min_date, max_date), min_value=min_date, max_value=max_date)
            # --- APPLY FILTERS ---
            filtered = df.copy()
            if selected_user != "All":
                filtered = filtered[filtered["user"] == selected_user]
            if selected_subject != "All":
                filtered = filtered[filtered["subject"] == selected_subject]
            if selected_game != "All":
                filtered = filtered[filtered["game_type"] == selected_game]
            filtered["timestamp"] = pd.to_datetime(filtered["timestamp"])
            if isinstance(date_range, tuple) and len(date_range) == 2:
                filtered = filtered[(filtered["timestamp"].dt.date >= date_range[0]) & (filtered["timestamp"].dt.date <= date_range[1])]
            # --- EXPORT CSV ---
            st.download_button(
                "Export Filtered Analytics as CSV",
                filtered.to_csv(index=False),
                file_name="filtered_analytics.csv",
                mime="text/csv"
            )
            # --- POPULARITY CHARTS ---
            st.subheader("Most Popular Subjects")
            st.bar_chart(filtered["subject"].value_counts())
            st.subheader("Most Popular Games")
            st.bar_chart(filtered["game_type"].value_counts())
            # --- TIME-SERIES CHART ---
            st.subheader("Games Generated Per Week")
            gen_df = filtered[filtered["event"] == "generate"].copy()
            if not gen_df.empty:
                gen_df["week"] = gen_df["timestamp"].dt.to_period("W").apply(lambda r: r.start_time)
                st.line_chart(gen_df.groupby("week").size())
            else:
                st.info("No game generation events in this filter.")
            # --- RECENT ACTIVITY ---
            st.subheader("Recent Activity")
            st.dataframe(filtered.sort_values("timestamp", ascending=False).head(20))
            st.stop()
        st.title("Admin Panel: Template/Game Management")
        st.info("Add, edit, or remove subjects and games. Changes are saved to templates.json.")
        st.markdown("---")
        # Subject management
        subjects = list(templates.keys())
        selected_subject = st.selectbox("Select Subject to Edit", subjects)
        if st.button("Delete Subject"):
            del templates[selected_subject]
            save_templates(templates)
            st.success(f"Subject '{selected_subject}' deleted.")
            st.rerun()
        st.markdown("---")
        new_subject = st.text_input("Add New Subject")
        if st.button("Add Subject") and new_subject.strip():
            if new_subject in templates:
                st.warning("Subject already exists.")
            else:
                templates[new_subject] = {"games": {}}
                save_templates(templates)
                st.success(f"Subject '{new_subject}' added.")
                st.rerun()
        st.markdown("---")
        # Game management for selected subject
        games = list(templates[selected_subject]["games"].keys())
        selected_game = st.selectbox("Select Game to Edit", games) if games else None
        if selected_game:
            st.text_area("Game Description", value=templates[selected_subject]["games"][selected_game]["description"], key="game_desc")
            st.text_area("Specific Fields (comma-separated)", value=", ".join(templates[selected_subject]["games"][selected_game]["specific_fields"]), key="game_fields")
            if st.button("Save Game Changes"):
                templates[selected_subject]["games"][selected_game]["description"] = st.session_state["game_desc"]
                templates[selected_subject]["games"][selected_game]["specific_fields"] = [f.strip() for f in st.session_state["game_fields"].split(",") if f.strip()]
                save_templates(templates)
                st.success(f"Game '{selected_game}' updated.")
        if selected_game and st.button("Delete Game"):
            del templates[selected_subject]["games"][selected_game]
            save_templates(templates)
            st.success(f"Game '{selected_game}' deleted.")
            st.rerun()
        st.markdown("---")
        new_game = st.text_input("Add New Game Name")
        new_game_desc = st.text_input("New Game Description")
        new_game_fields = st.text_input("New Game Specific Fields (comma-separated)")
        if st.button("Add Game") and new_game.strip():
            if new_game in templates[selected_subject]["games"]:
                st.warning("Game already exists.")
            else:
                templates[selected_subject]["games"][new_game] = {
                    "description": new_game_desc,
                    "specific_fields": [f.strip() for f in new_game_fields.split(",") if f.strip()]
                }
                save_templates(templates)
                st.success(f"Game '{new_game}' added to subject '{selected_subject}'.")
                st.rerun()
        st.stop()

    # Show teacher analytics dashboard if not admin
    if not admin_mode and st.session_state.user:
        analytics = []
        if os.path.exists(ANALYTICS_FILE):
            with open(ANALYTICS_FILE, "r") as f:
                try:
                    analytics = json.load(f)
                except Exception:
                    analytics = []
        import pandas as pd
        df = pd.DataFrame(analytics)
        user_email = st.session_state.user["email"]
        user_df = df[df["user"] == user_email]
        st.markdown("""
            <div class="header-container">
                <h2>📊 Your Activity Dashboard</h2>
            </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Games Generated", int((user_df["event"] == "generate").sum()))
        with col2:
            st.metric("Script Downloads", int((user_df["event"] == "download_script").sum()))
        with col3:
            st.metric("Input Downloads", int((user_df["event"] == "download_input").sum()))
        st.subheader("Most Used Subjects")
        if not user_df.empty:
            st.bar_chart(user_df["subject"].value_counts())
            st.subheader("Most Used Game Types")
            st.bar_chart(user_df["game_type"].value_counts())
            st.subheader("Games Generated Per Week")
            gen_df = user_df[user_df["event"] == "generate"].copy()
            if not gen_df.empty:
                gen_df["timestamp"] = pd.to_datetime(gen_df["timestamp"])
                gen_df["week"] = gen_df["timestamp"].dt.to_period("W").apply(lambda r: r.start_time)
                st.line_chart(gen_df.groupby("week").size())
            else:
                st.info("No game generation events yet.")
            st.subheader("Recent Activity")
            st.dataframe(user_df.sort_values("timestamp", ascending=False).head(20))
        else:
            st.info("No analytics data for your account yet.")

    # Add How to Use section at the top of the main app for new users
    if st.session_state.user and not st.session_state.get("seen_onboarding"):
        st.markdown("""
        <div class="success-banner">
            <h3>👋 Welcome to the Nomics Education Platform!</h3>
            <p>To get started, complete your teacher profile and follow the stepper at the top of the page.<br>
            You can always access help from the sidebar.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Got it! Hide this guide."):
            st.session_state["seen_onboarding"] = True

    st.markdown("""
        <div class="header-container">
            <h1>🎓 Nomics Education Platform</h1>
            <p style="font-size: 1.2em;">Create Engaging Educational Games for Your Students</p>
        </div>
    """, unsafe_allow_html=True)

    steps = ["Teacher Info", "Subject & Game", "Game Requirements", "Generate Game"]
    current_step = st.session_state.current_step
    # Stepper UI
    st.markdown("""
        <div class="stepper">
    """, unsafe_allow_html=True)
    for i, step in enumerate(steps, 1):
        active = "active" if i == current_step else ""
        st.markdown(f'<div class="step {active}">{i}. {step}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Step 1: Teacher Info
    if current_step == 1:
        st.markdown('<div class="step-container">', unsafe_allow_html=True)
        st.header("👩‍🏫 Teacher Profile")
        with st.form("teacher_info_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Your Name", value=st.session_state.teacher_info.get("name", ""), key="name_input", help="Enter your full name. This will be used for analytics and game ownership.", label_visibility="visible")
                if st.session_state.get("show_teacher_error") and not name.strip():
                    st.warning("Name is required.")
                grade_level = st.text_input("Grade Level", value=st.session_state.teacher_info.get("grade_level", ""), key="grade_input", help="E.g., 5th Grade, 8th Grade, etc.")
                subjects = st.text_input("Subjects", value=", ".join(st.session_state.teacher_info.get("subjects", [])), key="subjects_input", help="Comma-separated subjects you teach", label_visibility="visible")
                if st.session_state.get("show_teacher_error") and not subjects.strip():
                    st.warning("Subjects are required.")
            with col2:
                school = st.text_input("School Name", value=st.session_state.teacher_info.get("school", ""), key="school_input", help="Your school or organization.", label_visibility="visible")
                if st.session_state.get("show_teacher_error") and not school.strip():
                    st.warning("School Name is required.")
                teaching_style = st.selectbox(
                    "Teaching Style",
                    ["Interactive", "Traditional", "Project-based"],
                    index=["Interactive", "Traditional", "Project-based"].index(st.session_state.teacher_info.get("preferred_teaching_style", "Interactive")),
                    key="teaching_style_input",
                    help="Preferred teaching style",
                    label_visibility="visible"
                )
            st.markdown("---")
            st.subheader("LMS Integration (Optional)")
            lms_col1, lms_col2 = st.columns(2)
            with lms_col1:
                schoology_key = st.text_input("Schoology API Key", value=st.session_state.teacher_info.get("lms_integration", {}).get("schoology_key", ""), key="schoology_key", help="Enter your Schoology API Key (optional)")
                canvas_token = st.text_input("Canvas API Token", value=st.session_state.teacher_info.get("lms_integration", {}).get("canvas_token", ""), key="canvas_token", help="Enter your Canvas API Token (optional)")
            with lms_col2:
                blackboard_user = st.text_input("Blackboard Username", value=st.session_state.teacher_info.get("lms_integration", {}).get("blackboard_user", ""), key="blackboard_user", help="Enter your Blackboard username (optional)")
                blackboard_pass = st.text_input("Blackboard Password", value=st.session_state.teacher_info.get("lms_integration", {}).get("blackboard_pass", ""), key="blackboard_pass", type="password", help="Enter your Blackboard password (optional)")
            colA, colB = st.columns([1,1])
            with colA:
                st.write("")
            with colB:
                if st.form_submit_button("Next →"):
                    if name and school and grade_level and subjects and teaching_style:
                        st.session_state.teacher_info = {
                            "id": str(uuid.uuid4())[:8],
                            "name": name,
                            "school": school,
                            "grade_level": grade_level,
                            "subjects": [s.strip() for s in subjects.split(',')],
                            "preferred_teaching_style": teaching_style,
                            "timestamp": datetime.now().isoformat(),
                            "lms_integration": {
                                "schoology_key": schoology_key,
                                "canvas_token": canvas_token,
                                "blackboard_user": blackboard_user,
                                "blackboard_pass": blackboard_pass
                            }
                        }
                        st.session_state.current_step = 2
                        st.session_state["show_teacher_error"] = False
                        st.success("Teacher info saved! Proceed to the next step.")
                        st.rerun()
                    else:
                        st.session_state["show_teacher_error"] = True
        st.markdown('</div>', unsafe_allow_html=True)

    # Step 2: Subject & Game Selection
    elif current_step == 2:
        st.markdown('<div class="step-container">', unsafe_allow_html=True)
        st.header("🎮 Select Subject & Game")
        subject = st.selectbox(
            "Select Subject",
            list(templates.keys()),
            key="selected_subject",
            index=list(templates.keys()).index(st.session_state.game_request.get("subject", list(templates.keys())[0])) if st.session_state.game_request.get("subject") else 0
        )
        available_games = templates[subject]["games"]
        game_type = st.selectbox(
            "Select Game Type",
            list(available_games.keys()),
            key=f"selected_game_type_{subject}",
            index=list(available_games.keys()).index(st.session_state.game_request.get("game_type", list(available_games.keys())[0])) if st.session_state.game_request.get("game_type") else 0
        )
        st.markdown(f"**Game Description:** {available_games[game_type]['description']}")
        colA, colB = st.columns([1,1])
        with colA:
            if st.button("← Back"):
                st.session_state.current_step = 1
                st.rerun()
        with colB:
            if st.button("Next →"):
                st.session_state.game_request["subject"] = subject
                st.session_state.game_request["game_type"] = game_type
                st.session_state.current_step = 3
                st.success("Subject and game type selected! Proceed to the next step.")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Step 3: Game Requirements & Customization
    elif current_step == 3:
        st.markdown('<div class="step-container">', unsafe_allow_html=True)
        st.header("📝 Game Requirements & Customization")
        with st.form("game_requirements_form"):
            col1, col2 = st.columns(2)
            with col1:
                topic = st.text_input("Topic *", value=st.session_state.game_request.get("topic", ""), key="topic_input")
                if st.session_state.get("show_game_error") and not topic.strip():
                    st.warning("Topic is required.")
                grade_level = st.number_input("Target Grade Level", min_value=1, max_value=12, value=st.session_state.game_request.get("grade_level", 1), key="grade_level_input")
            with col2:
                objectives = st.text_input("Learning Objectives *", value=", ".join(st.session_state.game_request.get("learning_objectives", [])), key="objectives_input")
                if st.session_state.get("show_game_error") and not objectives.strip():
                    st.warning("Learning Objectives are required.")
                difficulty = st.slider("Difficulty Level", 1, 3, st.session_state.game_request.get("difficulty", 1), key="difficulty_input")
            specific_fields = templates[st.session_state.game_request["subject"]]["games"][st.session_state.game_request["game_type"]]["specific_fields"]
            missing_fields = []
            game_specifics = {}
            field_widget_map = {
                "problem_types": lambda: st.multiselect(
                    "Problem Types *",
                    ["Addition", "Subtraction", "Multiplication", "Division", "Fractions", "Decimals"],
                    help="Select types of problems to include"
                ),
                "value_ranges": lambda: st.slider(
                    "Number Range *",
                    1, 1000, (1, 100),
                    help="Select the range of numbers to use in problems"
                ),
                "difficulty_progression": lambda: st.checkbox("Enable Progressive Difficulty *"),
                "quest_type": lambda: st.selectbox(
                    "Quest Type *",
                    ["Story-based", "Challenge-based", "Exploration"]
                ),
                "math_concepts": lambda: st.multiselect(
                    "Math Concepts *",
                    ["Basic Operations", "Geometry", "Algebra", "Statistics", "Logic"]
                ),
                "reward_system": lambda: st.selectbox(
                    "Reward System *",
                    ["Stars", "Points", "Achievements", "Unlockable Content"]
                ),
                "experiment_types": lambda: st.multiselect(
                    "Experiment Types *",
                    ["Cell Biology", "Genetics", "Chemistry", "Physics", "Ecology"]
                ),
                "lab_equipment": lambda: st.multiselect(
                    "Lab Equipment *",
                    ["Microscope", "Test Tubes", "Beakers", "Bunsen Burner", "Safety Gear"]
                ),
                "safety_protocols": lambda: st.multiselect(
                    "Safety Protocols *",
                    ["Proper Equipment Handling", "Chemical Safety", "Emergency Procedures"]
                ),
                "ecosystem_type": lambda: st.selectbox(
                    "Ecosystem Type *",
                    ["Forest", "Ocean", "Desert", "Grassland", "Tundra"]
                ),
                "species_interactions": lambda: st.multiselect(
                    "Species Interactions *",
                    ["Predator-Prey", "Symbiosis", "Competition", "Adaptation"]
                ),
                "environmental_factors": lambda: st.multiselect(
                    "Environmental Factors *",
                    ["Climate", "Resources", "Human Impact", "Natural Disasters"]
                ),
                "historical_era": lambda: st.selectbox(
                    "Historical Era *",
                    ["Ancient", "Medieval", "Renaissance", "Modern"]
                ),
                "civilization_aspects": lambda: st.multiselect(
                    "Civilization Aspects *",
                    ["Government", "Economy", "Military", "Culture", "Technology"]
                ),
                "historical_events": lambda: st.multiselect(
                    "Historical Events *",
                    ["Wars", "Discoveries", "Inventions", "Social Changes"]
                ),
                "time_periods": lambda: st.multiselect(
                    "Time Periods *",
                    ["Prehistoric", "Ancient Civilizations", "Middle Ages", "Industrial Revolution", "Modern Era"]
                ),
                "historical_figures": lambda: st.multiselect(
                    "Historical Figures *",
                    ["Leaders", "Inventors", "Artists", "Scientists"]
                ),
                "key_decisions": lambda: st.checkbox("Include Key Historical Decisions *"),
                "genre": lambda: st.selectbox(
                    "Genre *",
                    ["Mystery", "Fantasy", "Historical Fiction", "Science Fiction"]
                ),
                "reading_level": lambda: st.slider(
                    "Reading Level *",
                    1, 12, 5,
                    help="Select the target reading level"
                ),
                "literary_elements": lambda: st.multiselect(
                    "Literary Elements *",
                    ["Plot", "Character", "Setting", "Theme", "Conflict"]
                ),
                "story_themes": lambda: st.multiselect(
                    "Story Themes *",
                    ["Adventure", "Friendship", "Growth", "Challenge"]
                ),
                "character_types": lambda: st.multiselect(
                    "Character Types *",
                    ["Hero", "Mentor", "Ally", "Antagonist"]
                ),
                "plot_elements": lambda: st.multiselect(
                    "Plot Elements *",
                    ["Quest", "Conflict", "Resolution", "Twist"]
                ),
                "map_types": lambda: st.multiselect(
                    "Map Types *",
                    ["Political", "Physical", "Climate", "Population"]
                ),
                "geographical_features": lambda: st.multiselect(
                    "Geographical Features *",
                    ["Mountains", "Rivers", "Deserts", "Forests", "Oceans"]
                ),
                "navigation_tools": lambda: st.multiselect(
                    "Navigation Tools *",
                    ["Compass", "GPS", "Landmarks", "Coordinates"]
                ),
                "regions": lambda: st.multiselect(
                    "Regions *",
                    ["North America", "South America", "Europe", "Asia", "Africa", "Oceania"]
                ),
                "cultural_elements": lambda: st.multiselect(
                    "Cultural Elements *",
                    ["Languages", "Customs", "Architecture", "Art"]
                ),
                "geographical_phenomena": lambda: st.multiselect(
                    "Geographical Phenomena *",
                    ["Weather", "Natural Disasters", "Ecosystems", "Landforms"]
                ),
            }
            for field in specific_fields:
                label = f"{field.replace('_', ' ').title()} *"
                field_key = f"custom_{field}_input"
                if field in field_widget_map:
                    value = field_widget_map[field]()
                    if field == "value_ranges":
                        game_specifics[field] = {"min": value[0], "max": value[1]}
                        if value == (1, 100):
                            missing_fields.append(label)
                            st.warning(f"{label} is required.")
                    elif isinstance(value, bool):
                        game_specifics[field] = value
                        if not value:
                            missing_fields.append(label)
                            st.warning(f"{label} is required.")
                    else:
                        game_specifics[field] = value
                        if not value or (isinstance(value, list) and not any(value)):
                            missing_fields.append(label)
                            st.warning(f"{label} is required.")
                else:
                    value = st.text_input(label, key=field_key)
                    game_specifics[field] = value
                    if not value.strip():
                        missing_fields.append(label)
                        st.warning(f"{label} is required.")
            time_limit = st.number_input("Time Limit (minutes)", min_value=0, value=st.session_state.game_request.get("time_limit", 0), key="time_limit_input")
            colA, colB = st.columns([1,1])
            with colA:
                if st.form_submit_button("← Back"):
                    st.session_state.current_step = 2
                    st.rerun()
            with colB:
                if st.form_submit_button("Generate Game →"):
                    if not topic.strip():
                        missing_fields.append("Topic *")
                        st.warning("Topic is required.")
                    if not objectives.strip():
                        missing_fields.append("Learning Objectives *")
                        st.warning("Learning Objectives are required.")
                    if missing_fields:
                        st.session_state["show_game_error"] = True
                    else:
                        st.session_state.game_request.update({
                            "topic": topic,
                            "learning_objectives": [obj.strip() for obj in objectives.split(',')],
                            "grade_level": grade_level,
                            "difficulty": difficulty,
                            "custom_content": "",
                            "time_limit": time_limit if time_limit > 0 else None,
                            "game_specifics": game_specifics,
                            "timestamp": datetime.now().isoformat()
                        })
                        st.session_state.current_step = 4
                        st.session_state["show_game_error"] = False
                        st.success("Game requirements saved! Generating your game...")
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Step 4: Generation & Download (reuse your existing code for this step)
    
    elif current_step == 4:
        st.markdown('<div class="generation-container">', unsafe_allow_html=True)
        st.header("🚀 Game Generation")
        # Generate a single timestamp for this generation step
        if 'generation_timestamp' not in st.session_state:
            st.session_state['generation_timestamp'] = datetime.now().strftime('%Y%m%d_%H%M%S')
        timestamp = st.session_state['generation_timestamp']
        # Prepare prompt for preview
        template_content = get_template_content(
            st.session_state.game_request["subject"],
            st.session_state.game_request["game_type"]
        )
        template_content = template_content.replace('{', '{{').replace('}', '}}')
        preview_prompt = create_llm_prompt(
            st.session_state.teacher_info,
            st.session_state.game_request,
            template_content
        )
        with st.expander("🔍 Preview LLM Prompt (Form Input + Template)", expanded=False):
            st.code(preview_prompt, language="markdown")
        with st.spinner("Generating your game, please wait..."):
            try:
                start_time = datetime.now()
                prompt = None  # Will be set later
                response = None
                # LLM selection with fallback
                if st.session_state.llm_provider == 'OpenAI (API)':
                    try:
                        from langchain_openai import OpenAI
                        llm = OpenAI(
                            openai_api_key=st.session_state.openai_api_key,
                            temperature=0.7
                        )
                        # Get template content and prompt as before
                        template_content = get_template_content(
                            st.session_state.game_request["subject"],
                            st.session_state.game_request["game_type"]
                        )
                        
                        template_content = template_content.replace('{', '{{').replace('}', '}}')
                        prompt = create_llm_prompt(
                            st.session_state.teacher_info,
                            st.session_state.game_request,
                            template_content
                        )
                        response = llm.invoke(prompt)
                        
                    except Exception as e:
                        st.warning(f"OpenAI API failed ({e}). Falling back to Ollama (llama3.2).")
                        llm = OllamaLLM(
                            model="llama3.2",
                            temperature=0.7,
                            base_url=os.environ.get('OLLAMA_BASE_URL', "http://localhost:11434")
                        )
                        # Get template content and prompt as before
                        template_content = get_template_content(
                            st.session_state.game_request["subject"],
                            st.session_state.game_request["game_type"]
                        )
                        template_content = template_content.replace('{', '{{').replace('}', '}}')
                        prompt = create_llm_prompt(
                            st.session_state.teacher_info,
                            st.session_state.game_request,
                            template_content
                        )
                        response = llm.invoke(prompt)
                else:
                    llm = OllamaLLM(
                        model="llama3.2",
                        temperature=0.7,
                        base_url=os.environ.get('OLLAMA_BASE_URL', "http://localhost:11434")
                    )
                    # Get template content and prompt as before
                    template_content = get_template_content(
                        st.session_state.game_request["subject"],
                        st.session_state.game_request["game_type"]
                    )
                    template_content = template_content.replace('{', '{{').replace('}', '}}')
                    prompt = create_llm_prompt(
                        st.session_state.teacher_info,
                        st.session_state.game_request,
                        template_content
                    )
                    response = llm.invoke(prompt)
                generated_script = str(response).strip()
                # Remove markdown code block markers if present
                if generated_script.startswith('```lua'):
                    generated_script = generated_script[6:]
                if generated_script.endswith('```'):
                    generated_script = generated_script[:-3]
                generated_script = generated_script.strip()

                if not generated_script:
                    raise ValueError("Failed to generate game script")

                # Save the input data
                input_file = f"llm_input_{timestamp}.json"
                os.makedirs("games_input", exist_ok=True)
                llm_input = {
                    "metadata": {
                        "version": "1.0",
                        "generation_time": datetime.now().isoformat()
                    },
                    "teacher_info": st.session_state.teacher_info,
                    "game_request": st.session_state.game_request
                }
                with open(os.path.join("games_input", input_file), 'w') as f:
                    json.dump(llm_input, f, indent=2)

                # Save the generated script
                output_dir = Path("games_output") / st.session_state.game_request["subject"]
                output_dir.mkdir(parents=True, exist_ok=True)
                script_file = output_dir / f"{st.session_state.teacher_info['id']}_{timestamp}.lua"
                with open(script_file, 'w') as f:
                    f.write(generated_script)

                # Log analytics for game generation
                log_analytics(
                    event_type="generate",
                    subject=st.session_state.game_request["subject"],
                    game_type=st.session_state.game_request["game_type"],
                    user=st.session_state.teacher_info.get("name", "anonymous")
                )

                # Calculate generation time
                generation_time = datetime.now() - start_time
                
                # Success message with analytics
                html_success = """
                    <div class="success-banner">
                        <h2>🎉 Game Generated Successfully!</h2>
                        <p>Generation completed in {} seconds</p>
                    </div>
                """
                html_success = html_success.format(round(generation_time.total_seconds(), 2))
                st.markdown(html_success, unsafe_allow_html=True)

                # Show generation analytics
                html_analytics = """
                    <div class="analytics-grid">
                        <div class="analytics-card">
                            <h4>Script Size</h4>
                            <p>{} KB</p>
                        </div>
                        <div class="analytics-card">
                            <h4>Lines of Code</h4>
                            <p>{}</p>
                        </div>
                        <div class="analytics-card">
                            <h4>Generation Time</h4>
                            <p>{} seconds</p>
                        </div>
                        <div class="analytics-card">
                            <h4>Learning Objectives</h4>
                            <p>{}</p>
                        </div>
                    </div>
                """
                html_analytics = html_analytics.format(
                    round(os.path.getsize(script_file) / 1024, 2),
                    len(generated_script.splitlines()),
                    round(generation_time.total_seconds(), 2),
                    len(st.session_state.game_request["learning_objectives"])
                )
                st.markdown(html_analytics, unsafe_allow_html=True)

                # Download section
                html_download = """
                    <div class="download-section">
                        <h3>📥 Generated Files</h3>
                        <div class="download-grid">
                """
                st.markdown(html_download, unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    with open(script_file, 'r') as f:
                        script_content = f.read()
                        st.download_button(
                            "📜 Download Game Script",
                            script_content,
                            file_name=f"game_script_{timestamp}.lua",
                            mime="text/plain",
                            help="Download the generated Lua script for your game"
                        )
                        # Log analytics for script download
                        log_analytics(
                            event_type="download_script",
                            subject=st.session_state.game_request["subject"],
                            game_type=st.session_state.game_request["game_type"],
                            user=st.session_state.teacher_info.get("name", "anonymous")
                        )
                        # Show script statistics
                        html_stats = """
                            <div class="file-stats">
                                <p>📊 Script Statistics:</p>
                                <p>• Size: {} KB</p>
                                <p>• Lines: {}</p>
                                <p>• Functions: {}</p>
                                <p>• Comments: {}</p>
                            </div>
                        """
                        html_stats = html_stats.format(
                            round(len(script_content) / 1024, 2),
                            len(script_content.splitlines()),
                            len([l for l in script_content.splitlines() if "function" in l]),
                            len([l for l in script_content.splitlines() if l.strip().startswith("--")])
                        )
                        st.markdown(html_stats, unsafe_allow_html=True)

                with col2:
                    input_file_path = os.path.join("games_input", input_file)
                    if os.path.exists(input_file_path):
                        with open(input_file_path, 'r') as f:
                            input_content = f.read()
                            st.download_button(
                                "📋 Download Input Data",
                                input_content,
                                file_name=f"input_data_{timestamp}.json",
                                mime="application/json",
                                help="Download the input configuration data"
                            )
                            # Log analytics for input data download
                            log_analytics(
                                event_type="download_input",
                                subject=st.session_state.game_request["subject"],
                                game_type=st.session_state.game_request["game_type"],
                                user=st.session_state.teacher_info.get("name", "anonymous")
                            )
                            # Show input statistics
                            html_input_stats = """
                                <div class="file-stats">
                                    <p>📊 Input Statistics:</p>
                                    <p>• Size: {} KB</p>
                                    <p>• Parameters: {}</p>
                                    <p>• Game Specifics: {}</p>
                                    <p>• Learning Objectives: {}</p>
                                </div>
                            """
                            html_input_stats = html_input_stats.format(
                                round(len(input_content) / 1024, 2),
                                len(st.session_state.game_request),
                                len(st.session_state.game_request["game_specifics"]),
                                len(st.session_state.game_request["learning_objectives"])
                            )
                            st.markdown(html_input_stats, unsafe_allow_html=True)
                    else:
                        st.error(f"Input file not found: {input_file_path}. Please try regenerating the game.")

                st.markdown("</div></div>", unsafe_allow_html=True)

                # Create another game button
                if st.button("🎮 Create Another Game"):
                    st.session_state.current_step = 1
                    st.session_state.teacher_info = {}
                    st.session_state.game_request = {}
                    st.session_state.pop('generation_timestamp', None)
                    st.rerun()

            except Exception as e:
                st.error(f"An error occurred while generating the game: {e}")
                if st.button("🔄 Try Again"):
                    st.session_state.current_step = 2
                    st.session_state.pop('generation_timestamp', None)
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    # Add responsive meta tag for mobile
    st.markdown("""
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    """, unsafe_allow_html=True)

    # Enhanced onboarding/help content
    if 'onboarded' not in st.session_state:
        st.session_state.onboarded = False
    if not st.session_state.onboarded:
        st.info("""
        **Welcome to Nomics Education Platform!**
        - Create custom educational games for your students in just a few steps.
        - Use the sidebar for navigation, help, and LLM provider selection.
        - Tooltips are available on most fields—hover for more info!
        """)
        if st.button("Got it! Start using the app"):
            st.session_state.onboarded = True

    # Add tooltips to key form fields (example for Teacher Profile)
    if current_step == 1:
        st.markdown('<div class="step-container">', unsafe_allow_html=True)
        st.header("👩‍🏫 Teacher Profile")
        with st.form("teacher_info_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Your Name", value=st.session_state.teacher_info.get("name", ""), key="name_input", help="Enter your full name. This will be used for analytics and game ownership.", label_visibility="visible")
                if st.session_state.get("show_teacher_error") and not name.strip():
                    st.warning("Name is required.")
                grade_level = st.text_input("Grade Level", value=st.session_state.teacher_info.get("grade_level", ""), key="grade_input", help="E.g., 5th Grade, 8th Grade, etc.")
            with col2:
                email = st.text_input("Email", value=st.session_state.teacher_info.get("email", ""), key="email_input", help="Used for login and analytics. We never share your email.")
                school = st.text_input("School Name", value=st.session_state.teacher_info.get("school", ""), key="school_input", help="Your school or organization.", label_visibility="visible")
            # ... existing code ...

    # Add notifications for background tasks (example: script sent to Roblox Studio)
    def notify_script_sent(filename):
        st.success(f"Script `{filename}` was successfully sent to Roblox Studio via Rojo.")

    # Call notify_script_sent at the appropriate place in your workflow after script generation and transfer
    # ... existing code ...

if __name__ == "__main__":
    main() 