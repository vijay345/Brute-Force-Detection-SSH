#!/usr/bin/env python3
"""
bruteforce_parser.py
SSH Brute Force Log Analyser
Author: Vijay Srinivasan
Description: Parses SSH auth logs to detect, summarise, and report brute force activity.
MITRE ATT&CK: T1110 - Brute Force

Usage:
    python3 bruteforce_parser.py --log /var/log/auth.log --threshold 5
    python3 bruteforce_parser.py --log /var/log/auth.log --threshold 5 --report report.txt
"""

import re
import sys
import argparse
from collections import defaultdict
from datetime import datetime


# ── Regex patterns ─────────────────────────────────────────────────────────────
FAILED_LOGIN_PATTERN = re.compile(
    r'(\w+\s+\d+\s+\d+:\d+:\d+).*Failed password for (?:invalid user )?(\S+) from (\d+\.\d+\.\d+\.\d+) port (\d+)'
)
ACCEPTED_LOGIN_PATTERN = re.compile(
    r'(\w+\s+\d+\s+\d+:\d+:\d+).*Accepted (?:password|publickey) for (\S+) from (\d+\.\d+\.\d+\.\d+)'
)


# ── ANSI colours ───────────────────────────────────────────────────────────────
class Colour:
    RED    = '\033[91m'
    YELLOW = '\033[93m'
    GREEN  = '\033[92m'
    CYAN   = '\033[96m'
    BOLD   = '\033[1m'
    RESET  = '\033[0m'

def red(s):    return f"{Colour.RED}{s}{Colour.RESET}"
def yellow(s): return f"{Colour.YELLOW}{s}{Colour.RESET}"
def green(s):  return f"{Colour.GREEN}{s}{Colour.RESET}"
def cyan(s):   return f"{Colour.CYAN}{s}{Colour.RESET}"
def bold(s):   return f"{Colour.BOLD}{s}{Colour.RESET}"


# ── Parser ─────────────────────────────────────────────────────────────────────
def parse_log(log_path: str) -> tuple:
    """
    Parse auth.log and return failed and accepted login records.
    Returns:
        failed_by_ip  : dict {ip: [{'user': ..., 'time': ..., 'port': ...}]}
        accepted_logins: list of dicts
    """
    failed_by_ip   = defaultdict(list)
    failed_by_user = defaultdict(int)
    accepted_logins = []

    try:
        with open(log_path, 'r', errors='replace') as f:
            for line in f:
                # Check for failed logins
                match = FAILED_LOGIN_PATTERN.search(line)
                if match:
                    timestamp, username, ip, port = match.groups()
                    failed_by_ip[ip].append({
                        'user':      username,
                        'time':      timestamp,
                        'port':      port,
                        'raw_line':  line.strip()
                    })
                    failed_by_user[username] += 1
                    continue

                # Check for successful logins
                match = ACCEPTED_LOGIN_PATTERN.search(line)
                if match:
                    timestamp, username, ip = match.groups()
                    accepted_logins.append({
                        'user': username,
                        'ip':   ip,
                        'time': timestamp
                    })

    except FileNotFoundError:
        print(red(f"[!] Log file not found: {log_path}"))
        print(yellow("    Try running: sudo python3 bruteforce_parser.py --log /var/log/auth.log"))
        sys.exit(1)
    except PermissionError:
        print(red(f"[!] Permission denied: {log_path}"))
        print(yellow("    Try running with sudo."))
        sys.exit(1)

    return failed_by_ip, failed_by_user, accepted_logins


# ── Analysis ───────────────────────────────────────────────────────────────────
def analyse(failed_by_ip: dict, failed_by_user: dict,
            accepted_logins: list, threshold: int) -> list:
    """Identify IPs exceeding the failure threshold."""
    suspects = []
    for ip, events in failed_by_ip.items():
        if len(events) >= threshold:
            users_targeted = list({e['user'] for e in events})
            suspects.append({
                'ip':              ip,
                'total_attempts':  len(events),
                'users_targeted':  users_targeted,
                'first_seen':      events[0]['time'],
                'last_seen':       events[-1]['time'],
                'events':          events
            })
    # Sort by most attempts
    suspects.sort(key=lambda x: x['total_attempts'], reverse=True)
    return suspects


# ── Report ─────────────────────────────────────────────────────────────────────
def print_banner():
    print(cyan("╔══════════════════════════════════════════════════════╗"))
    print(cyan("║   SSH Brute Force Log Analyser                       ║"))
    print(cyan("║   MITRE ATT&CK: T1110 – Brute Force                  ║"))
    print(cyan("╚══════════════════════════════════════════════════════╝"))
    print()


