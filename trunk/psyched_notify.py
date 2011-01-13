'''
Psyched is a scheduling and task management application.

Copyright 2007-2010 Eric Stein
License: GPL2/GPL3, at your option.  For details see LICENSE.

$Id$
'''

available = {}

try :
	import pynotify
	available['pynotify'] = True
except :
	available['pynotify'] = False

try :
	import hildon
	available['hildon'] = True
except :
	available['hildon'] = False

import gtk
import gtk.gdk
import xml.sax.saxutils

class Notifier :
	def notify(self, title, string) :
		return

class PyNotifier (Notifier) :
	def __init__(self, app) :
		self.app = app
		self.expire = pynotify.EXPIRES_NEVER
		pynotify.init(app)

	def notify(self, title, string) :
		p = pynotify.Notification(title, xml.sax.saxutils.escape(string))
		p.set_timeout(self.expire)
		p.show()

class HildonNotifier (Notifier) :
	def __init__(self, app) :
		self.app = app
	
	def notify(self, title, string) :
		hildon.hildon_banner_show_information(self.app, None, string)

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
