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
    st.subheader("📝 Leave Portal Dashboard")
    st.markdown("Select your name below to view your real-time balances and log new requests.")
    
    selected_name = st.selectbox("Select Your Name:", ["-- Choose Name --"] + list(EMP_DETAILS.keys()))
    
    if selected_name != "-- Choose Name --":
        emp_info = EMP_DETAILS[selected_name]
        
        st.markdown(f"#### 📊 Personal Balance Statement ({selected_name})")
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
                st.warning(f"⚠️ Profile matched, but no rows found matching '{selected_name}' in the 'Balances' sheet tab yet.")
        except Exception as e:
            st.error("Cannot read metrics. Please ensure your Google Sheet tab is named exactly 'Balances' and headers match your structure.")
            
        st.divider()
        
        tab1, tab2 = st.tabs(["🆕 New Request Form", "🔍 Check Request Status History"])
        
        with tab1:
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
                        
                        macro_url = "https://script.google.com/macros/s/AKfycbzui_OKkbjFmEU-MyGCLStlOGmAGHP_HZyQQI16f3gwalnDYiTjiuUrlaRgjfxd6Rq8/exec"
                        
                        try:
                            headers = {"Content-Type": "application/json"}
                            response = requests.post(macro_url, json=form_data, headers=headers)
                            st.success(f"🎉 Success! Request **{req_id}** submitted directly to Kulwant's ledger.")
                            st.balloons()
                        except Exception as e:
                            st.error("Database sync failed. Double check your web app permissions.")
        
        with tab2:
            st.markdown(f"### 📋 Recent Request Queue ({selected_name})")
            try:
                req_csv_url = "https://docs.google.com/spreadsheets/d/1CqNHI54xg4zE4v66pdF0HkJbMlW-fnQhlLK2ijenTzI/gviz/tq?tqx=out:csv&sheet=Requests"
                df = pd.read_csv(req_csv_url)
                
                df.columns = df.columns.str.strip()
                user_df = df[df['Name'].astype(str).str.strip().str.lower() == selected_name.strip().lower()]
                
                if not user_df.empty:
                    display_df = user_df[['ID', 'Date', 'Type', 'Status', 'Reason']]
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                else:
                    st.info("You haven't submitted any requests yet.")
            except Exception as e:
                st.warning("Unable to fetch your status history ledger at this moment.")

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
