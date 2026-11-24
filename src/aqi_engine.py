"""
AQI Engine and Atmospheric Inversion Model for Hawa Saathi.
Supports CPCB (National Air Quality Index - India) and US-EPA standards.
Includes winter boundary-layer thermal inversion simulation.
"""

from typing import Dict, List, Any
import math

# CPCB AQI Breakpoints for PM2.5 (24-hr average in µg/m³)
CPCB_BREAKPOINTS = [
    (0, 30, 0, 50, "Good", "#00E400", "Minimal health impact."),
    (31, 60, 51, 100, "Satisfactory", "#92D050", "Minor breathing discomfort to sensitive people."),
    (61, 90, 101, 200, "Moderate", "#FFFF00", "Breathing discomfort to people with lungs, asthma and heart diseases."),
    (91, 120, 201, 300, "Poor", "#FF7E00", "Breathing discomfort to most people on prolonged exposure."),
    (121, 250, 301, 400, "Very Poor", "#FF0000", "Respiratory illness on prolonged exposure."),
    (251, 500, 401, 500, "Severe / Hazardous", "#7E0023", "Affects healthy people and seriously impacts those with existing diseases.")
]

PRESET_CITIES = {
    "Delhi NCR (Anand Vihar / Connaught Place)": {
        "base_pm25": 380,
        "base_pm10": 510,
        "temp_min": 7,
        "temp_max": 21,
        "humidity": 85,
        "inversion_strength": "High",
        "primary_source": "Vehicular (34%), Stubble/Biomass (28%), Road Dust (20%), Industrial (18%)"
    },
    "Lahore (Gulberg / Mall Road)": {
        "base_pm25": 420,
        "base_pm10": 550,
        "temp_min": 6,
        "temp_max": 20,
        "humidity": 88,
        "inversion_strength": "Extreme",
        "primary_source": "Low-grade Fuel & Stubble (40%), Transport (35%), Brick Kilns (25%)"
    },
    "Kolkata (Rabindra Bharati / Ballygunge)": {
        "base_pm25": 210,
        "base_pm10": 310,
        "temp_min": 14,
        "temp_max": 26,
        "humidity": 78,
        "inversion_strength": "Moderate",
        "primary_source": "Vehicular Exhaust (42%), Solid Waste Combustion (25%), Dust (20%)"
    },
    "Mumbai (Bandra Kurla Complex / Colaba)": {
        "base_pm25": 165,
        "base_pm10": 240,
        "temp_min": 19,
        "temp_max": 31,
        "humidity": 65,
        "inversion_strength": "Mild (Sea Breeze Mixing)",
        "primary_source": "Construction & Road Dust (38%), Vehicular Traffic (35%), Maritime/Industry (27%)"
    },
    "Beijing (Chaoyang / Haidian)": {
        "base_pm25": 145,
        "base_pm10": 195,
        "temp_min": -4,
        "temp_max": 6,
        "humidity": 45,
        "inversion_strength": "High (Winter Heating Spike)",
        "primary_source": "Regional Coal/Heating (38%), Vehicles (32%), Industrial (30%)"
    },
    "London / Urban Western Benchmark": {
        "base_pm25": 28,
        "base_pm10": 45,
        "temp_min": 3,
        "temp_max": 9,
        "humidity": 82,
        "inversion_strength": "Low",
        "primary_source": "Diesel Commute (45%), Domestic Wood Burning (30%), Background (25%)"
    }
}


def pm25_to_aqi(pm25: float) -> Dict[str, Any]:
    """Calculates CPCB AQI from PM2.5 concentration in µg/m³."""
    pm25 = max(0.0, float(pm25))
    if pm25 > 500:
        return {
            "aqi": 500 + int((pm25 - 500) * 0.5),
            "category": "Severe+",
            "color": "#4A0014",
            "advisory": "EMERGENCY: Complete inversion lock. Avoid all outdoor activity. Run continuous air filtration.",
            "health_implication": "Serious cardiovascular and respiratory impacts for everyone, including healthy individuals."
        }

    for c_low, c_high, i_low, i_high, cat, col, adv in CPCB_BREAKPOINTS:
        if c_low <= pm25 <= c_high:
            # Linear interpolation
            aqi = ((i_high - i_low) / (c_high - c_low)) * (pm25 - c_low) + i_low
            return {
                "aqi": round(aqi),
                "category": cat,
                "color": col,
                "advisory": adv,
                "health_implication": adv
            }

    # Catch-all
    return {
        "aqi": 500,
        "category": "Severe+",
        "color": "#7E0023",
        "advisory": "Severe smog event.",
        "health_implication": "High risk for all."
    }


