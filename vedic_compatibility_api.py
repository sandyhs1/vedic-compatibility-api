from flask import Flask, request, jsonify
from flask_cors import CORS
import pyswisseph as swe
from datetime import datetime
import math
import json
import os
import traceback

app = Flask(__name__)
CORS(app)

# Initialize Swiss Ephemeris
swe.set_ephe_path(os.path.join(os.path.dirname(__file__), "ephe"))

# Nakshatra data (27 nakshatras with their lords and degrees)
NAKSHATRAS = [
    {"name": "Ashwini", "lord": "Ketu", "start": 0, "end": 13.333},
    {"name": "Bharani", "lord": "Venus", "start": 13.333, "end": 26.667},
    {"name": "Krittika", "lord": "Sun", "start": 26.667, "end": 40},
    {"name": "Rohini", "lord": "Moon", "start": 40, "end": 53.333},
    {"name": "Mrigashira", "lord": "Mars", "start": 53.333, "end": 66.667},
    {"name": "Ardra", "lord": "Rahu", "start": 66.667, "end": 80},
    {"name": "Punarvasu", "lord": "Jupiter", "start": 80, "end": 93.333},
    {"name": "Pushya", "lord": "Saturn", "start": 93.333, "end": 106.667},
    {"name": "Ashlesha", "lord": "Mercury", "start": 106.667, "end": 120},
    {"name": "Magha", "lord": "Ketu", "start": 120, "end": 133.333},
    {"name": "Purva Phalguni", "lord": "Venus", "start": 133.333, "end": 146.667},
    {"name": "Uttara Phalguni", "lord": "Sun", "start": 146.667, "end": 160},
    {"name": "Hasta", "lord": "Moon", "start": 160, "end": 173.333},
    {"name": "Chitra", "lord": "Mars", "start": 173.333, "end": 186.667},
    {"name": "Swati", "lord": "Rahu", "start": 186.667, "end": 200},
    {"name": "Vishakha", "lord": "Jupiter", "start": 200, "end": 213.333},
    {"name": "Anuradha", "lord": "Saturn", "start": 213.333, "end": 226.667},
    {"name": "Jyeshtha", "lord": "Mercury", "start": 226.667, "end": 240},
    {"name": "Mula", "lord": "Ketu", "start": 240, "end": 253.333},
    {"name": "Purva Ashadha", "lord": "Venus", "start": 253.333, "end": 266.667},
    {"name": "Uttara Ashadha", "lord": "Sun", "start": 266.667, "end": 280},
    {"name": "Shravana", "lord": "Moon", "start": 280, "end": 293.333},
    {"name": "Dhanishta", "lord": "Mars", "start": 293.333, "end": 306.667},
    {"name": "Shatabhisha", "lord": "Rahu", "start": 306.667, "end": 320},
    {"name": "Purva Bhadrapada", "lord": "Jupiter", "start": 320, "end": 333.333},
    {"name": "Uttara Bhadrapada", "lord": "Saturn", "start": 333.333, "end": 346.667},
    {"name": "Revati", "lord": "Mercury", "start": 346.667, "end": 360}
]

# Rashi data (12 rashis with their lords)
RASHIS = [
    {"name": "Mesha", "lord": "Mars", "start": 0, "end": 30},
    {"name": "Vrishabha", "lord": "Venus", "start": 30, "end": 60},
    {"name": "Mithuna", "lord": "Mercury", "start": 60, "end": 90},
    {"name": "Karka", "lord": "Moon", "start": 90, "end": 120},
    {"name": "Simha", "lord": "Sun", "start": 120, "end": 150},
    {"name": "Kanya", "lord": "Mercury", "start": 150, "end": 180},
    {"name": "Tula", "lord": "Venus", "start": 180, "end": 210},
    {"name": "Vrishchika", "lord": "Mars", "start": 210, "end": 240},
    {"name": "Dhanu", "lord": "Jupiter", "start": 240, "end": 270},
    {"name": "Makara", "lord": "Saturn", "start": 270, "end": 300},
    {"name": "Kumbha", "lord": "Saturn", "start": 300, "end": 330},
    {"name": "Meena", "lord": "Jupiter", "start": 330, "end": 360}
]

