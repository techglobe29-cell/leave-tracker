import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Team Dashboard", layout="wide")

# --- HIDE NATIVE STREAMLIT HEADER & FOOTER ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# 1. Initialize Database with your exact team data from the image
if 'employee_db' not in st.session_state:
    st.session_state.employee_db = pd.DataFrame({
        "Emp Code": [
            "Emp01", "Emp02", "Emp03", "Emp04", "Emp05", 
            "Emp06", "Emp07", "Emp08", "Emp09", "Emp10"
        ],
        "Name": [
            "Jagdish Gola", "Mandeep Rawat", "Jitendra Singh", 
            "Shakti Shukla", "Sanket Moharana", "Vijay Sharma", 
            "Nitin Kumar", "Dharambir", "Ravi Shanker Rai", "Kulwant"
        ],
        "Department": [
            "DIT", "DIT", "DIT", "DIT", "DIT", 
            "DIT", "DIT", "Maxworth", "Orbit", "DIT"
        ],
        "Total Annual Leave Quota": [8.0, 4.0, 7.0, 2.0, 3.0, 0.0, 3.0, 0.0, 0.0, 0.0],
        "Leaves Taken This Month": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "Comp Off Balance": [0.0, 0.0, 0.0, 0.0, 0.0, 5.5, 0.0, 0.0, 0.0, 0.0],
        "Approver Name": [
            "Kulwant", "Kulwant", "Kulwant", "Kulwant", "Kulwant", 
            "Kulwant", "Kulwant", "Kulwant", "Kulwant", "Kulwant"
        ]
    })

if 'leave_history' not in st.session_state:
    st.session_state.leave_history = pd.DataFrame(
        [], columns=["Date", "Emp Code", "Name", "Type", "Status"]
    )

# 2. Monthly Auto-Credit Feature (1.5 Leaves Added)
if 'last_month' not in st.session_state:
    st.session_state.last_month = datetime.today().strftime("%Y-%m")

cur_month = datetime.today().strftime("%Y-%m")

if cur_month != st.session_state.last_month:
    db = st.session_state.employee_db
    for idx, row in db.iterrows():
        st.session_state.employee_db.at[idx, "Total Annual Leave Quota"] = row["Total Annual Leave Quota"] + 1.5
        st.session_state.employee_db.at[idx, "Leaves Taken This Month"] = 0.0
    st.session_state.last_month = cur_month

# --- Layout Configuration ---
st.title("📊 Team Attendance & Leave Tracker")
st.markdown("Easily monitor monthly attendance, live leave balances, and Comp Off metrics.")
st.divider()

# Left Hand Navigation Options with GUI upgrade
with st.sidebar:
    action = option_menu(
        menu_title="Actions Panel",
        options=["View Dashboard", "Log Leave / Attendance", "Earn Overtime (Comp Off)", "Add New Employee"],
        icons=["speedometer2", "pencil-square", "hourglass-split", "person-plus"],
        menu_icon="sliders",
        default_index=0
    )

# --- FEATURE 1: VIEW DASHBOARD ---
if action == "View Dashboard":
    st.subheader("🗓️ Monthly Summary Dashboard")
    
    df = st.session_state.employee_db.copy()
    df["Remaining Balance"] = df["Total Annual Leave Quota"] - df["Leaves Taken This Month"]
    
    # Bordered Card container for core statistics
    with st.container(border=True):
        st.markdown("#### 📈 Operational Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Employees", len(df))
        col2.metric("Total Active Comp Off Days", int(df['Comp Off Balance'].sum()))
        col3.metric("Current Month Logs Checked", len(st.session_state.leave_history))
    
    st.markdown("### Employee Master Sheet")
    st.dataframe(df, use_container_width=True)
    
    if not st.session_state.leave_history.empty:
        st.markdown("### Recent Activity Logs")
        st.dataframe(st.session_state.leave_history, use_container_width=True)

