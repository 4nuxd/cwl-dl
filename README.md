# CWL Downloader 🚀

```text
     ██████╗██╗    ██╗██╗         ██████╗  ██████╗ ██╗    ██╗███╗   ██║
    ██╔════╝██║    ██║██║         ██║  ██║██╔═══██╗██║    ██║████╗  ██║
    ██║     ██║ █╗ ██║██║         ██║  ██║██║   ██║██║ █╗ ██║██╔██╗ ██║
    ██║     ██║███╗██║██║         ██║  ██║██║   ██║██║███╗██║██║╚██╗██║
    ╚██████╗╚███╔███╔╝███████╗    ██████╔╝╚██████╔╝╚███╔███╔╝██║ ╚████║
     ╚═════╝ ╚══╝╚══╝ ╚══════╝    ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═══╝
```

An automated, modern, and minimal course material downloader for **CyberWarfare Labs**.

## ✨ Features

- 🖥️ **Interactive UI**: Beautiful terminal interface with ASCII art and clean status updates.
- 📄 **PDF Downloads**: Automatically extracts and saves course write-ups and study materials.
- 🎬 **Video Support**: Full support for downloading **Vimeo** and **YouTube** videos.
- 🔄 **Deduplication**: Intelligent URL tracking to prevent duplicate downloads.
- 📊 **User Stats**: Displays your profile progress (modules, certs, flags) on login.
- 🛡️ **Bypass Restrictions**: Handles "embed-only" Vimeo videos via custom headers and referrers.
- 📁 **Organized Storage**: Automatically categorizes files by Course and Module.

Ensure you have Python 3.10+ installed and the following dependencies:

```bash
pip install -r requirements.txt
```

### 📦 System Dependencies (Required)

`ffmpeg` is required for merging high-quality video and audio streams. If you don't have it, install it using:

- **Linux (Parrot/Ubuntu/Debian)**: `sudo apt update && sudo apt install ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add the `bin` folder to your System PATH.

## 🚀 Getting Started

1. **Clone the repository**:
   ```bash
   git clone https://github.com/g4rxd/CWL-DL.git
   cd CWL-DL
   ```

2. **Run the script**:
   ```bash
   python3 cwl_downloader.py
   ```

3. **Login**:
   The script will prompt for your **JWT Token**.
   - Login to [labs.cyberwarfare.live](https://labs.cyberwarfare.live)
   - Open DevTools (F12) -> Application -> Cookies
   - Copy the value of the `token` field from the `user` cookie string.

## 📁 Output Structure

Downloaded materials are organized as follows:

```text
downloads/
├── course_summary.txt
└── CRTA/
    ├── course_details.txt
    ├── pdfs/
    │   └── CRTA_Walkthrough@piratexdumps.pdf
    └── videos/
        └── Module_1_Initial_Access/
            └── Introduction@piratexdumps.mp4
```

## ⚖️ Legal Disclaimer

This tool is for **personal educational use only**.
- Do not redistribute downloaded content.
- Respect the CyberWarfare Labs Terms of Service.
- The author is not responsible for any misuse of this tool.

---
**Made with ❤️ by [@4nuxd](https://github.com/4nuxd)**
