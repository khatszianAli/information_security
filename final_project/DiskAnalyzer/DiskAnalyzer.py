
import os
import sys
import argparse
import json
import time
import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Dict



def format_size(num_bytes: int) -> str:
    """Format bytes into human-readable form."""
    for unit in ['B','KB','MB','GB','TB','PB']:
        if num_bytes < 1024:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.2f} EB"

def dir_size_map(root_path: Path, follow_symlinks: bool = False) -> Dict[str,int]:
    sizes = {}
    root_path = Path(root_path).resolve()

    if not root_path.exists():
        raise FileNotFoundError(f"Root path does not exist: {root_path}")

    for dirpath, dirnames, filenames in os.walk(root_path, followlinks=follow_symlinks):
        dirp = Path(dirpath).resolve()
        sizes.setdefault(str(dirp), 0)

        for fname in filenames:
            fpath = dirp / fname
            try:
                stat = os.stat(fpath, follow_symlinks=follow_symlinks)
                fsize = stat.st_size
            except (FileNotFoundError, PermissionError, OSError):
                continue


            cur = dirp
            while True:
                sizes.setdefault(str(cur), 0)
                sizes[str(cur)] += fsize
                if cur == root_path or cur.parent == cur:
                    break
                cur = cur.parent

    return sizes

def make_text_report(sizes: Dict[str,int], top_n: int = 20, root: str = None) -> str:
    items = sorted(sizes.items(), key=lambda kv: kv[1], reverse=True)
    total = sizes.get(root, sum(v for k,v in sizes.items() if root and k.startswith(root))) if root else sum(sizes.values())

    lines = [
        f"Disk Analyzer Report",
        f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    ]
    if root:
        lines.append(f"Root scanned: {root}")
    lines.append(f"Total size under root: {format_size(total)}\n")
    lines.append(f"Top {top_n} largest directories:")
    lines.append("-" * 60)
    for i, (path, b) in enumerate(items[:top_n], 1):
        lines.append(f"{i:2d}. {format_size(b):>10}  {path}")
    lines.append("\nNotes:")
    lines.append("- Sizes are recursive (include subdirectories).")
    lines.append("- Some files/dirs may be skipped if permission denied.")
    return "\n".join(lines)

def send_email(smtp_server: str, smtp_port: int, user: str, password: str,
               sender: str, recipient: str, subject: str, body: str, attachment_path: str = None):
    msg = EmailMessage()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.set_content(body)

    if attachment_path:
        p = Path(attachment_path)
        if p.exists():
            with p.open('rb') as f:
                data = f.read()
            msg.add_attachment(data, maintype='text', subtype='plain', filename=p.name)

    server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
    try:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
    finally:
        server.quit()


def main():
    parser = argparse.ArgumentParser(description="Disk Analyzer: daily directory size report + email")
    parser.add_argument('--root', '-r', default='/', help="Root directory to scan")
    parser.add_argument('--out', '-o', default=None, help="Path to write text report")
    parser.add_argument('--json', action='store_true', help="Also write JSON file with raw sizes")
    parser.add_argument('--top', type=int, default=30, help="Top N largest directories to display")
    parser.add_argument('--follow-symlinks', action='store_true', help="Follow symbolic links")
    parser.add_argument('--mail', action='store_true', help="Send report by email (requires env vars)")
    parser.add_argument('--no-root-total', action='store_true', help="Skip computing root total")
    args = parser.parse_args()

    root_path = Path(args.root)
    if not root_path.exists():
        print("ERROR: root path does not exist:", args.root, file=sys.stderr)
        sys.exit(2)

    date_str = time.strftime("%Y-%m-%d")
    out_path = Path(args.out) if args.out else Path(f"disk_report_{date_str}.txt")
    out_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

    print("Scanning:", root_path)
    sizes = dir_size_map(root_path, follow_symlinks=args.follow_symlinks)

    report_text = make_text_report(sizes, top_n=args.top, root=str(root_path))
    out_path.write_text(report_text, encoding='utf-8')
    print("Report written to:", out_path)

    if args.json:
        json_path = out_path.with_suffix('.json')
        json.dump({k: int(v) for k,v in sizes.items()}, json_path.open('w', encoding='utf-8'), indent=2)
        print("JSON written to:", json_path)

    if args.mail:
        EMAIL_USER = os.environ.get('EMAIL_USER')
        EMAIL_PASS = os.environ.get('EMAIL_PASS')
        EMAIL_TO   = os.environ.get('EMAIL_TO', EMAIL_USER)
        SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))

        if not EMAIL_USER or not EMAIL_PASS or not EMAIL_TO:
            print("ERROR: EMAIL_USER, EMAIL_PASS and EMAIL_TO must be set in environment to send mail.", file=sys.stderr)
            sys.exit(3)

        subject = f"Disk Analyzer Report for {root_path} - {date_str}"
        body = report_text + "\n\n(Report attached.)"
        print("Sending email to", EMAIL_TO, "via", SMTP_SERVER)
        try:
            send_email(SMTP_SERVER, SMTP_PORT, EMAIL_USER, EMAIL_PASS,
                       sender=EMAIL_USER, recipient=EMAIL_TO,
                       subject=subject, body=body, attachment_path=str(out_path))
            print("Email sent.")
        except Exception as e:
            print("Failed to send email:", e, file=sys.stderr)
            sys.exit(4)

if __name__ == '__main__':
    main()
