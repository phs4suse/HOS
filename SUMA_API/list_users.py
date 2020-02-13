#!/usr/bin/env python3
from xmlrpc.client import ServerProxy

# Update this!!
MANAGER_URL = "http://FQDN/rpc/api"
MANAGER_LOGIN = ""
MANAGER_PASSWORD = ""

client = ServerProxy(MANAGER_URL)
key = client.auth.login(MANAGER_LOGIN, MANAGER_PASSWORD)

print(client.user.list_users(key))
client.auth.logout(key)
