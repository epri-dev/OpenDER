#!/usr/bin/env Python3
#
# Copyright 2024 Kenneth J. Gibson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" 
Simple IEEE 2030.5 SEP client  
"""

__authors__ = [
  '"Ken Gibson" <kenjgibson@gmail.com>'
]

import requests
import json
import time
from sep_types import *

class SEPClient:
    def __init__(self):
        # Full implementation will take initial values here
        return

    def discoverDERMS(self):
        # LOTS of discovery and security omitted here for this simple prototype
        # Assume test DERMS is run as a local process
        self.dermsURL = "http://localhost:8000"

    # Execute an HTTP verb used in 2030.5  Using the 'requests' package
    # keys in dictionaries will get decoded by the recipient as strings
    # so sep data objects should be designed accordingly.
    # For a GET that responds with a JSON body, returns the decoded body.
    def _doHTTP( self, verb, URI, body=None):
        retries = 2
        retry = 0
        while retry < retries:
            try:
                match verb:
                    case 'GET':
                        resp = requests.get(URI)
                    case 'HEAD':
                        resp = requests.head(URI)
                    case 'PUT':
                        # The following will set the content type to JSON
                        # and convert the body with json.dumps()
                        resp = requests.put(URI, json=body)
                        print( "Executed PUT, response text is:", resp.text)
                    case 'POST':
                        resp = requests.post(URI, json=body)
                        print( "Executed POST, response text is:", resp.text)
                    case _:
                        return None
            except requests.exceptions.Timeout as err:
                retry += 1
                if retry < retries:
                    continue
                print( "Error: timeout on Get to ", self.dermsURL)
                raise SystemExit(err)
            except requests.exceptions.ConnectTimeout as err:
                retry += 1
                if retry < retries:
                    continue
                print("Connection Timeout error on Get to: ", self.dermsURL)
                raise SystemExit(err)
            except requests.exceptions.TooManyRedirects as err:
                print( "Error: Too many redirects on Get to", self.dermsURL)
                raise SystemExit(err)
            except requests.exceptions.ConnectionError as err:
                print("Connection error on Get to: ", self.dermsURL)
                raise SystemExit(err)
            except requests.exceptions.HTTPError as err:
                print("HTTP error on Get to: ", self.dermsURL)
                raise SystemExit(err)
            except requests.exceptions.ReadTimeout as err:
                print("Read Timeout on Get to: ", self.dermsURL)
                raise SystemExit(err)
            else:
                # check for any other errors
                if resp.status_code != requests.codes.ok:
                    print( f"Uncaught error on verb {verb}, response status code: {resp.status_code}" )
                    raise SystemExit()
                else:   # Success
                    break
        if verb == 'GET':
            return json.loads(resp.text)
        else:
            return None

    # Returns the time since epoch as reported by the DERMS
    # Exception handling missing here.  Needs to be added.
    def getTime(self):
        endpoint = self.dermsURL + EP_TIME
        return self._doHTTP('GET', endpoint )

    # Get the Device Capability structure from the DERMS
    def getDevCap(self):
        endpoint = self.dermsURL + EP_DEVCAP
        dict = self._doHTTP('GET', endpoint)
        return DeviceCapability(dict)

    # Get the Default DER Control structure
    def getDDERC(self):
        endpoint = self.dermsURL + EP_DERPGM + EP_DDERCTL
        dict = self._doHTTP('GET', endpoint)
        return DefaultDERControl(dict)

    # Send the DERCapabilities to the DERMS.
    def sendDERCap(self, derCap):
        endpoint = self.dermsURL + EP_END_DEVICE + EP_DER + EP_DERCAP
        self._doHTTP('PUT', endpoint, derCap.toDict())
        return None

    def sendDERSettings(self, derSettings):
        endpoint = self.dermsURL + EP_END_DEVICE + EP_DER + EP_DERSETTINGS
        self._doHTTP('PUT', endpoint, derSettings.toDict())
        return None
