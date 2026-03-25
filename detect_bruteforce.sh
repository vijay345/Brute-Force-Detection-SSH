#!/bin/bash
# =============================================================================
# detect_bruteforce.sh
# SSH Brute Force Detection & Alerting Script
# Author: Vijay Srinivasan
# Description: Monitors SSH auth logs for brute force patterns and alerts
# =============================================================================

# ── Configuration ─────────────────────────────────────────────────────────────
THRESHOLD=5              # Number of failed attempts to trigger alert
TIME_WINDOW=600          # Time window in seconds (10 minutes)
LOG_FILE="/var/log/auth.log"
ALERT_LOG="/var/log/bruteforce_alerts.log"
BAN_ENABLED=false        # Set to true to auto-ban via fail2ban

# Colours for terminal output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m' # No Colour

# ── Functions ──────────────────────────────────────────────────────────────────

print_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════╗"
    echo "║     SSH Brute Force Detection Script             ║"
    echo "║     MITRE ATT&CK: T1110 - Brute Force           ║"
    echo "╚══════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}[!] This script must be run as root (sudo).${NC}"
        exit 1
    fi
}

check_logfile() {
    if [[ ! -f "$LOG_FILE" ]]; then
        echo -e "${RED}[!] Log file not found: $LOG_FILE${NC}"
        echo -e "${YELLOW}[*] Trying journalctl instead...${NC}"
        USE_JOURNALCTL=true
    else
        USE_JOURNALCTL=false
    fi
}

get_failed_logins() {
    echo -e "${CYAN}[*] Scanning for failed SSH login attempts...${NC}"

    if [[ "$USE_JOURNALCTL" == true ]]; then
        journalctl -u ssh --since "10 minutes ago" | grep "Failed password"
    else
        grep "Failed password" "$LOG_FILE"
    fi
}

extract_ips() {
    # Extract IPs using regex — works for both journalctl and auth.log formats
    if [[ "$USE_JOURNALCTL" == true ]]; then
        journalctl -u ssh --since "10 minutes ago" \
            | grep "Failed password" \
            | grep -oP 'from \K[\d\.]+' \
            | sort | uniq -c | sort -rn
    else
        grep "Failed password" "$LOG_FILE" \
            | grep -oP 'from \K[\d\.]+' \
            | sort | uniq -c | sort -rn
    fi
}

check_threshold() {
    echo -e "\n${CYAN}[*] Checking IPs exceeding threshold of $THRESHOLD attempts...${NC}\n"

    FOUND=false
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

    while read -r count ip; do
        if [[ "$count" -ge "$THRESHOLD" ]]; then
            FOUND=true
            echo -e "${RED}[ALERT] Brute Force Detected!${NC}"
            echo -e "  IP Address : ${RED}$ip${NC}"
            echo -e "  Attempts   : ${RED}$count${NC} failed logins"
            echo -e "  Threshold  : $THRESHOLD"
            echo -e "  Time       : $TIMESTAMP"
            echo ""

            # Log to alert file
            echo "[$TIMESTAMP] BRUTE_FORCE_DETECTED | IP: $ip | Attempts: $count" >> "$ALERT_LOG"

            # Optional: auto-ban
            if [[ "$BAN_ENABLED" == true ]]; then
                echo -e "${YELLOW}[*] Auto-banning $ip via Fail2Ban...${NC}"
                fail2ban-client set sshd banip "$ip" 2>/dev/null
                if [[ $? -eq 0 ]]; then
                    echo -e "${GREEN}[+] Successfully banned: $ip${NC}"
                    echo "[$TIMESTAMP] IP_BANNED | $ip" >> "$ALERT_LOG"
                else
                    echo -e "${RED}[!] Failed to ban $ip — is Fail2Ban running?${NC}"
                fi
            fi
        fi
    done < <(extract_ips)

    if [[ "$FOUND" == false ]]; then
        echo -e "${GREEN}[✓] No IPs exceeded the threshold of $THRESHOLD attempts.${NC}"
        echo -e "    System appears clean within the monitoring window.\n"
    fi
}

