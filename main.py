# main.py - Instagram Info API (External Fetch - SECURE)
# Made by @KINGFFAIAK47x · ANSH AFT

from flask import Flask, jsonify, request
import requests
import time
import re
import os
from functools import wraps

app = Flask(__name__)

# ==============================================
# 📱 INSTAGRAM INFO API
# Made by @KINGFFAIAK47x · ANSH AFT
# ==============================================

# ONLY 2 KEYS (HIDDEN)
VALID_KEYS = {
    "ANSHPAPA": "full_access",
    "FF": "full_access"
}

# ==============================================
# EXTERNAL API CONFIG
# ==============================================

EXTERNAL_API_BASE = "https://instagram-info-by-ansh.onrender.com/profile/"

# ==============================================
# AUTHENTICATION - URL PATH BASED
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
                "credit": {"username": "@KINGFFAIAK47x", "made_by": "ANSH AFT"}
            }), 401
        
        if api_key not in VALID_KEYS:
            return jsonify({
                "status": "error",
                "error_code": "INVALID_API_KEY",
                "message": "Invalid API key",
                "credit": {"username": "@KINGFFAIAK47x", "made_by": "ANSH AFT"}
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function


# ==============================================
# VALIDATION
# ==============================================

def validate_username(username):
    if not username:
        return False, "Username required"
    
    username = str(username).strip().lstrip('@').lower()
    
    if not re.match(r'^[A-Za-z0-9._]{1,30}$', username):
        return False, "Invalid Instagram username (letters, numbers, periods, underscores only, 1-30 chars)"
    
    return True, username


# ==============================================
# EXTERNAL API FETCH
# ==============================================

def fetch_from_external_api(username):
    url = f"{EXTERNAL_API_BASE}{username}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=30)
        
        if r.status_code == 200:
            try:
                data = r.json()
                return {"success": True, "data": data}
            except:
                return {"success": False, "error": "Invalid JSON from external API"}
        elif r.status_code == 404:
            return {"success": False, "error": f"Profile @{username} not found"}
        elif r.status_code == 429:
            return {"success": False, "error": "External API rate limited (429). Try again later."}
        else:
            return {"success": False, "error": f"External API returned status {r.status_code}"}
            
    except requests.exceptions.Timeout:
        return {"success": False, "error": "External API timeout (30s)"}
    except requests.exceptions.ConnectionError as e:
        return {"success": False, "error": f"Connection error: {str(e)[:150]}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)[:150]}"}


# ==============================================
# FORMAT RESPONSE
# ==============================================

def format_response(external_data, username):
    if not external_data:
        return None
    
    profile = external_data.get("profile", {}) or {}
    
    return {
        "status": "success",
        "username": profile.get("username", username),
        "final_url": external_data.get("final_url", f"https://www.instagram.com/{username}/?hl=en"),
        
        "profile": {
            "id": profile.get("id"),
            "username": profile.get("username", username),
            "full_name": profile.get("full_name"),
            "biography": profile.get("biography"),
            "is_private": profile.get("is_private", False),
            "is_verified": profile.get("is_verified", False),
            "is_business_account": profile.get("is_business_account", False),
            "is_professional_account": profile.get("is_professional_account", False),
            "category_name": profile.get("category_name"),
            "business_category_name": profile.get("business_category_name"),
            "profile_pic_url": profile.get("profile_pic_url"),
            "profile_pic_url_hd": profile.get("profile_pic_url_hd"),
            "external_url": profile.get("external_url"),
            "followers": profile.get("followers", 0),
            "following": profile.get("following", 0),
            "posts": profile.get("posts", 0),
            "account_creation_year": profile.get("account_creation_year"),
            "has_highlights": profile.get("has_highlights", False),
            "is_joined_recently": profile.get("is_joined_recently", False),
        },
        
        "credit": {
            "username": "@KINGFFAIAK47x",
            "made_by": "ANSH AFT"
        }
    }


# ==============================================
# MAIN PROCESS
# ==============================================

def process_profile(username):
    is_valid, result = validate_username(username)
    if not is_valid:
        return jsonify({
            "status": "error",
            "error_code": "INVALID_USERNAME",
            "message": result,
            "credit": {"username": "@KINGFFAIAK47x", "made_by": "ANSH AFT"}
        }), 400
    
    username_clean = result
    
    start_time = time.time()
    api_result = fetch_from_external_api(username_clean)
    total_time = round((time.time() - start_time) * 1000, 2)
    
    if not api_result.get("success"):
        return jsonify({
            "status": "error",
            "error_code": "EXTERNAL_API_ERROR",
            "message": api_result.get("error", "Unknown error"),
            "username": username_clean,
            "credit": {"username": "@KINGFFAIAK47x", "made_by": "ANSH AFT"}
        }), 400
    
    formatted = format_response(api_result.get("data"), username_clean)
    
    if not formatted:
        return jsonify({
            "status": "error",
            "error_code": "FORMAT_ERROR",
            "message": "Failed to format response",
            "credit": {"username": "@KINGFFAIAK47x", "made_by": "ANSH AFT"}
        }), 500
    
    formatted["response_time"] = f"{total_time}ms"
    
    return jsonify(formatted), 200


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "service": "📱 Instagram Info API",
        "version": "1.0.0",
        "description": "Get Instagram profile details",
        "endpoints": {
            "/api/profile/key={api_key}/username={username}": {
                "method": "GET",
                "description": "Fetch Instagram profile info",
                "example": "/api/profile/key=your_api_key/username=instagram"
            }
        },
        "credit": {
            "username": "@KINGFFAIAK47x",
            "made_by": "ANSH AFT"
        }
    })


