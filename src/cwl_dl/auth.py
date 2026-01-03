import requests
import json
import os
from pathlib import Path
from typing import Optional, Dict
import urllib.parse

class CWLAuth:
    BASE_URL = "https://labs.cyberwarfare.live"
    TOKEN_FILE = Path.home() / ".cwl_token"
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-GB,en;q=0.9",
            "Origin": self.BASE_URL,
            "Referer": f"{self.BASE_URL}/login"
        })
        self.jwt_token = None
        self.user_info = None
    def login_with_credentials(self, email: str, password: str) -> bool:
        login_url = f"{self.BASE_URL}/api/access/passwordlogin"
        payload = {
            "email": email,
            "password": password
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-GB,en;q=0.9",
            "Origin": self.BASE_URL,
            "Referer": f"{self.BASE_URL}/login",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty"
        }
        try:
            response = self.session.post(
                login_url,
                json=payload,
                headers=headers,
                timeout=60                                     
            )
            if response.status_code == 200:
                data = response.json()
                token = data.get('token')
                if token:
                    self.jwt_token = token
                    self.user_info = data
                    print(f"[+] Login successful! (User: {data.get('usename', 'N/A')})")
                    self.save_token()
                    return True
                else:
                    print("[!] Login response received but no token found")
                    print(f"[!] Response: {json.dumps(data, indent=2)}")
                    return False
            elif response.status_code == 401:
                print("[!] Login failed: Invalid credentials")
                try:
                    error_data = response.json()
                    print(f"[!] Error: {error_data}")
                except:
                    pass
                return False
            elif response.status_code == 429:
                print("[!] Rate limit exceeded. Please wait before trying again.")
                if 'X-Ratelimit-Reset' in response.headers:
                    reset_time = response.headers['X-Ratelimit-Reset']
                    print(f"[!] Rate limit resets at: {reset_time}")
                return False
            else:
                print(f"[!] Login failed with status: {response.status_code}")
                print(f"[!] Response: {response.text}")
                return False
        except requests.Timeout:
            print("[!] Request timeout. Please check your connection.")
            return False
        except requests.RequestException as e:
            print(f"[!] Request error: {e}")
            return False
        except json.JSONDecodeError:
            print("[!] Invalid JSON response")
            print(f"[!] Response text: {response.text}")
            return False
    def extract_token_from_cookie(self) -> Optional[str]:
        print("[*] Checking for existing session cookie...")
        for cookie in self.session.cookies:
            if cookie.name == 'user':
                try:
                    decoded = urllib.parse.unquote(cookie.value)
                    user_data = json.loads(decoded)
                    token = user_data.get('token')
                    if token:
                        self.jwt_token = token
                        self.user_info = user_data
                        print("[+] Token extracted from cookie")
                        return token
                except Exception as e:
                    print(f"[!] Error parsing cookie: {e}")
        return None
    def save_token(self):
        if self.jwt_token:
            try:
                token_data = {
                    "token": self.jwt_token,
                    "user_info": self.user_info
                }
                with open(self.TOKEN_FILE, 'w') as f:
                    json.dump(token_data, f, indent=2)
                os.chmod(self.TOKEN_FILE, 0o600)
            except Exception as e:
                print(f"[!] Error saving token: {e}")
    def load_token(self) -> bool:
        if self.TOKEN_FILE.exists():
            try:
                with open(self.TOKEN_FILE, 'r') as f:
                    data = json.load(f)
                self.jwt_token = data.get('token')
                self.user_info = data.get('user_info')
                if self.jwt_token:
                    return True
            except Exception as e:
                print(f"[!] Error loading token: {e}")
        return False
    def verify_token(self) -> bool:
        if not self.jwt_token:
            return False
        try:
            response = self.session.get(
                f"{self.BASE_URL}/api/user/mycoursename",
                headers={"Authorization": f"Bearer {self.jwt_token}"},
                timeout=30                          
            )
            return response.status_code == 200
        except:
            return False
    def get_token(self) -> Optional[str]:
        if self.load_token() and self.verify_token():
            return self.jwt_token
        env_token = os.environ.get('CWL_JWT_TOKEN')
        if env_token:
            self.jwt_token = env_token
            if self.verify_token():
                self.save_token()
                return self.jwt_token
        try:
            email = input("Email: ").strip()
            if not email:
                print("[!] Email is required")
                return None
            import getpass
            password = getpass.getpass("Password: ")
            if not password:
                print("[!] Password is required")
                return None
            if self.login_with_credentials(email, password):
                return self.jwt_token
            else:
                print("\n[!] Login failed. Please check your credentials and try again.")
                return None
        except KeyboardInterrupt:
            print("\n[!] Login cancelled by user")
            return None
        except Exception as e:
            print(f"\n[!] Error during login: {e}")
            return None
    def logout(self):
        if self.TOKEN_FILE.exists():
            self.TOKEN_FILE.unlink()
            print("[+] Token removed")
        self.jwt_token = None
        self.user_info = None

def main():
    auth = CWLAuth()
    token = auth.get_token()
    if token:
        print(f"\n[+] Authentication successful!")
        print(f"[+] Token: {token[:20]}...")
        if auth.user_info:
            print(f"[+] User: {auth.user_info.get('username', 'N/A')}")
            print(f"[+] Email: {auth.user_info.get('email', 'N/A')}")
    else:
        print("\n[!] Authentication failed")
if __name__ == "__main__":
    main()
