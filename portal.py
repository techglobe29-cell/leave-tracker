import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json

st.set_page_config(page_title="Team Portal", layout="wide", page_icon="🏢")

# --- 1. Team Data Matrix ---
EMP_DETAILS = {
    "Jagdish Gola": {"Code": "Emp01", "Dept": "DIT", "Approver": "Kulwant", "PIN": "2021"},
    "Mandeep Rawat": {"Code": "Emp02", "Dept": "DIT", "Approver": "Kulwant", "PIN": "2022"},
    "Jitendra Singh": {"Code": "Emp03", "Dept": "DIT", "Approver": "Kulwant", "PIN": "2023"},
    "Shakti Shukla": {"Code": "Emp04", "Dept": "DIT", "Approver": "Kulwant", "PIN": "2024"},
    "Sanket Moharana": {"Code": "Emp05", "Dept": "DIT", "Approver": "Kulwant", "PIN": "2025"},
    "Vijay Sharma": {"Code": "Emp06", "Dept": "DIT", "Approver": "Kulwant", "PIN": "2026"},
    "Nitin Kumar": {"Code": "Emp07", "Dept": "DIT", "Approver": "Kulwant", "PIN": "2027"},
    "Dharambir": {"Code": "Emp08", "Dept": "Maxworth", "Approver": "Kulwant", "PIN": "2028"},
    "Ravi Shanker Rai": {"Code": "Emp09", "Dept": "Orbit", "Approver": "Kulwant", "PIN": "2029"},
    "Kulwant": {"Code": "Emp10", "Dept": "DIT", "Approver": "Kulwant", "PIN": "2030"}
}

st.title("🏢 Enterprise Attendance Router")
role = st.sidebar.radio("Select View:", ["Employee Portal", "Manager Portal"])