# Guna Milan scoring tables
VASYA_SCORES = {
    ("Mesha", "Mesha"): 2, ("Mesha", "Vrishabha"): 1, ("Mesha", "Mithuna"): 2, ("Mesha", "Karka"): 0,
    ("Mesha", "Simha"): 2, ("Mesha", "Kanya"): 1, ("Mesha", "Tula"): 0, ("Mesha", "Vrishchika"): 2,
    ("Mesha", "Dhanu"): 1, ("Mesha", "Makara"): 0, ("Mesha", "Kumbha"): 0, ("Mesha", "Meena"): 1,
    ("Vrishabha", "Mesha"): 1, ("Vrishabha", "Vrishabha"): 2, ("Vrishabha", "Mithuna"): 1, ("Vrishabha", "Karka"): 2,
    ("Vrishabha", "Simha"): 0, ("Vrishabha", "Kanya"): 2, ("Vrishabha", "Tula"): 2, ("Vrishabha", "Vrishchika"): 1,
    ("Vrishabha", "Dhanu"): 0, ("Vrishabha", "Makara"): 1, ("Vrishabha", "Kumbha"): 1, ("Vrishabha", "Meena"): 0,
    ("Mithuna", "Mesha"): 2, ("Mithuna", "Vrishabha"): 1, ("Mithuna", "Mithuna"): 2, ("Mithuna", "Karka"): 1,
    ("Mithuna", "Simha"): 1, ("Mithuna", "Kanya"): 2, ("Mithuna", "Tula"): 2, ("Mithuna", "Vrishchika"): 1,
    ("Mithuna", "Dhanu"): 1, ("Mithuna", "Makara"): 0, ("Mithuna", "Kumbha"): 0, ("Mithuna", "Meena"): 1,
    ("Karka", "Mesha"): 0, ("Karka", "Vrishabha"): 2, ("Karka", "Mithuna"): 1, ("Karka", "Karka"): 2,
    ("Karka", "Simha"): 1, ("Karka", "Kanya"): 1, ("Karka", "Tula"): 2, ("Karka", "Vrishchika"): 0,
    ("Karka", "Dhanu"): 1, ("Karka", "Makara"): 2, ("Karka", "Kumbha"): 1, ("Karka", "Meena"): 2,
    ("Simha", "Mesha"): 2, ("Simha", "Vrishabha"): 0, ("Simha", "Mithuna"): 1, ("Simha", "Karka"): 1,
    ("Simha", "Simha"): 2, ("Simha", "Kanya"): 0, ("Simha", "Tula"): 1, ("Simha", "Vrishchika"): 2,
    ("Simha", "Dhanu"): 2, ("Simha", "Makara"): 0, ("Simha", "Kumbha"): 0, ("Simha", "Meena"): 1,
    ("Kanya", "Mesha"): 1, ("Kanya", "Vrishabha"): 2, ("Kanya", "Mithuna"): 2, ("Kanya", "Karka"): 1,
    ("Kanya", "Simha"): 0, ("Kanya", "Kanya"): 2, ("Kanya", "Tula"): 1, ("Kanya", "Vrishchika"): 1,
    ("Kanya", "Dhanu"): 0, ("Kanya", "Makara"): 1, ("Kanya", "Kumbha"): 1, ("Kanya", "Meena"): 0,
    ("Tula", "Mesha"): 0, ("Tula", "Vrishabha"): 2, ("Tula", "Mithuna"): 2, ("Tula", "Karka"): 2,
    ("Tula", "Simha"): 1, ("Tula", "Kanya"): 1, ("Tula", "Tula"): 2, ("Tula", "Vrishchika"): 1,
    ("Tula", "Dhanu"): 0, ("Tula", "Makara"): 1, ("Tula", "Kumbha"): 1, ("Tula", "Meena"): 0,
    ("Vrishchika", "Mesha"): 2, ("Vrishchika", "Vrishabha"): 1, ("Vrishchika", "Mithuna"): 1, ("Vrishchika", "Karka"): 0,
    ("Vrishchika", "Simha"): 2, ("Vrishchika", "Kanya"): 1, ("Vrishchika", "Tula"): 1, ("Vrishchika", "Vrishchika"): 2,
    ("Vrishchika", "Dhanu"): 1, ("Vrishchika", "Makara"): 0, ("Vrishchika", "Kumbha"): 0, ("Vrishchika", "Meena"): 1,
    ("Dhanu", "Mesha"): 1, ("Dhanu", "Vrishabha"): 0, ("Dhanu", "Mithuna"): 1, ("Dhanu", "Karka"): 1,
    ("Dhanu", "Simha"): 2, ("Dhanu", "Kanya"): 0, ("Dhanu", "Tula"): 0, ("Dhanu", "Vrishchika"): 1,
    ("Dhanu", "Dhanu"): 2, ("Dhanu", "Makara"): 1, ("Dhanu", "Kumbha"): 1, ("Dhanu", "Meena"): 2,
    ("Makara", "Mesha"): 0, ("Makara", "Vrishabha"): 1, ("Makara", "Mithuna"): 0, ("Makara", "Karka"): 2,
    ("Makara", "Simha"): 0, ("Makara", "Kanya"): 1, ("Makara", "Tula"): 1, ("Makara", "Vrishchika"): 0,
    ("Makara", "Dhanu"): 1, ("Makara", "Makara"): 2, ("Makara", "Kumbha"): 2, ("Makara", "Meena"): 1,
    ("Kumbha", "Mesha"): 0, ("Kumbha", "Vrishabha"): 1, ("Kumbha", "Mithuna"): 0, ("Kumbha", "Karka"): 1,
    ("Kumbha", "Simha"): 0, ("Kumbha", "Kanya"): 1, ("Kumbha", "Tula"): 1, ("Kumbha", "Vrishchika"): 0,
    ("Kumbha", "Dhanu"): 1, ("Kumbha", "Makara"): 2, ("Kumbha", "Kumbha"): 2, ("Kumbha", "Meena"): 1,
    ("Meena", "Mesha"): 1, ("Meena", "Vrishabha"): 0, ("Meena", "Mithuna"): 1, ("Meena", "Karka"): 2,
    ("Meena", "Simha"): 1, ("Meena", "Kanya"): 0, ("Meena", "Tula"): 0, ("Meena", "Vrishchika"): 1,
    ("Meena", "Dhanu"): 2, ("Meena", "Makara"): 1, ("Meena", "Kumbha"): 1, ("Meena", "Meena"): 2
}

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
    "bareilly": {"lat": 28.3670, "lon": 79.4304},
    "moradabad": {"lat": 28.8389, "lon": 78.7738},
    "mysore": {"lat": 12.2958, "lon": 76.6394},
    "gurgaon": {"lat": 28.4595, "lon": 77.0266},
    "aligarh": {"lat": 27.8974, "lon": 78.0880},
    "jalandhar": {"lat": 31.3260, "lon": 75.5762},
    "tiruchirappalli": {"lat": 10.7905, "lon": 78.7047},
    "bhubaneswar": {"lat": 20.2961, "lon": 85.8245},
    "salem": {"lat": 11.6643, "lon": 78.1460},
    "warangal": {"lat": 17.9689, "lon": 79.5941},
    "mira": {"lat": 19.2952, "lon": 72.8544},
    "thiruvananthapuram": {"lat": 8.5241, "lon": 76.9366},
    "bhiwandi": {"lat": 19.2969, "lon": 73.0625},
    "saharanpur": {"lat": 29.9675, "lon": 77.5451},
    "guntur": {"lat": 16.2991, "lon": 80.4575},
    "amravati": {"lat": 20.9374, "lon": 77.7796},
    "noida": {"lat": 28.5355, "lon": 77.3910},
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
    "bhagalpur": {"lat": 25.2445, "lon": 87.0068},
    "bellary": {"lat": 15.1394, "lon": 76.9214},
    "mangalore": {"lat": 12.9716, "lon": 74.8631},
    "tiruppur": {"lat": 11.1085, "lon": 77.3411},
    "malegaon": {"lat": 20.5609, "lon": 74.5251},
    "belgaum": {"lat": 15.8497, "lon": 74.4977},
    "kurnool": {"lat": 15.8281, "lon": 78.0373},
    "rajahmundry": {"lat": 17.0005, "lon": 81.8040},
    "kadapa": {"lat": 14.4753, "lon": 78.8354},
    "kakinada": {"lat": 16.9891, "lon": 82.2475},
    "tirupati": {"lat": 13.6288, "lon": 79.4192},
    "anantapur": {"lat": 14.6819, "lon": 77.6006},
    "karimnagar": {"lat": 18.4386, "lon": 79.1288},
    "nizamabad": {"lat": 18.6725, "lon": 78.0941},
    "eluru": {"lat": 16.7069, "lon": 81.1046},
    "baroda": {"lat": 22.3072, "lon": 73.1812},  # Same as vadodara
    "varanasi": {"lat": 25.3176, "lon": 82.9739},
    "srinagar": {"lat": 34.0837, "lon": 74.7973},
    "agra": {"lat": 27.1767, "lon": 78.0081},
    "lucknow": {"lat": 26.8467, "lon": 80.9462},
    "kanpur": {"lat": 26.4499, "lon": 80.3319},
    "nagpur": {"lat": 21.1458, "lon": 79.0882},
    "indore": {"lat": 22.7196, "lon": 75.8577},
    "bhopal": {"lat": 23.2599, "lon": 77.4126},
    "patna": {"lat": 25.5941, "lon": 85.1376},
    "ranchi": {"lat": 23.3441, "lon": 85.3096},
    "jabalpur": {"lat": 23.1815, "lon": 79.9864},
    "gwalior": {"lat": 26.2183, "lon": 78.1828},
    "jodhpur": {"lat": 26.2389, "lon": 73.0243},
    "raipur": {"lat": 21.2514, "lon": 81.6296},
    "kota": {"lat": 25.2138, "lon": 75.8648},
    "guwahati": {"lat": 26.1445, "lon": 91.7362},
    "chandigarh": {"lat": 30.7333, "lon": 76.7794},
    "bareilly": {"lat": 28.3670, "lon": 79.4304},
    "moradabad": {"lat": 28.8389, "lon": 78.7738},
    "aligarh": {"lat": 27.8974, "lon": 78.0880},
    "jalandhar": {"lat": 31.3260, "lon": 75.5762},
    "bhubaneswar": {"lat": 20.2961, "lon": 85.8245},
    "warangal": {"lat": 17.9689, "lon": 79.5941},
    "thiruvananthapuram": {"lat": 8.5241, "lon": 76.9366},
    "saharanpur": {"lat": 29.9675, "lon": 77.5451},
    "guntur": {"lat": 16.2991, "lon": 80.4575},
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
    "bhagalpur": {"lat": 25.2445, "lon": 87.0068},
    "bellary": {"lat": 15.1394, "lon": 76.9214},
    "mangalore": {"lat": 12.9716, "lon": 74.8631},
    "tiruppur": {"lat": 11.1085, "lon": 77.3411},
    "malegaon": {"lat": 20.5609, "lon": 74.5251},
    "belgaum": {"lat": 15.8497, "lon": 74.4977},
    "kurnool": {"lat": 15.8281, "lon": 78.0373},
    "rajahmundry": {"lat": 17.0005, "lon": 81.8040},
    "kadapa": {"lat": 14.4753, "lon": 78.8354},
    "kakinada": {"lat": 16.9891, "lon": 82.2475},
    "tirupati": {"lat": 13.6288, "lon": 79.4192},
    "anantapur": {"lat": 14.6819, "lon": 77.6006},
    "karimnagar": {"lat": 18.4386, "lon": 79.1288},
    "nizamabad": {"lat": 18.6725, "lon": 78.0941},
    "eluru": {"lat": 16.7069, "lon": 81.1046},
    "varanasi": {"lat": 25.3176, "lon": 82.9739}
}

