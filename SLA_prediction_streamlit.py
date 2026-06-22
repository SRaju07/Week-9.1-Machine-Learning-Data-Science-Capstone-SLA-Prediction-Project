import streamlit as st
import pandas as pd
import joblib
from datetime import datetime,組合

# --- PAGE LAYOUT CONFIGURATION ---
st.set_page_config(
    page_title="Enterprise IT SLA Intelligence Dashboard",
    page_icon="💻",
    layout="centered"
)

# --- CLEAN INTERFACE DESIGN CUSTOM CSS ---
st.markdown("""
<style>
    /* Hides Streamlit default margins and empty headers space padding */
    .block-container {
        padding-top: 2rem !important;
    }
    
    /* Box Interior Headings */
    .section-title {
        font-size: 22px;
        font-weight: 600;
        color: #0F172A;
        margin-bottom: 20px;
        border-bottom: 2px solid #F1F5F9;
        padding-bottom: 10px;
        margin-top: 20px;
    }

    /* Output Results Plain Styling Labels */
    .result-row {
        font-size: 15px;
        color: #334155;
        margin-bottom: 10px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .bold-value {
        font-weight: bold;
        color: #0F172A;
    }
    
    /* Reason List Bullet Styling */
    .reason-box {
        background-color: #F8FAFC;
        border-left: 4px solid #94A3B8;
        padding: 12px;
        border-radius: 4px;
        margin-top: 8px;
    }
    
    /* Precaution Box Styling */
    .precaution-box {
        background-color: #FFFBEB;
        border-left: 4px solid #F59E0B;
        padding: 12px;
        border-radius: 4px;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- ENTERPRISE IT TITLE WITH IT PROFESSIONAL ICON ---
st.title("🧑‍💻 Enterprise IT SLA Intelligence Dashboard")

# --- DATA ROUTING MATRIX FOR INCIDENTS ---
INCIDENT_RULES = {
    "Outlook / Email Issue": {
        "category": "Software", "team": "DevOps", "team_display": "MS Office Team", "remote": "Yes",
        "reasons": [
            "**Cloud Sync Failure:** Broken connection between local systems and cloud services.",
            "**Corrupted Local Index:** Damaged email cache files forcing a slow, complete history rebuild."
        ]
    },
    "VPN Issue": {
        "category": "Network", "team": "DevOps", "team_display": "Applications Team", "remote": "Yes",
        "reasons": [
            "**ISP Bandwidth Throttling:** Local provider congestion slowing connection speeds down.",
            "**Tunnel Capacity Maxed:** Maximum concurrent user limit reached on the corporate gateway."
        ]
    },
    "Firewall Outage": {
        "category": "Security Breach", "team": "Network Team", "team_display": "Network Team", "remote": "Yes",
        "reasons": [
            "**Bad Policy Deployment:** Faulty security rule update blocking legitimate traffic.",
            "**Resource Exhaustion:** Hardware CPU/Memory overloaded by high traffic volumes."
        ]
    },
    "Database Failure": {
        "category": "Database Failure", "team": "Database Admin", "team_display": "Database Team", "remote": "Yes",
        "reasons": [
            "**Query Deadlocks:** Conflicting heavy queries locking the same database tables.",
            "**Transaction Log Full:** Storage drive full from diary logging, blocking new changes."
        ]
    },
    "Server Crash": {
        "category": "Server Crash", "team": "DevOps", "team_display": "Infrastructure Team", "remote": "Yes",
        "reasons": [
            "**Kernel Panic / Memory Leak:** System memory leak or fatal OS crash.",
            "**Cascading Application Error:** Unhandled bad deployment causing a domino-effect crash."
        ]
    },
    "Motherboard": {
        "category": "Hardware", "team": "IT Support", "team_display": "IT Support Team", "remote": "No",
        "reasons": [
            "**Supply Chain Delay:** Required replacement spare parts pending courier delivery.",
            "**User Availability:** Device physical turnover delayed by user scheduling conflicts."
        ]
    },
    "Wi-Fi Connectivity Drop": {
        "category": "Network", "team": "Network Team", "team_display": "Network Team", "remote": "No",
        "reasons": [
            "**Access Point Outage:** Physical PoE wall/ceiling AP unit power drop.",
            "**RF Interference:** Heavy appliance or rogue electronic frequencies disrupting signals."
        ]
    }
}

# --- SHORT KEY POINTS PRECAUTIONS MATRIX ---
PRIORITY_PRECAUTIONS = {
    "Critical": [
        "**5-Min Page:** Alert backup engineer instantly if primary doesn't answer.",
        "**Bridge Call:** Start a bridge call with team leads immediately.",
        "**Failover Switch:** Switch users to a backup server right away instead of troubleshooting."
    ],
    "High": [
        "**Top of Queue:** Move the ticket straight to the top of the daily to-do list.",
        "**Supervisor Alert:** Automatically alert mail to boss at the 2-hour warning mark.",
        "**Freeze Minor Tasks:** Pause routine, non-urgent work to focus on this issue."
    ],
    "Medium": [
        "**2-Hour Pickup:** Claim and check the ticket within 2 hours of opening.",
        "**Tag Handover:** Directly pass the ticket to the next shift engineer if unresolved.",
        "**Auto-Diagnostics:** Run automatic tools immediately to collect error logs."
    ],
    "Low": [
        "**Age Check:** Review older tickets so they do not get buried by new ones.",
        "**12-Hour Ping:** Send an automatic message to the user to check if the issue persists.",
        "**Queue Reroute:** Pass the ticket to a free helpdesk in another region if local teams are busy."
    ]
}

def get_sla_target(priority):
    mapping = {"Critical": 4, "High": 8, "Medium": 12, "Low": 24}
    return mapping.get(priority, 24)

# --- USER SELECTION INTERFACE ---
st.markdown('<div class="section-title">🔍 Analyze Ticket</div>', unsafe_allow_html=True)

incident_selection = st.selectbox(
    "Select Incident Type:",
    list(INCIDENT_RULES.keys())
)

auto_data = INCIDENT_RULES[incident_selection]
st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    priority = st.selectbox("Priority:", ["Low", "Medium", "High", "Critical"], index=1)
    st.text_input("Detected Category:", value=auto_data["category"], disabled=True)
with col2:
    st.text_input("Assigned Correct Team:", value=auto_data["team_display"], disabled=True)
    st.text_input("Is Remote Resolvable:", value=auto_data["remote"], disabled=True)

# --- NEW REPORTED & RESOLVED TIMESTAMPS SELECTORS ---
st.markdown('<div class="section-title">⏱️ Ticket Lifecycle Timeline</div>', unsafe_allow_html=True)

col_time1, col_time2 = st.columns(2)

with col_time1:
    st.write("**Reported Timestamp**")
    reported_date = st.date_input("Reported Date", datetime.now().date(), key="rep_date")
    reported_time = st.time_input("Reported Time", datetime.now().time(), key="rep_time")
    reported_datetime = datetime.combine(reported_date, reported_time)

with col_time2:
    st.write("**Target / Resolved Timestamp**")
    resolved_date = st.date_input("Resolved Date", datetime.now().date(), key="res_date")
    resolved_time = st.time_input("Resolved Time", datetime.now().time(), key="res_time")
    resolved_datetime = datetime.combine(resolved_date, resolved_time)

# Calculate real processing duration from the interface inputs
time_delta = resolved_datetime - reported_datetime
actual_duration_hours = max(0.0, time_delta.total_seconds() / 3600.0)

st.info(f"⏳ Evaluated Duration from Inputs: **{actual_duration_hours:.2f} Hours**")
st.markdown("<br>", unsafe_allow_html=True)

# --- ML PREDICTION INFERENCE ---
if st.button("Predict SLA Completion", use_container_width=True, type="primary"):
    sla_hours = get_sla_target(priority)
    
    input_data = pd.DataFrame([{
        "Incident_ID": "INC100000",   
        "Incident_Type": auto_data["category"],
        "Priority": priority,
        "Assigned_Department": auto_data["team"],
        "Location": "Head Office",
        "Status": "Resolved",
        "Resolution_Type": "Reboot" if auto_data["category"] != "Hardware" else "Hardware Replacement",
        "Resolution_Time_Hours": float(actual_duration_hours), # Now mapping dynamically to user selections
        "Hour": reported_datetime.hour, 
        "Day": reported_datetime.weekday(), 
        "Month": reported_datetime.month,
        "SLA_Limit": sla_hours
    }])
    
    try:
        preprocessor = joblib.load("preprocessor.pkl")
        rfe = joblib.load("rfe_selector.pkl")
        model = joblib.load("SLA_prediction_model.pkl")
        
        X_enc = preprocessor.transform(input_data)
        X_rfe = rfe.transform(X_enc)
        
        prediction = model.predict(X_rfe)[0]
        
        try:
            probabilities = model.predict_proba(X_rfe)[0]
            risk_score = int(probabilities[1] * 100)
        except AttributeError:
            risk_score = 85 if prediction == 1 else 15
        
        # Hour Assignments Based on Selection
        if priority == "Critical":
            pred_resolution = 3.5
        elif priority == "High":
            pred_resolution = 7.2
        elif priority == "Medium":
            pred_resolution = 11.5  
        else:
            pred_resolution = 21.4
            
        is_breached = (pred_resolution > sla_hours) or (prediction == 1 or risk_score > 50) or (actual_duration_hours > sla_hours)
            
        st.markdown("<br><hr>", unsafe_allow_html=True)
        
        # Display the metrics layout elements
        st.markdown(f'<div class="result-row">Detected Category : <span class="bold-value">{auto_data["category"]}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-row">Priority : <span class="bold-value">{priority}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-row">Department : <span class="bold-value">{auto_data["team_display"]}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-row">Remote Resolvable : <span class="bold-value">{auto_data["remote"]}</span></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown(f'<div class="result-row">Input Record Duration : <span class="bold-value">{actual_duration_hours:.2f} Hours</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-row">Predicted Target Baseline : <span class="bold-value">{pred_resolution} Hours</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-row">SLA Limit Target : <span class="bold-value">{sla_hours} Hours</span></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown(f'<div class="result-row">Risk Score : <span class="bold-value">{risk_score}%</span></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        if is_breached:
            st.error(f"⚠ Possible SLA Breach Risk Flagged for {priority} Priority")
            st.markdown(f'<div class="result-row" style="margin-top: 15px;"><span class="bold-value" style="color: #D97706;">🚨 Required Precautions to Avoid Breach ({sla_hours}h Limit):</span></div>', unsafe_allow_html=True)
            precautions_html = "".join([f"<li>{p}</li>" for p in PRIORITY_PRECAUTIONS[priority]])
            st.markdown(f'<div class="precaution-box"><ul>{precautions_html}</ul></div>', unsafe_allow_html=True)
        else:
            st.success(f"✅ SLA Likely To Meet for {priority} Priority")
            st.markdown(f'<div class="result-row" style="margin-top: 15px;"><span class="bold-value" style="color: #059669;">🛡 Standard Protocol Checklist ({sla_hours}h Limit):</span></div>', unsafe_allow_html=True)
            precautions_html = "".join([f"<li>{p}</li>" for p in PRIORITY_PRECAUTIONS[priority]])
            st.markdown(f'<div class="precaution-box" style="border-left-color: #10B981; background-color: #ECFDF5;"><ul>{precautions_html}</ul></div>', unsafe_allow_html=True)
            
        st.markdown('<div class="result-row" style="margin-top: 15px;"><span class="bold-value">Common Reasons for Potential SLA Breach:</span></div>', unsafe_allow_html=True)
        reasons_html = "".join([f"<li>{r}</li>" for r in auto_data["reasons"]])
        st.markdown(f'<div class="reason-box"><ul>{reasons_html}</ul></div>', unsafe_allow_html=True)
            
    except FileNotFoundError:
        st.error("Model tracking error: Ensure 'preprocessor.pkl', 'rfe_selector.pkl', and 'SLA_prediction_model.pkl' are saved inside this exact script folder directory.")
    except Exception as e:
        st.error(f"Execution processing breakdown error: {e}")