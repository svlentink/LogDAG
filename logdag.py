#!/usr/bin/env python3

import os
from flask import Flask
from flask import request
import requests
import time
import datetime
app = Flask(__name__)
#from scenarios import *

# settings
config = {
  'links' : 2, # the amount of links a block will require
  'nodes' : [ 'cdn01', 'cdn02', 'cdn03', 'cdn04', 'cdn05'],
  'logdir' : '/var/log/LogDAG',
  'blockdir' : '/var/log/blocks',
  'hostname' : os.environ['HOSTNAME']
}

# global variables
LogDAG = []
crontime = ''

def init():
  if config['links'] > len(config['nodes']):
    raise Exception('config.links should be lower than config.nodes.length')
  # Adding genesis blocks
  for i in range(config['links']):
    nodename = config['nodes'][i]
    genesis = get_block_metadata('genesisBlock' + str(i), nodename)
    global LogDAG
    LogDAG.append(genesis)

def get_block_metadata(blockid : str, hostname: str = config['hostname'], validates = []):
  millis = int(round(time.time() * 1000))
  return {
    'blockid' : blockid,
    'hostname' : hostname,
    'time' : millis,
    'validates' : validates
  }


def cron():
  '''
  This function rotates the logs,
  which should be done by /etc/cron.d
  however, for this research, we do it here
  so we can see it in the logs
  '''
  now = datetime.datetime.now()
  arr = now.isoformat().split(':')
  timestr = arr[0] + '_' + arr[1]
  
  global crontime
  if crontime != timestr:
    if len(crontime):
      metadata = create_block()
      broadcast_metadata(metadata)
    crontime = timestr
    print('Log rotated')

def create_block():
  '''
  What this function should actually do (but we mock for now):
  mv the file, (so no new logs are added)
  calculate the hash based on the nodes it links to and
  '''
  validates = which_to_validate()
  blockid = config['hostname'] + str(datetime.datetime.now()) # TODO, this should be an hash of the encrypted block

  global crontime
  filename = config['logdir'] + '/' + crontime
  blockname = config['blockdir'] + '/' + blockid
  os.rename(filename,blockname)

  metadata = get_block_metadata(blockid, validates=validates)
  return metadata

def broadcast_metadata(metadata):
  for i in config['nodes']:
    url = "http://" + i + '/block/metadata'
    r = requests.post(url, data=metadata)
    print(r.status_code, r.reason)

def which_to_validate():
  '''
  This function should contain a nice algorithm that specifies
  which blocks it will link to, based on some way of assigning
  weight to blocks.
  However, we just take the last n blocks for now.
  '''
  global LogDAG
  n = config['links']
  return LogDAG[(-1*n):]

@app.route('/cdn/<int:inp>', methods=['GET'])
def cdn(inp):
  '''
  This function simulates a webserver or cdn.
  We use this instead of Nginx so we can use custom logging
  and trigger the cron function.
  '''
#  print(request) # debug

  cron()

  global crontime
  filename = config['logdir'] + '/' + crontime
  with open(filename, 'a') as f:
    f.write(str(inp) + '\n')

  return(inp,200)


@app.route('/block/<blockid>', methods=['GET'])
def get_block(blockid):
  '''
  This function returns a block based on its ID,
  which can be found in the LogDAG
  '''
#  print(request) # debug

  filename = config['blockdir'] + '/' + blockid
  with open(filename, 'r') as f:
    block = f.read()

  return(block,200)

@app.route('/block/metadata', methods=['POST'])
def put_block_metadata():
  data = request.form
  global LogDAG
  LogDAG.append(data)
  return(data,200)

if __name__ == '__main__':
  init()
  app.run(debug=True, port=80, host=config['hostname'])
