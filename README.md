# Vedic Compatibility API

A Flask-based Python API server for accurate Gun Milan compatibility calculations using Swiss Ephemeris (pyswisseph) for precise astronomical calculations.

## Features

- **Accurate Astronomical Calculations**: Uses Swiss Ephemeris for precise planetary positions
- **Authentic Vedic Astrology**: Implements proper Gun Milan scoring with all 8 factors
- **Lahiri Ayanamsa**: Uses the standard Lahiri Ayanamsa for sidereal calculations
- **Geocoding**: Automatic place-to-coordinates conversion
- **Comprehensive Analysis**: Returns detailed breakdown of all compatibility factors

## API Endpoint

### POST `/api/compatibility`

**Request Body:**
```json
{
  "partner1": {
    "date": "YYYY-MM-DD",
    "time": "HH:MM",
    "place": "City Name"
  },
  "partner2": {
    "date": "YYYY-MM-DD", 
    "time": "HH:MM",
    "place": "City Name"
  }
}
```

**Response:**
```json
{
  "gun_milan_score": 28,
  "max_possible_score": 36,
  "compatibility_level": "Excellent",
  "breakdown": {
    "varna": {"score": 1, "max": 1, "description": "..."},
    "vashya": {"score": 2, "max": 2, "description": "..."},
    "tara": {"score": 3, "max": 3, "description": "..."},
    "yoni": {"score": 4, "max": 4, "description": "..."},
    "graha_maitri": {"score": 5, "max": 5, "description": "..."},
    "gana": {"score": 6, "max": 6, "description": "..."},
    "bhakoot": {"score": 7, "max": 7, "description": "..."},
    "nadi": {"score": 8, "max": 8, "description": "..."}
  },
  "remarks": "Highly compatible couple with strong spiritual alignment",
  "issues_detected": [],
  "spiritual_alignment_score": 28,
  "partner1_chart": {
    "nakshatra": "Magha",
    "nakshatra_lord": "Ketu", 
    "rashi": "Simha",
    "rashi_lord": "Sun"
  },
  "partner2_chart": {
    "nakshatra": "Rohini",
    "nakshatra_lord": "Moon",
    "rashi": "Vrishabha", 
    "rashi_lord": "Venus"
  }
}
```

## Local Setup

1. **Install Python 3.8+**

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the server:**
```bash
python vedic_compatibility_api.py
```

4. **Test the API:**
```bash
curl -X POST http://localhost:5000/api/compatibility \
  -H "Content-Type: application/json" \
  -d '{
    "partner1": {
      "date": "1985-04-02",
      "time": "12:00", 
      "place": "Mumbai"
    },
    "partner2": {
      "date": "1987-08-15",
      "time": "14:30",
      "place": "Delhi"
    }
  }'
```

## Free Deployment Options

### Option 1: Railway.app (Recommended)

1. **Sign up** at [railway.app](https://railway.app)
2. **Connect your GitHub repository**
3. **Add environment variables** (if needed)
4. **Deploy automatically**

### Option 2: Render.com

1. **Sign up** at [render.com](https://render.com)
2. **Create a new Web Service**
3. **Connect your GitHub repository**
4. **Set build command:** `pip install -r requirements.txt`
5. **Set start command:** `python vedic_compatibility_api.py`

### Option 3: Google Cloud Run

1. **Install Google Cloud CLI**
2. **Create a Dockerfile:**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "vedic_compatibility_api.py"]
```

3. **Deploy:**
```bash
gcloud run deploy vedic-compatibility-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Gun Milan Scoring

The API calculates all 8 factors of Gun Milan:

1. **Varna (1 point)**: Social compatibility
2. **Vashya (2 points)**: Control and dominance
3. **Tara (3 points)**: Star compatibility
4. **Yoni (4 points)**: Sexual compatibility
5. **Graha Maitri (5 points)**: Planetary friendship
6. **Gana (6 points)**: Temperament compatibility
7. **Bhakoot (7 points)**: Rashi compatibility
8. **Nadi (8 points)**: Health and progeny

**Total Maximum Score: 36 points**

- **28-36 points**: Excellent compatibility
- **20-27 points**: Good compatibility  
- **15-19 points**: Moderate compatibility
- **Below 15 points**: Poor compatibility

## Accuracy Notes

- Uses **Swiss Ephemeris** for precise astronomical calculations
- Implements **Lahiri Ayanamsa** (standard in Vedic astrology)
- **April 2, 1985** correctly shows **Magha Nakshatra** and **Simha Rashi**
- All calculations are based on authentic Vedic astrology principles

## Health Check

```bash
curl http://localhost:5000/health
```

Returns: `{"status": "healthy", "service": "Vedic Compatibility API"}` # Force redeploy Sat Jul 12 12:51:52 IST 2025
# Force redeploy Sat Jul 12 15:06:12 IST 2025
# Force redeploy Sat Jul 12 15:59:43 IST 2025
# Force redeploy Sat Jul 12 16:13:07 IST 2025
# Force redeploy Sat Jul 12 16:36:24 IST 2025
# Force redeploy for OpenAI API switch Sat Jul 12 16:41:58 IST 2025
# Force redeploy to ensure OpenAI API is working Sat Jul 12 16:47:08 IST 2025
# Force redeploy to test updated OpenAI API key Sat Jul 12 16:52:42 IST 2025
# Force redeploy to refresh environment variables Sat Jul 12 16:55:58 IST 2025
# Force redeploy to fix 500 errors Sat Jul 12 17:03:46 IST 2025
