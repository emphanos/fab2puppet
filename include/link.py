#!/usr/bin/env python

# __Author : Romaric Philogene
# __Date : 6th January 2012
# __Description :

from conf import Conf
from common import Common, Hostname
from logger import Logger

from fabric.api import run, env
from fabric.contrib.files import exists, contains
from fabric.context_managers import hide

from time import sleep
import threading, string, re, subprocess

# ______________________________________________________


class ValidCert(threading.Thread,Conf):
	""" Threading class to valid certificate.
	"""
	def __init__(self):
		"""
		"""
		Conf.__init__(self)
		threading.Thread.__init__(self)

	def run(self):
		"""
		"""
		c = Common()

		sleep(3)
		subprocess.call(['/usr/sbin/puppetca', '--sign', '%s.%s' % (c.client_name(),self.domain)])


class AddCert(threading.Thread,Conf):
	""" Threaded class to push certification request from client to master.
	"""
	def __init__(self):
		"""
		"""
		Conf.__init__(self)
		threading.Thread.__init__(self)

	def checkCertificate(self):
		""" Method used to check if the host is already linked on master on not.
		return 'False' or 'True'.
		"""
		c = Common()

		try:
			checkCert = subprocess.Popen(['/usr/sbin/puppetca', '-la'],stdout=subprocess.PIPE)
			checkCertPIPE = checkCert.communicate()[0]
			clientCert = re.search('.*\+.*%s\.%s' % (c.client_name(),self.re_domain), checkCertPIPE)

		except Exception, e:
			print 'error :', e

		return clientCert

	def run(self):
		""" Method used to validate the certificats and update the puppet client.
		"""
		c = Common()
		result = self.checkCertificate()

		l = Logger(c.client_name())

		try:
			if result:
				with hide('warnings','stderr'):
					print '\n[+]--> %s is already linked to the master <--\n' % c.client_name()

					if exists('/etc/.hg'):
						print '[+]--> Configuration files is going to be saved by etckeeper <--\n'
						run('/usr/sbin/etckeeper commit \"Commit by puppet\"')

					runCacher = run('puppet agent --server %s --test' % self.puppet_server)
					runSplit = string.split(runCacher,'\n')

					for runLine in runSplit:
						fullString = '%s - %s' % (c.client_name(),runLine)
						l.logx(fullString)

					l.logx('-'*70)

			else:
				print '\n[-]--> %s is not linked to the master\n' % c.client_name()

				validcertificate = ValidCert()
				validcertificate.start()

				with hide('warnings'):
					run('puppet agent --server %s --waitforcert 3 --test' % self.puppet_server)

				validcertificate.join()

		except Exception, e:
			print 'error :', e

