#!/bin/bash
set -x

. /home/unifi/unifi_device_manager/bin/activate
cd /home/unifi/unifi_device_manager
./unifi_device_manager.py disableAP
sleep 5
./unifi_device_manager.py disableSwitchPorts
