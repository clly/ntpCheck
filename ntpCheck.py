#############################################################
#
#	ntpCheck.py: checks both internal and external NTP servers to 
#			ensure the time is correct
#
#	Library's needed: ntplib, random, smtplib, socket, ctime, MIMEText
#
#	ntplib can be found here: http://pypi.python.org/pypi/ntplib/
#
#	Changelog:
#			Creation by Connor Kelly on 3/7/2012
#
#		access policy for external NTP servers at last edit
#			us.pool.ntp.org: open as far as I know, NTP pool
#			clock.isc.org : Open access				Stratum 1
#			nist1.uccaribe.edu : Open access, Acerage min poll:	16 seconds, Stratum 1
#			timekeeper.isi.edu: open access			Stratum 1
#			t2.timegps.net : open access			Stratum 1
#			time.xmission.com : Open access			Stratum 1
#			tick.jpunix.net : Open access			Stratum 2
#			ntp.fwwds.com : Open access				Stratum 2
#			ntppub.tamu.edu : Open access			Stratum 2
#		Information from:	 support.ntp.org
#############################################################


import ntplib, random, smtplib, socket, sys, os, getopt		#used for random numbers, ntp messages, and sending email
from time import ctime							#used to change seconds from a date into human readable
from email.mime.text import MIMEText			#used to create email message
from os import path

class NTPInfo:
	def __init__(self):
		config = self.readConfig()
		self.extServers = config['externalNTP']
		self.intServers = config['internalNTP']
		self.external = random.sample(self.extServers, 1)[0].strip()
		self.internal = random.sample(self.intServers, 1)[0].strip()
		self.dc = config['dc'][0].strip()
		self.intResp = ""
		self.extResp = ""
		self.dcResp = ""
		self.intTime = 0
		self.extTime = 0
		self.dcTime = 0
		self.limit = int(config['limit'][0])
		self.accptOffset = float(config['accptOffset'][0])
		self.dstEmail = config['dstEmail']
		self.smtp = config['smtpServer'][0].strip()
	
	def readConfig(self, fn='ntpCheck.config'):
		fn = 'ntpCheck.config'
		conf = {}

		with file(fn) as fp:
			for line in fp:
				if not line or line.startswith('#'): continue
				str = line.strip()
				ar = str.split(':', 1)
				if(len(ar) == 2):
					conf[ar[0]] = ar[1].split(',')
		
		return(conf)
	
	def connect(self):
		"""Connects to ntp servers and ensures connection is successful"""
		bool = True
		ret = 0
		client = ntplib.NTPClient()
		message = ""
		count = 1
		limit = self.limit
		while(count <= limit and bool):
			count += 1
			try:
				self.extResp = client.request(self.external, version=3)
				bool = False
			except (socket.timeout, socket.error):
				self.external = random.sample(self.extServers, 1)[0]
				message += "Unable to contact external NTP server " + self.external + "\n\r"
			try:
				self.intResp = client.request(self.internal, version=3)
			except (socket.timeout, socket.error):
				message = "Unable to contact internal NTP server " + self.internal + "\n"
				ret = 1
				bool = True
				break
			try:
				self.dcResp = client.request(self.dc, version=3)
			except (socket.timeout, socket.error):
				message = "Unable to contact domain controller " + self.dc + "\n"
				ret = 1
				bool = True
				break
		if(count <= limit and not bool):
			self.intTime = self.intResp.recv_time
			self.extTime = self.extResp.recv_time
			self.dcTime = self.dcResp.recv_time
		return (ret, message)

	def sendEmail(self, message, subject="The Time Is Off!!"):
		fromaddr = 'WGHNTPWatch@wyman.com'				#service account emails are coming from
		toaddrs  = self.dstEmail		#people that need to be notified
		
		msg = MIMEText(message)			#creates the email with the message (body of the email) as an argument

		msg['Subject'] = subject		#subject of the email
		msg['From'] = fromaddr						#service account sending the email
		
		tostr = ""
		for i in range(len(toaddrs)):			#checks if there are more than one person receiving the message
			if(len(toaddrs) > 1):				#		and formats it appropriately 
				if(i != len(toaddrs) - 1):
					tostr += toaddrs[i] + ", "
				else:
					tostr += toaddrs[i]
			else:
				msg['To'] = toaddrs[0]

		msg['To'] = tostr
		# The actual mail send process
		server = smtplib.SMTP(self.smtp)
		a = server.sendmail(fromaddr, toaddrs, msg.as_string())	#sends the mail
		server.quit()		#also required

def main():
	info = NTPInfo()
	ret, msg = info.connect()
	if(ret):
		info.sendEmail(msg, subject="Unable to contact an internal server")
		sys.exit(0)
	elif(msg):
		info.sendEmail(msg, subject="Unable to contact an external NTP Server")
	s = False

	accptOffset = info.accptOffset		# acceptable offset in seconds.  Set as negative because of absolute value
	offset = info.intTime - info.extTime
	dcOffset = info.dcTime - info.extTime

	if(offset < accptOffset or offset > abs(accptOffset)):
		message = "\nThe internal NTP server " + info.internal + " is off by " + str(offset) + " from " \
			+ info.external + "\r\tOffset: " + str(offset) + "\n\tInternal Time: " + ctime(info.intTime) \
			+ "\n\tExternal Time: " + ctime(info.extTime) + "\n"
		s = True
	else:
		message = "\nThe internal NTP server " + info.internal + " is at an acceptable offset by " + str(offset) + " from " \
		+ info.external + "\n\tOffset: " + str(offset) + "\n\tInternal Time: " + ctime(info.intTime) \
		+ "\n\tExternal Time: " + ctime(info.extTime) + "\n"
	if(dcOffset < accptOffset or dcOffset > abs(accptOffset)):
		message += "\nThe time for domain controller " + info.dc + " is off by " + str(dcOffset) + " from "\
			+ info.external + "\n\tOffset: " + str(dcOffset) + "\n\tExternal time: " \
			+ ctime(info.extTime).center(27) + "\n\tDC Time: " + ctime(info.dcTime)
		s = True
	else:
		message += "\nThe domain controller time " + info.dc + " is at an acceptable " \
			+ "offset externally" + "\n\tOffset: " + str(dcOffset) + "\n\tExternal time: " \
			+ ctime(info.extTime).center(27) + "\n\tDC Time:\t " + ctime(info.dcTime)
	if(s):
		info.sendEmail(message)

def printConf():
	fn = 'ntpCheck.config'
	conf = {}

	print("\nConfiguration File Contents:\n")

	with file(fn) as fp:
		for line in fp:
			if not line or line.startswith('#'): continue
			str = line.strip()
			print("\t" + str)
		
if __name__ == '__main__':
	config = "ntpCheck.config"

	try:
		opts, args = getopt.getopt(argv, "hcC:", ["help", "show-config", "Config"])
	except: getopt.GetoptError:
		usage()
		sys.exit(2)

	if(path.exists(config)):
		if("-c" in sys.argv):
			printConf()
			sys.exit(0)
		else:
			main()
	else:
		print("Configuration file does not exists, try again")