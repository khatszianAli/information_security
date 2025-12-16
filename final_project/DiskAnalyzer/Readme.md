# DiskAnalyzer

DiskAnalyzer is a Python tool that scans directories, calculates folder sizes, and generates detailed disk usage reports.  
It can export reports as text and can optionally email the report automatically written by Ali Khantszian(ka12438) for the final project of course Information Security.
<img src="https://github.com/khatszianAli/information_security/blob/main/final_project/DiskAnalyzer/ezgif.com-video-to-gif-converter.gif" width="700">
---

## Features

- Recursively scans folders and subfolders
- Calculates total directory sizes
- Generates text reports
- Optional JSON export
- Email report support
- Handles permission errors safely
- Works on macOS, Linux, and Unix-like systems

---

## Installation

Clone the repository:

```bash
git clone https://github.com/khatszianAli/information_security.git
cd information_security/final_project/DiskAnalyzer
```
Make the script executable (optional):
```bash
chmod +x DiskAnalyzer.py
```
Check your Python version:
```bash
python3 --version
```
Usage
Basic command:
```bash
python3 DiskAnalyzer.py --root /path/to/directory --out report.txt --json
```
macOS example:
```bash
python3 DiskAnalyzer.py --root /Users/yourusername --out ~/disk_reports/disk_report_$(date +%F).txt --json
```

Email Reports
To enable sending reports by email, set these environment variables:
```bash
crontab -e
```
```bash
export EMAIL_USER="your_email@gmail.com"
export EMAIL_PASS="your_app_password"
export EMAIL_TO="receiver@email.com"
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
```
Run with email enabled:
```bash
python3 DiskAnalyzer.py --root /Users/yourusername --out report.txt --json --mail
```
Automate with cron (daily run)
Example cron job (runs every day at 21:00):
```bash
00 21 * * * /opt/homebrew/bin/python3 /path/to/DiskAnalyzer.py \
--root /Users/yourusername \
--out /Users/yourusername/disk_reports/disk_report_$(date +\%F).txt \
--json --mail >> /Users/yourusername/disk_reports/disk_analyzer.log 2>&1
```
Make sure the reports directory exists:
```bash
mkdir -p ~/disk_reports
```
Author
Developed by Ali Khantszian
