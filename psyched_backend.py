import os
import sys
import time
import pysqlite2.dbapi2 as sqlite

'''GMT unix timestamp

uses localtime because mktime requires local time
'''
def utime() :
	return time.mktime(time.localtime())

'''Psyched Backend

handles storage, querying, and changes.
'''
class PsychedBackend :
	def __init__(self) :
		os.chdir(self.get_directory())
		self.conn = sqlite.connect("psyched.db")
		self.cursor = self.conn.cursor()

		# check tables, create if needed
		try:
			i = self.cursor.execute('select count(*) from settings')
			i = self.cursor.execute('select count(*) from task')
			i = self.cursor.execute('select count(*) from sched')
		except sqlite.OperationalError:
			self.create_tables()

	def create_tables(self) :
		# create the tables
		self.cursor.execute('create table settings (id integer primary key, setting blob)')
		self.cursor.execute('create table task (id integer primary key autoincrement, text blob, due integer null)')
		self.cursor.execute('create table sched (id integer primary key autoincrement, text blob, duration integer null)')
		self.conn.commit()

	def setting_get(self, id) :
		s = self.cursor.execute('select setting from settings where id=?', (id,)).fetchall()
		if len(s) == 0 :
			return None
		elif len(s) == 1 :
			(r, ) = s
			return r
		else :
			raise RuntimeError, 'Multiple instances of one setting: ' + str(id)

	def setting_unset(self, id) :
		s = self.cursor.execute('select id from settings where id=?', (id,)).fetchall()
		if len(s) == 1 :
			self.cursor.execute('delete from settings where id=?', (id, ))
			self.conn.commit()
		if len(s) > 1 :
			raise RuntimeError, 'Multiple instances of one setting: ' + str(id)
		self.conn.commit()

	def setting_set(self, id, data) :
		s = self.cursor.execute('select id from settings where id=?', (id,)).fetchall()
		if len(s) == 0 :
			self.cursor.execute('insert into settings (id, setting) values (?, ?)', (id, data))
		elif len(s) == 1 :
			self.cursor.execute('update settings set setting=? where id=?', (data, id))
		else :
			raise RuntimeError, 'Multiple instances of one setting: ' + str(id)
		self.conn.commit()
		

	def get_directory(self) :
		dir = os.path.join(os.path.expanduser('~'), '.psyched')
		try:
			os.mkdir(dir)
		except Exception:
			return dir
		return dir
