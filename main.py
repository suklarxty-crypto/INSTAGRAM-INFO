# app.py - Instagram Info API (Render Ready)
from flask import Flask, jsonify, request
import instaloader
from instaloader import Instaloader, Profile
import time
import json
import random
import hashlib
import platform
import os
import re
import traceback
from datetime import datetime
from functools import wraps

app = Flask(__name__)

# ==============================================
# 📱 INSTAGRAM INFO API
# Made by @KINGFFAIAK47x · ANSH AFT
# ==============================================

# ONLY 2 KEYS
VALID_KEYS = {
    "ANSHPAPA": "full_access",
    "FF": "full_access"
}

# ==============================================
# AUTHENTICATION
# ==============================================

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.args.get('key', '').strip()
        
        if not api_key:
            return jsonify({
                "status": "error",
                "error_code": "MISSING_API_KEY",
                "message": "API key required",
                "usage": "/insta?user=username&key=your_api_key",
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
# DEVICE FINGERPRINT
# ==============================================

class UltimateDeviceFingerprint:
    def __init__(self):
        self.fingerprint = {}
        self.generation_count = 0
        self.rotation_counter = 0
        self.rotation_interval = 3
        self._generate_fingerprint()
    
    def _generate_fingerprint(self):
        self.generation_count += 1
        self.rotation_counter += 1
        system = platform.system()
        
        browsers = [
            {
                'name': 'Chrome',
                'version': f"{random.randint(110, 122)}.0.{random.randint(6000, 7000)}.{random.randint(0, 200)}",
                'user_agent': f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(110, 122)}.0.0.0 Safari/537.36"
            },
            {
                'name': 'Chrome',
                'version': f"{random.randint(110, 122)}.0.{random.randint(6000, 7000)}.{random.randint(0, 200)}",
                'user_agent': f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{random.randint(14, 15)}_{random.randint(0, 4)}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(110, 122)}.0.0.0 Safari/537.36"
            },
            {
                'name': 'Firefox',
                'version': f"{random.randint(115, 124)}.0",
                'user_agent': f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{random.randint(115, 124)}.0) Gecko/20100101 Firefox/{random.randint(115, 124)}.0"
            },
            {
                'name': 'Edge',
                'version': f"{random.randint(110, 122)}.0.{random.randint(2000, 3000)}.{random.randint(0, 200)}",
                'user_agent': f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(110, 122)}.0.0.0 Safari/537.36 Edg/{random.randint(110, 122)}.0.0.0"
            },
        ]
        
        browser = random.choice(browsers)
        screens = [(1920, 1080), (2560, 1440), (1366, 768), (1440, 900)]
        width, height = random.choice(screens)
        
        languages = ['en-US', 'en-GB', 'en-IN']
        timezones = ['Asia/Kolkata', 'America/New_York', 'Europe/London']
        
        self.fingerprint = {
            'browser': browser,
            'screen': {'width': width, 'height': height},
            'language': random.choice(languages),
            'timezone': random.choice(timezones),
            'platform': system,
            'fingerprint_id': hashlib.md5(str(time.time() + random.random()).encode()).hexdigest(),
            'generated_at': datetime.now().isoformat(),
        }
    
    def get_fingerprint(self):
        return self.fingerprint
    
    def rotate(self):
        self._generate_fingerprint()
        return self.fingerprint


# ==============================================
# INSTAGRAM SCANNER
# ==============================================

