#!/bin/bash

# Configuration
# TODO Use values from the secrets.env file instead
API_TOKEN="your-api-token-here"
ZONE_ID="your-zone-id-here"
RECORD_NAME="reviewer.yourdomain.com"
LOG_FILE="$HOME/cloudflare-ddns.log"
IP_CACHE_FILE="$HOME/.cloudflare-last-ip"

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" >> "$LOG_FILE"
}

# Get current public IP
get_public_ip() {
    curl -s -4 ifconfig.me || curl -s -4 icanhazip.com || curl -s -4 checkip.amazonaws.com
}

# Get DNS record ID from Cloudflare
get_record_id() {
    curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records?name=$RECORD_NAME&type=A" \
         -H "Authorization: Bearer $API_TOKEN" \
         -H "Content-Type: application/json" | \
    python3 -c "import sys, json; print(json.load(sys.stdin)['result'][0]['id'])" 2>/dev/null
}

# Get current IP from Cloudflare
get_cloudflare_ip() {
    curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records?name=$RECORD_NAME&type=A" \
         -H "Authorization: Bearer $API_TOKEN" \
         -H "Content-Type: application/json" | \
    python3 -c "import sys, json; print(json.load(sys.stdin)['result'][0]['content'])" 2>/dev/null
}

# Update Cloudflare DNS record
update_cloudflare() {
    local record_id=$1
    local new_ip=$2
    
    curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$record_id" \
         -H "Authorization: Bearer $API_TOKEN" \
         -H "Content-Type: application/json" \
         --data "{\"type\":\"A\",\"name\":\"$RECORD_NAME\",\"content\":\"$new_ip\",\"ttl\":120,\"proxied\":false}"
}

# Main logic
log "Starting DDNS update check"

# Get current public IP
CURRENT_IP=$(get_public_ip)

if [ -z "$CURRENT_IP" ]; then
    log "ERROR: Could not determine public IP"
    exit 1
fi

log "Current public IP: $CURRENT_IP"

# Check cached IP
if [ -f "$IP_CACHE_FILE" ]; then
    CACHED_IP=$(cat "$IP_CACHE_FILE")
    log "Cached IP: $CACHED_IP"
    
    if [ "$CURRENT_IP" == "$CACHED_IP" ]; then
        log "IP unchanged, no update needed"
        exit 0
    fi
fi

# Get Cloudflare record IP
CF_IP=$(get_cloudflare_ip)
log "Cloudflare IP: $CF_IP"

if [ "$CURRENT_IP" == "$CF_IP" ]; then
    log "Cloudflare already has correct IP"
    echo "$CURRENT_IP" > "$IP_CACHE_FILE"
    exit 0
fi

# IP has changed, update Cloudflare
log "IP changed from $CF_IP to $CURRENT_IP, updating..."

RECORD_ID=$(get_record_id)

if [ -z "$RECORD_ID" ]; then
    log "ERROR: Could not get record ID from Cloudflare"
    exit 1
fi

log "Record ID: $RECORD_ID"

# Perform update
RESPONSE=$(update_cloudflare "$RECORD_ID" "$CURRENT_IP")

# Check if successful
if echo "$RESPONSE" | grep -q '"success":true'; then
    log "✅ Successfully updated $RECORD_NAME to $CURRENT_IP"
    echo "$CURRENT_IP" > "$IP_CACHE_FILE"
else
    log "❌ Update failed: $RESPONSE"
    exit 1
fi