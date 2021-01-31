#!/bin/bash
set -x

source /home/unifi/unifi_device_manager/bin/activate
/home/unifi/unifi_device_manager/bin/python3 /home/unifi/unifi_device_manager/unifi_device_manager.py enable