# --- FEATURE 2: LOG LEAVE / ATTENDANCE ---
elif action == "Log Leave / Attendance":
    st.subheader("📝 Log Leave, Comp Off, or Attendance")
    df = st.session_state.employee_db
    
    with st.form("log_form", clear_on_submit=True):
        sel_name = st.selectbox("Select Employee", df["Name"].tolist())
        d_sel = st.date_input("Date", datetime.today())
        status = st.selectbox("Type", ["Present", "Sick Leave", "Casual Leave", "Take Comp Off Leave", "Unpaid Leave"])
        submit_btn = st.form_submit_button("Submit Record")
        
        if submit_btn:
            e_code = "EMP"
            for idx, row in st.session_state.employee_db.iterrows():
                if row["Name"] == sel_name:
                    e_code = row["Emp Code"]
                    
                    if status == "Take Comp Off Leave":
                        if row["Comp Off Balance"] >= 1.0:
                            st.session_state.employee_db.at[idx, "Comp Off Balance"] -= 1.0
                            st.toast(f"Deducted 1 Comp Off from {sel_name}!", icon="➖")
                        else:
                            st.error("Insufficient Comp Off Balance.")
                            st.stop()
                    elif "Leave" in status:
                        st.session_state.employee_db.at[idx, "Leaves Taken This Month"] += 1.0
                        st.toast(f"Logged {status} for {sel_name}!", icon="📝")
                    else:
                        st.toast(f"Logged {status} for {sel_name}!", icon="✅")
                        
            new_log = pd.DataFrame([{
                "Date": d_sel.strftime("%Y-%m-%d"), "Emp Code": e_code,
                "Name": sel_name, "Type": status, "Status": "Approved"
            }])
            st.session_state.leave_history = pd.concat([st.session_state.leave_history, new_log], ignore_index=True)

# --- FEATURE 3: EARN OVERTIME (COMP OFF) ---
elif action == "Earn Overtime (Comp Off)":
    st.subheader("⏳ Log Overtime / Extra Shift to Earn Comp Off")
    df = st.session_state.employee_db
    
    with st.form("overtime_form", clear_on_submit=True):
        sel_name = st.selectbox("Select Employee", df["Name"].tolist())
        d_worked = st.date_input("Date of Extra Shift", datetime.today())
        days_earned = st.number_input("Comp Off Days Earned", min_value=0.5, max_value=2.0, value=1.0, step=0.5)
        notes = st.text_input("Reason Note")
        submit_ot = st.form_submit_button("Grant Comp Off Credit")
        
        if submit_ot:
            e_code = "EMP"
            for idx, row in st.session_state.employee_db.iterrows():
                if row["Name"] == sel_name:
                    e_code = row["Emp Code"]
                    st.session_state.employee_db.at[idx, "Comp Off Balance"] += days_earned
                    
            new_log = pd.DataFrame([{
                "Date": d_worked.strftime("%Y-%m-%d"), "Emp Code": e_code,
                "Name": sel_name, "Type": f"Earned Comp Off (+{days_earned})", "Status": notes
            }])
            st.session_state.leave_history = pd.concat([st.session_state.leave_history, new_log], ignore_index=True)
            st.toast(f"Credited {days_earned} Comp Off day(s) to {sel_name}!", icon="➕")

# --- FEATURE 4: ADD NEW EMPLOYEE ---
elif action == "Add New Employee":
    st.subheader("➕ Onboard New Team Member")
    with st.form("add_emp_form", clear_on_submit=True):
        n_id = st.text_input("Emp Code:")
        n_name = st.text_input("Name:")
        dept = st.text_input("Dept:")
        quota = st.number_input("Quota:", min_value=0, value=5)
        submit_emp = st.form_submit_button("Save")
        
        if submit_emp:
            if n_id and n_name:
                new_row = pd.DataFrame([{"Emp Code": n_id, "Name": n_name, "Department": dept, "Total Annual Leave Quota": quota, "Leaves Taken This Month": 0.0, "Comp Off Balance": 0.0, "Approver Name": "Kulwant"}])
                st.session_state.employee_db = pd.concat([st.session_state.employee_db, new_row], ignore_index=True)
                st.toast("New profile added successfully!", icon="👤")
