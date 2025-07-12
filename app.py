import os
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
from skyfield.api import load, wgs84, utc
from skyfield.almanac import find_discrete, risings_and_settings
from datetime import datetime
import math
import json
import requests

app = Flask(__name__)
CORS(app)

# Local geocoding database for common Indian cities
INDIAN_CITIES = {
    "mumbai": {"lat": 19.0760, "lon": 72.8777},
    "delhi": {"lat": 28.7041, "lon": 77.1025},
    "bangalore": {"lat": 12.9716, "lon": 77.5946},
    "hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "chennai": {"lat": 13.0827, "lon": 80.2707},
    "kolkata": {"lat": 22.5726, "lon": 88.3639},
    "pune": {"lat": 18.5204, "lon": 73.8567},
    "ahmedabad": {"lat": 23.0225, "lon": 72.5714},
    "surat": {"lat": 21.1702, "lon": 72.8311},
    "jaipur": {"lat": 26.9124, "lon": 75.7873},
    "lucknow": {"lat": 26.8467, "lon": 80.9462},
    "kanpur": {"lat": 26.4499, "lon": 80.3319},
    "nagpur": {"lat": 21.1458, "lon": 79.0882},
    "indore": {"lat": 22.7196, "lon": 75.8577},
    "thane": {"lat": 19.2183, "lon": 72.9781},
    "bhopal": {"lat": 23.2599, "lon": 77.4126},
    "visakhapatnam": {"lat": 17.6868, "lon": 83.2185},
    "patna": {"lat": 25.5941, "lon": 85.1376},
    "vadodara": {"lat": 22.3072, "lon": 73.1812},
    "ghaziabad": {"lat": 28.6692, "lon": 77.4538},
    "ludhiana": {"lat": 30.9010, "lon": 75.8573},
    "agra": {"lat": 27.1767, "lon": 78.0081},
    "nashik": {"lat": 19.9975, "lon": 73.7898},
    "faridabad": {"lat": 28.4089, "lon": 77.3178},
    "meerut": {"lat": 28.9845, "lon": 77.7064},
    "rajkot": {"lat": 22.3039, "lon": 70.8022},
    "kalyan": {"lat": 19.2433, "lon": 73.1355},
    "vasai": {"lat": 19.4259, "lon": 72.8225},
    "srinagar": {"lat": 34.0837, "lon": 74.7973},
    "aurangabad": {"lat": 19.8762, "lon": 75.3433},
    "dhanbad": {"lat": 23.7957, "lon": 86.4304},
    "amritsar": {"lat": 31.6340, "lon": 74.8723},
    "allahabad": {"lat": 25.4358, "lon": 81.8463},
    "ranchi": {"lat": 23.3441, "lon": 85.3096},
    "howrah": {"lat": 22.5958, "lon": 88.2636},
    "coimbatore": {"lat": 11.0168, "lon": 76.9558},
    "jabalpur": {"lat": 23.1815, "lon": 79.9864},
    "gwalior": {"lat": 26.2183, "lon": 78.1828},
    "vijayawada": {"lat": 16.5062, "lon": 80.6480},
    "jodhpur": {"lat": 26.2389, "lon": 73.0243},
    "madurai": {"lat": 9.9252, "lon": 78.1198},
    "raipur": {"lat": 21.2514, "lon": 81.6296},
    "kota": {"lat": 25.2138, "lon": 75.8648},
    "guwahati": {"lat": 26.1445, "lon": 91.7362},
    "chandigarh": {"lat": 30.7333, "lon": 76.7794},
    "solapur": {"lat": 17.6599, "lon": 75.9064},
    "hubli": {"lat": 15.3647, "lon": 75.1240},
    "mysore": {"lat": 12.2958, "lon": 76.6394},
    "tiruchirappalli": {"lat": 10.7905, "lon": 78.7047},
    "bareilly": {"lat": 28.3670, "lon": 79.4304},
    "aligarh": {"lat": 27.8974, "lon": 78.0880},
    "moradabad": {"lat": 28.8389, "lon": 78.7738},
    "gurgaon": {"lat": 28.4595, "lon": 77.0266},
    "noida": {"lat": 28.5355, "lon": 77.3910},
    "greater noida": {"lat": 28.4744, "lon": 77.5040},
    "bhubaneswar": {"lat": 20.2961, "lon": 85.8245},
    "salem": {"lat": 11.6643, "lon": 78.1460},
    "warangal": {"lat": 17.9689, "lon": 79.5941},
    "guntur": {"lat": 16.2991, "lon": 80.4575},
    "bhiwandi": {"lat": 19.2969, "lon": 73.0625},
    "saharanpur": {"lat": 29.9675, "lon": 77.5451},
    "gorakhpur": {"lat": 26.7606, "lon": 83.3732},
    "bikaner": {"lat": 28.0229, "lon": 73.3119},
    "amravati": {"lat": 20.9374, "lon": 77.7796},
    "jamshedpur": {"lat": 22.8046, "lon": 86.2029},
    "bhilai": {"lat": 21.2094, "lon": 81.4285},
    "cuttack": {"lat": 20.4625, "lon": 85.8830},
    "firozabad": {"lat": 27.1591, "lon": 78.3958},
    "kochi": {"lat": 9.9312, "lon": 76.2673},
    "nellore": {"lat": 14.4426, "lon": 79.9865},
    "bhavnagar": {"lat": 21.7645, "lon": 72.1519},
    "dehradun": {"lat": 30.3165, "lon": 78.0322},
    "durgapur": {"lat": 23.5204, "lon": 87.3119},
    "asansol": {"lat": 23.6889, "lon": 86.9661},
    "rourkela": {"lat": 22.2492, "lon": 84.8828},
    "bhagalpur": {"lat": 25.2445, "lon": 87.0104},
    "bellary": {"lat": 15.1394, "lon": 76.9214},
    "mangalore": {"lat": 12.9716, "lon": 74.8631},
    "tirunelveli": {"lat": 8.7139, "lon": 77.7567},
    "malegaon": {"lat": 20.5609, "lon": 74.5250},
    "gaya": {"lat": 24.7914, "lon": 85.0002},
    "jalandhar": {"lat": 31.3260, "lon": 75.5762},
    "ujjain": {"lat": 23.1765, "lon": 75.7885},
    "sangli": {"lat": 16.8524, "lon": 74.5815},
    "loni": {"lat": 28.7515, "lon": 77.2889},
    "jammu": {"lat": 32.7266, "lon": 74.8570},
    "belgaum": {"lat": 15.8497, "lon": 74.4977},
    "ambattur": {"lat": 13.1143, "lon": 80.1547},
    "tiruppur": {"lat": 11.1085, "lon": 77.3411},
    "gulbarga": {"lat": 17.3297, "lon": 76.8343},
    "akola": {"lat": 20.7096, "lon": 77.0021},
    "jamnagar": {"lat": 22.4707, "lon": 70.0577},
    "bhayandar": {"lat": 19.2969, "lon": 72.8500},
    "morvi": {"lat": 22.8173, "lon": 70.8372}
}

