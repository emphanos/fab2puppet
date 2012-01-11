#!/usr/bin/env python

# __Author : Romaric Philogene
# __Date : 22th December 2011
# __Description : Module with common instructions.

import os, sys, subprocess, datetime, re, string

from conf import Conf
from fabric.api import run, env
from fabric.context_managers import hide


class Common(object):
	""" This class regroup several things commonly used by different instance
	"""
	def banner(self):
		if os.getuid() != 0:
			print '\n' + '-'*60
			print '<=== be sure to launch this command with local admin rights ===>'
			print '-'*60 + '\n'
			quit_execution()
		else:
			pass

	def quit_execution(self):
		""" Quit program execution
		"""
		quit = raw_input('Do you want to quit ? (y/n) ')
		if(quit == 'y' or quit == 'yes'):
			sys.exit(0)
		else:
			if(quit == 'n' or quit == 'no'):
				pass
			else:
				print('use \'yes\' or \'no\' only\n')
				quit_execution()

	def client_hosts(self):
		"""
		"""
		env.user = 'root'
		env.warn_only = True

	def client_name(self):
		"""
		"""
		with hide('running','stderr','stdout'):
			return run('hostname')

class Hostname(Conf):
	""" This class check if a host is correctly set
	"""
	def __init__(self):
		"""
		"""
		Conf.__init__(self)

	def check(self):
		"""
		"""
		c = Common()
		fileToCheck = ['/etc/hostname','/etc/hosts']

		hostname = c.client_name()
		with hide('running', 'stderr', 'stdout'):
			hostnameFile = run('/bin/cat /etc/hostname')
			hostsFile = run('/bin/cat /etc/hosts')

		splitHostsFile = string.split(hostsFile,'\n')

		if(re.search(r'^127\.0\.0\.1.*localhost.*', splitHostsFile[0])):
			pass
		else:
			print '"/etc/hostname" file from %s seems to be wrong' % c.client_name()
			sys.exit(1)
			
		if(re.search(r'127\.0\.1\.1.*%s\.%s.*%s.*' % (hostname,self.re_domain,hostname), splitHostsFile[1])):
			pass
		else:
			print '"/etc/hosts" file from %s seems to be wrong' % c.client_name()
			sys.exit(1)

