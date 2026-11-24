"""
🌿 Hawa Saathi (हवा साथी)
GenAI-Powered Winter Smog & Urban Air Pollution Companion
For Families and Communities.
"""

import os
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from PIL import Image
from dotenv import load_dotenv

# Load local modules
from src.aqi_engine import PRESET_CITIES, pm25_to_aqi, simulate_24h_inversion, compute_inhaled_dose
from src.impact_calculator import calculate_commute_impact, calculate_iaq_hack_impact
from src.genai_service import GenAIService

load_dotenv()

# Streamlit Page Config
st.set_page_config(
    page_title="Hawa Saathi (हवा साथी) — Clean Air Companion",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Quality Styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0F2027 0%, #203A43 50%, #2C5364 100%);
        padding: 24px 30px;
        border-radius: 16px;
        color: #ffffff;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        margin-bottom: 6px;
        letter-spacing: -0.5px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #B0BEC5;
        font-weight: 400;
        margin-bottom: 0px;
    }
    .metric-card {
        background: #ffffff;
        padding: 18px 20px;
        border-radius: 12px;
        border: 1px solid #E0E0E0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 12px;
    }
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-right: 6px;
    }
    .badge-danger { background-color: #FFEBEE; color: #C62828; border: 1px solid #FFCDD2; }
    .badge-caution { background-color: #FFF8E1; color: #F57F17; border: 1px solid #FFE082; }
    .badge-optimal { background-color: #E8F5E9; color: #2E7D32; border: 1px solid #A5D6A7; }
    .badge-safe { background-color: #E3F2FD; color: #1565C0; border: 1px solid #90CAF9; }
    .timeline-card {
        background-color: #fcfcfc;
        border-left: 5px solid #203A43;
        padding: 16px 20px;
        border-radius: 4px 10px 10px 4px;
        margin-bottom: 16px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    .sos-card {
        background: linear-gradient(135deg, #b71c1c 0%, #d32f2f 100%);
        color: white;
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "routine_plan" not in st.session_state:
    st.session_state.routine_plan = None
if "vision_result" not in st.session_state:
    st.session_state.vision_result = None

# Sidebar Configuration
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=300&auto=format&fit=crop&q=60", caption="Breathe Clean • Save Lives")
    st.markdown("### ⚙️ Location & Environmental Settings")
    
    selected_city_name = st.selectbox(
        "Select Urban Region / Hotspot:",
        list(PRESET_CITIES.keys()),
        index=0
    )
    city_data = PRESET_CITIES[selected_city_name]

    # Override sliders
    st.markdown("#### 🌡️ Atmospheric Conditions")
    pm25_input = st.slider(
        "Current PM2.5 Concentration (µg/m³):",
        min_value=10,
        max_value=650,
        value=city_data["base_pm25"],
        step=5,
        help="CPCB Severe threshold begins at 250 µg/m³. WHO safe 24-hr guideline is 15 µg/m³."
    )
    
    st.markdown(f"**Dominant Smog Sources:**\n*{city_data['primary_source']}*")
    st.markdown(f"**Inversion Dynamics:** `{city_data['inversion_strength']}`")

    st.markdown("---")
    st.markdown("### 🔑 GenAI Configuration")
    api_key_env = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    user_api_key = st.text_input(
        "Google Gemini API Key:",
        value=api_key_env,
        type="password",
        help="Powered by Gemini 4 Hydrogen & Multimodal Vision. If blank, smart environmental heuristic models will run seamlessly."
    )

    genai_client = GenAIService(api_key=user_api_key)
    if genai_client.is_live():
        st.success("🟢 Google Gemini Live Agent Active (gemini-4-hydrogen)")
    else:
        st.info("🟡 Smart Environmental Heuristic Engine (Offline / Demo Mode)")

    st.markdown("---")
    st.markdown("### 🗣️ Vernacular Language")
    lang_choice = st.radio("Display & Voice Language:", ["English", "हिन्दी (Hindi)"], index=0)


# Compute Live AQI info
aqi_data = pm25_to_aqi(pm25_input)
inversion_data = simulate_24h_inversion(pm25_input)

# Top Banner Header
st.markdown(f"""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <div class="main-title">🌿 Hawa Saathi (हवा साथी)</div>
            <div class="sub-title">GenAI Urban Smog & Clean Air Companion • Protecting Families & Communities</div>
        </div>
        <div style="text-align: right; margin-top: 10px;">
            <span style="font-size: 0.9rem; background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 20px;">
                📍 {selected_city_name.split('(')[0]}
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Top Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        label="Ambient PM2.5",
        value=f"{pm25_input} µg/m³",
        delta=f"{round((pm25_input/15), 1)}x WHO Limit",
        delta_color="inverse"
    )
with col2:
    st.metric(
        label="Calculated CPCB AQI",
        value=f"{aqi_data['aqi']}",
        delta=aqi_data["category"],
        delta_color="off"
    )
with col3:
    st.metric(
        label="Thermal Inversion Lock",
        value=city_data["inversion_strength"],
        help="Night radiation cooling traps surface emissions until solar boundary-layer mixing at midday."
    )
with col4:
    st.metric(
        label="Safe Outdoor Window",
        value="12:00 PM – 03:00 PM",
        help="Period of deepest thermal convection when surface PM2.5 drops by 30-45%."
    )

# Main Navigation Tabs
tab_radar, tab_planner, tab_iaq, tab_impact, tab_chat = st.tabs([
    "📡 Smog Radar & Inversion",
    "🗓️ GenAI Routine Optimizer",
    "🔬 IAQ & DIY Clean Air Lab",
    "📊 Lifestyle & Community Impact",
    "💬 Hawa Saathi Assistant & SOS"
])


# ==========================================
# TAB 1: SMOG RADAR & INVERSION SCIENCE
# ==========================================
with tab_radar:
    st.subheader("24-Hour Diurnal Boundary Layer & Smog Inversion Curve")
    st.markdown(
        "During severe winter smog, cold night air is pinned beneath a warm upper thermal lid (**temperature inversion**). "
        "Ground-level $\\text{PM}_{2.5}$ surges between **midnight and 8:00 AM**, but drops during the **midday solar mixing window** (12:00 PM – 3:00 PM)."
    )

    df_inv = pd.DataFrame(inversion_data)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_inv["time_label"],
        y=df_inv["pm25"],
        mode='lines+markers',
        name='PM2.5 Concentration (µg/m³)',
        line=dict(color='#D32F2F', width=3),
        fill='tozeroy',
        fillcolor='rgba(211, 47, 47, 0.15)'
    ))

    # Add safe window rectangle
    fig.add_vrect(
        x0="11:00", x1="15:00",
        fillcolor="#4CAF50", opacity=0.15,
        layer="below", line_width=1,
        annotation_text="Optimal Solar Mixing Window (Lowest Smog Exposure)",
        annotation_position="top left"
    )

    fig.update_layout(
        title="Hourly Ground PM2.5 Trapping vs. Thermal Convection",
        xaxis_title="Time of Day (24-Hour Winter Cycle)",
        yaxis_title="PM2.5 (µg/m³)",
        template="plotly_white",
        height=400,
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("🫁 Family Physiological Inhaled Dose Calculator")
    st.markdown("See the direct physical mass of sub-micron toxic particulate inhaled into family lung tissue under different routines:")

    col_dose1, col_dose2, col_dose3 = st.columns(3)
    with col_dose1:
        dose_hours = st.slider("Hours spent outdoors or unsealed:", 0.5, 8.0, 2.5, 0.5)
    with col_dose2:
        activity = st.selectbox(
            "Exertion / Activity Intensity:",
            [
                ("resting", "Resting / Sleeping (0.45 m³/h)"),
                ("sedentary", "Sedentary / Light Office / School (0.60 m³/h)"),
                ("moderate_walk", "Moderate Walking / Commuting (1.20 m³/h)"),
                ("vigorous_exercise", "Outdoor Jogging / Cycling (2.40 m³/h)")
            ],
            format_func=lambda x: x[1]
        )[0]
    with col_dose3:
        mask_protection = st.selectbox(
            "Masking Protection Factor:",
            [
                (0.0, "No Mask / Bare Breathing (0% filtration)"),
                (0.20, "Cloth Mask / Handkerchief (~20% filtration)"),
                (0.40, "Surgical Blue Mask (~40% filtration due to edge leaks)"),
                (0.95, "Fitted N95 / FFP2 Respirator (95% filtration)")
            ],
            format_func=lambda x: x[1]
        )[0]

    effective_pm25 = pm25_input * (1.0 - mask_protection)
    dose_res = compute_inhaled_dose(effective_pm25, dose_hours, activity)

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric(
            label="Inhaled PM2.5 Particulate Mass",
            value=f"{dose_res['inhaled_ug']} µg",
            help="Sub-2.5 micron particles deposit directly across the alveolar membrane into the bloodstream."
        )
    with col_m2:
        st.metric(
            label="Equivalent Cigarette Smoked",
            value=f"{dose_res['cig_equivalent']} cigarettes",
            delta=f"Based on Berkeley Earth inhalation ratio",
            delta_color="inverse"
        )
    with col_m3:
        if mask_protection >= 0.95:
            st.success("🛡️ Excellent! N95 filtration reduced alveolar toxic deposition by 95%.")
        elif mask_protection == 0.0:
            st.error("⚠️ Danger! High particulate deposition. Switch to N95 immediately.")
        else:
            st.warning("⚠️ Cloth/Surgical masks have high peripheral leakage for micro-particles.")


# ==========================================
# TAB 2: GENAI DYNAMIC ROUTINE OPTIMIZER
# ==========================================
with tab_planner:
    st.subheader("🗓️ GenAI Low-Emission Daily Routine Planner")
    st.markdown(
        "Tailors an hour-by-hour schedule around the **diurnal atmospheric inversion cycle** to shield vulnerable family members, "
        "cut commute emissions, and identify the exact moments for safe errand-running and clean-air room maintenance."
    )

    with st.expander("👤 Customize Your Family & Household Profile", expanded=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            family_members = st.multiselect(
                "Household Vulnerable Demographics:",
                [
                    "Infants / Toddlers (< 5 yrs)",
                    "School-going Children (5-16 yrs)",
                    "Senior Citizens (65+ yrs)",
                    "Asthmatic / COPD / Heart Patients",
                    "Pregnant Individuals",
                    "Outdoor Daily Commuter / Delivery Worker",
                    "Household Pets (Dogs/Cats)"
                ],
                default=["School-going Children (5-16 yrs)", "Senior Citizens (65+ yrs)"]
            )
        with col_f2:
            commute_type = st.selectbox(
                "Primary Commute Mode:",
                [
                    "Solo Petrol/Diesel Car",
                    "Two-Wheeler (Motorcycle/Scooter)",
                    "Shared Cab / Auto-Rickshaw",
                    "Carpool (3-4 People)",
                    "Electric Metro / Electric Bus",
                    "Work From Home (Zero Commute)"
                ],
                index=0
            )
        with col_f3:
            housing_type = st.selectbox(
                "Housing & Ventilation Setup:",
                [
                    "High-rise Apartment (Floor 8+) with Balcony",
                    "Mid-rise Flat (Floor 2-7)",
                    "Ground Floor / Independent House near Main Road",
                    "Older Building with High Window Drafts / Gaps"
                ],
                index=1
            )

    if st.button("✨ Generate AI Daily Smog Navigation Routine", type="primary"):
        with st.spinner("Analyzing atmospheric inversion models & synthesizing family schedule with Gemini 4..."):
            routine = genai_client.generate_routine(
                city=selected_city_name,
                current_pm25=pm25_input,
                family_members=family_members,
                commute_type=commute_type,
                housing_type=housing_type,
                language=lang_choice
            )
            st.session_state.routine_plan = routine

    if st.session_state.routine_plan:
        plan = st.session_state.routine_plan
        
        # Audio / Morning Briefing Player
        st.markdown(f"""
        <div style="background: #E8F0FE; border-left: 5px solid #1A73E8; padding: 16px 20px; border-radius: 8px; margin: 20px 0;">
            <div style="font-weight: 700; color: #174EA6; font-size: 1.1rem; margin-bottom: 6px;">
                📢 Hawa Saathi Morning Verbal Briefing / प्रात:कालीन संदेश:
            </div>
            <div style="font-size: 1rem; color: #202124; line-height: 1.5;">
                <em>"{plan.get('morning_briefing_hindi', 'सुप्रभात। आज भारी धुंध के कारण सुबह की सैर टालें और दोपहर के धूप वाले समय में ही आवश्यक काम करें।')}"</em>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Audio synthesizer button using Web Speech API
        briefing_text = plan.get('morning_briefing_hindi', '')
        st.components.v1.html(f"""
        <button onclick="speakBriefing()" style="background-color: #1A73E8; color: white; border: none; padding: 8px 16px; border-radius: 20px; font-weight: bold; cursor: pointer; display: inline-flex; align-items: center; gap: 8px;">
            🔊 Listen to Audio Briefing (आवाज़ सुनें)
        </button>
        <script>
            function speakBriefing() {{
                if ('speechSynthesis' in window) {{
                    window.speechSynthesis.cancel();
                    var msg = new SpeechSynthesisUtterance({repr(briefing_text)});
                    msg.lang = 'hi-IN';
                    msg.rate = 0.95;
                    window.speechSynthesis.speak(msg);
                }} else {{
                    alert('Web Speech API not supported on this browser.');
                }}
            }}
        </script>
        """, height=50)

        # Executive Summary & Risk Badge
        st.markdown(f"**Atmospheric Assessment:** {plan.get('summary', '')}")
        
        col_sum1, col_sum2 = st.columns(2)
        with col_sum1:
            st.metric("Personal PM2.5 Exposure Avoided", f"~{plan.get('personal_impact_grams_pm25_avoided', 3.8)} g", help="Calculated based on shifted commute and indoor sealing")
        with col_sum2:
            st.metric("Community Carbon Offset", f"~{plan.get('community_emission_kg_co2_offset', 4.8)} kg CO2", help="Through recommended transit and zero-combustion choices")

        st.markdown("### 🕒 Optimized Daily Itinerary")

        schedule = plan.get("schedule", [])
        badge_classes = {
            "DANGEROUS": "badge badge-danger",
            "CAUTION": "badge badge-caution",
            "OPTIMAL_WINDOW": "badge badge-optimal",
            "SAFE": "badge badge-safe"
        }

        for item in schedule:
            badge_class = badge_classes.get(item.get("outdoor_safety_level", "CAUTION"), "badge badge-caution")
            st.markdown(f"""
            <div class="timeline-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-weight: 800; font-size: 1.1rem; color: #203A43;">⏱️ {item.get('time_slot')} — {item.get('activity_title')}</span>
                    <span class="{badge_class}">{item.get('outdoor_safety_level')}</span>
                </div>
                <p style="margin-bottom: 6px;"><strong>🏃 Recommended Action:</strong> {item.get('recommended_action')}</p>
                <p style="margin-bottom: 6px;"><strong>🌱 Low-Emission Hack:</strong> {item.get('emission_hack')}</p>
                <p style="margin-bottom: 6px;"><strong>🏠 Indoor Air Step:</strong> {item.get('indoor_iaq_step')}</p>
                <p style="margin-bottom: 0px; color: #C62828;"><strong>⚠️ Vulnerable Member Alert:</strong> {item.get('vulnerable_alert')}</p>
            </div>
            """, unsafe_allow_html=True)


# ==========================================
# TAB 3: IAQ & DIY CLEAN AIR LAB
# ==========================================
with tab_iaq:
    st.subheader("🔬 Indoor Air Quality (IAQ) Bio-Hacks & Multimodal Vision Lab")
    st.markdown(
        "Outdoor smog infiltrates standard homes through door undercuts, window sashes, and AC conduit sleeves. "
        "Use GenAI Multimodal Vision to inspect your room, filter, or DIY box fan, or explore our proven DIY filtration recipes."
    )

    st.markdown("#### 📸 Multimodal Room & Filter Vision Inspector")
    st.markdown("Upload a photo of your **Air Purifier Filter**, **Window Frame / Gaps**, or **Living Room**, and Gemini Vision will diagnose saturation and leakage.")

    sample_col1, sample_col2, sample_col3 = st.columns(3)
    sample_choice = None
    with sample_col1:
        if st.button("🖼️ Test Sample: Used HEPA Filter"):
            sample_choice = "sample_images/sample_hepa_filter.jpg"
    with sample_col2:
        if st.button("🖼️ Test Sample: Window Sash Draft Gap"):
            sample_choice = "sample_images/sample_window_gap.jpg"
    with sample_col3:
        if st.button("🖼️ Test Sample: DIY Box Fan Build"):
            sample_choice = "sample_images/sample_diy_box_fan.jpg"

    uploaded_file = st.file_uploader("Or Upload Your Own Photo (JPEG/PNG):", type=["jpg", "jpeg", "png"])

    img_to_inspect = None
    if uploaded_file is not None:
        img_to_inspect = Image.open(uploaded_file)
    elif sample_choice and os.path.exists(sample_choice):
        img_to_inspect = Image.open(sample_choice)

    if img_to_inspect:
        col_img, col_diag = st.columns([1, 2])
        with col_img:
            st.image(img_to_inspect, caption="Image for GenAI Forensic Inspection", use_container_width=True)
            custom_q = st.text_input("Specific query for the AI inspector (optional):", "Inspect this filter/room for smog vulnerability and suggest fixes.")
            if st.button("🔍 Run GenAI Vision Diagnostic", type="primary"):
                with st.spinner("Analyzing particulate saturation & structural drafts with Gemini 4 Vision..."):
                    st.session_state.vision_result = genai_client.analyze_room_or_filter_image(img_to_inspect, custom_q)

        with col_diag:
            if st.session_state.vision_result:
                res = st.session_state.vision_result
                st.markdown(res["analysis_text"])
                st.caption(f"Engine: {res['source']}")

    st.markdown("---")
    st.subheader("🛠️ The DIY Corsi-Rosenthal Box Air Cleaner Wizard")
    st.markdown(
        "A **Corsi-Rosenthal Box** is an open-source, scientifically validated air purifier built with 4 MERV-13 filters and a standard 20-inch box fan. "
        "It achieves a CADR (Clean Air Delivery Rate) of **400–600 CFM**, outperforming commercial $250+ units for just **~$35 (₹2,500)**."
    )

    col_cr1, col_cr2 = st.columns(2)
    with col_cr1:
        st.markdown("""
        **Essential Components:**
        - **1x 20-inch Box Fan** (approx. 50W)
        - **4x MERV-13 Pleated HVAC Filters** (20" x 20" x 2")
        - **1x Roll of Heavy Duct Tape / Painter's Tape**
        - **1x Cardboard Box** (for base and circular fan shroud)
        
        **Assembly Steps:**
        1. Form a cube with the 4 filters; ensure the airflow direction arrows face **inward** toward the fan cavity.
        2. Tape all vertical filter seams airtight with duct tape.
        3. Tape the cardboard square to seal the bottom floor.
        4. Place the fan on top pointing **upward** (exhausting clean air into the room).
        5. **Pro-Tip (The Cardboard Shroud):** Cut a 16-inch circular hole in a piece of cardboard and tape it over the front face of the fan. This blocks the dead corners of the fan blades and boosts CADR by **20%**!
        """)
    with col_cr2:
        room_sqft = st.slider("Select Target Room Size (sq ft):", 100, 800, 250, 25)
        calc_hack = calculate_iaq_hack_impact(room_sqft, pm25_input, "diy_corsi_rosenthal")
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>📈 Performance in your {room_sqft} sq ft room:</h4>
            <p><strong>Predicted Indoor PM2.5:</strong> <span style="font-size: 1.3rem; color: #2E7D32; font-weight: bold;">{calc_hack['indoor_pm25']} µg/m³</span> (Down from {pm25_input} µg/m³)</p>
            <p><strong>Air Changes per Hour (ACH):</strong> <strong>{calc_hack['ach']} ACH</strong> (Hospital standard is > 6 ACH)</p>
            <p><strong>Time to 50% Air Purge:</strong> <strong>~{calc_hack['time_to_50pct_clean_min']} minutes</strong></p>
            <p><strong>Estimated Build Cost:</strong> <strong>${calc_hack['cost_est_usd']} (~₹2,800)</strong> vs Commercial Equivalent <strong>$220 (~₹18,000)</strong></p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🌿 Bedroom Phytoremediation (Natural Clean-Air Bio-Wall)")
    st.markdown("NASA Clean Air Study and Delhi IIT research showed specific plants optimize indoor oxygenation and VOC removal:")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.markdown("""
        **🌱 Snake Plant (Mother-in-Law's Tongue)**
        - **Mechanism:** CAM Photosynthesis (opens stomata at night, releases O2 while you sleep).
        - **Placement:** Bedroom (head of bed).
        - **Dose:** 4-6 waist-high plants per person.
        """)
    with col_p2:
        st.markdown("""
        **🌴 Areca Palm (Dypsis Lutescens)**
        - **Mechanism:** High daytime transpiration & oxygenation; natural humidifier for dry winter smog.
        - **Placement:** Living Room / Work desk.
        - **Dose:** 3-4 shoulder-high plants per person.
        """)
    with col_p3:
        st.markdown("""
        **🕷️ Spider Plant (Chlorophytum Comosum)**
        - **Mechanism:** Rapid breakdown of carbon monoxide, formaldehyde, and benzene from traffic exhaust.
        - **Placement:** Kitchen & entryway threshold.
        - **Dose:** 2-3 hanging pots.
        """)


# ==========================================
# TAB 4: LIFESTYLE & COMMUNITY IMPACT
# ==========================================
with tab_impact:
    st.subheader("📊 Sustainable Lifestyle & Community Action Engine")
    st.markdown(
        "Individual and collective choices make a measurable difference in peak winter smog. "
        "Quantify your personal footprint reduction and lead neighborhood anti-smog initiatives."
    )

    col_imp1, col_imp2 = st.columns(2)
    with col_imp1:
        st.markdown("#### 🚗 Commute Mode Switcher")
        commute_dist = st.slider("One-Way Commute Distance (km):", 2, 45, 14, 1)
        base_mode = st.selectbox(
            "Current Baseline Mode:",
            [
                ("solo_petrol_car", "Solo Petrol Car"),
                ("solo_diesel_car", "Solo Diesel Car"),
                ("two_wheeler_petrol", "Petrol Two-Wheeler / Scooter")
            ],
            format_func=lambda x: x[1]
        )[0]
        alt_mode = st.selectbox(
            "Sustainable Alternative:",
            [
                ("electric_metro_rail", "Electric Metro Rail"),
                ("electric_bus", "Electric City Bus"),
                ("carpool_4_people", "Carpool (4 Passengers)"),
                ("ev_two_wheeler", "Electric Scooter (EV)"),
                ("bicycle_walk", "Bicycle / Walking (with N95)")
            ],
            format_func=lambda x: x[1]
        )[0]

        res_commute = calculate_commute_impact(commute_dist, base_mode, alt_mode)

        st.markdown(f"""
        <div class="metric-card">
            <h4>🌿 Monthly Commute Savings:</h4>
            <ul>
                <li><strong>Tailpipe PM2.5 Prevented:</strong> <span style="color: #2E7D32; font-weight: bold;">{res_commute['monthly_pm25_saved_g']} grams</span></li>
                <li><strong>CO2e Greenhouse Gas Avoided:</strong> <span style="color: #2E7D32; font-weight: bold;">{res_commute['monthly_co2_saved_kg']} kg CO2</span></li>
                <li><strong>Volume of Clean Air Preserved:</strong> <strong>{res_commute['clean_air_m3_preserved']:,.0f} m³</strong></li>
                <li><strong>Equivalent Mature Tree Absorptions:</strong> <strong>{res_commute['tree_months_equivalent']} tree-months</strong></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_imp2:
        st.markdown("#### 🪵 Clean Winter Heating Transition")
        st.markdown(
            "A single evening coal/biomass brazier (*Angithi*) emits over **340 grams of toxic PM2.5 and 120 grams of carbon monoxide**, "
            "directly exposing security guards and families in enclosed spaces."
        )

        heating_choice = st.radio(
            "Heating Intervention:",
            [
                "Switch coal/wood angithi to electric oil-filled radiator",
                "Provide insulated wind-proof cabins & thermals to night guards",
                "Stop open roadside dry leaf / trash combustion"
            ]
        )

        if "angithi" in heating_choice:
            st.info("💡 **Impact:** Eliminates ~10.2 kg of toxic sub-micron particulates and 3.6 kg of carbon monoxide per household each month!")
        elif "guards" in heating_choice:
            st.success("🛡️ **Community Action:** Supplying thermal jackets and insulated security booths eliminates the need for open fire burning by neighborhood guards.")
        else:
            st.warning("🍂 **Leaf Composting:** Composting dry fallen leaves instead of burning spares 160g of PM2.5 and 45g of carcinogenic VOCs per 10kg pile.")

    st.markdown("---")
    st.subheader("📢 Community RWA Anti-Smog Notice Generator")
    st.markdown("Quickly generate a professional, persuasive notice for your Resident Welfare Association (RWA) or neighborhood WhatsApp group:")

    col_rwa1, col_rwa2 = st.columns([1, 2])
    with col_rwa1:
        notice_type = st.selectbox(
            "Notice Objective:",
            [
                "Strict Ban on Open Biomass & Leaf Burning",
                "Community Carpooling & Reduced Vehicle Movement",
                "Anti-Smog Dust Misting & Sweeping Protocol",
                "Support Scheme for Guard Heating Thermals"
            ]
        )
        society_name = st.text_input("Society / Colony Name:", "Green Park Residency")
        gen_notice_btn = st.button("📝 Generate Official RWA Notice")

    with col_rwa2:
        if gen_notice_btn:
            notice_text = f"""
**OFFICIAL ADVISORY: WINTER SMOG EMERGENCY ACTION**
**Issued by:** Managing Committee, {society_name}
**Current Air Quality:** Severe (PM2.5: {pm25_input} µg/m³ | AQI: {aqi_data['aqi']})

Dear Residents,

In light of the hazardous air quality and severe atmospheric inversion currently trapping toxic pollutants at ground level, our society is implementing immediate community safeguards:

1. **Focus: {notice_type}**
2. **Zero Open Fires:** Strictly zero burning of leaves, wood, or solid waste anywhere within society premises. Violations will be reported immediately to municipal pollution authorities.
3. **Guard Welfare:** The society will provide electric room heating and thermal layers for all night-shift security staff so they do not resort to open burning.
4. **Commute Pooling:** Residents are encouraged to use the society carpool registry or switch to electric metro transit.
5. **Dust Control:** Maintenance teams must use wet-mop sweeping only; dry sweeping of pathways is suspended until the smog lifts.

Let us protect our children and senior citizens together.
*Issued in Public Interest by {society_name} Environmental Committee in partnership with Hawa Saathi (हवा साथी).*
"""
            st.text_area("Generated RWA Notice (Copy & Share):", notice_text, height=260)


# ==========================================
# TAB 5: CHAT & EMERGENCY SOS
# ==========================================
with tab_chat:
    st.subheader("💬 Hawa Saathi Conversational Companion & Emergency SOS")
    st.markdown(
        "Chat with your bilingual AI environmental assistant for personalized guidance, or tap emergency action cards for acute respiratory crises."
    )

    # Emergency SOS Buttons Row
    st.markdown("#### 🚨 Rapid Emergency SOS Quick-Protocols")
    col_sos1, col_sos2, col_sos3, col_sos4 = st.columns(4)
    quick_prompt = None

    with col_sos1:
        if st.button("🫁 Acute Wheezing / Asthma Alert", use_container_width=True):
            quick_prompt = "What is the emergency triage protocol for acute wheezing and asthma during a severe smog spike?"
    with col_sos2:
        if st.button("😷 N95 Respirator Fit-Check", use_container_width=True):
            quick_prompt = "How do I perform a user seal check (positive/negative pressure test) on an N95 mask?"
    with col_sos3:
        if st.button("👶 Child / Infant Smog Defense", use_container_width=True):
            quick_prompt = "How do I protect an infant or toddler from indoor smog when air purifiers aren't enough?"
    with col_sos4:
        if st.button("👁️ Smog Eye-Burn & Throat Soothe", use_container_width=True):
            quick_prompt = "How to treat severe smog-induced eye burning, tearing, and throat scratchiness at home?"

    # Display Chat History
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    user_input = st.chat_input("Ask Hawa Saathi anything about air pollution, DIY filters, or health precautions...")
    prompt_to_send = quick_prompt or user_input

    if prompt_to_send:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt_to_send})
        with st.chat_message("user"):
            st.markdown(prompt_to_send)

        # Context dict
        ctx = {
            "city": selected_city_name,
            "pm25": pm25_input,
            "aqi": aqi_data["aqi"],
            "family": ", ".join(family_members) if "family_members" in locals() and family_members else "Families"
        }

        with st.chat_message("assistant"):
            with st.spinner("Hawa Saathi is thinking..."):
                reply = genai_client.chat_companion(prompt_to_send, st.session_state.chat_history, ctx)
                st.markdown(reply)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})


# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #78909C; font-size: 0.85rem;'>"
    "🌿 <strong>Hawa Saathi (हवा साथी)</strong> • Powered by Google Gemini 4 GenAI Architecture • "
    "Designed for Clean Air, Environmental Justice, and Community Health."
    "</div>",
    unsafe_allow_html=True
)