# ==============================================
# ROUTE 1: /api/profile/<username>/key=<key>
# ==============================================

@app.route('/api/profile/<username>/key=<key>', methods=['GET'])
@require_api_key
def get_profile_route1(username, key):
    """Format: /api/profile/instagram/key=your_api_key"""
    return process_profile(username)


# ==============================================
# ROUTE 2: /api/profile/key=<key>/username=<username>
# ==============================================

@app.route('/api/profile/key=<key>/username=<username>', methods=['GET'])
@require_api_key
def get_profile_route2(key, username):
    """Format: /api/profile/key=your_api_key/username=instagram"""
    return process_profile(username)


# ==============================================
# ROUTE 3: OLD FORMAT (backward compatible)
# ==============================================

@app.route('/profile/<username>', methods=['GET'])
def get_profile_old(username):
    """Old format: /profile/instagram?key=your_api_key"""
    api_key = request.args.get('key', '').strip()
    
    if not api_key:
        return jsonify({
            "status": "error",
            "error_code": "MISSING_API_KEY",
            "message": "API key required",
            "usage": "/api/profile/instagram/key=your_api_key",
            "credit": {"username": "@KINGFFAIAK47x", "made_by": "ANSH AFT"}
        }), 401
    
    if api_key not in VALID_KEYS:
        return jsonify({
            "status": "error",
            "error_code": "INVALID_API_KEY",
            "message": "Invalid API key",
            "credit": {"username": "@KINGFFAIAK47x", "made_by": "ANSH AFT"}
        }), 403
    
    return process_profile(username)


# ==============================================
# HEALTH
# ==============================================

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "credit": {"username": "@KINGFFAIAK47x", "made_by": "ANSH AFT"}
    })


# ==============================================
# ERROR HANDLERS
# ==============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "error_code": "NOT_FOUND",
        "message": "Endpoint not found",
        "usage": "/api/profile/instagram/key=your_api_key",
        "credit": {"username": "@KINGFFAIAK47x", "made_by": "ANSH AFT"}
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "status": "error",
        "error_code": "INTERNAL_ERROR",
        "message": "Internal server error",
        "credit": {"username": "@KINGFFAIAK47x", "made_by": "ANSH AFT"}
    }), 500


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "status": "error",
        "error_code": "METHOD_NOT_ALLOWED",
        "message": "Only GET requests are allowed",
        "credit": {"username": "@KINGFFAIAK47x", "made_by": "ANSH AFT"}
    }), 405


# ==============================================
# MAIN
# ==============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print("=" * 60)
    print("📱 INSTAGRAM INFO API v1.0.0")
    print("=" * 60)
    print(f"🚀 Running on: http://localhost:{port}")
    print(f"🌐 External API: {EXTERNAL_API_BASE}")
    print("\n🔑 Keys: ANSHPAPA, FF")
    print("\n📌 Endpoints:")
    print("  /api/profile/instagram/key=your_api_key")
    print("  /api/profile/key=your_api_key/username=instagram")
    print("  /profile/instagram?key=your_api_key (old)")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=False)
