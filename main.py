# main.py - Instagram Info API (Dual Source - SECURE)
# Made by @KINGFFAIAK47x · ANSH AFT

from flask import Flask, jsonify, request
import requests
import time
import re
import os
import json
from functools import wraps

app = Flask(__name__)

# ==============================================
# 🔐 API KEYS (env se lo, hardcode mat karo)
# ==============================================

VALID_KEYS = {}
_k1 = os.environ.get("API_KEY_1")
_k2 = os.environ.get("API_KEY_2")
if _k1: VALID_KEYS[_k1] = "full_access"
if _k2: VALID_KEYS[_k2] = "full_access"
# Fallback (sirf testing ke liye — production me hatao)
if not VALID_KEYS:
    VALID_KEYS = {"ANSHPAPA": "full_access", "FF": "full_access"}

CREDIT = {"username": "@KINGFFAIAK47x", "made_by": "ANSH AFT"}

# ==============================================
# 🌐 EXTERNAL SOURCES
# ==============================================

# Source 1: Cloud Function (File 1 wala — POST, no key)
CLOUD_FUNCTION_URL = "https://europe-west3-storyviewer-7a64d.cloudfunctions.net/getInstagramData"

# Source 2: Render API (File 2 wala — GET, full profile)
EXTERNAL_API_BASE = "https://instagram-info-by-ansh.onrender.com/profile/"

IS_VERCEL = os.environ.get("VERCEL", "") == "1" or os.environ.get("VERCEL_ENV", "") != ""
TIMEOUT = 8 if IS_VERCEL else 30

# ==============================================
# 🔐 AUTH
# ==============================================

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = kwargs.get('key', '').strip()
        if not api_key:
            return jsonify({
                "status": "error",
                "error_code": "MISSING_API_KEY",
                "message": "API key required",
                "usage": "/api/profile/{username}/key={your_key}",
                "credit": CREDIT
            }), 401
        if api_key not in VALID_KEYS:
            return jsonify({
                "status": "error",
                "error_code": "INVALID_API_KEY",
                "message": "Invalid API key",
                "credit": CREDIT
            }), 403
        return f(*args, **kwargs)
    return decorated_function

# ==============================================
# ✅ VALIDATION
# ==============================================

def validate_username(username):
    if not username:
        return False, "Username required"
    username = str(username).strip().lstrip('@').lower()
    if not re.match(r'^[A-Za-z0-9._]{1,30}$', username):
        return False, "Invalid Instagram username (letters, numbers, periods, underscores only, 1-30 chars)"
    return True, username

# ==============================================
# 📡 SOURCE 1: CLOUD FUNCTION (File 1 wala)
# ==============================================

