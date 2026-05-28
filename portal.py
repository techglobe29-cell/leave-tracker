import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json

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
# VIEW 1: EMPLOYEE PORTAL
# ====================================================================
if role == "Employee Portal":
    st.subheader("📝 Submit Leave / Comp Off Request")
    st.markdown("Fill out your details below to submit a request directly to Kulwant.")
    
    selected_name = st.selectbox("Select Your Name:", ["-- Choose Name --"] + list(EMP_DETAILS.keys()))
    
    if selected_name != "-- Choose Name --":
        emp_info = EMP_DETAILS[selected_name]
        st.info(f"👉 **Mapped Approver:** {emp_info['Approver']} | **Emp Code:** {emp_info['Code']} | **Dept:** {emp_info['Dept']}")
        
        st.divider()
        
        with st.form("native_leave_form", clear_on_submit=True):
            leave_date = st.date_input("Select Date:", datetime.today())
            leave_type = st.selectbox("Leave Type:", ["Sick Leave", "Casual Leave", "Take Comp Off Leave", "Earn Overtime (Comp Off)"])
            reason = st.text_input("Reason / Remarks:", placeholder="Type your reason here...")
            
            submit_btn = st.form_submit_button("Submit Request to Kulwant 🚀")
            
            if submit_btn:
                if not reason.strip():
                    st.error("Please provide a reason for your request.")
                else:
                    req_id = f"REQ-{datetime.now().strftime('%M%S')}"
                    
                    form_data = {
                        "ID": req_id,
                        "Date": leave_date.strftime("%Y-%m-%d"),
                        "Code": emp_info["Code"],
                        "Name": selected_name,
                        "Type": leave_type,
                        "Status": "Pending",
                        "Approver": emp_info["Approver"],
                        "Reason": reason
                    }
                    
                    # ⚠️ PASTE YOUR GOOGLE DEPLOYMENT LINK ENDING IN /exec HERE:
                    macro_url = "PASTE_YOUR_WEB_APP_URL_HERE"
                    
                    try:
                        # Headers tell Google explicitly to process this as JSON data
                        headers = {"Content-Type": "application/json"}
                        response = requests.post(macro_url, data=json.dumps(form_data), headers=headers)
                        
                        if response.status_code == 200:
                            st.success(f"🎉 Success! Request **{req_id}** submitted directly to Kulwant's ledger.")
                            st.balloons()
                        else:
                            st.error(f"Google Server responded with error code: {response.status_code}")
                    except Exception as e:
                        st.error(f"Network error: {str(e)}. Check your web app permissions.")

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
