#!/usr/bin/env python3

import time
import requests
import datetime

time.sleep(5)
while True:
  for n in ['cdn01', 'cdn02', 'cdn03', 'cdn04', 'cdn05']:
    time.sleep(2)
    url = "http://" + n + '/cdn/' + str(datetime.datetime.now().second)
    print(url)
    r = requests.get(url)
