import time, os, glob

class logger:
	def __init__(self, logDir, logDays=7, logFileName="logging.log"):
		"""
			sets logging directory, number of log days and name of log file
		"""
		self.orig = os.getcwd()
		self.logDir = logDir
		self.logDays = logDays
		self.logFileName = logFileName
		if(not os.path.exists(logDir)):
			os.makedirs(logDir)
		os.chdir(logDir)
	
	def checkTime(self):
		"""
			finds the newest file
		"""
		filelist = os.listdir(logDir)
		filelist = filter(lambda x: not os.path.isdir(x), filelist)
		newest = max(filelist, key=lambda x: os.stat(x).st_mtime)
		return newest
	
	def checkNeedNew(self, newest):
		"""
			Checks if the files need to be moved
		"""
		currFile = "1." + self.logFileName
		mday = int(time.strftime('%j', time.localtime(os.stat(currFile).st_mtime)))
		cday = int(time.strftime('%j'))
		return cday == mday
		
	
	def moveFiles(self):
		files = glob.glob1(logDir, "*" + self.logFileName)
		sortFiles = sorted(files, key=lambda x: float(x.split('.')[0]))
		for x in range(len(sortFiles)-1, -1, -1):
			os.rename(sortFiles[x], x + self.logFileName)
		os.remove(str(self.logDays+1) + "." + self.logFileName)
	
	def writeLog(self, message):
		"""
			writes messages to log
		"""
		newest = self.checkTime
		if(not self.checkNeedNew(newest)):
			self.moveFiles()
		with open(self.logDir + '\\1.' + self.logFileName, 'a') as f:
			f.write(message + "\n")
		