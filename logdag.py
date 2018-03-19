#!/usr/bin/env python3

import os
import shutil
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

def get_current_logfile():
  global crontime
  filename = config['logdir'] + '/' + crontime
  return filename

def create_block():
  '''
  What this function should actually do (but we mock for now):
  mv the file, (so no new logs are added)
  calculate the hash based on the nodes it links to and
  '''
  validates = which_to_validate()
  blockid = config['hostname'] + str(datetime.datetime.now().timestamp()) # TODO, this should be an hash of the encrypted block

  global crontime
  filename = get_current_logfile()
  blockname = config['blockdir'] + '/' + blockid
  shutil.move(filename,blockname)
  backup_DAG()

  metadata = get_block_metadata(blockid, validates=validates)
  return metadata

def broadcast_metadata(metadata):
  for i in config['nodes']:
    if i == config['hostname']:
      global LogDAG
      LogDAG.append(metadata)
    else:
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
  arr = LogDAG[(-1*n):]
  ids = []
  for i in arr:
    ids.append(i['blockid'])
  return ids

@app.route('/cdn/<int:inp>', methods=['GET'])
def cdn(inp):
  '''
  This function simulates a webserver or cdn.
  We use this instead of Nginx so we can use custom logging
  and trigger the cron function.
  '''
#  print(request) # debug

  cron()

  filename = get_current_logfile()
  with open(filename, 'a') as f:
    f.write(str(inp) + '\n')

  return str(inp)


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

  return block

@app.route('/block/metadata', methods=['POST'])
def put_block_metadata():
  data = request.form
  global LogDAG
  print(data)
  LogDAG.append(data)
  backup_DAG()
  return str(data)

def backup_DAG():
  global LogDAG
  filename = config['blockdir'] + '/' + 'logdag.bak'
  with open(filename, 'w') as f:
    f.write(str(LogDAG))

if __name__ == '__main__':
  init()
  app.run(debug=True, port=80, host=config['hostname'])
