# unifi_device_manager

## Overview
Unifi is great, but there are some things you want to do programmatically, and the API 
documentation isn't great.  The API is also notably different for UnifiOS devices than
previous gen devices.

It's not presently possible to 'disable' Unifi AP's on a schedule.  Disabling them (in the UI or mobile app)
turns off the radios (and also the LED's), which can reduce RF exposure (eg while folks are sleeping).

This script logs into the new UnifiOS API, and toggles AP's on and off (disabling/enabling them).
It's designed to be called from cron or another scheduler, to automatically turn AP's off at night,
and back on in the am.

This has now been extended to do other things on a schedule, like block specific switchports by setting their port profile to 'Disabled'.
This can be super handy for blocking teenagers' wired PS5, gaming PC, wired smart TV, etc. so that they can focus on homework
on school nights, etc.

### Usage
Invoke unifi_device_manager.py with one of the following CLI params:
 * enableAP
 * disableAP
 * enableSwitchPort
 * disableSwitchPort

disableAP: disables the radios on a Unifi AP
enableAP:  enables the radios on a Unifi AP
disableSwitchPort: sends a JSON blob of switchport overrides to a unifi switch, or an AP with switchports.  useful for disabling switchports, etc.
enableSwitchPort: sends a JSON blob of switchport overrides to a unifi switch, or an AP with switchports.  useful for enabling switchports, etc.

disableSwitchPorts / enableSwitchPort reads JSON blobs out of environment variables that must include config for *every switchport on the device*, not just the one you want 
to change.

This is obviously not ideal, but seems to be a hard constraint at this point.


## Gratitude
* Thanks to [@Art-Of-Wifi](https://github.com/Art-of-WiFi) for their [UniFi-API-Client](https://github.com/Art-of-WiFi/UniFi-API-client) and [Browser](https://github.com/Art-of-WiFi/UniFi-API-browser).  I didn't think I'd be spinning up Apache+PHP in 2021, but this package is extremely useful and represents probably the best documentation available for the Unifi API.

## Requirements
* Python3
* A Unifi controller. Tested against a Cloud Key Gen2+ running "Network" platform 6.0.43 and "Firmware" 2.0.24.
* Local (not cloud) credentials with administrative privileges for the site in question
* The GUID for the AP (or AP's) you wish to enable/disable

## Installation (Linux or OSX)
1. Create a separate user named 'unifi'
```console
sudo adduser unifi
```
2. Change to the 'unifi' user
```console
sudo su - unifi
```

3. Clone the repo
```console
git clone https://github.com/alchemydc/unifi_device_manager.git
cd unifi_device_manager
```

4. Create and activate a python virtual environment
(recommended to keep deps separate from system python)
 * OSX
  ```console
  python3 -m virtualenv . && source bin/activate
  ```
* Linux
```console
  python3 -m venv . && source bin/activate
  ```
5. Install python dependencies
 * requests: for making the https API calls
 * python-dotenv: for keeping secrets out of the source
 * requests_toolbelt: for debugging HTTP requests/responses
 ```console
 python -m pip install -r requirements.txt
 ```

## Configuration
1. Copy the environment template
```console
cp .env-template .env
chmod 600 .env
```

Note that the portconf_id's will be specific to your environment, so double check that these are correct.


2. Populate the .env file with the *local* username, password, BaseURL and AP GUID for your Unifi installation

## Test run
```console
python3 unifi_device_manager.py disableAP
python3 unifi_device_manager.py disableSwitchPort
python3 unifi_device_manager.py enableAP
python3 unifi_device_manager.py enableSwitchPort
```

## Schedule it to run automatically
The included crontab will disable the AP at 23:00 local time each night, and re-enable it at 07:00 each morning.

Install crontab to run the disable and enable scripts automatically:
```console
/usr/bin/crontab unifi.crontab
```

## Troubleshooting
If things aren't working as expected, ensure that your username, password, baseURL, site and AP GUID are set correctly.

If the script works when run directly, but fails when run by cron, check to ensure your home directory is correct in enable.sh and disable.sh and that env vars are being properly imported by python-dotenv.
