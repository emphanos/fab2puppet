#!/usr/bin/env python

# __Author : Romaric Philogene
# __Date : 22th December 2011
# __Description : Module to list hosts from puppet host.

import subprocess

from fabric.api import run, env

class Lists(object):
	""" Class to list hosts linked to puppet master.
	"""
	def __init__(self):
		"""
		"""

	def lists(self):
		""" This method invoke local execution of 'puppetca -la' to list linked hosts.
		"""
		
		print('\n---> name prefixed by \'+\' are already linked to the master by SSL\n')
		
		try:
			clientListPipe = subprocess.Popen(['/usr/sbin/puppetca','-la'], stdout=subprocess.PIPE)
			print clientListPipe.communicate()[0]

		except Exception:
			print Exception
			pass

