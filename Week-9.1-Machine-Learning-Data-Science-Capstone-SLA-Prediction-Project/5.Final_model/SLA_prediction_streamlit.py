import streamlit as st
import pandas as pd
import joblib

# Set page configuration
st.set_page_config(
    page_title="SLA Breach Prediction Portal",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a clean look
st.markdown("""
    <style>
    .main-header {
        font-size: 32px !important;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 5px;
    }
    .sub-header {
        font-size: 16px !important;
        color: #4B5563;
        margin-bottom: 25px;
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
# This replicates the natural routing logic found in your preprocessed dataset rows
DEPARTMENT_ROUTING = {
    "Network Outage": "Network Team",
    "Database Failure": "Database Admin",
    "Server Crash": "Database Admin",
    "Application Bug": "IT Support",
    "Security Breach": "Security Team"
}

# Department master list to keep track of drop-down indexing positions
DEPARTMENTS = ["Security Team", "Database Admin", "Network Team", "IT Support"]

# ----------------- MAIN UI -----------------
st.markdown('<div class="main-header">SLA Breach Prediction Portal</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Input data features to monitor target turnaround metrics and predict SLA breaches.</div>', unsafe_allow_html=True)

if preprocessor and rfe and model:
    
    st.markdown("### 📋 Enter Incident Details")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        incident_id = st.text_input("Incident ID", value="INC100000")
        
        # 1. User picks the Incident Type first
        incident_type = st.selectbox(
            "Incident Type", 
            ["Network Outage", "Database Failure", "Server Crash", "Application Bug", "Security Breach"]
        )
        
        # 2. Extract the recommended target department automatically based on selection
        automatically_selected_dept = DEPARTMENT_ROUTING.get(incident_type, "IT Support")
        
        # 3. Match the correct text position array index for the drop-down box baseline
        default_index = DEPARTMENTS.index(automatically_selected_dept) if automatically_selected_dept in DEPARTMENTS else 0
        
        # 4. Display drop-down with the automated selection preset dynamically
        assigned_dept = st.selectbox(
            "Assigned Department (Auto-Selected)", 
            options=DEPARTMENTS,
            index=default_index,
            help="This field automatically configures its department based on your chosen Incident Type."
        )
        
        priority = st.selectbox("Priority Level", ["Low", "Medium", "High", "Critical"])

    with col2:
        location = st.selectbox(
            "Location Context", 
            ["Data Center A", "Data Center B", "Head Office", "Remote Site 1", "Remote Site 2"]
        )
        status = st.selectbox("Current Status", ["Resolved", "Closed", "In Progress"])
        res_type = st.selectbox(
            "Resolution Type", 
            ["Reboot", "Patch Applied", "Configuration Fix", "Hardware Replacement"]
        )
        sla_limit = st.number_input("SLA Limit (Hours)", min_value=1, max_value=168, value=24)

    with col3:
        res_time = st.number_input("Resolution Time (Hours)", min_value=0.0, max_value=200.0, value=18.0)
        hour = st.slider("Creation Hour (0-23)", 0, 23, 4)
        day = st.slider("Day of the Week (0=Mon, 6=Sun)", 0, 6, 6)
        month = st.slider("Month of the Year (1-12)", 1, 12, 3)

    st.markdown("---")
    
    # Action Buttons
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
            
        except Exception as pred_error:
            st.error(f"Inference pipeline execution error: {pred_error}")

    # ----------------- DISPLAY RESULTS TABLE -----------------
    if st.session_state.prediction_history:
        st.markdown("### 📊 Prediction Log Table")
        
        history_df = pd.DataFrame(st.session_state.prediction_history)
        
        cols_order = ["Incident_ID", "Prediction_Result", "Incident_Type", "Priority", 
                      "Assigned_Department", "SLA_Limit", "Resolution_Time_Hours", 
                      "Status", "Location", "Resolution_Type", "Hour", "Day", "Month"]
        
        history_df = history_df[cols_order]
        
        def highlight_status(val):
            if val == "⚠️ BREACH":
                return "background-color: #FEE2E2; color: #991B1B; font-weight: bold;"
            elif val == "✅ COMPLIANT":
                return "background-color: #DCFCE7; color: #166534; font-weight: bold;"
            return ""

        styled_df = history_df.style.applymap(highlight_status, subset=["Prediction_Result"])
        st.dataframe(styled_df, use_column_width=True, hide_index=True)

else:
    st.warning("Missing model infrastructure files. Please check workspace directories for deployment artifacts.")