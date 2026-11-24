"""
Impact Calculator for Hawa Saathi.
Quantifies the direct personal and community impact of low-emission choices,
indoor air quality hacks, and sustainable daily routines.
"""

from typing import Dict, Any
import math

# Emission Factors (derived from CPCB, ICCT, and IPCC urban transport & domestic combustion inventories)
EMISSION_FACTORS = {
    # Transport (per passenger-km)
    "transport": {
        "solo_petrol_car": {"co2_g_km": 192.0, "pm25_g_km": 0.045, "pm10_g_km": 0.075},
        "solo_diesel_car": {"co2_g_km": 175.0, "pm25_g_km": 0.085, "pm10_g_km": 0.120},
        "carpool_4_people": {"co2_g_km": 48.0, "pm25_g_km": 0.011, "pm10_g_km": 0.019},
        "electric_metro_rail": {"co2_g_km": 15.0, "pm25_g_km": 0.001, "pm10_g_km": 0.005},
        "electric_bus": {"co2_g_km": 22.0, "pm25_g_km": 0.002, "pm10_g_km": 0.008},
        "cng_auto_shared": {"co2_g_km": 40.0, "pm25_g_km": 0.008, "pm10_g_km": 0.015},
        "two_wheeler_petrol": {"co2_g_km": 68.0, "pm25_g_km": 0.035, "pm10_g_km": 0.050},
        "ev_two_wheeler": {"co2_g_km": 12.0, "pm25_g_km": 0.002, "pm10_g_km": 0.004},
        "bicycle_walk": {"co2_g_km": 0.0, "pm25_g_km": 0.0, "pm10_g_km": 0.0}
    },
    # Domestic Heating & Cooking (per household-day)
    "heating_cooking": {
        "biomass_wood_coal_angithi": {"pm25_g_day": 340.0, "co2_kg_day": 8.5, "co_g_day": 120.0},
        "electric_radiator_oil_heater": {"pm25_g_day": 0.0, "co2_kg_day": 3.2, "co_g_day": 0.0},
        "hot_water_bottle_insulated_blanket": {"pm25_g_day": 0.0, "co2_kg_day": 0.4, "co_g_day": 0.0},
        "unvented_solid_chulha": {"pm25_g_day": 450.0, "co2_kg_day": 12.0, "co_g_day": 250.0},
        "induction_cooktop_clean_lpg": {"pm25_g_day": 5.0, "co2_kg_day": 2.1, "co_g_day": 2.0}
    },
    # Waste Management (per incident)
    "waste": {
        "open_leaf_trash_burn_10kg": {"pm25_g_burn": 160.0, "co2_kg_burn": 14.5, "voc_g_burn": 45.0},
        "composting_mulching": {"pm25_g_burn": 0.0, "co2_kg_burn": 1.2, "voc_g_burn": 0.0}
    }
}


def calculate_commute_impact(distance_km: float, baseline_mode: str, green_mode: str, days_per_month: int = 22) -> Dict[str, Any]:
    """
    Calculates emission savings from switching daily commute modes.
    """
    transport = EMISSION_FACTORS["transport"]
    base = transport.get(baseline_mode, transport["solo_petrol_car"])
    green = transport.get(green_mode, transport["electric_metro_rail"])

    daily_dist = distance_km * 2  # roundtrip
    base_co2_kg_day = (base["co2_g_km"] * daily_dist) / 1000.0
    green_co2_kg_day = (green["co2_g_km"] * daily_dist) / 1000.0
    saved_co2_kg_day = max(0.0, base_co2_kg_day - green_co2_kg_day)

    base_pm25_g_day = base["pm25_g_km"] * daily_dist
    green_pm25_g_day = green["pm25_g_km"] * daily_dist
    saved_pm25_g_day = max(0.0, base_pm25_g_day - green_pm25_g_day)

    monthly_co2_saved = saved_co2_kg_day * days_per_month
    monthly_pm25_saved = saved_pm25_g_day * days_per_month

    # Equivalent clean air volume: 1 gram of PM2.5 can contaminate 40,000 m³ of clean air to 25 µg/m³
    clean_air_m3_preserved = round(monthly_pm25_saved * 40000, 0)
    tree_months_equivalent = round(monthly_co2_saved / 1.8, 1)  # 1 mature tree absorbs ~1.8 kg CO2/month

    return {
        "daily_co2_saved_kg": round(saved_co2_kg_day, 2),
        "monthly_co2_saved_kg": round(monthly_co2_saved, 1),
        "daily_pm25_saved_g": round(saved_pm25_g_day, 3),
        "monthly_pm25_saved_g": round(monthly_pm25_saved, 2),
        "clean_air_m3_preserved": clean_air_m3_preserved,
        "tree_months_equivalent": tree_months_equivalent,
        "baseline_label": baseline_mode.replace("_", " ").title(),
        "green_label": green_mode.replace("_", " ").title()
    }