def fetch_from_cloud_function(username):
    payload = {
        "data": {
            "endpoint": "/v1/info",
            "params": {
                "include_about": True,
                "username_or_id_or_url": username
            }
        }
    }
    headers = {
        'User-Agent': "okhttp/4.10.0",
        'content-type': "application/json; charset=utf-8"
    }
    try:
        r = requests.post(CLOUD_FUNCTION_URL, json=payload, headers=headers, timeout=TIMEOUT)
        if r.status_code != 200:
            return {"success": False, "error": f"CloudFunction HTTP {r.status_code}: {r.text[:150]}"}
        try:
            data = r.json()
        except json.JSONDecodeError:
            return {"success": False, "error": "CloudFunction returned non-JSON"}

        about = data.get('result', {}).get('data', {}).get('about', {})
        main = data.get('result', {}).get('data', {})
        user_data = {**about, **main}
        for field in ['fbid_v2', 'instagram_pk', 'id']:
            user_data.pop(field, None)
        if not user_data:
            return {"success": False, "error": "No user data (private/deleted)"}
        return {"success": True, "data": user_data, "source": "cloudfunction"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": f"CloudFunction timeout ({TIMEOUT}s)"}
    except requests.exceptions.ConnectionError as e:
        return {"success": False, "error": f"CloudFunction connection error: {str(e)[:120]}"}
    except Exception as e:
        return {"success": False, "error": f"CloudFunction error: {str(e)[:120]}"}

# ==============================================
# 📡 SOURCE 2: RENDER API (File 2 wala)
# ==============================================

def fetch_from_external_api(username):
    url = f"{EXTERNAL_API_BASE}{username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        r = requests.get(url, headers=headers, timeout=TIMEOUT)
        if r.status_code == 200:
            try:
                return {"success": True, "data": r.json(), "source": "render"}
            except Exception:
                return {"success": False, "error": "Render API invalid JSON"}
        elif r.status_code == 404:
            return {"success": False, "error": f"Profile @{username} not found"}
        elif r.status_code == 429:
            return {"success": False, "error": "Render API rate limited (429)"}
        else:
            return {"success": False, "error": f"Render API HTTP {r.status_code}"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": f"Render API timeout ({TIMEOUT}s)"}
    except requests.exceptions.ConnectionError as e:
        return {"success": False, "error": f"Render connection error: {str(e)[:120]}"}
    except Exception as e:
        return {"success": False, "error": f"Render error: {str(e)[:120]}"}

# ==============================================
# 🎨 NORMALIZE RESPONSE (dono source ka same format)
# ==============================================

def normalize_cloudfunction(raw):
    return {
        "username": raw.get('username', 'N/A'),
        "full_name": raw.get('full_name', 'N/A'),
        "biography": raw.get('biography', 'N/A'),
        "joined": raw.get('date_joined', 'N/A'),
        "followers": raw.get('follower_count', 0),
        "following": raw.get('following_count', 0),
        "posts": raw.get('media_count', 0),
        "is_private": bool(raw.get('is_private')),
        "is_verified": bool(raw.get('is_verified')),
        "profile_pic_url": raw.get('profile_pic_url', 'N/A'),
        "account_creation_year": raw.get('account_creation_year'),
        "is_business_account": bool(raw.get('is_business_account')),
        "is_professional_account": bool(raw.get('is_professional_account')),
        "category_name": raw.get('category_name'),
        "external_url": raw.get('external_url'),
    }

def normalize_render(raw):
    profile = raw.get("profile", {}) or {}
    return {
        "username": profile.get("username", 'N/A'),
        "full_name": profile.get("full_name", 'N/A'),
        "biography": profile.get("biography", 'N/A'),
        "joined": profile.get("account_creation_year", 'N/A'),
        "followers": profile.get("followers", 0),
        "following": profile.get("following", 0),
        "posts": profile.get("posts", 0),
        "is_private": bool(profile.get("is_private")),
        "is_verified": bool(profile.get("is_verified")),
        "profile_pic_url": profile.get("profile_pic_url", 'N/A'),
        "profile_pic_url_hd": profile.get("profile_pic_url_hd"),
        "account_creation_year": profile.get("account_creation_year"),
        "is_business_account": bool(profile.get("is_business_account")),
        "is_professional_account": bool(profile.get("is_professional_account")),
        "category_name": profile.get("category_name"),
        "business_category_name": profile.get("business_category_name"),
        "external_url": profile.get("external_url"),
    }

# ==============================================
# 🚀 MAIN PROCESS (dual source + fallback)
# ==============================================

def process_profile(username, source="auto"):
    is_valid, result = validate_username(username)
    if not is_valid:
        return jsonify({
            "status": "error",
            "error_code": "INVALID_USERNAME",
            "message": result,
            "credit": CREDIT
        }), 400

    username_clean = result
    start_time = time.time()
    api_result = None
    tried = []

    # source=cloudfunction → sirf cloud
    # source=render       → sirf render
    # source=auto (default)→ cloud pehle, fail hone pe render fallback

    if source in ("auto", "cloudfunction"):
        api_result = fetch_from_cloud_function(username_clean)
        tried.append({"source": "cloudfunction", "success": api_result.get("success"), "error": api_result.get("error")})

    if (source in ("auto", "render")) and (not api_result or not api_result.get("success")):
        if source == "auto" and api_result:
            pass  # fallback continue
        render_result = fetch_from_external_api(username_clean)
        tried.append({"source": "render", "success": render_result.get("success"), "error": render_result.get("error")})
        if render_result.get("success"):
            api_result = render_result

    total_time = round((time.time() - start_time) * 1000, 2)

    if not api_result or not api_result.get("success"):
        return jsonify({
            "status": "error",
            "error_code": "ALL_SOURCES_FAILED",
            "message": "Dono sources fail ho gaye",
            "attempts": tried,
            "username": username_clean,
            "response_time": f"{total_time}ms",
            "credit": CREDIT
        }), 400

    # Normalize depending on which source succeeded
    if api_result.get("source") == "cloudfunction":
        profile = normalize_cloudfunction(api_result["data"])
        final_url = f"https://www.instagram.com/{profile['username']}/?hl=en"
    else:
        profile = normalize_render(api_result["data"])
        final_url = api_result["data"].get("final_url", f"https://www.instagram.com/{username_clean}/?hl=en")

    return jsonify({
        "status": "success",
        "source": api_result.get("source"),
        "username": profile["username"],
        "final_url": final_url,
        "profile": profile,
        "response_time": f"{total_time}ms",
        "attempts": tried,
        "credit": CREDIT
    }), 200

# ==============================================
# 🛣️ ROUTES
# ==============================================

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "service": "📱 Instagram Info API (Dual Source)",
        "version": "2.0.0",
        "description": "Cloud Function + Render API with auto-fallback",
        "sources": {
            "cloudfunction": CLOUD_FUNCTION_URL,
            "render": EXTERNAL_API_BASE
        },
        "endpoints": {
            "/api/profile/{username}/key={key}": "Auto (cloud → render fallback)",
            "/api/profile/{username}/key={key}?source=cloudfunction": "Force cloud function",
            "/api/profile/{username}/key={key}?source=render": "Force render API",
            "/api/instagram?username={username}&key={key}": "File 1 style (query params)",
            "/profile/{username}?key={key}": "Old format"
        },
        "credit": CREDIT
    })

