'''
Psyched is a scheduling and task management application.

Copyright 2007-2008 Eric Stein
License: GPL2/GPL3, at your option.  For details see LICENSE.

$Id$
'''

import os
import sys
import time
import pysqlite2.dbapi2 as sqlite

(
	SETTING_DATAVERSION,
	SETTING_RANGE,
	SETTING_POSITION_STORE,
	SETTING_POSITION_X,
	SETTING_POSITION_Y,
	SETTING_POSITION_XW,
	SETTING_POSITION_YW
) = range(7)

types = {
	SETTING_DATAVERSION : int,
	SETTING_RANGE : int,
	SETTING_POSITION_STORE : bool,
	SETTING_POSITION_X : int,
	SETTING_POSITION_Y : int,
	SETTING_POSITION_XW : int,
	SETTING_POSITION_YW : int
	}

def utime() :
	'''GMT unix timestamp
	
	uses localtime because mktime requires local time
	'''
	return int(time.mktime(time.localtime()))

def ts2dt(ts) :
	(y, m, d, a, b, c, d2, e, f) = time.localtime(ts)
	return (y, m, d)

def tod(ts) :
	return time.strftime('%H:%M', time.localtime(ts))

def fupack(t) :
	(a, ) = t
	return a

def sec2dur(s) :
	mins = s / 60
	m = str(mins % 60)
	h = str(mins / 60)
	if len(m) == 1 :
		m = '0' + m
	return h + ':' + m

class PsychedBackend :
	'''Psyched Backend
	
	handles storage, querying, and changes.
	'''
	def __init__(self) :
		os.chdir(self.get_directory())
		self.conn = sqlite.connect("psyched.db")
		self.conn.text_factory = str
		self.cursor = self.conn.cursor()

		# check tables, create if needed
		try:
			i = self.cursor.execute('select count(*) from settings')
		except sqlite.OperationalError:
			self.create_tables()
			self.initial_settings()
			self.conn.commit()
		assert (self.update_dataversion(2) == True)

#--------------------- INITIALIZATION
	def create_tables(self) :
		# create the tables
		self.cursor.execute('create table settings (id integer primary key, setting blob)')
		self.cursor.execute('create table task (id integer primary key autoincrement, text blob, due integer null, complete integer)')
		self.cursor.execute('create table sched (id integer primary key autoincrement, text blob, ts integer, duration integer, complete integer, task integer key)')

	def initial_settings(self) :
		'''Default settings
	
		Only use this function for initialization - not for resetting settings to default.
		'''
		self.setting_set(SETTING_DATAVERSION, 2)
		self.setting_set(SETTING_RANGE, 7)
		self.setting_set(SETTING_POSITION_STORE, True)
		self.setting_set(SETTING_POSITION_X, 0)
		self.setting_set(SETTING_POSITION_Y, 0)
		self.setting_set(SETTING_POSITION_XW, 500)
		self.setting_set(SETTING_POSITION_YW, 700)


#--------------------- DATA FORMAT VERSIONS
	def update_dataversion(self, rev) :
		updict = {
			2 : self.update_rev_2
		}
		crev = self.setting_get(SETTING_DATAVERSION)
		if (crev < rev) :
			for r in range(crev + 1, rev + 1) :
				updict[r]()
		elif (crev > rev) :
			return False
		self.setting_set(SETTING_DATAVERSION, rev)
		return True
	
	#update functions should not edit SETTING_DATAVERSION
	def update_rev_2(self) :
		self.setting_set(SETTING_POSITION_STORE, True)
		self.setting_set(SETTING_POSITION_X, 0)
		self.setting_set(SETTING_POSITION_Y, 0)
		self.setting_set(SETTING_POSITION_XW, 500)
		self.setting_set(SETTING_POSITION_YW, 700)
		return True

#--------------------- TRANSACTION SAFETY
	def action_complete(self) :
		self.conn.commit()


#--------------------- SETTERS
	def set_task_text(self, id, text) :
		self.cursor.execute('update task set text=? where id=?', (text, id))

	def set_task_due(self, id, due) :
		self.cursor.execute('update task set due=? where id=?', (due, id))
	
	def set_task_complete(self, id, complete) :
		self.cursor.execute('update task set complete=? where id=?', (complete, id))

	def set_sched_text(self, id, text) :
		self.cursor.execute('update sched set text=? where id=?', (text, id))
	
	def set_sched_ts(self, id, ts) :
		self.cursor.execute('update sched set ts=? where id=?', (ts, id))
	
	def set_sched_duration(self, id, duration) :
		self.cursor.execute('update sched set duration=? where id=?', (duration, id))

	def set_sched_complete(self, id, complete) :
		self.cursor.execute('update sched set complete=? where id=?', (complete, id))

	def set_sched_task(self, id, task) :
		self.cursor.execute('update sched set task=? where id=?', (task, id))

