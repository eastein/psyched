import os
import sys
import time
import pysqlite2.dbapi2 as sqlite

class PsychedBackend :
	def __init__(self) :
		os.chdir(self.get_directory())
		self.conn = sqlite.connect("psyched.db")

	def get_directory(self) :
		dir = os.path.join(os.path.expanduser('~'), '.psyched')
		try:
			os.mkdir(dir)
		except Exception:
			return dir
		return dir