def calculate_iaq_hack_impact(room_area_sqft: float, baseline_outdoor_pm25: float, hack_type: str) -> Dict[str, Any]:
    """
    Calculates indoor air quality improvements from DIY hacks & bio-interventions.
    Room volume in m³: Area (sqft) * 0.0929 * 2.8m (ceiling height)
    """
    room_vol_m3 = room_area_sqft * 0.0929 * 2.8

    # Hack reduction efficiency & CADR (Clean Air Delivery Rate in m³/h)
    hack_profiles = {
        "diy_corsi_rosenthal": {
            "name": "DIY Corsi-Rosenthal Box (Box Fan + 4x MERV-13 Filters)",
            "pm25_reduction_pct": 82.0,
            "cost_usd": 35.0,
            "cadr_m3_h": 650.0,
            "energy_watts": 45.0,
            "diy_steps": [
                "Acquire 1x 20-inch box fan and 4x MERV-13 pleated air filters (20x20x2 inches).",
                "Form a 4-sided cube with the 4 filters (airflow arrows facing inward).",
                "Tape the filters securely using duct tape at all seams to prevent air bypass.",
                "Tape a cardboard square as the bottom floor of the cube.",
                "Place the 20-inch box fan facing upwards on top of the cube and seal the perimeter.",
                "Cut a 16-inch round cardboard shroud on top of the fan to eliminate blade-corner vortex backflow (+20% CADR boost)."
            ]
        },
        "hepa_commercial_purifier": {
            "name": "Commercial True HEPA Purifier (H13 Glass Fiber)",
            "pm25_reduction_pct": 92.0,
            "cost_usd": 150.0,
            "cadr_m3_h": 400.0,
            "energy_watts": 55.0,
            "diy_steps": [
                "Position unit at least 1.5 feet away from walls in the central breathing zone.",
                "Keep windows and exterior doors tightly closed during operation.",
                "Vacuum or wipe pre-filter screen mesh bi-weekly to prevent HEPA pre-saturation."
            ]
        },
        "weatherstrip_window_seal": {
            "name": "Foam Weatherstripping & Silicone Window Border Draft Seal",
            "pm25_reduction_pct": 45.0,
            "cost_usd": 8.0,
            "cadr_m3_h": 0.0,
            "energy_watts": 0.0,
            "diy_steps": [
                "Clean the window frame channels thoroughly with rubbing alcohol.",
                "Measure gap tolerances using a coin or paper thickness test.",
                "Apply self-adhesive high-density EPDM foam strip along sash contact lines.",
                "Use wet-applied bubble wrap or heavy cellular thermal drapes to block night drafts."
            ]
        },
        "phytoremediation_plants": {
            "name": "Clean Air Bio-Wall (Areca Palm + Sansevieria + Spider Plants)",
            "pm25_reduction_pct": 20.0,
            "cost_usd": 25.0,
            "cadr_m3_h": 45.0,
            "energy_watts": 0.0,
            "diy_steps": [
                "Place 4 shoulder-high Areca Palms per person in living areas for daytime oxygenation.",
                "Place 6-8 Snake Plants (Sansevieria Trifasciata) in bedrooms (CAM photosynthesis generates nighttime O2 and absorbs VOCs).",
                "Wipe leaves weekly with a damp microfiber cloth to remove dust accumulation so stomata remain open."
            ]
        }
    }

    hack = hack_profiles.get(hack_type, hack_profiles["diy_corsi_rosenthal"])
    red_pct = hack["pm25_reduction_pct"]
    indoor_pm25 = baseline_outdoor_pm25 * (1.0 - (red_pct / 100.0))

    # Calculate hours to clean the room once (Air Changes per Hour - ACH)
    ach = round(hack["cadr_m3_h"] / room_vol_m3, 1) if hack["cadr_m3_h"] > 0 else 0.5
    time_to_50pct_clean_min = round((math.log(2) / max(ach, 0.1)) * 60, 0) if ach > 0 else 120

    return {
        "hack_name": hack["name"],
        "cost_est_usd": hack["cost_usd"],
        "cadr_m3_h": hack["cadr_m3_h"],
        "pm25_reduction_pct": red_pct,
        "ach": ach,
        "time_to_50pct_clean_min": time_to_50pct_clean_min,
        "indoor_pm25": round(indoor_pm25, 1),
        "diy_steps": hack["diy_steps"]
    }
