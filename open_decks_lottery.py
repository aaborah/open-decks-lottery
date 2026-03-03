import streamlit as st
import random
import datetime
import pandas as pd
import os
import re
import subprocess
import sys
import sqlite3
import time

# --- Configuration ---
st.set_page_config(
    page_title="EXTRA SPICY PLEASE Open Decks",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Use environment variable for password (fallback for development)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "spicy2024")
DB_FILE = "dj_signups.db"

# --- Mobile-Friendly CSS ---
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&display=swap');
    
    /* Global styling */
    .stApp {
        font-family: 'Outfit', sans-serif;
        color: var(--text);
        background-color: var(--black);
    }

    body,
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"] {
        background-color: var(--black);
        color: var(--text);
    }

    /* Hide Streamlit toolbar/footer branding */
    header[data-testid="stHeader"] {
        display: none;
    }
    [data-testid="stToolbar"] {
        display: none;
    }
    [data-testid="stDecoration"] {
        display: none;
    }
    footer {
        display: none;
    }

    a {
        color: var(--text);
    }

    h1, h2, h3, h4, h5, h6,
    p, label, span, li {
        color: var(--text);
    }

    .stCaption {
        color: var(--text-muted) !important;
    }

    /* Inputs */
    input,
    textarea,
    select {
        background-color: var(--black-2) !important;
        color: var(--text) !important;
        border: 1px solid var(--red) !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="select"] > div {
        background-color: var(--black-2) !important;
        border: 1px solid var(--red) !important;
        color: var(--text) !important;
    }

    div[data-baseweb="select"] span {
        color: var(--text) !important;
    }

    hr {
        border-color: var(--black-3);
    }

    input::placeholder,
    textarea::placeholder {
        color: var(--text-muted) !important;
    }

    /* Alerts */
    div[data-testid="stAlert"] {
        background-color: var(--black-2) !important;
        color: var(--text) !important;
        border: 1px solid var(--red) !important;
    }
    div[data-testid="stAlert"] p {
        color: var(--text) !important;
    }
    
    /* Focus styles for keyboard users */
    button:focus-visible,
    input:focus-visible,
    textarea:focus-visible,
    select:focus-visible {
        outline: 3px solid var(--text);
        outline-offset: 2px;
    }
    
    /* Mobile-friendly sizing */
    @media (max-width: 768px) {
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            flex-wrap: wrap;
            row-gap: 0.4rem;
            justify-content: center;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 0.6rem 1rem;
            font-size: 0.95rem;
        }
        .stButton>button {
            min-height: 44px;
            font-size: 1.05rem;
        }
        .stTextInput input {
            font-size: 16px !important; /* Prevents zoom on iOS */
            min-height: 45px;
        }
        h1 {
            font-size: 1.8rem !important;
        }
        h2, .stSubheader {
            font-size: 1.3rem !important;
        }
        .stDataFrame {
            font-size: 1rem;
        }
        /* Stack Streamlit columns on small screens */
        div[data-testid="stHorizontalBlock"] {
            flex-direction: column;
        }
        div[data-testid="stColumn"] {
            width: 100% !important;
        }
    }
    
    /* Theme colors */
    :root {
        --red: #c00000;
        --red-dark: #8b0000;
        --black: #0b0b0b;
        --black-2: #111111;
        --black-3: #1a1a1a;
        --text: #ffffff;
        --text-muted: rgba(255, 255, 255, 0.85);
    }
    
    /* Header styling */
    h1 {
        color: var(--text);
        font-weight: 800;
    }
    
    @media (forced-colors: active) {
        h1 {
            background: none;
            -webkit-text-fill-color: CanvasText;
            color: CanvasText;
        }
    }
    
    /* Default buttons */
    .stButton>button {
        background: var(--black-2);
        color: var(--text);
        border: 1px solid var(--black-3);
        border-radius: 12px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        line-height: 1.2;
    }

    div[data-testid="stDownloadButton"]>button {
        background: var(--black-2);
        color: var(--text);
        border: 1px solid var(--black-3);
        border-radius: 12px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        line-height: 1.2;
    }

    /* Primary buttons */
    .stButton>button[kind="primary"] {
        background: var(--red);
        color: var(--text);
        border: 1px solid var(--red);
        border-radius: 12px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        font-family: 'Outfit', sans-serif;
        transition: all 0.3s ease;
        text-transform: none;
        letter-spacing: 0;
    }

    .stButton>button:hover {
        background: var(--black-3);
        border-color: var(--black-3);
    }

    div[data-testid="stDownloadButton"]>button:hover {
        background: var(--black-3);
        border-color: var(--black-3);
    }

    .stButton>button[kind="primary"]:hover {
        background: var(--red-dark);
        border-color: var(--red-dark);
    }

    div[data-testid="stFormSubmitButton"]>button {
        width: auto;
        min-width: 140px;
    }
    
    /* Draw button special styling */
    .draw-button button {
        background: var(--red) !important;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(192, 0, 0, 0.4); }
        50% { box-shadow: 0 0 0 15px rgba(192, 0, 0, 0); }
    }
    
    /* Success message styling */
    .winner-announcement {
        background: var(--black-2);
        border: 2px solid var(--red);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
        animation: celebrateIn 0.5s ease-out;
    }
    
    .winner-announcement h2 {
        color: var(--text);
        font-size: 2rem;
        margin: 0;
    }
    
    @keyframes celebrateIn {
        0% { transform: scale(0.5); opacity: 0; }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); opacity: 1; }
    }
    
    /* Stats cards */
    .stat-card {
        background: var(--black-2);
        border-radius: 15px;
        padding: 1.2rem;
        text-align: center;
        border: 1px solid var(--red);
    }
    
    .stat-card h3 {
        color: var(--text);
        font-size: 2rem;
        margin: 0;
    }
    
    .stat-card p {
        color: var(--text-muted);
        margin: 0.5rem 0 0 0;
        font-size: 0.9rem;
    }
    
    /* Currently playing indicator */
    .now-playing {
        background: var(--red);
        color: var(--text);
        padding: 1rem 1.5rem;
        border-radius: 15px;
        text-align: center;
        font-weight: 700;
        font-size: 1.2rem;
        margin: 1rem 0;
    }
    
    @media (prefers-reduced-motion: reduce) {
        * {
            animation: none !important;
            transition: none !important;
            scroll-behavior: auto !important;
        }
    }
    
    /* Table improvements for mobile */
    .stDataFrame {
        font-size: 0.95rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--black-2);
        border-radius: 15px;
        padding: 0.5rem;
        gap: 0.6rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: var(--black-3);
        color: var(--text);
        border: 1px solid var(--black-3);
        border-radius: 10px;
        font-weight: 600;
        padding: 0.6rem 1.1rem;
        line-height: 1.2;
        white-space: nowrap;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--red);
        border-color: var(--red);
        color: var(--text);
    }
    
    /* Confirmation dialog styling */
    .confirm-box {
        background: var(--black-2);
        border: 2px solid var(--red);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }

    /* Hide "Press Enter to submit" helper text in forms */
    div[data-testid="stForm"] .stCaption,
    div[data-testid="stForm"] small,
    div[data-testid="stForm"] [data-testid="stCaptionContainer"],
    div[data-testid="stFormSubmitButton"] + div,
    .stForm small,
    [data-testid="stForm"] div:has(> small) {
        display: none !important;
    }

    /* Dataframe colors */
    div[data-testid="stDataFrame"] {
        background-color: var(--black-2);
        color: var(--text);
    }
    div[data-testid="stDataFrame"] table,
    div[data-testid="stDataFrame"] thead,
    div[data-testid="stDataFrame"] tbody,
    div[data-testid="stDataFrame"] tr,
    div[data-testid="stDataFrame"] th,
    div[data-testid="stDataFrame"] td {
        color: var(--text) !important;
        background-color: var(--black-2);
    }
    div[data-testid="stDataFrame"] tr:nth-child(even) td {
        background-color: var(--black-3);
    }
    
    /* Entry card delete button styling */
    .entry-delete-btn {
        min-width: 44px !important;
        min-height: 44px !important;
        padding: 0.5rem !important;
        font-size: 1.2rem !important;
    }
    
    /* Align delete button with expander */
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child {
        display: flex;
        align-items: flex-start;
        padding-top: 0.25rem;
    }
    
    /* On mobile, keep columns side by side for entry cards */
    @media (max-width: 768px) {
        .entries-row div[data-testid="stHorizontalBlock"] {
            flex-direction: row !important;
        }
        .entries-row div[data-testid="stColumn"]:first-child {
            flex: 5 !important;
        }
        .entries-row div[data-testid="stColumn"]:last-child {
            flex: 1 !important;
            max-width: 60px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email.strip()) is not None

def normalize_instagram(handle):
    """Normalize Instagram handle - strip @ and whitespace"""
    return handle.strip().lstrip('@')

def is_duplicate_dj(dj_name, existing_list):
    """Check if DJ name already exists (case-insensitive)"""
    for dj in existing_list:
        if dj['name'].lower().strip() == dj_name.lower().strip():
            return True
    return False

def is_absent(dj):
    """Return True if DJ is marked absent."""
    return bool(dj.get('absent'))

def is_picked(dj, played_djs):
    """Return True if DJ is already picked."""
    return bool(dj.get('picked')) or dj['name'] in played_djs

def is_eligible_for_draw(dj, played_djs):
    """Return True if DJ can be included in the next draw."""
    return (not is_absent(dj)) and (not is_picked(dj, played_djs))

def matches_admin_search(dj, query):
    """Return True if DJ matches admin search query."""
    if not query:
        return True
    query = query.strip().lower()
    if not query:
        return True
    instagram = dj.get('instagram', '')
    fields = [
        dj.get('name', ''),
        dj.get('real_name', ''),
        dj.get('email', ''),
        instagram,
        f"@{instagram}" if instagram else "",
    ]
    return any(query in str(field).lower() for field in fields)

def copy_to_clipboard(text):
    """Copy text to the system clipboard."""
    if not text:
        return False
    try:
        if sys.platform == "darwin":
            subprocess.run(["pbcopy"], input=text, text=True, check=False)
            return True
    except Exception:
        pass
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        return False

def show_toast(message):
    """Show a non-blocking toast if available."""
    if hasattr(st, "toast"):
        st.toast(message)
    else:
        st.success(message)

# --- Database Functions ---
def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS signups
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  real_name TEXT NOT NULL,
                  name TEXT UNIQUE NOT NULL,
                  email TEXT NOT NULL,
                  instagram TEXT,
                  arrival_time TEXT NOT NULL,
                  timestamp TEXT NOT NULL,
                  picked INTEGER DEFAULT 0,
                  pick_order INTEGER DEFAULT NULL,
                  absent INTEGER DEFAULT 0,
                  play_time TEXT DEFAULT NULL)''')
    conn.commit()
    conn.close()

def ensure_absent_column():
    """Add absent column if it does not exist (backward compatible)."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE signups ADD COLUMN absent INTEGER DEFAULT 0")
        conn.commit()
    except sqlite3.OperationalError:
        pass
    finally:
        conn.close()

def ensure_play_time_column():
    """Add play_time column if it does not exist (backward compatible)."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE signups ADD COLUMN play_time TEXT DEFAULT NULL")
        conn.commit()
    except sqlite3.OperationalError:
        pass
    finally:
        conn.close()

def load_djs():
    """Load all DJs from database"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM signups ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_dj(real_name, name, email, instagram):
    """Add a new DJ to database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    arrival_str = datetime.datetime.now().strftime("%H:%M:%S")
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        c.execute("""INSERT INTO signups (real_name, name, email, instagram, arrival_time, timestamp)
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (real_name, name, email, instagram, arrival_str, timestamp_str))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def mark_dj_picked(name, pick_order, play_time=None):
    """Mark a DJ as picked with optional play time"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE signups SET picked = 1, pick_order = ?, play_time = ? WHERE name = ?", (pick_order, play_time, name))
    conn.commit()
    conn.close()

def unmark_dj_picked(name):
    """Undo a DJ pick"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE signups SET picked = 0, pick_order = NULL WHERE name = ?", (name,))
    conn.commit()
    conn.close()

def set_dj_absent(dj_id, is_absent_flag):
    """Set DJ absent status."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE signups SET absent = ? WHERE id = ?", (1 if is_absent_flag else 0, dj_id))
    conn.commit()
    conn.close()

def delete_dj(dj_id):
    """Delete a DJ from database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM signups WHERE id = ?", (dj_id,))
    conn.commit()
    conn.close()

def reset_all_data():
    """Reset all data in database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM signups")
    conn.commit()
    conn.close()

def get_pick_count():
    """Get the current pick count for ordering"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT MAX(pick_order) FROM signups")
    result = c.fetchone()[0]
    conn.close()
    return (result or 0) + 1

# --- Migrate from CSV if exists ---
def migrate_from_csv():
    """One-time migration from CSV to SQLite"""
    csv_file = "dj_signups.csv"
    if os.path.exists(csv_file) and os.path.exists(DB_FILE):
        # Check if DB is empty
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM signups")
        count = c.fetchone()[0]
        conn.close()
        
        if count == 0:
            df = pd.read_csv(csv_file)
            conn = sqlite3.connect(DB_FILE)
            for _, row in df.iterrows():
                try:
                    conn.execute("""INSERT INTO signups 
                                    (real_name, name, email, instagram, arrival_time, timestamp, picked)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                                 (row.get('real_name', ''), row['name'], row['email'],
                                  row.get('instagram', ''), row['arrival_time'],
                                  row['timestamp'], int(row.get('picked', False))))
                except:
                    pass
            conn.commit()
            conn.close()
            # Rename old CSV as backup
            os.rename(csv_file, csv_file + ".bak")

# Initialize database
init_db()
ensure_absent_column()
ensure_play_time_column()
migrate_from_csv()

# --- Clear form session state before any widgets are created ---
if st.session_state.get("clear_form", False):
    st.session_state.form_real_name = ""
    st.session_state.form_name = ""
    st.session_state.form_email = ""
    st.session_state.form_instagram = ""
    st.session_state.clear_form = False
    st.rerun()

# Initialize session state for form fields
for field in ['form_real_name', 'form_name', 'form_email', 'form_instagram']:
    if field not in st.session_state:
        st.session_state[field] = ""

# Load DJ list from database
dj_list = load_djs()

# Track played DJs and wildcard picks from database
if 'played_djs' not in st.session_state:
    st.session_state.played_djs = [dj['name'] for dj in dj_list if dj.get('picked')]
if 'wildcard_djs' not in st.session_state:
    st.session_state.wildcard_djs = []
if 'current_dj' not in st.session_state:
    st.session_state.current_dj = None
if 'show_winner' not in st.session_state:
    st.session_state.show_winner = None
if 'pending_pick' not in st.session_state:
    st.session_state.pending_pick = None  # Stores DJ awaiting time confirmation
if 'pending_pick_is_wildcard' not in st.session_state:
    st.session_state.pending_pick_is_wildcard = False
if 'confirm_delete' not in st.session_state:
    st.session_state.confirm_delete = None
if 'confirm_reset' not in st.session_state:
    st.session_state.confirm_reset = False
if 'reduce_motion' not in st.session_state:
    st.session_state.reduce_motion = False

if st.session_state.reduce_motion:
    st.markdown("""
    <style>
        * {
            animation: none !important;
            transition: none !important;
            scroll-behavior: auto !important;
        }
    </style>
    """, unsafe_allow_html=True)

# --- UI Tabs ---
tab_signup, tab_entries, tab_history, tab_admin = st.tabs(["Sign Up", "Entries", "Play Order", "Admin"])

# --- Sign-Up & Lottery Tab ---
with tab_signup:
    st.title("EXTRA SPICY PLEASE")
    st.markdown("### Open Decks Lottery")
    
    # DJ Sign-Up Form
    st.subheader("DJ Sign-Up")
    
    with st.form("signup_form"):
        real_name = st.text_input("Your Name *", key="form_real_name", placeholder="John Smith")
        real_name_error = st.empty()
        name = st.text_input("DJ Name *", key="form_name", placeholder="DJ ABCXYZ")
        name_error = st.empty()
        email = st.text_input("Email *", key="form_email", placeholder="you@email.com")
        email_error = st.empty()
        instagram = st.text_input("Instagram *", key="form_instagram", placeholder="@yourhandle")
        instagram_error = st.empty()
        
        submitted = st.form_submit_button("Sign Up", type="primary")
        clear = st.form_submit_button("Clear Form")
        
        if submitted:
            has_error = False
            if not real_name.strip():
                real_name_error.error("Name is required")
                has_error = True
            if not name.strip():
                name_error.error("DJ name is required")
                has_error = True
            elif is_duplicate_dj(name, dj_list):
                name_error.error(f"DJ name '{name}' is already registered!")
                has_error = True
            if not email.strip():
                email_error.error("Email is required")
                has_error = True
            elif not is_valid_email(email):
                email_error.error("Enter a valid email address")
                has_error = True
            if not instagram.strip():
                instagram_error.error("Instagram is required")
                has_error = True
            
            if not has_error:
                # Normalize instagram
                clean_instagram = normalize_instagram(instagram)
                
                if add_dj(real_name.strip(), name.strip(), email.strip(), clean_instagram):
                    st.success(f"{name} signed up successfully.")
                    st.session_state.clear_form = True
                    time.sleep(3)
                    st.rerun()
                else:
                    st.error("Failed to sign up. DJ name may already exist.")
        
        if clear:
            st.session_state.clear_form = True
            st.rerun()

# --- Entries Tab ---
with tab_entries:
    st.subheader("All Sign-Up Entries")
    
    # Reload DJ list
    dj_list = load_djs()
    
    if dj_list:
        # Summary stats
        st.markdown(f"**{len(dj_list)}** DJs signed up - **{len(st.session_state.played_djs)}** have played")
        
        # Download button
        export_df = pd.DataFrame(dj_list)
        export_df['played'] = export_df['name'].apply(lambda x: 'Yes' if x in st.session_state.played_djs else 'No')
        export_df['wildcard'] = export_df['name'].apply(lambda x: 'Yes' if x in st.session_state.wildcard_djs else 'No')
        
        st.download_button(
            label="Download CSV",
            data=export_df.to_csv(index=False),
            file_name=f"dj_signups_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
        
        with st.expander("Summary table (optional)", expanded=False):
            summary_df = pd.DataFrame(dj_list)
            summary_df['status'] = summary_df['name'].apply(
                lambda x: 'Played' if x in st.session_state.played_djs else 'Waiting'
            )
            summary_df['wildcard'] = summary_df['name'].apply(
                lambda x: 'Yes' if x in st.session_state.wildcard_djs else ''
            )
            
            # Select and rename columns
            display_cols = ['real_name', 'name', 'instagram', 'arrival_time', 'status', 'wildcard']
            display_df = summary_df[[col for col in display_cols if col in summary_df.columns]].copy()
            display_df.columns = ['Name', 'DJ Name', 'Instagram', 'Arrival', 'Status', 'Wildcard']
            
            # Color coding
            def highlight_row(row):
                if 'Played' in str(row.get('Status', '')):
                    return ['background-color: #2b0000; color: #ffffff'] * len(row)
                return [''] * len(row)
            
            st.dataframe(
                display_df.style.apply(highlight_row, axis=1),
                use_container_width=True,
                hide_index=True
            )
        
        st.markdown("---")
        
        # --- Entry Cards with Delete ---
        st.markdown("### Entries")
        st.markdown('<div class="entries-row">', unsafe_allow_html=True)
        
        for dj in dj_list:
            status_label = "Played" if dj['name'] in st.session_state.played_djs else "Waiting"
            instagram_display = f"@{dj.get('instagram')}" if dj.get('instagram') else ""
            wildcard_badge = " (Wildcard)" if dj['name'] in st.session_state.wildcard_djs else ""
            
            # Delete confirmation state
            if st.session_state.confirm_delete == dj['id']:
                st.markdown(f"""
                <div class="confirm-box">
                    <p style="margin: 0 0 1rem 0;">Delete <strong>{dj['name']}</strong>?</p>
                </div>
                """, unsafe_allow_html=True)
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("Yes, Delete", key=f"confirm_del_{dj['id']}", type="primary"):
                        if dj['name'] in st.session_state.played_djs:
                            st.session_state.played_djs.remove(dj['name'])
                        if dj['name'] in st.session_state.wildcard_djs:
                            st.session_state.wildcard_djs.remove(dj['name'])
                        delete_dj(dj['id'])
                        st.session_state.confirm_delete = None
                        st.rerun()
                with col_no:
                    if st.button("Cancel", key=f"cancel_del_{dj['id']}"):
                        st.session_state.confirm_delete = None
                        st.rerun()
            else:
                # Entry card with inline delete
                col_info, col_delete = st.columns([5, 1])
                with col_info:
                    with st.expander(f"{status_label}: {dj['name']} ({dj.get('real_name', 'N/A')}){wildcard_badge}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Name:** {dj.get('real_name', 'N/A')}")
                            st.write(f"**DJ Name:** {dj['name']}")
                            st.write(f"**Instagram:** {instagram_display or 'N/A'}")
                        with col2:
                            st.write(f"**Email:** {dj['email']}")
                            st.write(f"**Arrival:** {dj['arrival_time']}")
                            st.write(f"**Signed up:** {dj['timestamp']}")
                        
                        if dj['name'] in st.session_state.wildcard_djs:
                            st.info("This DJ was a wildcard pick.")
                with col_delete:
                    if st.button("🗑️", key=f"delete_{dj['id']}", help="Delete this entry"):
                        st.session_state.confirm_delete = dj['id']
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No entries yet. Sign up on the first tab.")

# --- Play Order Tab ---
with tab_history:
    st.subheader("Tonight's Play Order")
    
    dj_list = load_djs()
    played_djs = [dj for dj in dj_list if dj.get('picked') and dj.get('pick_order')]
    played_djs.sort(key=lambda x: x.get('pick_order', 999))
    
    if played_djs:
        # Selected Players table
        schedule_data = []
        for i, dj in enumerate(played_djs, 1):
            wildcard = "Yes" if dj['name'] in st.session_state.wildcard_djs else ""
            play_time = dj.get('play_time', '-')
            status = "NOW PLAYING" if dj['name'] == st.session_state.current_dj else "Played" if i < len(played_djs) else "Up Next"
            schedule_data.append({
                "#": i,
                "DJ Name": dj['name'],
                "Time": play_time if play_time else "-",
                "Wildcard": wildcard,
                "Status": status
            })
        
        schedule_df = pd.DataFrame(schedule_data)
        st.dataframe(schedule_df, use_container_width=True, hide_index=True)
        
        # Undo last pick
        st.markdown("---")
        if st.button("Undo Last Pick"):
            if played_djs:
                last_dj = played_djs[-1]
                unmark_dj_picked(last_dj['name'])
                if last_dj['name'] in st.session_state.played_djs:
                    st.session_state.played_djs.remove(last_dj['name'])
                if last_dj['name'] in st.session_state.wildcard_djs:
                    st.session_state.wildcard_djs.remove(last_dj['name'])
                # Set current DJ to previous one
                if len(played_djs) > 1:
                    st.session_state.current_dj = played_djs[-2]['name']
                else:
                    st.session_state.current_dj = None
                st.success(f"Undid pick for {last_dj['name']}")
                st.rerun()
    else:
        st.info("No DJs have played yet. Start the lottery!")

# --- Admin Tab ---
with tab_admin:
    st.subheader("Admin Panel")
    pwd = st.text_input("Enter Admin Password", type="password")
    
    if pwd == ADMIN_PASSWORD:
        st.success("Authenticated")
        
        dj_list = load_djs()

        with st.expander("Display options"):
            st.checkbox(
                "Reduce motion effects",
                key="reduce_motion",
                help="Disable animations and celebration effects for a calmer experience."
            )

        # Stats row
        total_djs = len(dj_list)
        played_count = len(st.session_state.played_djs)
        remaining = total_djs - played_count
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <h3>{total_djs}</h3>
                <p>Total Signed Up</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <h3>{played_count}</h3>
                <p>Already Played</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <h3>{remaining}</h3>
                <p>Still Waiting</p>
            </div>
            """, unsafe_allow_html=True)

        # Currently Playing indicator
        if st.session_state.current_dj:
            st.markdown(f"""
            <div class="now-playing" role="status" aria-live="polite" aria-atomic="true">
                NOW PLAYING: {st.session_state.current_dj}
            </div>
            """, unsafe_allow_html=True)
        
        # Show winner announcement if just drawn
        if st.session_state.show_winner:
            st.markdown(f"""
            <div class="winner-announcement" role="status" aria-live="polite" aria-atomic="true">
                <h2>Next up: {st.session_state.show_winner}</h2>
                <p style="color: var(--text-muted); margin-top: 0.5rem;">You're up next!</p>
            </div>
            """, unsafe_allow_html=True)
            st.session_state.show_winner = None
        
        st.markdown("---")
        st.subheader("Lottery Draw")
        
        # Show pending pick confirmation with time picker
        if st.session_state.pending_pick:
            pending_dj = st.session_state.pending_pick
            wildcard_text = " (Wildcard)" if st.session_state.pending_pick_is_wildcard else ""
            
            st.markdown(f"""
            <div class="winner-announcement" role="status" aria-live="polite" aria-atomic="true">
                <h2>Next up: {pending_dj['name']}{wildcard_text}</h2>
                <p style="color: var(--text-muted); margin-top: 0.5rem;">Set their play time to confirm</p>
            </div>
            """, unsafe_allow_html=True)
            
            col_time, col_confirm = st.columns([2, 1])
            with col_time:
                play_time = st.time_input(
                    "Play Time",
                    value=datetime.datetime.now().time(),
                    key="pending_play_time"
                )
            with col_confirm:
                st.write("")  # Spacer for alignment
                if st.button("Confirm", type="primary", use_container_width=True, key="confirm_pick"):
                    play_time_str = play_time.strftime("%I:%M %p")
                    
                    # Mark as picked with time
                    if st.session_state.pending_pick_is_wildcard:
                        st.session_state.wildcard_djs.append(pending_dj['name'])
                    st.session_state.played_djs.append(pending_dj['name'])
                    st.session_state.current_dj = pending_dj['name']
                    st.session_state.show_winner = pending_dj['name']
                    
                    mark_dj_picked(pending_dj['name'], get_pick_count(), play_time_str)
                    
                    # Clear pending state
                    st.session_state.pending_pick = None
                    st.session_state.pending_pick_is_wildcard = False
                    st.rerun()
            
            if st.button("Cancel", use_container_width=True, key="cancel_pick"):
                st.session_state.pending_pick = None
                st.session_state.pending_pick_is_wildcard = False
                st.rerun()
        else:
            col_draw1, col_draw2 = st.columns(2)
            with col_draw1:
                if st.button("Draw Next DJ", use_container_width=True, type="primary"):
                    eligible_djs = [dj for dj in dj_list if is_eligible_for_draw(dj, st.session_state.played_djs)]
                    if not eligible_djs:
                        st.warning("No eligible DJs left to draw.")
                    else:
                        with st.spinner("Drawing..."):
                            time.sleep(1.5)
                        
                        now = datetime.datetime.now()
                        weights = []
                        for dj in eligible_djs:
                            arr_time = datetime.datetime.strptime(dj['arrival_time'], "%H:%M:%S").time()
                            elapsed = (now - datetime.datetime.combine(datetime.date.today(), arr_time)).total_seconds() / 60
                            # Ensure weight is always between 1 and 5
                            weights.append(max(1, min(5, int(elapsed // 15) + 1)))
                        
                        pick = random.choices(eligible_djs, weights=weights, k=1)[0]
                        st.session_state.pending_pick = pick
                        st.session_state.pending_pick_is_wildcard = False
                        st.rerun()
            
            with col_draw2:
                if st.button("Wildcard Pick", use_container_width=True):
                    eligible_djs = [dj for dj in dj_list if is_eligible_for_draw(dj, st.session_state.played_djs)]
                    if not eligible_djs:
                        st.warning("No eligible DJs left for wildcard.")
                    else:
                        with st.spinner("Selecting..."):
                            time.sleep(1)
                        
                        pick = random.choice(eligible_djs)
                        st.session_state.pending_pick = pick
                        st.session_state.pending_pick_is_wildcard = True
                        st.rerun()
        
        st.markdown("---")
        
        st.subheader("DJ Entries")
        admin_search = st.text_input(
            "Search DJs",
            placeholder="Search by DJ name, real name, email, Instagram",
            key="admin_search"
        )
        filtered_djs = [dj for dj in dj_list if matches_admin_search(dj, admin_search)]

        if not filtered_djs:
            st.info("No DJs match your search.")
        else:
            display_rows = []
            dj_meta = {}
            label_lookup = {}

            for dj in filtered_djs:
                picked = is_picked(dj, st.session_state.played_djs)
                absent = is_absent(dj)
                eligible = is_eligible_for_draw(dj, st.session_state.played_djs)

                pick_order = dj.get('pick_order') if picked else "-"
                dj_name = dj.get('name') or "-"
                real_name = dj.get('real_name') or "-"
                email_value = dj.get('email') or "-"
                instagram = dj.get('instagram', '')
                instagram_display = f"@{instagram}" if instagram else "-"
                arrival_time = dj.get('arrival_time') or "-"
                signup_time = dj.get('timestamp') or "-"

                if picked and absent:
                    status_label = "Picked / Absent"
                elif picked:
                    status_label = "Picked"
                elif absent:
                    status_label = "Absent"
                else:
                    status_label = "Eligible"

                attendance_label = "Absent" if absent else "Present"

                display_rows.append({
                    "Pick Order": pick_order,
                    "DJ Name": dj_name,
                    "Real Name": real_name,
                    "Email": email_value,
                    "Instagram": instagram_display,
                    "Status": status_label,
                    "Attendance": attendance_label,
                    "Arrival": arrival_time,
                    "Signed up": signup_time,
                })

                label_lookup[dj['id']] = f"{dj_name} ({real_name}) - {status_label}"
                dj_meta[dj['id']] = {
                    "eligible": eligible,
                    "absent": absent,
                    "pick_order": pick_order,
                    "dj_name": dj_name,
                    "real_name": real_name,
                    "email_value": email_value,
                    "instagram_display": instagram_display,
                    "status_label": status_label,
                    "attendance_label": attendance_label,
                }

            display_df = pd.DataFrame(display_rows)
            if not display_df.empty:
                st.dataframe(display_df, use_container_width=True, hide_index=True)

            st.markdown("### Actions")
            selected_id = st.selectbox(
                "Select DJ",
                options=[dj['id'] for dj in filtered_djs],
                format_func=lambda dj_id: label_lookup.get(dj_id, str(dj_id)),
                key="admin_action_select"
            )

            selected_dj = next((dj for dj in filtered_djs if dj['id'] == selected_id), None)
            selected_meta = dj_meta.get(selected_id, {})

            if selected_dj:
                copy_payload = (
                    f"Pick Order: {selected_meta.get('pick_order', '-')} | "
                    f"DJ Name: {selected_meta.get('dj_name', '-')} | "
                    f"Real Name: {selected_meta.get('real_name', '-')} | "
                    f"Email: {selected_meta.get('email_value', '-')} | "
                    f"Instagram: {selected_meta.get('instagram_display', '-')} | "
                    f"Status: {selected_meta.get('status_label', '-')} | "
                    f"Attendance: {selected_meta.get('attendance_label', '-')}"
                )

                action_cols = st.columns(3)
                with action_cols[0]:
                    if st.button(
                        "Pick",
                        key=f"pick_{selected_dj['id']}",
                        disabled=not selected_meta.get("eligible", False),
                        use_container_width=True
                    ):
                        if selected_dj['name'] not in st.session_state.played_djs:
                            st.session_state.played_djs.append(selected_dj['name'])
                        st.session_state.current_dj = selected_dj['name']
                        mark_dj_picked(selected_dj['name'], get_pick_count())
                        st.success(f"{selected_dj['name']} marked as picked.")
                        st.rerun()
                with action_cols[1]:
                    absent_label = "Mark present" if selected_meta.get("absent") else "Mark absent"
                    if st.button(absent_label, key=f"absent_{selected_dj['id']}", use_container_width=True):
                        set_dj_absent(selected_dj['id'], not selected_meta.get("absent"))
                        st.rerun()
                with action_cols[2]:
                    if st.button("Copy", key=f"copy_{selected_dj['id']}", use_container_width=True):
                        if copy_to_clipboard(copy_payload):
                            show_toast("Copied row to clipboard.")
                        else:
                            st.warning("Copy failed. Please copy manually.")
        
        st.markdown("---")
        
        # Clear current DJ indicator
        if st.session_state.current_dj:
            if st.button("Clear Now Playing indicator"):
                st.session_state.current_dj = None
                st.rerun()
        
        st.markdown("---")
        
        # Reset with confirmation
        if st.session_state.confirm_reset:
            st.error("This will delete ALL signups and reset everything!")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("Yes, Reset Everything", type="primary"):
                    reset_all_data()
                    st.session_state.played_djs = []
                    st.session_state.wildcard_djs = []
                    st.session_state.current_dj = None
                    st.session_state.confirm_reset = False
                    st.success("All data has been reset.")
                    st.rerun()
            with col_no:
                if st.button("Cancel"):
                    st.session_state.confirm_reset = False
                    st.rerun()
        else:
            if st.button("Reset All Data"):
                st.session_state.confirm_reset = True
                st.rerun()
        
        st.markdown("---")
        st.caption("Set ADMIN_PASSWORD environment variable to change the password.")
    elif pwd:
        st.error("Incorrect password")
    else:
        st.info("Enter the password to access admin controls.")

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--text-muted); font-size: 0.8rem;">
    EXTRA SPICY PLEASE - Open Decks Lottery System<br>
    <span style="font-size: 0.7rem;">Tip: Add to home screen on mobile for app-like experience!</span>
</div>
""", unsafe_allow_html=True)
