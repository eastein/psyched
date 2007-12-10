#!/usr/bin/env python
'''
Psyched is a scheduling and task management application.

Copyright 2007 Eric Stein
License: GPL2/GPL3, at your option.
'''

import gtk
import gobject
import random
import time
import threading
import pysqlite2.dbapi2 as sqlite
import psyched_validate
import psyched_backend as pb

(
	COLUMN_TIME,
	COLUMN_DESC,
	COLUMN_EDITABLE
) = range(3)

cont = True

class Psyched(gtk.Window) :
	def __init__(self, parent=None) :
		gtk.Window.__init__(self)
		self.connect('destroy', self.__die__)

		self.set_title("Psyched")
		self.set_default_size(450,600)
		self.set_border_width(0)

		schedule = gtk.VPaned()
		self.set_border_width(5)
		tasks = gtk.VPaned()
		self.set_border_width(5)
		slabel = gtk.Label("Schedule")
		tlabel = gtk.Label("Tasks")

		tabset = gtk.Notebook()
		tabset.append_page(schedule, slabel)
		tabset.append_page(tasks, tlabel)
		self.add(tabset)
		
		daylist = self.create_list_set()
		treeview = self.create_tree(daylist)
		self.add_columns(treeview)
		schedule.add(treeview)

		self.timer = BackgroundTimer()
		self.timer.start()

		self.backend = pb.PsychedBackend()

		self.win = None
		self.show_all()
		
	def __die__(self, parent=None) :
		global cont
		#gtk.main_quit()
		cont = False

	def add_items_to_vpane(self, vp, list) :
		for item in list :
			vp.add(item)

	def clear_vpaned(self, vp) :
		vp.forall(vp.remove)

	def create_tree(self, list) :
		treeview = gtk.TreeView(list)
		treeview.set_rules_hint(True)
		treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)

		return treeview

	'''Create List Set
	'''
	def create_list_set(self) :
		model = gtk.ListStore(
			gobject.TYPE_STRING,
			gobject.TYPE_STRING,
			gobject.TYPE_BOOLEAN
		)

		iter = model.append()
		model.set(iter, COLUMN_TIME, str(random.randint(0,23)) + ':' + str(random.randint(10,59)), COLUMN_DESC, "stuff",  COLUMN_EDITABLE, True)

		return model

	def add_columns(self, treeview):
		model = treeview.get_model()
	
		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_cell_edited, model)
		renderer.set_data("column", COLUMN_TIME)
	
		column = gtk.TreeViewColumn("Time", renderer, text=COLUMN_TIME,
		editable=COLUMN_EDITABLE)
		treeview.append_column(column)

		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_cell_edited, model)
		renderer.set_data("column", COLUMN_DESC)
	
		column = gtk.TreeViewColumn("Description", renderer, text=COLUMN_DESC,
		editable=COLUMN_EDITABLE)
		treeview.append_column(column)

	def dialog(self, s) :
		dialog = gtk.MessageDialog(self,
			gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
			gtk.MESSAGE_INFO, gtk.BUTTONS_OK, s)
		dialog.run()
		dialog.destroy()

	def on_cell_edited(self, cell, path_string, new_text, model) :
		iter = model.get_iter_from_string(path_string)
		path = model.get_path(iter)[0]
		column = cell.get_data("column")

		update = None
		if column == COLUMN_DESC :
			update = new_text
			# call into storage backend here
		elif column == COLUMN_TIME :
			if (psyched_validate.check_time(new_text)) :
				update = new_text
				# call into storage backend here
		if update == None :
			self.dialog('Incorrect formatting.')
		else :
			model.set(iter, column, update)


class BackgroundTimer(threading.Thread) :
	def __init__(self) :
		self.callbacks = {'d':[], 'h':[], 'm':[], 's':[]}
		threading.Thread.__init__(self)

	def run(self) :
		global cont

		self.gmt = time.gmtime()
		self.day = time.strftime('%j', self.gmt)
		self.hour = time.strftime('%H', self.gmt)
		self.min = time.strftime('%M', self.gmt)
		self.sec = time.strftime('%S', self.gmt)

		while cont :
			gmt = time.gmtime()
			_day = time.strftime('%j', gmt)
			_hour = time.strftime('%H', gmt)
			_min = time.strftime('%M', gmt)
			_sec = time.strftime('%S', gmt)

			if self.day != _day :
				for c in self.callbacks['d'] :
					c()
			if self.hour != _hour :
				for c in self.callbacks['h'] :
					c()
			if self.min != _min :
				for c in self.callbacks['m'] :
					c()
			if self.sec != _sec :
				for c in self.callbacks['s'] :
					c()
			self.day = _day
			self.hour = _hour
			self.min = _min
			self.sec = _sec

			time.sleep(0.5)

	def add_callback(self, period, callback) :
		self.callbacks[period].append(callback)

def gtkm() :
	global cont
	while cont :
		while gtk.events_pending() :
			gtk.main_iteration()
		time.sleep(0.02)

if __name__ == '__main__':
	psyched = Psyched()
	try:
		gtkm()
	except KeyboardInterrupt:
		cont = False
