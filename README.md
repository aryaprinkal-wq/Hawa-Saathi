# 🌿 Hawa Saathi (हवा साथी)
### *GenAI Urban Smog & Clean Air Companion for Families and Communities*

Hawa Saathi is a full-featured, GenAI-powered intelligent assistant that helps families and urban communities navigate severe winter smog and urban air pollution crises. Built with **Google Gemini 4 GenAI**, atmospheric boundary-layer physics, and multimodal vision diagnostics.

---

## 🌟 Key Features

1. **📡 Smog Radar & Atmospheric Inversion Model**
   - 24-hour diurnal thermal inversion curve tracking PM2.5 boundary layer trapping and solar convection windows.
   - Dynamic identification of the midday solar mixing window (12:00 PM – 3:00 PM) when ground-level PM2.5 drops by 30–45%.
   - Inhaled physiological particulate dose calculator ($\mu\text{g}$ and cigarette-equivalent lung burden).

2. **🗓️ GenAI Dynamic Routine Optimizer**
   - Vulnerability-calibrated routine planning (infants, asthmatic seniors, pregnant individuals, commuters).
   - Hour-by-hour structured itinerary with safety badges (`DANGEROUS`, `CAUTION`, `OPTIMAL_WINDOW`).
   - Morning verbal audio briefing in Hindi & English with in-browser Web Speech audio player.

3. **🔬 Multimodal IAQ & DIY Clean Air Lab**
   - **Gemini 4 Multimodal Vision Inspector**: Upload photos of air filters, window frames, or room setups to diagnose particulate saturation % and draft leaks.
   - **The DIY Corsi-Rosenthal Box Wizard**: Interactive calculator for building high-CADR (400–600 CFM) box fan air purifiers for ~$35 vs commercial $250+ units.
   - **Phytoremediation Bio-Wall**: Room-specific oxygenation and VOC absorption plant recommendations (Areca Palm, Snake Plant, Spider Plant).

4. **📊 Sustainable Lifestyle & Community Action Engine**
   - Direct impact math: Quantifies grams of tailpipe PM2.5 prevented, kg CO2e avoided, and cubic meters of clean air preserved.
   - Clean winter heating alternatives (replacing toxic biomass *angithis* with electric oil-heaters).
   - Community RWA Anti-Smog Notice & Whistleblower Generator.

5. **💬 Conversational Companion & Emergency SOS**
   - Real-time bilingual GenAI chat assistant.
   - 1-click Emergency SOS protocols for acute asthma/wheezing, N95 seal check, infant smog defense, and eye irritation relief.

---

## 🚀 Quick Start

### 1. Requirements
- Python 3.10+
- (Optional) `GEMINI_API_KEY` for live Gemini 4 model reasoning; includes automatic smart offline heuristics if no key is provided.

### 2. Run the Application
You can run Hawa Saathi directly:
```bash
streamlit run app.py
```
Or double-click `run_hawa_saathi.bat`.

The application will open automatically at `http://localhost:8501`.

---

## 🛠️ Architecture

- `app.py`: Streamlit responsive web dashboard with Plotly charts and audio synthesizer.
- `src/genai_service.py`: Google Gemini 4 Hydrogen integration, Structured JSON Outputs, Multimodal Vision, and conversational intelligence.
- `src/aqi_engine.py`: CPCB & WHO AQI computation, 24-hr boundary-layer thermal inversion simulation, and physiological lung dose math.
- `src/impact_calculator.py`: Transport, heating, and waste management emission factors, CADR and air changes per hour (ACH).
- `src/sample_images.py`: Demo images for immediate testing of the Multimodal Vision Lab.
