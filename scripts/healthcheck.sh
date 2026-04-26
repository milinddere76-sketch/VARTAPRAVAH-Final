#!/bin/bash
# Varta Pravah - Enterprise Health Monitor

echo "📊 [$(date)] Starting System Health Probe..."

# 1. Resource Monitoring
CPU_LOAD=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')
MEM_USAGE=$(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2 }')
echo "💻 CPU Load: ${CPU_LOAD}% | Memory Usage: ${MEM_USAGE}"

# 2. Service Connectivity
echo "📡 Checking Internal Services..."
declare -A SERVICES=( ["Dashboard"]="http://localhost:8000/health" ["Redis"]="6379" ["Postgres"]="5432" )

for NAME in "${!SERVICES[@]}"; do
    if [[ ${SERVICES[$NAME]} == http* ]]; then
        if curl -s --max-time 2 "${SERVICES[$NAME]}" | grep -q "healthy"; then
            echo "✅ $NAME: ONLINE"
        else
            echo "❌ $NAME: OFFLINE"
        fi
    else
        if nc -z localhost "${SERVICES[$NAME]}" 2>/dev/null; then
            echo "✅ $NAME: LISTENING"
        else
            echo "❌ $NAME: PORT CLOSED"
        fi
    fi
done

# 3. Stream Status (Nginx Stat)
if curl -s http://localhost:8080/stat | grep -q "live"; then
    echo "🎥 STREAM: ACTIVE"
else
    echo "⚠️ STREAM: INACTIVE / IDLE"
fi

# 4. Storage Health
FREE_GB=$(df -h / | awk 'NR==2 {print $4}' | sed 's/G//')
echo "💾 Disk Space: ${FREE_GB}GB Free"

if (( $(echo "$FREE_GB < 5" | bc -l) )); then
    echo "🚨 [ALERT] CRITICAL DISK SPACE"
fi

echo "✨ Probe Complete."
