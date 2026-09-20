# main.py - Instagram Info API (With Proxy Rotation)
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
# 📱 INSTAGRAM INFO API (PROXY ROTATION)
# Made by @KINGFFAIAK47x · ANSH AFT
# ==============================================

# ONLY 2 KEYS
VALID_KEYS = {
    "ANSHPAPA": "full_access",
    "FF": "full_access"
}

# ==============================================
# AUTHENTICATION - YE ZAROORI HAI
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
# PROXY LIST
# ==============================================

PROXIES = [
    "31.59.20.176:6754:bbpsdjvy:229lu1zbkyws",
    "45.38.107.97:6014:bbpsdjvy:229lu1zbkyws",
    "198.105.121.200:6462:bbpsdjvy:229lu1zbkyws",
    "64.137.96.74:6641:bbpsdjvy:229lu1zbkyws",
    "198.23.243.226:6361:bbpsdjvy:229lu1zbkyws",
    "38.154.185.97:6370:bbpsdjvy:229lu1zbkyws",
    "84.247.60.125:6095:bbpsdjvy:229lu1zbkyws",
    "142.111.67.146:5611:bbpsdjvy:229lu1zbkyws",
    "191.96.254.138:6185:bbpsdjvy:229lu1zbkyws",
    "31.58.9.4:6077:bbpsdjvy:229lu1zbkyws"
]


def parse_proxy(proxy_str):
    """Proxy string ko dict mein convert karta hai"""
    try:
        parts = proxy_str.split(':')
        if len(parts) == 4:
            ip, port, user, password = parts
            proxy_url = f"http://{user}:{password}@{ip}:{port}"
            return {
                "http": proxy_url,
                "https": proxy_url
            }
    except:
        pass
    return None


def get_random_proxy():
    """Random proxy return karta hai"""
    if not PROXIES:
        return None
    return parse_proxy(random.choice(PROXIES))


def get_all_proxies():
    """Saare proxies return karta hai (parsed)"""
    result = []
    for p in PROXIES:
        parsed = parse_proxy(p)
        if parsed:
            result.append(parsed)
    return result


