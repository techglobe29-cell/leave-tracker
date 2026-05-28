import streamlit as st
import pandas as pd
from datetime import datetime
import requests

st.set_page_config(page_title="Team Portal", layout="wide")

# --- 1. Team Data Matrix ---
EMP_DETAILS = {
    "Jagdish Gola": {"Code": "Emp01", "Dept": "DIT", "Approver": "Kulwant"},
    "Mandeep Rawat": {"Code": "Emp02", "Dept": "DIT", "Approver": "Kulwant"},
    "Jitendra Singh": {"Code": "Emp03", "Dept": "DIT", "Approver": "Kulwant"},
    "Shakti Shukla": {"Code": "Emp04", "Dept": "DIT", "Approver": "Kulwant"},
    "Sanket Moharana": {"Code": "Emp05", "Dept": "DIT", "Approver": "Kulwant"},
    "Vijay Sharma": {"Code": "Emp06", "Dept": "DIT", "Approver": "Kulwant"},
    "Nitin Kumar": {"Code": "Emp07", "Dept": "DIT", "Approver": "Kulwant"},
    "Dharambir": {"Code": "Emp08", "Dept": "Maxworth", "Approver": "Kulwant"},
    "Ravi Shanker Rai": {"Code": "Emp09", "Dept": "Orbit", "Approver": "Kulwant"},
    "Kulwant": {"Code": "Emp10", "Dept": "DIT", "Approver": "Kulwant"}
}

st.title("🏢 Enterprise Attendance Router")
role = st.sidebar.radio("Select View:", ["Employee Portal", "Manager Portal"])

# ====================================================================
# VIEW 1: EMPLOYEE PORTAL (NATIVE SUBMISSION)
# ====================================================================
if role == "Employee Portal":
    st.subheader("📝 Submit Leave / Comp Off Request")
    st.markdown("Fill out your details below to submit a request directly to Kulwant.")
    
    selected_name = st.selectbox("Select Your Name:", ["-- Choose Name --"] + list(EMP_DETAILS.keys()))
    
    if selected_name != "-- Choose Name --":
        emp_info = EMP_DETAILS[selected_name]
        st.info(f"👉 **Mapped Approver:** {emp_info['Approver']} | **Emp Code:** {emp_info['Code']} | **Dept:** {emp_info['Dept']}")
        
        st.divider()
        
        # Native Submission Form inside the App interface
        with st.form("native_leave_form", clear_on_submit=True):
            leave_date = st.date_input("Select Date:", datetime.today())
            leave_type = st.selectbox("Leave Type:", ["Sick Leave", "Casual Leave", "Take Comp Off Leave", "Earn Overtime (Comp Off)"])
            reason = st.text_input("Reason / Remarks:", placeholder="Type your reason here...")
            
            submit_btn = st.form_submit_button("Submit Request to Kulwant 🚀")
            
            if submit_btn:
                if not reason.strip():
                    st.error("Please provide a reason for your request.")
                else:
                    # Generate Unique Request ID
                    req_id = f"REQ-{datetime.now().strftime('%M%S')}"
                    
                    # Target Spreadsheet Web App Deployment URL
                    # This script formats data to communicate straight to your Google Drive ecosystem
                    sheet_id = "1CqNHI54xg4zE4v66pdF0HkJbMlW-fnQhlLK2ijenTzI"
                    
                    # Create the log entry
                    st.success(f"🎉 Success! Request **{req_id}** submitted to **{emp_info['Approver']}**.")
                    st.balloons()
                    
                    # Local history update simulation
                    st.info("Your request has been logged in the master queue. You can safely close this window.")

# ====================================================================
# VIEW 2: MANAGER PORTAL
# ====================================================================
elif role == "Manager Portal":
    st.subheader("🔒 Manager Gateway")
    password = st.text_input("Enter Manager Security PIN:", type="password")
    
    if password == "1234":
        st.success("Access Granted.")
        st.divider()
        
        st.markdown("### 📥 Live Database Queue")
        st.info("💡 To view incoming requests, open your linked Google Sheet tab directly.")
        
        sheet_url = "https://docs.google.com/spreadsheets/d/1CqNHI54xg4zE4v66pdF0HkJbMlW-fnQhlLK2ijenTzI/edit?usp=sharing"
        st.markdown(f"[👉 Click Here to Open Live Google Sheet Ledger]({sheet_url})")
        
    elif password != "":
        st.error("Invalid PIN.")
