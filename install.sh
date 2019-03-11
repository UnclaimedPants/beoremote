#!/usr/bin/env bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

echo "Beo4kodi Installer"
echo ""
echo "Before installation, you must answer a few configuration questions"
echo ""

read -p "Enter kodi hostname [localhost]: " INST_HOSTNAME
INST_HOSTNAME=${INST_HOSTNAME:-localhost}

read -p "Enter kodi username [kodi]: " INST_USERNAME
INST_USERNAME=${INST_USERNAME:-kodi}

read -p "Enter kodi password []: " INST_PASSWORD
INST_PASSWORD=${INST_PASSWORD}

read -p "Enter ir device [/dev/ttyACM0]: " INST_IR_DEVICE
INST_IR_DEVICE=${INST_IR_DEVICE:-/dev/ttyACM0}

STR="\"BR_KODI_USER=${INST_USERNAME}\" \"BR_KODI_PASS=${INST_PASSWORD}\" \"BR_KODI_HOST=${INST_HOSTNAME}\" \"BR_IR_DEVICE=${INST_IR_DEVICE}\""

echo ""
echo "Installing python dependencies.."
pip install -r requirements.txt

echo "Installing systemd unit.."
sed "s,\(Environment=\).*\$,\\1${STR}," beo4kodi.service > /etc/systemd/system/beo4kodi.service

echo "Installing beo4kodi.py into /usr/local/bin .."
cp beo4kodi.py /usr/local/bin/

echo "Starting and enabling unit.."
systemctl start beo4kodi.service
systemctl enable beo4kodi.service

