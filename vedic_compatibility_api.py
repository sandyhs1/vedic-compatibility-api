import os
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
import ephem
from datetime import datetime
import math
import json

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
    """Calculate birth chart using ephem"""
    try:
        # Parse date and time
        date_obj = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        
        # Get coordinates
        lat, lon = get_coordinates(place)
        
        # Create observer
        observer = ephem.Observer()
        observer.lat = str(lat)
        observer.lon = str(lon)
        observer.date = date_obj
        
        # Calculate Sun position
        sun = ephem.Sun()
        sun.compute(observer)
        
        # Get Sun's longitude (tropical)
        sun_longitude = math.degrees(sun.hlong)
        
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

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Vedic Compatibility API is running"})

@app.route('/api/compatibility', methods=['POST'])
def compatibility():
    try:
        data = request.get_json()
        
        if not data or 'partner1' not in data or 'partner2' not in data:
            return jsonify({"error": "Missing partner data"}), 400
        
        # Calculate birth charts
        chart1 = calculate_birth_chart(
            data['partner1']['date'],
            data['partner1']['time'],
            data['partner1']['place']
        )
        
        chart2 = calculate_birth_chart(
            data['partner2']['date'],
            data['partner2']['time'],
            data['partner2']['place']
        )
        
        if not chart1:
            return jsonify({
                "error": "Failed to calculate birth chart for partner1",
                "details": {
                    "error": str(e),
                    "trace": traceback.format_exc()
                }
            }), 400
        
        if not chart2:
            return jsonify({
                "error": "Failed to calculate birth chart for partner2",
                "details": {
                    "error": str(e),
                    "trace": traceback.format_exc()
                }
            }), 400
        
        # Calculate compatibility
        compatibility_result = calculate_compatibility(chart1, chart2)
        
        if not compatibility_result:
            return jsonify({
                "error": "Failed to calculate compatibility",
                "details": {
                    "error": str(e),
                    "trace": traceback.format_exc()
                }
            }), 400
        
        return jsonify({
            "success": True,
            "partner1_chart": chart1,
            "partner2_chart": chart2,
            "compatibility": compatibility_result
        })
        
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "details": {
                "error": str(e),
                "trace": traceback.format_exc()
            }
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
