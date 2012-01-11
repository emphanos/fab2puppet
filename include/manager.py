#!/usr/bin/env python

# __Author : Romaric Philogene
# __Date : 22th December 2011
# __Description : Module to manage puppet.

from conf import Conf
from common import Common, Hostname
from logger import Logger
from link import ValidCert, AddCert

from fabric.api import run, env
from fabric.contrib.files import exists, contains
from fabric.context_managers import hide

from time import sleep
import os, string, sys, re, subprocess

# ______________________________________________________


class _Puppet(Conf):
	""" Class to manage puppet client.
	This is the class initiated to install, remove puppet client.
	"""
	def __init__(self,hostAddr=None,choice=None):
		"""
		"""
		Conf.__init__(self)

		logfile = self.logfile

		self.__choice = choice
		self.__host = hostAddr
		self.__counter = 0

		env.host_string = self.__host

		if choice is None:
			print 'install or remove puppet ?'

		elif choice == 'install':
			self.install()

		elif choice == 'remove':
			self.remove()

		elif choice == 'restart':
			self.restart()

	def install(self):
		""" Method used to install, link, update puppet client.
		"""
		c = Common()
		c.banner()
		c.client_hosts()

		hostname = Hostname()
		hostname.check()

		l = Logger(c.client_name())

		reader = open(self.logfile)
		startline = len(reader.readlines())

		l.event_counter(startline)

		try:
			operatingSystem = run("/bin/cat /etc/issue | /usr/bin/awk '{print $1}'")

			if(operatingSystem=='Debian'):
				run('aptitude -y update && aptitude -y install puppet')
			else:
				print '--->\tOS not supported'
				sys.exit(0)

			puppetthread = AddCert()
			puppetthread.start()

			puppetthread.join()

		except Exception, e:
			print 'error :', e

		exit(0)

	def remove(self):
		""" Method used to remove puppet, erase custom facts on puppet client.
		"""
		c = Common()
		c.banner()
		c.client_hosts()

		operatingSystem = run("/bin/cat /etc/issue | /usr/bin/awk '{print $1}'")

		if(operatingSystem=='Debian'):
			run('aptitude -y purge puppet')
			run('find /var/lib/puppet -type f -print0 | xargs -0r rm')
		else:
			print '--->\tOS not supported'
			sys.exit(0)

		try:
			subprocess.call(['/usr/sbin/puppetca', '--clean', '%s.%s' % (c.client_name(),self.domain)])
		except Exception, e:
			print 'error :', e
			pass

		sleep(3)
		exit(0)

	def restart(self):
		""" Method used to restart puppet client.
		"""
		run('/etc/init.d/puppet restart')

class _Update(Conf):
	""" This class is used to update puppet client.
	"""
	def __init__(self,hostaddr=None,noop='noop'):
		"""
		"""
		Conf.__init__(self)

		logfile = self.logfile

		c = Common()
		c.banner()
		c.client_hosts()

		self.__host=hostaddr
		self.__noop=noop
		self.__counter = 0
		self.__exclude = 0

		self.__reader = open(logfile)
		self.__startline = len(self.__reader.readlines())
		self.__reader.close()

		l = Logger('initiator')
		l.logx('-'*70)

		if self.__host=='all':
			l.logx('Update command on all hosts executed')
			self.update_all()
			l.event_counter(self.__startline)

		elif re.match(r'^\.\*$',self.__host):
			print '\n[-]--> please use \'all\' instead of \'.*\'\n'

		elif re.match(r'.*[\.\*\+\[\]]+.*',self.__host):
			l.logx('Update regex command (%s) executed' % self.__host)
			self.reget_host()
			l.event_counter(self.__startline)

		else:
			l.logx('Update command on %s executed' % self.__host)
			env.host_string=self.__host
			self.update_host()
			l.event_counter(self.__startline)

		l.logx('End of execution')

	def matches_hosts(self,matcher):
		""" Method used to show matches hosts on stdout.
		"""
		self.__counter = 0

		if self.multiexecution is False:
			print 'You are going to apply changes on :\n'

		for re_host in matcher:
			self.__counter +=1
			if self.multiexecution is False:
				print '[%d]--> %s' % (self.__counter,re_host)

	def exclude_host(self,matcher):
		""" Method used to exclude host(s).
		"""
		self.__exclude = 1
		self.__counter = 0

		str_element = raw_input('\nWhich host(s) do you want to exclude (exemple : 1,3 to exclude host 1 and 3) ?\n')

		if re.match('.*,.*',str_element):
			separate_element = string.split(str_element,',')

			for element in separate_element:

				intelement = int(element)
				intelement -= 1

				result = intelement - self.__counter

				del matcher[result]
				self.__counter += 1

		else:
			single_element = int(str_element)
			single_element -= 1
			del matcher[single_element]

		return matcher

	def reget_host(self):
		""" Method used to match hosts with regex and then apply/noop updates.
		"""
		try:
			clientListPipe = subprocess.Popen(['/usr/sbin/puppetca','-la'], stdout=subprocess.PIPE)
			clientList = clientListPipe.communicate()[0]
			pattern = re.compile(r'\+ (%s)\.%s' % (self.__host,self.re_domain))
			matcher = re.findall(pattern,clientList)

			if self.__noop=='apply':

				self.matches_hosts(matcher)

				if self.friendly_user:

					if len(matcher)==0:
						print '[-]--> No matches'
						sys.exit(0)

					exclude = raw_input('\nDo you want to exclude any of these hosts ?\n')

					if (exclude=='yes' or exclude=='y'):
						matcher = self.exclude_host(matcher)

					if self.__exclude:
						self.matches_hosts(matcher)

					confirm = raw_input('\nAre you sure ? (y/n)\n')

					if (confirm=='yes' or confirm=='y'):
						pass
					else:
						sys.exit(0)

			else:
				print 'Your regex match :\n'

				for re_host in matcher:
					self.__counter +=1
					print '[%d]--> %s' % (self.__counter,re_host)
				print '\n' + '-'*60 + '\n'

			for re_host in matcher:

				if re.match(r'(^DNS:|%s)' % self.puppet_server,re_host):
					pass

				else:
					self.__host = re_host
					env.host_string = self.__host
					self.update_host()


		except Exception, e:
			print 'error :', e

	def noop_puppet(self):
		""" Method used for only showing changes without applying them.
		"""
		try:
			run('puppet agent --server %s --test --noop' % self.puppet_server)
			print '\n' + '-'*60 + '\n'

		except Exception, e:
			print 'error :', e

	def update_host(self):
		""" Method used to apply/noop updates on a specific host.
		"""
		c = Common()
		l = Logger(c.client_name())

		try:

			if self.__noop!='apply':
				self.noop_puppet()

			else:
				updatePuppet = AddCert()
				updatePuppet.start()
				updatePuppet.join()

				print '\n' + '-'*60 + '\n'
				return 0

		except Exception, e:
			print 'error :', e

	def update_all(self):
		""" Method used to apply/noop updates on all linked hosts.
		"""

		try:
			clientListPipe = subprocess.Popen(['/usr/sbin/puppetca','-la'], stdout=subprocess.PIPE)
			clientList = clientListPipe.communicate()[0]
			pattern = re.compile(r'(\S+)\.%s' % self.re_domain)
			matcher = re.findall(pattern,clientList)

			for result in matcher:
				if re.match(r'^DNS:',result):
					pass

				else:

					host = '%s' % result
					self.__host = host
					env.host_string = host
					self.update_host()

		except Exception, e:
			print 'error :', e
