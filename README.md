ntpCheck
========

checks internal and external ntp sources to ensure the time is correct

Usage
-----
	ntpCheck.py -c
		prints current configuration settings
	
	ntpCheck.py


Configuration File
------------------

All entries are the name of the variable seperated by a colon.  All entries are taken in as a list but in the case of a single requested value it will only take the first entry.  All lists are separated by commas.

	### externalNTP
	A list of external NTP servers to check against

	### internal NTP
	A list of internal NTP servers to check

	### dc
	A domain controller to check

	### limit
	The amount of times to check for an external server.  Useful for when an NTP server no longer responds

	### dstEmail
	The email to send alerts to

	### smtpServer
	The smtp server to send mail through

	### accptOffset
	The acceptable offset for the NTP servers in seconds.  Must be a negative number