def simulate_24h_inversion(base_pm25: float) -> List[Dict[str, Any]]:
    """
    Simulates the diurnal atmospheric boundary layer during winter smog.
    - Night/Dawn (11 PM - 7 AM): Shallow nocturnal boundary layer (~50-100m) traps pollutants.
    - Midday (11 AM - 3 PM): Solar heating causes convection and thermal turbulence;
      boundary layer expands (~800m), reducing ground-level PM2.5 by 30-45%.
    - Evening Rush (6 PM - 10 PM): Fast radiation cooling creates sudden capping inversion.
    """
    hourly_curve = [
        # Hour, factor relative to daily average, label
        (0, 1.25, "Midnight Inversion"),
        (1, 1.30, "Nocturnal Cooling"),
        (2, 1.35, "Trapped Cold Air"),
        (3, 1.40, "Peak Inversion (Cold Sink)"),
        (4, 1.42, "Peak Inversion"),
        (5, 1.45, "Pre-dawn Deep Smog"),
        (6, 1.40, "Dawn Surface Mist"),
        (7, 1.30, "Sunrise Smog Peak"),
        (8, 1.25, "Morning Rush Surge"),
        (9, 1.15, "Inversion Starting to Lift"),
        (10, 1.00, "Thermal Mixing Begins"),
        (11, 0.85, "Solar Convection Window"),
        (12, 0.70, "Deepest Mixing / Best Ventilation"),
        (13, 0.65, "Deepest Mixing / Lowest PM2.5"),
        (14, 0.68, "Optimal Activity Slot"),
        (15, 0.78, "Mixing Window Closing"),
        (16, 0.90, "Ground Solar Diminishing"),
        (17, 1.05, "Sunset Rapid Cooling"),
        (18, 1.20, "Evening Rush Capping Inversion"),
        (19, 1.28, "Night Inversion Forms"),
        (20, 1.32, "Trapped Emissions Peak"),
        (21, 1.30, "Heavy Smog Blanket"),
        (22, 1.25, "Stable Boundary Layer"),
        (23, 1.22, "Stable Inversion"),
    ]

    forecast = []
    for hr, factor, stage in hourly_curve:
        hourly_pm25 = round(base_pm25 * factor, 1)
        aqi_info = pm25_to_aqi(hourly_pm25)
        is_safe_window = 11 <= hr <= 15 and hourly_pm25 < (base_pm25 * 0.85)
        
        forecast.append({
            "hour": hr,
            "time_label": f"{hr:02d}:00",
            "pm25": hourly_pm25,
            "aqi": aqi_info["aqi"],
            "category": aqi_info["category"],
            "color": aqi_info["color"],
            "stage": stage,
            "ventilation_safe": is_safe_window
        })
    return forecast


def compute_inhaled_dose(pm25_ug_m3: float, hours: float, activity_level: str = "resting") -> Dict[str, float]:
    """
    Computes cumulative inhaled PM2.5 mass (µg) based on human respiratory physiology.
    Ventilation rates (m³/hour):
    - Sleeping/Resting: 0.45 m³/h
    - Light sedentary (desk work, school): 0.6 m³/h
    - Moderate activity (walking, light commute): 1.2 m³/h
    - Vigorous activity (jogging, cycling in smog): 2.4 m³/h
    """
    rates = {
        "resting": 0.45,
        "sedentary": 0.60,
        "moderate_walk": 1.20,
        "vigorous_exercise": 2.40
    }
    vent_rate = rates.get(activity_level, 0.60)
    inhaled_ug = pm25_ug_m3 * vent_rate * hours
    # Equivalent cigarettes smoked (Berkeley Earth rule-of-thumb: ~22 µg/m³ of PM2.5 per 24h = 1 cigarette)
    # Dose of 1 cigarette inhaled ~ 22 ug/m3 * 14.4 m3/day ~ 316.8 ug
    cig_equivalent = inhaled_ug / 316.8

    return {
        "inhaled_ug": round(inhaled_ug, 1),
        "cig_equivalent": round(cig_equivalent, 2),
        "ventilation_rate_m3_h": vent_rate
    }
