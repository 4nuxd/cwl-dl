import requests
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
import time
import getpass
from .auth import CWLAuth
import yt_dlp

class CWLDownloader:
    BASE_URL = "https://labs.cyberwarfare.live"
    def __init__(self, jwt_token: str, output_dir: str = "downloads", user_info: Dict = None):
        self.jwt_token = jwt_token
        self.user_info = user_info
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        })
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    def get_user_progress(self) -> Optional[Dict]:
        try:
            response = self.session.get(f"{self.BASE_URL}/api/user/progress", timeout=10)
            response.raise_for_status()
            return response.json()
        except:
            return None
    def mask_email(self, email: str) -> str:
        if '@' not in email:
            return email
        local, domain = email.split('@')
        if len(local) <= 3:
            masked_local = local[0] + '*' * (len(local) - 1)
        else:
            masked_local = local[:2] + '*' * (len(local) - 4) + local[-2:]
        return f"{masked_local}@{domain}"
    def display_banner(self, clear=False):
        if clear:
            import os
            os.system('clear' if os.name == 'posix' else 'cls')
        print("\n")
        print("\033[1;36m     ██████╗██╗    ██╗██╗         ██████╗  ██████╗ ██╗    ██╗███╗   ██║")
        print("    ██╔════╝██║    ██║██║         ██║  ██║██╔═══██╗██║    ██║████╗  ██║")
        print("    ██║     ██║ █╗ ██║██║         ██║  ██║██║   ██║██║ █╗ ██║██╔██╗ ██║")
        print("    ██║     ██║███╗██║██║         ██║  ██║██║   ██║██║███╗██║██║╚██╗██║")
        print("    ╚██████╗╚███╔███╔╝███████╗    ██████╔╝╚██████╔╝╚███╔███╔╝██║ ╚████║")
        print("     ╚═════╝ ╚══╝╚══╝ ╚══════╝    ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═══╝\033[0m")
        print("\n\033[0;37m                                  CyberWarfare Labs - Course Downloader\033[0m")
        print("\033[0;90m                                                        -Made By @4nuxd\033[0m\n")
    def display_header(self, user_data=None, clear=False):
        if clear:
            import os
            os.system('clear' if os.name == 'posix' else 'cls')
        self.display_banner(clear=False)
        if user_data:
            username = user_data.get('username') or user_data.get('usename') or 'N/A'
            firstname = user_data.get('firstname', '')
            lastname = user_data.get('lastname', '')
            email = user_data.get('email', 'N/A')
            modules = user_data.get('modules_completed', 0)
            flags = user_data.get('flags_completed', 0)
            badges = user_data.get('badge', [])
            courses = len(user_data.get('enrolled_courses', []))
            full_name = f"{firstname} {lastname}".strip() if (firstname or lastname) else username
            print(f"\033[1;37m{full_name}\033[0m \033[0;90m(@{username}) • {self.mask_email(email)}\033[0m")
            print(f"\033[1;36m📚 {courses}\033[0m courses  \033[1;32m✅ {modules}\033[0m modules  \033[1;33m🚩 {flags}\033[0m flags  \033[1;35m🏆 {len(badges)}\033[0m certs")
            if badges:
                cert_names = []
                for badge in badges[:3]:
                    title = badge.get('badge_id', {}).get('title', 'Unknown')
                    title = title.replace('Certified', '').replace('Certificate', '').replace('Analyst', '').strip()
                    cert_names.append(title)
                cert_display = ', '.join(cert_names)
                if len(badges) > 3:
                    cert_display += f" \033[0;90m+{len(badges)-3} more\033[0m"
                print(f"\033[0;90m🎓 {cert_display}\033[0m")
            print()
    def refresh_display(self, update_stats=True):
        import os
        os.system('clear' if os.name == 'posix' else 'cls')
        self.display_header(clear=False)
        if update_stats:
            print("\n\033[0;90m[*] Updating profile stats...\033[0m")
            user_data = self.get_user_progress()
            os.system('clear' if os.name == 'posix' else 'cls')
            self.display_header(user_data, clear=False)
        import sys
        sys.stdout.flush()
    def get_all_courses(self, quiet=True) -> List[Dict]:
        if not quiet:
            print("\n[*] Fetching course list...")
        try:
            response = self.session.get(f"{self.BASE_URL}/api/user/mycoursename")
            response.raise_for_status()
            courses = response.json()
            if not quiet:
                print(f"[+] Found {len(courses)} courses")
            return courses
        except requests.RequestException as e:
            if not quiet:
                print(f"[!] Error fetching courses: {e}")
            return []
    def get_course_details(self, course_tag: str, quiet=True) -> Optional[Dict]:
        if not quiet:
            print(f"[*] Fetching details for course: {course_tag}")
        try:
            response = self.session.get(
                f"{self.BASE_URL}/api/user/course/name/{course_tag}"
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[!] Error fetching course {course_tag}: {e}")
            return None
    def get_course_intro(self, course_tag: str) -> Optional[Dict]:
        try:
            response = self.session.get(
                f"{self.BASE_URL}/api/user/course/intro/{course_tag}"
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[!] Error fetching course intro: {e}")
            return None
    def display_course_intro(self, course_tag: str):
        import textwrap
        intro_data = self.get_course_intro(course_tag)
        if not intro_data:
            return
        courses = self.get_all_courses(quiet=True)
        course_meta = next((c for c in courses if c.get('course_tag') == course_tag), {})
        print(f"\n\n\033[1;36m━━━ \033[1;33m{course_tag.upper()}\033[1;36m ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\n")
        if course_meta:
            tabs = ', '.join([t['name'] for t in course_meta.get('tabs', [])])
            comp = str(course_meta.get('onCompletion', 'N/A')).capitalize()
            tab_lines = textwrap.wrap(tabs, width=58)
            for idx, line in enumerate(tab_lines):
                prefix = "  Tabs: " if idx == 0 else "        "
                print(f"  \033[1;37m{prefix}\033[0m{line}")
            comp_lines = textwrap.wrap(comp, width=52)
            for idx, line in enumerate(comp_lines):
                prefix = "  Completion: " if idx == 0 else "              "
                print(f"  \033[1;37m{prefix}\033[0m{line}")
            print("\n")
        data_sections = intro_data.get("data", [])
        for section in data_sections:
            for item in section.get("data", []):
                item_type = item.get("type")
                content = item.get("content")
                if not content: continue
                if item_type == "heading":
                    text = str(content).strip().upper()
                    if "LAB ARCHITECTURE" in text or "CERTIFICATION PROCEDURE" in text:
                        continue
                    print(f"\n  \033[1;32m● {text}\033[0m")
                elif item_type == "paragraph":
                    text = str(content).strip()
                    lines = textwrap.wrap(text, width=64)
                    for l in lines:
                        print(f"    {l}")
                elif item_type == "list" and content:
                    for list_item in content:
                        item_text = str(list_item).strip()
                        lines = textwrap.wrap(item_text, width=62)
                        for idx, l in enumerate(lines):
                            bullet = "•" if idx == 0 else " "
                            print(f"      \033[0;90m{bullet}\033[0m {l}")
        print(f"\n\033[1;36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m")
    def download_pdf(self, course_tag: str, module_id: str, pdf_name: str) -> bool:
        url = f"{self.BASE_URL}/api/imgandpdf/pdf/{course_tag}/{module_id}/{pdf_name}"
        if self.user_info:
            import json
            import urllib.parse
            cookie_data = {
                "user_id": self.user_info.get('user_id', self.user_info.get('_id', '')),
                "usename": self.user_info.get('usename', self.user_info.get('username', '')),
                "email": self.user_info.get('email', ''),
                "user_image": self.user_info.get('user_image', ''),
                "token": self.jwt_token
            }
            user_json = json.dumps(cookie_data, separators=(',', ':'))
            user_cookie = urllib.parse.quote(user_json)
            self.session.cookies.set('user', user_cookie, domain='labs.cyberwarfare.live')
        pdf_headers = self.session.headers.copy()
        pdf_headers.update({
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
        })
        course_dir = self.output_dir / course_tag / "pdfs"
        course_dir.mkdir(parents=True, exist_ok=True)
        if not pdf_name.endswith("@piratexdumps.pdf"):
            base_name = pdf_name.rsplit('.', 1)[0] if '.' in pdf_name else pdf_name
            final_name = f"{base_name}@piratexdumps.pdf"
        else:
            final_name = pdf_name
        output_path = course_dir / final_name
        if output_path.exists():
            print(f"\033[0;90m  ⊘  {final_name} (already downloaded)\033[0m")
            return True
        print(f"\n\033[1;36m▶\033[0m  \033[1;37m{final_name}\033[0m")
        try:
            response = self.session.get(url, headers=pdf_headers, stream=True, timeout=30)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            start_time = time.time()
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=16384):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        downloaded_mb = downloaded / (1024 * 1024)
                        elapsed = time.time() - start_time
                        speed_mb = (downloaded / elapsed) / (1024 * 1024) if elapsed > 0 else 0
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        total_mb = total_size / (1024 * 1024)
                        speed_str = f"{speed_mb:.1f} MB/s" if speed_mb > 0 else "..."
                        eta_str = f"{int((total_mb - downloaded_mb) / speed_mb)}s" if speed_mb > 0 else "..."
                        bar_length = 30
                        filled = int(bar_length * percent / 100)
                        bar = '█' * filled + '░' * (bar_length - filled)
                        print(f"\r    \033[K[{bar}] {percent:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB) @ {speed_str} ETA: {eta_str}", end='', flush=True)
                    else:
                        print(f"\r    \033[KDownloaded: {downloaded_mb:.2f} MB @ {speed_mb:.1f} MB/s", end='', flush=True)
            print(f"\r    \033[K\033[1;32m✓\033[0m \033[0;90mDownloaded\033[0m\n")
            return True
        except requests.Timeout:
            print(f"[!] Download timed out: {final_name}")
            return False
        except requests.HTTPError as e:
            print(f"[!] HTTP Error {e.response.status_code}: {final_name}")
            if e.response.status_code == 401:
                print(f"    [!] Unauthorized - authentication failed")
            return False
        except requests.RequestException as e:
            print(f"[!] Error downloading {final_name}: {e}")
            return False
    def save_course_metadata(self, course_tag: str, data: Dict):
        course_dir = self.output_dir / course_tag
        course_dir.mkdir(parents=True, exist_ok=True)
        self.save_course_details_txt(course_tag)
    def save_course_details_txt(self, course_tag: str):
        intro_data = self.get_course_intro(course_tag)
        if not intro_data:
            return
        details_path = self.output_dir / course_tag / "course_details.txt"
        with open(details_path, 'w', encoding='utf-8') as f:
            f.write(f"COURSE: {course_tag.upper()}\n")
            f.write("=" * 60 + "\n\n")
            data_sections = intro_data.get("data", [])
            for section in data_sections:
                for item in section.get("data", []):
                    item_type = item.get("type")
                    content = item.get("content")
                    if not content: continue
                    if item_type == "heading":
                        f.write(f"\n{str(content).upper()}\n")
                        f.write("-" * len(str(content)) + "\n")
                    elif item_type == "paragraph":
                        import textwrap
                        wrapped = textwrap.fill(str(content), width=80)
                        f.write(f"\n{wrapped}\n")
                    elif item_type == "list":
                        for li in content:
                            f.write(f"  • {str(li)}\n")
        print(f"\033[0;90m  ✓ Saved course details: {details_path.name}\033[0m")
    def extract_pdfs_from_course(self, course_data: Dict) -> List[Dict]:
        pdfs = []
        for category in course_data.get("modules", []):
            for module in category.get("items", []):
                module_id = module.get("_id")
                for tab in module.get("tabs", []):
                    if tab.get("type") == "pdf":
                        pdfs.append({
                            "module_id": module_id,
                            "pdf_name": tab.get("source")
                        })
        return pdfs
    def get_study_material(self, source_id: str) -> Optional[Dict]:
        try:
            endpoints = [
                f"{self.BASE_URL}/api/studymaterial/{source_id}",
                f"{self.BASE_URL}/api/study-material/{source_id}",
                f"{self.BASE_URL}/api/material/{source_id}",
            ]
            for endpoint in endpoints:
                try:
                    response = self.session.get(endpoint)
                    if response.status_code == 200:
                        return response.json()
                except:
                    continue
            return None
        except Exception as e:
            print(f"[!] Error fetching study material {source_id}: {e}")
            return None
    def extract_videos_from_course(self, course_data: Dict) -> List[Dict]:
        videos = []
        study_materials = course_data if isinstance(course_data, list) else [course_data]
        for material in study_materials:
            for study_module in material.get("study_material_module", []):
                module_title = study_module.get("title", "Unknown Module")
                for resource in study_module.get("study_material_resource", []):
                    resource_title = resource.get("titile", resource.get("title", ""))
                    for video in resource.get("study_material_resources_videos", []):
                        video_type = video.get("type", "").lower()
                        video_title = video.get("title", resource_title)
                        if video_type == "vimeo":
                            video_data = video.get("data", {})
                            video_url = video_data.get("url", "")
                            if video_url:
                                videos.append({
                                    "module_title": module_title,
                                    "video_title": video_title,
                                    "video_url": video_url,
                                    "video_type": "vimeo"
                                })
                        elif video_type == "youtube":
                            video_data = video.get("data", {})
                            video_url = video_data.get("url", "")
                            if video_url:
                                videos.append({
                                    "module_title": module_title,
                                    "video_title": video_title,
                                    "video_url": video_url,
                                    "video_type": "youtube"
                                })
        return videos
    def download_video(self, course_tag: str, module_title: str, video_title: str, video_url: str, video_type: str) -> bool:
        safe_module_title = "".join(c for c in module_title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_module_title = safe_module_title.replace(' ', '_')
        video_dir = self.output_dir / course_tag / "videos" / safe_module_title
        video_dir.mkdir(parents=True, exist_ok=True)
        existing_files = list(video_dir.glob("*.*"))
        suffix = "@piratexdumps"
        final_video_title = f"{video_title}{suffix}"
        if existing_files:
            safe_video_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).strip()
            for existing_file in existing_files:
                if safe_video_title.lower() in existing_file.stem.lower():
                    print(f"\033[0;90m  ⊘  {final_video_title} (already downloaded)\033[0m")
                    return True
        print(f"\n\033[1;36m▶\033[0m  \033[1;37m{final_video_title}\033[0m")
        last_percent = [0]
        def progress_hook(d):
            if d['status'] == 'downloading':
                try:
                    p = 0
                    if 'total_bytes' in d:
                        p = (d['downloaded_bytes'] / d['total_bytes']) * 100
                        downloaded = f"{d['downloaded_bytes'] / (1024 * 1024):.1f}/{d['total_bytes'] / (1024 * 1024):.1f} MB"
                    elif 'total_bytes_estimate' in d:
                        p = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                        downloaded = f"{d['downloaded_bytes'] / (1024 * 1024):.1f} MB"
                    else:
                        downloaded = f"{d['downloaded_bytes'] / (1024 * 1024):.1f} MB"
                        p = 0
                    speed = d.get('speed', 0)
                    speed_str = f"{speed / (1024 * 1024):.1f} MB/s" if speed else "0.0 MB/s"
                    if int(p) >= last_percent[0] + 1 or p >= 99 or p == 0:
                        last_percent[0] = int(p)
                        bar_length = 30
                        filled = int(bar_length * p / 100) if p > 0 else 0
                        bar = '█' * filled + '░' * (bar_length - filled)
                        print(f"\r    \033[K[{bar}] {p:.1f}% ({downloaded}) @ {speed_str}", end='', flush=True)
                except:
                    pass
            elif d['status'] == 'finished':
                last_percent[0] = 0
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': str(video_dir / f'%(title)s{suffix}.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'noprogress': True,
            'progress_hooks': [progress_hook],
            'ignoreerrors': True,
            'no_check_certificate': True,
        }
        if video_type == "vimeo":
            headers = dict(self.session.headers)
            headers.update({
                "Referer": "https://labs.cyberwarfare.live/",
                "Origin": "https://labs.cyberwarfare.live"
            })
            ydl_opts['http_headers'] = headers
            ydl_opts['referer'] = "https://labs.cyberwarfare.live/"
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            print(f"\r    \033[K\033[1;32m✓\033[0m \033[0;90mProcessed\033[0m\n")
            return True
        except Exception as e:
            print(f"\n\033[1;31m✗ Error: {e}\033[0m")
            return False
    def get_study_materials(self, course_tag: str, module_id: str, studymaterial_id: str) -> Optional[List]:
        try:
            response = self.session.get(
                f"{self.BASE_URL}/api/user/course/{course_tag}/module/{module_id}/studymaterial/{studymaterial_id}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None
    def download_course(self, course_tag: str) -> Dict:
        print(f"\n\n\033[1;36m━━━ \033[1;33m{course_tag.upper()}\033[1;36m ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\n")
        stats = {"pdfs": 0, "videos": 0, "modules": 0}
        course_data = self.get_course_details(course_tag)
        if not course_data:
            return stats
        self.save_course_metadata(course_tag, course_data)
        pdfs = self.extract_pdfs_from_course(course_data)
        stats["pdfs"] = len(pdfs)
        if pdfs:
            print(f"\n\033[1;34m📄 Found {len(pdfs)} PDF(s) in course\033[0m\n")
            for pdf_info in pdfs:
                self.download_pdf(
                    course_tag,
                    pdf_info["module_id"],
                    pdf_info["pdf_name"]
                )
                time.sleep(0.5)
        else:
            print("\033[0;90m  ⊘  No PDFs found in this course\033[0m\n")
        print("\n\033[1;35m🎬 Checking for videos...\033[0m")
        all_videos = []
        seen_urls = set()
        module_count = 0
        for category in course_data.get("modules", []):
            for module in category.get("items", []):
                module_id = module.get("_id")
                has_video_tab = False
                for tab in module.get("tabs", []):
                    if tab.get("type") == "study-material-v2":
                        has_video_tab = True
                        study_material_id = tab.get("source")
                        if study_material_id:
                            study_materials = self.get_study_materials(course_tag, module_id, study_material_id)
                            if study_materials:
                                videos = self.extract_videos_from_course(study_materials)
                                unique_videos = []
                                for video in videos:
                                    if video["video_url"] not in seen_urls:
                                        seen_urls.add(video["video_url"])
                                        unique_videos.append(video)
                                all_videos.extend(unique_videos)
                if has_video_tab:
                    module_count += 1
        stats["modules"] = module_count
        if all_videos:
            print(f"\033[1;34m📹 Found {len(all_videos)} video(s)\033[0m\n")
            confirm = input("\033[1;36m>> Download videos? (y/n): \033[0m").strip().lower()
            if confirm == 'y':
                stats["videos"] = len(all_videos)
                for video_info in all_videos:
                    self.download_video(
                        course_tag,
                        video_info["module_title"],
                        video_info["video_title"],
                        video_info["video_url"],
                        video_info["video_type"]
                    )
                    time.sleep(1)
            else:
                print("\n\033[0;90m  ⊘  Skipping video downloads\033[0m")
        else:
            print("\033[0;90m  ⊘  No videos found in this course\033[0m\n")
        return stats
    def download_all_courses(self):
        courses = self.get_all_courses()
        if not courses:
            print("\n\033[1;31m✗ No courses found or error occurred\033[0m")
            return
        print(f"\n\033[1;36m━━━ \033[1;33mPROCESSING {len(courses)} COURSES\033[1;36m ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\n")
        for course in courses:
            course_tag = course.get("course_tag")
            if course_tag:
                self.download_course(course_tag)
                time.sleep(1)
        print(f"\n\n\033[1;32m✓ All courses processed successfully!\033[0m")
        print(f"\033[0;90m  Files saved to: {self.output_dir.absolute()}\033[0m\n")
    def generate_course_summary(self):
        courses = self.get_all_courses()
        summary_path = self.output_dir / "course_summary.txt"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("CyberWarfare Labs - Course Summary\n")
            f.write("="*60 + "\n\n")
            for course in courses:
                f.write(f"Course: {course.get('course_tag', 'Unknown')}\n")
                f.write(f"Icon: {course.get('course_icon', 'N/A')}\n")
                f.write(f"Completion: {course.get('onCompletion', 'N/A')}\n")
                f.write(f"Tabs: {', '.join([t['name'] for t in course.get('tabs', [])])}\n")
                f.write("-"*60 + "\n\n")
        print(f"[+] Course summary saved to: {summary_path}")

def display_menu():
    print("\n\033[1;36m━━━ \033[1;33mMENU\033[1;36m ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\n")
    print("  \033[1;37m1.\033[0m List all courses")
    print("  \033[1;37m2.\033[0m Download specific course")
    print("  \033[1;37m3.\033[0m Download all courses")
    print("  \033[1;37m4.\033[0m Logout")
    print("  \033[1;37m5.\033[0m Exit\n")

def list_courses(downloader):
    courses = downloader.get_all_courses(quiet=True)
    if not courses:
        print("\n\033[1;31m✗ No courses found\033[0m")
        return None
    print(f"\n\n\033[1;36m━━━ \033[1;33m📚 COURSES\033[1;36m ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\n")
    for idx, course in enumerate(courses, 1):
        course_tag = course.get('course_tag', 'Unknown').upper()
        print(f"  \033[1;36m{idx:2d}.\033[0m \033[1;37m{course_tag}\033[0m")
    print(f"\n\033[0;90m💡 Type a number (1-{len(courses)}) or 'b' to go back\033[0m")
    return courses

def main():
    import argparse
    parser = argparse.ArgumentParser(description='CWL Course Downloader')
    parser.add_argument('-o', '--output', default='downloads', help='Output directory')
    args = parser.parse_args()
    auth = CWLAuth()
    jwt_token = auth.get_token()
    if not jwt_token:
        print("\n[!] Authentication failed. Please try again.")
        return
    downloader = CWLDownloader(jwt_token, args.output, user_info=auth.user_info)
    downloader.refresh_display()
    while True:
        try:
            user_data = downloader.get_user_progress()
            downloader.display_header(user_data, clear=True)
            display_menu()
            choice = input("\n\033[1;36m>> \033[0m").strip()
            if choice in ['1', '2', '3']:
                downloader.display_header(user_data, clear=True)
            if choice == '1':
                courses = list_courses(downloader)
                if courses:
                    course_choice = input("\n\033[1;36m>> \033[0m").strip()
                    if course_choice.lower() != 'b' and course_choice.isdigit():
                        idx = int(course_choice) - 1
                        if 0 <= idx < len(courses):
                            selected = courses[idx]
                            course_tag = selected.get('course_tag')
                            downloader.display_header(user_data, clear=True)
                            print(f"\n\033[1;36m━━━ \033[1;33mSELECTED: {course_tag.upper()}\033[1;36m ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\n")
                            action = input("\033[1;36m>> \033[0m[\033[1;32mD\033[0m]ownload  [\033[1;36mV\033[0m]iew  [\033[1;31mB\033[0m]ack: ").strip().lower()
                            if action == 'd':
                                downloader.display_header(user_data, clear=True)
                                stats = downloader.download_course(course_tag)
                                if stats['pdfs'] > 0 or stats['videos'] > 0:
                                    print(f"\n\033[1;32m✓ Course '{course_tag.upper()}' download complete!\033[0m")
                                    print(f"\033[0;90m  📊 {stats['modules']} modules • {stats['pdfs']} PDFs • {stats['videos']} videos\033[0m")
                                else:
                                    print(f"\n\033[1;33m⚠ Download finished (no new content saved)\033[0m")
                                input("\n\033[0;90m⏎ Press ENTER to continue...\033[0m")
                            elif action == 'v':
                                downloader.display_course_intro(course_tag)
                                input("\n\033[0;90m⏎ Press ENTER to continue...\033[0m")
            elif choice == '2':
                courses = list_courses(downloader)
                if courses:
                    course_choice = input("\n\033[1;36m>> \033[0m").strip()
                    if course_choice.lower() != 'b' and course_choice.isdigit():
                        idx = int(course_choice) - 1
                        if 0 <= idx < len(courses):
                            selected = courses[idx]
                            course_tag = selected.get('course_tag')
                            downloader.display_header(user_data, clear=True)
                            stats = downloader.download_course(course_tag)
                            if stats['pdfs'] > 0 or stats['videos'] > 0:
                                print(f"\n\033[1;32m✓ Course '{course_tag.upper()}' download complete!\033[0m")
                                print(f"\033[0;90m  📊 {stats['modules']} modules • {stats['pdfs']} PDFs • {stats['videos']} videos\033[0m")
                            else:
                                print(f"\n\033[1;33m⚠ Download finished (no new content saved)\033[0m")
                            print("\n\033[0;90m⟳ Refreshing stats...\033[0m")
                            user_data = downloader.get_user_progress()
                            input("\n\033[0;90m⏎ Press ENTER to continue...\033[0m")
            elif choice == '3':
                print(f"\n\n\033[1;36m━━━ \033[1;33m📦 DOWNLOAD ALL\033[1;36m ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\n")
                print("  \033[1;31m⚠\033[0m  This will download PDFs and videos from \033[1;37mall enrolled courses\033[0m\n")
                confirm = input("\n>> Continue? (y/n): ").strip().lower()
                if confirm == 'y':
                    downloader.display_header(user_data, clear=True)
                    downloader.download_all_courses()
                    print(f"\n\033[1;32m✓ All courses processed successfully!\033[0m")
                    input("\n\033[0;90m⏎ Press ENTER to continue...\033[0m")
            elif choice == '4':
                print(f"\n\n\033[1;36m━━━ \033[1;33mLOGOUT\033[1;36m ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\n")
                print("  This will remove your saved authentication token.\n")
                confirm = input("\033[1;36m>> Continue? (y/n): \033[0m").strip().lower()
                if confirm == 'y':
                    auth.remove_saved_token()
                    print("\n\033[1;32m✓ Successfully logged out\033[0m")
                    break
                else:
                    print("\n\033[0;90m[~] Logout cancelled\033[0m")
            elif choice == '5':
                print("\n\033[1;36m👋 Goodbye!\033[0m\n")
                break
            else:
                if choice:
                    print(f"\n\033[1;31m✗ Invalid choice: {choice}. Please try again.\033[0m")
                input("⏎ Press ENTER to continue...")
        except KeyboardInterrupt:
            print("\n\n\033[1;33m⚠ Operation cancelled\033[0m")
            print("\033[1;36m👋 Goodbye!\033[0m\n")
            break
        except Exception as e:
            print(f"\n[!] Error: {e}")
            input("⏎ Press ENTER to continue...")
if __name__ == "__main__":
    main()
