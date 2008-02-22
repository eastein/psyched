'''
Psyched is a scheduling and task management application.

Copyright 2007-2008 Eric Stein
License: GPL2/GPL3, at your option.  For details see LICENSE.

$Id$
'''

import pynotify
import gtk
import gtk.gdk

class Notifier :
	def notify(self, title, string) :
		return

class PyNotifier (Notifier) :
	def __init__(self, app) :
		self.app = app
		self.expire = pynotify.EXPIRES_NEVER
		pynotify.init(app)

	def notify(self, title, string) :
		p = pynotify.Notification(title, string)
		p.set_timeout(self.expire)
		p.show()

class PopNotifier (Notifier) :
	def __init__(self, app, window) :
		self.app = app
		self.win = window

	def notify(self, title, string) :
		dialog = gtk.MessageDialog(self.win,
			gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
			gtk.MESSAGE_INFO, gtk.BUTTONS_OK, string)
		dialog.set_title(self.app)
		dialog.run()
		dialog.destroy()
