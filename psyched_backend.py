'''
Psyched is a scheduling and task management application.

Copyright 2007 Eric Stein
License: GPL2/GPL3, at your option.
'''

import os
import sys
import time
import pysqlite2.dbapi2 as sqlite

(
	SETTING_DATAVERSION,
	SETTING_STANDIN
) = range(2)

'''GMT unix timestamp

uses localtime because mktime requires local time
'''
def utime() :
	return time.mktime(time.localtime())

def sec2dur(s) :
	mins = s / 60
	m = str(mins % 60)
	h = str(mins / 60)
	if len(m) == 1 :
		m = '0' + m
	return h + ':' + m

'''Psyched Backend

handles storage, querying, and changes.
'''
class PsychedBackend :
	def __init__(self) :
		os.chdir(self.get_directory())
		self.conn = sqlite.connect("psyched.db")
		self.conn.text_factory = str
		self.cursor = self.conn.cursor()

		# check tables, create if needed
		try:
			i = self.cursor.execute('select count(*) from settings')
			i = self.cursor.execute('select count(*) from task')
			i = self.cursor.execute('select count(*) from sched')
		except sqlite.OperationalError:
			self.create_tables()
			self.initial_settings()
			self.conn.commit()

#--------------------- INITIALIZATION
	def create_tables(self) :
		# create the tables
		self.cursor.execute('create table settings (id integer primary key, setting blob)')
		self.cursor.execute('create table task (id integer primary key autoincrement, text blob, due integer null, complete integer)')
		self.cursor.execute('create table sched (id integer primary key autoincrement, text blob, ts integer, duration integer, complete integer, task integer key)')

	'''Default settings

	Only use this function for initialization - not for resetting settings to default.
	'''
	def initial_settings(self) :
		self.setting_set(SETTING_DATAVERSION, "1")

#--------------------- TRANSACTION SAFETY
	def action_complete(self) :
		self.conn.commit()

#--------------------- ADDERS
	def insert_task(self, text, due) :
		self.cursor.execute('insert into task (text, due, complete) values (?, ?, ?)', (text, due, 0))
		return self.cursor.lastrowid

	def insert_sched(self, text, ts, duration, complete, task) :
		self.cursor.execute('insert into sched (text, ts, duration, complete, task) values (?, ?, ?, ?, ?)', (text, ts, duration, complete, task))
		return self.cursor.lastrowid
#--------------------- FETCHERS 

# TASKS
	def fetch_dated_tasks(self, timestamp, range) :
		return self.cursor.execute('select id,text,due,complete from task where due>=? and due<=?', (timestamp, timestamp + range)).fetchall()

	def fetch_undated_tasks(self) :
		return self.cursor.execute('select id,text,due,complete from task where due isnull').fetchall()

# SCHEDULE
	def fetch_task_sched(self, tid) :
		return self.cursor.execute('select sched.id,sched.text,sched.ts,sched.duration,sched.complete,sched.task from sched,task where task.id=? and sched.task=task.id', (tid, )).fetchall()

	def fetch_schedule(self, timestamp, range) :
		return self.cursor.execute('select id,text,ts,duration,complete,task from sched where ts>=? and ts<=?', (timestamp, timestamp + range)).fetchall()

#--------------------- SETTINGS
	'''Get a setting

	If the setting exists, it is returned as a unicode string.
	If it does not exist, returns None
	'''
	def setting_get(self, id) :
		s = self.cursor.execute('select setting from settings where id=?', (id,)).fetchall()
		if len(s) == 0 :
			return None
		elif len(s) == 1 :
			(r, ) = s[0]
			return r
		else :
			raise RuntimeError, 'Multiple instances of one setting: ' + str(id)

	'''Unset a setting

	If the setting exists, it is unset.
	'''
	def setting_unset(self, id) :
		s = self.cursor.execute('select id from settings where id=?', (id,)).fetchall()
		if len(s) == 1 :
			self.cursor.execute('delete from settings where id=?', (id, ))
			self.conn.commit()
		if len(s) > 1 :
			raise RuntimeError, 'Multiple instances of one setting: ' + str(id)
		self.conn.commit()

	'''Set a setting

	If the setting is set already, it is overwritten.
	'''
	def setting_set(self, id, data) :
		s = self.cursor.execute('select id from settings where id=?', (id,)).fetchall()
		if len(s) == 0 :
			self.cursor.execute('insert into settings (id, setting) values (?, ?)', (id, data))
		elif len(s) == 1 :
			self.cursor.execute('update settings set setting=? where id=?', (data, id))
		else :
			raise RuntimeError, 'Multiple instances of one setting: ' + str(id)
		self.conn.commit()
		

#--------------------- FILE ACCESS
	'''Get the working directory

	On UNIX systems, this is ~/.psyched.  Other systems are currently not supported.
	'''
	def get_directory(self) :
		dir = os.path.join(os.path.expanduser('~'), '.psyched')
		try:
			os.mkdir(dir)
		except Exception:
			return dir
		return dir
