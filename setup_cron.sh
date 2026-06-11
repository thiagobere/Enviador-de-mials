#!/bin/bash
# Installs a cron job to run the sponsor bot every day at 9:00 AM Argentina time (UTC-3 = 12:00 UTC)
# Run this once: bash setup_cron.sh

BOT_DIR="$(cd "$(dirname "$0")" && pwd)"
CRON_CMD="0 12 * * * cd $BOT_DIR && bash run.sh >> data/cron.log 2>&1"

# Remove existing sponsor bot cron if any
(crontab -l 2>/dev/null | grep -v "Enviador-de-mials") | crontab -

# Add new cron entry
(crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

echo "✅ Cron job instalado:"
echo "   $CRON_CMD"
echo ""
echo "Verifica con: crontab -l"
