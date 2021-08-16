#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# invoke with python3 -O to omit debug output

"""
quick and dirty python script to enable or disable a Unifi AP.
takes 'enable' or 'disable' as a cli argument
required secrets must be in .env
"""

import requests
from requests_toolbelt.utils import dump
import json
import sys
import os
import argparse
from pathlib import Path
from dotenv import load_dotenv
from time import sleep

# read secrets from env vars
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
BASEURL = os.getenv('BASEURL')
SITE = os.getenv('SITE')
UPSTAIRS_AP_GUID = os.getenv('UPSTAIRS_AP_GUID')
GAMEROOM_AP_GUID = os.getenv('GAMEROOM_AP_GUID')
GAMEROOM_SWITCH_ENABLE_OVERRIDES = os.getenv('AP_SWITCH_ENABLE_OVERRIDES')
GAMEROOM_SWITCH_DISABLE_OVERRIDES = os.getenv('AP_SWITCH_DISABLE_OVERRIDES')

# constants
LOGINURL = BASEURL + '/api/auth/login'
LOGOUTURL = BASEURL + '/api/auth/logout'

# create a custom requests object, modifying the global module throws an error
http = requests.Session()
assert_status_hook = lambda response, *args, **kwargs: response.raise_for_status()
http.hooks["response"] = [assert_status_hook]

# dump verbose request and response data to stdout
def logging_hook(response, *args, **kwargs):
    data = dump.dump_all(response)
    print(data.decode('utf-8'))

#setup Requests to log request and response to stdout verbosely
http = requests.Session()
http.hooks["response"] = [logging_hook]

# set required headers
http.headers.update({
    "Content-Type": "application/json; charset=utf-8"
})    

def login():
    creds = json.dumps({'username': USERNAME,'password': PASSWORD})
    response = http.post(LOGINURL, data=creds)
    # new API requires the CSRF token going forward else we get 401's or 404's
    http.headers.update({
        "X-CSRF-Token": response.headers['X-CSRF-Token']
    })

def logout():
    response = http.post(LOGOUTURL)
    
def toggleAP(guid, action):
    """
    Toggles an AP into 'disabled' mode and back. Perhaps useful for reducing RF exposure during sleep.
    Note the guid is NOT the MAC addr of the AP.
    To get the guid use the browser dev console
    """
    APURL = BASEURL + '/proxy/network/api/s/' + SITE + '/rest/device/' + guid
    if action == "enableAP":
        disableFlag = False
    elif action == "disableAP":
        disableFlag = True
    payload = json.dumps({'disabled': disableFlag})
    response = http.put(APURL, data = payload)

def OverrideSwitchPort(guid, jsonPutData):
    """
    Sets switch port overrides for a device, eg an AP. Useful for disabling wired connections
    to ensure that kids go to bed instead of staying up all night watching TV or playing games
    To get the guid use the browser dev console
    The jsonPutData is read as an env var, and must contain config data for ALL switchports on the device, else defaults will be written
    to unchanged ports.  See env.example
    """
    APURL = BASEURL + '/proxy/network/api/s/' + SITE + '/rest/device/' + guid
    response = http.put(APURL, data = jsonPutData)

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", help="'enableAP' or 'disableAP' or 'enableSwitchPort' or 'disableSwitchPort' (no quotes)")
    args = parser.parse_args()
    if args.action == "enableAP" or args.action == "disableAP" or args.action == "enableSwitchPort" or args.action == "disableSwitchPort":
        return(args.action)
    else:
        sys.exit("Invalid action specified. Please pass 'enableAP', 'disableAP', 'enableSwitchPort' or 'disableSwitchPort' as a cli arg")

def main():
    action = parseArgs()
    login()
    sleep(5)
    if(action == "enableAP" or action == "disableAP"):
        toggleAP(UPSTAIRS_AP_GUID,action)
    elif(action == "disableSwitchPort"):
        OverrideSwitchPort(GAMEROOM_AP_GUID, GAMEROOM_SWITCH_DISABLE_OVERRIDES)
    elif(action == "enableSwitchPort"):
        OverrideSwitchPort(GAMEROOM_AP_GUID, GAMEROOM_SWITCH_ENABLE_OVERRIDES)
    logout()

if __name__ == "__main__":
    main()