def print_report(failed_by_ip, failed_by_user, accepted_logins,
                 suspects, threshold, report_lines=None):

    def out(line=''):
        print(line)
        if report_lines is not None:
            report_lines.append(line)

    out(bold("═" * 56))
    out(bold("  SUMMARY"))
    out(bold("═" * 56))
    out(f"  Total unique attacker IPs  : {red(str(len(failed_by_ip)))}")
    out(f"  Total failed login events  : {red(str(sum(len(v) for v in failed_by_ip.values())))}")
    out(f"  Successful logins detected : {green(str(len(accepted_logins)))}")
    out(f"  Detection threshold        : {threshold} attempts")
    out(f"  Suspect IPs (>= threshold) : {red(str(len(suspects)))}")
    out()

    # ── Suspects ──
    if suspects:
        out(bold("═" * 56))
        out(bold(red("  ⚠  BRUTE FORCE SUSPECTS DETECTED")))
        out(bold("═" * 56))
        for s in suspects:
            out(f"\n  {bold('IP Address')}      : {red(s['ip'])}")
            out(f"  Failed Attempts  : {red(str(s['total_attempts']))}")
            out(f"  Usernames tried  : {yellow(', '.join(s['users_targeted']))}")
            out(f"  First seen       : {s['first_seen']}")
            out(f"  Last seen        : {s['last_seen']}")
            out(f"\n  {'Last 5 log entries':}")
            for e in s['events'][-5:]:
                out(f"    [{e['time']}] user={e['user']} port={e['port']}")
        out()
    else:
        out(green(f"  [✓] No IPs exceeded the threshold of {threshold} attempts."))
        out()

    # ── Top targeted usernames ──
    out(bold("═" * 56))
    out(bold("  TOP TARGETED USERNAMES"))
    out(bold("═" * 56))
    sorted_users = sorted(failed_by_user.items(), key=lambda x: x[1], reverse=True)[:10]
    out(f"  {'COUNT':<8} {'USERNAME'}")
    out(f"  {'-----':<8} {'--------'}")
    for user, count in sorted_users:
        out(f"  {str(count):<8} {yellow(user)}")
    out()

    # ── Top attacker IPs ──
    out(bold("═" * 56))
    out(bold("  TOP ATTACKER IPs (ALL TIME)"))
    out(bold("═" * 56))
    sorted_ips = sorted(failed_by_ip.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    out(f"  {'COUNT':<8} {'IP ADDRESS'}")
    out(f"  {'-----':<8} {'----------'}")
    for ip, events in sorted_ips:
        out(f"  {str(len(events)):<8} {red(ip)}")
    out()

    # ── Successful logins (post-attack verification) ──
    if accepted_logins:
        out(bold("═" * 56))
        out(bold(yellow("  ⚠  SUCCESSFUL LOGINS (verify these are legitimate)")))
        out(bold("═" * 56))
        out(f"  {'TIME':<25} {'USER':<15} {'IP'}")
        out(f"  {'----':<25} {'----':<15} {'--'}")
        for login in accepted_logins[-10:]:
            out(f"  {login['time']:<25} {login['user']:<15} {green(login['ip'])}")
        out()

    # ── Mitigation recommendations ──
    out(bold("═" * 56))
    out(bold("  RECOMMENDED ACTIONS"))
    out(bold("═" * 56))
    if suspects:
        for s in suspects:
            out(f"  sudo fail2ban-client set sshd banip {s['ip']}")
    out()
    out("  Hardening steps:")
    out("  1. Disable password auth  → PasswordAuthentication no")
    out("  2. Use SSH keys only      → ssh-keygen && ssh-copy-id")
    out("  3. Change default port    → Port 2222 in sshd_config")
    out("  4. Set MaxAuthTries       → MaxAuthTries 3")
    out("  5. Restrict by IP         → AllowUsers user@trusted_ip")
    out()

    out(f"  Scan completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    out(bold("═" * 56))


# ── Entry point ────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description='SSH Brute Force Log Analyser — MITRE T1110',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudo python3 bruteforce_parser.py --log /var/log/auth.log
  sudo python3 bruteforce_parser.py --log /var/log/auth.log --threshold 10
  sudo python3 bruteforce_parser.py --log /var/log/auth.log --report output.txt
        """
    )
    parser.add_argument('--log',       default='/var/log/auth.log',
                        help='Path to SSH auth log (default: /var/log/auth.log)')
    parser.add_argument('--threshold', type=int, default=5,
                        help='Minimum failed attempts to flag as suspect (default: 5)')
    parser.add_argument('--report',    default=None,
                        help='Optional: save plain-text report to file')
    args = parser.parse_args()

    print_banner()
    print(cyan(f"[*] Parsing log: {args.log}"))
    print(cyan(f"[*] Detection threshold: {args.threshold} failed attempts\n"))

    failed_by_ip, failed_by_user, accepted_logins = parse_log(args.log)
    suspects = analyse(failed_by_ip, failed_by_user, accepted_logins, args.threshold)

    report_lines = [] if args.report else None
    print_report(failed_by_ip, failed_by_user, accepted_logins,
                 suspects, args.threshold, report_lines)

    if args.report and report_lines is not None:
        # Strip ANSI codes for plain-text file
        ansi_escape = re.compile(r'\x1B\[[0-9;]*m')
        clean_lines = [ansi_escape.sub('', line) for line in report_lines]
        with open(args.report, 'w') as f:
            f.write('\n'.join(clean_lines))
        print(green(f"[✓] Report saved to: {args.report}"))


if __name__ == '__main__':
    main()