def get_coordinates(place):
    """Get coordinates for a place using local database"""
    try:
        # Clean the place name
        place_lower = place.lower().strip()
        
        # Remove common suffixes
        place_lower = place_lower.replace(", india", "").replace(", india", "")
        place_lower = place_lower.replace(" city", "").replace(" town", "")
        
        # Try exact match first
        if place_lower in INDIAN_CITIES:
            coords = INDIAN_CITIES[place_lower]
            return coords["lat"], coords["lon"]
        
        # Try partial matches
        for city, coords in INDIAN_CITIES.items():
            if city in place_lower or place_lower in city:
                return coords["lat"], coords["lon"]
        
        # Default to Mumbai if no match found
        print(f"Place '{place}' not found in database, defaulting to Mumbai")
        return 19.0760, 72.8777
        
    except Exception as e:
        print(f"Error in get_coordinates: {e}")
        # Default to Mumbai
        return 19.0760, 72.8777

def calculate_birth_chart(date_str, time_str, place):
    """Calculate birth chart using Swiss Ephemeris"""
    try:
        # Parse date and time
        date_obj = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        # Get coordinates
        lat, lon = get_coordinates(place)
        # Convert to Julian Day
        jd = swe.julday(date_obj.year, date_obj.month, date_obj.day, 
                       date_obj.hour + date_obj.minute/60.0)
        # Calculate Sun position (tropical)
        sun_pos = swe.calc_ut(jd, swe.SUN)[0]
        sun_longitude = sun_pos[0]
        # Apply Lahiri Ayanamsa correction (sidereal)
        ayanamsa = 23.85 + (date_obj.year - 2000) * 0.000000317
        sidereal_longitude = sun_longitude - ayanamsa
        # Normalize to 0-360
        sidereal_longitude = sidereal_longitude % 360
        # Find Nakshatra
        nakshatra = None
        for nak in NAKSHATRAS:
            if nak["start"] <= sidereal_longitude < nak["end"]:
                nakshatra = nak
                break
        # Find Rashi
        rashi = None
        for rash in RASHIS:
            if rash["start"] <= sidereal_longitude < rash["end"]:
                rashi = rash
                break
        return {
            "longitude": sidereal_longitude,
            "nakshatra": nakshatra["name"] if nakshatra else "Unknown",
            "nakshatra_lord": nakshatra["lord"] if nakshatra else "Unknown",
            "rashi": rashi["name"] if rashi else "Unknown",
            "rashi_lord": rashi["lord"] if rashi else "Unknown"
        }
    except Exception as e:
        print(f"Error calculating birth chart: {e}")
        traceback.print_exc()
        return {"error": str(e), "trace": traceback.format_exc()}

