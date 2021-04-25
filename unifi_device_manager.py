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
AP_GUID = os.getenv('UPSTAIRSAP_GUID')

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
    To get the guid call FIXME $baseurl/api/s/$site/stat/device
    """
    APURL = BASEURL + '/proxy/network/api/s/' + SITE + '/rest/device/' + guid
    if action == "enable":
        disableFlag = False
    elif action == "disable":
        disableFlag = True
    payload = json.dumps({'disabled': disableFlag})
    response = http.put(APURL, data = payload)

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", help="'enable' or 'disable' (no quotes)")
    args = parser.parse_args()
    if args.action == "enable" or args.action == "disable":
        return(args.action)
    else:
        sys.exit("Invalid action specified. Please pass 'enable' or 'disable' as a cli arg")

def main():
    action = parseArgs()
    login()
    sleep(5)
    toggleAP(AP_GUID,action)
    logout()

if __name__ == "__main__":
    main()