"""
Verification and Unit Test Suite for Hawa Saathi
"""

import sys
from PIL import Image

def test_aqi_engine():
    from src.aqi_engine import pm25_to_aqi, simulate_24h_inversion, compute_inhaled_dose
    
    # Test Good
    res_good = pm25_to_aqi(25)
    assert res_good["aqi"] <= 50, f"Expected AQI <= 50, got {res_good['aqi']}"
    
    # Test Severe
    res_severe = pm25_to_aqi(380)
    assert res_severe["aqi"] >= 400, f"Expected AQI >= 400, got {res_severe['aqi']}"

    # Test Inversion simulation
    inv = simulate_24h_inversion(300)
    assert len(inv) == 24, f"Expected 24 hours, got {len(inv)}"
    assert any(h["ventilation_safe"] for h in inv), "Expected at least one safe ventilation window"

    # Test Dose
    dose = compute_inhaled_dose(380, 2, "moderate_walk")
    assert dose["inhaled_ug"] > 0
    assert dose["cig_equivalent"] > 0
    print("✅ aqi_engine tests passed!")

def test_impact_calculator():
    from src.impact_calculator import calculate_commute_impact, calculate_iaq_hack_impact
    
    # Commute
    commute = calculate_commute_impact(15, "solo_petrol_car", "electric_metro_rail")
    assert commute["monthly_co2_saved_kg"] > 0
    assert commute["monthly_pm25_saved_g"] > 0

    # IAQ Hack
    iaq = calculate_iaq_hack_impact(250, 400, "diy_corsi_rosenthal")
    assert iaq["indoor_pm25"] < 400
    assert iaq["ach"] > 0
    print("✅ impact_calculator tests passed!")

def test_genai_service():
    from src.genai_service import GenAIService
    service = GenAIService()
    
    # Test synthetic routine generation
    routine = service.generate_routine(
        city="Delhi NCR",
        current_pm25=380,
        family_members=["Senior Citizens", "Infants"],
        commute_type="Solo Petrol Car",
        housing_type="Apartment"
    )
    assert "schedule" in routine
    assert len(routine["schedule"]) > 0
    assert "morning_briefing_hindi" in routine

    # Test Vision fallback
    dummy_img = Image.new("RGB", (200, 200), color="grey")
    vision_res = service.analyze_room_or_filter_image(dummy_img, "test query")
    assert "analysis_text" in vision_res

    # Test Chat fallback
    reply = service.chat_companion("What mask should I wear?", [], {"city": "Delhi", "pm25": 400, "aqi": 425})
    assert len(reply) > 20
    print("✅ genai_service tests passed!")

if __name__ == "__main__":
    print("Running Hawa Saathi verification suite...")
    test_aqi_engine()
    test_impact_calculator()
    test_genai_service()
    print("🎉 All Hawa Saathi core modules verified successfully!")
