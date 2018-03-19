#!/usr/bin/env python3

import time
import requests
import datetime

while True:
  for n in ['cdn01', 'cdn02', 'cdn03', 'cdn04', 'cdn05']:
    time.sleep(3)
    url = "http://" + n + '/cdn/' + str(datetime.datetime.now().second)
    print(url)
    r = requests.get(url)