class InstagramScanner:
    def __init__(self):
        self.fingerprint = UltimateDeviceFingerprint()
        self.loader = None
    
    def initialize_loader(self):
        try:
            fp = self.fingerprint.get_fingerprint()
            user_agent = fp['browser']['user_agent']
            
            self.loader = Instaloader(
                max_connection_attempts=5,
                request_timeout=45,
                user_agent=user_agent,
                sleep=True,
                quiet=True
            )
            return True
        except Exception:
            return False
    
    def estimate_account_creation_year(self, user_id):
        id_ranges = [
            (1, 2010), (100000, 2011), (1000000, 2011), (10000000, 2012),
            (50000000, 2013), (100000000, 2014), (300000000, 2015),
            (500000000, 2016), (1000000000, 2017), (3000000000, 2018),
            (5000000000, 2019), (8000000000, 2020), (12000000000, 2021),
            (18000000000, 2022), (25000000000, 2023), (35000000000, 2024),
            (45000000000, 2025),
        ]
        
        try:
            uid = int(user_id)
        except:
            return None
        
        for max_id, year in id_ranges:
            if uid <= max_id:
                return year
        
        if uid > 45000000000:
            return 2025 + (uid - 45000000000) // 5000000000
        
        return None
    
    def scan_profile(self, username):
        start_time = time.time()
        
        # Validate username
        if not username:
            return {
                "status": "error",
                "error_code": "MISSING_USERNAME",
                "message": "Username required"
            }
        
        username = username.strip().lstrip('@')
        
        # Instagram username validation
        if not re.match(r'^[A-Za-z0-9._]{1,30}$', username):
            return {
                "status": "error",
                "error_code": "INVALID_USERNAME",
                "message": "Invalid Instagram username. Only letters, numbers, periods, underscores (1-30 chars)"
            }
        
        try:
            if not self.initialize_loader():
                return {
                    "status": "error",
                    "error_code": "LOADER_INIT_FAILED",
                    "message": "Failed to initialize Instagram loader"
                }
            
            profile = Profile.from_username(self.loader.context, username)
            response_time = (time.time() - start_time) * 1000
            
            estimated_year = self.estimate_account_creation_year(profile.userid)
            
            # Safe attribute extraction
            def safe_get(obj, attr, default=None):
                try:
                    val = getattr(obj, attr, default)
                    return val if val not in [None, '', 'None'] else default
                except:
                    return default
            
            # Business info
            is_business = safe_get(profile, 'is_business_account', False)
            is_professional = safe_get(profile, 'is_professional_account', False)
            category = safe_get(profile, 'category_name')
            business_category = safe_get(profile, 'business_category_name')
            
            # Highlights
            highlight_count = safe_get(profile, 'highlight_reel_count', 0) or 0
            has_highlights = safe_get(profile, 'has_highlight_reels', False) or (highlight_count > 0)
            
            # IGTV
            igtv_count = safe_get(profile, 'igtv_count', 0) or 0
            
            # Recently joined
            is_joined_recently = safe_get(profile, 'is_joined_recently', False)
            
            # Bio links
            bio_links = []
            try:
                if hasattr(profile, 'biography_links'):
                    for link in profile.biography_links:
                        if isinstance(link, dict) and 'url' in link:
                            bio_links.append(link['url'])
                        elif isinstance(link, str):
                            bio_links.append(link)
            except:
                bio_links = []
            
            return {
                "status": "success",
                "collected_at": datetime.now().isoformat(),
                "response_time": f"{round(response_time, 2)}ms",
                "data": {
                    "id": str(profile.userid),
                    "username": profile.username,
                    "full_name": safe_get(profile, 'full_name', 'N/A'),
                    "biography": (safe_get(profile, 'biography', '') or '')[:200] or 'No bio available',
                    "is_private": safe_get(profile, 'is_private', False),
                    "is_verified": safe_get(profile, 'is_verified', False),
                    "is_business_account": is_business,
                    "is_professional_account": is_professional,
                    "category_name": category,
                    "business_category_name": business_category,
                    "profile_pic_url_hd": safe_get(profile, 'profile_pic_url_hd') or safe_get(profile, 'profile_pic_url'),
                    "external_url": safe_get(profile, 'external_url'),
                    "followers": safe_get(profile, 'followers', 0),
                    "following": safe_get(profile, 'followees', 0),
                    "posts": safe_get(profile, 'mediacount', 0),
                    "igtv_count": igtv_count,
                    "highlight_count": highlight_count,
                    "has_highlights": has_highlights,
                    "account_creation_year": estimated_year,
                    "is_joined_recently": is_joined_recently,
                    "bio_links": bio_links
                },
                "credit": {
                    "username": "@KINGFFAIAK47x",
                    "made_by": "ANSH AFT"
                }
            }
            
        except instaloader.exceptions.ProfileNotExistsException:
            return {
                "status": "error",
                "error_code": "PROFILE_NOT_FOUND",
                "message": f"Profile @{username} does not exist"
            }
        except instaloader.exceptions.PrivateProfileNotFollowedException:
            return {
                "status": "error",
                "error_code": "PRIVATE_PROFILE",
                "message": f"Profile @{username} is private"
            }
        except instaloader.exceptions.LoginRequiredException:
            return {
                "status": "error",
                "error_code": "LOGIN_REQUIRED",
                "message": "Instagram requires login. Try again later or use different profile."
            }
        except instaloader.exceptions.TooManyRequestsException:
            return {
                "status": "error",
                "error_code": "RATE_LIMITED",
                "message": "Instagram rate limit reached. Try again in a few minutes."
            }
        except instaloader.exceptions.ConnectionException as e:
            return {
                "status": "error",
                "error_code": "CONNECTION_ERROR",
                "message": f"Instagram connection error: {str(e)[:150]}"
            }
        except Exception as e:
            error_str = str(e)
            # Check for 401
            if "401" in error_str:
                time.sleep(2)
                # Retry once
                try:
                    self.fingerprint.rotate()
                    profile = Profile.from_username(self.loader.context, username)
                    return {
                        "status": "error",
                        "error_code": "RETRY_FAILED",
                        "message": "Session expired. Please try again."
                    }
                except:
                    return {
                        "status": "error",
                        "error_code": "AUTH_ERROR",
                        "message": "Instagram authentication failed. Try again later."
                    }
            
            return {
                "status": "error",
                "error_code": "UNKNOWN_ERROR",
                "message": error_str[:200]
            }


