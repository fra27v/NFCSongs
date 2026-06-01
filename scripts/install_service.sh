#!/bin/bash
set -e

USER_NAME="${1:-$USER}"

chmod +x /home/$USER_NAME/NFCSongs/scripts/start_nfc.sh

sudo cp /home/$USER_NAME/NFCSongs/scripts/nfcplayer.service /etc/systemd/system/nfcplayer@.service

sudo systemctl daemon-reload
sudo systemctl enable nfcplayer@$USER_NAME.service
sudo systemctl restart nfcplayer@$USER_NAME.service

echo "Installed and started nfcplayer@$USER_NAME.service"
echo "Status:"
systemctl status nfcplayer@$USER_NAME.service --no-pager