'''
Psyched is a scheduling and task management application.

Copyright 2007-2010 Eric Stein
License: GPL2/GPL3, at your option.  For details see LICENSE.
'''

import os
import sys
import time
import uuid
import threading

try :
	import sqlite3 as sqlite
except ImportError :
	import pysqlite2.dbapi2 as sqlite

NUM_SETTINGS = 13
(
	SETTING_DATAVERSION,
	SETTING_RANGE,
	SETTING_POSITION_STORE,
	SETTING_POSITION_X,
	SETTING_POSITION_Y,
	SETTING_POSITION_XW,
	SETTING_POSITION_YW,
	SETTING_NOTIFY_TASK,
	SETTING_NOTIFY_SCHED,
	SETTING_NOTIFY_TASK_ADVANCE,
	SETTING_NOTIFY_SCHED_ADVANCE,
	SETTING_SCT,
	SETTING_SHOW_CALENDAR
) = range(NUM_SETTINGS)

types = {
	SETTING_DATAVERSION : int,
	SETTING_RANGE : int,
	SETTING_POSITION_STORE : bool,
	SETTING_POSITION_X : int,
	SETTING_POSITION_Y : int,
	SETTING_POSITION_XW : int,
	SETTING_POSITION_YW : int,
	SETTING_NOTIFY_TASK : bool,
	SETTING_NOTIFY_SCHED : bool,
	SETTING_NOTIFY_TASK_ADVANCE : int,
	SETTING_NOTIFY_SCHED_ADVANCE : int,
	SETTING_SCT : bool,
	SETTING_SHOW_CALENDAR : bool
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

def getuuid() :
	return str(uuid.uuid4())

def sec2dur(s) :
	mins = s / 60
	m = str(mins % 60)
	h = str(mins / 60)
	if len(m) == 1 :
		m = '0' + m
	return h + ':' + m


# By Magnus Hetland (http://hetland.org/), props!
def levenshtein(a,b):
	"Calculates the Levenshtein distance between a and b."
	n, m = len(a), len(b)
	if n > m:
		# Make sure n <= m, to use O(min(n,m)) space
		a,b = b,a
		n,m = m,n
		
	current = range(n+1)
	for i in range(1,m+1):
		previous, current = current, [i]+[0]*n
		for j in range(1,n+1):
			add, delete = previous[j]+1, current[j-1]+1
			change = previous[j-1]
			if a[j-1] != b[i-1]:
				change = change + 1
			current[j] = min(add, delete, change)
			
	return current[n]

# naive implementation of LCS
def longest_common_substring(a,b) :
	l = 0
	ss = ''
	for a_s in range(len(a)) :
		for a_l in range(len(a) - a_s + 1) :
			ss_ = a[a_s:a_s+a_l]
			if ss_ in b and len(ss_) > l :
				l = len(ss_)
				ss = ss_
	return ss

def considered_similar(a, b) :
	m = 2.5
	m_mid = 1.5
	edit_extra = 0.2
	lev_total = 6.0
	a = a.lower()
	b = b.lower()
	fl_a = float(len(a))
	fl_b = float(len(b))
	ratio = 0
	try :
		ratio = max(fl_a / fl_b, fl_b / fl_a)
	except :
		return False

	if ratio >= m :
		return False

	lev = levenshtein(a, b)
	lcs = len(longest_common_substring(a, b))
	diff = abs(fl_a - fl_b)
	smaller = min(fl_a, fl_b)

	if lev <= ((fl_a + fl_b) / lev_total) :
		return True

	# here, the ratio of one to the other is pretty unbalanced, so go into close-to-lcs mode.
	if ratio > m_mid :
		if lcs <= smaller * (1 - edit_extra) :
			return False

	if lev <= diff + edit_extra * smaller :
		return True

	return False

class PsychedBackend :
	'''Psyched Backend
	
	handles storage, querying, and changes.
	'''

	CURRENT_DATAVERSION = 9

	def __init__(self, dbfile=None) :
		if not dbfile :
			d = self.get_directory()
			os.chdir(d)
			dbfile = "psyched.db"
		self.conn = sqlite.connect(dbfile)
		self.conn.text_factory = str
		self.cursor = self.conn.cursor()

		# check tables, create if needed
		try:
			i = self.cursor.execute('select count(*) from settings')
		except sqlite.OperationalError:
			self.create_tables()
			self.initial_settings()
			self.conn.commit()

		# TODO during migrating this, use a transaction? or more than one?
		assert (self.update_dataversion(PsychedBackend.CURRENT_DATAVERSION) == True)

		self.state_updated = False
		self.state_lock = threading.Lock()

	def statecheck(self) :
		with self.state_lock :
			oldstate = self.state_updated
			self.state_updated = False
			return oldstate

	def stateupdated(self) :
		with self.state_lock :
			self.state_updated = True

#--------------------- INITIALIZATION
	def create_tables(self) :
		# create the tables
		self.cursor.execute('create table settings (id integer primary key, setting blob)')
		self.cursor.execute('create table task (id integer primary key autoincrement, text blob, due integer null, complete integer, uuid varchar(36) unique)')
		self.cursor.execute('create table sched (id integer primary key autoincrement, text blob, ts integer, duration integer, complete integer, task integer key, uuid varchar(36) unique)')
		self.cursor.execute('create index task_due on task(due)')
		self.cursor.execute('create index task_complete on task(complete)')
		self.cursor.execute('create index sched_ts on sched(ts)')
		self.cursor.execute('create index sched_duration on sched(duration)')
		self.cursor.execute('create index sched_complete on sched(complete)')

	def initial_settings(self) :
		'''Default settings
	
		Only use this function for initialization - not for resetting settings to default.
		'''
		self.setting_set(SETTING_DATAVERSION, PsychedBackend.CURRENT_DATAVERSION)
		self.setting_set(SETTING_RANGE, 7)
		self.setting_set(SETTING_POSITION_STORE, True)
		self.setting_set(SETTING_POSITION_X, 0)
		self.setting_set(SETTING_POSITION_Y, 0)
		self.setting_set(SETTING_POSITION_XW, 500)
		self.setting_set(SETTING_POSITION_YW, 700)
		self.setting_set(SETTING_NOTIFY_TASK, True)
		self.setting_set(SETTING_NOTIFY_SCHED, True)
		self.setting_set(SETTING_NOTIFY_TASK_ADVANCE, 0)
		self.setting_set(SETTING_NOTIFY_SCHED_ADVANCE, 0)
		self.setting_set(SETTING_SCT, True)


#--------------------- DATA FORMAT VERSIONS
	def update_dataversion(self, rev) :
		updict = {
			2 : self.update_rev_2,
			3 : self.update_rev_3,
			4 : self.update_rev_4,
			5 : self.update_rev_5,
			6 : self.update_rev_6,
			7 : self.update_rev_7,
			8 : self.update_rev_8,
			9 : self.update_rev_9
		}
		assert (PsychedBackend.CURRENT_DATAVERSION in updict)

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

	def update_rev_3(self) :
		self.cursor.execute('create index sched_duration on sched(duration)')
		return True
	
	def update_rev_4(self) :
		self.setting_set(SETTING_NOTIFY_TASK, True)
		self.setting_set(SETTING_NOTIFY_SCHED, True)
		self.setting_set(SETTING_NOTIFY_TASK_ADVANCE, 0)
		self.setting_set(SETTING_NOTIFY_SCHED_ADVANCE, 0)
		return True

	def update_rev_5(self) :
		self.cursor.execute('create index task_complete on task(complete)')
		self.cursor.execute('create index sched_ts on sched(ts)')
		return True

	def update_rev_6(self) :
		self.setting_set(SETTING_SCT, True)
		return True

	def update_rev_7(self) :
		self.setting_set(SETTING_SHOW_CALENDAR, True)
		return True

	def update_rev_8(self) :
		self.cursor.execute('create index sched_complete on sched(complete)')
		self.cursor.execute('create index task_due on task(due)')
		return True

	def update_rev_9(self) :
		for table in ['task', 'sched'] :
			self.cursor.execute('alter table %s add column uuid varchar(36)' % table)
			# can't change the uniqueness of uuid directly via a table alter 
			# going to have to do some junk to make this work.
			# want the old primary key id to go away or not? probably not,
			# as the rest of the code already works with it as an integer. perhaps it's best
			# to make the uuid column only get used for communication between instances,
			# wheras the integer id is used for local operation. it's always going to exist anyway.
			idsets = []
			for i in [fupack(r) for r in self.cursor.execute('select id from %s' % table).fetchall()] :
				idsets.append((i, getuuid()))

			for i,u in idsets :
				self.cursor.execute('update %s set uuid=? where id=?' % table, (u, i))

		# FIXME XXX TODO
		# insert-from into temporary table, rename table, create new table with unique constraint, insert back, drop

		return True


#--------------------- TRANSACTION SAFETY
	def action_complete(self) :
		self.conn.commit()
	
	def action_undo(self) :
		self.conn.rollback()


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

	def get_sched_text(self, id) :
		return fupack(self.cursor.execute('select text from sched where id=?', (id, )).fetchall()[0])

	def get_task_due(self, id) :
		return fupack(self.cursor.execute('select due from task where id=?', (id, )).fetchall()[0])

	def get_task_text(self, id) :
		return fupack(self.cursor.execute('select text from task where id=?', (id, )).fetchall()[0])

#--------------------- ADDERS
	def insert_task(self, text, due) :
		self.cursor.execute('insert into task (text, due, complete, uuid) values (?, ?, ?, ?)', (text, due, 0, getuuid()))
		return self.cursor.lastrowid

	def insert_sched(self, text, ts, duration, complete, task) :
		self.cursor.execute('insert into sched (text, ts, duration, complete, task, uuid) values (?, ?, ?, ?, ?, ?)', (text, ts, duration, complete, task, getuuid()))
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

	def fetch_dated_tasks(self, timestamp, range, sct=True) :
		additional_where = ''
		if not sct :
			additional_where = ' and complete=0'
		return self.cursor.execute('select id,text,due,complete from task where due>=? and due<?%s' % additional_where, (timestamp, timestamp + range)).fetchall()

	def fetch_similar_onday(self, midnight_ts, text, skip=None) :
		similar = self.fetch_dated_tasks(midnight_ts, 3600*24, sct=False)
		similar = filter((lambda (a,b,c,d): considered_similar(b, text)), similar)
		if skip is not None :
			similar = filter((lambda (a,b,c,d): a != skip), similar)
		return similar

	# not used (yet)
	def fetch_undated_tasks(self) :
		return self.cursor.execute('select id,text,due,complete from task where due isnull').fetchall()

# SCHEDULE
	def fetch_sched(self, id) :
		return self.cursor.execute('select id,text,ts,duration,complete,task from sched where id=?', (id, )).fetchall()[0]

	def fetch_task_sched(self, tid) :
		return self.cursor.execute('select sched.id,sched.text,sched.ts,sched.duration,sched.complete,sched.task from sched,task where task.id=? and sched.task=task.id', (tid, )).fetchall()

	def fetch_schedule(self, timestamp, range) :
		return self.cursor.execute('select id,text,ts,duration,complete,task from sched where ts>=? and ts<?', (timestamp, timestamp + range)).fetchall()

	def fetch_schedule_overlap(self, timestamp, range) :
		(ml, ) = self.cursor.execute('select max(duration) from sched').fetchall()[0]
		if ml == None :
			start = 0
			end = 0
		else :
			start = timestamp - ml
			end = timestamp + range
		return self.cursor.execute('select id,text,ts,duration from (select * from sched where ts>? and ts<? and complete=0) where ts>=? or ts+duration>?', (start, end, timestamp, timestamp)).fetchall()

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
			os.mkdir(dir, 0700)
		except Exception:
			return dir
		return dir