def calculate_gun_milan(chart1, chart2):
    """Calculate Gun Milan compatibility"""
    breakdown = {}
    total_score = 0
    
    # Varna (1 point)
    varna1 = get_varna(chart1["rashi"])
    varna2 = get_varna(chart2["rashi"])
    varna_score = 1 if varna1 == varna2 else 0
    breakdown["varna"] = {"score": varna_score, "max": 1, "description": f"Varna compatibility: {varna1} & {varna2}"}
    total_score += varna_score
    
    # Vashya (2 points)
    vashya_key = (chart1["rashi"], chart2["rashi"])
    vashya_score = VASYA_SCORES.get(vashya_key, 0)
    breakdown["vashya"] = {"score": vashya_score, "max": 2, "description": f"Vashya compatibility: {chart1['rashi']} & {chart2['rashi']}"}
    total_score += vashya_score
    
    # Tara (3 points) - Simplified calculation
    tara_score = calculate_tara(chart1["nakshatra"], chart2["nakshatra"])
    breakdown["tara"] = {"score": tara_score, "max": 3, "description": f"Tara compatibility: {chart1['nakshatra']} & {chart2['nakshatra']}"}
    total_score += tara_score
    
    # Yoni (4 points)
    yoni_score = calculate_yoni(chart1["nakshatra"], chart2["nakshatra"])
    breakdown["yoni"] = {"score": yoni_score, "max": 4, "description": f"Yoni compatibility: {chart1['nakshatra']} & {chart2['nakshatra']}"}
    total_score += yoni_score
    
    # Graha Maitri (5 points)
    graha_score = calculate_graha_maitri(chart1["rashi_lord"], chart2["rashi_lord"])
    breakdown["graha_maitri"] = {"score": graha_score, "max": 5, "description": f"Graha Maitri: {chart1['rashi_lord']} & {chart2['rashi_lord']}"}
    total_score += graha_score
    
    # Gana (6 points)
    gana_score = calculate_gana(chart1["nakshatra"], chart2["nakshatra"])
    breakdown["gana"] = {"score": gana_score, "max": 6, "description": f"Gana compatibility: {chart1['nakshatra']} & {chart2['nakshatra']}"}
    total_score += gana_score
    
    # Bhakoot (7 points)
    bhakoot_score = calculate_bhakoot(chart1["rashi"], chart2["rashi"])
    breakdown["bhakoot"] = {"score": bhakoot_score, "max": 7, "description": f"Bhakoot compatibility: {chart1['rashi']} & {chart2['rashi']}"}
    total_score += bhakoot_score
    
    # Nadi (8 points)
    nadi_score = calculate_nadi(chart1["nakshatra"], chart2["nakshatra"])
    breakdown["nadi"] = {"score": nadi_score, "max": 8, "description": f"Nadi compatibility: {chart1['nakshatra']} & {chart2['nakshatra']}"}
    total_score += nadi_score
    
    return total_score, breakdown

