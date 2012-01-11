#!/usr/bin/env python

# __Author : Romaric Philogene
# __Date : 6th January 2012
# __Description : conf module for fab2puppet is used to load configuration file.

import sys, ConfigParser

class Conf(object):
	""" Class used to load variables from fab2puppet configuration file.
	"""
	def __init__(self):
		"""
		"""
		try:
			self.config = ConfigParser.RawConfigParser()
			self.config.read('fab2puppet.conf')
	
			self.puppet_server = self.config.get('manager','puppet_server')
			self.domain = self.config.get('manager','domain')
			self.re_domain = self.config.get('manager','re_domain')
			self.friendly_user = self.config.get('manager','friendly_user')
	
			self.smtp_server = self.config.get('log','smtp_server')
			self.smtp_port = self.config.get('log','smtp_port')
			self.mail_notification = self.config.get('log','mail_notification')
			self.mail_sender = self.config.get('log','mail_sender')
			self.mail_receiver = self.config.get('log','mail_receiver')
	
			self.log_directory = self.config.get('log','log_directory')
			self.file_log_name = self.config.get('log','log_file')
	
			self.multiexecution = self.config.get('multi_execution','use_multiexecution')
			self.threads_number = self.config.get('multi_execution','number_of_threads')
	
			self.logfile = ('%s/%s' % (self.log_directory,self.file_log_name))
	
			if self.friendly_user != 'yes' and self.friendly_user != 'no':
				self.error('friendly_user')
			elif self.friendly_user == 'no':
				self.friendly_user = False
			else:
				self.friendly_user = True
	
			if self.multiexecution != 'yes' and self.multiexecution != 'no':
				self.error('use_multiexecution')
			elif self.multiexecution == 'yes':
				self.multiexecution = True
				self.friendly_user = False
			else:
				self.multiexecution = False
	
			if self.multiexecution:
				if self.threads_number < 0 and self.threads_number > 5:
					print '[-]--> Thread numbers must be between 0 and 5'
					sys.exit(1)
	
			if self.mail_notification != 'yes' and self.mail_notification != 'no':
				self.error('mail_notification')
			
		except Exception, e:
			print 'Conf error:', e


	def error(self,err):
		"""
		"""
		print '[-]--> Conf err: use \'yes\' or \'no\' for', err
		sys.exit(1)