def get_coordinates(place):
    """Get coordinates for a place using local database"""
    place_lower = place.lower().strip()
    
    # Check if place is in our database
    if place_lower in INDIAN_CITIES:
        return INDIAN_CITIES[place_lower]["lat"], INDIAN_CITIES[place_lower]["lon"]
    
    # Default to Mumbai if not found
    return INDIAN_CITIES["mumbai"]["lat"], INDIAN_CITIES["mumbai"]["lon"]

def calculate_birth_chart(date_str, time_str, place):
    """Calculate birth chart using skyfield"""
    try:
        # Parse date and time
        date_obj = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        
        # Add UTC timezone (assuming input times are in local time)
        date_obj = date_obj.replace(tzinfo=utc)
        
        # Get coordinates
        lat, lon = get_coordinates(place)
        
        # Load ephemeris
        ts = load.timescale()
        t = ts.from_datetime(date_obj)
        
        # Get Sun position
        eph = load('de421.bsp')
        sun = eph['sun']
        earth = eph['earth']
        
        # Calculate Sun's position relative to Earth
        astrometric = earth.at(t).observe(sun)
        ra, dec, distance = astrometric.radec()
        
        # Convert to ecliptic longitude
        sun_longitude = ra.hours * 15  # Convert hours to degrees
        
        # Apply Lahiri Ayanamsa correction (sidereal)
        # For 1985, Lahiri Ayanamsa was approximately 23.85 degrees
        ayanamsa = 23.85 + (date_obj.year - 2000) * 0.000000317
        sidereal_longitude = sun_longitude - ayanamsa
        
        # Normalize to 0-360 degrees
        sidereal_longitude = (sidereal_longitude + 360) % 360
        
        # Calculate rashi (zodiac sign)
        rashi = int(sidereal_longitude / 30) + 1
        
        # Calculate nakshatra (lunar mansion)
        nakshatra = int(sidereal_longitude / 13.333333) + 1
        
        return {
            "rashi": rashi,
            "nakshatra": nakshatra,
            "longitude": sidereal_longitude,
            "coordinates": {"lat": lat, "lon": lon}
        }
        
    except Exception as e:
        print(f"Error in calculate_birth_chart: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return None

def calculate_compatibility(chart1, chart2):
    """Calculate Vedic compatibility between two charts"""
    try:
        # Rashi compatibility (basic)
        rashi1, rashi2 = chart1["rashi"], chart2["rashi"]
        
        # Nakshatra compatibility
        nakshatra1, nakshatra2 = chart1["nakshatra"], chart2["nakshatra"]
        
        # Calculate compatibility scores
        rashi_score = calculate_rashi_compatibility(rashi1, rashi2)
        nakshatra_score = calculate_nakshatra_compatibility(nakshatra1, nakshatra2)
        
        # Overall compatibility
        overall_score = (rashi_score + nakshatra_score) / 2
        
        return {
            "overall_score": round(overall_score, 2),
            "rashi_compatibility": round(rashi_score, 2),
            "nakshatra_compatibility": round(nakshatra_score, 2),
            "compatibility_level": get_compatibility_level(overall_score),
            "analysis": generate_compatibility_analysis(rashi1, rashi2, nakshatra1, nakshatra2, overall_score)
        }
        
    except Exception as e:
        print(f"Error in calculate_compatibility: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return None

def calculate_rashi_compatibility(rashi1, rashi2):
    """Calculate rashi compatibility score"""
    # Friend, neutral, enemy relationships
    friendly_signs = {
        1: [5, 9], 2: [6, 10], 3: [7, 11], 4: [8, 12],
        5: [1, 9], 6: [2, 10], 7: [3, 11], 8: [4, 12],
        9: [1, 5], 10: [2, 6], 11: [3, 7], 12: [4, 8]
    }
    
    enemy_signs = {
        1: [7, 8], 2: [8, 9], 3: [9, 10], 4: [10, 11],
        5: [11, 12], 6: [12, 1], 7: [1, 2], 8: [2, 3],
        9: [3, 4], 10: [4, 5], 11: [5, 6], 12: [6, 7]
    }
    
    if rashi1 == rashi2:
        return 85  # Same sign - good compatibility
    elif rashi2 in friendly_signs.get(rashi1, []):
        return 75  # Friendly signs
    elif rashi2 in enemy_signs.get(rashi1, []):
        return 35  # Enemy signs
    else:
        return 60  # Neutral signs

def calculate_nakshatra_compatibility(nakshatra1, nakshatra2):
    """Calculate nakshatra compatibility score"""
    # Simplified nakshatra compatibility
    if nakshatra1 == nakshatra2:
        return 80
    elif abs(nakshatra1 - nakshatra2) <= 2:
        return 70
    elif abs(nakshatra1 - nakshatra2) <= 5:
        return 60
    else:
        return 50

def get_compatibility_level(score):
    """Get compatibility level based on score"""
    if score >= 80:
        return "Excellent"
    elif score >= 70:
        return "Very Good"
    elif score >= 60:
        return "Good"
    elif score >= 50:
        return "Moderate"
    elif score >= 40:
        return "Fair"
    else:
        return "Challenging"

def generate_compatibility_analysis(rashi1, rashi2, nakshatra1, nakshatra2, score):
    """Generate detailed compatibility analysis"""
    rashi_names = [
        "Mesha (Aries)", "Vrishabha (Taurus)", "Mithuna (Gemini)", "Karka (Cancer)",
        "Simha (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrishchika (Scorpio)",
        "Dhanu (Sagittarius)", "Makara (Capricorn)", "Kumbha (Aquarius)", "Meena (Pisces)"
    ]
    
    nakshatra_names = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu",
        "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
        "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
        "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
        "Uttara Bhadrapada", "Revati"
    ]
    
    analysis = f"""
    **Vedic Compatibility Analysis**
    
    **Partner 1:**
    - Rashi: {rashi_names[rashi1-1]}
    - Nakshatra: {nakshatra_names[nakshatra1-1]}
    
    **Partner 2:**
    - Rashi: {rashi_names[rashi2-1]}
    - Nakshatra: {nakshatra_names[nakshatra2-1]}
    
    **Compatibility Assessment:**
    - Overall Score: {score}/100
    - Level: {get_compatibility_level(score)}
    
    **Key Insights:**
    """
    
    if score >= 80:
        analysis += "This is an excellent match with strong spiritual and emotional compatibility. The partners are likely to have a harmonious and fulfilling relationship."
    elif score >= 70:
        analysis += "This is a very good match with strong potential for a successful relationship. There may be minor challenges but overall compatibility is high."
    elif score >= 60:
        analysis += "This is a good match with moderate compatibility. The relationship will require understanding and compromise from both partners."
    elif score >= 50:
        analysis += "This is a moderate match. The relationship may face some challenges but can work with mutual effort and understanding."
    else:
        analysis += "This match may face significant challenges. However, with strong commitment and spiritual growth, any relationship can be transformed."
    
    return analysis

RASHI_NAMES = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", 
    "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"
]

NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", 
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", 
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", 
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

RASHI_LORDS = [
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"
]

NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
    "Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun",
    "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
    "Jupiter", "Saturn", "Mercury"
]

@app.route('/debug/env', methods=['GET'])
def debug_env():
    """Debug endpoint to check environment variables"""
    return jsonify({
        "OPENAI_API_KEY": "SET" if os.environ.get('OPENAI_API_KEY') else "NOT SET",
        "AZURE_OPENAI_API_KEY": "SET" if os.environ.get('AZURE_OPENAI_API_KEY') else "NOT SET",
        "AZURE_OPENAI_API_BASE": "SET" if os.environ.get('AZURE_OPENAI_API_BASE') else "NOT SET",
        "AZURE_OPENAI_ENDPOINT": "SET" if os.environ.get('AZURE_OPENAI_ENDPOINT') else "NOT SET",
        "AZURE_OPENAI_DEPLOYMENT_NAME": os.environ.get('AZURE_OPENAI_DEPLOYMENT_NAME', 'NOT SET'),
        "AZURE_OPENAI_API_VERSION": os.environ.get('AZURE_OPENAI_API_VERSION', 'NOT SET')
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Vedic Compatibility API v2.0 is running"})

@app.route('/', methods=['GET'])
def root():
    return jsonify({"status": "healthy", "message": "Vedic Compatibility API v2.0 is running"})

@app.route('/api/compatibility', methods=['POST'])
def compatibility():
    try:
        data = request.get_json()
        
        if not data or 'partner1' not in data or 'partner2' not in data:
            return jsonify({"error": "Missing partner data"}), 400
        
        partner1_data = data['partner1']
        partner2_data = data['partner2']
        
        # Calculate birth charts
        chart1 = calculate_birth_chart(partner1_data['date'], partner1_data['time'], partner1_data['place'])
        chart2 = calculate_birth_chart(partner2_data['date'], partner2_data['time'], partner2_data['place'])
        
        if not chart1 or not chart2:
            return jsonify({"error": "Failed to calculate birth charts"}), 500
        
        # Calculate compatibility
        compatibility_data = calculate_compatibility(chart1, chart2)
        
        # Calculate Guna Milan (8 aspects of compatibility)
        gun_milan_score = calculate_guna_milan(chart1, chart2)
        max_possible_score = 36  # Maximum possible score in Guna Milan
        
        # Generate detailed breakdown
        breakdown = generate_gun_milan_breakdown(chart1, chart2)
        
        # Generate remarks and issues
        remarks = generate_compatibility_remarks(gun_milan_score, max_possible_score)
        issues_detected = detect_compatibility_issues(chart1, chart2, gun_milan_score)
        
        # Calculate spiritual alignment
        spiritual_alignment_score = calculate_spiritual_alignment(chart1, chart2)
        
        # Format charts with proper names
        partner1_chart = {
            "longitude": chart1["longitude"],
            "nakshatra": NAKSHATRA_NAMES[chart1["nakshatra"] - 1],
            "nakshatra_lord": NAKSHATRA_LORDS[chart1["nakshatra"] - 1],
            "rashi": RASHI_NAMES[chart1["rashi"] - 1],
            "rashi_lord": RASHI_LORDS[chart1["rashi"] - 1]
        }
        
        partner2_chart = {
            "longitude": chart2["longitude"],
            "nakshatra": NAKSHATRA_NAMES[chart2["nakshatra"] - 1],
            "nakshatra_lord": NAKSHATRA_LORDS[chart2["nakshatra"] - 1],
            "rashi": RASHI_NAMES[chart2["rashi"] - 1],
            "rashi_lord": RASHI_LORDS[chart2["rashi"] - 1]
        }
        
        # Return the complete compatibility report
        report = {
            "gun_milan_score": gun_milan_score,
            "max_possible_score": max_possible_score,
            "compatibility_level": compatibility_data["compatibility_level"],
            "breakdown": breakdown,
            "remarks": remarks,
            "issues_detected": issues_detected,
            "spiritual_alignment_score": spiritual_alignment_score,
            "partner1_chart": partner1_chart,
            "partner2_chart": partner2_chart
        }
        
        return jsonify(report)
        
    except Exception as e:
        print(f"Error in compatibility endpoint: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/compatibility/enhanced', methods=['POST'])
def enhanced_compatibility():
    """Generate enhanced compatibility report using GPT-4o"""
    try:
        data = request.get_json()
        
        if not data or 'partner1' not in data or 'partner2' not in data:
            return jsonify({"error": "Missing partner data"}), 400
        
        partner1_data = data['partner1']
        partner2_data = data['partner2']
        
        # Calculate birth charts
        chart1 = calculate_birth_chart(partner1_data['date'], partner1_data['time'], partner1_data['place'])
        chart2 = calculate_birth_chart(partner2_data['date'], partner2_data['time'], partner2_data['place'])
        
        if not chart1 or not chart2:
            return jsonify({"error": "Failed to calculate birth charts"}), 500
        
        # Calculate compatibility
        compatibility_data = calculate_compatibility(chart1, chart2)
        
        # Calculate Guna Milan (8 aspects of compatibility)
        gun_milan_score = calculate_guna_milan(chart1, chart2)
        max_possible_score = 36  # Maximum possible score in Guna Milan
        
        # Generate detailed breakdown
        breakdown = generate_gun_milan_breakdown(chart1, chart2)
        
        # Generate remarks and issues
        remarks = generate_compatibility_remarks(gun_milan_score, max_possible_score)
        issues_detected = detect_compatibility_issues(chart1, chart2, gun_milan_score)
        
        # Calculate spiritual alignment
        spiritual_alignment_score = calculate_spiritual_alignment(chart1, chart2)
        
        # Format charts with proper Sanskrit names
        partner1_chart = {
            "longitude": chart1["longitude"],
            "nakshatra": NAKSHATRA_NAMES[chart1["nakshatra"] - 1],
            "nakshatra_lord": NAKSHATRA_LORDS[chart1["nakshatra"] - 1],
            "rashi": RASHI_NAMES[chart1["rashi"] - 1],
            "rashi_lord": RASHI_LORDS[chart1["rashi"] - 1]
        }
        
        partner2_chart = {
            "longitude": chart2["longitude"],
            "nakshatra": NAKSHATRA_NAMES[chart2["nakshatra"] - 1],
            "nakshatra_lord": NAKSHATRA_LORDS[chart2["nakshatra"] - 1],
            "rashi": RASHI_NAMES[chart2["rashi"] - 1],
            "rashi_lord": RASHI_LORDS[chart2["rashi"] - 1]
        }
        
        # Prepare Vedic data for GPT-4o
        vedic_data = {
            "gun_milan_score": gun_milan_score,
            "max_possible_score": max_possible_score,
            "compatibility_level": compatibility_data["compatibility_level"],
            "breakdown": breakdown,
            "remarks": remarks,
            "issues_detected": issues_detected,
            "spiritual_alignment_score": spiritual_alignment_score,
            "partner1_chart": partner1_chart,
            "partner2_chart": partner2_chart,
            "partner1_details": partner1_data,
            "partner2_details": partner2_data
        }
        
        # Generate enhanced report using GPT-4o
        enhanced_report = generate_enhanced_report(vedic_data)
        
        return jsonify({
            "vedic_data": vedic_data,
            "enhanced_report": enhanced_report
        })
        
    except Exception as e:
        print(f"Error in enhanced compatibility endpoint: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Internal server error"}), 500

def generate_enhanced_report(vedic_data):
    """Generate enhanced report using GPT-4o"""
    try:
        # Check if OpenAI API key is available
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            return {"error": "OpenAI API key not configured"}
        
        # Create comprehensive prompt for GPT-4o
        prompt = f"""You are a master Vedic astrologer and relationship expert with 50+ years of experience. Generate a COMPREHENSIVE, DETAILED, and HIGHLY PERSONALIZED compatibility report for this couple.

PARTNER DETAILS:
Partner 1: {vedic_data['partner1_details'].get('name', 'Person 1')} 
- Date of Birth: {vedic_data['partner1_details']['date']}
- Time of Birth: {vedic_data['partner1_details']['time']} 
- Place of Birth: {vedic_data['partner1_details']['place']}

Partner 2: {vedic_data['partner2_details'].get('name', 'Person 2')}
- Date of Birth: {vedic_data['partner2_details']['date']}
- Time of Birth: {vedic_data['partner2_details']['time']}
- Place of Birth: {vedic_data['partner2_details']['place']}

VEDIC CALCULATIONS & ASTROLOGICAL DATA:
{json.dumps(vedic_data, indent=2)}

INSTRUCTIONS:
Generate a BEAUTIFUL, COLORFUL, COMPREHENSIVE, ROBUST, ACTION-ORIENTED, and HIGHLY PERSONALIZED compatibility report. This report should be:

1. **DEEP & ACCURATE**: Use the Vedic calculations to provide precise astrological insights
2. **COMPREHENSIVE**: Cover all aspects of compatibility - personality, emotional, spiritual, practical
3. **PERSONALIZED**: Reference specific details about each partner's birth chart
4. **ACTION-ORIENTED**: Provide specific, actionable advice and practices
5. **BEAUTIFUL**: Use rich, descriptive language that feels magical and meaningful
6. **BALANCED**: Highlight both strengths and growth areas constructively

REQUIRED JSON STRUCTURE (return ONLY valid JSON, no markdown):
{{
  "compatibility_score": number (0-100, based on Vedic calculations),
  "compatibility_summary": "A beautiful, comprehensive 2-3 sentence summary of their cosmic connection",
  "guna_milan": {{
    "varna": {{ "score": number, "max": number }},
    "vashya": {{ "score": number, "max": number }},
    "tara": {{ "score": number, "max": number }},
    "yoni": {{ "score": number, "max": number }},
    "graha_maitri": {{ "score": number, "max": number }},
    "gana": {{ "score": number, "max": number }},
    "bhakoot": {{ "score": number, "max": number }},
    "nadi": {{ "score": number, "max": number }},
    "total_score": number
  }},
  "personality_matching": "Detailed analysis of how their personalities complement each other, including specific traits from their birth charts",
  "emotional_compatibility": "Deep dive into emotional harmony, communication styles, and emotional needs based on their astrological profiles",
  "spiritual_alignment": "Analysis of their spiritual paths, growth potential, and shared spiritual journey",
  "life_goals_dharma": "Assessment of life purpose alignment, career compatibility, and shared life goals",
  "relationship_strengths": [
    "Specific strength 1 with astrological basis",
    "Specific strength 2 with astrological basis", 
    "Specific strength 3 with astrological basis",
    "Specific strength 4 with astrological basis",
    "Specific strength 5 with astrological basis"
  ],
  "growth_areas": [
    "Specific growth area 1 with constructive guidance",
    "Specific growth area 2 with constructive guidance",
    "Specific growth area 3 with constructive guidance"
  ],
  "daily_affirmations": [
    "Personalized affirmation 1 for their specific compatibility",
    "Personalized affirmation 2 for their specific compatibility",
    "Personalized affirmation 3 for their specific compatibility"
  ],
  "personalized_mantras": "A specific Sanskrit mantra with pronunciation guide and meaning, tailored to their compatibility",
  "custom_rituals": [
    "Specific ritual 1 with step-by-step instructions",
    "Specific ritual 2 with step-by-step instructions", 
    "Specific ritual 3 with step-by-step instructions"
  ],
  "action_items": [
    "Specific actionable step 1 for immediate implementation",
    "Specific actionable step 2 for immediate implementation",
    "Specific actionable step 3 for immediate implementation"
  ]
}}

IMPORTANT REQUIREMENTS:
- Use the Vedic calculations to inform every section
- Make each section deeply personalized to their specific birth details
- Provide specific, actionable advice, not generic statements
- Use beautiful, spiritual language that feels meaningful
- Ensure all text is clear, visible, and high contrast
- Make the report comprehensive yet easy to understand
- Include specific astrological references where relevant
- Focus on both practical and spiritual aspects of their relationship

Generate a report that would make a master Vedic astrologer proud - comprehensive, accurate, beautiful, and deeply meaningful."""

        # Call OpenAI API (standard, not Azure)
        headers = {
            'Authorization': f'Bearer {openai_api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'gpt-4o',
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are a master Vedic astrologer with 50+ years of experience in relationship compatibility analysis. You have deep knowledge of Vedic astrology, Guna Milan, Nakshatra matching, and spiritual relationship dynamics. Generate COMPLETELY ACCURATE, COMPREHENSIVE, and HIGHLY PERSONALIZED compatibility reports based on provided birth details and Vedic calculations. Your reports should be beautiful, meaningful, and actionable. Return ONLY valid JSON, no markdown or extra text. Every section should be deeply personalized and specific to the couple.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.8,
            'max_tokens': 4000,
            'top_p': 0.9,
            'frequency_penalty': 0.1,
            'presence_penalty': 0.1
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            return {"error": f"OpenAI API error: {response.status_code}"}
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # Parse the JSON response
        try:
            # Remove any non-JSON content that might be present
            import re
            json_str = re.sub(r'^```json\s*|\s*```$', '', content.strip())
            enhanced_report = json.loads(json_str)
            return enhanced_report
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse GPT response: {str(e)}", "raw_content": content}
            
    except Exception as e:
        print(f"Error generating enhanced report: {str(e)}")
        return {"error": f"Failed to generate enhanced report: {str(e)}"}

def calculate_guna_milan(chart1, chart2):
    """Calculate Guna Milan score (1-36)"""
    score = 0
    
    # Varna (1 point)
    varna1 = (chart1["rashi"] - 1) % 4
    varna2 = (chart2["rashi"] - 1) % 4
    if varna1 == varna2:
        score += 1
    
    # Vashya (2 points)
    vashya_score = calculate_vashya_compatibility(chart1["rashi"], chart2["rashi"])
    score += vashya_score
    
    # Tara (3 points)
    tara_score = calculate_tara_compatibility(chart1["nakshatra"], chart2["nakshatra"])
    score += tara_score
    
    # Yoni (4 points)
    yoni_score = calculate_yoni_compatibility(chart1["nakshatra"], chart2["nakshatra"])
    score += yoni_score
    
    # Graha Maitri (5 points)
    graha_score = calculate_graha_maitri(chart1["rashi"], chart2["rashi"])
    score += graha_score
    
    # Gana (6 points)
    gana_score = calculate_gana_compatibility(chart1["nakshatra"], chart2["nakshatra"])
    score += gana_score
    
    # Bhakoot (7 points)
    bhakoot_score = calculate_bhakoot_compatibility(chart1["rashi"], chart2["rashi"])
    score += bhakoot_score
    
    # Nadi (8 points)
    nadi_score = calculate_nadi_compatibility(chart1["nakshatra"], chart2["nakshatra"])
    score += nadi_score
    
    return score

def calculate_vashya_compatibility(rashi1, rashi2):
    """Calculate Vashya compatibility (0-2 points)"""
    # Simplified calculation
    diff = abs(rashi1 - rashi2)
    if diff == 0:
        return 2
    elif diff in [1, 11]:
        return 1
    else:
        return 0

def calculate_tara_compatibility(nakshatra1, nakshatra2):
    """Calculate Tara compatibility (0-3 points)"""
    # Simplified calculation
    diff = abs(nakshatra1 - nakshatra2)
    if diff == 0:
        return 3
    elif diff in [1, 2, 3]:
        return 2
    elif diff in [4, 5, 6]:
        return 1
    else:
        return 0

def calculate_yoni_compatibility(nakshatra1, nakshatra2):
    """Calculate Yoni compatibility (0-4 points)"""
    # Simplified calculation
    diff = abs(nakshatra1 - nakshatra2)
    if diff == 0:
        return 4
    elif diff in [1, 2]:
        return 3
    elif diff in [3, 4]:
        return 2
    elif diff in [5, 6]:
        return 1
    else:
        return 0

def calculate_graha_maitri(rashi1, rashi2):
    """Calculate Graha Maitri compatibility (0-5 points)"""
    # Simplified calculation
    diff = abs(rashi1 - rashi2)
    if diff == 0:
        return 5
    elif diff in [1, 5, 9]:
        return 4
    elif diff in [2, 4, 6, 8, 10]:
        return 3
    else:
        return 2

def calculate_gana_compatibility(nakshatra1, nakshatra2):
    """Calculate Gana compatibility (0-6 points)"""
    # Simplified calculation
    diff = abs(nakshatra1 - nakshatra2)
    if diff == 0:
        return 6
    elif diff in [1, 2, 3]:
        return 5
    elif diff in [4, 5, 6]:
        return 4
    else:
        return 3

def calculate_bhakoot_compatibility(rashi1, rashi2):
    """Calculate Bhakoot compatibility (0-7 points)"""
    # Simplified calculation
    diff = abs(rashi1 - rashi2)
    if diff == 0:
        return 7
    elif diff in [1, 2, 3]:
        return 6
    elif diff in [4, 5, 6]:
        return 5
    else:
        return 4

def calculate_nadi_compatibility(nakshatra1, nakshatra2):
    """Calculate Nadi compatibility (0-8 points)"""
    # Simplified calculation
    diff = abs(nakshatra1 - nakshatra2)
    if diff == 0:
        return 8
    elif diff in [1, 2, 3]:
        return 7
    elif diff in [4, 5, 6]:
        return 6
    else:
        return 5

def generate_gun_milan_breakdown(chart1, chart2):
    """Generate detailed breakdown of all 8 gunas"""
    return {
        "varna": {
            "score": 1 if ((chart1["rashi"] - 1) % 4) == ((chart2["rashi"] - 1) % 4) else 0,
            "max": 1,
            "description": "Social compatibility and class harmony"
        },
        "vashya": {
            "score": calculate_vashya_compatibility(chart1["rashi"], chart2["rashi"]),
            "max": 2,
            "description": "Control and dominance compatibility"
        },
        "tara": {
            "score": calculate_tara_compatibility(chart1["nakshatra"], chart2["nakshatra"]),
            "max": 3,
            "description": "Star compatibility and destiny alignment"
        },
        "yoni": {
            "score": calculate_yoni_compatibility(chart1["nakshatra"], chart2["nakshatra"]),
            "max": 4,
            "description": "Sexual compatibility and physical harmony"
        },
        "graha_maitri": {
            "score": calculate_graha_maitri(chart1["rashi"], chart2["rashi"]),
            "max": 5,
            "description": "Planetary friendship and mental compatibility"
        },
        "gana": {
            "score": calculate_gana_compatibility(chart1["nakshatra"], chart2["nakshatra"]),
            "max": 6,
            "description": "Temperament and nature compatibility"
        },
        "bhakoot": {
            "score": calculate_bhakoot_compatibility(chart1["rashi"], chart2["rashi"]),
            "max": 7,
            "description": "Love and affection compatibility"
        },
        "nadi": {
            "score": calculate_nadi_compatibility(chart1["nakshatra"], chart2["nakshatra"]),
            "max": 8,
            "description": "Health and progeny compatibility"
        }
    }

def generate_compatibility_remarks(score, max_score):
    """Generate detailed remarks based on compatibility score"""
    percentage = (score / max_score) * 100
    
    if percentage >= 80:
        return f"Excellent compatibility! With a score of {score}/{max_score} ({percentage:.1f}%), this is considered an ideal match in Vedic astrology. The couple shares strong spiritual, emotional, and physical harmony."
    elif percentage >= 60:
        return f"Good compatibility with a score of {score}/{max_score} ({percentage:.1f}%). This relationship has strong potential but may require some understanding and compromise from both partners."
    elif percentage >= 40:
        return f"Moderate compatibility scoring {score}/{max_score} ({percentage:.1f}%). While there are challenges, with mutual effort and understanding, this relationship can work well."
    elif percentage >= 20:
        return f"Low compatibility with a score of {score}/{max_score} ({percentage:.1f}%). This relationship will require significant effort, patience, and understanding from both partners."
    else:
        return f"Very low compatibility scoring {score}/{max_score} ({percentage:.1f}%). This match faces significant challenges and may not be advisable according to Vedic principles."

def detect_compatibility_issues(chart1, chart2, score):
    """Detect potential compatibility issues"""
    issues = []
    
    if score < 18:
        issues.append("Low overall compatibility score indicates potential relationship challenges")
    
    # Check for specific problematic combinations
    rashi_diff = abs(chart1["rashi"] - chart2["rashi"])
    if rashi_diff == 6:  # Opposition signs
        issues.append("Opposition of zodiac signs may create tension and conflicts")
    
    nakshatra_diff = abs(chart1["nakshatra"] - chart2["nakshatra"])
    if nakshatra_diff == 13:  # Opposition nakshatras
        issues.append("Opposition of nakshatras may affect emotional compatibility")
    
    if score < 25:
        issues.append("Consider consulting a Vedic astrologer for detailed guidance")
    
    return issues

def calculate_spiritual_alignment(chart1, chart2):
    """Calculate spiritual alignment score (0-100)"""
    # Simplified calculation based on nakshatra compatibility
    nakshatra_diff = abs(chart1["nakshatra"] - chart2["nakshatra"])
    
    if nakshatra_diff == 0:
        return 100
    elif nakshatra_diff <= 3:
        return 85
    elif nakshatra_diff <= 6:
        return 70
    elif nakshatra_diff <= 9:
        return 55
    elif nakshatra_diff <= 13:
        return 40
    else:
        return 25

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"Starting Vedic Compatibility API on port {port}")
    print(f"Environment: PORT={os.environ.get('PORT', 'Not set')}")
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"Failed to start server: {e}")
        import traceback
        traceback.print_exc()
# Force redeploy - Sat Jul 12 14:54:12 IST 2025
