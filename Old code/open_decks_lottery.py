import streamlit as st
import random
import datetime
import pandas as pd
import os

# --- Configuration ---
st.set_page_config(page_title="EXTRA SPICY PLEASE Open Decks", layout="centered")
CSV_FILE = "dj_signups.csv"
ADMIN_PASSWORD = "spicy2024"

# --- Clear form session state before any widgets are created ---
if st.session_state.get("clear_form", False):
    st.session_state.form_real_name = ""
    st.session_state.form_name = ""
    st.session_state.form_email = ""
    st.session_state.form_instagram = ""
    st.session_state.clear_form = False
    st.rerun()
    st.stop()

# Initialize session state for form fields
if 'form_real_name' not in st.session_state:
    st.session_state.form_real_name = ""
if 'form_name' not in st.session_state:
    st.session_state.form_name = ""
if 'form_email' not in st.session_state:
    st.session_state.form_email = ""
if 'form_instagram' not in st.session_state:
    st.session_state.form_instagram = ""

# --- Load or Initialize Data ---
if os.path.exists(CSV_FILE):
    df_existing = pd.read_csv(CSV_FILE)
    if 'picked' not in df_existing.columns:
        df_existing['picked'] = False
    df_existing["arrival_time"] = pd.to_datetime(df_existing["arrival_time"]).dt.strftime("%H:%M:%S")
    df_existing["timestamp"] = pd.to_datetime(df_existing["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    dj_list = df_existing.to_dict(orient="records")
else:
    dj_list = []

# Track played DJs and wildcard picks
if 'played_djs' not in st.session_state:
    # Load picked DJs from CSV
    st.session_state.played_djs = [dj['name'] for dj in dj_list if 'picked' in dj and dj['picked'] is True or dj['picked'] == True]
if 'wildcard_djs' not in st.session_state:
    st.session_state.wildcard_djs = []  # names drawn via wildcard

# --- UI Tabs ---
tab_signup, tab_entries, tab_admin = st.tabs(["🎵 Sign-Up & Lottery", "📊 Entries", "🔒 Admin"])

# --- Sign-Up & Lottery Tab ---
with tab_signup:
    st.title("🔥 EXTRA SPICY PLEASE: Open Decks")

    # DJ Sign-Up Form
    st.subheader("🎧 DJ Sign-Up")
    
    with st.form("signup_form"):
        real_name = st.text_input("Name", key="form_real_name")
        name = st.text_input("DJ Name", key="form_name")
        email = st.text_input("Email (to send your recording)", key="form_email")
        instagram = st.text_input("Instagram", key="form_instagram")
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Sign Up")
        with col2:
            clear = st.form_submit_button("Clear Form")
        if submitted:
            if not real_name.strip() or not name.strip() or not email.strip() or not instagram.strip():
                st.error("❗ Name, DJ Name, Email, and Instagram are required!")
            else:
                arrival_str = datetime.datetime.now().strftime("%H:%M:%S")
                new_dj = {"real_name": real_name, "name": name, "arrival_time": arrival_str,
                           "email": email, "instagram": instagram, "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                dj_list.append(new_dj)
                pd.DataFrame(dj_list).to_csv(CSV_FILE, index=False)
                st.success(f"✅ {name} signed up!")
                st.session_state.clear_form = True
                st.rerun()
        if clear:
            st.session_state.clear_form = True
            st.rerun()

    # Lottery Draw Controls
    st.subheader("🎲 Lottery Draw")
    if st.button("Draw Next DJ"):
        remaining = [dj for dj in dj_list if dj['name'] not in st.session_state.played_djs]
        if not remaining:
            st.warning("All DJs have played or none signed up.")
        else:
            now = datetime.datetime.now()
            weights = []
            for dj in remaining:
                arr_time = datetime.datetime.strptime(dj['arrival_time'], "%H:%M:%S").time()
                elapsed = (now - datetime.datetime.combine(datetime.date.today(), arr_time)).total_seconds() / 60
                weights.append(min(5, int(elapsed//15) + 1))
            pick = random.choices(remaining, weights=weights, k=1)[0]
            st.session_state.played_djs.append(pick['name'])
            # Update CSV to persist picked DJs
            for dj in dj_list:
                if dj['name'] == pick['name']:
                    dj['picked'] = True
            pd.DataFrame(dj_list).to_csv(CSV_FILE, index=False)
            st.success(f"🎉 Next up: {pick['name']}!")
            st.rerun()
    if st.button("Wildcard Pick"):
        remaining = [dj for dj in dj_list if dj['name'] not in st.session_state.played_djs and dj['name'] not in st.session_state.wildcard_djs]
        if not remaining:
            st.warning("No DJs left for wildcard.")
        else:
            pick = random.choice(remaining)
            st.session_state.wildcard_djs.append(pick['name'])
            st.session_state.played_djs.append(pick['name'])
            # Update CSV to persist picked DJs
            for dj in dj_list:
                if dj['name'] == pick['name']:
                    dj['picked'] = True
            pd.DataFrame(dj_list).to_csv(CSV_FILE, index=False)
            st.success(f"🎯 Wildcard: {pick['name']}!")
            st.rerun()

# --- Entries Tab ---
with tab_entries:
    st.subheader("📊 All Sign-Up Entries")
    if dj_list:
        # --- Summary Table ---
        summary_df = pd.DataFrame(dj_list)
        summary_df['wildcard'] = summary_df['name'].apply(lambda x: x in st.session_state.wildcard_djs)
        # Reorder and select columns for summary
        summary_columns = ['real_name', 'name', 'instagram', 'arrival_time', 'wildcard', 'timestamp']
        summary_df = summary_df[[col for col in summary_columns if col in summary_df.columns]]
        summary_df = summary_df.rename(columns={
            'real_name': 'Name',
            'name': 'DJ Name',
            'instagram': 'Instagram',
            'arrival_time': 'Arrival Time',
            'wildcard': 'Wildcard',
            'timestamp': 'Timestamp'
        })
        summary_df['Wildcard'] = summary_df['Wildcard'].apply(lambda v: 'Yes' if v else 'No')
        
        # Accessible green for picked DJs
        picked_green = 'background-color: #228B22; color: white;'
        def highlight_summary_row(row):
            if row['DJ Name'] in st.session_state.played_djs:
                return [picked_green] * len(row)
            return [''] * len(row)
        styled_summary_df = summary_df.style.apply(highlight_summary_row, axis=1)
        st.dataframe(styled_summary_df, use_container_width=True)

        # --- Expanders for Details and Delete ---
        delete_index = None
        for i, dj in enumerate(dj_list):
            with st.expander(f"{dj.get('real_name', '')} | {dj['name']} | {dj.get('instagram', '')} | {dj['email']} | {dj['arrival_time']} | {dj['timestamp']}"):
                st.write(f"**Name:** {dj.get('real_name', '')}")
                st.write(f"**DJ Name:** {dj['name']}")
                st.write(f"**Instagram:** {dj.get('instagram', '')}")
                st.write(f"**Email:** {dj['email']}")
                st.write(f"**Arrival Time:** {dj['arrival_time']}")
                st.write(f"**Timestamp:** {dj['timestamp']}")
                st.write(f"**Wildcard:** {'Yes' if dj['name'] in st.session_state.wildcard_djs else 'No'}")
                if st.button(f"Delete Entry {i}"):
                    delete_index = i
        if delete_index is not None:
            removed_name = dj_list[delete_index]['name']
            dj_list.pop(delete_index)
            pd.DataFrame(dj_list).to_csv(CSV_FILE, index=False)
            if removed_name in st.session_state.played_djs:
                st.session_state.played_djs.remove(removed_name)
            st.rerun()
        # Mark wildcard column
        df = pd.DataFrame(dj_list)
        df['wildcard'] = df['name'].apply(lambda x: x in st.session_state.wildcard_djs)
        # Reorder columns
        if 'real_name' in df.columns and 'instagram' in df.columns:
            df = df[['real_name', 'name', 'arrival_time', 'timestamp', 'wildcard', 'instagram', 'email']]
        elif 'real_name' in df.columns:
            df = df[['real_name', 'name', 'arrival_time', 'timestamp', 'wildcard', 'email']]
        elif 'instagram' in df.columns:
            df = df[['name', 'arrival_time', 'timestamp', 'wildcard', 'instagram', 'email']]
        else:
            df = df[['name', 'arrival_time', 'timestamp', 'wildcard', 'email']]
        # Format for display
        def highlight_download_row(row):
            if row['name'] in st.session_state.played_djs:
                color = 'background-color: lightgreen'
            elif row['name'] in st.session_state.wildcard_djs:
                color = 'background-color: #fff9b1'
            else:
                color = ''
            return [color] * len(row)

        df_style = df.style.apply(highlight_download_row, axis=1)
        df_style = df_style.format({'arrival_time': '{}', 'timestamp': '{}', 'wildcard': lambda v: 'Yes' if v else 'No'})
        st.download_button(
            label="📥 Download CSV",
            data=df.to_csv(index=False),
            file_name="dj_signups.csv",
            mime="text/csv"
        )
    else:
        st.info("No entries yet.")

# --- Admin Tab ---
with tab_admin:
    st.subheader("🔒 Admin Panel")
    pwd = st.text_input("Enter Admin Password", type="password")
    if pwd == ADMIN_PASSWORD:
        # Manual DJ pick option
        unpicked_djs = [dj['name'] for dj in dj_list if dj['name'] not in st.session_state.played_djs]
        if unpicked_djs:
            manual_pick = st.selectbox("Manually pick a DJ (mark as played)", unpicked_djs, key="manual_pick_select")
            if st.button("Mark as Picked"):
                st.session_state.played_djs.append(manual_pick)
                # Update CSV to persist picked DJs
                for dj in dj_list:
                    if dj['name'] == manual_pick:
                        dj['picked'] = True
                pd.DataFrame(dj_list).to_csv(CSV_FILE, index=False)
                st.success(f"✅ {manual_pick} marked as picked.")
                st.rerun()
        if st.button("🔄 Reset All Data"):
            if os.path.exists(CSV_FILE):
                os.remove(CSV_FILE)
            st.session_state.played_djs = []
            st.session_state.wildcard_djs = []
            dj_list.clear()
            st.success("✅ Data reset.")
        st.write("*Use this panel to reset signups and clear history.*")
    else:
        st.info("Enter the correct password to access admin controls.")