# ====================================================================
# VIEW 1: EMPLOYEE PORTAL
# ====================================================================
if role == "Employee Portal":
    st.subheader("📝 Leave Portal Dashboard")
    st.markdown("Select your name and enter your private PIN to access your personal workspace.")
    
    selected_name = st.selectbox("Select Your Name:", ["-- Choose Name --"] + list(EMP_DETAILS.keys()))
    
    if selected_name != "-- Choose Name --":
        emp_info = EMP_DETAILS[selected_name]
        emp_pin = st.text_input(f"Enter Private PIN for {selected_name}:", type="password")
        
        if emp_pin == emp_info["PIN"]:
            st.success(f"🔓 Access Verified. Welcome back, {selected_name}!")
            
            # --- LIVE METRIC DASHBOARD ---
            st.markdown("#### 📊 Personal Balance Statement")
            try:
                bal_csv_url = "https://docs.google.com/spreadsheets/d/1CqNHI54xg4zE4v66pdF0HkJbMlW-fnQhlLK2ijenTzI/gviz/tq?tqx=out:csv&sheet=Balances"
                bal_df = pd.read_csv(bal_csv_url)
                bal_df.columns = bal_df.columns.str.strip()
                bal_df['Name'] = bal_df['Name'].astype(str).str.strip().str.lower()
                user_bal = bal_df[bal_df['Name'] == selected_name.strip().lower()]
                
                if not user_bal.empty:
                    m1, m2, m3, m4 = st.columns(4)
                    with m1:
                        st.metric("Leave Quota", float(user_bal['Leave Quota'].values[0]))
                    with m2:
                        st.metric("Leave Taken", float(user_bal['Leave Taken'].values[0]))
                    with m3:
                        st.metric("Leave Balance", float(user_bal['Leave Balance'].values[0]))
                    with m4:
                        st.metric("Comp Off Balance", float(user_bal['Comp Off Balance'].values[0]))
                else:
                    st.warning("⚠️ No balance metrics found in the master sheet yet.")
            except:
                st.error("Temporary network lag. Unable to display balance cards.")
                
            st.divider()
            
            tab1, tab2 = st.tabs(["🆕 New Request Form", "🔍 Check Request Status History"])
            
            with tab1:
                with st.form("native_leave_form", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        from_date = st.date_input("From Date:", datetime.today())
                    with c2:
                        to_date = st.date_input("To Date (Inclusive):", datetime.today())
                    
                    leave_type = st.selectbox("Leave Type:", ["Sick Leave", "Casual Leave", "Take Comp Off Leave", "Earn Overtime (Comp Off)"])
                    
                    # Smart conditional hints
                    placeholder_text = "Type your reason here..."
                    if leave_type == "Earn Overtime (Comp Off)":
                        placeholder_text = "Describe weekend task completed/project details..."
                        
                    reason = st.text_input("Reason / Remarks:", placeholder=placeholder_text)
                    submit_btn = st.form_submit_button("Submit Request to Kulwant 🚀")
                    
                    if submit_btn:
                        if to_date < from_date:
                            st.error("❌ 'To Date' cannot be earlier than 'From Date'.")
                        elif not reason.strip():
                            st.error("❌ Please provide a validation remark reason.")
                        else:
                            total_days = (to_date - from_date).days + 1
                            req_id = f"REQ-{datetime.now().strftime('%M%S')}"
                            date_string = f"{from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')}" if total_days > 1 else from_date.strftime('%Y-%m-%d')
                            
                            form_data = {
                                "ID": req_id,
                                "Date": date_string,
                                "Code": emp_info["Code"],
                                "Name": selected_name,
                                "Type": leave_type,
                                "Status": "Pending",
                                "Approver": emp_info["Approver"],
                                "Reason": reason,
                                "Days": total_days # New numeric field sent to database backend
                            }
                            
                            macro_url = "https://script.google.com/macros/s/AKfycbzui_OKkbjFmEU-MyGCLStlOGmAGHP_HZyQQI16f3gwalnDYiTjiuUrlaRgjfxd6Rq8/exec"
                            
                            try:
                                headers = {"Content-Type": "application/json"}
                                requests.post(macro_url, json=form_data, headers=headers)
                                st.success(f"🎉 Request **{req_id}** ({total_days} Day(s)) logged safely!")
                                st.balloons()
                            except:
                                st.error("Database submission sync failure.")
            
            with tab2:
                st.markdown("### 📋 Recent Request Queue")
                try:
                    req_csv_url = "https://docs.google.com/spreadsheets/d/1CqNHI54xg4zE4v66pdF0HkJbMlW-fnQhlLK2ijenTzI/gviz/tq?tqx=out:csv&sheet=Requests"
                    df = pd.read_csv(req_csv_url)
                    df.columns = df.columns.str.strip()
                    user_df = df[df['Name'].astype(str).str.strip().str.lower() == selected_name.strip().lower()]
                    
                    if not user_df.empty:
                        st.dataframe(user_df[['ID', 'Date', 'Type', 'Status', 'Reason']], use_container_width=True, hide_index=True)
                    else:
                        st.info("No submission records logged yet.")
                except:
                    st.warning("History trail reading offline.")
                    
        elif emp_pin != "":
            st.error("❌ Incorrect security PIN.")

# ====================================================================
# VIEW 2: MANAGER PORTAL
# ====================================================================
elif role == "Manager Portal":
    st.subheader("🔒 Manager Gateway")
    password = st.text_input("Enter Manager Security PIN:", type="password")
    
    if password == "1234":
        st.success("Access Granted.")
        st.divider()
        
        # Admin Operations
        st.markdown("### 📥 Live Database Queue Dashboard")
        sheet_url = "https://docs.google.com/spreadsheets/d/1CqNHI54xg4zE4v66pdF0HkJbMlW-fnQhlLK2ijenTzI/edit?usp=sharing"
        st.markdown(f"[🔗 Open Master Google Sheet Workspace Ledger]({sheet_url})")
        
        try:
            req_csv_url = "https://docs.google.com/spreadsheets/d/1CqNHI54xg4zE4v66pdF0HkJbMlW-fnQhlLK2ijenTzI/gviz/tq?tqx=out:csv&sheet=Requests"
            all_reqs = pd.read_csv(req_csv_url)
            all_reqs.columns = all_reqs.columns.str.strip()
            
            pending_reqs = all_reqs[all_reqs['Status'].str.strip().str.lower() == 'pending']
            
            if not pending_reqs.empty:
                st.warning(f"⚠️ You have {len(pending_reqs)} pending action items requiring approval attention:")
                st.dataframe(pending_reqs[['ID', 'Name', 'Date', 'Type', 'Reason']], use_container_width=True, hide_index=True)
            else:
                st.success("✅ Clear desk! No pending requests out standing.")
        except:
            st.info("Open the main workspace link above to manage entries.")
            
    elif password != "":
        st.error("Invalid PIN.")
