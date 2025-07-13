#!/usr/bin/env python3
"""
Test script for Swiss Ephemeris Vedic calculations
Tests with Sandesh's birth details: 1985-04-02, 11:15, Bangalore, India
"""

import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import swisseph as swe
    from geopy.geocoders import Nominatim
    from timezonefinder import TimezoneFinder
    from datetime import datetime
    import pytz
    
    print("✅ All Swiss Ephemeris libraries imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Install with: pip install pyswisseph geopy timezonefinder")
    sys.exit(1)

# Initialize Swiss Ephemeris
swe.set_ephe_path('.')
swe.set_sid_mode(swe.SIDM_LAHIRI)

# Vedic astrology constants
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

RASHIS = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena"
]

def get_coordinates(place_name):
    """Get coordinates using geopy"""
    try:
        geo = Nominatim(user_agent="soulsync_test")
        location = geo.geocode(place_name)
        if location:
            return location.latitude, location.longitude
        else:
            raise Exception(f"Location not found: {place_name}")
    except Exception as e:
        print(f"Geopy error: {e}")
        # Fallback for Bangalore
        return 12.9716, 77.5946

def get_timezone(lat, lon):
    """Get timezone using timezonefinder"""
    try:
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lng=lon, lat=lat)
        return tz_name if tz_name else "Asia/Kolkata"
    except Exception as e:
        print(f"TimezoneFinder error: {e}")
        return "Asia/Kolkata"

def convert_to_utc(dob_str, tob_str, place):
    """Convert local date/time to UTC Julian Day"""
    try:
        # Parse date and time
        dt_local = datetime.strptime(f"{dob_str} {tob_str}", "%Y-%m-%d %H:%M")
        
        # Get coordinates and timezone
        lat, lon = get_coordinates(place)
        tz_name = get_timezone(lat, lon)
        
        print(f"📍 Location: {place}")
        print(f"🌍 Coordinates: {lat:.4f}, {lon:.4f}")
        print(f"⏰ Timezone: {tz_name}")
        
        # Convert local time to UTC
        local_tz = pytz.timezone(tz_name)
        local_dt = local_tz.localize(dt_local)
        utc_dt = local_dt.astimezone(pytz.UTC)
        
        print(f"🕐 Local time: {local_dt}")
        print(f"🌐 UTC time: {utc_dt}")
        
        # Calculate Julian Day
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, 
                       utc_dt.hour + utc_dt.minute / 60.0)
        
        print(f"📅 Julian Day: {jd:.6f}")
        
        return jd, lat, lon, utc_dt
    except Exception as e:
        print(f"Error converting to UTC: {e}")
        raise

def get_moon_data(jd):
    """Get Moon's position using Swiss Ephemeris"""
    try:
        # Calculate Moon's position
        moon_long, _ = swe.calc_ut(jd, swe.MOON)
        
        # Get sidereal longitude (already corrected for ayanamsa)
        sidereal_long = moon_long[0]  # Longitude in degrees
        
        print(f"🌙 Moon longitude: {sidereal_long:.6f}°")
        
        # Calculate rashi (zodiac sign) - 0-11
        rashi_index = int(sidereal_long / 30)
        rashi_index = max(0, min(11, rashi_index))
        
        # Calculate nakshatra (lunar mansion) - 0-26
        nakshatra_index = int(sidereal_long / (360 / 27))
        nakshatra_index = max(0, min(26, nakshatra_index))
        
        rashi_name = RASHIS[rashi_index]
        nakshatra_name = NAKSHATRAS[nakshatra_index]
        
        print(f"♈ Rashi: {rashi_name} (index: {rashi_index})")
        print(f"✨ Nakshatra: {nakshatra_name} (index: {nakshatra_index})")
        
        return {
            "longitude": sidereal_long,
            "rashi": rashi_index + 1,
            "nakshatra": nakshatra_index + 1,
            "rashi_name": rashi_name,
            "nakshatra_name": nakshatra_name
        }
    except Exception as e:
        print(f"Error calculating Moon data: {e}")
        raise

def main():
    """Test with Sandesh's birth details"""
    print("🧪 Testing Swiss Ephemeris Vedic Calculations")
    print("=" * 50)
    
    # Test data
    dob = "1985-04-02"
    tob = "11:15"
    place = "Bangalore, India"
    
    print(f"👤 Test Person: Sandesh")
    print(f"📅 Date of Birth: {dob}")
    print(f"🕐 Time of Birth: {tob}")
    print(f"📍 Place of Birth: {place}")
    print()
    
    try:
        # Convert to UTC
        jd, lat, lon, utc_dt = convert_to_utc(dob, tob, place)
        print()
        
        # Get Moon data
        moon_data = get_moon_data(jd)
        print()
        
        # Display results
        print("📊 RESULTS:")
        print("=" * 30)
        print(f"🌙 Moon Longitude: {moon_data['longitude']:.6f}°")
        print(f"♈ Rashi: {moon_data['rashi_name']}")
        print(f"✨ Nakshatra: {moon_data['nakshatra_name']}")
        print(f"📅 Julian Day: {jd:.6f}")
        print()
        
        print("✅ Swiss Ephemeris calculation successful!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 