def get_varna(rashi):
    """Get Varna for Rashi"""
    varna_map = {
        "Mesha": "Kshatriya", "Vrishabha": "Vaishya", "Mithuna": "Brahmin", "Karka": "Kshatriya",
        "Simha": "Kshatriya", "Kanya": "Vaishya", "Tula": "Vaishya", "Vrishchika": "Kshatriya",
        "Dhanu": "Brahmin", "Makara": "Shudra", "Kumbha": "Shudra", "Meena": "Brahmin"
    }
    return varna_map.get(rashi, "Unknown")

def calculate_tara(nakshatra1, nakshatra2):
    """Calculate Tara compatibility (simplified)"""
    # Get nakshatra indices
    idx1 = next((i for i, nak in enumerate(NAKSHATRAS) if nak["name"] == nakshatra1), 0)
    idx2 = next((i for i, nak in enumerate(NAKSHATRAS) if nak["name"] == nakshatra2), 0)
    
    # Calculate distance
    distance = abs(idx1 - idx2) % 27
    
    # Tara scoring
    if distance in [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 25, 26]:
        return 3  # Excellent
    elif distance in [6, 12, 18, 24]:
        return 1  # Poor
    else:
        return 2  # Good

def calculate_yoni(nakshatra1, nakshatra2):
    """Calculate Yoni compatibility (simplified)"""
    # Yoni animals for nakshatras
    yoni_map = {
        "Ashwini": "Horse", "Bharani": "Elephant", "Krittika": "Ram", "Rohini": "Snake",
        "Mrigashira": "Snake", "Ardra": "Dog", "Punarvasu": "Cat", "Pushya": "Ram",
        "Ashlesha": "Cat", "Magha": "Rat", "Purva Phalguni": "Rat", "Uttara Phalguni": "Bull",
        "Hasta": "Buffalo", "Chitra": "Tiger", "Swati": "Buffalo", "Vishakha": "Tiger",
        "Anuradha": "Deer", "Jyeshtha": "Deer", "Mula": "Dog", "Purva Ashadha": "Monkey",
        "Uttara Ashadha": "Mongoose", "Shravana": "Monkey", "Dhanishta": "Lion",
        "Shatabhisha": "Horse", "Purva Bhadrapada": "Lion", "Uttara Bhadrapada": "Cow",
        "Revati": "Elephant"
    }
    
    yoni1 = yoni_map.get(nakshatra1, "Unknown")
    yoni2 = yoni_map.get(nakshatra2, "Unknown")
    
    if yoni1 == yoni2:
        return 4  # Same yoni
    elif yoni1 in ["Horse", "Elephant", "Buffalo", "Lion"] and yoni2 in ["Horse", "Elephant", "Buffalo", "Lion"]:
        return 3  # Compatible
    elif yoni1 in ["Ram", "Tiger", "Deer"] and yoni2 in ["Ram", "Tiger", "Deer"]:
        return 3  # Compatible
    else:
        return 1  # Incompatible

