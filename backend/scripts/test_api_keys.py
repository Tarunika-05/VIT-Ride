import os
import sys
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
gmaps_key = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()

print("=" * 60)
print("🔑 API KEYS VERIFICATION REPORT")
print("=" * 60)

# 1. Test Gemini API (using gemini-3.6-flash)
print("\n[1/2] Testing Google Gemini API...")
if not gemini_key:
    print("[-] FAIL: GEMINI_API_KEY is empty in .env")
else:
    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel("gemini-3.6-flash")
        response = model.generate_content("Reply with 'Gemini API is verified and working!'")
        print(f"[+] SUCCESS: Gemini API responded:")
        print(f"    '{response.text.strip()}'")
    except Exception as e:
        print(f"[-] ERROR with Gemini API: {e}")

# 2. Test Google Routes API (Modern Directions API)
print("\n[2/2] Testing Google Routes API (Travel Times & Distance)...")
if not gmaps_key:
    print("[-] FAIL: GOOGLE_MAPS_API_KEY is empty in .env")
else:
    try:
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": gmaps_key,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters"
        }
        # Chromepet to VIT Chennai
        payload = {
            "origin": {"location": {"latLng": {"latitude": 12.9516, "longitude": 80.1462}}},
            "destination": {"location": {"latLng": {"latitude": 12.8406, "longitude": 80.1534}}},
            "travelMode": "DRIVE"
        }
        res = requests.post("https://routes.googleapis.com/directions/v2:computeRoutes", headers=headers, json=payload, timeout=10)
        if res.status_code == 200:
            data = res.json()
            route = data["routes"][0]
            dist_km = round(route.get("distanceMeters", 0) / 1000, 2)
            dur_sec = int(route.get("duration", "0s").replace("s", ""))
            dur_min = round(dur_sec / 60, 1)
            print(f"[+] SUCCESS: Google Routes API connected!")
            print(f"    Sample Route: Chromepet -> VIT Chennai")
            print(f"    Distance: {dist_km} km, Estimated Travel Duration: {dur_min} mins")
        else:
            print(f"[-] ERROR with Google Routes API (Status {res.status_code}): {res.text}")
    except Exception as e:
        print(f"[-] ERROR with Google Routes API: {e}")

print("\n" + "=" * 60)
