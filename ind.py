"""
CISCO SAMPLE CODE LICENSE
                                  Version 1.1
                Copyright (c) 2020 Cisco and/or its affiliates
   These terms govern this Cisco Systems, Inc. ("Cisco"), example or demo
   source code and its associated documentation (together, the "Sample
   Code"). By downloading, copying, modifying, compiling, or redistributing
   the Sample Code, you accept and agree to be bound by the following terms
   and conditions (the "License"). If you are accepting the License on
   behalf of an entity, you represent that you have the authority to do so
   (either you or the entity, "you"). Sample Code is not supported by Cisco
   TAC and is not tested for quality or performance. This is your only
   license to the Sample Code and all rights not expressly granted are
   reserved.
   1. LICENSE GRANT: Subject to the terms and conditions of this License,
      Cisco hereby grants to you a perpetual, worldwide, non-exclusive, non-
      transferable, non-sublicensable, royalty-free license to copy and
      modify the Sample Code in source code form, and compile and
      redistribute the Sample Code in binary/object code or other executable
      forms, in whole or in part, solely for use with Cisco products and
      services. For interpreted languages like Java and Python, the
      executable form of the software may include source code and
      compilation is not required.
   2. CONDITIONS: You shall not use the Sample Code independent of, or to
      replicate or compete with, a Cisco product or service. Cisco products
      and services are licensed under their own separate terms and you shall
      not use the Sample Code in any way that violates or is inconsistent
      with those terms (for more information, please visit:
      www.cisco.com/go/terms).
   3. OWNERSHIP: Cisco retains sole and exclusive ownership of the Sample
      Code, including all intellectual property rights therein, except with
      respect to any third-party material that may be used in or by the
      Sample Code. Any such third-party material is licensed under its own
      separate terms (such as an open source license) and all use must be in
      full accordance with the applicable license. This License does not
      grant you permission to use any trade names, trademarks, service
      marks, or product names of Cisco. If you provide any feedback to Cisco
      regarding the Sample Code, you agree that Cisco, its partners, and its
      customers shall be free to use and incorporate such feedback into the
      Sample Code, and Cisco products and services, for any purpose, and
      without restriction, payment, or additional consideration of any kind.
      If you initiate or participate in any litigation against Cisco, its
      partners, or its customers (including cross-claims and counter-claims)
      alleging that the Sample Code and/or its use infringe any patent,
      copyright, or other intellectual property right, then all rights
      granted to you under this License shall terminate immediately without
      notice.
   4. LIMITATION OF LIABILITY: CISCO SHALL HAVE NO LIABILITY IN CONNECTION
      WITH OR RELATING TO THIS LICENSE OR USE OF THE SAMPLE CODE, FOR
      DAMAGES OF ANY KIND, INCLUDING BUT NOT LIMITED TO DIRECT, INCIDENTAL,
      AND CONSEQUENTIAL DAMAGES, OR FOR ANY LOSS OF USE, DATA, INFORMATION,
      PROFITS, BUSINESS, OR GOODWILL, HOWEVER CAUSED, EVEN IF ADVISED OF THE
      POSSIBILITY OF SUCH DAMAGES.
   5. DISCLAIMER OF WARRANTY: SAMPLE CODE IS INTENDED FOR EXAMPLE PURPOSES
      ONLY AND IS PROVIDED BY CISCO "AS IS" WITH ALL FAULTS AND WITHOUT
      WARRANTY OR SUPPORT OF ANY KIND. TO THE MAXIMUM EXTENT PERMITTED BY
      LAW, ALL EXPRESS AND IMPLIED CONDITIONS, REPRESENTATIONS, AND
      WARRANTIES INCLUDING, WITHOUT LIMITATION, ANY IMPLIED WARRANTY OR
      CONDITION OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-
      INFRINGEMENT, SATISFACTORY QUALITY, NON-INTERFERENCE, AND ACCURACY,
      ARE HEREBY EXCLUDED AND EXPRESSLY DISCLAIMED BY CISCO. CISCO DOES NOT
      WARRANT THAT THE SAMPLE CODE IS SUITABLE FOR PRODUCTION OR COMMERCIAL
      USE, WILL OPERATE PROPERLY, IS ACCURATE OR COMPLETE, OR IS WITHOUT
      ERROR OR DEFECT.
   6. GENERAL: This License shall be governed by and interpreted in
      accordance with the laws of the State of California, excluding its
      conflict of laws provisions. You agree to comply with all applicable
      United States export laws, rules, and regulations. If any provision of
      this License is judged illegal, invalid, or otherwise unenforceable,
      that provision shall be severed and the rest of the License shall
      remain in full force and effect. No failure by Cisco to enforce any of
      its rights related to the Sample Code or to a breach of this License
      in a particular situation will act as a waiver of such rights. In the
      event of any inconsistencies with any other terms, this License shall
      take precedence.
"""

from aiohttp import BasicAuth
from dotenv import load_dotenv
from flask import jsonify
import requests, os, json
from dotenv import load_dotenv

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

# Set IND access profile password
def set_password(ap, pw):
    url = f"https://{os.environ['IND_HOST']}/api/v1/access-profiles/{ap}"

    user = os.environ['IND_USER']
    password = os.environ['IND_PASS']

    headers = {
        "Accept" : "application/json",
        "Content-Type" : "application/json"
    }

    resp = requests.get(url, headers=headers, auth=requests.auth.HTTPBasicAuth(user, password), verify=False)
    profile = resp.json()['record']
    profile['deviceAccessSettings']['password'] = pw
    profile.pop('associatedDevicesCount')
    profile.pop('id')
    profile.pop('associatedDiscoveryProfilesCount')
    profile['deviceAccessSettings']['advancedDeviceAccessSettings'].pop('sshSettings')
    
    with open('profile.json', 'w') as f:
        json.dump(profile, f, indent=2)

    profile_string = ""
    with open('profile.json', 'r') as f:
        profile_string=f.read()

    resp = requests.put(url, data=profile_string, headers=headers, auth=requests.auth.HTTPBasicAuth(user, password), verify=False)

# Retrieve IND access profile password
def get_password(ap_id):
    url = f"https://{os.environ['IND_HOST']}/api/v1/access-profiles/{ap_id}"

    user = os.environ['IND_USER']
    password = os.environ['IND_PASS']

    headers = {
        "Accept" : "application/json"
    }

    device = requests.get(url, headers=headers, auth=requests.auth.HTTPBasicAuth(user, password), verify=False)

    try:
        return device.json()['record']['deviceAccessSettings']['password']
    except:
        return "No password in IND"

# Retrieve a list of IND network devices
def get_network_devices():
    url = f"https://{os.environ['IND_HOST']}/api/v1/devices"

    user = os.environ['IND_USER']
    password = os.environ['IND_PASS']

    headers = {
        "Accept" : "application/json"
    }

    resp = requests.get(url, headers=headers, auth=requests.auth.HTTPBasicAuth(user, password), verify=False)
    devices = resp.json()['records']

    result = []
    for d in devices:
        result += [{
            'name' : d['name'],
            'id' : d['id'],
            'description' : d['description'],
            'type' : d['deviceType'],
            'password' : get_password(d['accessProfileId']),
            'ip' : d['ipAddress'],
            'ap' : d['accessProfileId']
        }]
    
    return result

if __name__ == "__main__":
    load_dotenv()
    print(json.dumps(get_network_devices(), indent=2))
