import streamlit as st
import random
import datetime
import pandas as pd
import os
import re
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
    }
    
    /* Mobile-friendly sizing */
    @media (max-width: 768px) {
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 0.5rem 0.8rem;
            font-size: 0.9rem;
        }
        .stButton>button {
            width: 100%;
            min-height: 50px;
            font-size: 1.1rem;
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
    }
    
    /* Spicy theme colors */
    :root {
        --spicy-orange: #ff6b35;
        --spicy-red: #e63946;
        --spicy-yellow: #f7931e;
        --spicy-dark: #1a1a2e;
    }
    
    /* Header styling */
    h1 {
        background: linear-gradient(90deg, var(--spicy-orange), var(--spicy-red));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
    }
    
    /* Primary buttons */
    .stButton>button[kind="primary"], 
    div[data-testid="stFormSubmitButton"]>button {
        background: linear-gradient(135deg, var(--spicy-orange), var(--spicy-red));
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.6rem 2rem;
        font-weight: 700;
        font-family: 'Outfit', sans-serif;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(255, 107, 53, 0.4);
    }
    
    /* Draw button special styling */
    .draw-button button {
        background: linear-gradient(135deg, #00c853, #00e676) !important;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(0, 200, 83, 0.4); }
        50% { box-shadow: 0 0 0 15px rgba(0, 200, 83, 0); }
    }
    
    /* Success message styling */
    .winner-announcement {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 3px solid var(--spicy-orange);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
        animation: celebrateIn 0.5s ease-out;
    }
    
    .winner-announcement h2 {
        color: var(--spicy-orange);
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
        background: linear-gradient(135deg, #16213e, #1a1a2e);
        border-radius: 15px;
        padding: 1.2rem;
        text-align: center;
        border: 1px solid rgba(255, 107, 53, 0.3);
    }
    
    .stat-card h3 {
        color: var(--spicy-orange);
        font-size: 2rem;
        margin: 0;
    }
    
    .stat-card p {
        color: #888;
        margin: 0.5rem 0 0 0;
        font-size: 0.9rem;
    }
    
    /* Currently playing indicator */
    .now-playing {
        background: linear-gradient(90deg, var(--spicy-orange), var(--spicy-red));
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 15px;
        text-align: center;
        font-weight: 700;
        font-size: 1.2rem;
        margin: 1rem 0;
        animation: glow 2s ease-in-out infinite;
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 10px var(--spicy-orange); }
        50% { box-shadow: 0 0 25px var(--spicy-orange), 0 0 40px var(--spicy-red); }
    }
    
    /* Table improvements for mobile */
    .stDataFrame {
        font-size: 0.85rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(26, 26, 46, 0.5);
        border-radius: 15px;
        padding: 0.3rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--spicy-orange), var(--spicy-red));
    }
    
    /* Confirmation dialog styling */
    .confirm-box {
        background: #2d2d44;
        border: 2px solid var(--spicy-red);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
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
                  pick_order INTEGER DEFAULT NULL)''')
    conn.commit()
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

def mark_dj_picked(name, pick_order):
    """Mark a DJ as picked"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE signups SET picked = 1, pick_order = ? WHERE name = ?", (pick_order, name))
    conn.commit()
    conn.close()

def unmark_dj_picked(name):
    """Undo a DJ pick"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE signups SET picked = 0, pick_order = NULL WHERE name = ?", (name,))
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
if 'confirm_delete' not in st.session_state:
    st.session_state.confirm_delete = None
if 'confirm_reset' not in st.session_state:
    st.session_state.confirm_reset = False

# --- UI Tabs ---
tab_signup, tab_entries, tab_history, tab_admin = st.tabs(["🎵 Sign-Up", "📊 Entries", "🎤 Play Order", "🔒 Admin"])

# --- Sign-Up & Lottery Tab ---
with tab_signup:
    st.title("🔥 EXTRA SPICY PLEASE")
    st.markdown("### Open Decks Lottery")
    
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
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Currently Playing indicator
    if st.session_state.current_dj:
        st.markdown(f"""
        <div class="now-playing">
            🎧 NOW PLAYING: {st.session_state.current_dj}
        </div>
        """, unsafe_allow_html=True)
    
    # Show winner announcement if just drawn
    if st.session_state.show_winner:
        st.markdown(f"""
        <div class="winner-announcement">
            <h2>🎉 {st.session_state.show_winner} 🎉</h2>
            <p style="color: #ccc; margin-top: 0.5rem;">You're up next!</p>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
        st.session_state.show_winner = None
    
    # Lottery Draw Controls
    st.subheader("🎲 Lottery Draw")
    
    col_draw1, col_draw2 = st.columns(2)
    with col_draw1:
        if st.button("🎰 Draw Next DJ", use_container_width=True, type="primary"):
            remaining_djs = [dj for dj in dj_list if dj['name'] not in st.session_state.played_djs]
            if not remaining_djs:
                st.warning("All DJs have played or none signed up.")
            else:
                # Show spinning animation placeholder
                with st.spinner("🎲 Spinning the wheel..."):
                    time.sleep(1.5)  # Suspense!
                
                now = datetime.datetime.now()
                weights = []
                for dj in remaining_djs:
                    arr_time = datetime.datetime.strptime(dj['arrival_time'], "%H:%M:%S").time()
                    elapsed = (now - datetime.datetime.combine(datetime.date.today(), arr_time)).total_seconds() / 60
                    weights.append(min(5, int(elapsed // 15) + 1))
                
                pick = random.choices(remaining_djs, weights=weights, k=1)[0]
                st.session_state.played_djs.append(pick['name'])
                st.session_state.current_dj = pick['name']
                st.session_state.show_winner = pick['name']
                
                # Update database
                mark_dj_picked(pick['name'], get_pick_count())
                st.rerun()
    
    with col_draw2:
        if st.button("🎯 Wildcard Pick", use_container_width=True):
            remaining_djs = [dj for dj in dj_list if dj['name'] not in st.session_state.played_djs]
            if not remaining_djs:
                st.warning("No DJs left for wildcard.")
            else:
                with st.spinner("🎯 Random selection..."):
                    time.sleep(1)
                
                pick = random.choice(remaining_djs)
                st.session_state.wildcard_djs.append(pick['name'])
                st.session_state.played_djs.append(pick['name'])
                st.session_state.current_dj = pick['name']
                st.session_state.show_winner = pick['name']
                
                # Update database
                mark_dj_picked(pick['name'], get_pick_count())
                st.rerun()
    
    st.markdown("---")
    
    # DJ Sign-Up Form
    st.subheader("🎧 DJ Sign-Up")
    
    with st.form("signup_form"):
        real_name = st.text_input("Your Name *", key="form_real_name", placeholder="John Smith")
        name = st.text_input("DJ Name *", key="form_name", placeholder="DJ Spicy")
        email = st.text_input("Email * (for your recording)", key="form_email", placeholder="you@email.com")
        instagram = st.text_input("Instagram", key="form_instagram", placeholder="@yourhandle")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("🔥 Sign Up", use_container_width=True, type="primary")
        with col2:
            clear = st.form_submit_button("Clear Form", use_container_width=True)
        
        if submitted:
            # Validation
            errors = []
            if not real_name.strip():
                errors.append("Name is required")
            if not name.strip():
                errors.append("DJ Name is required")
            if not email.strip():
                errors.append("Email is required")
            elif not is_valid_email(email):
                errors.append("Please enter a valid email address")
            if is_duplicate_dj(name, dj_list):
                errors.append(f"DJ Name '{name}' is already registered!")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Normalize instagram
                clean_instagram = normalize_instagram(instagram)
                
                if add_dj(real_name.strip(), name.strip(), email.strip(), clean_instagram):
                    st.success(f"✅ {name} signed up successfully!")
                    st.session_state.clear_form = True
                    st.rerun()
                else:
                    st.error("❌ Failed to sign up. DJ name may already exist.")
        
        if clear:
            st.session_state.clear_form = True
            st.rerun()

# --- Entries Tab ---
with tab_entries:
    st.subheader("📊 All Sign-Up Entries")
    
    # Reload DJ list
    dj_list = load_djs()
    
    if dj_list:
        # Summary stats
        st.markdown(f"**{len(dj_list)}** DJs signed up • **{len(st.session_state.played_djs)}** have played")
        
        # --- Summary Table ---
        summary_df = pd.DataFrame(dj_list)
        summary_df['status'] = summary_df['name'].apply(
            lambda x: '✅ Played' if x in st.session_state.played_djs else '⏳ Waiting'
        )
        summary_df['wildcard'] = summary_df['name'].apply(
            lambda x: '🎯 Yes' if x in st.session_state.wildcard_djs else ''
        )
        
        # Select and rename columns
        display_cols = ['real_name', 'name', 'instagram', 'arrival_time', 'status', 'wildcard']
        display_df = summary_df[[col for col in display_cols if col in summary_df.columns]].copy()
        display_df.columns = ['Name', 'DJ Name', 'Instagram', 'Arrival', 'Status', 'Wildcard']
        
        # Color coding
        def highlight_row(row):
            if '✅' in str(row.get('Status', '')):
                return ['background-color: #1a4d1a'] * len(row)
            return [''] * len(row)
        
        st.dataframe(
            display_df.style.apply(highlight_row, axis=1),
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        export_df = pd.DataFrame(dj_list)
        export_df['played'] = export_df['name'].apply(lambda x: 'Yes' if x in st.session_state.played_djs else 'No')
        export_df['wildcard'] = export_df['name'].apply(lambda x: 'Yes' if x in st.session_state.wildcard_djs else 'No')
        
        st.download_button(
            label="📥 Download CSV",
            data=export_df.to_csv(index=False),
            file_name=f"dj_signups_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
        
        st.markdown("---")
        
        # --- Expanders for Details and Delete ---
        st.markdown("### Individual Entries")
        for dj in dj_list:
            status_icon = "✅" if dj['name'] in st.session_state.played_djs else "⏳"
            with st.expander(f"{status_icon} {dj['name']} ({dj.get('real_name', 'N/A')})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Name:** {dj.get('real_name', 'N/A')}")
                    st.write(f"**DJ Name:** {dj['name']}")
                    st.write(f"**Instagram:** @{dj.get('instagram', 'N/A')}")
                with col2:
                    st.write(f"**Email:** {dj['email']}")
                    st.write(f"**Arrival:** {dj['arrival_time']}")
                    st.write(f"**Signed up:** {dj['timestamp']}")
                
                if dj['name'] in st.session_state.wildcard_djs:
                    st.info("🎯 This DJ was a wildcard pick!")
                
                # Delete with confirmation
                if st.session_state.confirm_delete == dj['id']:
                    st.warning(f"⚠️ Are you sure you want to delete {dj['name']}?")
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
                    if st.button(f"🗑️ Delete", key=f"delete_{dj['id']}"):
                        st.session_state.confirm_delete = dj['id']
                        st.rerun()
    else:
        st.info("No entries yet. Sign up on the first tab!")

# --- Play Order Tab ---
with tab_history:
    st.subheader("🎤 Tonight's Play Order")
    
    dj_list = load_djs()
    played_djs = [dj for dj in dj_list if dj.get('picked') and dj.get('pick_order')]
    played_djs.sort(key=lambda x: x.get('pick_order', 999))
    
    if played_djs:
        for i, dj in enumerate(played_djs, 1):
            is_current = dj['name'] == st.session_state.current_dj
            wildcard = "🎯" if dj['name'] in st.session_state.wildcard_djs else ""
            
            if is_current:
                st.markdown(f"""
                <div class="now-playing">
                    #{i} {dj['name']} {wildcard} - NOW PLAYING
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"**#{i}** {dj['name']} {wildcard}")
        
        # Undo last pick
        st.markdown("---")
        if st.button("↩️ Undo Last Pick"):
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
                st.success(f"↩️ Undid pick for {last_dj['name']}")
                st.rerun()
    else:
        st.info("No DJs have played yet. Start the lottery!")

# --- Admin Tab ---
with tab_admin:
    st.subheader("🔒 Admin Panel")
    pwd = st.text_input("Enter Admin Password", type="password")
    
    if pwd == ADMIN_PASSWORD:
        st.success("✅ Authenticated")
        
        dj_list = load_djs()
        
        # Manual DJ pick option
        unpicked_djs = [dj['name'] for dj in dj_list if dj['name'] not in st.session_state.played_djs]
        if unpicked_djs:
            manual_pick = st.selectbox("Manually pick a DJ (mark as played)", unpicked_djs, key="manual_pick_select")
            if st.button("✅ Mark as Picked", type="primary"):
                st.session_state.played_djs.append(manual_pick)
                st.session_state.current_dj = manual_pick
                mark_dj_picked(manual_pick, get_pick_count())
                st.success(f"✅ {manual_pick} marked as picked.")
                st.rerun()
        else:
            st.info("All DJs have been picked!")
        
        st.markdown("---")
        
        # Clear current DJ indicator
        if st.session_state.current_dj:
            if st.button("🔄 Clear 'Now Playing' indicator"):
                st.session_state.current_dj = None
                st.rerun()
        
        st.markdown("---")
        
        # Reset with confirmation
        if st.session_state.confirm_reset:
            st.error("⚠️ This will delete ALL signups and reset everything!")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("Yes, Reset Everything", type="primary"):
                    reset_all_data()
                    st.session_state.played_djs = []
                    st.session_state.wildcard_djs = []
                    st.session_state.current_dj = None
                    st.session_state.confirm_reset = False
                    st.success("✅ All data has been reset.")
                    st.rerun()
            with col_no:
                if st.button("Cancel"):
                    st.session_state.confirm_reset = False
                    st.rerun()
        else:
            if st.button("🔄 Reset All Data"):
                st.session_state.confirm_reset = True
                st.rerun()
        
        st.markdown("---")
        st.caption("💡 Set ADMIN_PASSWORD environment variable to change the password.")
    elif pwd:
        st.error("❌ Incorrect password")
    else:
        st.info("Enter the password to access admin controls.")

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8rem;">
    🔥 EXTRA SPICY PLEASE • Open Decks Lottery System<br>
    <span style="font-size: 0.7rem;">Tip: Add to home screen on mobile for app-like experience!</span>
</div>
""", unsafe_allow_html=True)
