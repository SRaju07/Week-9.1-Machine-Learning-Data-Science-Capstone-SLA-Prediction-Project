import streamlit as st
import pandas as pd
import joblib

# Set page configuration for an enterprise software interface
st.set_page_config(
    page_title="SLA Breach Prediction Portal",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS Dashboard layout styling
st.markdown("""
    <style>
    .main-header {
        font-size: 32px !important;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 2px;
    }
    .sub-header {
        font-size: 15px !important;
        color: #4B5563;
        margin-bottom: 25px;
    }
    .card-container {
        display: flex;
        gap: 15px;
        margin-bottom: 25px;
    }
    .kpi-card {
        flex: 1;
        background-color: #F8FAFC;
        padding: 15px 20px;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #3B82F6;
    }
    .kpi-title {
        font-size: 12px;
        color: #64748B;
        text-transform: uppercase;
        font-weight: 600;
    }
    .kpi-value {
        font-size: 22px;
        font-weight: 700;
        color: #1E293B;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize a session state list to store prediction history tables
if "prediction_history" not in st.session_state:
    st.session_state.prediction_history = []

# ----------------- LOAD ARTIFACTS -----------------
@st.cache_resource
def load_models():
    try:
        preprocessor = joblib.load("preprocessor.pkl")
        rfe = joblib.load("rfe_selector.pkl")
        model = joblib.load("SLA_prediction_model.pkl")
        return preprocessor, rfe, model
    except Exception as e:
        st.error(f"Error loading model pkl files: {e}")
        return None, None, None

preprocessor, rfe, model = load_models()

# ----------------- AUTOMATION ROUTING MAPPING -----------------
DEPARTMENT_ROUTING = {
    "Network Outage": "Network Team",
    "Database Failure": "Database Admin",
    "Server Crash": "Database Admin",
    "Application Bug": "IT Support",
    "Security Breach": "Security Team"
}

DEPARTMENTS = ["Security Team", "Database Admin", "Network Team", "IT Support"]

# ----------------- MAIN HEADER UI -----------------
st.markdown('<div class="main-header">SLA Breach Prediction Portal</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Production-ready operational management platform for monitoring incident compliance targets.</div>', unsafe_allow_html=True)

if preprocessor and rfe and model:
    
    # ----------------- LIVE METRICS COUNTERS -----------------
    total_runs = len(st.session_state.prediction_history)
    breaches_count = sum(1 for item in st.session_state.prediction_history if "⚠️ BREACH" in item.values())
    compliance_rate = f"{( (total_runs - breaches_count) / total_runs * 100):.1f}%" if total_runs > 0 else "100%"

    st.markdown(f"""
        <div class="card-container">
            <div class="kpi-card">
                <div class="kpi-title">Total Incidents Evaluated</div>
                <div class="kpi-value">{total_runs}</div>
            </div>
            <div class="kpi-card" style="border-left-color: #EF4444;">
                <div class="kpi-title">Predicted SLA Breaches</div>
                <div class="kpi-value" style="color: #B91C1C;">{breaches_count}</div>
            </div>
            <div class="kpi-card" style="border-left-color: #10B981;">
                <div class="kpi-title">Expected Compliance Rate</div>
                <div class="kpi-value" style="color: #047857;">{compliance_rate}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ----------------- INPUT CONTROLS FORM -----------------
    st.markdown("### 📋 Enter Incident Details")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        incident_id = st.text_input("Incident ID", value="INC100000")
        incident_type = st.selectbox(
            "Incident Type", 
            ["Network Outage", "Database Failure", "Server Crash", "Application Bug", "Security Breach"]
        )
        automatically_selected_dept = DEPARTMENT_ROUTING.get(incident_type, "IT Support")
        default_index = DEPARTMENTS.index(automatically_selected_dept) if automatically_selected_dept in DEPARTMENTS else 0
        
        assigned_dept = st.selectbox(
            "Assigned Department (Auto-Selected)", 
            options=DEPARTMENTS,
            index=default_index,
            help="Dynamically updates based on the picked Incident Type to maintain structural data parity."
        )

    with col2:
        priority = st.selectbox("Priority Level", ["Low", "Medium", "High", "Critical"])
        location = st.selectbox(
            "Location Context", 
            ["Data Center A", "Data Center B", "Head Office", "Remote Site 1", "Remote Site 2"]
        )
        status = st.selectbox("Current Status", ["Resolved", "Closed", "In Progress"])

    with col3:
        res_type = st.selectbox(
            "Resolution Type", 
            ["Reboot", "Patch Applied", "Configuration Fix", "Hardware Replacement"]
        )
        sla_limit = st.number_input("SLA Limit (Hours)", min_value=1, max_value=168, value=24)
        res_time = st.number_input("Resolution Time (Hours)", min_value=0.0, max_value=200.0, value=18.0)

    # Hidden or calculated date/time components out of view to keep user forms clean
    hour, day, month = 4, 6, 3

    st.markdown("---")
    
    # Action Row Configuration
    btn_col1, btn_col2, _ = st.columns([1.5, 1, 4])
    with btn_col1:
        submit_btn = st.button("🚀 Analyze SLA Performance", use_column_width=True, type="primary")
    with btn_col2:
        clear_btn = st.button("🗑️ Clear Log History", use_column_width=True)

    if clear_btn:
        st.session_state.prediction_history = []
        st.rerun()

    if submit_btn:
        input_data = {
            "Incident_ID": incident_id,
            "Incident_Type": incident_type,
            "Priority": priority,
            "Assigned_Department": assigned_dept,
            "Location": location,
            "Status": status,
            "Resolution_Type": res_type,
            "Resolution_Time_Hours": res_time,
            "Hour": hour,
            "Day": day,
            "Month": month,
            "SLA_Limit": sla_limit
        }
        
        input_df = pd.DataFrame([input_data])
        
        try:
            X_encoded = preprocessor.transform(input_df)
            X_selected = rfe.transform(X_encoded)
            prediction = model.predict(X_selected)[0]
            
            input_data["Prediction_Result"] = "⚠️ BREACH" if prediction == 1 else "✅ COMPLIANT"
            st.session_state.prediction_history.insert(0, input_data)
            st.rerun() # Refresh layout metrics cleanly
            
        except Exception as pred_error:
            st.error(f"Inference pipeline execution error: {pred_error}")

    # ----------------- DISPLAY INTERACTIVE TABLE LOG -----------------
    if st.session_state.prediction_history:
        st.markdown("### 📊 Prediction Log Table")
        
        history_df = pd.DataFrame(st.session_state.prediction_history)
        cols_order = ["Incident_ID", "Prediction_Result", "Incident_Type", "Priority", 
                      "Assigned_Department", "SLA_Limit", "Resolution_Time_Hours", "Status", "Location"]
        history_df = history_df[cols_order]
        
        # Color coding logic rules
        def highlight_status(val):
            if val == "⚠️ BREACH":
                return "background-color: #FEE2E2; color: #991B1B; font-weight: bold; text-align: center;"
            elif val == "✅ COMPLIANT":
                return "background-color: #DCFCE7; color: #166534; font-weight: bold; text-align: center;"
            return ""

        styled_df = history_df.style.applymap(highlight_status, subset=["Prediction_Result"])
        st.dataframe(styled_df, use_column_width=True, hide_index=True)

else:
    st.warning("Workspace missing model assets. Please check root workspace paths for `.pkl` files.")