def get_headers():
    """Random headers return karta hai"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }


# ==============================================
# DEVICE FINGERPRINT
# ==============================================

class UltimateDeviceFingerprint:
    def __init__(self):
        self.fingerprint = {}
        self.generation_count = 0
        self._generate_fingerprint()
    
    def _generate_fingerprint(self):
        self.generation_count += 1
        system = platform.system()
        
        browsers = [
            {
                'name': 'Chrome',
                'version': f"{random.randint(110, 122)}.0.{random.randint(6000, 7000)}.{random.randint(0, 200)}",
                'user_agent': f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(110, 122)}.0.0.0 Safari/537.36"
            },
            {
                'name': 'Firefox',
                'version': f"{random.randint(115, 124)}.0",
                'user_agent': f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{random.randint(115, 124)}.0) Gecko/20100101 Firefox/{random.randint(115, 124)}.0"
            },
        ]
        
        browser = random.choice(browsers)
        
        self.fingerprint = {
            'browser': browser,
            'platform': system,
            'fingerprint_id': hashlib.md5(str(time.time() + random.random()).encode()).hexdigest(),
        }
    
    def get_fingerprint(self):
        return self.fingerprint
    
    def rotate(self):
        self._generate_fingerprint()
        return self.fingerprint


# ==============================================
# INSTAGRAM SCANNER WITH PROXY
# ==============================================

class InstagramScanner:
    def __init__(self):
        self.fingerprint = UltimateDeviceFingerprint()
        self.loader = None
        self.current_proxy = None
    
    def initialize_loader(self, proxy_dict=None):
        try:
            fp = self.fingerprint.get_fingerprint()
            user_agent = fp['browser']['user_agent']
            
            self.loader = Instaloader(
                max_connection_attempts=3,
                request_timeout=45,
                user_agent=user_agent,
                sleep=True,
                quiet=True
            )
            
            if proxy_dict and hasattr(self.loader, 'context'):
                try:
                    if hasattr(self.loader.context, '_session'):
                        self.loader.context._session.proxies.update(proxy_dict)
                        self.current_proxy = proxy_dict
                except:
                    pass
            
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
    
    def _extract_profile_data(self, profile, start_time, proxy_used):
        response_time = (time.time() - start_time) * 1000
        estimated_year = self.estimate_account_creation_year(profile.userid)
        
        def safe_get(obj, attr, default=None):
            try:
                val = getattr(obj, attr, default)
                return val if val not in [None, '', 'None'] else default
            except:
                return default
        
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
            "proxy_used": "Yes" if proxy_used else "No",
            "data": {
                "id": str(profile.userid),
                "username": profile.username,
                "full_name": safe_get(profile, 'full_name', 'N/A'),
                "biography": (safe_get(profile, 'biography', '') or '')[:200] or 'No bio available',
                "is_private": safe_get(profile, 'is_private', False),
                "is_verified": safe_get(profile, 'is_verified', False),
                "is_business_account": safe_get(profile, 'is_business_account', False),
                "is_professional_account": safe_get(profile, 'is_professional_account', False),
                "category_name": safe_get(profile, 'category_name'),
                "business_category_name": safe_get(profile, 'business_category_name'),
                "profile_pic_url_hd": safe_get(profile, 'profile_pic_url_hd') or safe_get(profile, 'profile_pic_url'),
                "external_url": safe_get(profile, 'external_url'),
                "followers": safe_get(profile, 'followers', 0),
                "following": safe_get(profile, 'followees', 0),
                "posts": safe_get(profile, 'mediacount', 0),
                "igtv_count": safe_get(profile, 'igtv_count', 0) or 0,
                "highlight_count": safe_get(profile, 'highlight_reel_count', 0) or 0,
                "has_highlights": safe_get(profile, 'has_highlight_reels', False),
                "account_creation_year": estimated_year,
                "is_joined_recently": safe_get(profile, 'is_joined_recently', False),
                "bio_links": bio_links
            },
            "credit": {
                "username": "@KINGFFAIAK47x",
                "made_by": "ANSH AFT"
            }
        }
    
    def scan_profile_with_proxy(self, username, proxy_dict=None):
        start_time = time.time()
        
        try:
            if not self.initialize_loader(proxy_dict):
                return None
            
            profile = Profile.from_username(self.loader.context, username)
            return self._extract_profile_data(profile, start_time, proxy_dict is not None)
        except Exception as e:
            return {"_error": str(e), "_exception": e}
    
    def scan_profile(self, username):
        start_time = time.time()
        
        if not username:
            return {
                "status": "error",
                "error_code": "MISSING_USERNAME",
                "message": "Username required"
            }
        
        username = username.strip().lstrip('@')
        
        if not re.match(r'^[A-Za-z0-9._]{1,30}$', username):
            return {
                "status": "error",
                "error_code": "INVALID_USERNAME",
                "message": "Invalid Instagram username"
            }
        
        all_proxies = get_all_proxies()
        random.shuffle(all_proxies)
        proxy_attempts = [None] + all_proxies[:5]
        
        last_error = None
        errors_log = []
        
        for i, proxy_dict in enumerate(proxy_attempts):
            try:
                result = self.scan_profile_with_proxy(username, proxy_dict)
                
                if result and "status" in result and result.get("status") == "success":
                    return result
                
                if result and "_error" in result:
                    errors_log.append({
                        "attempt": i + 1,
                        "proxy": "direct" if proxy_dict is None else "proxy",
                        "error": result["_error"][:100]
                    })
                    last_error = result["_exception"]
                    continue
                
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
                    "message": "Instagram requires login"
                }
            except Exception as e:
                errors_log.append({
                    "attempt": i + 1,
                    "error": str(e)[:100]
                })
                last_error = e
                continue
        
        return {
            "status": "error",
            "error_code": "ALL_ATTEMPTS_FAILED",
            "message": "All proxies failed. Instagram may be blocking requests.",
            "details": errors_log[-3:] if errors_log else [],
            "total_attempts": len(proxy_attempts)
        }


# Global scanner
scanner = InstagramScanner()


# ==============================================
# ENDPOINTS
# ==============================================

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "service": "📱 Instagram Info API (Proxy Rotation)",
        "version": "1.0.0",
        "endpoints": {
            "/insta": {
                "method": "GET",
                "description": "Get Instagram profile details",
                "example": "/insta?user=username&key=your_api_key"
            },
            "/proxy-test": {
                "method": "GET",
                "description": "Test all proxies",
                "example": "/proxy-test?key=your_api_key"
            }
        },
        "proxy_count": len(PROXIES),
        "credit": {
            "username": "@KINGFFAIAK47x",
            "made_by": "ANSH AFT"
        }
    })


@app.route('/insta', methods=['GET'])
@require_api_key
def get_insta_info():
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


@app.route('/proxy-test', methods=['GET'])
@require_api_key
def proxy_test():
    results = []
    working = 0
    test_url = "https://www.instagram.com/"
    
    for proxy_str in PROXIES[:10]:
        proxy_dict = parse_proxy(proxy_str)
        if not proxy_dict:
            continue
        
        try:
            import requests
            start = time.time()
            r = requests.get(
                test_url,
                proxies=proxy_dict,
                headers=get_headers(),
                timeout=10
            )
            elapsed = round((time.time() - start) * 1000, 2)
            
            results.append({
                "proxy": proxy_str.split(':')[0] + ':' + proxy_str.split(':')[1],
                "status": "working" if r.status_code == 200 else "failed",
                "status_code": r.status_code,
                "response_time": f"{elapsed}ms"
            })
            
            if r.status_code == 200:
                working += 1
        except Exception as e:
            results.append({
                "proxy": proxy_str.split(':')[0] + ':' + proxy_str.split(':')[1],
                "status": "failed",
                "error": str(e)[:100]
            })
    
    return jsonify({
        "status": "success",
        "total_proxies": len(PROXIES),
        "tested": len(results),
        "working": working,
        "results": results,
        "credit": {
            "username": "@KINGFFAIAK47x",
            "made_by": "ANSH AFT"
        }
    })


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "proxies_loaded": len(PROXIES)
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
    
    print("=" * 60)
    print("📱 INSTAGRAM INFO API (PROXY ROTATION)")
    print("=" * 60)
    print(f"🚀 Running on: http://localhost:{port}")
    print(f"🌐 Proxies loaded: {len(PROXIES)}")
    print("\n🔑 Key: ANSHPAPA")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=False)
