#!/usr/bin/python

# __Author : Romaric Philogene
# __First release Date : 25th November 2011
# __Update : 23th December 2011
# __Description : Script to deploy puppet client over ssh on linux OS.
# __Prerequisites : fabric library, paramiko, and all standard python library like os, sys, subprocess..
# __Prerequisites 2 : dbcollect to import hosts data inside a sqlite db.

from include.dbcollect import DBcollect
from include.lists import Lists
from include.manager import _Update,_Puppet
from include.common import Common

def list_hosts():
	c = Common()
	c.banner()
	hostsList = Lists()
	hostsList.lists()

def update(client,noop):
	c = Common()
	c.banner()
	c.client_hosts()

	up = _Update(client,noop)

def puppet(client,choice):
	c = Common()
	c.banner()
	c.client_hosts()

	pup = _Puppet(client,choice)

if __name__ == "__main__":

	print """
-------------------------------------------------------------------------------------------------'
Fab2Puppet could not be launch as standalone application.
Please use command line as below.

Commands:'

This command install puppet on the hostname and link it to the master.'
	--> fab puppet:specific_host,install

This command remove puppet on the hostname and remove certs on the client and the master.'
	--> fab puppet:specific_host,remove

If you just want to restart puppet agent on the client side.'
	--> fab puppet:specific_host,restart

This command list host(s) linked to the master.'
	--> fab list_hosts

This command show every changes on all hosts without applying it.'
	--> fab update:all,noop

This command apply every changes on all hosts.'
	--> fab update:all,apply

If you want watch/apply changes on hosts with regex.'
	ex : I want to see changes on host-dev, host-prod, host-poc without making them.

	--> fab update:host.*,noop

If you want to show/apply changes on a specific host.'
	--> fab update:specific_host,noop
	--> fab update:specific_host,apply

-----------------------------------------------------------------------------------------------'
		"""