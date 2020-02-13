#!/usr/bin/env python3
## Author: Steve Brown

from xmlrpc.client import ServerProxy

import datetime
import time
import ssl

# Update this!!
MANAGER_URL = "http://FQDN/rpc/api"
MANAGER_LOGIN = ""
MANAGER_PASS = ""

# Connect to SUMA
client = ServerProxy(MANAGER_URL)       # If you have a valid SSL cert for SUMA or no SSL
#client = ServerProxy(MANAGER_URL,None,verbose = False,use_datetime = True,use_builtin_types = True,context=ssl._create_unverified_context())   # If you don't have a valid SSL cert for SUMA

# Login
key = client.auth.login(MANAGER_LOGIN, MANAGER_PASS)

clientServerName = 'szsles12sp3b.susezoom.com'                                          # Client Server Name goes here
newKickstartName = 'sle15sp1'                                   # Kickstart profile name goes here, not the Label
registerCommand = 'curl -Sks http://hkdsuma4.susezoom.com/pub/bootstrap/bootstrap-15sp1.sh |/bin/bash'  # Command to be run to re-register the system
whenToStart = datetime.datetime.now()   # Scheduled start time for distro upgrade action
pollingInterval = 15                                    # Interval (in seconds) for polling action status

# Verify Kickstart profile exists
allKickstarts = client.kickstart.listKickstarts(key)
if not any(ks for ks in allKickstarts if ks['name'] == newKickstartName):
        print('Kickstart not found')
        raise SystemExit
theKs = [ ks for ks in allKickstarts if ks['name'] == newKickstartName ][0]

results = client.system.getId(key, clientServerName)
if len(results) == 0:
        print ('Server not found')
else:
        theSystem = results[0]
        print(theSystem)
        actionId = client.system.scheduleDistUpgrade(key, theSystem['id'], ['sles-15-sp1-chan...', 'sles-15-sp1-chan2', '...'], False,whenToStart)
        #actionId = client.system.scheduleScriptRun(key, theSystem['id'], 'root', 'root', 600, 'ls -al', whenToStart)
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ': Upgrade action scheduled for server ' + theSystem['name'] + '.  Waiting for action to completion...')

        # Loop until action is completed
        completedServers = client.schedule.listCompletedSystems(key, actionId)
        while len(completedServers) == 0:
                print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ':    Action not complete...')
                time.sleep(pollingInterval)
                completedServers = client.schedule.listCompletedSystems(key, actionId)

        print()
        print (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ': Upgrade complete!')

        # Schedule the reboot action
        actionId = client.system.scheduleReboot(key, theSystem['id'], datetime.datetime.now())
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ': Reboot action has been scheduled.  Waiting for action to complete...')
        completedServers = client.schedule.listCompletedSystems(key, actionId)
        while len(completedServers) == 0:
                print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ':    Action not complete...')
                time.sleep(pollingInterval)
                completedServers = client.schedule.listCompletedSystems(key, actionId)
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ': Reboot completed!')

        # Schedule script to re-register the system
        actionId = client.system.scheduleScriptRun(key, 'Re-Register system in SUMA', theSystem['id'], 'root', 'root', 600, registerCommand, datetime.datetime.now())
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ': Register action submitted to server.  Waiting for action to complete...')
        completedServers = client.schedule.listCompletedSystems(key, actionId)
        while len(completedServers) == 0:
                print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ':      Action not complete...')
                time.sleep(pollingInterval)
                completedServers = client.schedule.listCompletedSystems(key, actionId)
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ': Register completed!')

        # Schedule package refresh
        actionId = client.system.schedulePackageRefresh(key, theSystem['id'], datetime.datetime.now())
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ': Package refresh scheduled.  Waiting for action to complete...')
        completedServers = client.schedule.listCompletedSystems(key, actionId)
        while len(completedServers) == 0:
                print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ':      Action not complete...')
                time.sleep(pollingInterval)
                completedServers = client.schedule.listCompletedSystems(key, actionId)
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ': Refresh completed!')

# Disconnect
client.auth.logout(key);