def calculate_graha_maitri(lord1, lord2):
    """Calculate Graha Maitri compatibility"""
    # Planetary friendship
    friends = {
        "Sun": ["Mars", "Jupiter"], "Moon": ["Mercury"], "Mars": ["Sun", "Jupiter"],
        "Mercury": ["Moon", "Venus"], "Jupiter": ["Sun", "Mars"], "Venus": ["Mercury", "Saturn"],
        "Saturn": ["Venus"], "Rahu": ["Ketu"], "Ketu": ["Rahu"]
    }
    
    if lord1 == lord2:
        return 5  # Same lord
    elif lord2 in friends.get(lord1, []):
        return 4  # Friends
    elif lord2 in ["Sun", "Mars"] and lord1 in ["Sun", "Mars"]:
        return 3  # Neutral
    else:
        return 2  # Enemies

def calculate_gana(nakshatra1, nakshatra2):
    """Calculate Gana compatibility"""
    # Gana classification
    deva = ["Ashwini", "Mrigashira", "Punarvasu", "Pushya", "Hasta", "Swati", "Anuradha", "Revati"]
    manushya = ["Bharani", "Rohini", "Ardra", "Purva Phalguni", "Uttara Phalguni", "Purva Ashadha", "Uttara Ashadha", "Purva Bhadrapada", "Uttara Bhadrapada"]
    rakshasa = ["Krittika", "Ashlesha", "Magha", "Chitra", "Vishakha", "Jyeshtha", "Mula", "Dhanishta", "Shatabhisha"]
    
    gana1 = "deva" if nakshatra1 in deva else "manushya" if nakshatra1 in manushya else "rakshasa"
    gana2 = "deva" if nakshatra2 in deva else "manushya" if nakshatra2 in manushya else "rakshasa"
    
    if gana1 == gana2:
        return 6  # Same gana
    elif (gana1 == "deva" and gana2 == "manushya") or (gana1 == "manushya" and gana2 == "deva"):
        return 5  # Compatible
    else:
        return 1  # Incompatible