# Route 1: /api/profile/<username>/key=<key>
@app.route('/api/profile/<username>/key=<key>', methods=['GET'])
@require_api_key
def get_profile_route1(username, key):
    source = request.args.get('source', 'auto').lower().strip()
    return process_profile(username, source=source)

# Route 2: /api/profile/key=<key>/username=<username>
@app.route('/api/profile/key=<key>/username=<username>', methods=['GET'])
@require_api_key
def get_profile_route2(key, username):
    source = request.args.get('source', 'auto').lower().strip()
    return process_profile(username, source=source)

# Route 3: File 1 style — /api/instagram?username=X&key=Y
@app.route('/api/instagram', methods=['GET'])
def get_instagram_info_query():
    api_key = request.args.get('key', '').strip()
    username = request.args.get('username', '').strip()
    if not api_key:
        return jsonify({"status": "error", "error_code": "MISSING_API_KEY",
                        "usage": "/api/instagram?username=therock&key=your_key",
                        "credit": CREDIT}), 401
    if api_key not in VALID_KEYS:
        return jsonify({"status": "error", "error_code": "INVALID_API_KEY", "credit": CREDIT}), 403
    if not username:
        return jsonify({"status": "error", "error_code": "MISSING_USERNAME",
                        "usage": "/api/instagram?username=therock&key=your_key",
                        "credit": CREDIT}), 400
    source = request.args.get('source', 'auto').lower().strip()
    return process_profile(username, source=source)

# Route 4: Old format /profile/<username>?key=X
@app.route('/profile/<username>', methods=['GET'])
def get_profile_old(username):
    api_key = request.args.get('key', '').strip()
    if not api_key:
        return jsonify({"status": "error", "error_code": "MISSING_API_KEY",
                        "usage": "/profile/instagram?key=your_api_key",
                        "credit": CREDIT}), 401
    if api_key not in VALID_KEYS:
        return jsonify({"status": "error", "error_code": "INVALID_API_KEY", "credit": CREDIT}), 403
    source = request.args.get('source', 'auto').lower().strip()
    return process_profile(username, source=source)

# Health
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "sources": {
            "cloudfunction": CLOUD_FUNCTION_URL,
            "render": EXTERNAL_API_BASE
        },
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "credit": CREDIT
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"status": "error", "error_code": "NOT_FOUND",
                    "message": "Endpoint not found",
                    "usage": "/api/profile/instagram/key=your_key",
                    "credit": CREDIT}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"status": "error", "error_code": "INTERNAL_ERROR",
                    "message": "Internal server error", "credit": CREDIT}), 500

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"status": "error", "error_code": "METHOD_NOT_ALLOWED",
                    "message": "Only GET allowed", "credit": CREDIT}), 405

# ==============================================
# MAIN
# ==============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 60)
    print("📱 INSTAGRAM INFO API v2.0.0 (Dual Source)")
    print("=" * 60)
    print(f"🚀 Running on: http://localhost:{port}")
    print(f"☁️  Cloud Function: {CLOUD_FUNCTION_URL}")
    print(f"🌐 Render API:     {EXTERNAL_API_BASE}")
    print(f"⏱️  Timeout: {TIMEOUT}s")
    print("\n📌 Usage:")
    print("  /api/profile/instagram/key=ANSHPAPA")
    print("  /api/profile/instagram/key=ANSHPAPA?source=cloudfunction")
    print("  /api/profile/instagram/key=ANSHPAPA?source=render")
    print("  /api/instagram?username=therock&key=ANSHPAPA")
    print("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=False)
