import streamlit as st
import pandas as pd
from datetime import datetime
import requests  # <-- Added for background Google Sheets automation
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Kyndryl Resources Leave Tracker", layout="wide")

# --- HIDE NATIVE STREAMLIT HEADER & FOOTER + CUSTOM CSS ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            /* Make primary buttons look like an alert red */
            div.stButton > button[kind="primary"] {
                background-color: #ff4b4b;
                color: white;
                border-color: #ff4b4b;
            }
            div.stButton > button[kind="primary"]:hover {
                background-color: #ff3333;
                color: white;
                border-color: #ff3333;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# 1. Initialize Database with exact team data
if 'employee_db' not in st.session_state:
    st.session_state.employee_db = pd.DataFrame({
        "Emp Code": ["Emp01", "Emp02", "Emp03", "Emp04", "Emp05", "Emp06", "Emp07", "Emp08", "Emp09", "Emp10"],
        "Name": [
            "Jagdish Gola", "Mandeep Rawat", "Jitendra Singh", "Shakti Shukla", 
            "Sanket Moharana", "Vijay Sharma", "Nitin Kumar", "Dharambir", 
            "Ravi Shanker Rai", "Kulwant"
        ],
        "Department": ["DIT", "DIT", "DIT", "DIT", "DIT", "DIT", "DIT", "Maxworth", "Orbit", "DIT"],
        "Total Annual EL Quota": [8.0, 4.0, 7.0, 2.0, 3.0, 0.0, 3.0, 0.0, 0.0, 0.0],
        "EL Taken This Month": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "Comp Off Balance": [0.0, 0.0, 0.0, 0.0, 0.0, 5.5, 0.0, 0.0, 0.0, 0.0],
        "Approver Name": ["Kulwant"] * 10
    })

if 'leave_history' not in st.session_state:
    st.session_state.leave_history = pd.DataFrame([
        {"Log ID": 101, "Date": "2026-06-18", "Emp Code": "Emp02", "Name": "Mandeep Rawat", "Type": "Earned Leave (EL)", "Status": "Pending Approval"},
        {"Log ID": 102, "Date": "2026-06-19", "Emp Code": "Emp05", "Name": "Sanket Moharana", "Type": "Take Comp Off Leave", "Status": "Pending Approval"}
    ])

# 2. Monthly Auto-Credit Feature (1.5 EL Added)
if 'last_month' not in st.session_state:
    st.session_state.last_month = datetime.today().strftime("%Y-%m")

cur_month = datetime.today().strftime("%Y-%m")

if cur_month != st.session_state.last_month:
    db = st.session_state.employee_db
    for idx, row in db.iterrows():
        st.session_state.employee_db.at[idx, "Total Annual EL Quota"] = row["Total Annual EL Quota"] + 1.5
        st.session_state.employee_db.at[idx, "EL Taken This Month"] = 0.0
    st.session_state.last_month = cur_month

# Prepare operational data frame
df_master = st.session_state.employee_db.copy()
df_master["Remaining EL Balance"] = df_master["Total Annual EL Quota"] - df_master["EL Taken This Month"]


# --- TWO-COLUMN WORKSPACE LAYOUT ---
nav_col, content_col = st.columns([1, 3.2], gap="large")

with nav_col:
    st.write("### 🖥️ Main Menu")
    action = option_menu(
        menu_title=None, 
        options=["Employee Portal", "Log Leave Request", "Earn Overtime", "Manager Approvals", "Add Employee"],
        icons=["person-workspace", "pencil-square", "hourglass-split", "check2-circle", "person-plus"],
        default_index=0,
        styles={
            "container": {"padding": "0px", "background-color": "#f8f9fa"},
            "nav-link": {"font-size": "15px", "text-align": "left", "margin": "4px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#ff4b4b", "color": "white"}
        }
    )


with content_col:
    # --- ACTION 1: CENTRAL EMPLOYEE PORTAL ---
    if action == "Employee Portal":
        st.title("🏢 Kyndryl Resources Leave Tracker")
        st.subheader("📝 Leave Portal Dashboard")
        st.markdown("Select your name to view personal balances, or check the team summary below.")
        
        # User dropdown selection
        names_list = ["-- Choose Name --"] + df_master["Name"].tolist()
        selected_user = st.selectbox("Select Your Name:", names_list)
        
        # Show Personal Metric Section ONLY if a valid name is picked
        if selected_user != "-- Choose Name --":
            emp_info = df_master[df_master["Name"] == selected_user].iloc[0]
            st.markdown(f"### 👋 Personal Balance: **{selected_user}**")
            
            with st.container(border=True):
                m_col1, m_col2, m_col3 = st.columns(3)
                m_col1.metric("Remaining EL Balance", f"{emp_info['Remaining EL Balance']} Days")
                m_col2.metric("Comp Off Balance", f"{emp_info['Comp Off Balance']} Days")
                m_col3.metric("EL Booked This Month", f"{emp_info['EL Taken This Month']} Days")
        
        st.divider()
        
        # --- CENTRALIZED TEAM LEAVE BALANCE SHEET (Visible to All) ---
        st.markdown("### 📋 Central Team Leave Balances")
        st.markdown("All employee metrics and remaining holiday balances are listed transparently below:")
        
        # Selectable view for clean reporting
        st.dataframe(
            df_master[["Emp Code", "Name", "Department", "Comp Off Balance", "Remaining EL Balance", "EL Taken This Month", "Approver Name"]], 
            use_container_width=True, 
            hide_index=True
        )
        
        # Shared Log history so everyone sees pending updates
        if not st.session_state.leave_history.empty:
            st.markdown("#### 📜 Recent Activity & Approval Logs")
            st.dataframe(st.session_state.leave_history[["Date", "Name", "Type", "Status"]], use_container_width=True, hide_index=True)

    # --- ACTION 2: LOG LEAVE REQUEST ---
    elif action == "Log Leave Request":
        st.title("📝 Log Leave Request")
        with st.form("log_form", clear_on_submit=True):
            sel_name = st.selectbox("Select Employee", df_master["Name"].tolist())
            d_sel = st.date_input("Date of Leave", datetime.today())
            status = st.selectbox("Type", ["Earned Leave (EL)", "Take Comp Off Leave"])
            
            emp_row = df_master[df_master["Name"] == sel_name].iloc[0]
            rem_el_bal = emp_row["Remaining EL Balance"]
            is_low_balance = (rem_el_bal < 2.0 and status == "Earned Leave (EL)") or (emp_row["Comp Off Balance"] < 1.0 and status == "Take Comp Off Leave")
            
            if is_low_balance:
                st.warning(f"⚠️ warning: {sel_name}'s balance is critically low! (EL Remainder: {rem_el_bal} Days | Comp Off: {emp_row['Comp Off Balance']} Days)")
                submit_btn = st.form_submit_button("Submit Request Anyway (Low Balance)", type="primary")
            else:
                submit_btn = st.form_submit_button("Submit Leave Request")
            
            if submit_btn:
                e_code = emp_row["Emp Code"]
                new_id = int(datetime.timestamp(datetime.now()))
                new_log = pd.DataFrame([{
                    "Log ID": new_id, 
                    "Date": d_sel.strftime("%Y-%m-%d"), 
                    "Emp Code": e_code, 
                    "Name": sel_name, 
                    "Type": status, 
                    "Status": "Pending Approval"
                }])
                st.session_state.leave_history = pd.concat([st.session_state.leave_history, new_log], ignore_index=True)
                st.success(f"Leave request successfully queued for approval for {sel_name}!")
                st.rerun()

    # --- ACTION 3: EARN OVERTIME ---
    elif action == "Earn Overtime":
        st.title("⏳ Log Overtime / Extra Shift to Earn Comp Off")
        with st.form("overtime_form", clear_on_submit=True):
            sel_name = st.selectbox("Select Employee", df_master["Name"].tolist())
            d_worked = st.date_input("Date of Extra Shift", datetime.today())
            days_earned = st.number_input("Comp Off Days Earned", min_value=0.5, max_value=2.0, value=1.0, step=0.5)
            notes = st.text_input("Reason / Operational Requirement Note")
            submit_ot = st.form_submit_button("Grant Comp Off Credit")
            
            if submit_ot:
                emp_row = df_master[df_master["Name"] == sel_name].iloc[0]
                idx = df_master[df_master["Name"] == sel_name].index[0]
                st.session_state.employee_db.at[idx, "Comp Off Balance"] += days_earned
                
                new_id = int(datetime.timestamp(datetime.now()))
                new_log = pd.DataFrame([{
                    "Log ID": new_id, 
                    "Date": d_worked.strftime("%Y-%m-%d"), 
                    "Emp Code": emp_row["Emp Code"], 
                    "Name": sel_name, 
                    "Type": f"Earned Comp Off (+{days_earned})", 
                    "Status": f"Approved: {notes}"
                }])
                st.session_state.leave_history = pd.concat([st.session_state.leave_history, new_log], ignore_index=True)
                st.toast(f"Credited {days_earned} Comp Off day(s) to {sel_name}!", icon="➕")
                st.rerun()

    # --- ACTION 4: MANAGER APPROVALS ---
    elif action == "Manager Approvals":
        st.title("🔑 Approver Control Panel (Logged in as: Kulwant)")
        lh = st.session_state.leave_history
        pending_df = lh[lh["Status"] == "Pending Approval"]
        
        if pending_df.empty:
            st.info("🎉 Hooray! There are no outstanding leave approvals pending decision.")
        else:
            for idx, row in pending_df.iterrows():
                with st.container(border=True):
                    col_i, col_n, col_t, col_d, col_act = st.columns([1, 2, 2, 2, 3])
                    col_i.write(f"**ID:** {row['Log ID']}")
                    col_n.write(f"**Name:** {row['Name']}")
                    col_t.write(f"**Type:** {row['Type']}")
                    col_d.write(f"**Date:** {row['Date']}")
                    
                    app_btn = col_act.button("Approve", key=f"app_{row['Log ID']}", type="secondary")
                    rej_btn = col_act.button("Reject", key=f"rej_{row['Log ID']}")
                    
                    if app_btn:
                        MACRO_URL = "https://script.google.com/macros/s/AKfycbzcZ-sn3yY0EdapTs2gNB8ITGyuFTK6LWzxCYllb6jmV7x5LCEtfM9g_XFotUZY32AS/exec"
                        payload = {"name": row['Name'], "type": row['Type']}
                        
                        try:
                            response = requests.post(MACRO_URL, json=payload, headers={"Content-Type": "application/json"})
                            if response.status_code == 200:
                                db_idx = st.session_state.employee_db[st.session_state.employee_db["Name"] == row["Name"]].index[0]
                                current_emp_data = st.session_state.employee_db.loc[db_idx]
                                
                                if row["Type"] == "Take Comp Off Leave":
                                    if current_emp_data["Comp Off Balance"] >= 1.0:
                                        st.session_state.employee_db.at[db_idx, "Comp Off Balance"] -= 1.0
                                        st.session_state.leave_history.at[idx, "Status"] = "Approved"
                                        st.toast(f"✅ Approved! Live Google Sheet updated for {row['Name']}.", icon="📊")
                                        st.rerun()
                                    else:
                                        st.error(f"Cannot approve. {row['Name']} no longer has enough balance.")
                                elif row["Type"] == "Earned Leave (EL)":
                                    st.session_state.employee_db.at[db_idx, "EL Taken This Month"] += 1.0
                                    st.session_state.leave_history.at[idx, "Status"] = "Approved"
                                    st.toast(f"✅ Approved! Live Google Sheet updated for {row['Name']}.", icon="📊")
                                    st.rerun()
                            else:
                                st.error(f"Failed to connect with macro server. Code: {response.status_code}")
                        except Exception as e:
                            st.error(f"Error syncing with Google Sheets: {e}")
                            
                    if rej_btn:
                        st.session_state.leave_history.at[idx, "Status"] = "Rejected"
                        st.toast("Leave Request Rejected")
                        st.rerun()

    # --- ACTION 5: ADD EMPLOYEE ---
    elif action == "Add Employee":
        st.title("➕ Onboard New Team Member")
        with st.form("add_emp_form", clear_on_submit=True):
            n_id = st.text_input("Emp Code:")
            n_name = st.text_input("Name:")
            dept = st.text_input("Dept:")
            quota = st.number_input("EL Quota:", min_value=0, value=5)
            submit_emp = st.form_submit_button("Save Record")
            
            if submit_emp:
                if n_id and n_name:
                    new_row = pd.DataFrame([{"Emp Code": n_id, "Name": n_name, "Department": dept, "Total Annual EL Quota": quota, "EL Taken This Month": 0.0, "Comp Off Balance": 0.0, "Approver Name": "Kulwant"}])
                    st.session_state.employee_db = pd.concat([st.session_state.employee_db, new_row], ignore_index=True)
                    st.toast("New profile added successfully!", icon="👤")
                    st.rerun()