def calculate_bhakoot(rashi1, rashi2):
    """Calculate Bhakoot compatibility"""
    # Bhakoot scoring based on rashi compatibility
    compatible_pairs = [
        ("Mesha", "Simha"), ("Mesha", "Dhanu"), ("Vrishabha", "Kanya"), ("Vrishabha", "Makara"),
        ("Mithuna", "Tula"), ("Mithuna", "Kumbha"), ("Karka", "Vrishchika"), ("Karka", "Meena"),
        ("Simha", "Mesha"), ("Simha", "Dhanu"), ("Kanya", "Vrishabha"), ("Kanya", "Makara"),
        ("Tula", "Mithuna"), ("Tula", "Kumbha"), ("Vrishchika", "Karka"), ("Vrishchika", "Meena"),
        ("Dhanu", "Mesha"), ("Dhanu", "Simha"), ("Makara", "Vrishabha"), ("Makara", "Kanya"),
        ("Kumbha", "Mithuna"), ("Kumbha", "Tula"), ("Meena", "Karka"), ("Meena", "Vrishchika")
    ]
    
    if (rashi1, rashi2) in compatible_pairs:
        return 7  # Excellent
    elif rashi1 == rashi2:
        return 5  # Same rashi
    else:
        return 0  # Incompatible

def calculate_nadi(nakshatra1, nakshatra2):
    """Calculate Nadi compatibility"""
    # Nadi classification
    adi = ["Ashwini", "Ardra", "Punarvasu", "Ashlesha", "Magha", "Uttara Phalguni", "Swati", "Jyeshtha", "Mula", "Purva Ashadha", "Dhanishta", "Shatabhisha", "Purva Bhadrapada"]
    madhya = ["Bharani", "Mrigashira", "Pushya", "Purva Phalguni", "Hasta", "Vishakha", "Anuradha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
    antya = ["Krittika", "Rohini", "Chitra", "Uttara Ashadha", "Shravana"]
    
    nadi1 = "adi" if nakshatra1 in adi else "madhya" if nakshatra1 in madhya else "antya"
    nadi2 = "adi" if nakshatra2 in adi else "madhya" if nakshatra2 in madhya else "antya"
    
    if nadi1 == nadi2:
        return 0  # Nadi dosha - very bad
    else:
        return 8  # Different nadi - excellent

@app.route('/api/compatibility', methods=['POST'])
def compatibility():
    try:
        data = request.get_json()
        
        # Extract partner data
        partner1 = data.get('partner1', {})
        partner2 = data.get('partner2', {})
        
        # Calculate birth charts
        chart1 = calculate_birth_chart(partner1['date'], partner1['time'], partner1['place'])
        chart2 = calculate_birth_chart(partner2['date'], partner2['time'], partner2['place'])
        
        # If either chart is an error dict, return the error
        if isinstance(chart1, dict) and 'error' in chart1:
            return jsonify({"error": "Failed to calculate birth chart for partner1", "details": chart1}), 400
        if isinstance(chart2, dict) and 'error' in chart2:
            return jsonify({"error": "Failed to calculate birth chart for partner2", "details": chart2}), 400
        if not chart1 or not chart2:
            return jsonify({"error": "Failed to calculate birth charts"}), 400
        
        # Calculate Gun Milan
        gun_milan_score, breakdown = calculate_gun_milan(chart1, chart2)
        
        # Determine compatibility level
        if gun_milan_score >= 28:
            compatibility_level = "Excellent"
            remarks = "Highly compatible couple with strong spiritual alignment"
        elif gun_milan_score >= 20:
            compatibility_level = "Good"
            remarks = "Good compatibility with some areas for growth"
        elif gun_milan_score >= 15:
            compatibility_level = "Moderate"
            remarks = "Moderate compatibility, requires understanding and effort"
        else:
            compatibility_level = "Poor"
            remarks = "Challenging compatibility, requires significant effort and remedies"
        
        # Check for specific issues
        issues_detected = []
        if breakdown["nadi"]["score"] == 0:
            issues_detected.append("nadi_dosha")
        if breakdown["bhakoot"]["score"] == 0:
            issues_detected.append("bhakoot_dosha")
        if breakdown["gana"]["score"] <= 1:
            issues_detected.append("gana_dosha")
        
        # Calculate spiritual alignment score (same as gun milan for now)
        spiritual_alignment_score = gun_milan_score
        
        response = {
            "gun_milan_score": gun_milan_score,
            "max_possible_score": 36,
            "compatibility_level": compatibility_level,
            "breakdown": breakdown,
            "remarks": remarks,
            "issues_detected": issues_detected,
            "spiritual_alignment_score": spiritual_alignment_score,
            "partner1_chart": chart1,
            "partner2_chart": chart2
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"API error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "Vedic Compatibility API"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 