show_top_attackers() {
    echo -e "${CYAN}[*] Top 10 IPs with failed SSH logins (all time):${NC}\n"
    printf "  %-8s %-20s\n" "COUNT" "IP ADDRESS"
    printf "  %-8s %-20s\n" "-----" "----------"

    if [[ "$USE_JOURNALCTL" == true ]]; then
        journalctl -u ssh | grep "Failed password" \
            | grep -oP 'from \K[\d\.]+' \
            | sort | uniq -c | sort -rn | head -10 \
            | while read -r count ip; do
                printf "  %-8s ${RED}%-20s${NC}\n" "$count" "$ip"
            done
    else
        grep "Failed password" "$LOG_FILE" \
            | grep -oP 'from \K[\d\.]+' \
            | sort | uniq -c | sort -rn | head -10 \
            | while read -r count ip; do
                printf "  %-8s ${RED}%-20s${NC}\n" "$count" "$ip"
            done
    fi
    echo ""
}

show_targeted_usernames() {
    echo -e "${CYAN}[*] Most targeted usernames:${NC}\n"
    printf "  %-8s %-20s\n" "COUNT" "USERNAME"
    printf "  %-8s %-20s\n" "-----" "--------"

    if [[ "$USE_JOURNALCTL" == true ]]; then
        journalctl -u ssh | grep "Failed password" \
            | grep -oP 'for (invalid user )?\K\S+' \
            | sort | uniq -c | sort -rn | head -10 \
            | while read -r count user; do
                printf "  %-8s ${YELLOW}%-20s${NC}\n" "$count" "$user"
            done
    else
        grep "Failed password" "$LOG_FILE" \
            | grep -oP 'for (invalid user )?\K\S+' \
            | sort | uniq -c | sort -rn | head -10 \
            | while read -r count user; do
                printf "  %-8s ${YELLOW}%-20s${NC}\n" "$count" "$user"
            done
    fi
    echo ""
}

show_fail2ban_status() {
    echo -e "${CYAN}[*] Fail2Ban SSH Jail Status:${NC}\n"
    if command -v fail2ban-client &>/dev/null; then
        fail2ban-client status sshd 2>/dev/null || echo -e "${YELLOW}  Fail2Ban sshd jail not active.${NC}"
    else
        echo -e "${YELLOW}  Fail2Ban not installed or not in PATH.${NC}"
    fi
    echo ""
}

show_summary() {
    echo -e "${CYAN}══════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  Detection Summary${NC}"
    echo -e "${CYAN}══════════════════════════════════════════════════${NC}"

    if [[ "$USE_JOURNALCTL" == true ]]; then
        TOTAL_FAILURES=$(journalctl -u ssh | grep -c "Failed password")
        UNIQUE_IPS=$(journalctl -u ssh | grep "Failed password" \
            | grep -oP 'from \K[\d\.]+' | sort -u | wc -l)
    else
        TOTAL_FAILURES=$(grep -c "Failed password" "$LOG_FILE" 2>/dev/null || echo 0)
        UNIQUE_IPS=$(grep "Failed password" "$LOG_FILE" 2>/dev/null \
            | grep -oP 'from \K[\d\.]+' | sort -u | wc -l)
    fi

    echo -e "  Total failed login attempts : ${RED}$TOTAL_FAILURES${NC}"
    echo -e "  Unique attacker IPs         : ${RED}$UNIQUE_IPS${NC}"
    echo -e "  Alert threshold             : $THRESHOLD attempts"
    echo -e "  Auto-ban enabled            : $BAN_ENABLED"
    echo -e "  Alert log                   : $ALERT_LOG"
    echo -e "${CYAN}══════════════════════════════════════════════════${NC}\n"
}

# ── Main ───────────────────────────────────────────────────────────────────────
print_banner
check_root
check_logfile
show_top_attackers
show_targeted_usernames
check_threshold
show_fail2ban_status
show_summary

echo -e "${GREEN}[✓] Detection scan complete.${NC}\n"
