#!/usr/bin/env python

# __Author : Romaric Philogene
# __Date : 4th January 2012
# __Description : logger module is used to log fab2puppet execution

import logging, os, linecache, re, smtplib, StringIO, codecs

from common import Common
from fabric.api import env
from conf import Conf

from email.MIMEText import MIMEText

class Logger(Conf):
	""" Class used to log execution events
	"""
	def __init__(self,loghandler):
		"""
		"""
		Conf.__init__(self)

		self.__counterr = 0
		self.__countwarn = 0
		self.__notification_required = False

		self.__logger = logging.getLogger(loghandler)

		if not self.__logger.handlers:
			self.__hdlr = logging.FileHandler(self.logfile)
			self.__formatter = logging.Formatter('%(asctime)s [%(levelname)s] : %(message)s')
			self.__hdlr.setFormatter(self.__formatter)
			self.__logger.addHandler(self.__hdlr)
			self.__logger.setLevel(logging.INFO)

	def logx(self,method):
		""" Method used to write log from handler.
		"""
		if os.path.isfile(self.logfile):
			output = self.remove_color(method)
			self.__logger.info(output)

		else:
			newFile = open(self.logfile, 'w')
			newFile.write('\n')
			newFile.close()
			self.log(method)

	def notification(self,level,line):
		""" Method used to mail notify.
		"""
		try:
			msg = self.remove_color(line)

			mail = MIMEText(msg)

			mail['From'] = self.mail_sender
			mail['Subject'] = '[Fab2Puppet] %s report' % level
			mail['To'] = self.mail_receiver

			smtp = smtplib.SMTP()
			smtp.connect(self.smtp_server,self.smtp_port)

			smtp.sendmail(self.mail_sender,[self.mail_receiver],mail.as_string())

			smtp.close()

		except Exception, e:
			print 'mail notification error :', e

	def event_counter(self,startline):
		""" Method used to count warnings and errors from execution.
		"""
		reader = open(self.logfile)

		start = int(startline)
		end = len(reader.readlines())
		reader.close()

		streamOutput = StringIO.StringIO()

		while start != end:
			line = linecache.getline((self.logfile), start)
			if re.match(r'.*err:.*',line):
				self.__counterr += 1
				self.__notification_required = True
				if(self.mail_notification == 'yes'):
					streamOutput.write(line)

			elif re.match(r'.*warning:.*',line):
				self.__countwarn += 1
				self.__notification_required = True
				if(self.mail_notification == 'yes'):
					streamOutput.write(line)

			start += 1

		if self.__notification_required:
			self.notification('Error(s)',streamOutput.getvalue())

		print 'Warning(s) during execution :', self.__countwarn
		print 'Error(s) during execution :', self.__counterr

	def remove_color(self,input):
		"""
		"""
		pattern = re.compile('\033\[[0-9;]+m')
		output = re.sub(pattern,'',input)

		return output

	def log_parser(self):
		"""
		"""
		self.event_counter('0')

if __name__ == "__main__":
	"""
	"""
	c = Common()
	env.host_string='puppet-client'

	l = Logger(c.client_name())
	l.log_parser()
