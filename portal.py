import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Employee Portal & Router", layout="wide")

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

if 'requests_db' not in st.session_state:
    st.session_state.requests_db = pd.DataFrame(
        [], columns=["Request ID", "Date", "Emp Code", "Name", "Type", "Status", "Mapped Approver"]
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

# --- GUI NAVIGATION ---
st.title("🏢 Enterprise Attendance & Approval Router")
role = st.sidebar.radio("Select Portal View:", ["Employee Self-Service", "Manager / Approver Dashboard"])

# ====================================================================
# VIEW 1: EMPLOYEE SELF-SERVICE (Dropdown-Based Lookup)
# ====================================================================
if role == "Employee Self-Service":
    st.subheader("📝 Submit Leave / Comp Off Request")
    st.markdown("Select your name to automatically fetch your live profile and balances.")
    
    df_emp = st.session_state.employee_db
    selected_name = st.selectbox("Select Your Name:", ["-- Choose Name --"] + df_emp["Name"].tolist())
    
    if selected_name != "-- Choose Name --":
        # Automatically pull profile metrics
        emp_data = df_emp[df_emp["Name"] == selected_name].iloc[0]
        
        st.success(f"✅ Profile Verified: **{emp_data['Name']}** ({emp_data['Department']}) | Code: {emp_data['Emp Code']}")
        
        col1, col2 = st.columns(2)
        col1.metric("Your Remaining Leaves", float(emp_data['Total Annual Leave Quota'] - emp_data['Leaves Taken This Month']))
        col2.metric("Your Available Comp Off Balance", f"{emp_data['Comp Off Balance']} Days")
        
        st.info(f"👉 Direct Reporting Approver: **{emp_data['Approver Name']}**")
        st.divider()
        
        with st.form("leave_submission_form", clear_on_submit=True):
            req_date = st.date_input("Date of Leave / Extra Shift:", datetime.today())
            req_type = st.selectbox("Action Type", ["Sick Leave", "Casual Leave", "Take Comp Off Leave", "Earn Overtime (Comp Off)"])
            reason = st.text_input("Reason / Remarks:")
            submit_req = st.form_submit_button("Submit Request")
            
            if submit_req:
                if req_type == "Take Comp Off Leave" and emp_data['Comp Off Balance'] < 1.0:
                    st.error("Submission Failed! You do not have enough Comp Off balance.")
                    st.stop()
                    
                req_id = f"REQ-{datetime.now().strftime('%M%S')}"
                
                new_row = pd.DataFrame([{
                    "Request ID": req_id,
                    "Date": req_date.strftime("%Y-%m-%d"),
                    "Emp Code": emp_data['Emp Code'],
                    "Name": emp_data['Name'],
                    "Type": req_type,
                    "Status": "Pending",
                    "Mapped Approver": emp_data['Approver Name']
                }])
                
                st.session_state.requests_db = pd.concat([st.session_state.requests_db, new_row], ignore_index=True)
                st.success(f"🚀 Request {req_id} logged! Routed straight to {emp_data['Approver Name']}.")

# ====================================================================
# VIEW 2: SECURED MANAGER / APPROVER DASHBOARD
# ====================================================================
elif role == "Manager / Approver Dashboard":
    st.subheader("🔒 Manager Gateway")
    password = st.text_input("Enter Manager Security PIN:", type="password")
    
    if password == "5656":
        st.success("Access Granted.")
        st.divider()
        
        st.markdown("### 📥 Pending Team Approvals Queue")
        req_df = st.session_state.requests_db
        
        if not req_df.empty:
            pending_df = req_df[req_df["Status"] == "Pending"]
            st.dataframe(pending_df, use_container_width=True)
            
            if not pending_df.empty:
                with st.form("approval_action_form"):
                    target_req = st.selectbox("Select Request ID to process:", pending_df["Request ID"].tolist())
                    decision = st.radio("Action:", ["Approve", "Reject"])
                    submit_decision = st.form_submit_button("Execute Action")
                    
                    if submit_decision:
                        match_req = req_df[req_df["Request ID"] == target_req].iloc[0]
                        target_emp_code = match_req["Emp Code"]
                        target_type = match_req["Type"]
                        
                        # Process updates on database upon approval confirmation
                        if decision == "Approve":
                            for idx, row in st.session_state.employee_db.iterrows():
                                if row["Emp Code"] == target_emp_code:
                                    if target_type in ["Sick Leave", "Casual Leave"]:
                                        st.session_state.employee_db.at[idx, "Leaves Taken This Month"] += 1.0
                                    elif target_type == "Take Comp Off Leave":
                                        st.session_state.employee_db.at[idx, "Comp Off Balance"] -= 1.0
                                    elif target_type == "Earn Overtime (Comp Off)":
                                        st.session_state.employee_db.at[idx, "Comp Off Balance"] += 1.0
                        
                        st.session_state.requests_db.loc[st.session_state.requests_db["Request ID"] == target_req, "Status"] = f"{decision}d"
                        st.success(f"Request {target_req} has been {decision}d!")
            else:
                st.write("🎉 No requests pending decision.")
        else:
            st.write("No transaction histories logged yet.")
            
        st.markdown("### 📊 Complete Employee Master Balance Directory")
        st.dataframe(st.session_state.employee_db, use_container_width=True)
        
    elif password != "":
        st.error("Invalid Code. Access Denied.")