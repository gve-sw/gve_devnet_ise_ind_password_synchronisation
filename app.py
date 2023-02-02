""" Copyright (c) 2020 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. 
"""

# Import Section
from flask import Flask, render_template, request, url_for, redirect
from collections import defaultdict
import datetime
import requests
import json
from dotenv import load_dotenv
import os
#import merakiAPI
from dnacentersdk import api
import ise, ind

# load all environment variables
load_dotenv()


# Global variables
app = Flask(__name__)



# Read data from json file
def getJson(filepath):
	with open(filepath, 'r') as f:
		json_content = json.loads(f.read())
		f.close()

	return json_content

# Write data to json file
def writeJson(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f)
    f.close()


# Landing page
@app.route('/', methods=['GET', 'POST'])
def home():
    try:
        if request.method == "POST":
            info = request.form.get('device')
            info_split = info.split('-')
            ap_id = info_split[0]
            pw = info_split[1]
            ind.set_password(ap_id, pw)

        ise_devices = ise.get_network_devices()
        ind_devices = ind.get_network_devices()

        devices = get_combined_list(ise_devices, ind_devices)

        return render_template('home.html', hiddenLinks=False, devices=devices)
    except Exception as e: 
        print(e)  
        return render_template('home.html', error=False, errormessage="CUSTOMIZE: Add custom message here.", errorcode=e)

# Get combined list of devices and passwords
def get_combined_list(ise, ind):
    result = []
    for d in ind:
        ip = d['ip']
        for i in ise:
            if ip == i['ip']:
                result += [{
                    'indname' : d['name'],
                    'isename' : i['name'],
                    'type' : d['type'],
                    'ip' : d['ip'],
                    'indpw' : d['password'],
                    'isepw' : i['password'],
                    'ap' : d['ap']
                }]
    return result

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5555, debug=True)