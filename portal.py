import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Team Portal", layout="wide")

# --- HIDE NATIVE STREAMLIT HEADER & FOOTER ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 1. Team Data Matrix with Individual PINs ---
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

# --- CUSTOM SIDEBAR MENU ---
with st.sidebar:
    role = option_menu(
        menu_title="Main Menu", 
        options=["Employee Portal", "Manager Portal"], 
        icons=["person-badge", "shield-lock"], 
        menu_icon="cast", 
        default_index=0
    )

# ====================================================================
# VIEW 1: EMPLOYEE PORTAL (SECURED WITH PIN)
# ====================================================================
if role == "Employee Portal":
    st.subheader("📝 Leave Portal Dashboard")
    st.markdown("Select your name and enter your private PIN to access your personal workspace.")
    
    selected_name = st.selectbox("Select Your Name:", ["-- Choose Name --"] + list(EMP_DETAILS.keys()))
    
    if selected_name != "-- Choose Name --":
        emp_info = EMP_DETAILS[selected_name]
        
        # 🔐 Password Box Entry Gate
        emp_pin = st.text_input(f"Enter Private PIN for {selected_name}:", type="password")
        
        if emp_pin == emp_info["PIN"]:
            st.success(f"🔓 Access Granted. Welcome back, {selected_name}!")
            
            # 📊 LIVE METERING SECTION (NOW IN A BORDERED CARD)
            with st.container(border=True):
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
                        st.warning(f"⚠️ Profile matched, but no balance records found in the spreadsheet tab yet.")
                except Exception as e:
                    st.error("Cannot read metrics from the server database.")
                
            st.divider()
            
            # --- FORM AND HISTORY INTERFACE ---
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
                                st.toast(f"🎉 Success! Request **{req_id}** submitted directly to Kulwant's ledger.", icon="✅")
                                st.balloons()
                            except Exception as e:
                                st.error("Database sync failed. Double check your web app permissions.")
            
            with tab2:
                st.markdown("### 📋 Recent Request Queue")
                try:
                    req_csv_url = "https://docs.google.com/spreadsheets/d/1CqNHI54xg4zE4v66pdF0HkJbMlW-fnQhlLK2ijenTzI/gviz/tq?tqx=out:csv&sheet=Requests"
                    df = pd.read_csv(req_csv_url)
                    
                    df.columns = df.columns.str.strip()
                    user_df = df[df['Name'].astype(str).str.strip().str.lower() == selected_name.strip().lower()]
                    
                    if not user_df.empty:
                        display_df = user_df[['ID', 'Date', 'Type', 'Status', 'Reason']]
                        # WRAPPED TABLE IN EXPANDER
                        with st.expander("🔍 Click to view your past requests", expanded=True):
                            st.dataframe(display_df, use_container_width=True, hide_index=True)
                    else:
                        st.info("You haven't submitted any requests yet.")
                except Exception as e:
                    st.warning("Unable to fetch your status history ledger at this moment.")
                    
        elif emp_pin != "":
            st.error("❌ Incorrect security PIN. Access denied. Please ask your administrator for assistance.")

# ====================================================================
# VIEW 2: MANAGER PORTAL
# ====================================================================
elif role == "Manager Portal":
    st.subheader("🔒 Manager Gateway")
    password = st.text_input("Enter Manager Security PIN:", type="password")
    
    # NEW MANAGER PIN SET TO 5656
    if password == "5656":
        st.success("Access Granted.")
        st.divider()
        
        st.markdown("### 📥 Live Database Queue")
        st.info("💡 To view incoming requests, open your linked Google Sheet tab directly.")
        
        sheet_url = "https://docs.google.com/spreadsheets/d/1CqNHI54xg4zE4v66pdF0HkJbMlW-fnQhlLK2ijenTzI/edit?usp=sharing"
        st.markdown(f"[👉 Click Here to Open Live Google Sheet Ledger]({sheet_url})")
        
    elif password != "":
        st.error("Invalid PIN.")