#--------------------- GETTERS
	def get_sched_ts(self, id) :
		return fupack(self.cursor.execute('select ts from sched where id=?', (id, )).fetchall()[0])

	def get_sched_duration(self, id) :
		return fupack(self.cursor.execute('select duration from sched where id=?', (id, )).fetchall()[0])

	def get_task_due(self, id) :
		return fupack(self.cursor.execute('select due from task where id=?', (id, )).fetchall()[0])

#--------------------- ADDERS
	def insert_task(self, text, due) :
		self.cursor.execute('insert into task (text, due, complete) values (?, ?, ?)', (text, due, 0))
		return self.cursor.lastrowid

	def insert_sched(self, text, ts, duration, complete, task) :
		self.cursor.execute('insert into sched (text, ts, duration, complete, task) values (?, ?, ?, ?, ?)', (text, ts, duration, complete, task))
		return self.cursor.lastrowid

#--------------------- REMOVERS
	def remove_task(self, id) :
		self.cursor.execute('delete from task where id=?', (id, ))

	def remove_sched(self, id) :
		self.cursor.execute('delete from sched where id=?', (id, ))
#--------------------- FETCHERS 

# TASKS
	def fetch_task(self, id) :
		return self.cursor.execute('select id,text,due,complete from task where id=?', (id, )).fetchall()[0]

	def fetch_dated_tasks(self, timestamp, range) :
		return self.cursor.execute('select id,text,due,complete from task where due>=? and due<=?', (timestamp, timestamp + range)).fetchall()

	def fetch_undated_tasks(self) :
		return self.cursor.execute('select id,text,due,complete from task where due isnull').fetchall()

# SCHEDULE
	def fetch_sched(self, id) :
		return self.cursor.execute('select id,text,ts,duration,complete,task from sched where id=?', (id, )).fetchall()[0]

	def fetch_task_sched(self, tid) :
		return self.cursor.execute('select sched.id,sched.text,sched.ts,sched.duration,sched.complete,sched.task from sched,task where task.id=? and sched.task=task.id', (tid, )).fetchall()

	def fetch_schedule(self, timestamp, range) :
		return self.cursor.execute('select id,text,ts,duration,complete,task from sched where ts>=? and ts<=?', (timestamp, timestamp + range)).fetchall()

#--------------------- SETTINGS
	def setting_get(self, id) :
		'''Get a setting
	
		If the setting exists, it is returned as the correct type.
		If the setting is not known by this file, it will raise a RuntimeError.
		If it is not set, returns None
		'''
		s = self.cursor.execute('select setting from settings where id=?', (id,)).fetchall()
		if len(s) == 0 :
			return None
		elif len(s) == 1 :
			(r, ) = s[0]
			if types.has_key(id) :
				return types[id](r)
			else :
				raise RuntimeError, 'Setting has unknown type.  Cannot read.'
		else :
			raise RuntimeError, 'Multiple instances of one setting: ' + str(id)

	def setting_unset(self, id) :
		'''Unset a setting
	
		If the setting exists, it is unset.
		'''
		s = self.cursor.execute('select id from settings where id=?', (id,)).fetchall()
		if len(s) == 1 :
			self.cursor.execute('delete from settings where id=?', (id, ))
			self.conn.commit()
		if len(s) > 1 :
			raise RuntimeError, 'Multiple instances of one setting: ' + str(id)
		self.conn.commit()

	def setting_set(self, id, data) :
		'''Set a setting
	
		If the setting is set already, it is overwritten.
		'''
		s = self.cursor.execute('select id from settings where id=?', (id,)).fetchall()
		if len(s) == 0 :
			self.cursor.execute('insert into settings (id, setting) values (?, ?)', (id, data))
		elif len(s) == 1 :
			self.cursor.execute('update settings set setting=? where id=?', (data, id))
		else :
			raise RuntimeError, 'Multiple instances of one setting: ' + str(id)
		self.conn.commit()
		

#--------------------- FILE ACCESS
	def get_directory(self) :
		'''Get the working directory
	
		On UNIX systems, this is ~/.psyched.  Other systems are currently not supported.
		'''
		dir = os.path.join(os.path.expanduser('~'), '.psyched')
		try:
			os.mkdir(dir)
		except Exception:
			return dir
		return dir