# Global scanner instance
scanner = InstagramScanner()


# ==============================================
# ENDPOINTS
# ==============================================

@app.route('/', methods=['GET'])
def home():
    """API Info"""
    return jsonify({
        "service": "📱 Instagram Info API",
        "version": "1.0.0",
        "description": "Get Instagram profile information",
        "endpoint": {
            "/insta": {
                "method": "GET",
                "description": "Get Instagram profile details",
                "example": "/insta?user=username&key=your_api_key"
            }
        },
        "credit": {
            "username": "@KINGFFAIAK47x",
            "made_by": "ANSH AFT"
        }
    })


@app.route('/insta', methods=['GET'])
@require_api_key
def get_insta_info():
    """
    Get Instagram profile info
    Example: /insta?user=cristiano&key=ANSHPAPA
    """
    username = request.args.get('user', '').strip()
    
    if not username:
        return jsonify({
            "status": "error",
            "error_code": "MISSING_USERNAME",
            "message": "Instagram username required",
            "usage": "/insta?user=username&key=your_api_key",
            "credit": {"username": "@KINGFFAIAK47x", "made_by": "ANSH AFT"}
        }), 400
    
    start_time = time.time()
    result = scanner.scan_profile(username)
    response_time = round((time.time() - start_time) * 1000, 2)
    
    result["response_time"] = f"{response_time}ms"
    result["credit"] = {
        "username": "@KINGFFAIAK47x",
        "made_by": "ANSH AFT"
    }
    
    if result.get('status') == 'success':
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "message": "Endpoint not found. Use /insta",
        "credit": {"username": "@KINGFFAIAK47x", "made_by": "ANSH AFT"}
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "status": "error",
        "message": "Internal server error",
        "credit": {"username": "@KINGFFAIAK47x", "made_by": "ANSH AFT"}
    }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print("=" * 50)
    print("📱 INSTAGRAM INFO API")
    print("=" * 50)
    print(f"🚀 Running on: http://localhost:{port}")
    print("\n🔑 Key: ANSHPAPA")
    print("\n📌 ENDPOINT:")
    print("  GET /insta?user=cristiano&key=ANSHPAPA")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=port, debug=False)
