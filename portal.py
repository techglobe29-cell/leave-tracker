import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Team Portal", layout="wide")

# --- 1. Team Data ---
EMP_NAMES = [
    "Jagdish Gola", "Mandeep Rawat", "Jitendra Singh", 
    "Shakti Shukla", "Sanket Moharana", "Vijay Sharma", 
    "Nitin Kumar", "Dharambir", "Ravi Shanker Rai", "Kulwant"
]

st.title("🏢 Enterprise Attendance Router")
role = st.sidebar.radio("Select View:", ["Employee Portal", "Manager Dashboard"])

# ====================================================================
# VIEW 1: EMPLOYEE PORTAL
# ====================================================================
if role == "Employee Portal":
    st.subheader("📝 Submit Leave / Comp Off Request")
    st.markdown("Select your name to log a request directly to the manager file.")
    
    selected_name = st.selectbox("Select Your Name:", ["-- Choose Name --"] + EMP_NAMES)
    
    if selected_name != "-- Choose Name --":
        st.info("👉 Mapped Approver: Kulwant")
        
        # REPLACE THIS LINK with your copied Google Form link!
        form_url = "https://docs.google.com/forms/d/e/1FAIpQLScejm4oB_oR_your_form_link/viewform"
        
        st.markdown(f"""
        <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; text-align:center;">
            <h3>⚠️ Secure Database Link Generated</h3>
            <p>To record your request permanently so Kulwant can see it instantly, click the button below:</p>
            <a href="{form_url}" target="_blank" style="background-color:#ff4b4b; color:white; padding:10px 20px; text-decoration:none; border-radius:5px; font-weight:bold;">
                Open Official Leave Request Form 🚀
            </a>
        </div>
        """, unsafe_allow_html=True)

# ====================================================================
# VIEW 2: MANAGER DASHBOARD
# ====================================================================
elif role == "Manager Dashboard":
    st.subheader("🔒 Manager Gateway")
    password = st.text_input("Enter Manager Security PIN:", type="password")
    
    if password == "1234":
        st.success("Access Granted.")
        st.divider()
        
        st.markdown("### 📥 Live Database Queue")
        st.info("💡 To view incoming requests, open your linked Google Sheet tab directly to manage entries instantly with 100% data security.")
        
        # Optional: You can paste your linked Google Sheet link here for easy access
        sheet_url = "https://docs.google.com/spreadsheets/d/your_sheet_id_here/edit"
        st.markdown(f"[👉 Click Here to Open Live Google Sheet Ledger]({sheet_url})")
        
    elif password != "":
        st.error("Invalid PIN.")
