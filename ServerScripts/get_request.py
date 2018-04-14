import requests
import math
import numpy

import json

myheaders = {"Authorization":"Bearer 57:3996aa851ea17f9dd462969c686314ed878c0cf7"}

url = 'http://glenlivet.inf.ed.ac.uk:8080/api/v1/svc/apps/data/docs/everything'
endpoint = "http://glenlivet.inf.ed.ac.uk:8080/api/v1/svc/ep/get"

#payload = {"timestamp": "value1", "rssi": "value2", "device_mac": "value 3"}
r = requests.get(url, headers=myheaders)
print(r.text)
print(r.json())
print(math.pow(2,3))

"""
for i in range(10):
    r = requests.get(endpoint, headers=myheaders)
    print(r.text)

r = requests.get(url, headers=myheaders)
print(r.text)

payload = {'key1': 'value1', 'key2': 'value2'}

r = requests.post(url, headers=myheaders, data=payload)
print(r.text)

r = requests.get(endpoint, headers=myheaders)
print(r.text)
"""

